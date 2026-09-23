from sqlalchemy import create_engine

def build_engine(config):
    return create_engine(config['DATABASE_URL'], pool_pre_ping=True,
        pool_size=config['DB_POOL_SIZE'], max_overflow=config['DB_MAX_OVERFLOW'],
        pool_recycle=config['DB_POOL_RECYCLE'], future=True)
