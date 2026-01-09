import streamlit as st
import pandas as pd
from sklearn.linear_model import LinearRegression
import google.generativeai as genai
from supabase import create_client

# --- 1. KREDENSIAL TERVERIFIKASI ---
SUPABASE_URL = "https://oftpulsqxjhhtfukmmtr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9mdHB1bHNxeGpoaHRmdWttbXRyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjU1NzAwNjksImV4cCI6MjA4MTE0NjA2OX0.aDLgRF2mzaJEW43h2hmZOBadEnDtUoRTZCueJHdfh04"
GEMINI_API_KEY = "AIzaSyApzYuBJ0QWbw6QXd75X9CYjo_E6_fZHoE" # API Key Anda sudah terpasang

# Inisialisasi Service
try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    genai.configure(api_key=GEMINI_API_KEY)
    model_ai = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Gagal Inisialisasi: {e}")

@st.cache_data
def load_data():
    try:
        # Menghubungkan ke tabel bacakuy_sales sesuai permintaan
        res = supabase.table("bacakuy_sales").select("*").execute()
        df = pd.DataFrame(res.data)
        # Normalisasi angka (mengubah koma ke titik)
        for col in ['book_average_rating', 'gross_sale']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(',', '.').astype(float)
        return df
    except:
        return pd.DataFrame()

st.set_page_config(page_title="Bacakuy Smart Monitor PRO", layout="wide")
df = load_data()

# =========================================================
# BAGIAN ATAS: KALKULATOR PREDIKSI & AI INSIGHT
# =========================================================
st.title("📑 Bacakuy Sales Prediction & Islamic Strategy AI")
col_in, col_res = st.columns([1, 2])

with col_in:
    st.subheader("🔍 Input Fitur Prediksi")
    u_input = st.number_input("Jumlah Unit Terjual (Units)", value=100)
    r_input = st.slider("Rating Rata-rata Buku", 0.0, 5.0, 4.0)
    btn_predict = st.button("Prediksi Sekarang", use_container_width=True)

with col_res:
    if btn_predict and not df.empty:
        # Prediksi Linear Regression
        X = df[['units_sold', 'book_average_rating']]
        y = df['gross_sale']
        model = LinearRegression().fit(X, y)
        pred = model.predict([[u_input, r_input]])[0]
        
        st.metric("Estimasi Gross Sales (IDR)", f"Rp {pred:,.0f}")
        
        # --- KONEKSI AI GEMINI ---
        st.subheader("☪️ Analisis Strategi Bisnis Syariah (AI)")
        with st.spinner("AI sedang merancang strategi..."):
            try:
                prompt = f"Berikan 1 strategi marketing syariah dan 1 pesan moral untuk target profit Rp {pred:,.0f}."
                response = model_ai.generate_content(prompt)
                st.info(response.text)
            except Exception as e:
                st.error(f"AI Error: {e}")

st.divider()

# =========================================================
# BAGIAN TENGAH: STRATEGIC INTELLIGENCE HUB
# =========================================================
st.title("🚀 Strategic Intelligence Hub")
if not df.empty:
    # Metrik Utama
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Market Valuation", f"Rp {df['gross_sale'].sum():,.0f}", "+5.2%")
    m2.metric("Circulation", f"{df['units_sold'].sum():,.0f}", "Units Delivered")
    m3.metric("Brand Loyalty", f"{df['book_average_rating'].mean():.2f}/5", "Avg Sentiments")
    m4.metric("Status", "Live Production", "Active")

st.divider()

# =========================================================
# BAGIAN BAWAH: GOOGLE AI STUDIO & FILTERED ANALYTICS
# =========================================================
st.title("🤖 Google AI Studio & Analytics")
col_side, col_main = st.columns([1, 3])

with col_side:
    st.write("⚙️ **Settings & Filters**")
    # Filter Genre Baru
    filter_genre = st.multiselect("Filter Genre", options=df['genre'].unique(), default=df['genre'].unique())
    # Filter Rating Baru
    min_rating = st.slider("Minimal Rating di Grafik", 0.0, 5.0, 0.0)
    
    st.write("---")
    st.button("Analyze Author Performance")
    st.button("Track Profitability")

# Terapkan Filter ke Data
df_filtered = df[(df['genre'].isin(filter_genre)) & (df['book_average_rating'] >= min_rating)]

with col_main:
    tab1, tab2, tab3 = st.tabs(["Monthly Trend", "Units Distribution", "Correlation Analysis"])
    
    with tab1:
        st.subheader("Monthly Sales Trend (Filtered)")
        # Grafik Tren Operasional
        st.area_chart(df_filtered['gross_sale'])
        
    with tab2:
        st.subheader("Units Sold by Genre")
        # Grafik Batang Horizontal
        genre_summary = df_filtered.groupby('genre')['units_sold'].sum()
        st.bar_chart(genre_summary, horizontal=True)
        
    with tab3:
        st.subheader("Rating vs Units Sold")
        # Grafik Korelasi
        st.scatter_chart(df_filtered[['book_average_rating', 'units_sold']])
