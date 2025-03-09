import json
import requests
import time

def get_tour():
    url = "http://apis.data.go.kr/B551011/KorService1/areaBasedList1"
    MobileOs = "ETC"
    MobileApp = "Plan4Land"
    dataType = "json"
    serviceKey = "IgykVu0qTZbi+3YtfC645Gag515ri7KsHHpE3r6Ef3iTiNaSDdmKZJizindrVRYzN4DEDknnAjoziHs/KDj/6g=="

    # 필드명 변환 매핑 테이블
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

    # 가져올 필드 목록 (제외하고 싶은 필드는 포함시키지 않음)
    allowed_fields = {
        "addr1", "addr2", "area_code", "cat1", "cat2", "cat3", "content_id",
        "content_type_id", "created_time", "first_image", "first_image2",
        "map_x", "map_y", "modified_time", "sigungu_code", "tel", "title"
    }

    params = {
        "MobileOS": MobileOs,
        "MobileApp": MobileApp,
        "_type": dataType,
        "serviceKey": serviceKey
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"tour 정보 요청 실패 : {e}")
        return json.dumps({"에러": str(e)}, ensure_ascii=False)

    data = response.json()
    total_counts = data['response']['body']['totalCount']
    print(f"총 데이터 수: {total_counts}")

    items_total = []

    for page in range(1, (total_counts // 200) + 2):
        params = {
            "numOfRows": 200,
            "pageNo": page,
            "MobileOS": MobileOs,
            "MobileApp": MobileApp,
            "_type": dataType,
            "serviceKey": serviceKey
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            items = data['response']['body']['items']['item']

            # 필드 변환, 필터링 및 값 변환
            for item in items:
                filtered_item = {}
                # 필드명 변환 및 허용된 필드만 선택
                for key, value in item.items():
                    new_key = snake_case_mapping.get(key, key)
                    if new_key in allowed_fields:
                        filtered_item[new_key] = value

                # 제외 조건 적용
                if (filtered_item.get("sigungu_code") == "99" or
                    filtered_item.get("map_x") == "0" or
                    filtered_item.get("content_type_id") == "15"):
                    continue  # 해당 조건에 맞으면 이 항목을 제외

                # content_type_id 값 변환
                # content_type_id = filtered_item.get("content_type_id")
                # if content_type_id in content_type_mapping:
                #     filtered_item["content_type_id"] = content_type_mapping[content_type_id]

                items_total.append(filtered_item)

            print(f"페이지 {page} 처리 완료 ({len(items_total)} / {total_counts})")
            time.sleep(2)

        except requests.exceptions.RequestException as e:
            print(f"페이지 {page} 요청 실패: {e}")
            continue

    # JSON 파일로 저장
    output_path = "../tour_spot_info2.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(items_total, f, ensure_ascii=False, indent=4)
    print(f"데이터 저장 완료: {output_path}")

# 실행
if __name__ == "__main__":
    get_tour()