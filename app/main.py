"""XelaCare HaaS foundation. NOT approved for live protected health information."""
from __future__ import annotations
import hashlib, hmac, os, secrets, uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Annotated, Literal
import jwt
from fastapi import FastAPI, Depends, HTTPException, Header, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import create_engine, ForeignKey, String, DateTime, Float, Integer, Text, Boolean, select, func, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session, sessionmaker

DB_URL = os.getenv('DATABASE_URL', 'sqlite:///./xelacare.db')
SECRET = os.getenv('JWT_SECRET', '')
IS_PROD = os.getenv('APP_ENV', 'development') == 'production'
if IS_PROD and (len(SECRET) < 48 or DB_URL.startswith('sqlite')):
    raise RuntimeError('Production requires a strong JWT_SECRET and PostgreSQL DATABASE_URL')
if not SECRET:
    SECRET = secrets.token_urlsafe(48)  # dev only; restarts invalidate sessions
engine = create_engine(DB_URL, connect_args={'check_same_thread': False} if DB_URL.startswith('sqlite') else {}, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
class Base(DeclarativeBase): pass

def uid(): return str(uuid.uuid4())
def now(): return datetime.now(timezone.utc)
class Organization(Base):
    __tablename__='organizations'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    name: Mapped[str] = mapped_column(String(160))
    slug: Mapped[str] = mapped_column(String(80), unique=True)
    plan: Mapped[str] = mapped_column(String(24), default='trial')
    status: Mapped[str] = mapped_column(String(24), default='trial')
    stripe_customer_id: Mapped[str | None] = mapped_column(String(120), unique=True)
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(120), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
class TenantSettings(Base):
    __tablename__='tenant_settings'
    org_id: Mapped[str] = mapped_column(ForeignKey('organizations.id'), primary_key=True)
    operating_country: Mapped[str] = mapped_column(String(2), default='LC')
    data_region: Mapped[str] = mapped_column(String(24), default='unassigned')
    currency: Mapped[str] = mapped_column(String(3), default='USD')
    timezone: Mapped[str] = mapped_column(String(64), default='America/St_Lucia')
    consent_required: Mapped[bool] = mapped_column(Boolean, default=True)
    clinical_mode: Mapped[bool] = mapped_column(Boolean, default=False)

class PatientConsent(Base):
    __tablename__='patient_consents'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    org_id: Mapped[str] = mapped_column(ForeignKey('organizations.id'), index=True)
    patient_id: Mapped[str] = mapped_column(ForeignKey('patients.id'), index=True)
    purpose: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(16))
    evidence_reference: Mapped[str] = mapped_column(String(255))
    recorded_by: Mapped[str] = mapped_column(String(36))
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class User(Base):
    __tablename__='users'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    org_id: Mapped[str] = mapped_column(ForeignKey('organizations.id'), index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    name: Mapped[str] = mapped_column(String(160))
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(32), default='clinician')
    active: Mapped[bool] = mapped_column(Boolean, default=True)
class Patient(Base):
    __tablename__='patients'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    org_id: Mapped[str] = mapped_column(ForeignKey('organizations.id'), index=True)
    name: Mapped[str] = mapped_column(String(160))
    external_id: Mapped[str | None] = mapped_column(String(80))
    condition: Mapped[str] = mapped_column(String(100), default='General monitoring')
    status: Mapped[str] = mapped_column(String(24), default='active')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    __table_args__=(UniqueConstraint('org_id','external_id',name='uq_patient_external_per_tenant'),)
class Observation(Base):
    __tablename__='observations'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    org_id: Mapped[str] = mapped_column(ForeignKey('organizations.id'), index=True)
    patient_id: Mapped[str] = mapped_column(ForeignKey('patients.id'), index=True)
    kind: Mapped[str] = mapped_column(String(32))
    value: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(24))
    source: Mapped[str] = mapped_column(String(24), default='manual')
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
class Alert(Base):
    __tablename__='alerts'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    org_id: Mapped[str] = mapped_column(ForeignKey('organizations.id'), index=True)
    patient_id: Mapped[str] = mapped_column(ForeignKey('patients.id'), index=True)
    title: Mapped[str] = mapped_column(String(160))
    severity: Mapped[str] = mapped_column(String(16), default='medium')
    status: Mapped[str] = mapped_column(String(24), default='open')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
class Audit(Base):
    __tablename__='audit_events'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    org_id: Mapped[str] = mapped_column(ForeignKey('organizations.id'), index=True)
    user_id: Mapped[str] = mapped_column(String(36))
    action: Mapped[str] = mapped_column(String(80))
    resource_id: Mapped[str] = mapped_column(String(36))
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

