import json
from elasticsearch import Elasticsearch, helpers
from dotenv import load_dotenv
import os
import logging
from datetime import datetime

from elastic.delete_elastic_index import delete_elasticsearch_index

logging.basicConfig(level=logging.INFO)

load_dotenv()

elastic_pwd = os.getenv("ELASTIC_PASSWORD")

diary_index_body = {
    "settings": {
        "analysis": {
            "char_filter": {
                "remove_special": {
                    "type": "pattern_replace",
                    "pattern": "[^가-힣a-zA-Z0-9]",  # 한글, 영어, 숫자 외 제거
                    "replacement": ""
                }
            },
            "normalizer": {
                "clean_korean": {
                    "type": "custom",
                    "char_filter": ["remove_special"]
                }
            },
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
            "diary_id": {"type": "keyword"},
            "title": {
                "type": "text",
                "analyzer": "nori_analyzer_with_stopwords",
                "fields": {
                    "ngram": {
                        "type": "text",
                        "analyzer": "nori_ngram_analyzer"
                    },
                    "clean": {
                        "type": "keyword",
                        "normalizer": "clean_korean"
                    },
                    "korean_sorted": {
                        "type": "icu_collation_keyword",
                        "language": "ko",
                        "country": "KR",
                        "strength": "tertiary"
                    }
                }
            },
            "region": {
                "type": "text",
                "analyzer": "nori_analyzer_with_stopwords",
                "fields": {
                    "ngram": {
                        "type": "text",
                        "analyzer": "nori_ngram_analyzer"
                    }
                }
            },
            "content": {
                "type": "text",
                "analyzer": "nori_analyzer_with_stopwords",
                "fields": {
                    "ngram": {
                        "type": "text",
                        "analyzer": "nori_ngram_analyzer"
                    },
                }
            },
            "member_id": {"type": "keyword"},
            "created_time": {"type": "date", "format": "date_hour_minute_second_millis"},
            "start_date": {"type": "date", "format": "basic_date"},
            "end_date": {"type": "date", "format": "basic_date"},
            "tags": {"type": "keyword"},
            "total_cost": {"type": "integer"},
            "is_public": {"type": "boolean"},
            "bookmark_count": {"type": "float"},
            "area_code": {"type": "keyword"},
            "sigungu_code": {"type": "keyword"},
        }
    }
}


def create_diary_index():
    try:
        es = Elasticsearch("http://localhost:9200", basic_auth=('elastic', elastic_pwd))

        if not es.indices.exists(index='diary'):
            es.indices.create(index='diary', body=diary_index_body)
            logging.info("Index created")
        else:
            logging.info("Index already exists")
    except Exception as e:
        logging.error(e)

