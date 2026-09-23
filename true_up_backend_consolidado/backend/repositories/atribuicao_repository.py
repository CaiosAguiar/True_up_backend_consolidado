from sqlalchemy import text
from .base import BaseRepository
class AtribuicaoRepository(BaseRepository):
    def resolver_identidade(self,conn,iid=None,matricula=None):
        if iid: return self.one(conn,'SELECT identidade_id,matricula,ativa FROM true_up_2026.identidade WHERE identidade_id=:id',{'id':iid})
        rows=self.all(conn,'SELECT identidade_id,matricula,ativa FROM true_up_2026.identidade WHERE UPPER(TRIM(matricula))=UPPER(TRIM(:m)) LIMIT 2',{'m':matricula})
        return rows[0] if len(rows)==1 else None
    def ativa(self,conn,iid,lid,lock=False): return self.one(conn,'SELECT * FROM true_up_2026.colaborador_licenca WHERE identidade_id=:i AND licenca_id=:l AND ativa=1'+(' FOR UPDATE' if lock else ''),{'i':iid,'l':lid})
    def contar_ativas(self,conn,lid): return conn.execute(text('SELECT COUNT(*) FROM true_up_2026.colaborador_licenca WHERE licenca_id=:l AND ativa=1'),{'l':lid}).scalar_one()
    def criar(self,conn,iid,lid,origem,motivo,user):
        q="""INSERT INTO true_up_2026.colaborador_licenca(identidade_id,licenca_id,origem_atribuicao,motivo,usuario_operacao,atribuido_por_importacao) VALUES(:i,:l,:o,:m,:u,0)"""
        return conn.execute(text(q),{'i':iid,'l':lid,'o':origem,'m':motivo,'u':user}).lastrowid
    def liberar(self,conn,aid,motivo,user):
        conn.execute(text('UPDATE true_up_2026.colaborador_licenca SET ativa=0,data_liberacao=CURRENT_TIMESTAMP(6),motivo=:m,usuario_operacao=:u WHERE atribuicao_id=:a AND ativa=1'),{'m':motivo,'u':user,'a':aid})
    def listar(self,p):
        w=['1=1']; b={}
        for k in ('identidade_id','licenca_id','ativa'):
            if p.get(k) is not None: w.append('cl.'+k+'=:'+k); b[k]=p[k]
        b.update(limit=p['tamanho'],offset=(p['pagina']-1)*p['tamanho']); c=' AND '.join(w)
        sql="""SELECT cl.atribuicao_id,cl.identidade_id,i.matricula,i.login,i.nome_completo,cl.licenca_id,l.codigo licenca_codigo,l.nome licenca_nome,cl.data_atribuicao,cl.data_liberacao,cl.ativa,cl.origem_atribuicao,cl.motivo,cl.usuario_operacao FROM true_up_2026.colaborador_licenca cl JOIN true_up_2026.identidade i ON i.identidade_id=cl.identidade_id JOIN true_up_2026.licenca l ON l.licenca_id=cl.licenca_id WHERE """
        with self.engine.connect() as x:
            rows=self.all(x,sql+c+' ORDER BY cl.data_atribuicao DESC,cl.atribuicao_id DESC LIMIT :limit OFFSET :offset',b)
            total=x.execute(text('SELECT COUNT(*) FROM true_up_2026.colaborador_licenca cl WHERE '+c),b).scalar_one()
        return rows,total
