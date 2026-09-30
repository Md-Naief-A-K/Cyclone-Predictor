import os
import pandas as pd
import pydeck as pdk
import streamlit as st
from cyclone import data, model
from cyclone.gemini import ask_gemini

# Page Config with Dark Tactical Theme
st.set_page_config(page_title="CYCLONE OPS | Tactical Command", page_icon="🌀", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    div[data-testid="stMetricValue"] { font-size: 28px; font-weight: bold; color: #58a6ff; }
    </style>
""", unsafe_allow_html=True)

st.title("🌀 CYCLONE OPS: Infrastructure Vulnerability & Early Warning")
st.caption("Google Earth Engine Telemetry → Surge & Rainfall Analysis → Gemini Multimodal Advisory")

with st.sidebar:
    st.header("⚡ Command Controls")
    key = st.text_input(
        "Gemini API Key",
        value=os.environ.get("GEMINI_API_KEY", ""),
        type="password",
        help="Get your key at aistudio.google.com/apikey"
    )
    mdl = st.text_input("Model ID", "gemini-2.5-flash")
    lang = st.selectbox("Dispatch Language", ["Odia", "Bengali", "Hindi", "Telugu", "Tamil", "Burmese"])
    img = st.file_uploader("Satellite / Radar Overlay (Optional)", type=["png", "jpg", "jpeg", "webp"])

st.subheader("1 · Cyclone Track Trajectory Vector (Last Point = Landfall)")
default_track = pd.DataFrame({
    "lat": [14.0, 16.5, 18.5, 20.2],
    "lon": [88.5, 88.0, 87.2, 86.6],
    "kt": [80, 95, 105, 110]
})
df = st.data_editor(default_track, num_rows="dynamic", use_container_width=True)

if st.button("🚀 Run Tactical Assessment & Generate Advisory", type="primary"):
    if len(df) < 2:
        st.error("At least 2 trajectory points required.")
        st.stop()

    try:
        track = df.dropna().to_dict("records")
        lf = track[-1]

        with st.status("Executing Analytics Pipeline...", expanded=True) as status:
            status.write("📡 Fetching meteorological telemetry...")
            rain72, gust = data.get_weather(lf["lat"], lf["lon"])

            status.write("🏥 Mapping critical infrastructure assets...")
            assets = data.get_assets(lf["lat"], lf["lon"])

            status.write("🌊 Running hydrodynamic storm surge simulation...")
            surge = model.analyse(track, assets, rain72)

            # DEMO / MOCK FALLBACK MODE
            if not key or key.strip().lower() == "demo":
                status.write("🤖 Generating AI plan (Demo Simulation Mode)...")
                plan = {
                    "severity": "CRITICAL",
                    "headline": "Category 3 Cyclone landfall imminent within 12 hours. High surge threat to critical coastal assets.",
                    "evacuation": [
                        {"zone": "Sector Alpha (0-5km Shoreline)", "action": "Mandatory immediate evacuation to elevated shelters", "timing": "0-4 Hours"},
                        {"zone": "Sector Bravo (Low-lying inland)", "action": "Advisory evacuation for vulnerable housing", "timing": "4-8 Hours"}
                    ],
                    "insurance": {
                        "trigger": f"Storm surge estimate of {surge:.1f}m breaches the 2.0m parametric payout threshold.",
                        "rationale": "Automated liquidity release dispatched to municipal emergency fund."
                    },
                    "hardening": [
                        {"priority": "P0", "asset": "Substation Alpha (Grid)", "action": "Deploy perimeter flood barriers and initiate graceful transformer grid disconnect."},
                        {"priority": "P1", "asset": "District General Hospital", "action": "Transfer emergency power load to roof-mounted backup diesel generators."}
                    ],
                    "advisory_en": "EMERGENCY ADVISORY: Severe Tropical Cyclone heading towards landfall. Seek immediate shelter inland. Do not cross flooded roadways.",
                    "advisory_local": f"জরুরী সতর্কতা: উপকূলে সাইক্লোন আছড়ে পড়ার সম্ভাবনা। অবিলম্বে নিরাপদ আশ্রয়ে চলে যান। ({lang} Dispatch)"
                }
            else:
                status.write("🤖 Dispatching multimodal payload to Gemini...")
                ctx = {
                    "track": track,
                    "landfall": lf,
                    "surgeM": round(surge, 2),
                    "rain72hMm": round(rain72),
                    "maxGustKmh": gust,
                    "topAssets": [{k: a[k] for k in ("name", "type", "elev", "depth", "wind", "dTrack", "risk")} for a in assets]
                }
                plan = ask_gemini(
                    key, mdl, ctx, lang,
                    img.getvalue() if img else None,
                    img.type if img else "image/png"
                )
            status.update(label="Assessment Complete!", state="complete")

        st.session_state["res"] = dict(track=track, assets=assets, surge=surge, rain=rain72, gust=gust, plan=plan, lang=lang)

    except Exception as e:
        st.error(f"Execution Error: {str(e)}")

r = st.session_state.get("res")
if r:
    a = pd.DataFrame(r["assets"])
    t = pd.DataFrame(r["track"])

    # Metrics Display
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Peak Wind Speed", f"{max(p['kt'] for p in r['track'])} kt")
    c2.metric("Est. Storm Surge", f"{r['surge']:.1f} m")
    c3.metric("72h Rainfall", f"{r['rain']:.0f} mm")
    c4.metric("Max Gust", f"{r['gust']:.0f} km/h")
    c5.metric("HIGH Risk Assets", f"{(a.risk == 'HIGH').sum()}/{len(a)}")

    # High-Tech Map Render
    st.subheader("2 · Satellite & Infrastructure Threat Map")
    colors = {"HIGH": [239, 68, 68, 230], "MED": [245, 158, 11, 230], "LOW": [34, 197, 94, 230]}
    a["color"] = a.risk.map(colors)

    st.pydeck_chart(pdk.Deck(
        map_style=None,
        initial_view_state=pdk.ViewState(latitude=t.lat.mean(), longitude=t.lon.mean(), zoom=6.5, pitch=30),
        layers=[
            pdk.Layer("TileLayer", data="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", min_zoom=0, max_zoom=19),
            pdk.Layer("PathLayer", [{"path": t[["lon", "lat"]].values.tolist()}], get_path="path", get_color=[255, 215, 0], width_min_pixels=4),
            pdk.Layer("ScatterplotLayer", t, get_position=["lon", "lat"], get_radius=10000, get_fill_color=[255, 0, 0, 200]),
            pdk.Layer("ScatterplotLayer", a, get_position=["lon", "lat"], get_radius=2500, get_fill_color="color", pickable=True),
        ],
        tooltip={"text": "{name}\nType: {type}\nElevation: {elev}m | Flood Depth: {depth}m\nRisk Level: {risk}"}
    ))

    # Gemini Plan Display
    p = r["plan"]
    st.subheader(f" Gemini Tactical Plan — Threat Level: {p.get('severity', 'HIGH')}")
    st.info(p.get("headline", ""))

    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown("###  Evacuation Zones")
        for e in p.get("evacuation", []):
            st.markdown(f"- **{e['zone']}**: {e['action']} _({e['timing']})_")

        st.markdown("###  Parametric Insurance Trigger")
        ins = p.get("insurance", {})
        st.write(f"**Trigger:** {ins.get('trigger', 'N/A')}")
        st.caption(ins.get('rationale', ''))

    with col_right:
        st.markdown("### Infrastructure Hardening Directives")
        for h in p.get("hardening", []):
            st.markdown(f"- `{h['priority']}` **{h['asset']}**: {h['action']}")

    st.subheader(" Early Warning Broadcast Dispatches")
    e1, e2 = st.columns(2)
    e1.text_area("Official English Dispatch", p.get("advisory_en", ""), height=180)
    e2.text_area(f"Local Dispatch ({r['lang']})", p.get("advisory_local", ""), height=180)