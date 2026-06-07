import sys
import io
import requests
import pandas as pd
import time
from datetime import datetime, timedelta
import subprocess
import os  
from dotenv import load_dotenv

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv() 
API_KEY = os.environ.get("SEOUL_API_KEY")

if not API_KEY:
    raise ValueError("API 키가 없습니다. .env 파일을 확인해주세요.")

HDFS_PATH = "/user/maria_dev/project/" 

def upload_to_hdfs(file_name):
    command = f"hdfs dfs -put -f {file_name} {HDFS_PATH}"
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"성공: {file_name}\n")
    except subprocess.CalledProcessError as e:
        print(f"실패: {e}\n") 

def get_seoul_data_all(api_name, total_count):
    all_rows = []
    for start_idx in range(1, total_count, 1000):
        end_idx = start_idx + 999
        url = f"http://openapi.seoul.go.kr:8088/{API_KEY}/json/{api_name}/{start_idx}/{end_idx}/"
        
        try:
            response = requests.get(url)
            data = response.json()
            
            key = list(data.keys())[0]
            if "row" in data[key]:
                all_rows.extend(data[key]["row"])
            else:
                break
        except Exception as e:
            print(f"[{api_name}] 에러 발생:", e)
            break
        time.sleep(0.1)
    return pd.DataFrame(all_rows)


# ==========================================
# 1. 버스 정류소 좌표 데이터
# ==========================================
print(" 버스 정류소 좌표 수집")
bus_df = get_seoul_data_all("busStopLocationXyInfo", 13000)
bus_file = "bus_stop_coords.csv"
bus_df.to_csv(bus_file, index=False, encoding="utf-8-sig")
print(f"버스 정류소 {len(bus_df)}건 로컬 저장")
upload_to_hdfs(bus_file)


# ==========================================
# 2. 지하철역 좌표 데이터
# ==========================================
print(" 지하철역 좌표 수집")
sub_df = get_seoul_data_all("subwayStationMaster", 2000) 
sub_file = "subway_station_coords.csv"
sub_df.to_csv(sub_file, index=False, encoding="utf-8-sig")
print(f"지하철역 {len(sub_df)}건 로컬 저장 ")
upload_to_hdfs(sub_file)


# ==========================================
# 3. 행정동 영역(좌표) 데이터 
# ==========================================
print(" 행정동 영역 좌표 수집 ")
dong_df = get_seoul_data_all("TbgisAdstrdRelmW", 1000) 
dong_file = "dong_area.csv"
dong_df.to_csv(dong_file, index=False, encoding="utf-8-sig")
print(f"행정동 좌표 {len(dong_df)}건 로컬 저장")
upload_to_hdfs(dong_file)


# ==========================================
# 4. 시간대별 버스 승하차 데이터 (2025년 1년치)
# ==========================================
print("시간대별 버스 승하차 데이터 수집 ")
months_to_collect = [f"2025{str(m).zfill(2)}" for m in range(1, 13)]
all_bus_time_data = []

for month in months_to_collect:
    start_idx = 1
    while True:
        end_idx = start_idx + 999
        url = f"http://openapi.seoul.go.kr:8088/{API_KEY}/json/CardBusTimeNew/{start_idx}/{end_idx}/{month}"
        try:
            response = requests.get(url)
            data = response.json()
            if "CardBusTimeNew" in data:
                rows = data["CardBusTimeNew"]["row"]
                all_bus_time_data.extend(rows)
                if len(rows) < 1000:
                    break
                start_idx += 1000
            else:
                break
        except Exception:
            break
        time.sleep(0.5)

bus_time_df = pd.DataFrame(all_bus_time_data)
bus_time_file = "bus_time_data_2025.csv" # 파일명 덮어쓰기 방지!
bus_time_df.to_csv(bus_time_file, index=False, encoding="utf-8-sig")
print(f"시간대별 버스 데이터 {len(bus_time_df)}건 로컬 저장 ")
upload_to_hdfs(bus_time_file)


# ==========================================
# 5. 행정동 단위 생활인구 데이터 (2025년 1년치)
# ==========================================
print("행정동 단위 생활인구 수집 ")

start_date = datetime(2025, 1, 1)
days_to_collect = 365 
all_pop_data = []

for i in range(days_to_collect):
    target_date = start_date + timedelta(days=i)
    date_str = target_date.strftime("%Y%m%d")
    
    for start_idx in range(1, 12000, 1000):
        end_idx = start_idx + 999
        url = f"http://openapi.seoul.go.kr:8088/{API_KEY}/json/SPOP_LOCAL_RESD_DONG/{start_idx}/{end_idx}/{date_str}"
        
        try:
            response = requests.get(url)
            data = response.json()
            
            if "SPOP_LOCAL_RESD_DONG" in data:
                rows = data["SPOP_LOCAL_RESD_DONG"]["row"]
                all_pop_data.extend(rows)
                
                if len(rows) < 1000:
                    break
            else:
                break
                
        except Exception as e:
            pass 
            
        time.sleep(0.1) 
        
    if (i + 1) % 10 == 0:
        print(f"  >> {date_str}까지 수집 ... (현재 누적: {len(all_pop_data):,}건)")

pop_df = pd.DataFrame(all_pop_data)
pop_file = "seoul_living_pop_dong_2025.csv"
pop_df.to_csv(pop_file, index=False, encoding="utf-8-sig")
print(f"생활인구 {len(pop_df):,}건 로컬 저장")
upload_to_hdfs(pop_file)

print("\n 모든 데이터 수집 완료")
