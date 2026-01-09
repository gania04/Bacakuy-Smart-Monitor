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
    # Gunakan nama model dasar tanpa prefix v1beta
    model_ai = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Inisialisasi Gagal: {e}")

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

st.set_page_config(page_title="Bacakuy Smart Monitor", layout="wide")
df = load_data()

# =========================================================
# BAGIAN ATAS: ANALISIS AI
# =========================================================
st.title("📑 Bacakuy Sales Prediction & Insight")

col_in, col_res = st.columns([1, 2])

with col_in:
    in_units = st.number_input("Unit Terjual", value=100)
    in_rating = st.slider("Rating Buku", 0.0, 5.0, 4.2)
    predict_btn = st.button("Dapatkan Insight AI", use_container_width=True)

with col_res:
    if predict_btn and not df.empty:
        # Prediksi
        X = df[['units_sold', 'book_average_rating']]
        y = df['gross_sale']
        regr = LinearRegression().fit(X, y)
        prediction = regr.predict([[in_units, in_rating]])[0]
        
        st.metric("Estimasi Sales", f"Rp {prediction:,.0f}")
        
        # PROSES AI DENGAN LOGIKA RECOVERY
        st.subheader("🤖 Insight Strategi Bisnis")
        with st.spinner("Menghubungkan ke server Google..."):
            try:
                prompt = f"Berikan 1 insight strategi marketing syariah untuk target profit Rp {prediction:,.0f}."
                response = model_ai.generate_content(prompt)
                st.success(response.text)
            except Exception as e:
                # Pesan bantuan khusus jika requirements.txt belum diupdate
                st.error(f"Koneksi Gagal (404).")
                st.warning("Pastikan Anda sudah mengupdate file requirements.txt di GitHub dengan: google-generativeai==0.8.3")
    else:
        st.info("Klik tombol untuk memproses.")

st.divider()

# =========================================================
# BAGIAN BAWAH: HUB DENGAN FILTER DROPDOWN
# =========================================================
st.title("🚀 Strategic Intelligence Hub")

if not df.empty:
    # Filter Dropdown (Pilihan ke bawah)
    c1, c2 = st.columns(2)
    with c1:
        genres = ["Semua Kategori"] + sorted(list(df['genre'].unique()))
        sel_genre = st.selectbox("Pilih Kategori:", genres)
    with c2:
        sel_rating = st.selectbox("Minimal Rating:", [0.0, 3.0, 4.0, 4.5, 5.0])

    df_f = df.copy()
    if sel_genre != "Semua Kategori":
        df_f = df_f[df_f['genre'] == sel_genre]
    df_f = df_f[df_f['book_average_rating'] >= sel_rating]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Valuation", f"Rp {df_f['gross_sale'].sum():,.0f}")
    m2.metric("Units", f"{df_f['units_sold'].sum():,.0f}")
    m3.metric("Rating", f"{df_f['book_average_rating'].mean():.2f}")
    m4.metric("Status", "Connected")

    st.area_chart(df_f['gross_sale'])
