# -*- coding: utf-8 -*-
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("Final_Distance_Calc").getOrCreate()
spark.conf.set("spark.sql.crossJoin.enabled", "true")

# [1] 데이터 불러오기 (좌표 변환이 이미 끝난 파일을 사용)
bus_df = spark.read.csv("hdfs:///user/maria_dev/project/result_bus_data", header=True, inferSchema=True)
dong_df = spark.read.csv("hdfs:///user/maria_dev/project/result_pop_data_converted.csv", header=True, inferSchema=True) # 변환된 파일!
subway_df = spark.read.csv("hdfs:///user/maria_dev/project/subway_station_coords.csv", header=True, inferSchema=True)

# [2] SQL 뷰 생성
bus_df.createOrReplaceTempView("bus")
dong_df.createOrReplaceTempView("dong")
subway_df.createOrReplaceTempView("subway")

# [3] 거리 계산 쿼리 실행
query = """
WITH BusDongMapping AS (
    SELECT STOPS_NO, STOPS_NM, XCRD, YCRD, TOTAL_PASSENGERS, ADSTRD_NM, ANNUAL_TOT_LVPOP_CO
    FROM (
        SELECT 
            b.STOPS_NO, b.STOPS_NM, b.XCRD, b.YCRD, b.TOTAL_PASSENGERS,
            d.ADSTRD_NM, d.ANNUAL_TOT_LVPOP_CO,
            ROW_NUMBER() OVER(
                PARTITION BY b.STOPS_NO 
                ORDER BY SQRT(POWER((b.YCRD - d.DONG_LAT) * 111.0, 2) + POWER((b.XCRD - d.DONG_LON) * 88.0, 2)) ASC
            ) as rn
        FROM bus b CROSS JOIN dong d
    ) WHERE rn = 1
),
BusSubwayDist AS (
    SELECT 
        b.STOPS_NO,
        MIN(SQRT(POWER((b.YCRD - s.LAT) * 111.0, 2) + POWER((b.XCRD - s.LOT) * 88.0, 2))) as min_subway_dist
    FROM BusDongMapping b CROSS JOIN subway s
    GROUP BY b.STOPS_NO
)
SELECT 
    b.STOPS_NM, 
    b.ADSTRD_NM, 
    b.XCRD, b.YCRD, 
    CAST(b.ANNUAL_TOT_LVPOP_CO AS BIGINT) as total_living_pop,
    ROUND(s.min_subway_dist, 2) as distance_km, 
    b.TOTAL_PASSENGERS as daily_total_on
FROM BusDongMapping b
JOIN BusSubwayDist s ON b.STOPS_NO = s.STOPS_NO
"""

spark.sql(query).write.mode("overwrite").option("header", "true").csv("hdfs:///user/maria_dev/project/final")
print("완료")
spark.stop()