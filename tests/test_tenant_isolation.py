import os, tempfile
fd,path=tempfile.mkstemp(suffix='.db');os.close(fd)
os.environ['DATABASE_URL']='sqlite:///'+path
os.environ['JWT_SECRET']='test-secret-not-for-production-48-characters-minimum-123456789'
from fastapi.testclient import TestClient
from app.main import app
c=TestClient(app)
def register(org,email):
    r=c.post('/api/auth/register',json={'organization':org,'name':'Demo Owner','email':email,'password':'strong-demo-password-123'})
    assert r.status_code==201,r.text
    return {'Authorization':'Bearer '+r.json()['access_token']}
def test_cross_tenant_access():
    a=register('Demo Island Clinic','clinic-a@example.com')
    b=register('Demo Coastal Clinic','clinic-b@example.com')
    p=c.post('/api/patients',headers=a,json={'name':'Synthetic Patient A','condition':'Diabetes'});assert p.status_code==201
    pid=p.json()['id']
    assert len(c.get('/api/patients',headers=a).json())==1
    assert c.get('/api/patients',headers=b).json()==[]
    assert c.post('/api/observations',headers=b,json={'patient_id':pid,'kind':'glucose','value':100,'unit':'mg/dL'}).status_code==404
    assert c.post('/api/alerts',headers=b,json={'patient_id':pid,'title':'Review synthetic reading'}).status_code==404
    assert c.get('/api/observations',headers=b,params={'patient_id':pid}).status_code==404
    assert c.post('/api/observations',headers=a,json={'patient_id':pid,'kind':'glucose','value':100,'unit':'mg/dL'}).status_code==201
    alert=c.post('/api/alerts',headers=a,json={'patient_id':pid,'title':'Review synthetic reading'});assert alert.status_code==201
    assert c.patch('/api/alerts/'+alert.json()['id'],headers=b,json={'status':'resolved'}).status_code==404
    assert c.patch('/api/alerts/'+alert.json()['id'],headers=a,json={'status':'resolved'}).status_code==200
    assert c.get('/api/overview',headers=b).json()['patients']==0
    assert c.get('/api/audit',headers=b).status_code==200
    assert all(x['resource_id']!=pid for x in c.get('/api/audit',headers=b).json())
def test_auth_and_billing_fail_closed():
    assert c.get('/api/patients').status_code==401
    a=register('Third Demo Clinic','clinic-c@example.com')
    assert c.post('/api/billing/checkout',headers=a).status_code==503
    assert c.post('/api/auth/login',json={'email':'clinic-c@example.com','password':'wrong'}).status_code==401
    assert c.post('/api/auth/login',json={'email':'clinic-c@example.com','password':'strong-demo-password-123'}).status_code==200
    assert c.post('/api/patients',headers=a,json={'name':'x'}).status_code==422
