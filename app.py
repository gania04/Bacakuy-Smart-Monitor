import streamlit as st
import pandas as pd
from sklearn.linear_model import LinearRegression
import google.generativeai as genai
from supabase import create_client

# --- 1. MENGAMBIL KREDENSIAL DARI SECRETS ---
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    
    # Inisialisasi Service
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    genai.configure(api_key=GEMINI_API_KEY)
    # Gunakan model dasar agar kompatibel dengan library 0.8.3
    model_ai = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Gagal memuat Secrets: {e}. Pastikan format TOML di menu Secrets sudah benar.")

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
st.title("📑 Bacakuy Sales Prediction & AI Analysis")
col_in, col_res = st.columns([1, 2])

with col_in:
    st.subheader("🔍 Input Fitur")
    in_units = st.number_input("Unit Terjual", value=100)
    in_rating = st.slider("Rating Buku", 0.0, 5.0, 4.2)
    predict_btn = st.button("Aktifkan Analisis AI", use_container_width=True)

with col_res:
    if predict_btn and not df.empty:
        # Prediksi Linear Regression
        X = df[['units_sold', 'book_average_rating']]
        y = df['gross_sale']
        regr = LinearRegression().fit(X, y)
        prediction = regr.predict([[in_units, in_rating]])[0]
        st.metric("Estimasi Gross Sales", f"Rp {prediction:,.0f}")
        
        st.subheader("🤖 Hasil Analisis Strategi AI")
        with st.spinner("Menghubungkan ke Google AI Studio..."):
            try:
                # Memaksa penggunaan format prompt yang simpel
                prompt = f"Berikan 1 strategi marketing syariah untuk target profit Rp {prediction:,.0f}."
                response = model_ai.generate_content(prompt)
                st.info(response.text)
            except Exception as e:
                st.error(f"Koneksi AI Gagal: {e}")
                st.warning("Jika muncul Error 404, Anda WAJIB melakukan 'Reboot App' dari menu Manage App.")

st.divider()

# =========================================================
# BAGIAN BAWAH: HUB DENGAN DROPDOWN FILTER
# =========================================================
st.title("🚀 Strategic Intelligence Hub")
if not df.empty:
    c1, c2 = st.columns(2)
    with c1:
        sel_genre = st.selectbox("Pilih Genre:", ["Semua Kategori"] + sorted(list(df['genre'].unique())))
    with c2:
        sel_rating = st.selectbox("Filter Minimal Rating:", [0.0, 3.0, 4.0, 4.5, 5.0])

    df_f = df.copy()
    if sel_genre != "Semua Kategori":
        df_f = df_f[df_f['genre'] == sel_genre]
    df_f = df_f[df_f['book_average_rating'] >= sel_rating]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Market Valuation", f"Rp {df_f['gross_sale'].sum():,.0f}")
    m2.metric("Circulation", f"{df_f['units_sold'].sum():,.0f}")
    m3.metric("Brand Loyalty", f"{df_f['book_average_rating'].mean():.2f}")
    m4.metric("Status", "Live Connected")

    st.area_chart(df_f['gross_sale'])
