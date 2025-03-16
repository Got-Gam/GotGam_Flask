import json
import logging
import os
import re
from datetime import datetime

from dotenv import load_dotenv
from elasticsearch import Elasticsearch, helpers

logging.basicConfig(level=logging.INFO)

load_dotenv()

elastic_pwd = os.getenv("ELASTIC_PASSWORD")

tour_index_body = {
    "settings": {
        "index": {
            "max_ngram_diff": 2  # 차이를 2로 설정
        },
        "analysis": {
            "tokenizer": {
                "nori_user_dict_tokenizer": {
                    "type": "nori_tokenizer",
                    "decompound_mode": "mixed",
                    "discard_punctuation": "false"
                }
            },
            "filter": {
                "ngram_filter": {
                    "type": "ngram",
                    "min_gram": 2,
                    "max_gram": 4
                },
                "english_ngram_filter": {
                    "type": "ngram",
                    "min_gram": 2,
                    "max_gram": 3
                }
            },
            "analyzer": {
                "nori_analyzer_simple": {
                    "type": "custom",
                    "tokenizer": "nori_user_dict_tokenizer",
                    "filter": ["nori_readingform", "trim"]
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
            "title": {
                "type": "text",
                "analyzer": "nori_analyzer_simple",
                "fields": {
                    "ngram": {
                        "type": "text",
                        "analyzer": "nori_ngram_analyzer"
                    },
                    "sort": {
                        "type": "icu_collation_keyword",
                        "language": "ko",
                        "country": "KR",
                        "strength": "primary"
                    },
                }
            },
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
            "area_code": {"type": "keyword"},
            "sigungu_code": {"type": "keyword"},
            "content_id": {"type": "keyword"},
            "content_type_id": {"type": "keyword"},
            "cat1": {"type": "keyword"},
            "cat2": {"type": "keyword"},
            "cat3": {"type": "keyword"},
            "created_time": {"type": "date", "format": "date_hour_minute_second"},
            "modified_time": {"type": "date", "format": "date_hour_minute_second"},
            "first_image": {"type": "keyword"},
            "first_image2": {"type": "keyword"},
            "tel": {"type": "keyword"},
            "map_x": {"type": "float"},
            "map_y": {"type": "float"},
            "review_count": {"type": "float"},
            "rating": {"type": "float"},
            "avg_rating": {"type": "double"},
            "bookmark_count": {"type": "float"},
            "char_type": {"type": "byte"},
            "location": {"type": "geo_point"},
            "classified_type_id": {"type": "keyword"},
        }
    }
}

# content_type_id 변환 규칙
content_type_mapping = {
    "12": "100",
    "14": "100",
    "25": "100",
    "28": "100",
    "38": "100",
    "32": "200",
    "39": "300"
}


def determine_chat_type(title):
    """title의 첫 글자를 기준으로 chat_type을 결정"""
    if not title:  # title이 비어있는 경우
        return 3  # 기본값으로 특수문자 취급
    first_char = title[0]
    if re.match(r'[가-힣]', first_char):
        return 0  # 한글
    elif re.match(r'[a-zA-Z]', first_char):
        return 1  # 영어
    elif re.match(r'[0-9]', first_char):
        return 2  # 숫자
    else:
        return 3  # 특수문자


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

                item['char_type'] = determine_chat_type(item.get("title", ""))
                item['location'] = {
                    "lat": float(item.get("map_y")),  # 위도
                    "lon": float(item.get("map_x"))  # 경도
                }

                type_id = item.get("content_type_id")
                if type_id in content_type_mapping:
                    item['classified_type_id'] = content_type_mapping[type_id]

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
