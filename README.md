# 여행지 추천 시스템

## 프로젝트 개요
이 프로젝트는 사용자의 특성과 여행 스타일을 기반으로 맞춤형 여행지를 추천하는 서비스입니다. 머신러닝 모델과 Elasticsearch를 활용하여 개인화된 여행지 추천 기능을 제공합니다.

## 기술 스택
- **백엔드**: Python, Flask
- **데이터베이스**: Elasticsearch
- **머신러닝**: CatBoost
- **배포**: Docker, Docker Compose

## 주요 기능
1. **개인화된 여행지 추천**: 사용자의 성별, 나이, 여행 스타일, 동반자 수 등을 고려한 맞춤형 여행지 추천
2. **여행 일지 관리**: Elasticsearch를 활용한 여행 일지 데이터 저장 및 검색
3. **자동 데이터 업데이트**: 스케줄러를 통한 여행지 정보의 주기적 업데이트

## 프로젝트 구조
```
  ├── ML/                  : 머신러닝 관련 코드 및 모델 파일이 위치합니다.
  │   ├── learning/        : 모델 학습 관련 스크립트가 포함됩니다.
  │   ├── recomendation.py : 사용자 특성 기반 여행지 추천 알고리즘을 구현합니다.
  │   ├── catboost_model.cbm : 학습된 CatBoost 모델 파일입니다.
  │   └── label_encoder.pkl : 레이블 인코딩 정보를 저장합니다.
  │
  ├── api/                 : API 엔드포인트 관련 코드가 위치합니다.
  │   └── tour_spot.py     : 여행지 정보 관련 API 기능을 처리합니다.
  │
  ├── csv/                 : 데이터 파일을 저장하는 디렉토리입니다.
  │
  ├── elastic/             : Elasticsearch 관련 기능을 구현한 모듈입니다.
  │   ├── diary_elastic.py : 여행 일지 인덱스 생성 및 관리를 담당합니다.
  │   ├── tour_to_elastic.py : 여행지 데이터를 Elasticsearch에 적재합니다.
  │   ├── update_spot.py   : 여행지 정보 자동 업데이트 기능을 구현합니다.
  │   ├── delete_elastic_index.py : Elasticsearch 인덱스 삭제 기능을 제공합니다.
  │   └── convert_snake_case.py : 데이터 정규화를 위한 스크립트입니다.
  │
  ├── app.py               : 메인 Flask 애플리케이션으로 웹 서버와 API를 구현합니다.
  ├── new.py               : 서버 초기화 스크립트로 인덱스 재생성을 담당합니다.
  │
  ├── tour_spot_info.json : 여행지 정보를 포함하는 데이터 파일입니다.
  │
  ├── Dockerfile           : Docker 이미지 빌드 설정 파일입니다.
  └── docker-compose-ec2.yml : Docker Compose 배포 설정 파일입니다.
```
## 사용된 패키지 및 라이브러리

### 백엔드 및 웹 서버
- **Flask**: 웹 서버 및 API 구현을 위한 경량 프레임워크
- **APScheduler**: 백그라운드 작업 스케줄링 라이브러리

### 데이터베이스 및 검색 엔진
- **Elasticsearch**: 분산형 RESTful 검색 및 분석 엔진
- **elasticsearch-py**: Elasticsearch Python 클라이언트

### 머신러닝 및 데이터 분석
- **CatBoost**: 그래디언트 부스팅 의사결정 트리 구현 라이브러리
- **NumPy**: 수치 연산 및 배열 처리 라이브러리
- **Pandas**: 데이터 분석 및 조작 라이브러리
- **Scikit-learn**: 머신러닝 알고리즘 및 데이터 전처리 라이브러리

### 유틸리티 및 기타
- **python-dotenv**: 환경 변수 관리 라이브러리
- **requests**: HTTP 라이브러리
- **logging**: 로깅 기능 제공
- **datetime**: 날짜 및 시간 조작 라이브러리
- **json**: JSON 데이터 처리 라이브러리
- **re**: 정규 표현식 지원 모듈
- **os**: 운영 체제 인터페이스 모듈

### 배포 및 인프라
- **Docker**: 애플리케이션 컨테이너화 플랫폼
- **Docker Compose**: 다중 컨테이너 Docker 애플리케이션 정의 및 실행 도구

