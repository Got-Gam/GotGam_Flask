from elastic.delete_elastic_index import delete_elasticsearch_index
from elastic.diary_elastic import create_diary_index
from elastic.tour_to_elastic import send_to_elastic


delete_elasticsearch_index("tour_spots")
delete_elasticsearch_index("diary") # 다이어리 인덱스 초기화
send_to_elastic("./tour_spot_info2.json")
create_diary_index()