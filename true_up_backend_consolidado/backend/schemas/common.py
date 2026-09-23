from datetime import datetime
from . import __name__
from ..errors import AppError
MONTHS={'JANEIRO':1,'FEVEREIRO':2,'MARCO':3,'MARÇO':3,'ABRIL':4,'MAIO':5,'JUNHO':6,'JULHO':7,'AGOSTO':8,'SETEMBRO':9,'OUTUBRO':10,'NOVEMBRO':11,'DEZEMBRO':12}
def integer(v,name,minimum=1,maximum=None,default=None):
    if v is None: v=default
    try: n=int(v)
    except (TypeError,ValueError): raise AppError('PARAMETRO_INVALIDO',f'{name} deve ser inteiro.')
    if n<minimum or (maximum is not None and n>maximum): raise AppError('PARAMETRO_INVALIDO',f'{name} fora do intervalo.')
    return n
def page(args,config): return integer(args.get('pagina'),'pagina',default=1),integer(args.get('tamanho'),'tamanho',maximum=config['MAX_PAGE_SIZE'],default=config['DEFAULT_PAGE_SIZE'])
def required_str(data,name,maxlen=1000):
    v=data.get(name)
    if not isinstance(v,str) or not v.strip(): raise AppError('CAMPO_OBRIGATORIO',f'{name} e obrigatorio.')
    if len(v.strip())>maxlen: raise AppError('CAMPO_INVALIDO',f'{name} excede o tamanho permitido.')
    return v.strip()
def optional_int(data,name): return None if data.get(name) in (None,'') else integer(data.get(name),name)
def owner(data,prefix=''):
    iid=optional_int(data,prefix+'identidade_id'); mat=data.get(prefix+'matricula')
    mat=mat.strip() if isinstance(mat,str) and mat.strip() else None
    if iid is None and mat is None: raise AppError('PROPRIETARIO_OBRIGATORIO','Informe identidade_id ou matricula.')
    return iid,mat
