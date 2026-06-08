import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 기본 설정
st.set_page_config(page_title="서울시 대중교통 사각지대 분석", layout="wide")
st.title("서울시 대중교통 사각지대 분석 대시보드")

# 2. 데이터 로드 및 전처리
@st.cache
def load_data():
    df = pd.read_csv("final_top100_report.csv")
    
    # 'rankeddata.stops_nm' 등의 접두사 제거
    df.columns = [c.split('.')[-1] for c in df.columns]
    
    # 시각화 및 UI를 위한 컬럼명 통일
    df = df.rename(columns={
        'stops_nm': 'STOPS_NM', 
        'adstrd_nm': 'ADSTRD_NM', 
        'lon': 'LON', 
        'lat': 'LAT'
    })
    
    # 필수 데이터 결측치 제거
    df = df.dropna(subset=['LAT', 'LON', 'daily_total_on', 'distance_km', 'robust_score'])
    return df

df = load_data()

# ==========================================
# 사이드바
# ==========================================

# A. 가중치 동적 조절 (시뮬레이터)
st.sidebar.header("교통 취약 지수 가중치 시뮬레이션")
st.sidebar.caption("각 지표의 중요도를 조절하여 새로운 소외지역을 탐색하세요.")

w_pop = st.sidebar.slider("생활인구 가중치 (잠재수요)", 0.0, 1.0, 0.3, step=0.1)
w_on = st.sidebar.slider("승하차 인원 가중치 (실수요)", 0.0, 1.0, 0.4, step=0.1)
w_dist = st.sidebar.slider("지하철역 거리 가중치", 0.0, 1.0, 0.3, step=0.1)

# 가중치 합이 1이 되도록 자동 보정
total_w = w_pop + w_on + w_dist
if total_w > 0:
    w_pop, w_on, w_dist = w_pop / total_w, w_on / total_w, w_dist / total_w
else:
    w_pop, w_on, w_dist = 0.33, 0.33, 0.33

# 실시간 동적 점수 계산 (p_norm, b_norm, d_norm 활용)
df['dynamic_score'] = (w_pop * df['p_norm']) + (w_on * df['b_norm']) + (w_dist * df['d_norm'])

# B. 탐색 조건 필터링
st.sidebar.markdown("---")
st.sidebar.header("탐색 조건 설정")

# 다중 행정동 선택
selected_dongs = st.sidebar.multiselect("관심 행정동 선택", options=sorted(df['ADSTRD_NM'].unique()))

# 최소 기준 슬라이더
min_on = st.sidebar.slider("최소 승하차 인원", min_value=0, max_value=int(df['daily_total_on'].max()), value=10000)
min_dist = st.sidebar.slider("최소 지하철역 거리(km)", min_value=1.0, max_value=float(df['distance_km'].max()), value=1.0)

# 조건에 따른 데이터 필터링 및 정렬
filtered_df = df[(df['daily_total_on'] >= min_on) & (df['distance_km'] >= min_dist)]
if selected_dongs:
    filtered_df = filtered_df[filtered_df['ADSTRD_NM'].isin(selected_dongs)]

filtered_df = filtered_df.sort_values('dynamic_score', ascending=False)

# C. 데이터 내보내기 (다운로드)
st.sidebar.markdown("---")
st.sidebar.subheader("시뮬레이션 결과 내보내기")
csv_data = filtered_df.to_csv(index=False).encode('utf-8-sig')
st.sidebar.download_button(
    label="결과 다운로드 (CSV)",
    data=csv_data,
    file_name="simulated_transit_blind_spots.csv",
    mime="text/csv"
)

# ==========================================
# 메인 화면 (대시보드)
# ==========================================
st.subheader(f"조건에 맞는 소외지역 정류장 ({len(filtered_df)}개)")

# 7:3 비율로 화면 분할
col1, col2 = st.columns([7, 3])

with col1:
    if len(filtered_df) > 0:
        fig_map = px.scatter_mapbox(
            filtered_df, lat="LAT", lon="LON", hover_name="STOPS_NM",
            hover_data={
                "ADSTRD_NM": True, "total_living_pop": True, "distance_km": ':.2f',
                "daily_total_on": ':.0f', "dynamic_score": ':.3f',
                "LAT": False, "LON": False, "p_norm": False, "b_norm": False, "d_norm": False, "robust_score": False
            },
            size="daily_total_on", color="dynamic_score",
            color_continuous_scale=px.colors.sequential.YlOrRd, size_max=35, opacity=0.9,
            labels={
                "dynamic_score": "시뮬레이션 취약 지수", "daily_total_on": "승하차 인원", 
                "distance_km": "지하철역 거리(km)", "total_living_pop": "생활인구", "ADSTRD_NM": "행정동"
            }
        )
        fig_map.update_layout(
            mapbox_style="carto-positron",
            mapbox_zoom=10.5,
            mapbox_center={"lat": 37.5665, "lon": 126.9780},
            margin={"r":0, "t":0, "l":0, "b":0}
        )
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.warning("조건에 맞는 정류장이 없습니다. 좌측 패널에서 조건을 완화해 보세요.")

with col2:
    st.dataframe(
        filtered_df[['STOPS_NM', 'ADSTRD_NM', 'daily_total_on', 'dynamic_score']].head(15)
    )
