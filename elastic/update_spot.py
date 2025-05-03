import logging
import datetime
import re
import requests
from elasticsearch import Elasticsearch
import os
from dotenv import load_dotenv

from elastic.tour_to_elastic import generate_sort_title

# 로깅 설정
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# 환경 변수 로드
load_dotenv()
elastic_pwd = os.getenv("ELASTIC_PASSWORD")

# Elasticsearch 연결
es = Elasticsearch("http://elasticsearch:9200", basic_auth=('elastic', elastic_pwd))

# API 설정
tour_api_url = "http://apis.data.go.kr/B551011/KorService1/areaBasedSyncList1"
service_key = "IgykVu0qTZbi+3YtfC645Gag515ri7KsHHpE3r6Ef3iTiNaSDdmKZJizindrVRYzN4DEDknnAjoziHs/KDj/6g=="

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

# 필드 변환 및 필터링 설정
snake_case_mapping = {
    "addr1": "addr1",
    "addr2": "addr2",
    "areacode": "area_code",
    "booktour": "book_tour",
    "cat1": "cat1",
    "cat2": "cat2",
    "cat3": "cat3",
    "contentid": "content_id",
    "contenttypeid": "content_type_id",
    "createdtime": "created_time",
    "firstimage": "first_image",
    "firstimage2": "first_image2",
    "cpyrhtDivCd": "cpyrht_div_cd",
    "mapx": "map_x",
    "mapy": "map_y",
    "mlevel": "m_level",
    "modifiedtime": "modified_time",
    "sigungucode": "sigungu_code",
    "tel": "tel",
    "title": "title",
    "zipcode": "zipcode"
}

allowed_fields = {
    "addr1", "addr2", "area_code", "cat1", "cat2", "cat3", "content_id",
    "content_type_id", "created_time", "first_image", "first_image2",
    "map_x", "map_y", "modified_time", "sigungu_code", "tel", "title"
}


# 스케줄링 작업 정의
def update_tour_data():
    logger.info(f"스케줄러 실행: {datetime.datetime.now()}")

    # 하루 전 날짜 계산
    yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y%m%d")
    logger.info(f"대상 수정일 (modifiedtime): {yesterday}")

    # API에서 modifiedtime이 하루 전인 데이터 조회
    params = {
        "MobileOS": "ETC",
        "MobileApp": "Plan4Land",
        "_type": "json",
        "serviceKey": service_key,
        "numOfRows": 200,
        "pageNo": 1,
        "modifiedtime": yesterday,
        "listYN": "Y"
    }

    try:
        # 총 데이터 수 확인
        response = requests.get(tour_api_url, params=params)
        response.raise_for_status()
        data = response.json()
        total_counts = data['response']['body']['totalCount']
        logger.info(f"총 데이터 수: {total_counts}")

        if total_counts == 0:
            logger.info("업데이트할 데이터가 없습니다.")
            return

        items_total = []

        # 페이지네이션 처리
        for page in range(1, (total_counts // 200) + 2):
            params["pageNo"] = page
            try:
                response = requests.get(tour_api_url, params=params)
                response.raise_for_status()
                data = response.json()
                items = data['response']['body']['items']['item']

                # 데이터 처리
                for item in items:
                    filtered_item = {}
                    for key, value in item.items():
                        new_key = snake_case_mapping.get(key, key)
                        if new_key in allowed_fields:
                            filtered_item[new_key] = value

                    # 제외 조건 적용
                    if (filtered_item.get("sigungu_code") == "99" or
                        filtered_item.get("map_x") == "0" or
                        filtered_item.get("content_type_id") == "15"):
                        logger.info(f"content_id {filtered_item.get('content_id')} 제외됨 (조건 충족)")
                        continue

                    # 날짜 형식 변환
                    created_time_str = filtered_item.get("created_time")
                    if created_time_str:
                        created_datetime = datetime.datetime.strptime(created_time_str, "%Y%m%d%H%M%S")
                        filtered_item["created_time"] = created_datetime.strftime("%Y-%m-%dT%H:%M:%S")

                    modified_time_str = filtered_item.get("modified_time")
                    if modified_time_str:
                        modified_datetime = datetime.datetime.strptime(modified_time_str, "%Y%m%d%H%M%S")
                        filtered_item["modified_time"] = modified_datetime.strftime("%Y-%m-%dT%H:%M:%S")

                    # char_type 및 location 추가
                    filtered_item['sort_title'] = generate_sort_title(filtered_item.get("title", ""))
                    filtered_item['location'] = {
                        "lat": float(filtered_item.get("map_y")),
                        "lon": float(filtered_item.get("map_x"))
                    }

                    # content_type_id 변환
                    type_id = filtered_item.get("content_type_id")
                    if type_id in content_type_mapping:
                        filtered_item['classified_type_id'] = content_type_mapping[type_id]

                    items_total.append(filtered_item)

                logger.info(f"페이지 {page} 처리 완료 ({len(items_total)} / {total_counts})")

            except requests.exceptions.RequestException as e:
                logger.error(f"페이지 {page} 요청 실패: {e}")
                continue

        # Elasticsearch에 저장
        for item in items_total:
            content_id = item.get("content_id")
            try:
                # 기존 데이터 조회
                response = es.get(index="tour_spots", id=content_id, ignore=404)
                existing_data = response.get("_source", None)

                # detail 필드가 있는지 확인하고 제거 로그 출력
                if existing_data and 'detail' in existing_data:
                    logger.info(f"content_id {content_id}에서 Detail 필드 제거됨 (덮어씌우기)")

                # 데이터 업데이트 또는 삽입
                es.index(index="tour_spots", id=content_id, body=item)
                logger.info(f"content_id {content_id} 업데이트 완료")

            except Exception as e:
                logger.error(f"content_id {content_id} 처리 중 오류: {e}")
                continue

        logger.info("모든 데이터 업데이트 완료")

    except Exception as e:
        logger.error(f"스케줄링 작업 중 오류 발생: {e}")