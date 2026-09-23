import math
from sqlalchemy.exc import IntegrityError
from ..errors import AppError
class ColaboradorService:
    MAP={'ATIVO':True,'DESLIGAMENTO INVOLUNTÁRIO':False,'DESLIGAMENTO VOLUNTÁRIO':False}
    def __init__(self,r): self.r=r
    def _map(self,x):
        raw=(x.get('status_colaborador') or '').strip().upper(); x['ativo']=self.MAP.get(raw)
        if raw and raw not in self.MAP: x['status_mapeado']='DESCONHECIDO'
        return x
    def listar(self,p):
        rows,total=self.r.listar(p); return {'dados':[self._map(x) for x in rows],'paginacao':meta(p,total)}
    def obter(self,m,a,mes):
        rows=self.r.obter(m,a,mes)
        if not rows: raise AppError('COLABORADOR_NAO_ENCONTRADO','Colaborador nao encontrado.',404)
        if len(rows)>1: raise AppError('COLABORADOR_AMBIGUO','Mais de um colaborador para matricula e competencia.',409)
        return {'dados':self._map(rows[0])}
class LicencaService:
    def __init__(self,r): self.r=r
    def listar(self,p):
        rows,total=self.r.listar(p); return {'dados':rows,'paginacao':meta(p,total)}
    def criar(self,d):
        with self.r.engine.begin() as c:
            lid=self.r.inserir(c,d)
        return {'licenca_id':lid}
    def atualizar(self,lid,d):
        with self.r.engine.begin() as c:
            if not self.r.obter(c,lid,True): raise AppError('LICENCA_NAO_ENCONTRADA','Licenca nao encontrada.',404)
            self.r.atualizar(c,lid,d)
        return {'licenca_id':lid}
def meta(p,total): return {'pagina':p['pagina'],'tamanho':p['tamanho'],'total_itens':total,'total_paginas':math.ceil(total/p['tamanho']) if total else 0}
