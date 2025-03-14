# recomendation.py
import os
from catboost import CatBoostClassifier
import pandas as pd
import pickle

# 현재 파일(recomendation.py)의 디렉토리 기준으로 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, 'catboost_model.cbm')
label_path = os.path.join(BASE_DIR, 'label_encoder.pkl')
csv_path = os.path.join(BASE_DIR, 'df_learning.csv')

# 파일 존재 여부 확인 (디버깅용)
if not os.path.exists(model_path):
    raise FileNotFoundError(f"모델 파일이 존재하지 않습니다: {model_path}")

model = CatBoostClassifier()
model.load_model(model_path)
with open(label_path, 'rb') as f:
    le = pickle.load(f)
df_learning = pd.read_csv(csv_path)


# 추천 함수
def recommend_top_destinations(user_input, top_n=10, threshold=0.7):
    destinations = df_learning[['VISIT_AREA_NM', 'VISIT_AREA_TYPE_CD']].drop_duplicates()
    destinations['VISIT_AREA_NM_CODE'] = le.transform(destinations['VISIT_AREA_NM'])

    prediction_data = []
    for _, row in destinations.iterrows():
        combined_input = user_input.copy()
        combined_input['VISIT_AREA_TYPE_CD'] = row['VISIT_AREA_TYPE_CD']
        combined_input['VISIT_AREA_NM_CODE'] = row['VISIT_AREA_NM_CODE']
        prediction_data.append(combined_input)

    cat_features_extended = ['GENDER', 'AGE_GRP', 'TRAVEL_STYL_1', 'TRAVEL_STYL_2',
                             'TRAVEL_STYL_3', 'TRAVEL_STYL_4', 'TRAVEL_STYL_5',
                             'TRAVEL_STYL_6', 'TRAVEL_STYL_7', 'TRAVEL_STYL_8',
                             'TRAVEL_MOTIVE_1', 'TRAVEL_COMPANIONS_NUM',
                             'TRAVEL_MISSION_INT', 'VISIT_AREA_TYPE_CD', 'VISIT_AREA_NM_CODE']

    prediction_df = pd.DataFrame(prediction_data, columns=cat_features_extended)
    proba = model.predict_proba(prediction_df)
    prob_5 = proba[:, 4]  # 5.0 확률

    recommendations = pd.DataFrame({
        'VISIT_AREA_NM': destinations['VISIT_AREA_NM'],
        'Probability_5.0': prob_5
    })
    return recommendations[recommendations['Probability_5.0'] >= threshold].nlargest(top_n, 'Probability_5.0')
