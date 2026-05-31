import pandas as pd
import plotly.express as px

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

fig = px.scatter_map(
    df,
    lat="LAT",
    lon="LON",
    hover_name="STOPS_NM",
    hover_data=["ADSTRD_NM", "total_living_pop", "distance_km", "daily_total_on"],
    size="daily_total_on",
    color="distance_km",
    color_continuous_scale=px.colors.sequential.Inferno,
    size_max=35,
    opacity=0.9,
    zoom=10.5,
    center={"lat": 37.5665, "lon": 126.9780},
    title="서울시 대중교통 사각지대 핵심 정류장 (Top 100)"
)

fig.update_layout(map_style="carto-positron")
fig.show()
