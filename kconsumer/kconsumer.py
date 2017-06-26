from pymongo import MongoClient
from kafka import KafkaConsumer
from kafka.common import KafkaError


import requests
import logging
import json
from datetime import datetime
from configparser import ConfigParser
import threading, queue, time


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
                log.debug("Conectando em {} para caputar GeoIP".format(send_url))
                r = requests.get(send_url)
                self.geojson = json.loads(r.text)
                log.debug("GeoIp resultcode: {}".format(r))
                log.debug("GeoIp Result data: {}".format(self.geojson ))
            except Exception as e :
                log.error("Error on get GeoIP {}".format(e))


        def getlatlong(self):
            latlon = dict()
            latlon['lat'] = self.geojson['latitude']
            latlon['lon'] = self.geojson['longitude']
            return latlon

        def getRegion(self):
            region = dict()
            if len(self.geojson['region_name']) < 1:
                self.geojson['region_name'] = "Sao Paulo"

            region['Estado'] = self.geojson['region_name']

            if len(self.geojson['city']) < 1:
                self.geojson['city'] = "Sao Paulo"

            region['Cidadade'] = self.geojson['city']

            if len(self.geojson['country_code']) < 1:
                self.geojson['country_code'] = "BR"
            region['Pais'] = self.geojson['country_code']
            return region




class Mongo(object):
    def __init__(self, mongoserver, mongodb, collection):
        try:
            self.conn = MongoClient("mongodb://{}".format(mongoserver))
            self.client = self.conn[mongodb][collection]
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
            try:
                self.conn.close()
                log.debug("Finalizando conexão com o MongodDB")
                pass
            except Exception as e:
                log.error("Error ao finalizar conexão com o MongodDB: {}".format(e))
                exit(1)

class Consumer(object):
    def __init__(self, topic, kafkaserver, kafka_group_id, mongooserver, mongo_database, collection):
        self.mongoo_server = mongooserver
        self.mongo_database = mongo_database
        self.mongo_collection = collection
        self.consumer = KafkaConsumer(topic,
                                      bootstrap_servers = kafkaserver,
                                      group_id = kafka_group_id,
                                      value_deserializer = lambda m: json.loads(m.decode('ascii')),
                                      api_version=(0, 10, 1),
                                      enable_auto_commit=False,
                                      auto_offset_reset='earliest'
                                      )

    def flush(self):

        try:
            mongo = Mongo(self.mongoo_server, self.mongo_database, self.mongo_collection)
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
                self.consumer.commit()
                log.debug("Saving into the MongoDB offset {0} , message {1} ".format(message.offset, message.value))
            self.consumer.close()

        except Exception as e:
            log.error("Ferrou em: {0}".format(e))
            pass
        finally:
            log.debug("Fechando conexão com o kafka")
            self.consumer.close();



if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s:kconsumer:%(name)s:%(thread)d:%(levelname)s:%(process)d:%(message)s',
        level=config_log_level
        ,filename=config_log_file
    )
    log.info("KConsumer iniciado com sucesso :)")
    try:
        while True:
            kafka = Consumer(config_kafka_topic, config_kafka_server, config_kafka_group_id, config_mongo_server, config_mongo_db, config_mongo_collection)
            kafka.flush()
            time.sleep(5)  # Delay for 5 seconds.


    except Exception as e:
        log.error("Erro ao instanciar o Kafka Consumer: {}".format(e))
