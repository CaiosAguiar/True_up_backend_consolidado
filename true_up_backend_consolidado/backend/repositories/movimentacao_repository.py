from sqlalchemy import text
from .base import BaseRepository
class MovimentacaoRepository(BaseRepository):
    def criar(self,conn,**p):
        q="""INSERT INTO true_up_2026.movimentacao_licenca(licenca_id,atribuicao_origem_id,atribuicao_destino_id,identidade_origem_id,identidade_destino_id,matricula_origem,matricula_destino,tipo_movimentacao,usuario_operacao,motivo,observacao,correlacao_id) VALUES(:licenca_id,:atribuicao_origem_id,:atribuicao_destino_id,:identidade_origem_id,:identidade_destino_id,:matricula_origem,:matricula_destino,:tipo_movimentacao,:usuario_operacao,:motivo,:observacao,:correlacao_id)"""
        conn.execute(text(q),p)
    def listar(self,p):
        w=['1=1']; b={}
        for k in ('tipo_movimentacao','licenca_id'):
            if p.get(k): w.append('m.'+k+'=:'+k); b[k]=p[k]
        if p.get('inicio'): w.append('m.data_movimentacao>=:inicio'); b['inicio']=p['inicio']
        if p.get('fim'): w.append('m.data_movimentacao<=:fim'); b['fim']=p['fim']
        b.update(limit=p['tamanho'],offset=(p['pagina']-1)*p['tamanho']); c=' AND '.join(w)
        with self.engine.connect() as x:
            rows=self.all(x,'SELECT m.*,l.codigo licenca_codigo,l.nome licenca_nome FROM true_up_2026.movimentacao_licenca m JOIN true_up_2026.licenca l ON l.licenca_id=m.licenca_id WHERE '+c+' ORDER BY m.data_movimentacao DESC,m.movimentacao_id DESC LIMIT :limit OFFSET :offset',b)
            total=x.execute(text('SELECT COUNT(*) FROM true_up_2026.movimentacao_licenca m WHERE '+c),b).scalar_one()
        return rows,total
