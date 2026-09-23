import pytest
from backend.schemas.common import owner
from backend.errors import AppError

def test_owner_aceita_identidade(): assert owner({'identidade_id':1})==(1,None)
def test_owner_aceita_matricula_para_resolucao(): assert owner({'matricula':' 001 '})==(None,'001')
def test_owner_obrigatorio():
    with pytest.raises(AppError): owner({})
