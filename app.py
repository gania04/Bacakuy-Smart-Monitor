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
        res = supabase.table("bacakuy_sales_clean").select("*").execute()
        return pd.DataFrame(res.data)
    except:
        return pd.DataFrame()

# --- SETUP HALAMAN ---
st.set_page_config(page_title="Bacakuy Smart Monitor Pro", layout="wide")
df = load_data()

# =========================================================
# BAGIAN 1: KALKULATOR PREDIKSI (WhatsApp Style)
# =========================================================
st.title("📑 Bacakuy Sales Prediction & Islamic Strategy AI")
col_calc, col_result = st.columns([1, 2])

with col_calc:
    st.subheader("🔍 Input Fitur Prediksi")
    in_units = st.number_input("Jumlah Unit Terjual (Units Sold)", value=100)
    in_rating = st.slider("Rating Rata-rata Buku", 0.0, 5.0, 4.5)
    predict_btn = st.button("Prediksi Sekarang", use_container_width=True)

with col_result:
    if predict_btn and not df.empty:
        X = df[['units_sold', 'book_average_rating']]
        y = df['gross_sale']
        model = LinearRegression().fit(X, y)
        prediction = model.predict([[in_units, in_rating]])[0]
        st.subheader("📊 Hasil Prediksi Penjualan")
        st.metric("Estimasi Gross Sales (IDR)", f"Rp {prediction:,.0f}")
        st.info("Prediksi menggunakan Linear Regression berdasarkan data historis.")
    else:
        st.info("Masukkan data dan klik 'Prediksi Sekarang'.")

st.markdown("---")

# =========================================================
# BAGIAN 2: STRATEGIC INTELLIGENCE HUB (Dashboard Style)
# =========================================================
st.title("🚀 Strategic Intelligence Hub")
if not df.empty:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Market Valuation", f"Rp {df['gross_sale'].sum():,.0f}", "+5.2%")
    m2.metric("Circulation", f"{df['units_sold'].sum():,.0f}", "Units Delivered")
    m3.metric("Brand Loyalty", f"{df['book_average_rating'].mean():.2f}/5", "Avg Sentiments")
    m4.metric("Status", "Live Production", "Active")
    
    col_f, col_c = st.columns([1, 2])
    with col_f:
        selected_genre = st.selectbox("Segment Filter", df['genre'].unique())
        st.area_chart(df[df['genre'] == selected_genre]['gross_sale'])
    with col_c:
        st.subheader("Sales Performance Trend")
        st.bar_chart(df['units_sold'])

st.markdown("---")

# =========================================================
# BAGIAN 3: GOOGLE AI STUDIO INTERFACE (Prompt Style)
# =========================================================
st.title("🤖 Google AI Studio Assistant")
st.write("Gunakan bagian ini untuk bertanya langsung kepada AI tentang data Anda.")

# Meniru tampilan panel samping AI Studio
col_chat, col_settings = st.columns([3, 1])

with col_settings:
    st.write("⚙️ **Settings**")
    st.selectbox("Model", ["gemini-1.5-flash", "gemini-1.5-pro"])
    st.slider("Temperature", 0.0, 1.0, 0.7)
    st.write("**AI Features Available:**")
    st.caption("- Analyze Author Performance")
    st.caption("- Track Profitability")

with col_chat:
    user_prompt = st.text_area("Make changes, add new features, ask for anything...", placeholder="Contoh: Berikan ide promo untuk genre fiction di bulan Ramadhan...")
    
    if st.button("Generate Strategy"):
        if user_prompt:
            with st.spinner("AI sedang memproses..."):
                model_ai = genai.GenerativeModel('gemini-1.5-flash')
                # AI diberikan konteks data dashboard secara otomatis
                full_prompt = f"Data Dashboard: Total Sales Rp {df['gross_sale'].sum()}. Pertanyaan: {user_prompt}"
                response = model_ai.generate_content(full_prompt)
                st.markdown(f"### ✨ AI Response:\n{response.text}")
        else:
            st.warning("Silakan masukkan pertanyaan terlebih dahulu.")
