# 서울시 지하철 접근성 소외지역 시각화 분석 및 후보지 도출 시스템 설계

> 빅데이터 프로그래밍 기말 프로젝트
> 학번: 60220889
> 성명: 김명관

---

# 1. 프로젝트 개요 및 문제 정의

현재 수도권의 대중교통망은 외형적으로 잘 구축되어 있으나, 실제 생활인구 및 유동인구의 분포와 비교할 때 지하철 접근성이 현저히 떨어지는 교통 소외 지역이 존재한다. 특히 명지대학교 인근과 같이 대중교통 의존도가 높고 등하교 시간대 상습적인 혼잡을 겪는 지역이 대표적이다.

본 프로젝트는 서울시 전역의 다차원 데이터(생활인구, 정류장별 승하차 인원, 지하철 역사 위치 등)를 통합 분석하여 인구 밀집도 대비 지하철 접근성이 낮은 지역을 정량적으로 식별하고, 신규 지하철역 입지 타당성을 검토할 수 있는 시각화 분석 시스템을 설계하는 것을 목표로 한다.

## 핵심 분석 질문

1. 해당 버스 정류장이 지하철역으로부터 1km 이상 떨어진 물리적 소외 지역에 해당하는가?
2. 해당 소외 지역 정류장의 실제 대중교통(버스) 이용 수요는 어느 정도인가?
3. 해당 소외 지역 정류장이 속한 행정동의 생활인구 밀집도는 높은가?
4. 교통 소외 정류장들이 특정 행정동에 군집화되어 나타나는가?

---

# 2. 시스템 아키텍처 및 기술 스택

대용량 시계열 데이터를 안정적으로 처리하고 공간 연산의 복잡도를 분산하기 위해 Hadoop-Spark-Hive 기반의 분석 파이프라인을 구축하였다.

## 기술 스택

| 구분             | 기술                                      |
| -------------- | --------------------------------------- |
| OS / Platform  | Linux (HDP)                             |
| Storage        | HDFS                                    |
| Processing     | Apache Spark (DataFrame API, Spark SQL) |
| Data Warehouse | Apache Hive                             |
| Language       | Python (PySpark, PyProj)                |
| Automation     | Bash Script                             |
| Visualization  | Plotly                                  |

## 데이터 파이프라인

### 1. Ingestion

* `data.py`
* 서울 열린데이터 광장 API 데이터 수집
* HDFS 적재

### 2. Processing

* `join_data.py`

* 데이터 정제 및 Join

* `convert.py`

* 좌표계 변환

* EPSG:5181 → EPSG:4326

### 3. Analytics

* `analysis.py`
* Spark SQL 기반 공간 분석
* 정류장 ↔ 지하철역 최단거리 계산

### 4. Serving

* `run_pipeline.sh`
* Hive External Table 생성
* 상위 후보지 집계 및 조회

---

# 3. 프로젝트 구조

```text
bigdata-subway-station-analysis/
├── README.md
├── .gitignore
├── .env
└── src/
    └── pipeline/
        ├── data.py
        ├── join_data.py
        ├── convert.py
        ├── analysis.py
        ├── run_pipeline.sh
        └── plot.py
```

---

# 4. 데이터셋

모든 데이터는 서울 열린데이터 광장 Open API를 통해 자동 수집하였다.

## 사용 데이터

* 행정동 단위 서울 생활인구 (내국인)

  * `seoul_living_pop_dong_2025.csv`

* 서울시 상권분석서비스 (영역-행정동)

  * `dong_area.csv`

* 서울시 역사 마스터 정보

  * `subway_station_coords.csv`

* 서울시 버스노선별 정류장별 시간대별 승하차 인원

  * `bus_time_data_2025.csv`

* 서울시 버스정류소 위치정보

  * `bus_stop_coords.csv`

---

# 5. 실행 가이드

## Step 1. 환경 변수 설정

프로젝트 루트에 `.env` 파일 생성

```bash
echo 'SEOUL_API_KEY="YOUR_API_KEY"' > .env
```

## Step 2. 실행 권한 부여

```bash
cd src/pipeline
chmod +x run_pipeline.sh
```

## Step 3. 전체 파이프라인 실행

```bash
./run_pipeline.sh
```

실행 결과:

```text
final_top100_report.csv
```

생성

## Step 4. 시각화 실행

```bash
python plot.py
```

---

# 6. 분석 결과 및 인사이트

## 시각화 기준

### 버블 크기

* `daily_total_on`
* 일일 총 승차 인원

### 색상

* `distance_km`
* 지하철역과의 거리

거리 1km 이상인 정류장일수록 붉은색으로 표현된다.

## 핵심 인사이트

분석 결과 특정 행정동 단위에서 다음 특징이 확인되었다.

* 높은 생활인구
* 높은 버스 이용량
* 낮은 지하철 접근성

특히 교통 소외 정류장이 특정 지역에 군집화되는 현상이 관찰되었으며, 이는 신규 지하철역 또는 경전철 환승 거점 검토 시 활용 가능한 데이터 기반 근거를 제공한다.

---

# 7. AI Tool Usage

본 프로젝트에서는 다음과 같은 AI 도구를 활용하였다.

### Gemini 3.1 Pro

* 프로젝트 기획 아이디어 도출
* Hadoop-Spark-Hive 파이프라인 설계 검토
* Spark UDF 구현 보조
* PyProj 관련 오류 디버깅 지원
* Plotly 시각화 코드 작성 보조

AI는 개발 보조 도구로 활용되었으며, 최종 구현 및 검증은 직접 수행하였다.
