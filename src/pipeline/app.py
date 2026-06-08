import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 기본 설정 (layout을 centered로 변경하여 너비 최적화)
st.set_page_config(page_title="서울시 지하철 접근성 소외지역 분석", layout="centered")
st.title("서울시 지하철 접근성 소외지역 분석 대시보드")

# 2. 데이터 로드 및 전처리
@st.cache(allow_output_mutation=True)
def load_data():
    df = pd.read_csv("final_top100_report.csv")
    df.columns = [c.split('.')[-1] for c in df.columns]
    df = df.rename(columns={'stops_nm': 'STOPS_NM', 'adstrd_nm': 'ADSTRD_NM', 'lon': 'LON', 'lat': 'LAT'})
    df = df.dropna(subset=['LAT', 'LON', 'daily_total_on', 'distance_km', 'robust_score'])
    return df

df_original = load_data()
df = df_original.copy() 

# ==========================================
# 사이드바 (컨트롤 패널)
# ==========================================

st.sidebar.header("교통 취약 지수 가중치 설정")
st.sidebar.caption("각 지표의 중요도를 조절하면 비율에 맞게 자동 환산되어 순위가 재계산됩니다.")

# 가중치 입력
raw_w_pop = st.sidebar.slider("생활인구 중요도 (잠재수요)", 0.0, 1.0, 0.3, step=0.1)
raw_w_on = st.sidebar.slider("승하차 인원 중요도 (실수요)", 0.0, 1.0, 0.4, step=0.1)
raw_w_dist = st.sidebar.slider("지하철역 거리 중요도 (접근성)", 0.0, 1.0, 0.3, step=0.1)

# 가중치 합 자동 보정 로직 (Normalization)
total_w = raw_w_pop + raw_w_on + raw_w_dist
if total_w > 0:
    w_pop, w_on, w_dist = raw_w_pop / total_w, raw_w_on / total_w, raw_w_dist / total_w
else:
    w_pop, w_on, w_dist = 0.333, 0.333, 0.333

# 적용된 실제 비율(%)을 사용자에게 명확히 고지
st.sidebar.info(
    f"**실제 적용 반영비율**\n\n"
    f"- 생활인구: **{w_pop*100:.1f}%**\n\n"
    f"- 승하차 수요: **{w_on*100:.1f}%**\n\n"
    f"- 물리적 거리: **{w_dist*100:.1f}%**"
)

# 실시간 동적 점수 계산
df['dynamic_score'] = (w_pop * df['p_norm']) + (w_on * df['b_norm']) + (w_dist * df['d_norm'])

st.sidebar.markdown("---")
st.sidebar.header("탐색 조건 설정")

# 다중 행정동 선택
selected_dongs = st.sidebar.multiselect("특정 행정동 집중 탐색", options=sorted(df['ADSTRD_NM'].unique()))

# 조건에 따른 데이터 필터링 및 정렬
if selected_dongs:
    filtered_df = df[df['ADSTRD_NM'].isin(selected_dongs)]
else:
    filtered_df = df

filtered_df = filtered_df.sort_values('dynamic_score', ascending=False)

# C. 데이터 내보내기 (다운로드)
st.sidebar.markdown("---")
st.sidebar.subheader("결과 내보내기")
csv_data = filtered_df.to_csv(index=False).encode('utf-8-sig')
st.sidebar.download_button(
    label="현재 Top 100 결과 다운로드 (CSV)",
    data=csv_data,
    file_name="simulated_transit_blind_spots.csv",
    mime="text/csv"
)

# ==========================================
# 메인 화면 (대시보드)
# ==========================================
st.subheader(f"도출된 소외지역 정류장 목록 ({len(filtered_df)}개)")

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
            "dynamic_score": "취약 지수 (
