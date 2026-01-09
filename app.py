import streamlit as st
import pandas as pd

# --- 1. LOGIKA PERHITUNGAN JUMLAH DATA (SUPABASE RECORDS) ---
# Mengambil jumlah total baris data dari dataframe
total_records = len(df_raw) if not df_raw.empty else 0

# --- 2. TAMPILAN KARTU INFORMASI (MIRIP SCREENSHOT) ---
# Bagian ini akan menampilkan angka jumlah tabel seperti 1047
st.markdown(f"""
    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 12px; border: 1px solid #e9ecef; width: 250px; margin-bottom: 20px;">
        <p style="color: #6366f1; font-size: 0.8rem; font-weight: bold; margin-bottom: 5px; letter-spacing: 0.05em;">SUPABASE RECORDS</p>
        <h1 style="margin: 0; color: #1e1b4b; font-size: 2.2rem;">{total_records:,}</h1>
        <p style="color: #6b7280; font-size: 0.75rem; margin-top: 5px; font-style: italic;">Table: bacakuy_sales</p>
    </div>
""", unsafe_allow_html=True)

# --- 3. KODE ASLI ANDA (TANPA DIUBAH) ---
show_data = st.checkbox("Show Table", value=False)
if show_data:
    st.dataframe(df_raw, use_container_width=True)

with tab_add:
    with st.form("add_form"):
        c1, c2 = st.columns(2)
        with c1:
            nt = st.text_input("Judul Buku")
            na = st.text_input("Author")
            # Menghindari error jika dataframe kosong
            genre_list = sorted(df_raw['genre'].unique()) if not df_raw.empty else ["Fiction"]
            ng = st.selectbox("Genre", genre_list)
            np = st.text_input("Publisher")
        with c2:
            nu = st.number_input("Units Sold", min_value=0)
            n_price = st.number_input("Sale Price ($)", min_value=0.0)
            nr = st.number_input("Rating", 0.0, 5.0)
            ntgl = st.date_input("Tanggal")
        
        calc_gross = nu * n_price
        st.info(f"Gross Sale Otomatis: $ {calc_gross:,.2f}")

        if st.form_submit_button("Simpan Data"):
            # Proses insert ke tabel bacakuy_sales
            supabase.table("bacakuy_sales").insert({
                "book_title": nt, 
                "author": na, 
                "genre": ng, 
                "publisher": np,
                "units_sold": nu, 
                "book_average_rating": nr, 
                "gross_sale": calc_gross, 
                "tanggal_transaksi": str(ntgl)
            }).execute()
            
            st.success("Data Tersimpan!")
            # Membersihkan cache agar jumlah records langsung terupdate
            st.cache_data.clear()
            st.rerun()
