import streamlit as st
import pandas as pd
import plotly.express as px

# Konfigurasi Halaman
st.set_page_config(page_title="Dashboard PWS-KIA Pecangaan", layout="wide")

# Load Data hasil cleaning kita
@st.cache_data
def load_data():
    return pd.read_excel('Laporan_Final_PWS_KIA.xlsx')

df = load_data()

# --- SIDEBAR FILTER ---
st.sidebar.header("Filter Dashboard")
desa_filter = st.sidebar.multiselect(
    "Pilih Desa:",
    options=df["Desa"].unique(),
    default=df["Desa"].unique()
)

df_filtered = df[df["Desa"].isin(desa_filter)]

# --- HEADER & DYNAMIC CARDS ---
st.title("📊 Dashboard Pemantauan PWS-KIA")
st.markdown("Analisis Kinerja Pelayanan Kesehatan Ibu dan Anak")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Desa", len(df_filtered))
with col2:
    st.metric("Total Sasaran", f"{df_filtered['Sasaran'].sum():.0f}")
with col3:
    avg_kum = df_filtered['Kum_%'].mean()
    st.metric("Rata-rata Capaian", f"{avg_kum:.2f}%")
with col4:
    baik_count = len(df_filtered[df_filtered['Status'] == 'BAIK'])
    st.metric("Desa Status BAIK", baik_count)

st.divider()

# --- VISUALISASI INTERAKTIF ---
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("Grafik Capaian Kumulatif per Desa")
    fig = px.bar(df_filtered, x='Desa', y='Kum_%', 
                 color='Status', 
                 color_discrete_map={'BAIK': '#2ecc71', 'CUKUP': '#f1c40f', 'JELEK': '#e74c3c', 'KURANG': '#e67e22'},
                 text_auto='.2s',
                 title="Capaian K1 vs Target")
    fig.add_hline(y=8.33, line_dash="dash", line_color="red", annotation_text="Target 8.33%")
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("Proporsi Status Desa")
    fig_pie = px.pie(df_filtered, names='Status', 
                     color='Status',
                     color_discrete_map={'BAIK': '#2ecc71', 'CUKUP': '#f1c40f', 'JELEK': '#e74c3c', 'KURANG': '#e67e22'})
    st.plotly_chart(fig_pie, use_container_width=True)

# --- PIVOT TABLE SECTION ---
st.subheader("Ringkasan Data (Pivot Table Style)")
pivot_df = df_filtered.groupby('Status').agg({
    'Desa': 'count',
    'Sasaran': 'sum',
    'Kum_%': 'mean'
}).rename(columns={'Desa': 'Jumlah Desa', 'Kum_%': 'Rata-rata Capaian (%)'})

st.table(pivot_df)

# Menampilkan Data Mentah
if st.checkbox("Tampilkan Detail Data"):
    st.dataframe(df_filtered)