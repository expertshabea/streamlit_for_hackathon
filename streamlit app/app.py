import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import json

st.set_page_config(
    page_title="FoodFlow Analytics",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #0b1020;
}

.block-container {
    padding: 1.8rem 2.5rem 3rem;
    max-width: 1500px;
}

.hero {
    padding: 28px 32px;
    border-radius: 24px;
    background: linear-gradient(135deg, #151d38 0%, #202b52 50%, #17213e 100%);
    border: 1px solid rgba(255,255,255,.08);
    margin-bottom: 22px;
    box-shadow: 0 15px 50px rgba(0,0,0,.25);
}

.hero h1 {
    margin: 0;
    font-size: 42px;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -1.5px;
}

.hero p {
    margin: 8px 0 0;
    color: #aeb9d5;
    font-size: 16px;
}

.badge {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 999px;
    background: rgba(99,102,241,.18);
    color: #a5b4fc;
    font-size: 12px;
    font-weight: 700;
    margin-bottom: 12px;
}

.kpi {
    padding: 20px;
    border-radius: 18px;
    background: #141b31;
    border: 1px solid rgba(255,255,255,.07);
    min-height: 125px;
}

.kpi-label {
    color: #8e9ab7;
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 8px;
}

.kpi-value {
    color: #ffffff;
    font-size: 29px;
    font-weight: 800;
}

.kpi-sub {
    color: #667390;
    font-size: 12px;
    margin-top: 5px;
}

.section {
    color: #ffffff;
    font-size: 23px;
    font-weight: 750;
    margin: 30px 0 14px;
}

.answer {
    padding: 20px;
    border-radius: 18px;
    background: linear-gradient(135deg, #151d38, #11172a);
    border: 1px solid rgba(99,102,241,.22);
    min-height: 150px;
}

.answer-label {
    color: #8fa0c5;
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.answer h3 {
    color: #ffffff;
    margin: 8px 0;
    font-size: 21px;
}

.answer p {
    color: #aeb9d5;
    margin: 0;
    line-height: 1.55;
}

.insight {
    padding: 18px 20px;
    border-left: 4px solid #818cf8;
    border-radius: 12px;
    background: #141b31;
    margin-bottom: 12px;
    color: #d9def0;
    line-height: 1.55;
}

div[data-testid="stMetric"] {
    background: #141b31;
    border: 1px solid rgba(255,255,255,.07);
    padding: 18px;
    border-radius: 18px;
}

div[data-testid="stMetricValue"] {
    color: white;
}

div[data-testid="stMetricLabel"] {
    color: #8e9ab7;
}

[data-testid="stSidebar"] {
    background: #0e1427;
}

[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] label {
    color: #dce3f7 !important;
}

.stButton > button {
    border-radius: 12px;
    font-weight: 700;
}

footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <div class="badge">AI & DS • FOOD DELIVERY ANALYTICS</div>
    <h1>🍔 FoodFlow Analytics</h1>
    <p>Turn delivery data into decisions — traffic, distance, weather and operational performance.</p>
</div>
""", unsafe_allow_html=True)

@st.cache_data
def load_data(file):
    df = pd.read_csv(file)
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"[^a-z0-9]+", "_", regex=True)
        .str.strip("_")
    )
    return df

with st.sidebar:
    st.markdown("## 🍔 FoodFlow")
    st.caption("Delivery Operations Dashboard")
    uploaded = st.file_uploader("Upload your CSV", type=["csv"])

    if uploaded is None:
        st.info("Upload the hackathon CSV to start the dashboard.")
        st.stop()

df = load_data(uploaded)

required = [
    "time_taken_min", "distance_km", "delivery_person_age",
    "delivery_person_ratings", "weather_conditions",
    "road_traffic_density"
]

missing_required = [c for c in required if c not in df.columns]
if missing_required:
    st.error(f"Missing required columns: {', '.join(missing_required)}")
    st.stop()

for col in [
    "delivery_person_age", "delivery_person_ratings",
    "vehicle_condition", "multiple_deliveries",
    "time_taken_min", "distance_km"
]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

duplicate_count = int(df.duplicated().sum())
df = df.drop_duplicates().copy()

invalid_age = (df["delivery_person_age"] < 15) | (df["delivery_person_age"] > 80)
invalid_rating = (df["delivery_person_ratings"] < 0) | (df["delivery_person_ratings"] > 5)
invalid_time = df["time_taken_min"] <= 0
invalid_distance = df["distance_km"] < 0

df.loc[invalid_age, "delivery_person_age"] = np.nan
df.loc[invalid_rating, "delivery_person_ratings"] = np.nan
df.loc[invalid_time, "time_taken_min"] = np.nan
df.loc[invalid_distance, "distance_km"] = np.nan

# Delivery speed is derived from distance and delivery time.
df["delivery_speed"] = df["distance_km"] / (df["time_taken_min"] / 60)

with st.sidebar:
    st.markdown("### Filters")

    cities = sorted(df["city"].dropna().unique()) if "city" in df.columns else []
    city_choice = st.multiselect("City", cities, default=cities)

    traffic_values = sorted(df["road_traffic_density"].dropna().unique())
    traffic_choice = st.multiselect(
        "Traffic",
        traffic_values,
        default=traffic_values
    )

    weather_values = sorted(df["weather_conditions"].dropna().unique())
    weather_choice = st.multiselect(
        "Weather",
        weather_values,
        default=weather_values
    )

filtered = df.copy()

if "city" in df.columns and city_choice:
    filtered = filtered[filtered["city"].isin(city_choice)]

if traffic_choice:
    filtered = filtered[filtered["road_traffic_density"].isin(traffic_choice)]

if weather_choice:
    filtered = filtered[filtered["weather_conditions"].isin(weather_choice)]

if len(filtered) == 0:
    st.warning("No deliveries match the selected filters.")
    st.stop()

total = len(filtered)
avg_time = filtered["time_taken_min"].mean()
avg_distance = filtered["distance_km"].mean()
avg_speed = filtered["delivery_speed"].mean()
avg_rating = filtered["delivery_person_ratings"].mean()

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="kpi">
        <div class="kpi-label">TOTAL DELIVERIES</div>
        <div class="kpi-value">{total:,.0f}</div>
        <div class="kpi-sub">Filtered records</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="kpi">
        <div class="kpi-label">AVG DELIVERY TIME</div>
        <div class="kpi-value">{avg_time:.2f} min</div>
        <div class="kpi-sub">Overall performance</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="kpi">
        <div class="kpi-label">AVG DISTANCE</div>
        <div class="kpi-value">{avg_distance:.2f} km</div>
        <div class="kpi-sub">Delivery distance</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="kpi">
        <div class="kpi-label">AVG SPEED</div>
        <div class="kpi-value">{avg_speed:.2f} km/h</div>
        <div class="kpi-sub">Derived from distance/time</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="section">🏆 Competition Answers</div>', unsafe_allow_html=True)

traffic_avg = (
    filtered.dropna(subset=["road_traffic_density", "time_taken_min"])
    .groupby("road_traffic_density")["time_taken_min"]
    .mean()
    .sort_values(ascending=False)
)

q1_condition = traffic_avg.index[0]
q1_time = traffic_avg.iloc[0]

distance_df = filtered[["distance_km", "time_taken_min"]].dropna().copy()
correlation = distance_df["distance_km"].corr(distance_df["time_taken_min"])

if len(distance_df) >= 4:
    distance_df["distance_group"] = pd.qcut(
        distance_df["distance_km"], q=4, duplicates="drop"
    )
    distance_groups = distance_df.groupby(
        "distance_group", observed=True
    )["time_taken_min"].mean()
    shortest_time = distance_groups.iloc[0]
    longest_time = distance_groups.iloc[-1]
else:
    shortest_time = np.nan
    longest_time = np.nan

combined_avg = (
    filtered.dropna(subset=[
        "weather_conditions",
        "road_traffic_density",
        "time_taken_min"
    ])
    .groupby(["weather_conditions", "road_traffic_density"])["time_taken_min"]
    .mean()
    .sort_values(ascending=False)
)

q3_weather, q3_traffic = combined_avg.index[0]
q3_time = combined_avg.iloc[0]

a1, a2, a3 = st.columns(3)

with a1:
    st.markdown(f"""
    <div class="answer">
        <div class="answer-label">Q1 • Traffic Impact</div>
        <h3>🚦 {q1_condition}</h3>
        <p>Highest average delivery time: <b>{q1_time:.2f} minutes</b>.</p>
    </div>
    """, unsafe_allow_html=True)

with a2:
    st.markdown(f"""
    <div class="answer">
        <div class="answer-label">Q2 • Distance Impact</div>
        <h3>📍 Correlation {correlation:.3f}</h3>
        <p>Longest-distance deliveries average <b>{longest_time:.2f} min</b> vs <b>{shortest_time:.2f} min</b> for the shortest group.</p>
    </div>
    """, unsafe_allow_html=True)

with a3:
    st.markdown(f"""
    <div class="answer">
        <div class="answer-label">Q3 • Combined Conditions</div>
        <h3>🌫️ {q3_weather} + {q3_traffic}</h3>
        <p>Highest average delivery time: <b>{q3_time:.2f} minutes</b>.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="section">📊 Performance Analytics</div>', unsafe_allow_html=True)

left, right = st.columns(2)

with left:
    traffic_plot = traffic_avg.reset_index()
    traffic_plot.columns = ["Traffic", "Average Delivery Time"]
    fig = px.bar(
        traffic_plot,
        x="Traffic",
        y="Average Delivery Time",
        title="Average Delivery Time by Traffic",
        text_auto=".2f"
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20,r=20,t=60,b=20),
        yaxis_title="Minutes"
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    sample = distance_df
    if len(sample) > 12000:
        sample = sample.sample(12000, random_state=42)

    fig2 = px.scatter(
        sample,
        x="distance_km",
        y="time_taken_min",
        title="Delivery Distance vs Delivery Time",
        opacity=0.45,
        trendline="ols"
    )
    fig2.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20,r=20,t=60,b=20),
        xaxis_title="Distance (km)",
        yaxis_title="Delivery Time (minutes)"
    )
    st.plotly_chart(fig2, use_container_width=True)

st.markdown('<div class="section">🌦️ Weather × Traffic</div>', unsafe_allow_html=True)

heatmap = (
    filtered.dropna(subset=[
        "weather_conditions",
        "road_traffic_density",
        "time_taken_min"
    ])
    .pivot_table(
        index="weather_conditions",
        columns="road_traffic_density",
        values="time_taken_min",
        aggfunc="mean"
    )
)

fig3 = px.imshow(
    heatmap,
    text_auto=".2f",
    aspect="auto",
    title="Average Delivery Time by Weather and Traffic"
)
fig3.update_layout(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=20,r=20,t=60,b=20)
)
st.plotly_chart(fig3, use_container_width=True)

