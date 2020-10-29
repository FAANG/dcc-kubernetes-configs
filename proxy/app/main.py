from elasticsearch import Elasticsearch
from flask_cors import CORS, cross_origin
from flask import Flask
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
es = Elasticsearch(['elasticsearch-master-headless:9200'])


@app.route("/organism")
@cross_origin()
def bovreg_organisms():
    data = es.search(index='organism', size=10000)
    return data


@app.route("/specimen")
@cross_origin()
def bovreg_specimens():
    data = es.search(index='specimen', size=10000)
    return data


if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host='0.0.0.0', debug=True, port=80)
