from sqlalchemy import text
from .base import BaseRepository
class LicencaRepository(BaseRepository):
    def listar(self,p):
        w=['1=1']; b={}
        if p.get('ativa') is not None: w.append('l.ativa=:ativa'); b['ativa']=p['ativa']
        if p.get('busca'): w.append('(l.codigo LIKE :q OR l.nome LIKE :q OR l.descricao LIKE :q)'); b['q']='%'+p['busca']+'%'
        c=' AND '.join(w); b.update(limit=p['tamanho'],offset=(p['pagina']-1)*p['tamanho'])
        base="""SELECT l.licenca_id,l.aplicacao_id,l.role_id_origem,l.codigo,l.nome,l.descricao,l.role_type,l.classe_catalogo,l.quantidade_contratada,l.controlar_saldo,l.ativa,l.criado_em,l.atualizado_em, SUM(CASE WHEN cl.ativa=1 THEN 1 ELSE 0 END) atribuicoes_ativas, CASE WHEN l.controlar_saldo=1 AND l.quantidade_contratada IS NOT NULL THEN l.quantidade_contratada-SUM(CASE WHEN cl.ativa=1 THEN 1 ELSE 0 END) ELSE NULL END saldo FROM true_up_2026.licenca l LEFT JOIN true_up_2026.colaborador_licenca cl ON cl.licenca_id=l.licenca_id WHERE """
        with self.engine.connect() as x:
            rows=self.all(x,base+c+' GROUP BY l.licenca_id ORDER BY l.nome LIMIT :limit OFFSET :offset',b)
            total=x.execute(text('SELECT COUNT(*) FROM true_up_2026.licenca l WHERE '+c),b).scalar_one()
        return rows,total
    def obter(self,conn,lid,lock=False): return self.one(conn,'SELECT * FROM true_up_2026.licenca WHERE licenca_id=:id'+(' FOR UPDATE' if lock else ''),{'id':lid})
    def inserir(self,conn,d):
        q="""INSERT INTO true_up_2026.licenca(aplicacao_id,role_id_origem,codigo,nome,descricao,role_type,classe_catalogo,quantidade_contratada,controlar_saldo,ativa) VALUES(:aplicacao_id,:role_id_origem,:codigo,:nome,:descricao,:role_type,:classe_catalogo,:quantidade_contratada,:controlar_saldo,:ativa)"""
        r=conn.execute(text(q),d); return r.lastrowid
    def atualizar(self,conn,lid,d):
        allowed={'codigo','nome','descricao','role_type','classe_catalogo','quantidade_contratada','controlar_saldo','ativa'}
        vals={k:v for k,v in d.items() if k in allowed}
        if vals: conn.execute(text('UPDATE true_up_2026.licenca SET '+','.join(f'{k}=:{k}' for k in vals)+' WHERE licenca_id=:id'),{**vals,'id':lid})
