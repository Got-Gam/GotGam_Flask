import os

from dotenv import load_dotenv

from elastic.delete_elastic_index import delete_elasticsearch_index
from elastic.diary_elastic import create_diary_index
from elastic.tour_to_elastic import send_to_elastic


delete_elasticsearch_index("tour_spots")
delete_elasticsearch_index("diary")
send_to_elastic("./snake_case_tour_info.json")
create_diary_index()