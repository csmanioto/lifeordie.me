# lifeordie.me

## ML-API

API do Machine Learning

### pré-requisitos

- Python3.x
- flask_restful
- flask
- sklearn

### Instalação
pip3 install flask flask_restful sklearn lz4 kafka-python

### Execução

python3 api_ml.py


### Para testar:

Basta um CURL na API na porta 5000

- curl http://127.0.0.1:5000

- curl -v -i -X POST -H "Content-Type: application/json" -H "Accept: application/json" -d '{"user_id": 102345, "weight": {"idade":39,"estado_civil":1,"fumante":1,"ativo":0,"pressao":1}}'  http://127.0.0.1:5000/helth/api/v1.0/score_cholesterol


### FB-API

API de integração com o Facebook
