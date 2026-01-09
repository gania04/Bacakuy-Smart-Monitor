import streamlit as st
import pandas as pd
# Pastikan library supabase sudah diimport di atas

# --- 1. AMBIL DATA DARI SUPABASE (Harus di atas agar df_raw terdefinisi) ---
try:
    response = supabase.table("bacakuy_sales").select("*").execute()
    df_raw = pd.DataFrame(response.data)
except Exception as e:
    df_raw = pd.DataFrame() # Jika gagal, buat dataframe kosong agar tidak error
    st.error(f"Gagal mengambil data: {e}")

# --- 2. LOGIKA PERHITUNGAN JUMLAH DATA ---
# Sekarang df_raw sudah ada, jadi baris ini tidak akan NameError lagi
total_records = len(df_raw) if not df_raw.empty else 0

# --- 3. TAMPILAN KARTU INFORMASI (DI ATAS FORM) ---
st.markdown(f"""
    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 12px; border: 1px solid #e9ecef; width: fit-content; margin-bottom: 20px;">
        <p style="color: #6366f1; font-size: 0.8rem; font-weight: bold; margin-bottom: 5px; letter-spacing: 0.05em;">SUPABASE RECORDS</p>
        <h1 style="margin: 0; color: #1e1b4b; font-size: 2.2rem;">{total_records:,}</h1>
        <p style="color: #6b7280; font-size: 0.75rem; margin-top: 5px; font-style: italic;">Table: bacakuy_sales</p>
    </div>
""", unsafe_allow_html=True)

# --- 4. KODE FORM ASLI ANDA ---
show_data = st.checkbox("Show Table", value=False)
if show_data:
    st.dataframe(df_raw, use_container_width=True)

# ... (Sisa kode tab_add dan form tetap sama seperti sebelumnya)
