from flask import jsonify,g
class AppError(Exception):
    def __init__(self,code,message,status=400,details=None):
        super().__init__(message); self.code=code; self.message=message; self.status=status; self.details=details

def register_errors(app):
    @app.errorhandler(AppError)
    def handled(e):
        body={'erro':{'codigo':e.code,'mensagem':e.message,'correlacao_id':g.get('correlacao_id')}}
        if e.details: body['erro']['detalhes']=e.details
        return jsonify(body),e.status
    @app.errorhandler(404)
    def missing(_): return jsonify({'erro':{'codigo':'ROTA_NAO_ENCONTRADA','mensagem':'Rota nao encontrada.','correlacao_id':g.get('correlacao_id')}}),404
    @app.errorhandler(Exception)
    def unexpected(e):
        app.logger.exception('erro_nao_tratado correlacao_id=%s',g.get('correlacao_id'))
        return jsonify({'erro':{'codigo':'ERRO_INTERNO','mensagem':'Erro interno.','correlacao_id':g.get('correlacao_id')}}),500
