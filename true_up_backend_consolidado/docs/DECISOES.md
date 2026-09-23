# Registro consolidado de decisões

- DEC-STATUS: três valores confirmados; ATIVO é ativo, os dois desligamentos são inativos.
- DEC-COMPETENCIA: competência operacional configurada como JUNHO/2026. Não é inferida alfabeticamente.
- DEC-RH-DDL: campos usados nas consultas foram confirmados por evidência estrutural.
- DEC-AUTH: acesso restrito ao dono da aplicação; token externo ao código e identidade operacional configurada.
- DEC-IDENTIDADE: identidade_id é a chave primária operacional. Matrícula somente resolve identidade inequívoca.
- DEC-TIMEZONE: aplicação configurada como America/Sao_Paulo; timestamps de persistência permanecem gerados pelo MySQL para aderência ao DDL. Validar o timezone do SO antes de produção.
- DEC-DRIVER: PyMySQL adotado para MySQL Community Server 8.4.3.
- RETENCAO: fora deste incremento por decisão do responsável. Dados sensíveis permanecem excluídos das respostas e logs.
