import streamlit as st
import pandas as pd
from sklearn.linear_model import LinearRegression
import google.generativeai as genai
from supabase import create_client

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Bacakuy Smart Monitor PRO", layout="wide")

# --- 2. KREDENSIAL DARI SECRETS ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    model_ai = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Gagal memuat konfigurasi: {e}")

# Fungsi Tarik Data
def load_data():
    try:
        res = supabase.table("bacakuy_sales").select("*").execute()
        df = pd.DataFrame(res.data)
        cols_to_fix = ['units_sold', 'book_average_rating', 'gross_sale']
        for col in cols_to_fix:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce')
        return df.dropna(subset=['gross_sale']).reset_index(drop=True)
    except Exception as e:
        return pd.DataFrame()

df = load_data()

# =========================================================
# BAGIAN 1: KALKULATOR PREDIKSI & AI
# =========================================================
st.title("📑 Bacakuy Sales Prediction & AI Analysis")
col_in, col_res = st.columns([1, 2])

with col_in:
    st.subheader("🔍 Kalkulator Prediksi")
    in_units = st.number_input("Target Unit Terjual", min_value=1, value=100)
    in_rating = st.slider("Target Rating Buku", 0.0, 5.0, 4.20)
    predict_btn = st.button("Hitung Prediksi & Insight AI", use_container_width=True)

with col_res:
    if predict_btn and not df.empty:
        X = df[['units_sold', 'book_average_rating']]
        y = df['gross_sale']
        regr = LinearRegression().fit(X, y)
        prediction = regr.predict([[in_units, in_rating]])[0]
        st.metric("Estimasi Gross Sales (IDR)", f"Rp {prediction:,.2f}")
        
        with st.spinner("Menghubungkan ke AI Studio..."):
            try:
                response = model_ai.generate_content(f"Berikan 1 strategi marketing syariah untuk target profit Rp {prediction:,.0f}")
                st.success(response.text)
            except:
                st.warning("Insight AI sedang tidak tersedia.")
    else:
        st.info("Gunakan kalkulator untuk simulasi pendapatan.")

st.divider()

# =========================================================
# BAGIAN 2: STRATEGIC HUB & VISUALISASI
# =========================================================
st.title("🚀 Strategic Intelligence Hub")
if not df.empty:
    c1, c2 = st.columns(2)
    with c1:
        sel_genre = st.selectbox("Pilih Kategori Buku:", ["Semua Kategori"] + sorted(list(df['genre'].unique())))
    with c2:
        sel_pub = st.selectbox("Pilih Publisher:", ["Semua Publisher"] + sorted(list(df['publisher'].unique())))

    df_f = df.copy()
    if sel_genre != "Semua Kategori": df_f = df_f[df_f['genre'] == sel_genre]
    if sel_pub != "Semua Publisher": df_f = df_f[df_f['publisher'] == sel_pub]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Market Valuation", f"Rp {df_f['gross_sale'].sum():,.0f}")
    m2.metric("Total Units", f"{df_f['units_sold'].sum():,.0f}")
    m3.metric("Avg Rating", f"{df_f['book_average_rating'].mean():.2f}")
    m4.metric("Status", "Live Sync")

    st.area_chart(df_f.set_index(df_f.index)['gross_sale'])

st.divider()

# =========================================================
# BAGIAN 3: DATA EXPLORER & TAMBAH DATA (SUPABASE)
# =========================================================
t1, t2 = st.tabs(["📊 Database View", "➕ Tambah Data Baru"])

with t1:
    st.subheader("Data Bersih Supabase")
    st.dataframe(df, use_container_width=True) # Tabel data clean

with t2:
    st.subheader("Input Data Penjualan Baru")
    with st.form("form_tambah_data"):
        col1, col2 = st.columns(2)
        with col1:
            new_title = st.text_input("Judul Buku")
            new_genre = st.selectbox("Genre", sorted(list(df['genre'].unique())))
            new_pub = st.text_input("Publisher")
        with col2:
            new_units = st.number_input("Units Sold", min_value=0)
            new_rating = st.number_input("Rating", min_value=0.0, max_value=5.0, step=0.1)
            new_sale = st.number_input("Gross Sale (IDR)", min_value=0)
        
        submitted = st.form_submit_button("Simpan ke Supabase")
        
        if submitted:
            new_data = {
                "book_title": new_title,
                "genre": new_genre,
                "publisher": new_pub,
                "units_sold": new_units,
                "book_average_rating": new_rating,
                "gross_sale": new_sale
            }
            try:
                supabase.table("bacakuy_sales").insert(new_data).execute()
                st.success("Data Berhasil Disimpan! Silakan Refresh halaman.")
                st.cache_data.clear() # Membersihkan cache agar data baru muncul
            except Exception as e:
                st.error(f"Gagal menyimpan data: {e}")