Base.metadata.create_all(engine)  # replace with reviewed migrations before production
app=FastAPI(title='XelaCare HaaS API',version='0.2.0',docs_url=None if IS_PROD else '/docs')
if os.getenv('CORS_ORIGINS'):
    app.add_middleware(CORSMiddleware,allow_origins=os.environ['CORS_ORIGINS'].split(','),allow_credentials=True,allow_methods=['GET','POST','PATCH'],allow_headers=['Authorization','Content-Type'])
STATIC=Path(__file__).resolve().parent.parent/'static'
app.mount('/assets',StaticFiles(directory=STATIC),name='assets')
@app.get('/',include_in_schema=False)
def homepage(): return FileResponse(STATIC/'index.html')
@app.get('/health')
def health(): return {'status':'ok','product':'XelaCare HaaS','version':'0.2.0'}

def db_session():
    with SessionLocal() as db: yield db
DB=Annotated[Session,Depends(db_session)]
def hash_pw(password:str)->str:
    salt=secrets.token_bytes(16)
    return f'{salt.hex()}:{hashlib.scrypt(password.encode(),salt=salt,n=2**14,r=8,p=1).hex()}'
def verify_pw(password:str, stored:str)->bool:
    try:
        salt,expected=stored.split(':')
        got=hashlib.scrypt(password.encode(),salt=bytes.fromhex(salt),n=2**14,r=8,p=1).hex()
        return hmac.compare_digest(got,expected)
    except (ValueError,TypeError): return False

def token(user:User):
    return jwt.encode({'sub':user.id,'org':user.org_id,'exp':now()+timedelta(hours=8),'iat':now()},SECRET,algorithm='HS256')
def current_user(authorization:Annotated[str|None,Header()]=None,db:Session=Depends(db_session))->User:
    if not authorization or not authorization.startswith('Bearer '): raise HTTPException(401,'Authentication required')
    try:
        data=jwt.decode(authorization[7:],SECRET,algorithms=['HS256'])
        user=db.get(User,data['sub'])
        if not user or not user.active or user.org_id!=data['org']: raise ValueError('invalid user')
        return user
    except (jwt.PyJWTError,ValueError,KeyError): raise HTTPException(401,'Invalid session')
AUTH=Annotated[User,Depends(current_user)]
def require(user:User,roles:set[str]):
    if user.role not in roles: raise HTTPException(403,'Insufficient privileges')
def log(db:Session,user:User,action:str,resource:str): db.add(Audit(org_id=user.org_id,user_id=user.id,action=action,resource_id=resource))
class TenantSettingsIn(BaseModel):
    operating_country: Literal['LC','KN','GD','VC','DM','AG','BB','TT','JM','BS','US','CA','GB','OTHER']
    data_region: Literal['unassigned','caribbean','us','canada','uk','eu']
    currency: Literal['USD','XCD','CAD','GBP','EUR']
    timezone: str=Field(min_length=3,max_length=64)

class ConsentIn(BaseModel):
    purpose: Literal['remote_monitoring','telehealth','caregiver_access','data_sharing']
    status: Literal['granted','withdrawn']
    evidence_reference: str=Field(min_length=6,max_length=255)

class Register(BaseModel):
    organization: str=Field(min_length=2,max_length=160)
    name: str=Field(min_length=2,max_length=160)
    email: EmailStr
    password: str=Field(min_length=12,max_length=128)
class Login(BaseModel):
    email: EmailStr
    password: str
class PatientIn(BaseModel):
    name:str=Field(min_length=2,max_length=160)
    external_id:str|None=Field(default=None,max_length=80)
    condition:str=Field(default='General monitoring',max_length=100)
class ObservationIn(BaseModel):
    patient_id:str
    kind:Literal['glucose','systolic_bp','diastolic_bp','heart_rate','spo2','temperature','weight']
    value:float=Field(ge=0,le=10000,allow_inf_nan=False)
    unit:str=Field(min_length=1,max_length=24)
class AlertIn(BaseModel):
    patient_id:str
    title:str=Field(min_length=3,max_length=160)
    severity:Literal['low','medium','high']='medium'
class AlertStatus(BaseModel):
    status:Literal['open','acknowledged','resolved']

@app.post('/api/auth/register',status_code=201)
def register(payload:Register,db:DB):
    # Public self-signup creates a trial tenant. Invite-only accounts are needed for staff in production.
    if db.scalar(select(User).where(User.email==payload.email.lower())): raise HTTPException(409,'Email already registered')
    org=Organization(name=payload.organization,slug=f'{payload.organization.lower().replace(" ","-")[:35]}-{secrets.token_hex(4)}')
    db.add(org);db.flush()
    user=User(org_id=org.id,email=payload.email.lower(),name=payload.name,password_hash=hash_pw(payload.password),role='owner')
    db.add(user);db.add(TenantSettings(org_id=org.id));db.flush();log(db,user,'organization.created',org.id);db.commit()
    return {'access_token':token(user),'organization':{'id':org.id,'name':org.name,'plan':org.plan},'user':{'name':user.name,'role':user.role}}
