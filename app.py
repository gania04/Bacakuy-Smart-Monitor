import streamlit as st
import pandas as pd
from sklearn.linear_model import LinearRegression
import google.generativeai as genai
from supabase import create_client

# --- 1. KREDENSIAL ---
GEMINI_API_KEY = "AIzaSyApzYuBJ0QWbw6QXd75X9CYjo_E6_fZHoE"
SUPABASE_URL = "https://oftpulsqxjhhtfukmmtr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9mdHB1bHNxeGpoaHRmdWttbXRyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjU1NzAwNjksImV4cCI6MjA4MTE0NjA2OX0.aDLgRF2mzaJEW43h2hmZOBadEnDtUoRTZCueJHdfh04"

# --- 2. INISIALISASI ---
try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    genai.configure(api_key=GEMINI_API_KEY)
    
    # PERBAIKAN: Menggunakan format nama model lengkap untuk menghindari Error 404
    model_ai = genai.GenerativeModel('models/gemini-1.5-flash')
except Exception as e:
    st.error(f"Gagal Inisialisasi: {e}")

@st.cache_data
def load_data():
    try:
        res = supabase.table("bacakuy_sales").select("*").execute()
        df = pd.DataFrame(res.data)
        for col in ['book_average_rating', 'gross_sale']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(',', '.').astype(float)
        return df
    except:
        return pd.DataFrame()

st.set_page_config(page_title="Bacakuy Smart Monitor PRO", layout="wide")
df = load_data()

# =========================================================
# BAGIAN ATAS: PREDIKSI & INSIGHT AI (GEMINI 1.5 FLASH)
# =========================================================
st.title("📑 Bacakuy Sales Prediction & AI Analysis")

col_in, col_res = st.columns([1, 2])

with col_in:
    st.subheader("🔍 Input Data")
    in_units = st.number_input("Unit Terjual", value=100)
    in_rating = st.slider("Rating Buku", 0.0, 5.0, 4.2)
    predict_btn = st.button("Aktifkan Analisis AI", use_container_width=True)

with col_res:
    if predict_btn and not df.empty:
        # Kalkulasi Prediksi
        X = df[['units_sold', 'book_average_rating']]
        y = df['gross_sale']
        regr = LinearRegression().fit(X, y)
        prediction = regr.predict([[in_units, in_rating]])[0]
        
        st.metric("Estimasi Gross Sales (IDR)", f"Rp {prediction:,.0f}")
        
        # Eksekusi Gemini 1.5 Flash
        st.subheader("🤖 Strategi Bisnis & Insight (Gemini Flash)")
        with st.spinner("Menghubungkan ke Google AI Studio..."):
            try:
                prompt = f"Berikan 1 strategi marketing syariah untuk target profit Rp {prediction:,.0f}."
                response = model_ai.generate_content(prompt)
                st.info(response.text)
            except Exception as e:
                # Jika masih 404, tampilkan cara memperbaiki library
                st.error(f"AI Error: {e}")
                st.write("Coba jalankan: `pip install -U google-generativeai` di terminal Anda.")
    else:
        st.info("Klik tombol untuk memproses data.")

st.divider()

# =========================================================
# BAGIAN BAWAH: STRATEGIC HUB DENGAN DROPDOWN FILTER
# =========================================================
st.title("🚀 Strategic Intelligence Hub")

if not df.empty:
    # Filter Dropdown (Pilihan ke bawah)
    c1, c2 = st.columns(2)
    with c1:
        genres = ["Semua Kategori"] + sorted(list(df['genre'].unique()))
        sel_genre = st.selectbox("Pilih Kategori Buku:", genres)
    with c2:
        sel_rating = st.selectbox("Filter Minimal Rating:", [0.0, 3.0, 4.0, 4.5, 5.0])

    # Filter Data
    df_f = df.copy()
    if sel_genre != "Semua Kategori":
        df_f = df_f[df_f['genre'] == sel_genre]
    df_f = df_f[df_f['book_average_rating'] >= sel_rating]

    # Metrik
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Valuation", f"Rp {df_f['gross_sale'].sum():,.0f}")
    m2.metric("Total Units", f"{df_f['units_sold'].sum():,.0f}")
    m3.metric("Avg Rating", f"{df_f['book_average_rating'].mean():.2f}")
    m4.metric("Status", "Live Connected")

    # Grafik
    st.subheader(f"Statistik Penjualan: {sel_genre}")
    st.area_chart(df_f['gross_sale'])
