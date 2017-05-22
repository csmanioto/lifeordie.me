# https://blog.miguelgrinberg.com/post/designing-a-restful-api-using-flask-restful
# https://flask-restful.readthedocs.io/en/0.3.5/quickstart.html
# http://pycoder.net/bospy/presentation.html#bonus-material

from flask import Flask, jsonify, request
from flask_restful import reqparse, abort, Api, Resource
from score import HelthRandomForest

app = Flask(__name__)
api = Api(app)

class IndexResource(Resource):
    """A welcome Machine Learning API."""

    def get(self):
        return {'message': 'A welcome Machine Learning API.'}


class Helth(Resource):

    def get(self):
        return {'status': 'ok'}

    def post(self):
        data = request.get_json(force=True)
        weigth_data = data['weight']

        '''
        Carrega a classe HelthRandomForest.

        Enviamos para o construtor do HelthRandomForest um
        dicionário.

        Esse dicionário deve conter todas as variáveis que possam ser necessários
        para obter o score através do metodo get_score().
        '''
        ml = HelthRandomForest(**weigth_data)


        '''
        Dicionario helth_user com o score de saúde e
        os dados adicionais recebido pelo POST.
        '''
        helth_user =  {'id': data['user_id'],
                  'score': ml.get_score(),
                  'weight':  weigth_data
                 }
        return helth_user, 201


if __name__ == '__main__':
    api.add_resource(IndexResource, '/')
    api.add_resource(Helth, '/helth/api/v1.0/score')
    app.run(port=5000, debug=True)
