# https://blog.miguelgrinberg.com/post/designing-a-restful-api-using-flask-restful
# https://flask-restful.readthedocs.io/en/0.3.5/quickstart.html
# http://pycoder.net/bospy/presentation.html#bonus-material

import logging
from configparser import ConfigParser
from flask import Flask, jsonify, request
from flask_restful import reqparse, abort, Api, Resource
import base64, os
import datetime

# Local imports
from score import *
from savedata import kafkaAPI

config = ConfigParser()
try:
    config.read("config.ini")

    config_kafka_server = config.get('kafka', 'broken')
    config_kafka_topic = config.get('kafka', 'topic')

    config_api_tcp_port = config.getint('api', 'tcp_port')
    config_flask_debug = config.getboolean('api', 'flash_debug')
    config_flask_reloader = config.getboolean('api', 'flash_reloader')

    config_log_file = config.get('log', 'logfile')
    config_log_level = config.get('log', 'loglevel')

except:
    config_kafka_server = '192.168.18.30:9092'
    config_kafka_topic = 'app'
    config_api_tcp_port = 8080
    api_debug = True
    config_log_file = ml - api.log

log = logging.getLogger(__name__)

app = Flask(__name__)
api = Api(app)


class IndexResource(Resource):
    """A welcome Machine Learning API."""

    def get(self):
        return {'message': 'A welcome Machine Learning API.'}


class Helth(Resource):
    def get(self):
        # Test only
        return {'status': 'ok'}

    def post(self):
        # {"nome": "Carlos", "facebookID": 102345, "IP": "200.123.123.123","weight": {"sexo":0,"horotadia":4,"frutadia":1,"carnegordura":0, "atividade":0,"hiptertensao":0,"diabetes":1}}
        data = request.get_json(force=True)
        weigth_data = data['weight']

        ml = HelthCholesterol("Base.csv", "helthcholesterol.pkl")
        score = ml.score(**weigth_data)

        logging.info("Socre: {}".format(score))

        hash = base64.urlsafe_b64encode(os.urandom(32))



        helth_user = {'Application': 'ML-API',
                      'RequestID': str(hash),
                      'RequestData': str(datetime.datetime.utcnow()),
                      'nome': data['nome'],
                      'facebookID': data['facebookID'],
                      'IP': data['IP'],
                      'sexo': weigth_data["sexo"],
                      'idade':  weigth_data["idade"],
                      'imc' : weigth_data["imc"],
                      'hortadia': weigth_data["hortadia"],
                      'frutadia': weigth_data["frutadia"],
                      'carnegordura': weigth_data["carnegordura"],
                      'atividade': weigth_data["atividade"],
                      'hiptertensao': weigth_data["hiptertensao"],
                      'diabetes': weigth_data["diabetes"],
                      'score': score
                      }

        kafka = kafkaAPI(config_kafka_server)
        kafka.send(config_kafka_topic, helth_user)
        return helth_user, 201


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s:ml-api:%(name)s:%(thread)d:%(levelname)s:%(process)d:%(message)s',
        level=config_log_level,
        filename=config_log_file
    )

    api.add_resource(IndexResource, '/')
    api.add_resource(Helth, '/helth/api/v1.0/score_cholesterol')
    print("Iniciando API  na porta 8080")
    app.run(host='0.0.0.0', port=config_api_tcp_port, debug=config_flask_debug, use_reloader=config_flask_reloader)
