from elastic.delete_elastic_index import delete_elasticsearch_index
from elastic.diary_elastic import create_diary_index
from elastic.tour_to_elastic import send_to_elastic
# app.py
from flask import Flask, request, jsonify, render_template
from apscheduler.schedulers.background import BackgroundScheduler
from ML.recomendation import recommend_top_destinations
import datetime

app = Flask(__name__)

# 스케줄러 설정
scheduler = BackgroundScheduler()


# def scheduled_task():
#     print(f"스케줄러 실행: {datetime.datetime.now()}")
#
#
# scheduler.add_job(scheduled_task, 'interval', minutes=1)  # 1분마다 실행
# scheduler.start()


# 홈 페이지
@app.route('/')
def index():
    return render_template('index.html')

# 추천 API
@app.route('/recommend', methods=['POST'])
def get_recommendations():
    try:
        # 클라이언트에서 보낸 JSON 데이터 받기
        data = request.get_json()

        # 입력 데이터 파싱
        user_input = {
            'GENDER': int(data['GENDER']),
            'AGE_GRP': int(data['AGE_GRP']),
            'TRAVEL_STYL_1': int(data['TRAVEL_STYL_1']),
            'TRAVEL_STYL_2': int(data['TRAVEL_STYL_2']),
            'TRAVEL_STYL_3': int(data['TRAVEL_STYL_3']),
            'TRAVEL_STYL_4': int(data['TRAVEL_STYL_4']),
            'TRAVEL_STYL_5': int(data['TRAVEL_STYL_5']),
            'TRAVEL_STYL_6': int(data['TRAVEL_STYL_6']),
            'TRAVEL_STYL_7': int(data['TRAVEL_STYL_7']),
            'TRAVEL_STYL_8': int(data['TRAVEL_STYL_8']),
            'TRAVEL_MOTIVE_1': int(data['TRAVEL_MOTIVE_1']),
            'TRAVEL_COMPANIONS_NUM': int(data['TRAVEL_COMPANIONS_NUM']),
            'TRAVEL_MISSION_INT': int(data['TRAVEL_MISSION_INT'])
        }

        # 추천 결과 생성
        recs = recommend_top_destinations(user_input, top_n=10, threshold=0.7)

        # 결과를 JSON으로 변환
        result = recs.to_dict(orient='records')
        return jsonify({'status': 'success', 'recommendations': result})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/server-initialize', methods=['POST'])
def initialize():
    try:
        delete_elasticsearch_index("tour_spots")
        delete_elasticsearch_index("diary")  # 다이어리 인덱스 초기화
        send_to_elastic("./tour_spot_info2.json")
        create_diary_index()
        return jsonify({'status': 'success', 'message': 'Server initialized successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# 서버 종료 시 스케줄러 정리
def shutdown_scheduler():
    scheduler.shutdown()


if __name__ == '__main__':
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    finally:
        shutdown_scheduler()