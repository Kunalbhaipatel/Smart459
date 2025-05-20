import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
st.set_page_config(page_title="Shaker Health Dashboard", layout="wide")
# Google-style CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500&display=swap');
    html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif;
        background-color: #f5f5f5;
    }
    .main {
        background-color: #ffffff;
        padding: 1rem 2rem;
        border-radius: 8px;
        margin: 2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    h1, h2, h3 {
        color: #202124;
        font-weight: 500;
    }
    .stButton>button {
        background-color: #4285F4;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 0.5rem 1rem;
    }
    .stSlider>div>div {
        background-color: #e8f0fe !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        background-color: #f1f3f4;
        border-radius: 8px;
        padding: 0.5rem;
    }
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)
# Sidebar Branding
try:
    st.sidebar.image("assets/Prodigy_IQ_logo.png", width=200)
except:
    st.sidebar.warning("⚠️ Logo failed to load.")
st.title("🛠️ Real-Time Shaker Monitoring Dashboard")
        shaker_col = 'SHAKER #3 (PERCENT)'
        shaker_avg = df[shaker_col].mean()
        shaker_min = df[shaker_col].min()
        shaker_max = df[shaker_col].max()
        screen_col = 'Screen Utilization (%)'
        screen_avg = df[screen_col].mean() if screen_col in df.columns else 0
        screen_min = df[screen_col].min() if screen_col in df.columns else 0
        screen_max = df[screen_col].max() if screen_col in df.columns else 0
        colA, colB, colC = st.columns(3)
        colA.metric("🛢️ Depth Drilled (ft)", f"{total_depth:,.0f}")
        colB.metric("🔄 Shaker Load", f"{shaker_avg:.1f}% (avg)", f"{shaker_min:.1f}–{shaker_max:.1f}%")
        colC.metric("📉 Screen Utilization", f"{screen_avg:.1f}% (avg)", f"{screen_min:.1f}–{screen_max:.1f}%")
    except Exception as e:
        st.warning(f"Summary stats unavailable: {e}")
# Inputs
SCREEN_MESH_CAPACITY = {"API 100": 250, "API 140": 200, "API 170": 160, "API 200": 120}
df_mesh_type = st.sidebar.selectbox("Select Screen Mesh Type", list(SCREEN_MESH_CAPACITY.keys()))
mesh_capacity = SCREEN_MESH_CAPACITY[df_mesh_type]
util_threshold = st.sidebar.slider("Utilization Threshold (%)", 50, 100, 80)
@st.cache_data(show_spinner=True)
def load_data(uploaded_file):
    return pd.read_csv(uploaded_file, low_memory=False)
uploaded_file = st.file_uploader("📤 Upload Shaker CSV Data", type=["csv"])
if uploaded_file:
    df = load_data(uploaded_file)

tabs = st.tabs(["📊 Overview", "📈 Charts", "🧪 Diagnostics", "📋 Raw Data"])

# 📊 Overview Tab
with tabs[0]:
    st.markdown("### Summary + KPIs + Advisor")
    with st.expander("📌 Summary: Drilling & Shaker Overview", expanded=True):
        try:
            depth_col = 'Bit Depth (feet)' if 'Bit Depth (feet)' in df.columns else 'Hole Depth (feet)'
            total_depth = df[depth_col].max()
            shaker_avg = df['SHAKER #3 (PERCENT)'].mean()
            shaker_min = df['SHAKER #3 (PERCENT)'].min()
            shaker_max = df['SHAKER #3 (PERCENT)'].max()
            screen_avg = df['Screen Utilization (%)'].mean() if 'Screen Utilization (%)' in df.columns else 0
            screen_min = df['Screen Utilization (%)'].min() if 'Screen Utilization (%)' in df.columns else 0
            screen_max = df['Screen Utilization (%)'].max() if 'Screen Utilization (%)' in df.columns else 0

            colA, colB, colC = st.columns(3)
            colA.metric("🛢️ Depth Drilled (ft)", f"{total_depth:,.0f}")
            colB.metric("🔄 Shaker Load", f"{shaker_avg:.1f}% (avg)", f"{shaker_min:.1f}–{shaker_max:.1f}%")
            colC.metric("📉 Screen Utilization", f"{screen_avg:.1f}% (avg)", f"{screen_min:.1f}–{screen_max:.1f}%")
        except Exception as e:
            st.warning(f"Summary stats unavailable: {e}")

    st.subheader("🤖 AI Screen Advisor")
    try:
        alerts = []
        if screen_avg > 85:
            alerts.append("🔄 Screen Change Recommended — sustained utilization above 85%.")
        if shaker_max > 95 and screen_avg > 80:
            alerts.append("⚠️ High shaker output may indicate blinding or overload.")
        if screen_avg < 75 and shaker_avg < 70:
            alerts.append("✅ Screen and shaker running healthy.")
        for a in alerts:
            st.info(a)
    except Exception as e:
        st.warning(f"AI Summary error: {e}")