@app.post('/api/auth/login')
def login(payload:Login,db:DB):
    user=db.scalar(select(User).where(User.email==payload.email.lower()))
    if not user or not user.active or not verify_pw(payload.password,user.password_hash): raise HTTPException(401,'Invalid credentials')
    return {'access_token':token(user),'user':{'name':user.name,'role':user.role}}
@app.get('/api/me')
def me(user:AUTH,db:DB):
    org=db.get(Organization,user.org_id)
    return {'user':{'id':user.id,'name':user.name,'email':user.email,'role':user.role},'organization':{'id':org.id,'name':org.name,'plan':org.plan,'status':org.status}}
@app.get('/api/tenant/settings')
def tenant_settings(user:AUTH,db:DB):
    require(user,{'owner','admin'})
    settings=db.get(TenantSettings,user.org_id)
    if not settings: raise HTTPException(409,'Tenant configuration missing; migration required')
    return {'operating_country':settings.operating_country,'data_region':settings.data_region,
            'currency':settings.currency,'timezone':settings.timezone,
            'consent_required':settings.consent_required,'clinical_mode':settings.clinical_mode}

@app.patch('/api/tenant/settings')
def update_tenant_settings(payload:TenantSettingsIn,user:AUTH,db:DB):
    require(user,{'owner'})
    settings=db.get(TenantSettings,user.org_id)
    if not settings: raise HTTPException(409,'Tenant configuration missing; migration required')
    if payload.data_region != settings.data_region and settings.data_region!='unassigned':
        raise HTTPException(409,'Data region migration requires an approved operational process')
    # A data-region label is metadata, NOT evidence that data is hosted there.
    if payload.data_region!='unassigned':
        raise HTTPException(409,'Regional deployment not configured; data residency cannot be claimed')
    for k,v in payload.model_dump().items(): setattr(settings,k,v)
    log(db,user,'tenant.settings_updated',user.org_id);db.commit()
    return {'status':'updated','data_region':settings.data_region}

@app.get('/api/patients/{patient_id}/consents')
def patient_consents(patient_id:str,user:AUTH,db:DB):
    require(user,{'owner','admin','clinician'})
    if not db.scalar(select(Patient.id).where(Patient.id==patient_id,Patient.org_id==user.org_id)):
        raise HTTPException(404,'Patient not found')
    rows=db.scalars(select(PatientConsent).where(PatientConsent.org_id==user.org_id,
        PatientConsent.patient_id==patient_id).order_by(PatientConsent.recorded_at.desc())).all()
    return [{'id':c.id,'purpose':c.purpose,'status':c.status,'recorded_at':c.recorded_at.isoformat(),
             'evidence_reference':c.evidence_reference} for c in rows]

@app.post('/api/patients/{patient_id}/consents',status_code=201)
def record_consent(patient_id:str,payload:ConsentIn,user:AUTH,db:DB):
    require(user,{'owner','admin','clinician'})
    if not db.scalar(select(Patient.id).where(Patient.id==patient_id,Patient.org_id==user.org_id)):
        raise HTTPException(404,'Patient not found')
    c=PatientConsent(org_id=user.org_id,patient_id=patient_id,recorded_by=user.id,**payload.model_dump())
    db.add(c);db.flush();log(db,user,'consent.'+payload.status,c.id);db.commit()
    return {'id':c.id,'status':c.status,'purpose':c.purpose}

def assert_monitoring_consent(db:Session,org_id:str,patient_id:str):
    # Enforce consent for clinical use in all environments; demo mode remains non-clinical.
    settings=db.get(TenantSettings,org_id)
    if not settings: raise HTTPException(409,'Tenant configuration missing')
    if not settings.clinical_mode: return
    last=db.scalar(select(PatientConsent).where(PatientConsent.org_id==org_id,
        PatientConsent.patient_id==patient_id,PatientConsent.purpose=='remote_monitoring')
        .order_by(PatientConsent.recorded_at.desc(),PatientConsent.id.desc()).limit(1))
    if not last or last.status!='granted': raise HTTPException(403,'Remote monitoring consent is required')

@app.get('/api/overview')
def overview(user:AUTH,db:DB):
    o=user.org_id
    return {'patients':db.scalar(select(func.count()).select_from(Patient).where(Patient.org_id==o)),'observations':db.scalar(select(func.count()).select_from(Observation).where(Observation.org_id==o)),'open_alerts':db.scalar(select(func.count()).select_from(Alert).where(Alert.org_id==o,Alert.status=='open')),'clinicians':db.scalar(select(func.count()).select_from(User).where(User.org_id==o,User.active==True))}
