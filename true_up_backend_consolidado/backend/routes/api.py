from flask import Blueprint,current_app,g,jsonify,request
from sqlalchemy import text
from ..security import owner_required
from ..errors import AppError
from ..schemas.common import integer,page,required_str,optional_int,owner
from ..repositories.colaborador_repository import ColaboradorRepository
from ..repositories.licenca_repository import LicencaRepository
from ..repositories.atribuicao_repository import AtribuicaoRepository
from ..repositories.movimentacao_repository import MovimentacaoRepository
from ..services.core_services import ColaboradorService,LicencaService,meta
from ..services.operacao_service import OperacaoService
bp=Blueprint('api',__name__)
def repos():
    e=current_app.extensions['db_engine']; return e,ColaboradorRepository(e),LicencaRepository(e),AtribuicaoRepository(e),MovimentacaoRepository(e)
def paging():
    a,b=page(request.args,current_app.config); return {'pagina':a,'tamanho':b}
def body():
    d=request.get_json(silent=True)
    if not isinstance(d,dict): raise AppError('JSON_INVALIDO','Corpo JSON obrigatorio.')
    return d
@bp.get('/health')
def health():
    try:
        with current_app.extensions['db_engine'].connect() as c: c.execute(text('SELECT 1'))
        return jsonify({'status':'ok','database':'ok'}),200
    except Exception: return jsonify({'status':'degraded','database':'unavailable'}),503
@bp.get('/api/colaboradores')
@owner_required
def colaboradores():
    _,r,_,_,_=repos(); p=paging(); p.update(ano=integer(request.args.get('ano'),'ano',2000,2100, current_app.config['CURRENT_YEAR']),mes=(request.args.get('mes') or current_app.config['CURRENT_MONTH']).strip().upper(),busca=(request.args.get('busca') or '').strip()[:150])
    amap={'matricula','nome','email','subarea','centro_custo'}; p['ordem']=request.args.get('ordenar_por','nome'); p['direcao']=request.args.get('direcao','asc').upper()
    if p['ordem'] not in amap or p['direcao'] not in {'ASC','DESC'}: raise AppError('ORDENACAO_INVALIDA','Ordenacao nao permitida.')
    fm={'status':'status_colaborador','regional':'regional','filial':'filial','diretoria_1':'diretoria_1','gerencia_sr':'gerencia_sr','subarea':'subarea','centro_custo':'centro_custo'}; p['filtros']={v:request.args[k][:150] for k,v in fm.items() if request.args.get(k)}
    return jsonify(ColaboradorService(r).listar(p))
@bp.get('/api/colaboradores/<matricula>')
@owner_required
def colaborador(matricula):
    _,r,_,_,_=repos(); ano=integer(request.args.get('ano'),'ano',2000,2100,current_app.config['CURRENT_YEAR']); mes=(request.args.get('mes') or current_app.config['CURRENT_MONTH']).upper()
    return jsonify(ColaboradorService(r).obter(matricula.strip(),ano,mes))
@bp.get('/api/licencas')
@owner_required
def licencas():
    _,_,r,_,_=repos(); p=paging(); p['busca']=(request.args.get('busca') or '').strip()[:150]; p['ativa']=None if request.args.get('ativa') is None else integer(request.args.get('ativa'),'ativa',0,1)
    return jsonify(LicencaService(r).listar(p))
@bp.post('/api/licencas')
@owner_required
def criar_licenca():
    _,_,r,_,_=repos(); d=body(); d={k:d.get(k) for k in ('aplicacao_id','role_id_origem','codigo','nome','descricao','role_type','classe_catalogo','quantidade_contratada','controlar_saldo','ativa')}; d['nome']=required_str(d,'nome',255); d['controlar_saldo']=int(bool(d.get('controlar_saldo'))); d['ativa']=int(d.get('ativa',1) is not False)
    return jsonify(LicencaService(r).criar(d)),201
@bp.put('/api/licencas/<int:lid>')
@owner_required
def editar_licenca(lid):
    _,_,r,_,_=repos(); return jsonify(LicencaService(r).atualizar(lid,body()))
def op():
    e,_,l,a,m=repos(); return OperacaoService(e,a,l,m)
@bp.get('/api/atribuicoes')
@owner_required
def atribuicoes():
    _,_,_,r,_=repos(); p=paging()
    for k in ('identidade_id','licenca_id'): p[k]=None if request.args.get(k) is None else integer(request.args.get(k),k)
    p['ativa']=None if request.args.get('ativa') is None else integer(request.args.get('ativa'),'ativa',0,1)
    rows,total=r.listar(p); return jsonify({'dados':rows,'paginacao':meta(p,total)})
@bp.post('/api/atribuicoes')
@owner_required
def atribuir():
    d=body(); iid,mat=owner(d); d['identidade_id']=iid; d['matricula']=mat; d['licenca_id']=integer(d.get('licenca_id'),'licenca_id'); d['motivo']=required_str(d,'motivo'); return jsonify(op().atribuir(d,g.usuario_operacao,g.correlacao_id)),201
@bp.post('/api/atribuicoes/<int:aid>/liberacao')
@owner_required
def liberar(aid):
    d=body(); d['motivo']=required_str(d,'motivo'); return jsonify(op().liberar(aid,d,g.usuario_operacao,g.correlacao_id))
@bp.post('/api/transferencias')
@owner_required
def transferir():
    d=body(); oi,om=owner(d,'origem_'); di,dm=owner(d,'destino_'); ids=d.get('licenca_ids')
    if not isinstance(ids,list) or not ids: raise AppError('LICENCAS_OBRIGATORIAS','licenca_ids deve ser lista nao vazia.')
    d.update(origem_identidade_id=oi,origem_matricula=om,destino_identidade_id=di,destino_matricula=dm,licenca_ids=[integer(v,'licenca_id') for v in ids],motivo=required_str(d,'motivo'))
    if len(set(d['licenca_ids']))!=len(d['licenca_ids']): raise AppError('LICENCAS_DUPLICADAS','licenca_ids contem duplicidade.')
    return jsonify(op().transferir(d,g.usuario_operacao,g.correlacao_id))
@bp.get('/api/historico')
@owner_required
def historico():
    _,_,_,_,r=repos(); p=paging(); p.update(tipo_movimentacao=request.args.get('tipo'),licenca_id=request.args.get('licenca_id'),inicio=request.args.get('inicio'),fim=request.args.get('fim')); rows,total=r.listar(p); return jsonify({'dados':rows,'paginacao':meta(p,total)})
@bp.get('/api/dashboard')
@owner_required
def dashboard():
    e,_,_,_,_=repos()
    with e.connect() as c:
        q=lambda s: c.execute(text(s)).scalar_one()
        data={'licencas_ativas':q('SELECT COUNT(*) FROM true_up_2026.licenca WHERE ativa=1'),'atribuicoes_ativas':q('SELECT COUNT(*) FROM true_up_2026.colaborador_licenca WHERE ativa=1'),'movimentacoes':q('SELECT COUNT(*) FROM true_up_2026.movimentacao_licenca'),'colaboradores_competencia':c.execute(text('SELECT COUNT(*) FROM rh.colaboradores_rh WHERE ano=:a AND UPPER(TRIM(mes))=:m'),{'a':current_app.config['CURRENT_YEAR'],'m':current_app.config['CURRENT_MONTH']}).scalar_one()}
    return jsonify({'dados':data,'competencia':{'ano':current_app.config['CURRENT_YEAR'],'mes':current_app.config['CURRENT_MONTH']}})
