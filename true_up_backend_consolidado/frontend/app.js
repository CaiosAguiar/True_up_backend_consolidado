'use strict';
const $ = (s, r = document) => r.querySelector(s);
const esc = v => String(v ?? '—').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fd = v => v ? new Date(v).toLocaleString('pt-BR', {timeZone: 'UTC'}) : '—'; // MySQL devolve horário sem fuso
const badge = (t, c = '') => `<span class="badge ${c}">${esc(t)}</span>`;
const S = {base: localStorage.getItem('tu_base') || '', token: sessionStorage.getItem('tu_token') || ''};

/* ---------- API ---------- */
async function api(path, {method = 'GET', params, body} = {}) {
  const qs = params ? '?' + new URLSearchParams(Object.entries(params).filter(([, v]) => v !== '' && v != null)) : '';
  let r;
  try {
    r = await fetch(S.base + path + qs, {method, body: body && JSON.stringify(body), headers: {
      'Authorization': 'Bearer ' + S.token, 'Content-Type': 'application/json', 'X-Correlation-ID': crypto.randomUUID()}});
  } catch { throw {mensagem: 'Não foi possível conectar à API. Verifique a URL, se o backend está no ar e o CORS.'}; }
  const j = await r.json().catch(() => ({}));
  if (!r.ok) { if (r.status === 401 && $('#app').hidden === false) logout(); throw j.erro || {mensagem: 'Erro HTTP ' + r.status}; }
  return j;
}
function toast(m, bad) {
  const t = document.createElement('div'); t.className = 'toast' + (bad ? ' bad' : '');
  t.innerHTML = esc(typeof m === 'string' ? m : m.mensagem) + (m.codigo ? `<small>${esc(m.codigo)}${m.correlacao_id ? ' · ' + esc(m.correlacao_id.slice(0, 8)) : ''}</small>` : '');
  $('#toasts').append(t); setTimeout(() => t.remove(), 6000);
}
const fail = e => toast(e, true);

