def test_transferencia_usa_contexto_transacional():
    from pathlib import Path
    source=Path('backend/services/operacao_service.py').read_text(encoding='utf-8')
    assert 'with self.engine.begin() as c:' in source
    assert "tipo_movimentacao='TRANSFERENCIA'" in source
    assert 'DELETE FROM' not in source.upper()
