from elasticsearch import Elasticsearch
from flask_cors import CORS, cross_origin
from flask import Flask
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
es = Elasticsearch(['elasticsearch-master-headless:9200'])


# @app.route("/organism/<mode>")
# @cross_origin()
# def bovreg_organisms(mode):
#     if mode == 'private':
#         data = es.search(index='organism', size=10000)
#     else:
#         data = es.search(index='organism', q="private:false", size=10000)
#     return data
#
#
# @app.route("/specimen")
# @cross_origin()
# def bovreg_specimens():
#     data = es.search(index='specimen', size=10000)
#     return data

@app.route("/protocols_samples")
@cross_origin()
def all_records():
    return es.search(index="protocols_samples", size=10000)


@app.route("/protocols_samples/<record_id>")
@cross_origin()
def details(record_id):
    return es.search(index="protocols_samples", q=f"_id:{record_id}")


if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host='0.0.0.0', debug=True, port=80)
