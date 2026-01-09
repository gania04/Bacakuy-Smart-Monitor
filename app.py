import streamlit as st
import pandas as pd
from sklearn.linear_model import LinearRegression
import google.generativeai as genai
from supabase import create_client

# --- 1. KONFIGURASI KONEKSI ---
SUPABASE_URL = "https://oftpulsqxjhhtfukmmtr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9mdHB1bHNxeGpoaHRmdWttbXRyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjU1NzAwNjksImV4cCI6MjA4MTE0NjA2OX0.aDLgRF2mzaJEW43h2hmZOBadEnDtUoRTZCueJHdfh04"
GEMINI_API_KEY = "AIzaSyApzYuBJ0QWbw6QXd75X9CYjo_E6_fZHoE"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
genai.configure(api_key=GEMINI_API_KEY)

@st.cache_data
def load_data():
    try:
        # Mengambil data dari tabel yang sudah dibersihkan
        res = supabase.table("bacakuy_sales_clean").select("*").execute()
        return pd.DataFrame(res.data)
    except Exception as e:
        return pd.DataFrame()

# --- SETUP HALAMAN ---
st.set_page_config(page_title="Bacakuy Smart Monitor", layout="wide")
df = load_data()

# =========================================================
# BAGIAN ATAS: KALKULATOR PREDIKSI & ISLAMIC STRATEGY AI
# (Meniru WhatsApp Image 2026-01-08 at 11.39.51.jpeg)
# =========================================================
st.title("📑 Bacakuy Sales Prediction & Islamic Strategy AI")
st.write("Masukkan data untuk mendapatkan estimasi profit dan strategi bisnis.")

col_calc, col_result = st.columns([1, 2])

with col_calc:
    st.subheader("🔍 Input Fitur Prediksi")
    in_units = st.number_input("Jumlah Unit Terjual (Units Sold)", value=100)
    # Menggunakan slider untuk rating agar presisi
    in_rating = st.slider("Rating Rata-rata Buku", 0.0, 5.0, 4.5)
    predict_btn = st.button("Prediksi Sekarang", use_container_width=True)

with col_result:
    if predict_btn and not df.empty:
        # Logika Machine Learning
        X = df[['units_sold', 'book_average_rating']]
        y = df['gross_sale']
        model = LinearRegression().fit(X, y)
        prediction = model.predict([[in_units, in_rating]])[0]
        
        st.subheader("📊 Hasil Prediksi Penjualan")
        st.metric("Estimasi Gross Sales (IDR)", f"Rp {prediction:,.0f}")
        st.info("Prediksi ini menggunakan algoritma Linear Regression berdasarkan data historis.")
        
        # Analisis Strategi AI
        st.subheader("☪️ Analisis Strategi Bisnis Syariah (AI)")
        try:
            model_ai = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"Berikan strategi marketing syariah untuk penjualan {in_units} buku dengan estimasi profit Rp {prediction:,.0f}."
            response = model_ai.generate_content(prompt)
            st.write(response.text)
        except:
            st.warning("Gagal mendapatkan analisis AI. Periksa koneksi atau API Key Gemini Anda.")
    else:
        st.info("Silakan masukkan data dan klik 'Prediksi Sekarang' untuk melihat hasil.")

st.markdown("---") # Garis Pembatas

# =========================================================
# BAGIAN BAWAH: DASHBOARD MONITORING (STRATEGIC HUB)
# (Meniru image_d4186a.png)
# =========================================================
st.title("📊 Strategic Intelligence Hub")
st.write("Menganalisis performa judul buku secara real-time dari Supabase.")

if not df.empty:
    # Metric Cards
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Market Valuation", f"Rp {df['gross_sale'].sum():,.0f}", "+5.2%")
    m2.metric("Circulation", f"{df['units_sold'].sum():,.0f}", "Units Delivered")
    m3.metric("Brand Loyalty", f"{df['book_average_rating'].mean():.2f}/5", "Avg Sentiments")
    m4.metric("Status", "Live Production", "Active")

    # Filter & Grafik
    col_filter, col_chart = st.columns([1, 2])
    with col_filter:
        st.subheader("Segment Filter")
        selected_genre = st.selectbox("All Categories", df['genre'].unique())
        df_filtered = df[df['genre'] == selected_genre]
        
    with col_chart:
        st.subheader("Sales Performance Trend")
        st.area_chart(df_filtered['gross_sale'])
else:
    st.error("Data Supabase tidak ditemukan. Pastikan koneksi benar.")