# 📈 Charts Tab
with tabs[1]:
    st.subheader("📊 Real-Time Shaker Performance")
    try:
        plot_df = df.sort_values('Timestamp').tail(1000)
        fig_realtime = go.Figure()
        fig_realtime.add_trace(go.Scatter(x=plot_df['Timestamp'], y=plot_df['SHAKER #3 (PERCENT)'], mode='lines+markers'))
        fig_realtime.update_layout(title='SHAKER #3 - Last 1000 Points')
        st.plotly_chart(fig_realtime, use_container_width=True)
    except Exception as e:
        st.warning(f"Real-time chart error: {e}")

# 🧪 Diagnostics Tab
with tabs[2]:
    st.subheader("🥧 Solids Removal Efficiency")
    try:
        in_rate = (df['Weight on Bit (klbs)'] * df['MA_Flow_Rate (gal/min)']) / 100
        out_rate = df['SHAKER #3 (PERCENT)']
        efficiency = (out_rate / (in_rate + 1e-5)) * 100
        eff_avg = efficiency.mean()
        pie = px.pie(values=[eff_avg, 100 - eff_avg], names=['Removed Solids', 'Losses'], title="Solids Removal Efficiency")
        st.plotly_chart(pie, use_container_width=True)
    except Exception as e:
        st.warning(f"Efficiency chart error: {e}")

    st.subheader("🔥 Mud Flow Impact Heatmap")
    try:
        heat_df = df[['Timestamp', 'MA_Flow_Rate (gal/min)', 'SHAKER #1 (Units)']].copy()
        heat_df['Hour'] = pd.to_datetime(heat_df['Timestamp']).dt.hour
        heat_df['Day'] = pd.to_datetime(heat_df['Timestamp']).dt.date
        heatmap = heat_df.groupby(['Day', 'Hour'])['MA_Flow_Rate (gal/min)'].mean().unstack().fillna(0)
        fig_heat = px.imshow(heatmap, labels=dict(color="Flow Rate"), title="Mud Flow vs Time Impact")
        st.plotly_chart(fig_heat, use_container_width=True)
    except Exception as e:
        st.warning(f"Heatmap error: {e}")

    st.subheader("🔍 AutoML Diagnostic Simulation")
    try:
        df['flag'] = ['normal'] * len(df)
        df.loc[df['Screen Utilization (%)'] > 90, 'flag'] = 'overloaded'
        df.loc[(df['Screen Utilization (%)'] > 80) & (df['SHAKER #3 (PERCENT)'] > 95), 'flag'] = 'warning'
        fig_ml = px.scatter(df, x='MA_Flow_Rate (gal/min)', y='Screen Utilization (%)',
                            color='flag', title="AutoML Diagnosis (Simulated)", opacity=0.7)
        st.plotly_chart(fig_ml, use_container_width=True)
    except Exception as e:
        st.warning(f"AutoML simulation failed: {e}")

# 📋 Raw Data Tab
with tabs[3]:
    st.subheader("📋 Full Dataset")
    page_size = st.selectbox("Rows per page", [50, 100, 200], index=1)
    total_rows = df.shape[0]
    total_pages = (total_rows - 1) // page_size + 1
    page = st.number_input("Page", min_value=1, max_value=total_pages, value=1)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    st.dataframe(df.iloc[start_idx:end_idx])
with st.expander("📌 Summary: Drilling & Shaker Overview", expanded=True):
    try:
        depth_col = 'Bit Depth (feet)' if 'Bit Depth (feet)' in df.columns else 'Hole Depth (feet)'
        total_depth = df[depth_col].max()

        df['Timestamp'] = pd.to_datetime(df['YYYY/MM/DD'] + ' ' + df['HH:MM:SS'])
        df = df.sort_values('Timestamp')
        df['Date'] = df['Timestamp'].dt.date
    except:
        st.warning("Could not parse timestamp.")
    if 'Screen Utilization (%)' not in df.columns and 'Weight on Bit (klbs)' in df.columns:
        df['Solids Volume Rate (gpm)'] = df['Weight on Bit (klbs)'] * df['MA_Flow_Rate (gal/min)'] / 100
        df['Screen Utilization (%)'] = (df['Solids Volume Rate (gpm)'] / mesh_capacity) * 100
    st.subheader("📊 Key Metrics")
    avg_util = df['Screen Utilization (%)'].mean()
    avg_flow = df['MA_Flow_Rate (gal/min)'].mean()
    shaker_max = df['SHAKER #3 (PERCENT)'].max()
    col1, col2, col3 = st.columns(3)
    col1.metric("Avg Utilization", f"{avg_util:.1f}%")
    col2.metric("Avg Flow Rate", f"{avg_flow:.1f} gpm")
    col3.metric("Max SHKR3", f"{shaker_max:.1f}%")