st.markdown('<div class="section">💡 Business Insights</div>', unsafe_allow_html=True)

traffic_best = traffic_avg.iloc[-1]
traffic_difference = q1_time - traffic_best
distance_difference = longest_time - shortest_time

insights = [
    f"Traffic is a major delivery-time factor. {q1_condition} traffic has the highest average delivery time at {q1_time:.2f} minutes, {traffic_difference:.2f} minutes above the lowest-traffic condition.",
    f"Distance affects delivery time. The longest-distance group averages {longest_time:.2f} minutes compared with {shortest_time:.2f} minutes for the shortest-distance group, a difference of {distance_difference:.2f} minutes.",
    f"The most challenging combined condition is {q3_weather} weather with {q3_traffic} traffic, producing an average delivery time of {q3_time:.2f} minutes."
]

for i, insight in enumerate(insights, 1):
    st.markdown(
        f'<div class="insight"><b>0{i}</b>&nbsp;&nbsp; {insight}</div>',
        unsafe_allow_html=True
    )

st.markdown('<div class="section">🤖 AI Business Explanation</div>', unsafe_allow_html=True)

ai_findings = {
    "total_deliveries": int(total),
    "average_delivery_time_min": round(float(avg_time), 2),
    "average_distance_km": round(float(avg_distance), 2),
    "average_delivery_speed_kmh": round(float(avg_speed), 2),
    "average_rating": round(float(avg_rating), 2),
    "q1_traffic_condition": str(q1_condition),
    "q1_average_time_min": round(float(q1_time), 2),
    "q2_correlation": round(float(correlation), 3),
    "q2_shortest_group_time_min": round(float(shortest_time), 2),
    "q2_longest_group_time_min": round(float(longest_time), 2),
    "q3_weather": str(q3_weather),
    "q3_traffic": str(q3_traffic),
    "q3_average_time_min": round(float(q3_time), 2)
}

