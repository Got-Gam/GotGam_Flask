# import json
#
# def convert_to_snake_case_custom(json_data, exclude_fields=None):
#     """
#     JSON 파일의 필드명을 사용자 정의 스네이크 케이스로 변경하고, 제외할 필드를 제거하는 함수
#     :param json_data: 변환할 JSON 데이터
#     :param exclude_fields: 제외할 필드 이름 목록 (기본값: None)
#     :return: 변환된 JSON 데이터
#     """
#     # 제외할 필드 목록 (기본값 설정)
#     if exclude_fields is None:
#         exclude_fields = {"zipcode", "booktour", "cpyrhtDivCd", "mlevel"}
#
#     # 필드명 변환 매핑 테이블
#     snake_case_mapping = {
#         "areacode": "area_code",
#         "booktour": "book_tour",  # 제외되므로 실제로는 적용되지 않음
#         "contentid": "content_id",
#         "contenttypeid": "content_type_id",
#         "createdtime": "created_time",
#         "firstimage": "first_image",
#         "firstimage2": "first_image2",
#         "mapx": "map_x",
#         "mapy": "map_y",
#         "mlevel": "m_level",  # 제외되므로 실제로는 적용되지 않음
#         "modifiedtime": "modified_time",
#         "sigungucode": "sigungu_code",
#         "zipcode": "zipcode",  # 제외되므로 실제로는 적용되지 않음
#         "cpyrhtDivCd": "cpyrht_div_cd"  # 제외되므로 실제로는 적용되지 않음
#     }
#
#     if isinstance(json_data, list):
#         new_json_list = []
#         for item in json_data:
#             new_item = {}
#             for key, value in item.items():
#                 # 제외할 필드가 아닌 경우에만 처리
#                 if key not in exclude_fields:
#                     new_key = snake_case_mapping.get(key, key)  # 매핑 테이블에 없으면 기존 키 사용
#                     new_item[new_key] = value
#             new_json_list.append(new_item)
#         return new_json_list
#     elif isinstance(json_data, dict):
#         new_json_data = {}
#         for key, value in json_data.items():
#             # 제외할 필드가 아닌 경우에만 처리
#             if key not in exclude_fields:
#                 new_key = snake_case_mapping.get(key, key)  # 매핑 테이블에 없으면 기존 키 사용
#                 new_json_data[new_key] = value
#         return new_json_data
#     else:
#         return json_data
#
# def convert_json_file_to_snake_case(input_filepath, output_filepath, exclude_fields=None):
#     """
#     JSON 파일을 읽어 사용자 정의 스네이크 케이스로 필드명을 변경하고,
#     특정 필드를 제외한 후 새로운 파일로 저장하는 함수
#     :param input_filepath: 입력 JSON 파일 경로
#     :param output_filepath: 출력 JSON 파일 경로
#     :param exclude_fields: 제외할 필드 이름 목록 (기본값: None)
#     """
#     with open(input_filepath, "r", encoding='utf-8') as old_f:
#         json_data = json.load(old_f)
#
#     # 제외할 필드를 지정하여 변환
#     snake_case_json_data = convert_to_snake_case_custom(json_data, exclude_fields)
#
#     with open(output_filepath, "w", encoding='utf-8') as new_f:
#         json.dump(snake_case_json_data, new_f, ensure_ascii=False, indent=4)
#
#     print(f"{output_filepath} 파일로 저장 완료")
#
# # 파일 경로 지정
# input_filepath = "../tour_info.json"  # 기존 JSON 파일 경로
# output_filepath = "../snake_case_tour_info.json"  # 새로운 JSON 파일 경로
#
# # 제외할 필드 목록 (필요 시 커스터마이징 가능)
# exclude_fields = {"zipcode", "booktour", "cpyrhtDivCd", "mlevel"}
#
# # 함수 호출
# convert_json_file_to_snake_case(input_filepath, output_filepath, exclude_fields)