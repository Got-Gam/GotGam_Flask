import json
from elasticsearch import Elasticsearch, helpers
from dotenv import load_dotenv
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)

load_dotenv()

elastic_pwd = os.getenv("ELASTIC_PASSWORD")

tour_index_body = {
    "settings": {
        "analysis": {
            # 노말라이저 추가
            "normalizer": {
                "korean_collation": {
                    "type": "icu_normalizer",
                    "name": "nfkc_cf"
                }
            },
            "tokenizer": {
                "nori_user_dict_tokenizer": {
                    # 한국어 처리를 위한 Nori 토크나이저
                    "type": "nori_tokenizer",
                    # 복합어를 혼합모드로 분리
                    "decompound_mode": "mixed",
                    # 구두점을 버리지 않고 유지
                    "discard_punctuation": "false"
                }
            },
            "filter": {
                # 관광지 이름은 하나의 고유명사이기 때문에 불용어 제외
                # "korean_stop": {
                #     "type": "stop",
                #     "stopwords_path": "analysis/stopwords/korean_stopwords.txt"
                # },
                # nori_part_of_speech : 특정 품사를 제거하는 필터, 이것 또한 고유명사에 불필요
                # "nori_filter": {
                #     "type": "nori_part_of_speech",
                #     "stoptags": [
                #         "E", "IC", "J", "MAG", "MAJ", "MM", "SP", "SSC", "SSO", "SC", "SE", "XPN", "XSA", "XSN",
                #         "XSV",
                #         "UNA", "NA", "VSV", "NP"
                #     ]
                # },
                # ngram 필터 : 텍스트를 2~3글자 단위로 분리
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
                # 불용어, 품사가 필터가 불필요하기 때문에 분석기 새로 설정
                # "nori_analyzer_with_stopwords": {
                #     "type": "custom",
                #     "tokenizer": "nori_user_dict_tokenizer",
                #     "filter": ["nori_readingform", "korean_stop", "nori_filter", "trim"]
                # },
                # 한국어 텍스트 분석기                
                "nori_analyzer_simple": {
                    "type": "custom",
                    "tokenizer": "nori_user_dict_tokenizer",
                    "filter": ["nori_readingform", "trim"] # 불용어 / 품사 필터 제거
                },
                "nori_ngram_analyzer": {
                    "type": "custom",
                    "tokenizer": "nori_user_dict_tokenizer",
                    "filter": ["nori_readingform", "ngram_filter", "trim"]
                },
                # 영어로 되어있는 관광지 존재
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
                "analyzer": "nori_analyzer_simple",
                "fields": {
                    "ngram": {
                        "type": "text",
                        "analyzer": "nori_ngram_analyzer"
                    }
                }
            },
            "addr2": {
                "type": "text",
                "analyzer": "nori_analyzer_simple",
                "fields": {
                    "ngram": {
                        "type": "text",
                        "analyzer": "nori_ngram_analyzer"
                    }
                }
            },
            "title": {
                "type": "text",
                "analyzer": "nori_analyzer_simple",
                "fields": {
                    "ngram": {
                        "type": "text",
                        "analyzer": "nori_ngram_analyzer"
                    },
                    "keyword": {
                        "type": "keyword",
                    },
                    # 한글 우선 정렬
                    "korean_sorted": {
                        "type": "keyword",
                        "normalizer": "korean_collation"
                    }
                }
            },
            "area_code": {"type": "keyword"},
            "sigungu_code": {"type": "keyword"},
            # "zipcode": {"type": "keyword"}, # 우편번호 - 제거
            "content_id": {"type": "keyword"},
            "content_type_id": {"type": "keyword"},
            "cat1": {"type": "keyword"},
            "cat2": {"type": "keyword"},
            "cat3": {"type": "keyword"},
            "created_time": {"type": "date", "format": "date_hour_minute_second"},
            "modified_time": {"type": "date", "format": "date_hour_minute_second"},
            "first_image": {"type": "keyword"},
            "first_image2": {"type": "keyword"},
            # "book_tour": {"type": "keyword"}, # 교과서정보 - 제거
            # "cpyrht_div_cd": {"type": "keyword"}, # 저작권 관련 - 제거
            "tel": {"type": "keyword"},
            "map_x": {"type": "float"},
            "map_y": {"type": "float"},
            # "m_level": {"type": "float"}, # 지도 레벨 - 제거
            "review_count": {"type": "float"},
            "rating": {"type": "double"},
            "bookmark_count": {"type": "float"},
        }
    }
}


# 위의 createdtime, modifiedtime의 format은 넣을 데이터의 현재 포멧을 말하는 것이다.
# 따라서 현재 JSON파일에 들어가있는 포멧과 일치시켜야 한다
def send_to_elastic(file_path):
    es = Elasticsearch("http://localhost:9200",
                       basic_auth=('elastic', elastic_pwd))
    index_name = "tour_spots"
    batch_size = 2000
    total_docs = 0

    try:
        if not es.indices.exists(index=index_name):
            es.indices.create(index=index_name, body=tour_index_body)
        else:
            print("Index already exists")

        with open(file_path, "r", encoding='utf-8') as f:
            tour_data = json.load(f)

            for item in tour_data:  # tour_data를 순회하며 각 item (도큐먼트) 처리
                created_time_str = item.get("created_time")
                if created_time_str:  # createdtime 값이 있는 경우에만 변환
                    created_datetime = datetime.strptime(created_time_str, "%Y%m%d%H%M%S")  # 기존 형식 파싱
                    item["created_time"] = created_datetime.strftime("%Y-%m-%dT%H:%M:%S")  # 새 형식으로 변환 및 저장

                modified_time_str = item.get("modified_time")
                if modified_time_str:  # modifiedtime 값이 있는 경우에만 변환
                    modified_datetime = datetime.strptime(modified_time_str, "%Y%m%d%H%M%S")  # 기존 형식 파싱
                    item["modified_time"] = modified_datetime.strftime("%Y-%m-%dT%H:%M:%S")  # 새 형식으로 변환 및 저장

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
