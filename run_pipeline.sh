#!/bin/bash

set -e

echo "======================================================"
echo "파이프라인 시작"
echo "======================================================"

echo "[1] 데이터 수집 및 HDFS 업로드 (data.py)"
python3.6 data.py
echo "1 done"
echo "------------------------------------------------------"

echo "[2] spark 데이터 전처리 및 1차 조인 (join_data.py)"
hadoop fs -rm -r -skipTrash /user/maria_dev/project/result_bus_data 2>/dev/null || true
hadoop fs -rm -r -skipTrash /user/maria_dev/project/result_pop_data 2>/dev/null || true
spark-submit --master yarn --deploy-mode cluster join_data.py
echo "2 done"
echo "------------------------------------------------------"

echo "[3] 좌표계 변환 (EPSG:5181 -> WGS84) (convert.py)"
python3.6 convert.py
echo "3 done"
echo "------------------------------------------------------"

echo "[4] 스파크 거리 계산 및 최종 분석 (analysis.py)"
hadoop fs -rm -r -skipTrash /user/maria_dev/project/final 2>/dev/null || true
spark-submit --master yarn --deploy-mode cluster analysis.py
echo "4 done"
echo "------------------------------------------------------"

echo "[5] Hive로 Top 100 리포트 추출"
export HADOOP_CLIENT_OPTS="-Dfile.encoding=UTF-8"
# 하이브 쿼리 실행 후 결과를 로컬 CSV로 저장
hive --silent=true --showHeader=true --outputformat=csv2 -e "SELECT * FROM final_transit_blind_spot WHERE distance_km >= 1.0 ORDER BY total_living_pop DESC, daily_total_on DESC LIMIT 100;" > final_top100_report.csv

# 최종 리포트를 HDFS에 백업
hadoop fs -put -f final_top100_report.csv /user/maria_dev/project/
echo "5 done: final_top100_report.csv 생성 및 HDFS 업로드"
echo "======================================================"
echo "all done"
echo "======================================================"