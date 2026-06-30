import streamlit as st
import pandas as pd
import calendar
import os
import hashlib
from datetime import datetime, time, date

# ==============================================================================
# 1. KONFIGURASI UTAMA & DATABASE CLOUD PERMANEN (FIXED ANTI REFRESH)
# ==============================================================================
RUANGAN = {"Training 1": "45 Orang", "Training 2": "15 Orang", "Training 3": "15 Orang"}
CLOUD_DB = "data_booking_cloud.csv"
USER_DB = "data_user_cloud.csv"

st.set_page_config(page_title="Booking Ruangan Cloud", layout="wide")

st.markdown(
    """
    <style>
    html, body {
        overscroll-behavior-y: contain !important;
        overscroll-behavior-x: none !important;
    }
    [data-testid="stAppViewContainer"] {
        overscroll-behavior-y: contain !important;
        overflow-y: auto !important;
        -webkit-overflow-scrolling: touch !important;
    }
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stHeader"] {background: rgba(0,0,0,0); height: 0rem;}
    </style>
    """,
    unsafe_allow_html=True
)

def hash_password(password_teks):
    return hashlib.sha256(str(password_teks).encode()).hexdigest()

if not os.path.exists(CLOUD_DB):
    pd.DataFrame(columns=["Departemen", "Ruangan", "Tanggal", "Jam Mulai", "Jam Selesai", "Keperluan", "Nama Pemesan"]).to_csv(CLOUD_DB, index=False)

if not os.path.exists(USER_DB):
    password_admin_terenkripsi = hash_password("adminbooking")
    pd.DataFrame([["ADMIN", password_admin_terenkripsi, "Admin Utama", "MANAGEMENT"]], columns=["Username", "Password", "Nama Lengkap", "Departemen"]).to_csv(USER_DB, index=False)

def load_cloud_data():
    try:
        if not os.path.exists(CLOUD_DB):
            return pd.DataFrame(columns=["Departemen", "Ruangan", "Tanggal", "Jam Mulai", "Jam Selesai", "Keperluan", "Nama Pemesan"])
        df = pd.read_csv(CLOUD_DB)
        for col in ["Departemen", "Ruangan", "Tanggal", "Jam Mulai", "Jam Selesai", "Keperluan", "Nama Pemesan"]:
            if col not in df.columns:
                df[col] = ""
        return df.fillna("")
    except:
        df_new = pd.DataFrame(columns=["Departemen", "Ruangan", "Tanggal", "Jam Mulai", "Jam Selesai", "Keperluan", "Nama Pemesan"])
        df_new.to_csv(CLOUD_DB, index=False)
        return df_new

def load_user_data():
    if not os.path.exists(USER_DB):
        password_admin_terenkripsi = hash_password("adminbooking")
        return pd.DataFrame([["ADMIN", password_admin_terenkripsi, "Admin Utama", "MANAGEMENT"]], columns=["Username", "Password", "Nama Lengkap", "Departemen"])
    return pd.read_csv(USER_DB).fillna("")

# ==============================================================================
# 2. SISTEM NAVIGASI LOGIN & DAFTAR (NATIVE SYSTEM)
# ==============================================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.username = ""
    st.session_state.fullname = ""
    st.session_state.user_dept = ""

if "page_control" not in st.session_state:
    st.session_state.page_control = "login"

