import os
import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client, Client
from datetime import datetime

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="bacakuy-smart-monitoring",
    page_icon="📈",
    layout="wide"
)

# --- 2. KONEKSI AMAN KE SUPABASE (OS ENVIRON) ---
@st.cache_resource
def init_connection():
    try:
        # Mengambil kredensial dari environment variables untuk keamanan
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        
        if not url or not key:
            st.error("Konfigurasi Gagal: SUPABASE_URL atau SUPABASE_KEY tidak ditemukan di environment variables.")
            return None
        
        return create_client(url, key)
    except Exception as e:
        st.error(f"Gagal menginisialisasi koneksi Supabase: {e}")
        return None

# --- 3. FUNGSI PENGAMBILAN DATA ---
@st.cache_data(ttl=600)  # Refresh data setiap 10 menit
def load_data():
    supabase = init_connection()
    if not supabase:
        return pd.DataFrame()
    
    try:
        # Mengambil data dari tabel penjualan_buku
        response = supabase.table("penjualan_buku").select("*").execute()
        df = pd.DataFrame(response.data)
        
        if not df.empty:
            # Konversi tanggal dan pastikan tipe data numerik benar
            df['publish_date'] = pd.to_datetime(df['publish_date'])
            numeric_cols = ['publisher_revenue', 'units_sold', 'author_rating', 'book_average_rating']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Terjadi kesalahan saat menarik data: {e}")
        return pd.DataFrame()

# Inisialisasi Data Utama
df_raw = load_data()

# --- 4. TAMPILAN HEADER ---
st.title("📊 bacakuy-smart-monitoring")
st.markdown("""
Dashboard ini berfungsi untuk menganalisis performa penjualan buku secara *real-time* berdasarkan data yang tersimpan di Supabase. 
Gunakan filter di sidebar untuk menyesuaikan tampilan data.
""")
st.divider()

# Cek apakah data tersedia sebelum melanjutkan
if df_raw.empty:
    st.warning("⚠️ Data tidak tersedia. Pastikan tabel 'penjualan_buku' memiliki data dan koneksi Supabase sudah benar.")
    st.stop()

# --- 5. SIDEBAR FILTER ---
st.sidebar.header("Filter Navigasi")

# Filter Berdasarkan Genre
genres = sorted(df_raw['genre'].dropna().unique())
selected_genres = st.sidebar.multiselect("Pilih Genre:", options=genres, default=genres)

# Filter Berdasarkan Author Rating
min_rate = float(df_raw['author_rating'].min())
max_rate = float(df_raw['author_rating'].max())
selected_rating = st.sidebar.slider(
    "Rentang Author Rating:",
    min_value=min_rate,
    max_value=max_rate,
    value=(min_rate, max_rate)
)

# Aplikasi Filter ke Dataframe
df_filtered = df_raw[
    (df_raw['genre'].isin(selected_genres)) &
    (df_raw['author_rating'] >= selected_rating[0]) &
    (df_raw['author_rating'] <= selected_rating[1])
]

# --- 6. KPI UTAMA ---
if not df_filtered.empty:
    kpi1, kpi2, kpi3 = st.columns(3)
    
    with kpi1:
        total_rev = df_filtered['publisher_revenue'].sum()
        # Format Mata Uang Dollar dengan pemisah ribuan koma
        st.metric("Total Publisher Revenue", f"${total_rev:,.2f}")
        
    with kpi2:
        total_units = int(df_filtered['units_sold'].sum())
        st.metric("Total Units Sold", f"{total_units:,}")
        
    with kpi3:
        avg_rating = df_filtered['book_average_rating'].mean()
        st.metric("Average Book Rating", f"{avg_rating:.2f} / 5.0")

    st.write("") # Spacer

    # --- 7. GRAFIK TREN BULANAN (LINE CHART) ---
    st.subheader("📈 Tren Pendapatan Bulanan")
    try:
        df_filtered['month_year'] = df_filtered['publish_date'].dt.to_period('M').astype(str)
        monthly_trend = df_filtered.groupby('month_year')['publisher_revenue'].sum().reset_index()
        
        fig_line = px.line(
            monthly_trend, 
            x='month_year', 
            y='publisher_revenue',
            labels={'publisher_revenue': 'Revenue ($)', 'month_year': 'Bulan'},
            markers=True,
            template="plotly_white"
        )
        fig_line.update_traces(line_color='#1f77b4')
        st.plotly_chart(fig_line, use_container_width=True)
    except Exception as e:
        st.error(f"Gagal memuat grafik tren: {e}")

    # --- 8. KOMPOSISI GENRE (HORIZONTAL BAR CHART) ---
    st.subheader("📚 Unit Terjual Berdasarkan Genre")
    try:
        genre_data = df_filtered.groupby('genre')['units_sold'].sum().sort_values(ascending=True).reset_index()
        
        fig_bar = px.bar(
            genre_data,
            x='units_sold',
            y='genre',
            orientation='h',
            color='units_sold',
            # Menggunakan skema warna Blues yang profesional
            color_continuous_scale='Blues',
            labels={'units_sold': 'Total Unit', 'genre': 'Genre'},
            template="plotly_white"
        )
        fig_bar.update_layout(showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)
    except Exception as e:
        st.error(f"Gagal memuat grafik genre: {e}")

else:
    st.info("💡 Tidak ada data yang sesuai dengan kriteria filter Anda.")

# --- 9. FOOTER ---
st.divider()
st.caption(f"bacakuy-smart-monitoring | System Status: Online | {datetime.now().year}")
