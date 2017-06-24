from pymongo import MongoClient
from kafka import KafkaConsumer
from kafka.common import KafkaError


import requests
import logging
import json
from datetime import datetime
from configparser import ConfigParser
import threading, queue


config = ConfigParser()
try:
    config.read("config.ini")

    config_kafka_server = config.get('kafka', 'broken')
    config_kafka_topic = config.get('kafka', 'topic')
    config_kafka_group_id = config.get('kafka', 'group_id')


    config_mongo_server = config.get('mongo', 'servers')
    config_mongo_db = config.get('mongo', 'db')
    config_mongo_collection = config.get('mongo', 'collection')

    config_log_file = config.get('log', 'logfile')
    config_log_level = config.get('log', 'loglevel')

except:
    config_kafka_server = '192.168.18.30:9092'
    config_kafka_topic =  'app'
    config_kafka_group_id = 'mongoconsumer'


    config_mongo_server = '192.168.18.30:27017'
    config_mongo_db = 'lifeordieDB'
    config_mongo_collection = 'resultados'

    config_log_file = 'kconsumer.log'
    config_log_level = 'DEBUG'

log = logging.getLogger(__name__)


class GeoIP(object):
        def __init__(self, IP):
            try:
                send_url = 'http://freegeoip.net/json/{}'.format(IP)
                r = requests.get(send_url)
                self.geojson = json.loads(r.text)
            except Exception as e :
                log.error("Error on get GeoIP {}".format(e))


        def getlatlong(self):
            latlon = dict()
            latlon['lat'] = self.geojson['latitude']
            latlon['lon'] = self.geojson['longitude']
            return latlon

        def getRegion(self):
            region = dict()
            region['Estado'] = self.geojson['region_name']
            region['Cidadade'] = self.geojson['city']
            region['Pais'] = self.geojson['country_code']
            return region




class Mongo(object):
    def __init__(self, mongoserver, mongodb, collection):
        try:
            conn = MongoClient("mongodb://{}".format(mongoserver))
            self.client = conn[mongodb][collection]
        except Exception as e:
            log.error("Erro ao conectar no hostname: {0} - {1}".format(mongoserver, e))


    def save(self, data):
        try:
            db = self.client
            result = db.insert_one(data)
            log.info("Dado inserido no mongo com sucesso: {0}".format(result))
            return result
        except  Exception as e:
            log.error("Erro ao inserir no MongoDB")
        finally:
            log.debug("Finalizando conexão com o MongodDB")
            self.client.close()


class Consumer(object):
    def __init__(self, topic, kafkaserver, kafka_group_id, mongooserver, mongodb, collection):
        self.mongoo_server = mongooserver
        self.mongo_db = mongodb
        self.mongo_collection = collection
        self.consumer = KafkaConsumer(topic,
                                      bootstrap_servers = kafkaserver,
                                      group_id = kafka_group_id,
                                      value_deserializer = lambda m: json.loads(m.decode('ascii')),
                                      api_version=(0, 10, 1),
                                      auto_offset_reset='earliest')

    def flush(self):

        try:
            mongo = Mongo(self.mongoo_server, self.mongo_db, self.mongo_collection)
            log.debug("Abrindo conexão com os Brokens...")
            for message in self.consumer:
                self.consumer.commit()
                data = message.value
                data["RequestData"] = datetime.strptime(data["RequestData"], '%Y-%m-%d %H:%M:%S.%f')

                geoip = GeoIP(data["IP"])
                data['geoIP_Pais'] = geoip.getRegion()['Pais']
                data['geoIP_Estado'] = geoip.getRegion()['Estado']
                data['geoIP_Cidadade'] = geoip.getRegion()['Cidadade']

                data['geoIP_Latitude'] = geoip.getlatlong()['lat']
                data['geoIP_Longitude'] = geoip.getlatlong()['lon']

                mongo.save(data)
                log.debug("Saving into the MongoDB offset {0} , message {1} ".format(message.offset, message.value))
            self.consumer.close()

        except Exception as e:
            log.error("Ferrou em: {0}".format(e))
        finally:
            log.debug("Fechando conexão com o kafka")
            self.consumer.close();


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s:kconsumer:%(name)s:%(thread)d:%(levelname)s:%(process)d:%(message)s',
        level=config_log_level
        #,filename=config_log_file
    )
    try:
      #  while True:
            kafka = Consumer(config_kafka_topic, config_kafka_server, config_kafka_group_id, config_mongo_server, config_mongo_db, config_mongo_collection)
            kafka.flush()

    except Exception as e:
        log.error("Erro ao instanciar o Kafka Consumer: {}".format(e))
