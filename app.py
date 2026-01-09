import streamlit as st
import pandas as pd
from sklearn.linear_model import LinearRegression
import google.generativeai as genai
from supabase import create_client

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Bacakuy Smart Monitor PRO", layout="wide")

# --- 2. INISIALISASI KREDENSIAL (DARI SECRETS) ---
try:
    # Mengambil kredensial dari menu Settings > Secrets di Streamlit
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    
    # Inisialisasi Service
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    genai.configure(api_key=GEMINI_API_KEY)
    
    # Inisialisasi Model Gemini (Versi paling stabil untuk library 0.8.3)
    model_ai = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Gagal memuat konfigurasi atau Secrets: {e}")

@st.cache_data
def load_data():
    try:
        res = supabase.table("bacakuy_sales").select("*").execute()
        df = pd.DataFrame(res.data)
        # Membersihkan data angka agar bisa dihitung oleh Kalkulator Prediksi
        for col in ['units_sold', 'book_average_rating', 'gross_sale']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce')
        return df.dropna(subset=['gross_sale', 'units_sold'])
    except:
        return pd.DataFrame()

df = load_data()

# =========================================================
# BAGIAN ATAS: KALKULATOR PREDIKSI & ANALISIS AI
# =========================================================
st.title("📑 Bacakuy Sales Prediction & AI Analysis")
st.markdown("Gunakan kalkulator di bawah untuk memprediksi pendapatan berdasarkan performa buku.")

col_in, col_res = st.columns([1, 2])

with col_in:
    st.subheader("🔍 Kalkulator Prediksi")
    in_units = st.number_input("Target Unit Terjual", min_value=1, value=100)
    in_rating = st.slider("Target Rating Buku", 0.0, 5.0, 4.2)
    predict_btn = st.button("Hitung Prediksi & Insight AI", use_container_width=True)

with col_res:
    if predict_btn and not df.empty:
        # LOGIKA KALKULATOR: Linear Regression
        X = df[['units_sold', 'book_average_rating']]
        y = df['gross_sale']
        regr = LinearRegression().fit(X, y)
        prediction = regr.predict([[in_units, in_rating]])[0]
        
        # Tampilan Hasil Prediksi
        st.metric("Estimasi Gross Sales (IDR)", f"Rp {prediction:,.0f}")
        
        # LOGIKA AI: Insight Strategi Bisnis
        st.subheader("🤖 Strategi Bisnis Syariah (AI Insight)")
        with st.spinner("AI sedang menyusun strategi..."):
            try:
                prompt = f"Berikan 1 insight strategi marketing syariah untuk target profit Rp {prediction:,.0f} dengan rating buku {in_rating}."
                response = model_ai.generate_content(prompt)
                st.success(response.text)
            except Exception:
                st.warning("Insight AI sementara tidak tersedia (Error 404). Silakan Reboot aplikasi di menu Manage App.")
    else:
        st.info("Masukkan angka unit dan rating, lalu klik tombol untuk melihat hasil.")

st.divider()

# =========================================================
# BAGIAN BAWAH: STRATEGIC HUB (METRIK & DROPDOWN FILTER)
# =========================================================
st.title("🚀 Strategic Intelligence Hub")

if not df.empty:
    # Filter Dropdown (Pilihan menarik ke bawah)
    c1, c2 = st.columns(2)
    with c1:
        genres = ["Semua Kategori"] + sorted(list(df['genre'].unique()))
        sel_genre = st.selectbox("Pilih Kategori Buku:", genres)
    with c2:
        sel_rating = st.selectbox("Filter Minimal Rating:", [0.0, 3.0, 4.0, 4.5, 5.0])

    # Proses Filter Data
    df_f = df.copy()
    if sel_genre != "Semua Kategori":
        df_f = df_f[df_f['genre'] == sel_genre]
    df_f = df_f[df_f['book_average_rating'] >= sel_rating]

    # Barisan Metrik Ringkasan
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Market Valuation", f"Rp {df_f['gross_sale'].sum():,.0f}")
    m2.metric("Total Units", f"{df_f['units_sold'].sum():,.0f}")
    m3.metric("Avg Rating", f"{df_f['book_average_rating'].mean():.2f}")
    m4.metric("Status", "Live Sync")

    # Grafik Area Visualisasi
    st.subheader(f"Tren Penjualan: {sel_genre}")
    st.area_chart(df_f['gross_sale'])
else:
    st.error("Data dari Supabase tidak ditemukan atau gagal dimuat.")