if not st.session_state.logged_in:
    if st.session_state.page_control == "login":
        st.subheader("Silakan Masuk Menggunakan NIK dan Password Anda")
        with st.form("form_login"):
            u = st.text_input("Masukkan NIK Anda (Khusus Admin ketik: ADMIN)").strip()
            p = st.text_input("Masukkan Password", type="password").strip()
            
            if st.form_submit_button("Masuk Aplikasi"):
                df_user = load_user_data()
                p_hashed = hash_password(p)
                user_match = df_user[(df_user["Username"].astype(str).str.upper() == u.upper()) & (df_user["Password"].astype(str) == p_hashed)]
                
                if not user_match.empty:
                    st.session_state.logged_in = True
                    st.session_state.username = u.upper()
                    st.session_state.fullname = str(user_match["Nama Lengkap"].values[0])
                    st.session_state.user_dept = str(user_match["Departemen"].values[0])
                    st.session_state.user_role = "admin" if u.upper() == "ADMIN" else "user"
                    st.rerun()
                else:
                    st.error(" NIK atau Password yang Anda masukkan salah!")

        st.markdown("---")
        if st.button(" Klik Di Sini Untuk Daftar Akun Baru"):
            st.session_state.page_control = "daftar"
            st.rerun()
            
    elif st.session_state.page_control == "daftar":
        st.subheader("Form Pendaftaran Akun Karyawan Baru")
        with st.form("form_daftar", clear_on_submit=True):
            reg_dept = st.text_input("1. Ketik Nama Departemen / Section Anda (Misal: PPC, QA, HRCA)").strip()
            reg_name = st.text_input("2. Ketik Nama Lengkap Karyawan").strip()
            reg_nik = st.text_input("3. Ketik Nomor NIK Karyawan (Digunakan untuk Login)").strip()
            reg_p = st.text_input("4. Buat Password Baru Anda", type="password").strip()
            confirm_p = st.text_input("5. Ulangi Password Baru Anda", type="password").strip()
            
            if st.form_submit_button("Daftar Sekarang"):
                df_user = load_user_data()
                if not reg_dept or not reg_name or not reg_nik or not reg_p:
                    st.error(" Gagal! Seluruh kolom isian wajib diisi lengkap.")
                elif reg_p != confirm_p:
                    st.error(" Gagal! Konfirmasi password tidak cocok.")
                elif reg_nik.upper() in df_user["Username"].astype(str).str.upper().values:
                    st.error(f" Gagal! Nomor NIK '{reg_nik}' sudah terdaftar di sistem.")
                else:
                    reg_p_hashed = hash_password(reg_p)
                    new_user_row = pd.DataFrame([[reg_nik.upper(), reg_p_hashed, reg_name, reg_dept.upper()]], columns=["Username", "Password", "Nama Lengkap", "Departemen"])
                    new_user_row.to_csv(USER_DB, mode='a', header=False, index=False)
                    st.success(f" Registrasi Sukses! Akun NIK '{reg_nik}' berhasil dibuat.")
                    st.session_state.page_control = "login"
                    st.rerun()
                    
        st.markdown("---")
        if st.button(" Sudah Punya Akun? Kembali ke Halaman Login"):
            st.session_state.page_control = "login"
            st.rerun()

# ==============================================================================
# HALAMAN UTAMA (SETELAH BERHASIL LOGIN)
# ==============================================================================
if st.session_state.logged_in:
    df_live = load_cloud_data()
    
    st.sidebar.markdown(f"### Nama: **{st.session_state.fullname.upper()}**")
    st.sidebar.markdown(f"### NIK: **{st.session_state.username}**")
    st.sidebar.markdown(f"### Dept: **{st.session_state.user_dept.upper()}**")
    
    if st.sidebar.button(" Segarkan Kalender (Refresh)"):
        st.rerun()
        
    if st.sidebar.button(" Keluar (Logout)"):
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.session_state.username = ""
        st.session_state.fullname = ""
        st.session_state.user_dept = ""
        st.session_state.page_control = "login"
        st.rerun()
        
    st.title(" Sistem Booking Ruangan Training Cloud")
    cols = st.columns(3)
    for i, (nama, kap) in enumerate(RUANGAN.items()):
        cols[i].metric(label=nama, value=kap)
    st.markdown("---")
    
    # ==============================================================================
    # 3. PANEL ADMIN (EDIT LIVE)
    # ==============================================================================
    if st.session_state.user_role == "admin":
        st.subheader(" Panel Admin: Edit & Pembatalan Jadwal Booking")
        st.write(" *Ubah detail data langsung pada tabel di bawah untuk mengedit, lalu klik tombol **Simpan Perubahan Jadwal Admin**.*")
        
        if not df_live.empty:
            df_admin_edit = st.data_editor(
                df_live,
                hide_index=False,
                num_rows="dynamic",
                column_config={
                    "Ruangan": st.column_config.SelectboxColumn("Ruangan", options=list(RUANGAN.keys()), required=True),
                    "Tanggal": st.column_config.TextColumn("Tanggal (YYYY-MM-DD)", required=True),
                    "Jam Mulai": st.column_config.TextColumn("Jam Mulai (HH:MM)", required=True),
                    "Jam Selesai": st.column_config.TextColumn("Jam Selesai (HH:MM)", required=True),
                    "Departemen": st.column_config.TextColumn("Departemen / Section", disabled=True),
                    "Nama Pemesan": st.column_config.TextColumn("Nama Pemesan", disabled=True)
                },
                use_container_width=True,
                key="admin_live_editor"
            )
            
            if st.button(" Simpan Perubahan Jadwal Admin", use_container_width=True, type="primary"):
                df_admin_edit.to_csv(CLOUD_DB, index=False)
                st.success(" Seluruh perubahan data booking berhasil diperbarui dan disimpan!")
                st.rerun()
        else:
            st.info("Belum ada jadwal booking yang terdaftar di sistem pusat.")
        st.markdown("---")
        
    # ==============================================================================
    # 4. FORM BOOKING RUANGAN (DENGAN FIX LOGIKA DAN ANTI HILANG KALENDER)
    # ==============================================================================
    fullname_clean = str(st.session_state.fullname).replace("[", "").replace("]", "").replace("'", "").replace('"', '')
