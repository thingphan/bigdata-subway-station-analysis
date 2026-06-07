import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

df = pd.read_csv("final_top100_report.csv")
df = df.rename(columns={
    'final_transit_blind_spot.stops_nm': 'STOPS_NM',
    'final_transit_blind_spot.adstrd_nm': 'ADSTRD_NM',
    'final_transit_blind_spot.lon': 'LON',
    'final_transit_blind_spot.lat': 'LAT',
    'final_transit_blind_spot.total_living_pop': 'total_living_pop',
    'final_transit_blind_spot.distance_km': 'distance_km',
    'final_transit_blind_spot.daily_total_on': 'daily_total_on'
})

df = df.dropna(subset=['LAT', 'LON', 'daily_total_on', 'distance_km'])

top_n = 15
df_top = df.nlargest(top_n, 'daily_total_on')

fig = make_subplots(
    rows=1, cols=2,
    column_widths=[0.7, 0.3],
    specs=[[{"type": "scattermap"}, {"type": "table"}]],
    horizontal_spacing=0.02
)

fig_map = px.scatter_map(
    df,
    lat="LAT",
    lon="LON",
    hover_name="STOPS_NM",
    hover_data={
        "ADSTRD_NM": True,
        "total_living_pop": True,
        "distance_km": ':.2f',
        "daily_total_on": ':.0f',
        "LAT": False,
        "LON": False
    },
    size="daily_total_on",
    color="distance_km",
    color_continuous_scale=px.colors.sequential.Inferno,
    size_max=35,
    opacity=0.9
)

for trace in fig_map.data:
    fig.add_trace(trace, row=1, col=1)

fig.add_trace(
    go.Table(
        header=dict(
            values=["<b>정류장명</b>", "<b>행정동</b>", "<b>승하차 인원</b>", "<b>거리(km)</b>"],
            fill_color="lightgray",
            align="center",
            font=dict(size=12, color="black")
        ),
        cells=dict(
            values=[
                df_top["STOPS_NM"],
                df_top["ADSTRD_NM"],
                df_top["daily_total_on"].round(0).astype(int),
                df_top["distance_km"].round(2)
            ],
            fill_color="white",
            align="center",
            font=dict(size=11, color="black")
        )
    ),
    row=1, col=2
)

fig.update_layout(
    map_style="carto-positron",
    map_zoom=10.5,
    map_center={"lat": 37.5665, "lon": 126.9780},
    title_text=f"서울시 대중교통 사각지대 핵심 정류장 (Top 100) & 상위 {top_n}개 목록",
    title_font_size=20,
    margin={"r": 10, "t": 60, "l": 10, "b": 10},
    height=700
)

fig.show()
