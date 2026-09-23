# TRUE-UP 2026 Back-End consolidado

API Flask em camadas para MySQL 8.4.3, schemas `true_up_2026` e `rh`.

## Decisões incorporadas
- Status: `ATIVO=true`; desligamentos voluntário e involuntário `false`.
- Competência configurada: `JUNHO/2026`, alterável por ambiente.
- Proprietário: persistência por `identidade_id`; matrícula é resolvida para uma única identidade.
- Autorização: usuário único, token Bearer controlado por ambiente; `usuario_operacao` vem de `OWNER_ID`.
- Driver: PyMySQL.
- Timezone da aplicação configurado por `APP_TIMEZONE`; datas persistidas usam `CURRENT_TIMESTAMP(6)` do MySQL para coerência com o DDL.
- Sem exclusão física e sem criação/alteração automática de tabelas.

## Instalação no PowerShell
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
flask --app wsgi:app run
```

Gere segredos:
```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Todas as rotas `/api/*` exigem `Authorization: Bearer <OWNER_TOKEN>`.

## Endpoints
- `GET /health`
- `GET /api/colaboradores`
- `GET /api/colaboradores/{matricula}`
- `GET/POST /api/licencas`
- `PUT /api/licencas/{id}`
- `GET/POST /api/atribuicoes`
- `POST /api/atribuicoes/{id}/liberacao`
- `POST /api/transferencias`
- `GET /api/historico`
- `GET /api/dashboard`

## Testes
```powershell
pytest
ruff check .
```

## Operações transacionais
Atribuição cria vínculo e movimentação no mesmo `engine.begin()`. Liberação desativa o vínculo e cria a movimentação na mesma transação. Transferência múltipla bloqueia registros com `FOR UPDATE`, processa todos os itens e efetua commit único; qualquer exceção provoca rollback integral.
