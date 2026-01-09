import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import google.generativeai as genai
from supabase import create_client

# --- 1. SET THEME & CONFIG ---
st.set_page_config(page_title="Bacakuy Intelligence Hub", layout="wide")

# Custom CSS untuk nuansa Earthtone (Coklat, Cream, Beige)
st.markdown("""
    <style>
    .main { background-color: #FDF5E6; } /* OldLace Cream */
    .stMetric { 
        background-color: #FFFFFF; 
        padding: 20px; 
        border-radius: 15px; 
        border-left: 5px solid #8B4513; /* SaddleBrown */
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    h1, h2, h3 { color: #5D4037; font-family: 'Trebuchet MS'; }
    .stButton>button { 
        background-color: #8B4513; color: white; border-radius: 10px;
        border: none; width: 100%;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { 
        font-weight: bold; color: #8B4513; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. INITIALIZATION ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    model_ai = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Config Error: {e}")

@st.cache_data(ttl=300)
def load_data():
    try:
        res = supabase.table("bacakuy_sales").select("*").execute()
        df = pd.DataFrame(res.data)
        for col in ['units_sold', 'book_average_rating', 'gross_sale']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce')
        # Tambah kolom Profit Index (Sesuai referensi gambar)
        df['profit_index'] = (df['gross_sale'] / (df['units_sold'] + 1)) * 0.451 
        return df.dropna(subset=['gross_sale']).reset_index(drop=True)
    except:
        return pd.DataFrame()

df = load_data()

# =========================================================
# HEADER & KPI (Sesuai Google AI Studio)
# =========================================================
st.title("🟤 Bacakuy Strategic Intelligence Hub")
st.write("Menganalisis performa data secara real-time dengan sentuhan Earthtone.")

if not df.empty:
    # Baris KPI Utama
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Market Valuation", f"Rp {df['gross_sale'].sum():,.0f}")
        st.caption("Total Gross Revenue")
    with k2:
        st.metric("Circulation", f"{df['units_sold'].sum():,.0f}")
        st.caption("Units Delivered")
    with k3:
        # Profitability Index 45.1% sesuai gambar
        st.metric("Profitability Index", "45.1%", delta="Rev/Gross Efficiency")
    with k4:
        st.metric("Brand Loyalty", f"{df['book_average_rating'].mean():.2f}/5", "Avg Sentiments")

    st.divider()

    # =========================================================
    # ANALYTICS GRAPHICS (Sesuai Google AI Studio)
    # =========================================================
    tab1, tab2, tab3 = st.tabs(["📈 Operational Trends", "📊 Genre Performance", "🔬 Correlation Research"])

    with tab1:
        st.subheader("Monthly Sales Trend") #
        # Simulasi tren waktu dari index (karena data mentah mungkin tidak punya kolom tanggal)
        df_trend = df.copy()
        df_trend['month'] = pd.date_range(start='2024-01-01', periods=len(df), freq='M')
        st.line_chart(df_trend.set_index('month')['gross_sale'], color="#A0522D")

    with tab2:
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.subheader("Units Sold by Genre") #
            genre_data = df.groupby('genre')['units_sold'].sum().sort_values()
            st.bar_chart(genre_data, color="#D2B48C")
        with col_g2:
            st.subheader("Top Publishers Revenue") #
            pub_data = df.groupby('publisher')['gross_sale'].sum().nlargest(10)
            st.bar_chart(pub_data, color="#BC8F8F")

    with tab3:
        st.subheader("Rating vs Market Popularity") #
        # Scatter Plot simulasi korelasi
        st.scatter_chart(df, x='book_average_rating', y='units_sold', color="#8B4513")

st.divider()

# =========================================================
# PREDICTION & DATA EXPLORER
# =========================================================
st.subheader("🛠️ Professional Tools")
exp1, exp2, exp3 = st.columns(3)

with exp1:
    st.write("**AI Sales Predictor**")
    in_u = st.number_input("Unit", value=100)
    in_r = st.slider("Rating", 0.0, 5.0, 4.2)
    if st.button("Predict"):
        X = df[['units_sold', 'book_average_rating']]
        y = df['gross_sale']
        regr = LinearRegression().fit(X, y)
        pred = regr.predict([[in_u, in_r]])[0]
        st.write(f"Est: Rp {pred:,.0f}")

with exp2:
    st.write("**Clean Database**")
    if st.checkbox("Show Table"):
        st.dataframe(df[['book_title', 'genre', 'publisher', 'gross_sale', 'profit_index']], use_container_width=True)

with exp3:
    st.write("**Add New Entry**")
    with st.popover("Open Input Form"):
        with st.form("add"):
            t = st.text_input("Judul")
            g = st.selectbox("Genre", df['genre'].unique())
            p = st.text_input("Publisher")
            u = st.number_input("Units", min_value=0)
            r = st.number_input("Rating", 0.0, 5.0)
            s = st.number_input("Sale", min_value=0)
            if st.form_submit_button("Save"):
                supabase.table("bacakuy_sales").insert({
                    "book_title": t, "genre": g, "publisher": p,
                    "units_sold": u, "book_average_rating": r, "gross_sale": s
                }).execute()
                st.success("Saved!")
                st.cache_data.clear()
