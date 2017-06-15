
import logging, time

from kafka import KafkaProducer
from kafka.common import KafkaError
import json


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

class kafkaAPI(object):

    def __init__(self, servers=['localhost:9092']):
        self.servers = servers

    def send(self, topic, message):
        try:
            log.debug("Abrindo conexão com os Brokens...")
            producer = KafkaProducer(api_version=(0, 10, 1), value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                                          compression_type='lz4',
                                          bootstrap_servers=self.servers)

            log.debug("Enviando mensagem...")
            producer.send(topic, message)
            log.debug("Fechando conexão com o Kafka...")
            producer.close()

        except KafkaError as e:
            log.exception(e)

class Mongo(object):

    def __init__(self):
        pass
