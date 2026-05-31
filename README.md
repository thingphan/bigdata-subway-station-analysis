# bigdata-subway-station-analysis

# 서울시 지하철 접근성 소외지역 시각화 분석 및 후보지 도출 시스템 설계

---

## 1. 문제 정의

현재 수도권의 대중교통망은 외형적으로는 잘 구축되어 있으나, 실제 생활인구 및 유동인구의 분포와 비교할 때 지하철 접근성이 현저히 떨어지는 '교통 소외 지역'이 상존함.

특히 명지대학교 인근과 같이 대중교통 의존도가 높고 출퇴근 시간대 상습적인 혼잡을 겪는 지역이 대표적임.

본 프로젝트는 서울시 전역의 다차원 데이터(생활인구, 정류장별 승하차, 지하철 역사 위치)를 통합 분석하여, 인구 밀집도 대비 지하철 접근성이 낮은 지역을 정량적으로 식별하고, 신규 지하철역 입지 타당성을 검토할 수 있는 시각화 분석 시스템을 설계하는 것을 목적으로 함.

본 프로젝트는 단순히 인구수와 노선도를 비교하는 것이 아니라, 서울 전역의 정류장별 시간대별 승하차 데이터(연간 수천만 건)와 행정동별 상시 생활인구 데이터를 정밀하게 결합해야 하고, 서울 시내 모든 버스 정류장과 지하철역 사이의 거리(공간 연산)를 계산하는 과정은 수십만 번 이상의 반복 연산이 요구되므로 데이터 규모 및 다양성, 연산 복잡도 측면에서 빅데이터 기술이 필요함.

---

## 2. 사용 데이터

서울시 공공데이터포털에서 제공하는 공간 데이터, 인구 통계 데이터, 교통 이용 데이터를 활용함.

### 📌 행정동 단위 서울 생활인구(내국인)

**파일명**

* `seoul_living_pop_dong_2025.csv`

**출처**

* https://data.seoul.go.kr/dataList/OA14991/A/1/datasetView.do

**설명**

* 특정 시점(일 단위)에 행정동 내에 존재하는 인구 통계 데이터를 수집하여, 해당 지역의 상주 및 유동인구 규모를 파악함.

---

### 📌 서울시 상권분석서비스(영역-행정동)

**파일명**

* `dong_area.csv`

**출처**

* https://data.seoul.go.kr/dataList/OA14991/A/1/datasetView.do

**설명**

* 각 행정동의 좌표 및 영역 정보를 수집하여 공간 매핑의 기준점으로 활용함.

---

### 📌 서울시 역사마스터 정보

**파일명**

* `subway_station_coords.csv`

**출처**

* https://data.seoul.go.kr/dataList/OA-21232/S/1/datasetView.do

**설명**

* 서울 시내 모든 지하철역의 위치 정보를 수집하여 버스 정류장과 지하철역 간의 최단 거리를 계산하는 기준으로 활용함.

---

### 📌 서울시 버스노선별 정류장별 시간대별 승하차 인원 정보

**파일명**

* `bus_time_data_2025.csv`

**출처**

* https://data.seoul.go.kr/dataList/OA-12913/S/1/datasetView.do

**설명**

* 노선별·정류장별 시간대별 승하차 승객 데이터를 통해 각 정류장의 실질적인 대중교통 이용 수요를 도출함.

---

### 📌 서울시 버스정류소 위치정보

**파일명**

* `bus_stop_coords.csv`

**출처**

* https://data.seoul.go.kr/dataList/OA-15067/A/1/datasetView.do

**설명**

* 모든 버스 정류장의 좌표를 확보하여 공간 분석의 기초 데이터로 활용함.

---

## 3. 사용 기술 및 환경

본 프로젝트는 대용량 시계열 데이터를 안정적으로 처리하기 위해 Hadoop-Spark-Hive로 이어지는 분산 처리 스택을 채택함.

### SW 스택

* **OS/Platform**

  * Linux (HDP - Hortonworks Data Platform)

* **Data Processing**

  * Apache Spark (ETL 및 공간 연산)

* **Storage**

  * HDFS (분산 파일 시스템)

* **Data Warehouse**

  * Apache Hive (분석 데이터 마트)

* **Language**

  * Python (PySpark, PyProj 라이브러리 활용)

---

### Pipeline

#### Ingestion (수집)

* Python API 연동을 통해 데이터를 수집하고, HDFS `/user/maria_dev/project` 경로에 Raw 데이터를 로드함.

#### Processing (가공/변환)

* Spark를 사용하여 데이터 스키마 정제 및 좌표계 변환을 수행함.

#### Analytics (공간 조인)

* 버스 정류장-행정동-지하철역 간의 최단 거리를 연산하여 `Distance_km` 지표를 산출함.

#### Serving (조회)

* Hive 외부 테이블(External Table)을 통해 분석된 결과를 비즈니스 로직(1km 이상 소외지역 필터링)에 맞춰 실시간 조회 가능하도록 함.

---

### 저장 포맷

#### 중간 저장

* CSV (HDFS 기반, 파이프라인 각 단계 간의 호환성 및 범용성 고려)

#### 분석 결과

* CSV (Hive를 통한 최종 추출, 엑셀 호환성 확보)

---

### 프로젝트 구성

* `data.py`
* `analysis.py`
* `convert.py`
* `join_data.py`
* `run_pipeline.sh`

`data.py`, `analysis.py`, `convert.py`, `join_data.py`에서는 Spark를 사용하며, `run_pipeline.sh`에서는 Hive 기술 스택을 사용함.

---

### 실행 방법

`run_pipeline.sh`로 데이터 수집부터 결과 산출까지의 파이프라인이 자동화되어 있음.

```bash
./run_pipeline.sh
```

※ HDFS `/user/maria_dev/project` 경로가 존재해야 함.

---

## 4. 주차별 구현 계획

* **11주차**

  * 주제 선정 및 데이터 조사
  * GitHub 환경 구성
  * 데이터 수집 테스트

* **12주차**

  * 공공데이터 수집 코드 작성
  * HDFS 적재 및 데이터 확인

* **13주차**

  * Spark 기반 데이터 전처리
  * 생활인구와 교통 데이터 결합

* **14주차**

  * 교통 취약 지역 분석
  * 혼잡도 및 접근성 시각화

* **15주차**

  * 전체 파이프라인 점검
  * 최종 결과 정리 및 발표 자료 작성

---

## 5. AI Tool Usage

* 프로젝트명 아이디어 참고
* 기술 스택 및 분석 방향 참고
