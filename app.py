from elastic.delete_elastic_index import delete_elasticsearch_index
from elastic.diary_elastic import create_diary_index
from elastic.tour_to_elastic import send_to_elastic
# app.py
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from ML.recomendation import recommend_top_destinations
import logging

from elastic.update_spot import update_tour_data

# 로깅 설정
logging.basicConfig(
    level=logging.DEBUG,  # DEBUG 이상 모두 기록
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]  # 콘솔 출력
)
logger = logging.getLogger(__name__)
app = Flask(__name__)
CORS(app)

# 스케줄러 설정
scheduler = BackgroundScheduler()

# 스케줄링 작업 추가 (매일 새벽 3시 실행)
scheduler.add_job(update_tour_data, 'cron', hour=3, minute=0)  # 매일 새벽 3시 실행
scheduler.start()


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
        logging.info(data)

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

        logging.info('추천 진입')
        # 추천 결과 생성
        recs = recommend_top_destinations(user_input, top_n=10, threshold=0.7)

        # 결과를 JSON으로 변환
        result = recs.to_dict(orient='records')
        return jsonify({'status': 'success', 'recommendations': result})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})




@app.route('/test', methods=['GET'])
def test():
    print('test')
    logger.info("Test endpoint called")
    return jsonify({'status': 'success'})


# 서버 종료 시 스케줄러 정리
def shutdown_scheduler():
    scheduler.shutdown()


if __name__ == '__main__':
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    finally:
        shutdown_scheduler()