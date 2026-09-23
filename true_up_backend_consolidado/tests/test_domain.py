from backend.services.core_services import ColaboradorService

def test_status_reais():
    class R: pass
    s=ColaboradorService(R())
    assert s._map({'status_colaborador':'ATIVO'})['ativo'] is True
    assert s._map({'status_colaborador':'DESLIGAMENTO INVOLUNTÁRIO'})['ativo'] is False
    assert s._map({'status_colaborador':'DESLIGAMENTO VOLUNTÁRIO'})['ativo'] is False
