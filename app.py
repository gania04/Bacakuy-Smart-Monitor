import streamlit as st
import pandas as pd
from sklearn.linear_model import LinearRegression
import google.generativeai as genai
from supabase import create_client

# --- KREDENSIAL ---
SUPABASE_URL = "https://oftpulsqxjhhtfukmmtr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9mdHB1bHNxeGpoaHRmdWttbXRyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjU1NzAwNjksImV4cCI6MjA4MTE0NjA2OX0.aDLgRF2mzaJEW43h2hmZOBadEnDtUoRTZCueJHdfh04"
GEMINI_API_KEY = "AIzaSyApzYuBJ0QWbw6QXd75X9CYjo_E6_fZHoE"

# Inisialisasi Service
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
genai.configure(api_key=GEMINI_API_KEY)

@st.cache_data
def load_data():
    try:
        # Memanggil tabel yang sudah dibersihkan (Langkah SQL di atas)
        res = supabase.table("bacakuy_sales_clean").select("*").execute()
        return pd.DataFrame(res.data)
    except Exception as e:
        st.error(f"Koneksi Gagal: {e}")
        return pd.DataFrame()

# --- UI DASHBOARD ---
st.set_page_config(page_title="Bacakuy Smart Monitor", layout="wide")

# Header sesuai desain Bacakuy PRO
st.title("📊 Bacakuy Smart Monitor")
st.subheader("Strategic Intelligence Hub")
st.write("Menganalisis performa judul buku secara real-time.")

df = load_data()

if not df.empty:
    # --- BARIS 1: KARTU METRIK (Metric Cards) ---
    # Layout ini meniru desain Market Valuation & Circulation
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Market Valuation", f"Rp {df['gross_sale'].sum():,.0f}", "+5.2%")
    with m2:
        st.metric("Circulation", f"{df['units_sold'].sum():,.0f}", "Units Delivered")
    with m3:
        st.metric("Brand Loyalty", f"{df['book_average_rating'].mean():.2f}/5", "Avg Sentiments")
    with m4:
        st.metric("Status", "Live Production", "Active")

    st.divider()

    # --- BARIS 2: ANALISIS & PREDIKSI ---
    col_input, col_graph = st.columns([1, 2])

    with col_input:
        st.markdown("### Segment Filter & Prediction")
        # Filter Kategori
        genres = df['genre'].unique().tolist()
        selected_genre = st.selectbox("All Categories", genres)
        
        df_f = df[df['genre'] == selected_genre]
        
        st.write("---")
        # Fitur Prediksi Profit
        in_u = st.number_input("Target Terjual (Units)", value=100)
        in_r = st.slider("Target Rating", 1.0, 5.0, 4.5)
        
        if st.button("Generate Strategic Insight", use_container_width=True):
            # Machine Learning (Linear Regression)
            X = df_f[['units_sold', 'book_average_rating']]
            y = df_f['gross_sale']
            model = LinearRegression().fit(X, y)
            pred = model.predict([[in_u, in_r]])[0]
            
            st.success(f"Estimasi Gross Profit: Rp {pred:,.0f}")
            
            # AI Strategy Insight
            with st.spinner("Gemini AI sedang berpikir..."):
                model_ai = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"""
                Analisis Strategis Bacakuy:
                Genre: {selected_genre}, Target: {in_u} unit, Estimasi Profit: Rp {pred:,.0f}.
                Berikan 2 strategi pemasaran kreatif dan 1 pesan moral kejujuran dalam berdagang.
                """
                response = model_ai.generate_content(prompt)
                st.info(response.text)

    with col_graph:
        st.markdown("### Sales Performance Trend")
        # Visualisasi Tren Penjualan
        st.area_chart(df_f['gross_sale'])
        
        st.markdown("### Units Distribution")
        st.bar_chart(df_f['units_sold'])

else:
    st.error("Data gagal dimuat. Pastikan tabel 'bacakuy_sales_clean' sudah dibuat di Supabase.")
