# -*- coding: utf-8 -*-
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, expr, sum as _sum


spark = SparkSession.builder \
    .appName("SeoulData_Preprocess_and_Join") \
    .getOrCreate()


spark.sparkContext.setLogLevel("WARN")

# ==========================================
# 버스 데이터 전처리 및 조인 
# ==========================================
df_coords = spark.read.csv("hdfs:///user/maria_dev/project/bus_stop_coords.csv", header=True, inferSchema=True)
df_time = spark.read.csv("hdfs:///user/maria_dev/project/bus_time_data_2025.csv", header=True, inferSchema=True)


#좌표 등 필요한 컬럼만 남기고 지우기
df_coords_processed = df_coords.select("STOPS_NO", "STOPS_NM", "XCRD", "YCRD")

#각 시간대별 승하차 인구 수 모두 합산
hr_columns = [c for c in df_time.columns if c.startswith("HR_")]
sum_expression = " + ".join(hr_columns)

df_time_processed = df_time.withColumn("ROW_TOTAL", expr(sum_expression)) \
                            .groupBy("STOPS_ARS_NO") \
                            .agg(_sum("ROW_TOTAL").alias("TOTAL_PASSENGERS"))

#둘이 이너 Inner join
#조건: bus_stop_coords의 STOPS_NO == bus_time_data_2025의 STOPS_ARS_NO
df_bus_joined = df_coords_processed.join(
    df_time_processed,
    df_coords_processed.STOPS_NO == df_time_processed.STOPS_ARS_NO,
    "inner"
).drop("STOPS_ARS_NO")

# ==========================================
# 행정동 + 생활인구 데이터 전처리 및 조인 
# ==========================================
# 1. HDFS에서 파일 불러오기
df_dong_area = spark.read.csv("hdfs:///user/maria_dev/project/dong_area.csv", header=True, inferSchema=True)
df_pop = spark.read.csv("hdfs:///user/maria_dev/project/seoul_living_pop_dong_2025.csv", header=True, inferSchema=True)

# 2. 생활인구 데이터 전처리 (행정동별 1년치 총합 구하기)
# ADSTRD_CODE_SE를 기준으로 그룹화하고, TOT_LVPOP_CO(총생활인구수)를 모두 더함.
df_pop_processed = df_pop.groupBy("ADSTRD_CODE_SE") \
                        .agg(_sum("TOT_LVPOP_CO").alias("ANNUAL_TOT_LVPOP_CO"))

# 3. 행정동 영역과 생활인구 Inner Join
# 조건: dong_area의 'ADSTRD_CD' == pop_processed의 'ADSTRD_CODE_SE'
df_dong_joined = df_dong_area.join(
    df_pop_processed,
    df_dong_area.ADSTRD_CD == df_pop_processed.ADSTRD_CODE_SE,
    "inner"
).drop("ADSTRD_CODE_SE") 


# ==========================================
# 저장
# ==========================================
print("\n저장")

# 1. 버스 조인 데이터 저장 
df_bus_joined.write \
    .mode("overwrite") \
    .option("header", "true") \
    .csv("hdfs:///user/maria_dev/project/result_bus_data")

# 2. 행정동 생활인구 조인 데이터 저장 
df_dong_joined.write \
    .mode("overwrite") \
    .option("header", "true") \
    .csv("hdfs:///user/maria_dev/project/result_pop_data")

print("완료")

spark.stop()