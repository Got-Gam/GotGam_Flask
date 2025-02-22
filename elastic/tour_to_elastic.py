import json
from elasticsearch import Elasticsearch, helpers
from dotenv import load_dotenv
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)

load_dotenv()

elastic_pwd = os.getenv("ELASTIC_PASSWORD")

index_body = {
    "settings": {
        "analysis": {
            "tokenizer": {
                "nori_user_dict_tokenizer": {
                    "type": "nori_tokenizer",
                    "decompound_mode": "mixed",
                    "discard_punctuation": "false"
                }
            },
            "filter": {
                "korean_stop": {
                    "type": "stop",
                    "stopwords_path": "analysis/stopwords/korean_stopwords.txt"
                },
                "nori_filter": {
                    "type": "nori_part_of_speech",
                    "stoptags": [
                        "E", "IC", "J", "MAG", "MAJ", "MM", "SP", "SSC", "SSO", "SC", "SE", "XPN", "XSA", "XSN",
                        "XSV",
                        "UNA", "NA", "VSV", "NP"
                    ]
                },
                "ngram_filter": {
                    "type": "ngram",
                    "min_gram": 2,
                    "max_gram": 3
                },
                "english_ngram_filter": {
                    "type": "ngram",
                    "min_gram": 2,
                    "max_gram": 3
                },
            },
            "analyzer": {
                "nori_analyzer_with_stopwords": {
                    "type": "custom",
                    "tokenizer": "nori_user_dict_tokenizer",
                    "filter": ["nori_readingform", "korean_stop", "nori_filter", "trim"]
                },
                "nori_ngram_analyzer": {
                    "type": "custom",
                    "tokenizer": "nori_user_dict_tokenizer",
                    "filter": ["nori_readingform", "ngram_filter", "trim"]
                },
                "english_ngram_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase", "english_ngram_filter", "trim"]
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "addr1": {
                "type": "text",
                "analyzer": "nori_analyzer_with_stopwords",
                "fields": {
                    "ngram": {
                        "type": "text",
                        "analyzer": "nori_ngram_analyzer"
                    }
                }
            },
            "addr2": {
                "type": "text",
                "analyzer": "nori_analyzer_with_stopwords",
                "fields": {
                    "ngram": {
                        "type": "text",
                        "analyzer": "nori_ngram_analyzer"
                    }
                }
            },
            "title": {
                "type": "text",
                "analyzer": "nori_analyzer_with_stopwords",
                "fields": {
                    "ngram": {
                        "type": "text",
                        "analyzer": "nori_ngram_analyzer"
                    }
                }
            },
            "areacode": {"type": "keyword"},
            "sigungucode": {"type": "keyword"},
            "zipcode": {"type": "keyword"},
            "contentid": {"type": "keyword"},
            "contenttypeid": {"type": "keyword"},
            "cat1": {"type": "keyword"},
            "cat2": {"type": "keyword"},
            "cat3": {"type": "keyword"},
            "createdtime": {"type": "date", "format": "basic_date_time_no_millis"},
            "modifiedtime": {"type": "date", "format": "basic_date_time_no_millis"},
            "firstimage": {"type": "keyword"},
            "firstimage2": {"type": "keyword"},
            "booktour": {"type": "keyword"},
            "cpyrhtDivCd": {"type": "keyword"},
            "tel": {"type": "keyword"},
            "mapx": {"type": "float"},
            "mapy": {"type": "float"},
            "mlevel": {"type": "float"}
        }
    }
}
# 위의 createdtime, modifiedtime의 format은 넣을 데이터의 현재 포멧을 말하는 것이다.
# 따라서 현재 JSON파일에 들어가있는 포멧과 일치시켜야 한다
def send_to_elastic():
    es = Elasticsearch("http://localhost:9200",
                       basic_auth=('elastic', elastic_pwd))
    index_name = "tour_spots"
    batch_size = 2000
    total_docs = 0

    try:
        if not es.indices.exists(index=index_name):
            es.indices.create(index=index_name, body=index_body)
        else:
            print("Index already exists")

        with open("../tour_info.json", "r", encoding='utf-8') as f:
            tour_data = json.load(f)

            for item in tour_data:  # tour_data를 순회하며 각 item (도큐먼트) 처리
                # 날짜 형식 변환 (createdtime)
                created_time_str = item.get("createdtime")
                if created_time_str:  # createdtime 값이 있는 경우에만 변환
                    created_datetime = datetime.strptime(created_time_str, "%Y%m%d%H%M%S")  # 기존 형식 파싱
                    item["createdtime"] = created_datetime.strftime("%Y%m%dT%H%M%S+0900")  # 새 형식으로 변환 및 저장

                # 날짜 형식 변환 (modifiedtime)
                modified_time_str = item.get("modifiedtime")
                if modified_time_str:  # modifiedtime 값이 있는 경우에만 변환
                    modified_datetime = datetime.strptime(modified_time_str, "%Y%m%d%H%M%S")  # 기존 형식 파싱
                    item["modifiedtime"] = modified_datetime.strftime("%Y%m%dT%H%M%S+0900")  # 새 형식으로 변환 및 저장

            for i in range(0, len(tour_data), batch_size):
                batch = tour_data[i:i + batch_size]
                actions = [
                    {
                        "_index": index_name,
                        "_source": data
                    }
                    for data in batch
                ]

                success, failed = helpers.bulk(es, actions)
                total_docs += success
                print(f'인덱싱 진행중... : {total_docs} / {len(tour_data)}')

                if failed:
                    print(f'오류 발생')
                    print(failed)

            print('벌크 인덱싱 성공')
    except Exception as e:
        if isinstance(e, helpers.BulkIndexError):
            print('***실패 정보 출력***')
            logging.error(e.errors)
        else:
            logging.error(f'오류 메시지 발생 : {e}')
            logging.error(type(e))


send_to_elastic()
