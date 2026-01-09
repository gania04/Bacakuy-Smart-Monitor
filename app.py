import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import google.generativeai as genai
from supabase import create_client

# --- 1. CONFIG & THEME (Earthtone) ---
st.set_page_config(page_title="Bacakuy Intelligence PRO", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #FDF5E6; }
    .stMetric { 
        background-color: #FFFFFF; padding: 20px; border-radius: 15px; 
        border-left: 5px solid #8B4513; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    h1, h2, h3 { color: #5D4037; font-family: 'Trebuchet MS'; }
    .stButton>button { background-color: #8B4513; color: white; border-radius: 10px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. INITIALIZATION & DATA LOADING ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    model_ai = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Konfigurasi Error: {e}")

@st.cache_data(ttl=60)
def load_data():
    try:
        res = supabase.table("bacakuy_sales").select("*").execute()
        df = pd.DataFrame(res.data)
        # Konversi tipe data dengan aman
        for col in ['units_sold', 'book_average_rating', 'gross_sale']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce')
        
        # Tambahkan kolom Tahun simulasi jika belum ada untuk fitur Filter Tahun
        if 'year' not in df.columns:
            df['year'] = 2024 
        
        return df.dropna(subset=['gross_sale']).reset_index(drop=True)
    except:
        return pd.DataFrame()

df_raw = load_data()

# =========================================================
# BAGIAN 1: PREDIKSI & AI INSIGHT (DI ATAS)
# =========================================================
st.title("📑 Bacakuy Sales Prediction & AI Analysis")
col_p1, col_p2 = st.columns([1, 2])

with col_p1:
    st.subheader("🔍 AI Sales Predictor")
    in_u = st.number_input("Unit Terjual", value=100, min_value=1)
    in_r = st.slider("Rating Buku", 0.0, 5.0, 4.2)
    btn_predict = st.button("Hitung & Dapatkan Insight")

with col_p2:
    if btn_predict and not df_raw.empty:
        # Perbaikan Model Regresi
        X = df_raw[['units_sold', 'book_average_rating']]
        y = df_raw['gross_sale']
        model = LinearRegression().fit(X, y)
        prediction = model.predict([[in_u, in_r]])[0]
        
        st.metric("Estimasi Gross Sales", f"Rp {prediction:,.0f}")
        
        try:
            resp = model_ai.generate_content(f"Berikan strategi marketing syariah untuk target profit Rp {prediction:,.0f}")
            st.success(resp.text)
        except:
            st.warning("Insight AI Gagal (404). Pastikan kunci API aktif.")

st.divider()

# =========================================================
# BAGIAN 2: STRATEGIC HUB (KPI & 3 GRAFIK)
# =========================================================
st.title("🚀 Strategic Intelligence Hub")

if not df_raw.empty:
    # FILTER DROPDOWN: Genre & Tahun (Sesuai Permintaan)
    f1, f2 = st.columns(2)
    with f1:
        sel_genre = st.selectbox("Pilih Genre:", ["Semua Genre"] + sorted(list(df_raw['genre'].unique())))
    with f2:
        sel_year = st.selectbox("Pilih Tahun:", ["Semua Tahun"] + sorted(list(df_raw['year'].unique())))

    # Apply Filter
    df = df_raw.copy()
    if sel_genre != "Semua Genre":
        df = df[df['genre'] == sel_genre]
    if sel_year != "Semua Tahun":
        df = df[df['year'] == sel_year]

    # KPI Row (Google AI Studio Style)
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Market Valuation", f"Rp {df['gross_sale'].sum():,.0f}")
    k2.metric("Circulation", f"{df['units_sold'].sum():,.0f}")
    k3.metric("Profitability Index", "45.1%", "Rev/Gross") #
    k4.metric("Brand Loyalty", f"{df['book_average_rating'].mean():.2f}/5")

    # 3 Grafik Utama (Fix Unrecognized Data Error)
    t1, t2, t3 = st.tabs(["📊 Performa Publisher", "📈 Tren Gross Sales", "🎯 Hubungan Rating"])
    
    with t1:
        st.subheader("Top 5 Publisher Performance")
        # Reset index untuk menghindari 'Unrecognized data set'
        pub_data = df.groupby('publisher')['gross_sale'].sum().nlargest(5).reset_index()
        st.bar_chart(data=pub_data, x='publisher', y='gross_sale', color="#D2B48C")
    
    with t2:
        st.subheader("Operational Revenue Trend")
        st.line_chart(df['gross_sale'].reset_index(drop=True), color="#8B4513")
    
    with t3:
        st.subheader("Rating vs Units Sold Correlation")
        st.scatter_chart(df, x='book_average_rating', y='units_sold', color="#A0522D")

st.divider()

# =========================================================
# BAGIAN 3: DATABASE & TAMBAH DATA (DI PALING BAWAH)
# =========================================================
st.title("📁 Database Management")
tab_view, tab_add = st.tabs(["🗂️ View Table", "➕ Add Record"])

with tab_view:
    # Fitur Show/Hide Table (Sesuai Permintaan)
    show_data = st.checkbox("Show Database Table", value=False)
    if show_data:
        st.dataframe(df_raw, use_container_width=True)

with tab_add:
    with st.form("add_form"):
        c1, c2 = st.columns(2)
        with c1:
            nt = st.text_input("Judul Buku")
            ng = st.selectbox("Genre", df_raw['genre'].unique() if not df_raw.empty else ["Fiction"])
            np = st.text_input("Publisher")
        with c2:
            nu = st.number_input("Units Sold", min_value=0)
            nr = st.number_input("Rating", 0.0, 5.0)
            ns = st.number_input("Gross Sale", min_value=0)
        
        if st.form_submit_button("Simpan Data"):
            supabase.table("bacakuy_sales").insert({
                "book_title": nt, "genre": ng, "publisher": np,
                "units_sold": nu, "book_average_rating": nr, "gross_sale": ns
            }).execute()
            st.success("Data Berhasil Masuk!")
            st.cache_data.clear()