with st.expander("Generate Gemini explanation", expanded=False):
    gemini_key = st.text_input(
        "Gemini API key",
        value=os.getenv("GEMINI_API_KEY", ""),
        type="password"
    )

    if st.button("✨ Generate AI Explanation"):
        if not gemini_key:
            st.warning("Enter a Gemini API key first.")
        else:
            try:
                from google import genai
                client = genai.Client(api_key=gemini_key)

                prompt = f"""
You are a food-delivery business analyst.

Python and Pandas have already performed the primary analysis.
Do not calculate new statistics and do not invent numbers.

Explain the following calculated findings in clear business language.
Give a concise executive summary and three practical recommendations.

Calculated findings:
{json.dumps(ai_findings, indent=2)}
"""

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )

                st.success("AI explanation generated.")
                st.markdown(response.text)

            except Exception as e:
                st.error(f"Gemini request failed: {e}")

st.markdown('<div class="section">🔎 Data Explorer</div>', unsafe_allow_html=True)

st.caption(f"Showing {len(filtered):,} filtered records.")
st.dataframe(filtered, use_container_width=True, height=420)

csv = filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Download Filtered Data",
    csv,
    "filtered_food_delivery_data.csv",
    "text/csv"
)

st.markdown("""
<div style="text-align:center;color:#596681;padding:30px 0 5px;">
FoodFlow Analytics • Python + Pandas + Streamlit + Gemini
</div>
""", unsafe_allow_html=True)
