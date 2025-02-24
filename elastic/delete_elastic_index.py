from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import os

load_dotenv()

elastic_pwd = os.getenv("ELASTIC_PASSWORD")

def delete_elasticsearch_index(index_name):
    try:
        es = Elasticsearch("http://localhost:9200",
                           basic_auth=('elastic', elastic_pwd))

        if es.indices.exists(index=index_name):
            es.indices.delete(index=index_name)
            print("Delete index: " + index_name)
        else:
            print("Index does not exist: " + index_name)

    except Exception as e:
        print(e)

