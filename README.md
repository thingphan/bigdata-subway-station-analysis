Markdown
# 서울시 지하철 접근성 소외지역 시각화 분석 및 후보지 도출 시스템 설계
> **빅데이터 프로그래밍 기말 프로젝트** > **학번:** 60220889 / **성명:** 김명관

---

## 1. 프로젝트 개요 및 문제 정의

현재 수도권의 대중교통망은 외형적으로 잘 구축되어 있으나, 실제 생활인구 및 유동인구의 분포와 비교할 때 지하철 접근성이 현저히 떨어지는 '교통 소외 지역'이 상존합니다. 특히 명지대학교 인근과 같이 대중교통 의존도가 높고 등하교 시간대 상습적인 혼잡을 겪는 지역이 대표적입니다.

본 프로젝트는 서울시 전역의 다차원 데이터(생활인구, 정류장별 승하차, 지하철 역사 위치 등)를 통합 분석하여, 인구 밀집도 대비 지하철 접근성이 낮은 지역을 정량적으로 식별하고, 신규 지하철역 입지 타당성을 검토할 수 있는 시각화 분석 시스템을 설계하는 것을 목적으로 합니다.

### 4가지 핵심 분석 질문
1. **[공간]** 해당 버스 정류장이 지하철역으로부터 1km 이상 떨어진 물리적 소외 지역에 해당하는가?
2. **[실수요]** 해당 소외 지역 정류장의 실제 대중교통(버스) 일일 이용 수요는 어느 정도인가?
3. **[잠재수요]** 해당 소외 지역 정류장이 속한 행정동의 상시 생활인구 밀집도는 높은가?
4. **[인사이트]** 도출된 교통 소외 정류장들이 특정 행정동에 뚜렷하게 군집화(Clustering)되어 나타나는가?

---

## 2. 시스템 아키텍처 및 기술 스택

대용량 시계열 데이터를 안정적으로 처리하고 공간 연산의 복잡도를 분산하기 위해 **Hadoop-Spark-Hive**로 이어지는 분산 처리 파이프라인을 구축하였습니다.

### 기술 스택 (SW Stack)
* **OS / Platform:** Linux (HDP - Hortonworks Data Platform)
* **Storage:** HDFS (분산 파일 시스템)
* **Data Processing:** Apache Spark (DataFrame API, Spark SQL 및 공간 연산)
* **Data Warehouse:** Apache Hive (분석 데이터 마트 구성 및 결과 분산 조회)
* **Language & Automation:** Python (PySpark, PyProj 활용), Shell Script (`bash`)
* **Visualization:** Python Plotly (VS Code 로컬 환경)

### 데이터 파이프라인 흐름
1. **Ingestion (수집):** `data.py`를 통해 서울 열린데이터 광장 API로부터 Raw 데이터(CSV)를 수집하여 HDFS 경로에 로드합니다.
2. **Processing (가공/변환):** `join_data.py`로 데이터 정제 및 그룹화 조인을 수행한 후, `convert.py`를 통해 투영좌표계를 경위도 좌표계(WGS84, EPSG:4326)로 표준화합니다.
3. **Analytics (공간 연산):** `analysis.py`에서 Spark SQL의 Cross Join 및 유클리드 거리 공식을 활용해 정류장-지하철역 간의 최단 거리(`distance_km`)를 연산합니다.
4. **Serving (조회):** `run_pipeline.sh`를 통해 분석 결과를 Hive 외부 테이블(External Table)로 연결하고 정량적 조건에 부합하는 상위 100개 데이터를 집계·추출합니다.

---

## 3. GitHub Repository 구조

