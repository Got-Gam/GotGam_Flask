import json

def convert_to_snake_case_custom(json_data):
    """JSON 파일의 필드명을 사용자 정의 스네이크 케이스로 변경하는 함수"""

    snake_case_mapping = {
        "areacode": "area_code",
        "booktour": "book_tour",
        "contentid": "content_id",
        "contenttypeid": "content_type_id",
        "createdtime": "created_time",
        "firstimage": "first_image",
        "firstimage2": "first_image2", # firstimage2는 이미 스네이크 케이스 형태이므로 변경하지 않아도 되지만, 명시적으로 포함
        "mapx": "map_x",
        "mapy": "map_y",
        "mlevel": "m_level",
        "modifiedtime": "modified_time",
        "sigungucode": "sigungu_code",
        "zipcode": "zipcode", # zipcode는 이미 스네이크 케이스 형태이므로 변경하지 않아도 되지만, 명시적으로 포함
        "cpyrhtDivCd": "cpyrht_div_cd" # cpyrhtDivCd는 요청대로 변경
    }

    if isinstance(json_data, list):
        new_json_list = []
        for item in json_data:
            new_item = {}
            for key, value in item.items():
                new_key = snake_case_mapping.get(key, key) # 매핑 테이블에 없으면 기존 키 사용
                new_item[new_key] = value
            new_json_list.append(new_item)
        return new_json_list
    elif isinstance(json_data, dict):
        new_json_data = {}
        for key, value in json_data.items():
            new_key = snake_case_mapping.get(key, key) # 매핑 테이블에 없으면 기존 키 사용
            new_json_data[new_key] = value
        return new_json_data
    else:
        return json_data


def convert_json_file_to_snake_case(input_filepath, output_filepath):
    """JSON 파일을 읽어 사용자 정의 스네이크 케이스로 필드명을 변경하고 새로운 파일로 저장하는 함수"""
    with open(input_filepath, "r", encoding='utf-8') as old_f:
        json_data = json.load(old_f)

    snake_case_json_data = convert_to_snake_case_custom(json_data)

    with open(output_filepath, "w", encoding='utf-8') as new_f:
        json.dump(snake_case_json_data, new_f, ensure_ascii=False, indent=4)

    print(f"{output_filepath} 파일로 저장 완료")


# 파일 경로 지정
input_filepath = "../tour_info.json"  # 기존 JSON 파일 경로
output_filepath = "../snake_case_tour_info.json" # 새로운 JSON 파일 경로

convert_json_file_to_snake_case(input_filepath, output_filepath)