@app.get('/api/patients')
def patients(user:AUTH,db:DB):
    return [{'id':p.id,'name':p.name,'external_id':p.external_id,'condition':p.condition,'status':p.status} for p in db.scalars(select(Patient).where(Patient.org_id==user.org_id).order_by(Patient.created_at.desc()).limit(500))]
@app.post('/api/patients',status_code=201)
def add_patient(payload:PatientIn,user:AUTH,db:DB):
    require(user,{'owner','admin','clinician'})
    if payload.external_id and db.scalar(select(Patient).where(Patient.org_id==user.org_id,Patient.external_id==payload.external_id)):
        raise HTTPException(409,'Patient reference already exists')
    p=Patient(org_id=user.org_id,**payload.model_dump());db.add(p);db.flush();log(db,user,'patient.created',p.id);db.commit()
    return {'id':p.id,'name':p.name}
@app.get('/api/observations')
def observations(user:AUTH,db:DB,patient_id:str|None=None):
    stmt=select(Observation).where(Observation.org_id==user.org_id)
    if patient_id:
        if not db.scalar(select(Patient.id).where(Patient.id==patient_id,Patient.org_id==user.org_id)): raise HTTPException(404,'Patient not found')
        stmt=stmt.where(Observation.patient_id==patient_id)
    return [{'id':x.id,'patient_id':x.patient_id,'kind':x.kind,'value':x.value,'unit':x.unit,'source':x.source,'observed_at':x.observed_at.isoformat()} for x in db.scalars(stmt.order_by(Observation.observed_at.desc()).limit(200))]
@app.post('/api/observations',status_code=201)
def add_observation(payload:ObservationIn,user:AUTH,db:DB):
    require(user,{'owner','admin','clinician'})
    if not db.scalar(select(Patient.id).where(Patient.id==payload.patient_id,Patient.org_id==user.org_id)): raise HTTPException(404,'Patient not found')
    assert_monitoring_consent(db,user.org_id,payload.patient_id)
    o=Observation(org_id=user.org_id,**payload.model_dump());db.add(o);db.flush();log(db,user,'observation.created',o.id);db.commit()
    return {'id':o.id,'status':'recorded'}
@app.get('/api/alerts')
def alerts(user:AUTH,db:DB):
    return [{'id':a.id,'patient_id':a.patient_id,'title':a.title,'severity':a.severity,'status':a.status,'created_at':a.created_at.isoformat()} for a in db.scalars(select(Alert).where(Alert.org_id==user.org_id).order_by(Alert.created_at.desc()).limit(200))]
@app.post('/api/alerts',status_code=201)
def add_alert(payload:AlertIn,user:AUTH,db:DB):
    require(user,{'owner','admin','clinician'})
    if not db.scalar(select(Patient.id).where(Patient.id==payload.patient_id,Patient.org_id==user.org_id)): raise HTTPException(404,'Patient not found')
    a=Alert(org_id=user.org_id,**payload.model_dump());db.add(a);db.flush();log(db,user,'alert.created',a.id);db.commit()
    return {'id':a.id}
@app.patch('/api/alerts/{alert_id}')
def update_alert(alert_id:str,payload:AlertStatus,user:AUTH,db:DB):
    require(user,{'owner','admin','clinician'})
    a=db.scalar(select(Alert).where(Alert.id==alert_id,Alert.org_id==user.org_id))
    if not a: raise HTTPException(404,'Alert not found')
    a.status=payload.status;log(db,user,'alert.status_updated',a.id);db.commit()
    return {'id':a.id,'status':a.status}
@app.get('/api/audit')
def audit(user:AUTH,db:DB):
    require(user,{'owner','admin'})
    return [{'action':x.action,'resource_id':x.resource_id,'occurred_at':x.occurred_at.isoformat()} for x in db.scalars(select(Audit).where(Audit.org_id==user.org_id).order_by(Audit.occurred_at.desc()).limit(100))]
@app.get('/api/billing/plans')
def plans():
    return [{'code':'starter','price_usd_month':99,'patient_limit':25},{'code':'professional','price_usd_month':299,'patient_limit':100},{'code':'business','price_usd_month':799,'patient_limit':300},{'code':'enterprise','price_usd_month':None,'patient_limit':None}]
@app.post('/api/billing/checkout')
def checkout(user:AUTH,db:DB):
    require(user,{'owner'})
    # No fictitious checkout or payments. Integrate provider only after credentials + merchant review.
    raise HTTPException(503,'Billing checkout is not enabled. Configure a verified payment provider before accepting payments.')
