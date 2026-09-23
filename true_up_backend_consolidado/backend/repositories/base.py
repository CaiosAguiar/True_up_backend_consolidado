from sqlalchemy import text
class BaseRepository:
    def __init__(self,engine): self.engine=engine
    @staticmethod
    def one(conn,sql,p):
        row=conn.execute(text(sql),p).mappings().first(); return dict(row) if row else None
    @staticmethod
    def all(conn,sql,p): return [dict(x) for x in conn.execute(text(sql),p).mappings()]
