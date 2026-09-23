from sqlalchemy.exc import IntegrityError
from ..errors import AppError
class OperacaoService:
    def __init__(self,engine,atr,lic,mov): self.engine=engine; self.atr=atr; self.lic=lic; self.mov=mov
    def _ident(self,c,iid,mat):
        x=self.atr.resolver_identidade(c,iid,mat)
        if not x: raise AppError('IDENTIDADE_NAO_RESOLVIDA','Proprietario nao resolve exatamente uma identidade valida.',409)
        if not x.get('ativa'): raise AppError('IDENTIDADE_INATIVA','Identidade inativa.',409)
        return x
    def _lic(self,c,lid):
        l=self.lic.obter(c,lid,True)
        if not l or not l['ativa']: raise AppError('LICENCA_INATIVA_OU_INEXISTENTE','Licenca inexistente ou inativa.',409)
        if l['controlar_saldo'] and l['quantidade_contratada'] is not None and self.atr.contar_ativas(c,lid)>=l['quantidade_contratada']:
            raise AppError('SALDO_ESGOTADO','Saldo da licenca esgotado.',409)
        return l
    def atribuir(self,d,user,corr):
        try:
            with self.engine.begin() as c:
                i=self._ident(c,d.get('identidade_id'),d.get('matricula')); self._lic(c,d['licenca_id'])
                if self.atr.ativa(c,i['identidade_id'],d['licenca_id'],True): raise AppError('LICENCA_DUPLICADA','Proprietario ja possui a licenca ativa.',409)
                aid=self.atr.criar(c,i['identidade_id'],d['licenca_id'],'MANUAL',d['motivo'],user)
                self.mov.criar(c,licenca_id=d['licenca_id'],atribuicao_origem_id=None,atribuicao_destino_id=aid,identidade_origem_id=None,identidade_destino_id=i['identidade_id'],matricula_origem=None,matricula_destino=i.get('matricula'),tipo_movimentacao='ATRIBUICAO',usuario_operacao=user,motivo=d['motivo'],observacao=d.get('observacao'),correlacao_id=corr)
            return {'atribuicao_id':aid}
        except IntegrityError as e: raise AppError('LICENCA_DUPLICADA','Vinculo ativo duplicado.',409) from e
    def liberar(self,aid,d,user,corr):
        with self.engine.begin() as c:
            a=self.atr.one(c,'SELECT * FROM true_up_2026.colaborador_licenca WHERE atribuicao_id=:a FOR UPDATE',{'a':aid})
            if not a: raise AppError('ATRIBUICAO_NAO_ENCONTRADA','Atribuicao nao encontrada.',404)
            if not a['ativa']: raise AppError('ATRIBUICAO_JA_LIBERADA','Atribuicao ja liberada.',409)
            self.atr.liberar(c,aid,d['motivo'],user)
            self.mov.criar(c,licenca_id=a['licenca_id'],atribuicao_origem_id=aid,atribuicao_destino_id=None,identidade_origem_id=a['identidade_id'],identidade_destino_id=None,matricula_origem=a['matricula'],matricula_destino=None,tipo_movimentacao='LIBERACAO',usuario_operacao=user,motivo=d['motivo'],observacao=d.get('observacao'),correlacao_id=corr)
        return {'atribuicao_id':aid,'ativa':False}
    def transferir(self,d,user,corr):
        with self.engine.begin() as c:
            origem=self._ident(c,d.get('origem_identidade_id'),d.get('origem_matricula')); destino=self._ident(c,d.get('destino_identidade_id'),d.get('destino_matricula'))
            if origem['identidade_id']==destino['identidade_id']: raise AppError('ORIGEM_IGUAL_DESTINO','Origem e destino devem ser diferentes.',400)
            result=[]
            for lid in d['licenca_ids']:
                self._lic(c,lid); a=self.atr.ativa(c,origem['identidade_id'],lid,True)
                if not a: raise AppError('LICENCA_NAO_ATRIBUIDA_ORIGEM',f'Origem nao possui licenca ativa {lid}.',409)
                if self.atr.ativa(c,destino['identidade_id'],lid,True): raise AppError('LICENCA_DUPLICADA_DESTINO',f'Destino ja possui licenca ativa {lid}.',409)
                self.atr.liberar(c,a['atribuicao_id'],d['motivo'],user)
                novo=self.atr.criar(c,destino['identidade_id'],lid,'TRANSFERENCIA',d['motivo'],user)
                self.mov.criar(c,licenca_id=lid,atribuicao_origem_id=a['atribuicao_id'],atribuicao_destino_id=novo,identidade_origem_id=origem['identidade_id'],identidade_destino_id=destino['identidade_id'],matricula_origem=origem.get('matricula'),matricula_destino=destino.get('matricula'),tipo_movimentacao='TRANSFERENCIA',usuario_operacao=user,motivo=d['motivo'],observacao=d.get('observacao'),correlacao_id=corr)
                result.append({'licenca_id':lid,'atribuicao_origem_id':a['atribuicao_id'],'atribuicao_destino_id':novo})
        return {'transferencias':result}
