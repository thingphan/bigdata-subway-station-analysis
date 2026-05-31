# -*- coding: utf-8 -*-
import os
import subprocess
import pandas as pd
import pyproj

HDFS_INPUT = "/user/maria_dev/project/result_pop_data"
LOCAL_INPUT = "result_pop_data.csv"
LOCAL_OUTPUT = "result_pop_data_converted.csv"
HDFS_OUTPUT = "/user/maria_dev/project/result_pop_data_converted.csv"

def run_cmd(cmd):
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    if result.returncode != 0:
        raise RuntimeError(f"fail: {' '.join(cmd)}\n{result.stderr}")
    return result.stdout

# 1. HDFS -> 로컬 다운로드
run_cmd(["hdfs", "dfs", "-get", "-f", HDFS_INPUT, LOCAL_INPUT])

# 2. 로컬 파일 읽기
df = pd.read_csv(LOCAL_INPUT)

# 3. 좌표 변환
transformer = pyproj.Transformer.from_crs("epsg:5181", "epsg:4326", always_xy=True)

def transform(x, y):
    lon, lat = transformer.transform(x, y)
    return lon, lat

df[["DONG_LON", "DONG_LAT"]] = df.apply(
    lambda r: pd.Series(transform(r["XCNTS_VALUE"], r["YDNTS_VALUE"])),
    axis=1
)

# 4. 로컬 저장
df.to_csv(LOCAL_OUTPUT, index=False)

# 5. 로컬 -> HDFS 업로드
run_cmd(["hdfs", "dfs", "-put", "-f", LOCAL_OUTPUT, HDFS_OUTPUT])

print("done:", HDFS_OUTPUT)