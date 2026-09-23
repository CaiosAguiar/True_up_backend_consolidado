import hmac,uuid
from functools import wraps
from flask import current_app,g,request
from .errors import AppError

def register_security(app):
    @app.before_request
    def context():
        raw=request.headers.get('X-Correlation-ID','')
        try: g.correlacao_id=str(uuid.UUID(raw)) if raw else str(uuid.uuid4())
        except ValueError: g.correlacao_id=str(uuid.uuid4())
    @app.after_request
    def headers(resp):
        resp.headers['X-Correlation-ID']=g.correlacao_id
        resp.headers['Cache-Control']='no-store'; resp.headers['X-Content-Type-Options']='nosniff'
        return resp

def owner_required(fn):
    @wraps(fn)
    def wrapper(*a,**kw):
        supplied=request.headers.get('Authorization','')
        expected='Bearer '+current_app.config['OWNER_TOKEN']
        if not current_app.config['OWNER_TOKEN'] or not hmac.compare_digest(supplied,expected):
            raise AppError('NAO_AUTENTICADO','Autenticacao obrigatoria.',401)
        g.usuario_operacao=current_app.config['OWNER_ID']
        return fn(*a,**kw)
    return wrapper
