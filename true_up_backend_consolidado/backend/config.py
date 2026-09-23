import os
class Config:
    SECRET_KEY=os.getenv('SECRET_KEY','')
    DATABASE_URL=os.getenv('DATABASE_URL','')
    OWNER_TOKEN=os.getenv('OWNER_TOKEN','')
    OWNER_ID=os.getenv('OWNER_ID','dono-aplicacao')
    APP_TIMEZONE=os.getenv('APP_TIMEZONE','America/Sao_Paulo')
    CURRENT_YEAR=int(os.getenv('CURRENT_YEAR','2026'))
    CURRENT_MONTH=os.getenv('CURRENT_MONTH','JUNHO').upper()
    DB_POOL_SIZE=int(os.getenv('DB_POOL_SIZE','5'))
    DB_MAX_OVERFLOW=int(os.getenv('DB_MAX_OVERFLOW','10'))
    DB_POOL_RECYCLE=int(os.getenv('DB_POOL_RECYCLE','1800'))
    DEFAULT_PAGE_SIZE=int(os.getenv('DEFAULT_PAGE_SIZE','25'))
    MAX_PAGE_SIZE=int(os.getenv('MAX_PAGE_SIZE','100'))
    TESTING=False
    @classmethod
    def validate(cls):
        missing=[x for x in ('SECRET_KEY','DATABASE_URL','OWNER_TOKEN','OWNER_ID') if not getattr(cls,x)]
        if missing: raise RuntimeError('Variaveis obrigatorias ausentes: '+', '.join(missing))
        if not cls.DATABASE_URL.startswith('mysql+pymysql://'): raise RuntimeError('DATABASE_URL deve usar mysql+pymysql')
