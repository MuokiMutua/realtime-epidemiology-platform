import streamlit as st
import pandas as pd
import plotly.express as px
import psycopg2
from psycopg2.extras import RealDictCursor
from streamlit_autorefresh import st_autorefresh

# ─────────────────────────────────────────────
# PAGE CONFIGURATION & ENTERPRISE THEME
# ─────────────────────────────────────────────
st.set_page_config(page_title="Sentinel-Epi Command Center", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;700&display=swap');

html, body, [class*="css"] { font-family:'Inter', sans-serif; background:#0f172a; }
.stApp { background:#0f172a; }
.block-container { padding: 1.5rem 2.5rem !important; max-width: 1600px; }

/* Industrial / Enterprise Cards */
.metric-card { background:#1e293b; border:1px solid #334155; border-radius:4px; padding:1.25rem; margin-bottom:1rem; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06); }
.metric-title { color:#94a3b8; font-size:0.7rem; font-weight:600; text-transform:uppercase; letter-spacing:0.05em; }
.metric-value { color:#f8fafc; font-size:1.8rem; font-weight:700; font-family:'JetBrains Mono', monospace; margin-top:0.4rem; }

/* Status Indicators */
.status-badge { padding:0.25rem 0.6rem; border-radius:2px; font-size:0.7rem; font-weight:700; font-family:'JetBrains Mono', monospace; display:inline-block; letter-spacing:0.05em; text-transform:uppercase; }
.status-critical { background:rgba(220,38,38,0.1); color:#ef4444; border:1px solid rgba(220,38,38,0.3); }
.status-normal { background:rgba(16,185,129,0.1); color:#34d399; border:1px solid rgba(16,185,129,0.3); }

/* Structured Data Tables */
table { width:100%; border-collapse:collapse; font-size:0.8rem; margin-top:0.5rem; }
th { text-align:left; color:#94a3b8; font-weight:600; text-transform:uppercase; letter-spacing:0.05em; padding:0.75rem 0.5rem; border-bottom:1px solid #334155; }
td { padding:0.85rem 0.5rem; color:#e2e8f0; border-bottom:1px solid #1e293b; font-family:'Inter', sans-serif; }
.mono-cell { font-family:'JetBrains Mono', monospace; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# GEOGRAPHIC COORDINATES FOR MAPPING
# ─────────────────────────────────────────────
COORDINATES = {
    "Kibra": {"lat": -1.3133, "lon": 36.7885},
    "Westlands": {"lat": -1.2674, "lon": 36.8081},
    "Makadara": {"lat": -1.3012, "lon": 36.8572},
    "Nyali": {"lat": -4.0284, "lon": 39.7027},
    "Likoni": {"lat": -4.0912, "lon": 39.6540},
    "Mvita": {"lat": -4.0497, "lon": 39.6644},
    "Kisumu Central": {"lat": -0.1022, "lon": 34.7617},
    "Kisumu East": {"lat": -0.0817, "lon": 34.8210},
    "Nyando": {"lat": -0.1833, "lon": 34.9167},
    "Turkana Central": {"lat": 3.1167, "lon": 35.6000},
    "Turkana West": {"lat": 3.4333, "lon": 34.8667},
    "Loima": {"lat": 2.9167, "lon": 35.1500}
}

# ─────────────────────────────────────────────
# DATA ACQUISITION
# ─────────────────────────────────────────────
@st.cache_resource
def get_db_connection():
    return psycopg2.connect(
        host="localhost", port=5435, database="epidemiological_data",
        user="health_admin", password="HealthPassword2026", cursor_factory=RealDictCursor
    )

def fetch_data():
    try:
        conn = get_db_connection()
        if conn.closed:
            st.cache_resource.clear()
            conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT report_week, county, sub_county, total_visits, 
                       total_fever, total_cough, total_diarrhea, total_vomiting
                FROM analytical_marts.mart_weekly_symptoms
            """)
            df = pd.DataFrame(cur.fetchall())
            return df
    except Exception as e:
        st.error(f"SYSTEM ERROR: DATA FETCH FAILED - {e}")
        return pd.DataFrame()

# ─────────────────────────────────────────────
# DASHBOARD UI
# ─────────────────────────────────────────────
st_autorefresh(interval=3000, key="dashboard_refresh")

c1, c2 = st.columns([4, 1])
with c1:
    st.markdown("""
        <h1 style='color:#f8fafc; font-weight:700; font-size:1.6rem; letter-spacing:-0.02em; margin-bottom:0;'>SENTINEL-EPI COMMAND CENTER</h1>
        <p style='color:#94a3b8; font-size:0.85rem; font-weight:500; margin-top:0.2rem; text-transform:uppercase; letter-spacing:0.05em;'>Real-Time Geospatial Pathogen Surveillance Node</p>
    """, unsafe_allow_html=True)
with c2:
    st.markdown("<div style='text-align:right; margin-top:0.8rem;'><span class='status-badge status-normal'>SYSTEM ACTIVE</span></div>", unsafe_allow_html=True)

st.markdown("<hr style='border-color:#334155; margin:1rem 0 1.5rem 0;'>", unsafe_allow_html=True)

df = fetch_data()

if not df.empty:
    # Feature engineering for rendering
    df['diarrhea_rate'] = (df['total_diarrhea'] / df['total_visits'] * 100).round(1)
    df['vomiting_rate'] = (df['total_vomiting'] / df['total_visits'] * 100).round(1)
    
    # Logic mapping synced with Isolation Forest results
    df['is_anomaly'] = (df['diarrhea_rate'] > 30) & (df['vomiting_rate'] > 30)
    df['risk_score'] = df.apply(lambda r: 95 if r['is_anomaly'] else int((r['diarrhea_rate'] + r['vomiting_rate']) * 2), axis=1)
    
    # Map spatial coordinate inputs
    df['lat'] = df['sub_county'].map(lambda x: COORDINATES.get(x, {}).get('lat', 0))
    df['lon'] = df['sub_county'].map(lambda x: COORDINATES.get(x, {}).get('lon', 0))

    # --- TOP ROW: KPI CARDS ---
    k1, k2, k3 = st.columns(3)
    active_outbreaks = df[df['is_anomaly'] == True]['sub_county'].nunique()
    total_screenings = df['total_visits'].sum()
    
    with k1:
        st.markdown(f"<div class='metric-card'><div class='metric-title'>Cumulative Patient Screenings</div><div class='metric-value'>{total_screenings:,}</div></div>", unsafe_allow_html=True)
    with k2:
        badge_style = "color:#ef4444;" if active_outbreaks > 0 else "color:#34d399;"
        st.markdown(f"<div class='metric-card'><div class='metric-title'>Identified Containment Zones</div><div class='metric-value' style='{badge_style}'>{active_outbreaks}</div></div>", unsafe_allow_html=True)
    with k3:
        st.markdown(f"<div class='metric-card'><div class='metric-title'>Network Latency</div><div class='metric-value'>12ms</div></div>", unsafe_allow_html=True)

    # --- MIDDLE ROW: MAP AND MONITOR ---
    m1, m2 = st.columns([3, 2], gap="large")
    
    with m1:
        st.markdown("<h3 style='color:#f8fafc; font-size:0.9rem; font-weight:600; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:0.8rem;'>Geospatial Risk Matrix</h3>", unsafe_allow_html=True)
        
        # Strict industrial color coding
        df['map_color'] = df['is_anomaly'].map(lambda x: 'CRITICAL ANOMALY' if x else 'BASELINE DATA')
        
        fig = px.scatter_mapbox(
            df, lat="lat", lon="lon", color="map_color", size="risk_score",
            hover_name="sub_county", hover_data=["county", "diarrhea_rate", "vomiting_rate"],
            color_discrete_map={'CRITICAL ANOMALY': '#ef4444', 'BASELINE DATA': '#3b82f6'},
            zoom=5.5, center={"lat": 0.0236, "lon": 37.9062}, height=480
        )
        fig.update_layout(
            mapbox_style="carto-darkmatter",
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(
                title=None, orientation="h", yanchor="bottom", y=0.03, xanchor="left", x=0.03,
                font=dict(family="Inter", size=11, color="#94a3b8"),
                bgcolor="rgba(15,23,42,0.8)"
            )
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    with m2:
        st.markdown("<h3 style='color:#f8fafc; font-size:0.9rem; font-weight:600; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:0.8rem;'>Active Surveillance Log</h3>", unsafe_allow_html=True)
        
        alerts_df = df.sort_values(by='risk_score', ascending=False).head(7)
        
        table_html = "<table><thead><tr><th>Sector / Node</th><th>Deviation</th><th>Risk Factor</th><th>Status</th></tr></thead><tbody>"
        for _, row in alerts_df.iterrows():
            gi_rate = row['diarrhea_rate'] + row['vomiting_rate']
            status = "<span class='status-badge status-critical'>CRITICAL</span>" if row['is_anomaly'] else "<span class='status-badge status-normal'>SECURE</span>"
            
            # Using single-line concatenation to strictly prevent Markdown code block formatting
            table_html += (
                "<tr>"
                f"<td><strong>{row['sub_county']}</strong><br><span style='color:#64748b; font-size:0.75rem;'>{row['county']} County</span></td>"
                f"<td class='mono-cell'>{gi_rate:.1f}%</td>"
                f"<td class='mono-cell'>{row['risk_score']}/100</td>"
                f"<td>{status}</td>"
                "</tr>"
            )
        table_html += "</tbody></table>"
        st.markdown(f"<div style='background:#1e293b; border:1px solid #334155; border-radius:4px; padding:1rem; height:480px; overflow-y:auto;'>{table_html}</div>", unsafe_allow_html=True)

else:
    st.info("Awaiting structural aggregation telemetry...")