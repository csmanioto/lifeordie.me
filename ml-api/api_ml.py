# https://blog.miguelgrinberg.com/post/designing-a-restful-api-using-flask-restful
# https://flask-restful.readthedocs.io/en/0.3.5/quickstart.html
# http://pycoder.net/bospy/presentation.html#bonus-material

import logging
from flask import Flask, jsonify, request
from flask_restful import reqparse, abort, Api, Resource
import base64, os
import datetime

# Local imports
from score import *
from savedata import kafkaAPI

app = Flask(__name__)
api = Api(app)

log = logging.getLogger(__name__)

class IndexResource(Resource):
    """A welcome Machine Learning API."""

    def get(self):
        return {'message': 'A welcome Machine Learning API.'}


class Helth(Resource):
    def get(self):
        # Test only
        return {'status': 'ok'}

    def post(self):
        #{"nome": "Carlos", "facebookID": 102345, "IP": "200.123.123.123","weight": {"sexo":0,"horotadia":4,"frutadia":1,"carnegordura":0, "atividade":0,"hiptertensao":0,"diabetes":1}}
        data = request.get_json(force=True)
        weigth_data = data['weight']

        ml = HelthCholesterol("Base.csv", "helthcholesterol.pkl")
        score = ml.score(**weigth_data)

        logging.info("Socre: {}".format(score))

        hash =  base64.urlsafe_b64encode(os.urandom(32))
        helth_user = {'Application': 'ML-API',
                      'RequestID': str(hash),
                      'RequestData': str(datetime.datetime.utcnow()),
                      'nome': data['nome'],
                      'facebookID': data['facebookID'],
                      'IP':   data['IP'],
                      'weight': weigth_data,
                      'sexo': weigth_data["sexo"],
                      'hortadia': weigth_data["horotadia"],
                      'frutadia': weigth_data["frutadia"],
                      'carnegordura': weigth_data["carnegordura"],
                      'atividade': weigth_data["atividade"],
                      'hiptertensao' : weigth_data["hiptertensao"],
                      'diabetes': weigth_data["diabetes"],
                      'score': score
                      }

        kafka = kafkaAPI('192.168.18.30:9092')
        kafka.send('app', helth_user)
        return helth_user, 201


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s:ml-api:%(name)s:%(thread)d:%(levelname)s:%(process)d:%(message)s',
        level=logging.INFO,
        filename="ml-api.log"
    )

    api.add_resource(IndexResource, '/')
    api.add_resource(Helth, '/helth/api/v1.0/score_cholesterol')
    print("Iniciando API  na porta 8080")
    app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)