```text
bigdata-subway-station-analysis/
├── README.md
├── .gitignore
├── .env                  # API 인증키 관리 (깃허브 업로드 제외)
└── src/
    └── pipeline/
        ├── data.py          # 공공 API 데이터 수집 및 HDFS 적재
        ├── join_data.py     # 버스 및 행정동 데이터 1차 가공 및 Join
        ├── convert.py       # 좌표계 변환 처리 (EPSG:5181 -> EPSG:4326)
        ├── analysis.py      # Spark SQL 기반 최단 거리 분산 연산
        ├── run_pipeline.sh  # 전체 파이프라인 자동화 및 Hive 조회 스크립트
        └── plot.py          # Plotly 기반 지도 시각화 대시보드 (로컬 실행)
4. 데이터 소스 (Dataset Information)
모든 데이터는 서울 열린데이터 광장 공공 API를 활용하여 자동 수집되었습니다. (총 누적 용량 100MB 초과)

행정동 단위 서울 생활인구 (내국인) [seoul_living_pop_dong_2025.csv]

서울시 상권분석서비스 (영역-행정동) [dong_area.csv]

서울시 역사마스터 정보 [subway_station_coords.csv]

서울시 버스노선별 정류장별 시간대별 승하차 인원 정보 (2025년 1년치) [bus_time_data_2025.csv]

서울시 버스정류소 위치정보 [bus_stop_coords.csv]

5. 실행 가이드 (Execution Guide)
가동하기 전 HDFS 내에 /user/maria_dev/project 경로가 생성되어 있어야 합니다.

Step 1. 환경변수 설정 (.env)
프로젝트 최상위 폴더에 .env 파일을 생성하고 서울 열린데이터 광장에서 발급받은 인증키를 입력합니다.

Bash
echo 'SEOUL_API_KEY="본인의_서울시_API_인증키"' > .env
Step 2. 파이프라인 스크립트 실행 권한 부여
Bash
cd src/pipeline
chmod +x run_pipeline.sh
Step 3. 엔드투엔드 파이프라인 구동 (자동화)
수집, 전처리, 좌표 변환, 최단 거리 연산, Hive 테이블 데이터 마트 추출까지 일괄 실행됩니다.

Bash
./run_pipeline.sh
최종 추출된 데이터는 동일 디렉토리에 final_top100_report.csv로 저장됩니다.

Step 4. 시각화 대시보드 확인 (로컬 환경)
추출된 final_top100_report.csv 파일을 로컬 개발 환경(VS Code 등)으로 가져온 후 아래 명령어로 대시보드를 구동합니다.

Bash
python plot.py
6. 분석 결과 및 핵심 인사이트
1) 시각화 지표 매핑 기준
Size (버블 크기): 해당 정류장의 daily_total_on(일일 총 승차 인원)을 반영하여 수요가 높은 곳을 시각적으로 강조.

Color (색상 척도): Inferno 컬러 스케일을 적용하여 지하철역과의 거리가 멀수록(distance_km >= 1.0) 더 밝고 붉게 표현.

2) 핵심 인사이트 (Clustering 현상 파악)
시각화 분석 결과, 특정 행정동 단위로 짙은 붉은색 버블과 거대한 크기의 버블이 강하게 군집화(Clustering)되는 현상이 정량적으로 확인되었습니다. 이는 해당 구역 주민들이 지하철 인프라의 부재로 인해 버스 교통망에 과도하게 의존하고 있음을 증명합니다. 본 시스템을 통해 도출된 소외 구역 군집 중심지는 단순한 버스 노선 증차를 넘어, 신규 거점 지하철역 신설 및 경전철 환승 인프라 구축의 타당성을 뒷받침하는 강력한 데이터적 근거로 활용될 수 있습니다.

7. AI Tool Usage
Gemini 3.1 Pro: 프로젝트 기획 단계에서의 명칭 아이디어 및 Hadoop-Spark-Hive 기술 스택 연동 설계 참고, 데이터 처리 중 하둡 분산 환경에서의 Spark UDF 구현 및 pyproj 라이브러리 의존성 에러 디버깅 보조, Plotly Subplots 레이아웃 구성 코드 작성에 활용함.