/* ---------- UI helpers ---------- */
const field = (n, l, t = 'text', x = '') => `<label>${l}<input name="${n}" type="${t}" ${x}></label>`;
const check = (n, l, on) => `<label><input type="checkbox" name="${n}" ${on ? 'checked' : ''}>${l}</label>`;
const opts = (a, all = 'Todos') => `<option value="">${all}</option>` + a.map(([v, l]) => `<option value="${esc(v)}">${esc(l)}</option>`).join('');
const table = (cols, rows) => !rows.length ? '<p class="muted">Nenhum registro encontrado.</p>' :
  `<div class="tw"><table><thead><tr>${cols.map(c => `<th>${c[0]}</th>`).join('')}</tr></thead><tbody>${rows.map(r => `<tr>${cols.map(c => `<td>${c[1](r)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
const pager = p => `<div class="pager"><span>${p.total_itens} registro(s) · página ${p.pagina} de ${p.total_paginas || 1}</span>
  <button class="btn ghost sm" data-p="${p.pagina - 1}" ${p.pagina <= 1 ? 'disabled' : ''}>Anterior</button>
  <button class="btn ghost sm" data-p="${p.pagina + 1}" ${p.pagina >= p.total_paginas ? 'disabled' : ''}>Próxima</button></div>`;
const formData = f => { const o = {}; for (const [k, v] of new FormData(f)) if (v.trim() !== '') o[k] = v.trim(); return o; };

function modal(title, html, onSubmit, ok = 'Salvar') {
  const d = $('#dlg');
  d.innerHTML = `<form><h2>${title}</h2>${html}<div class="acts"><button type="button" class="btn ghost" value="x">Cancelar</button><button class="btn">${ok}</button></div></form>`;
  const f = $('form', d);
  $('[value=x]', f).onclick = () => d.close();
  f.onsubmit = async e => { e.preventDefault(); try { await onSubmit(f); d.close(); } catch (x) { fail(x); } };
  d.showModal();
}

/* Tela de listagem paginada genérica */
function listView({title, path, filters = '', cols, btn = '', map = p => p, actions, idKey, novo}) {
  return async main => {
    let pg = 1, rows = [];
    main.innerHTML = `<div class="bar"><h2>${title}</h2>${btn}</div><form class="filters">${filters}<button class="btn">Filtrar</button></form><div id="out"></div>`;
    const form = $('.filters', main), out = $('#out', main);
    const load = async () => {
      out.innerHTML = '<p class="muted">Carregando…</p>';
      try {
        const r = await api(path, {params: map({...Object.fromEntries(new FormData(form)), pagina: pg, tamanho: 15})});
        rows = r.dados; out.innerHTML = table(cols, rows) + pager(r.paginacao);
      } catch (e) { out.innerHTML = ''; fail(e); }
    };
    form.onsubmit = e => { e.preventDefault(); pg = 1; load(); };
    main.onclick = e => {
      const p = e.target.closest('[data-p]'); if (p) { pg = +p.dataset.p; load(); return; }
      const a = e.target.closest('[data-act]'); if (a && actions) actions(a.dataset.act, rows.find(r => String(r[idKey]) === a.dataset.id), load);
      if (e.target.closest('#novo') && novo) novo(load);
    };
    load();
  };
}

/* ---------- Telas ---------- */
const views = {};
const ativoBadge = a => a ? badge('Ativa', 'ok') : badge('Inativa');

views.dashboard = {label: 'Dashboard', render: async main => {
  main.innerHTML = '<div class="bar"><h2>Dashboard</h2></div><div id="k" class="kpis"><p class="muted">Carregando…</p></div>';
  try {
    const {dados: d, competencia: c} = await api('/api/dashboard');
    const k = [['Licenças ativas', d.licencas_ativas], ['Atribuições ativas', d.atribuicoes_ativas], ['Movimentações registradas', d.movimentacoes], [`Colaboradores em ${c.mes}/${c.ano}`, d.colaboradores_competencia]];
    $('#k').innerHTML = k.map(([l, v]) => `<div class="kpi"><b>${esc(v)}</b><span>${esc(l)}</span></div>`).join('');
  } catch (e) { $('#k').innerHTML = ''; fail(e); }
}};

views.colaboradores = {label: 'Colaboradores', render: listView({
  title: 'Colaboradores', path: '/api/colaboradores',
  filters: field('busca', 'Buscar (matrícula, nome, e-mail)') +
    `<label>Status<select name="status">${opts([['ATIVO', 'Ativo'], ['DESLIGAMENTO VOLUNTÁRIO', 'Desligamento voluntário'], ['DESLIGAMENTO INVOLUNTÁRIO', 'Desligamento involuntário']])}</select></label>` +
    `<label>Ordenar por<select name="ordenar_por">${opts([['nome', 'Nome'], ['matricula', 'Matrícula'], ['email', 'E-mail'], ['subarea', 'Subárea'], ['centro_custo', 'Centro de custo']], 'Padrão')}</select></label>` +
    `<label>Direção<select name="direcao"><option value="asc">Crescente</option><option value="desc">Decrescente</option></select></label>`,
  cols: [['Matrícula', r => esc(r.matricula)], ['Nome', r => esc(r.nome)], ['E-mail', r => esc(r.email)],
    ['Situação', r => r.ativo === true ? badge('Ativo', 'ok') : r.ativo === false ? badge('Desligado', 'bad') : badge('Desconhecido', 'warn')],
    ['Subárea', r => esc(r.subarea)], ['Centro de custo', r => esc(r.centro_custo)], ['Cargo', r => esc(r.cargo)]],
  map: p => ({...p, ordenar_por: p.ordenar_por || 'nome'})
})};

function licencaForm(l = {}) {
  return field('codigo', 'Código', 'text', `value="${esc(l.codigo ?? '')}"`) + field('nome', 'Nome *', 'text', `required value="${esc(l.nome ?? '')}"`) +
    field('descricao', 'Descrição', 'text', `value="${esc(l.descricao ?? '')}"`) +
    `<div class="grid2">${field('role_type', 'Tipo (role_type)', 'text', `value="${esc(l.role_type ?? '')}"`)}${field('classe_catalogo', 'Classe do catálogo', 'text', `value="${esc(l.classe_catalogo ?? '')}"`)}</div>` +
    field('quantidade_contratada', 'Quantidade contratada', 'number', `min="0" value="${l.quantidade_contratada ?? ''}"`) +
    check('controlar_saldo', 'Controlar saldo', l.controlar_saldo) + '<br>' + check('ativa', 'Licença ativa', l.ativa ?? 1);
}
function licencaBody(f) {
  const d = formData(f), b = {nome: d.nome, controlar_saldo: f.controlar_saldo.checked, ativa: f.ativa.checked};
  for (const k of ['codigo', 'descricao', 'role_type', 'classe_catalogo']) b[k] = d[k] ?? null;
  b.quantidade_contratada = d.quantidade_contratada != null ? +d.quantidade_contratada : null;
  return b;
}
const novaLicenca = load => modal('Nova licença', licencaForm(), async f => { await api('/api/licencas', {method: 'POST', body: licencaBody(f)}); toast('Licença criada.'); load(); });
views.licencas = {label: 'Licenças', render: listView({
    idKey: 'licenca_id', novo: novaLicenca,
    title: 'Licenças', path: '/api/licencas', btn: '<button class="btn" id="novo">Nova licença</button>',
    filters: field('busca', 'Buscar (código, nome, descrição)') + `<label>Situação<select name="ativa">${opts([['1', 'Ativas'], ['0', 'Inativas']])}</select></label>`,
    cols: [['Código', r => esc(r.codigo)], ['Nome', r => esc(r.nome)], ['Contratadas', r => esc(r.quantidade_contratada)], ['Em uso', r => esc(r.atribuicoes_ativas ?? 0)],
      ['Saldo', r => r.saldo == null ? badge('Sem controle') : badge(r.saldo, r.saldo <= 0 ? 'bad' : r.saldo <= 3 ? 'warn' : 'ok')],
      ['Situação', r => ativoBadge(r.ativa)], ['', r => `<button class="btn ghost sm" data-act="edit" data-id="${r.licenca_id}">Editar</button>`]],
    actions: (a, l, load) => modal('Editar licença #' + l.licenca_id, licencaForm(l), async f => { await api('/api/licencas/' + l.licenca_id, {method: 'PUT', body: licencaBody(f)}); toast('Licença atualizada.'); load(); })
  })};

const owner = (p, t) => `<div class="grid2">${field(p + 'matricula', t + ' — matrícula')}${field(p + 'identidade_id', 'ou identidade_id', 'number', 'min="1"')}</div>`;
function ownerBody(d, p = '') { const o = {}; if (d[p + 'matricula']) o[p + 'matricula'] = d[p + 'matricula']; if (d[p + 'identidade_id']) o[p + 'identidade_id'] = +d[p + 'identidade_id']; return o; }

const novaAtribuicao = load => modal('Nova atribuição',
    owner('', 'Colaborador') + field('licenca_id', 'ID da licença *', 'number', 'min="1" required') + field('motivo', 'Motivo *', 'text', 'required') + field('observacao', 'Observação'),
    async f => { const d = formData(f); await api('/api/atribuicoes', {method: 'POST', body: {...ownerBody(d), licenca_id: +d.licenca_id, motivo: d.motivo, observacao: d.observacao}}); toast('Licença atribuída.'); load(); }, 'Atribuir');
views.atribuicoes = {label: 'Atribuições', render: listView({
    idKey: 'atribuicao_id', novo: novaAtribuicao,
    title: 'Atribuições', path: '/api/atribuicoes', btn: '<button class="btn" id="novo">Nova atribuição</button>',
    filters: field('identidade_id', 'Identidade (ID)', 'number', 'min="1"') + field('licenca_id', 'Licença (ID)', 'number', 'min="1"') + `<label>Situação<select name="ativa">${opts([['1', 'Ativas'], ['0', 'Liberadas']])}</select></label>`,
    cols: [['ID', r => r.atribuicao_id], ['Matrícula', r => esc(r.matricula)], ['Colaborador', r => esc(r.nome_completo)], ['Licença', r => esc((r.licenca_codigo ? r.licenca_codigo + ' · ' : '') + r.licenca_nome)],
      ['Atribuída em', r => fd(r.data_atribuicao)], ['Liberada em', r => fd(r.data_liberacao)], ['Origem', r => esc(r.origem_atribuicao)], ['Situação', r => r.ativa ? badge('Ativa', 'ok') : badge('Liberada')],
      ['', r => r.ativa ? `<button class="btn danger sm" data-act="lib" data-id="${r.atribuicao_id}">Liberar</button>` : '']],
    actions: (a, r, load) => modal('Liberar atribuição #' + r.atribuicao_id, `<p class="muted">${esc(r.nome_completo)} · ${esc(r.licenca_nome)}</p>` + field('motivo', 'Motivo *', 'text', 'required') + field('observacao', 'Observação'),
      async f => { await api(`/api/atribuicoes/${r.atribuicao_id}/liberacao`, {method: 'POST', body: formData(f)}); toast('Licença liberada.'); load(); }, 'Liberar')
  })};

views.transferencias = {label: 'Transferências', render: main => {
  main.innerHTML = `<div class="bar"><h2>Transferência de licenças</h2></div><form id="tf" class="panel" style="max-width:640px">
    ${owner('origem_', 'Origem')}${owner('destino_', 'Destino')}${field('licenca_ids', 'IDs das licenças * (separados por vírgula)', 'text', 'required placeholder="3, 8, 15"')}
    ${field('motivo', 'Motivo *', 'text', 'required')}${field('observacao', 'Observação')}
    <p class="muted">A operação é atômica: se uma licença falhar, nenhuma é transferida.</p><button class="btn">Transferir</button></form>`;
  $('#tf').onsubmit = async e => {
    e.preventDefault(); const d = formData(e.target);
    const ids = d.licenca_ids.split(',').map(s => +s.trim()).filter(Boolean);
    try {
      const r = await api('/api/transferencias', {method: 'POST', body: {...ownerBody(d, 'origem_'), ...ownerBody(d, 'destino_'), licenca_ids: ids, motivo: d.motivo, observacao: d.observacao}});
      toast(`${r.transferencias.length} licença(s) transferida(s).`); e.target.reset();
    } catch (x) { fail(x); }
  };
}};

views.historico = {label: 'Histórico', render: listView({
  title: 'Histórico de movimentações', path: '/api/historico',
  filters: `<label>Tipo<select name="tipo">${opts([['ATRIBUICAO', 'Atribuição'], ['LIBERACAO', 'Liberação'], ['TRANSFERENCIA', 'Transferência']])}</select></label>` +
    field('licenca_id', 'Licença (ID)', 'number', 'min="1"') + field('inicio', 'De', 'date') + field('fim', 'Até', 'date'),
  map: p => ({...p, fim: p.fim ? p.fim + ' 23:59:59' : ''}),
  cols: [['Data', r => fd(r.data_movimentacao)], ['Tipo', r => badge(r.tipo_movimentacao, r.tipo_movimentacao === 'LIBERACAO' ? 'bad' : r.tipo_movimentacao === 'ATRIBUICAO' ? 'ok' : 'warn')],
    ['Licença', r => esc(r.licenca_nome)], ['Origem', r => esc(r.matricula_origem)], ['Destino', r => esc(r.matricula_destino)], ['Motivo', r => `<span title="${esc(r.observacao || '')}">${esc(r.motivo)}</span>`],
    ['Usuário', r => esc(r.usuario_operacao)], ['Correlação', r => esc(String(r.correlacao_id || '').slice(0, 8))]]
})};

/* ---------- Navegação e sessão ---------- */
function route() {
  const k = views[location.hash.slice(1)] ? location.hash.slice(1) : 'dashboard';
  location.hash = k; const main = $('#main'); main.onclick = null;
  document.querySelectorAll('#nav a').forEach(a => a.classList.toggle('on', a.hash === '#' + k));
  views[k].render(main); health();
}
async function health() {
  try { const r = await fetch(S.base + '/health'); $('#hl').className = 'dot ' + (r.ok ? 'ok' : 'bad'); $('#ht').textContent = r.ok ? 'API e banco online' : 'Banco indisponível'; }
  catch { $('#hl').className = 'dot bad'; $('#ht').textContent = 'API offline'; }
}
function enter() {
  $('#login').hidden = true; $('#app').hidden = false;
  $('#nav').innerHTML = Object.entries(views).map(([k, v]) => `<a href="#${k}">${v.label}</a>`).join('');
  route();
}
function logout() { sessionStorage.removeItem('tu_token'); S.token = ''; $('#app').hidden = true; $('#login').hidden = false; $('#lerr').textContent = 'Sessão encerrada ou token inválido.'; }
$('#out').onclick = logout;
window.addEventListener('hashchange', () => !$('#app').hidden && route());
$('#base').value = S.base;
$('#lf').onsubmit = async e => {
  e.preventDefault(); S.base = $('#base').value.trim().replace(/\/$/, ''); S.token = $('#tok').value.trim(); $('#lerr').textContent = '';
  try { await api('/api/dashboard'); localStorage.setItem('tu_base', S.base); sessionStorage.setItem('tu_token', S.token); $('#tok').value = ''; enter(); }
  catch (x) { $('#lerr').textContent = x.mensagem || 'Falha ao autenticar.'; }
};
if (S.token) enter();
