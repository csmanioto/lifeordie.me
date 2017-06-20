from pymongo import MongoClient
from kafka import KafkaConsumer
from kafka.common import KafkaError

import logging
import json
from datetime import datetime
import threading, queue

log = logging.getLogger(__name__)


class Mongo(object):
    def __init__(self, hostname):
        try:
            self.client = MongoClient("mongodb://{0}".format(hostname))
        except Exception as e:
            log.error("Erro ao conectar no hostname: {0} - {1}".format(hostname, e))

    def save(self, data):
        try:
            db = self.client.lifeordiedDB
            result = db.resultados.insert_one(data)
            log.info("Dado inserido no mongo com sucesso: {0}".format(result))
            return result
        except  Exception as e:
            log.error("Erro ao inserir no MongoDB")
        finally:
            log.debug("Finalizando conexão com o MongodDB")
            self.client.close()


class Consumer(object):
    def __init__(self, topic, kafkaserver, mongooserver):
        self.mongooserver = mongooserver
        self.consumer = KafkaConsumer(topic,
                                      bootstrap_servers=kafkaserver,
                                      group_id='mongoconsumer',
                                      value_deserializer=lambda m: json.loads(m.decode('ascii')),
                                      api_version=(0, 10, 1),
                                      auto_offset_reset='earliest')

    def flush(self):

        try:
            mongo = Mongo(self.mongooserver)
            log.debug("Abrindo conexão com os Brokens...")
            for message in self.consumer:
                self.consumer.commit()
                data = message.value
                data["RequestData"] = datetime.strptime(data["RequestData"], '%Y-%m-%d %H:%M:%S.%f')
                mongo.save(data)
                log.debug("Saving into the MongoDB offset {0} , message {1} ".format(message.offset, message.value))

        except Exception as e:
            log.error("Ferrou em: {0}".format(e))
        finally:
            log.debug("Fechando conexão com o kafka")
            self.consumer.close();


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s:kconsumer:%(name)s:%(thread)d:%(levelname)s:%(process)d:%(message)s',
        level=logging.INFO
    )
    try:
        kafka = Consumer("app", "192.168.18.30:9092", "192.168.18.31:27017")
        kafka.flush()
    except:
        log.error("Erro ao instanciar o Kafka Consumer")
