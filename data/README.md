##  사용 데이터

서울시 공공데이터포털에서 제공하는 공간 데이터, 인구 통계 데이터, 교통 이용 데이터를 활용함.

| 데이터명 | 파일명 | 설명 | 출처 |
| :--- | :--- | :--- | :--- |
| **행정동 단위 서울 생활인구(내국인)** | `seoul_living_pop_dong_2025.csv` | 특정 시점(일 단위) 행정동 내 상주 및 유동인구 규모 파악 | [링크](https://data.seoul.go.kr/dataList/OA-14991/A/1/datasetView.do;jsessionid=352B86F9D55D154F919948EE35444433.new_portal-svr-11) |
| **서울시 상권분석서비스(행정동)** | `dong_area.csv` | 각 행정동의 좌표 및 영역 정보를 수집하여 공간 매핑 기준점으로 활용 | [링크](https://data.seoul.go.kr/dataList/OA-22160/S/1/datasetView.do) |
| **서울시 역사마스터 정보** | `subway_station_coords.csv` | 서울 시내 지하철역 위치 정보 (버스 정류장과의 최단 거리 계산 기준) | [링크](https://data.seoul.go.kr/dataList/OA-21232/S/1/datasetView.do) |
| **버스 정류장별 시간대별 승하차** | `bus_time_data_2025.csv` | 노선별·정류장별 시간대별 승하차 승객 데이터로 실질적 수요 도출 | [링크](https://data.seoul.go.kr/dataList/OA-12913/S/1/datasetView.do) |
| **서울시 버스정류소 위치정보** | `bus_stop_coords.csv` | 모든 버스 정류장의 좌표를 확보하여 공간 분석의 기초 데이터로 활용 | [링크](https://data.seoul.go.kr/dataList/OA-15067/A/1/datasetView.do) |


##  추출 데이터
| 데이터명 | 파일명 | 스키마 |
| :--- | :--- | :--- |
| **버스 데이터** | `result_bus_data` | 정류소번호(STOPS_NO), 정류소명(STOPS_NM), X좌표(XCRD), Y좌표(YCRD), 총승하차인원(TOTAL_PASSENGERS) |
| **행정동 데이터** | `result_pop_data` | 행정동_코드(ADSTRD_CD), 행정동_명(ADSTRD_NM), X좌표(XCNTS_VALUE), Y좌표(YDNTS_VALUE), 영역_면적(RELM_AR), 총생활인구수(ANNUAL_TOT_LVPOP_CO) |
| **행정동 좌표 변환 데이터** | `result_pop_data_converted` | 행정동_코드(ADSTRD_CD), 행정동_명(ADSTRD_NM), X좌표(XCNTS_VALUE), Y좌표(YDNTS_VALUE), 영역_면적(RELM_AR), 총생활인구수(ANNUAL_TOT_LVPOP_CO), 경도(DONG_LON), 위도(DONG_LAT) |
| **final 데이터** | `final` | 정류소명(STOPS_NM), 행정동_명(ADSTRD_NM), X좌표(XCRD), Y좌표(YCRD), 총생활인구수(total_living_pop), 지하철역간의거리(distance_km), 일일총승하차인원(daily_total_on) |
| **final top 100 데이터** | `final_top100_report` | 정류소명(rankeddata.stops_nm), 행정동_명(rankeddata.adstrd_nm), X좌표(rankeddata.lon), Y좌표(rankeddata.lat), 총생활인구수(rankeddata.total_living_pop), 지하철역간의거리(rankeddata.distance_km), 일일총승하차인원(rankeddata.daily_total_on), 생활인구정규화(rankeddata.p_norm), 승하차인원정규화(rankeddata.b_norm), 지하철거리정규화(rankeddata.d_norm), 교통취약점수(robust_score) |
