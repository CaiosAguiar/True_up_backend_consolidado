from sqlalchemy import text
from .base import BaseRepository
COLS='id,matricula,nome,email,email_gestor,status_colaborador,regional,filial,diretoria_1,gerencia_sr,subarea,centro_custo,cargo,nome_empresa,ano,mes'
class ColaboradorRepository(BaseRepository):
    def listar(self,p):
        w=['ano=:ano','UPPER(TRIM(mes))=:mes']; b={'ano':p['ano'],'mes':p['mes']}
        if p['busca']: w.append('(matricula LIKE :q OR nome LIKE :q OR email LIKE :q)'); b['q']='%'+p['busca']+'%'
        for col,val in p['filtros'].items(): w.append(f'{col}=:{col}'); b[col]=val
        c=' AND '.join(w); b.update(limit=p['tamanho'],offset=(p['pagina']-1)*p['tamanho'])
        with self.engine.connect() as x:
            rows=self.all(x,f'SELECT {COLS} FROM rh.colaboradores_rh WHERE {c} ORDER BY {p["ordem"]} {p["direcao"]} LIMIT :limit OFFSET :offset',b)
            total=x.execute(text(f'SELECT COUNT(*) FROM rh.colaboradores_rh WHERE {c}'),b).scalar_one()
        return rows,total
    def obter(self,matricula,ano,mes):
        with self.engine.connect() as x: return self.all(x,f'SELECT {COLS} FROM rh.colaboradores_rh WHERE TRIM(matricula)=:m AND ano=:a AND UPPER(TRIM(mes))=:mes LIMIT 2',{'m':matricula,'a':ano,'mes':mes})
