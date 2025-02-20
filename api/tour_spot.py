import json
import requests
import time

def get_tour():
    url = "http://apis.data.go.kr/B551011/KorService1/areaBasedList1"
    MobileOs = "ETC"
    MobileApp = "Plan4Land"
    dataType = "json"
    serviceKey = "IgykVu0qTZbi+3YtfC645Gag515ri7KsHHpE3r6Ef3iTiNaSDdmKZJizindrVRYzN4DEDknnAjoziHs/KDj/6g=="
    params = {
        "MobileOS": MobileOs,
        "MobileApp": MobileApp,
        "_type": dataType,
        "serviceKey": serviceKey
    }

    try:
        response = requests.get(url, params=params)
    except requests.exceptions.RequestException as e:
        print(f"tour 정보 요청 실패 : {e}")
        return json.dumps({"에러": str(e)}, ensure_ascii=False)

    data = response.json()
    total_counts = data['response']['body']['totalCount']
    print(total_counts)

    items_total = []

    for page in range(1, (total_counts//200+2)):
        params = {
            "numOfRows": 200,
            "pageNo": page,
            "MobileOS": MobileOs,
            "MobileApp": MobileApp,
            "_type": dataType,
            "serviceKey": serviceKey
        }
        response = requests.get(url, params=params)
        data = response.json()
        items = data['response']['body']['items']['item']
        items_total.extend(items)
        time.sleep(2)

    with open("D:/dev/Final_Project/Final_Flask/tour_info.json", "w", encoding="utf-8") as f:
        json.dump(items_total, f, ensure_ascii=False, indent=4)