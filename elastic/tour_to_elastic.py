import json
from elasticsearch import Elasticsearch, helpers

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
                "createdtime": {"type": "date", "format": "yyyy:MM:dd:HH:mm:ss"},
                "modifiedtime": {"type": "date", "format": "yyyy:MM:dd:HH:mm:ss"},
                "firstimage": {"type": "keyword"},
                "firstimage2": {"type": "keyword"},
                "booktour": {"type": "keyword"},
                "cpyrhtDivCd": {"type": "keyword"},
                "tel": {"type": "keyword"},
                "mapx": {"type": "geo_point"},
                "mapy": {"type": "geo_point"},
                "mlevel": {"type": "float"}
            }
        }
    }

def send_to_elastic():
    es = Elasticsearch("http://localhost:9200")
    index_name = "tour_spots"
    batch_size = 2000
    total_docs = 0

    try:
        if not es.indices.exists(index=index_name):
            es.indices.create(index=index_name, body=index_body)
        else:
            print("Index already exists")

        with open("D:/dev/Final_Project/Final_Flask/tour_info.json", "r", encoding='utf-8') as f:
            tour_data = json.load(f)

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
                    print(f'오류 발생 : {failed}')

            print('벌크 인덱싱 성공')
    except Exception as e:
        print(f'오류 발생 : {e}')

send_to_elastic()
