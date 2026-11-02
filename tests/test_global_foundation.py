from test_tenant_isolation import c, register

def test_tenant_region_is_not_falsely_claimed():
    a=register('Global Test Clinic','global-clinic@example.com')
    response=c.get('/api/tenant/settings',headers=a)
    assert response.status_code==200
    assert response.json()['data_region']=='unassigned'
    change={'operating_country':'CA','data_region':'canada','currency':'CAD','timezone':'America/Toronto'}
    assert c.patch('/api/tenant/settings',headers=a,json=change).status_code==409
    change['data_region']='unassigned'
    assert c.patch('/api/tenant/settings',headers=a,json=change).status_code==200
    assert c.get('/api/tenant/settings',headers=a).json()['operating_country']=='CA'

def test_consent_is_scoped_and_audited():
    a=register('Consent Test Clinic','consent-a@example.com')
    b=register('Other Consent Clinic','consent-b@example.com')
    p=c.post('/api/patients',headers=a,json={'name':'Synthetic Patient'}).json()['id']
    endpoint=f'/api/patients/{p}/consents'
    assert c.get(endpoint,headers=b).status_code==404
    assert c.post(endpoint,headers=b,json={'purpose':'remote_monitoring','status':'granted','evidence_reference':'synthetic-evidence'}).status_code==404
    assert c.post(endpoint,headers=a,json={'purpose':'remote_monitoring','status':'granted','evidence_reference':'synthetic-evidence'}).status_code==201
    assert c.post(endpoint,headers=a,json={'purpose':'remote_monitoring','status':'withdrawn','evidence_reference':'synthetic-withdrawal'}).status_code==201
    assert [x['status'] for x in c.get(endpoint,headers=a).json()] == ['withdrawn','granted']
    assert any(x['action']=='consent.withdrawn' for x in c.get('/api/audit',headers=a).json())
