import streamlit as st
import pandas as pd
from sklearn.linear_model import LinearRegression
import google.generativeai as genai
from supabase import create_client

# --- 1. KONFIGURASI KREDENSIAL ---
# Menggunakan URL dan Key dari dashboard Supabase Anda
SUPABASE_URL = "https://oftpulsqxjhhtfukmmtr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9mdHB1bHNxeGpoaHRmdWttbXRyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjU1NzAwNjksImV4cCI6MjA4MTE0NjA2OX0.aDLgRF2mzaJEW43h2hmZOBadEnDtUoRTZCueJHdfh04"
# Menggunakan API Key Google AI Studio Anda
GEMINI_API_KEY = "AIzaSyApzYuBJ0QWbw6QXd75X9CYjo_E6_fZHoE"

# Inisialisasi Service
try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    genai.configure(api_key=GEMINI_API_KEY)
    # Perbaikan Model: Menggunakan 'gemini-1.5-flash' untuk menghindari Error 404
    model_ai = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Gagal Inisialisasi Service: {e}")

@st.cache_data
def load_data():
    try:
        # Menghubungkan ke tabel bacakuy_sales
        res = supabase.table("bacakuy_sales").select("*").execute()
        df = pd.DataFrame(res.data)
        
        # Normalisasi Data: Mengubah koma menjadi titik agar bisa dihitung
        for col in ['book_average_rating', 'gross_sale']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(',', '.').astype(float)
        return df
    except Exception as e:
        st.error(f"Gagal mengambil data dari Supabase: {e}")
        return pd.DataFrame()

# --- SETUP HALAMAN ---
st.set_page_config(page_title="Bacakuy Smart Monitor PRO", layout="wide")
df = load_data()

# =========================================================
# BAGIAN ATAS: KALKULATOR PREDIKSI & ISLAMIC STRATEGY AI
# =========================================================
st.title("📑 Bacakuy Sales Prediction & Islamic Strategy AI")
st.write("Masukkan data untuk mendapatkan estimasi profit dan strategi bisnis.")

col_calc, col_result = st.columns([1, 2])

with col_calc:
    st.subheader("🔍 Input Fitur Prediksi")
    in_units = st.number_input("Jumlah Unit Terjual (Units Sold)", value=100)
    # Slider rating default disesuaikan dengan rata-rata data Anda
    in_rating = st.slider("Rating Rata-rata Buku", 0.0, 5.0, 4.0) 
    predict_btn = st.button("Prediksi Sekarang", use_container_width=True)

with col_result:
    if predict_btn and not df.empty:
        # Logika Prediksi Linear Regression
        X = df[['units_sold', 'book_average_rating']]
        y = df['gross_sale']
        model_lr = LinearRegression().fit(X, y)
        prediction = model_lr.predict([[in_units, in_rating]])[0]
        
        st.subheader("📊 Hasil Prediksi Penjualan")
        st.metric("Estimasi Gross Sales (IDR)", f"Rp {prediction:,.0f}")
        
        # --- KONEKSI AI GEMINI ---
        st.subheader("☪️ Analisis Strategi Bisnis Syariah (AI)")
        with st.spinner("AI sedang merancang strategi bisnis..."):
            try:
                # Prompt instruksi untuk AI
                prompt = f"Berikan 1 strategi marketing syariah untuk penjualan buku dengan estimasi profit Rp {prediction:,.0f}."
                response = model_ai.generate_content(prompt)
                st.info(response.text) # Menampilkan hasil AI
            except Exception as e:
                st.error(f"AI Error: {e}. Periksa kembali API Key atau kuota Google AI Studio Anda.")
    else:
        st.info("Silakan masukkan data dan klik 'Prediksi Sekarang'.")

st.divider()

# =========================================================
# BAGIAN TENGAH: STRATEGIC INTELLIGENCE HUB (METRIK UTAMA)
# =========================================================
st.title("🚀 Strategic Intelligence Hub")
if not df.empty:
    # Menampilkan metrik utama sesuai desain Bacakuy PRO
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Market Valuation", f"Rp {df['gross_sale'].sum():,.0f}", "+5.2%")
    m2.metric("Circulation", f"{df['units_sold'].sum():,.0f}", "Units Delivered")
    m3.metric("Brand Loyalty", f"{df['book_average_rating'].mean():.2f}/5", "Avg Sentiments")
    m4.metric("Status", "Live Production", "Active")

st.divider()

# =========================================================
# BAGIAN BAWAH: GOOGLE AI STUDIO & FILTERED ANALYTICS
# =========================================================
st.title("🤖 Google AI Studio & Performance Analytics")
col_side, col_main = st.columns([1, 3])

with col_side:
    st.write("⚙️ **Settings & Filter Hub**")
    
    # FILTER DROPDOWN (Pilihan ke bawah)
    if not df.empty:
        genres = ["Semua Kategori"] + sorted(list(df['genre'].unique()))
        selected_genre = st.selectbox("Pilih Genre:", genres)
        
        rating_list = [0.0, 1.0, 2.0, 3.0, 4.0, 4.5, 5.0]
        selected_min_rating = st.selectbox("Minimal Rating:", rating_list, index=0)
    
    st.write("---")
    st.button("Analyze Author Performance", use_container_width=True)
    st.button("Track Profitability", use_container_width=True)

# Menerapkan Filter ke Data
if not df.empty:
    df_filtered = df.copy()
    if selected_genre != "Semua Kategori":
        df_filtered = df_filtered[df_filtered['genre'] == selected_genre]
    df_filtered = df_filtered[df_filtered['book_average_rating'] >= selected_min_rating]

    with col_main:
        tab1, tab2, tab3 = st.tabs(["Monthly Trend", "Units by Genre", "Performance Intelligence"])
        
        with tab1:
            st.subheader(f"Sales Trend: {selected_genre}")
            # Grafik tren operasional
            st.area_chart(df_filtered['gross_sale'])
            
        with tab2:
            st.subheader("Units Sold Distribution")
            # Grafik batang horizontal sesuai desain
            genre_data = df_filtered.groupby('genre')['units_sold'].sum()
            st.bar_chart(genre_data, horizontal=True)
            
        with tab3:
            st.subheader("Rating vs Market Popularity")
            # Scatter plot korelasi
            st.scatter_chart(df_filtered[['book_average_rating', 'units_sold']])
else:
    st.warning("Data belum tersedia. Pastikan tabel 'bacakuy_sales' di Supabase sudah terisi.")
