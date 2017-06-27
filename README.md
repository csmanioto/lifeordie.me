# lifeordie.me

## Flume

Arquivos de configuração do Flume:
 - flume_httpd: Instalação do flume no servidor apache, pegar os log do apache e jogar no kafka
 - flume_kconsumer: Instalação do flume no servidor do kconsumer, pega os log da aplicação e joga no kafka
 - flume_mlapi:  Instalação do flume no servidor do ml-api, pega os log da aplicação e joga no kafka
 - flume_server: Instalação do servidor flume que irá consumir do kafka e jogar no Solr/Mongo, etc.
 
## Bases

Base de dados da Vigital utilizada para ensinar o modelo de Machine Learning

## Front

Código PHP + HTML da camada de FrontEnd do projeto.

## kconsumer

Serviço em python que lê do kafka as mensagens geradas pela ML-API e joga no MongoDB com dados de Latitude e Longitude.


### pré-requisitos

- Python3.x
- Possui arquivo requirements.txt para instalação das dependências:
pip install -r requirements.txt

### Execução

Após setup do config.ini, 
nohup python3 kconsumer.py &

## Mongodb

Rotina de instalação do servidor MongoDB para o projeto.

## ML-API

API do Machine Learning

### pré-requisitos

- Python3.x
- Possui arquivo requirements.txt para instalação das dependências:

pip install -r requirements.txt

### Execução

Após setup do config.ini, 
nohup python3 api_ml.py &

### Para testar:

Basta um CURL na API na porta 80

- curl http://127.0.0.1:80

- curl -v -i -X POST -H "Content-Type: application/json" -H "Accept: application/json" -d '{"user_id": 102345, "weight": {"idade":39,"estado_civil":1,"fumante":1,"ativo":0,"pressao":1, "imc": 29.4}}'  http://127.0.0.1:80/helth/api/v1.0/score_cholesterol


### FB-API

API de integração com o Facebook
