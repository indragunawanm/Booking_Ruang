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
    df_fresh_data = load_cloud_data()
    
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
    # 3. PANEL ADMIN (EDIT LIVE - VARIABEL SUDAH DI-FIX)
    # ==============================================================================
    if st.session_state.user_role == "admin":
        st.subheader(" Panel Admin: Edit & Pembatalan Jadwal Booking")
        st.write(" *Ubah detail data langsung pada tabel di bawah untuk mengedit, lalu klik tombol **Simpan Perubahan Jadwal Admin**.*")
        
        if not df_fresh_data.empty:
            df_admin_edit = st.data_editor(
                df_fresh_data,
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
    # 4. FORM BOOKING RUANGAN (DENGAN REVISI TOTAL LOGIKA MINGGU BERJALAN)
    # ==============================================================================
    fullname_clean = str(st.session_state.fullname).replace("[", "").replace("]", "").replace("'", "").replace('"', '')
    user_dept_clean = str(st.session_state.user_dept).replace("[", "").replace("]", "").replace("'", "").replace('"', '')
    
    st.markdown(f"### Welcome, {fullname_clean.upper()}!")
    st.subheader(" Form Peminjaman Ruangan Training")
    
    with st.container(border=True):
        with st.form("form_booking", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                st.info(f" Departemen Pengunci: **{user_dept_clean.upper()}**")
                r_pilih = st.selectbox("Pilih Ruangan", list(RUANGAN.keys()))
                tanggal = st.date_input("Tanggal Pinjam", min_value=datetime.today().date())
            with col2:
                j_mulai = st.time_input("Jam Mulai", value=time(8, 0))
                j_selesai = st.time_input("Jam Selesai", value=time(9, 0))
                keperluan = st.text_area("Keperluan / Nama Training")
                
            if st.form_submit_button("Booking Sekarang"):
                hari_ini = datetime.today().date()
                tgl_str = str(tanggal)
                
                # Mengambil NOMOR MINGGU dan TAHUN dari isocalendar (Format: tuple)
                iso_ini = hari_ini.isocalendar()
                iso_booking = tanggal.isocalendar()
                
                bisa_simpan = True
                
                if not keperluan.strip():
                    st.error(" Isi keperluan atau nama training!")
                    bisa_simpan = False
                    
                if bisa_simpan and j_mulai >= j_selesai:
                    st.error(" Jam Selesai salah! Harus lebih besar dari Jam Mulai.")
                    bisa_simpan = False
                    
                # PEMBATASAN BULAN & PENGECUALIAN MINGGU BERJALAN YANG VALID
                if bisa_simpan and (tanggal.month != hari_ini.month or tanggal.year != hari_ini.year):
                    # iso[0] adalah Tahun ISO, iso[1] adalah Nomor Minggu ISO
                    if (iso_booking[1] != iso_ini[1]) or (iso_booking[0] != iso_ini[0]):
                        st.error(f" Gagal! Anda hanya diperbolehkan melakukan booking untuk bulan aktif berjalan saat ini ({calendar.month_name[hari_ini.month]} {hari_ini.year}) atau dalam minggu berjalan yang sama.")
                        bisa_simpan = False
                        
                if bisa_simpan:
                    df_db = load_cloud_data()
                    df_dept_hari = df_db[(df_db["Departemen"].astype(str).str.upper() == user_dept_clean.upper()) & (df_db["Tanggal"] == tgl_str)]
                    if not df_dept_hari.empty:
                        nama_pengunci = df_dept_hari["Nama Pemesan"].values[0]
                        st.error(f" Gagal! Departemen {user_dept_clean.upper()} sudah melakukan booking di tanggal ini. Silakan hubungi Rekan Anda: **{str(nama_pengunci).upper()}** yang sudah booking duluan!")
                        bisa_simpan = False
                        
                    if bisa_simpan:
                        df_hari = df_db[(df_db["Ruangan"] == r_pilih) & (df_db["Tanggal"] == tgl_str)]
                        bentrok = False
                        for _, row in df_hari.iterrows():
                            jam_mulai_db = str(row["Jam Mulai"]).strip()
                            jam_selesai_db = str(row["Jam Selesai"]).strip()
                            if jam_mulai_db and jam_selesai_db:
                                if not (j_selesai.strftime("%H:%M") <= jam_mulai_db or j_mulai.strftime("%H:%M") >= jam_selesai_db):
                                    bentrok = True
                                    break
                        if bentrok:
                            st.error(" Gagal! Ruangan sudah dipesan pada jam tersebut oleh departemen lain.")
                            bisa_simpan = False
                            
                if bisa_simpan:
                    new_row = pd.DataFrame([[user_dept_clean.upper(), r_pilih, tgl_str, j_mulai.strftime("%H:%M"), j_selesai.strftime("%H:%M"), keperluan, fullname_clean]], columns=["Departemen", "Ruangan", "Tanggal", "Jam Mulai", "Jam Selesai", "Keperluan", "Nama Pemesan"])
                    new_row.to_csv(CLOUD_DB, mode='a', header=False, index=False)
                    st.success(" Berhasil dipesan dan tersimpan permanen di cloud server!")
                    st.rerun()

    st.markdown("---")
    
    # ==============================================================================
    # 5. TAMPILAN KALENDER BULANAN KERJA INTERAKTIF (ANTI CRASH / AMAN)
    # ==============================================================================
    st.subheader(" Kalender Pemakaian Ruang Training (Senin - Jumat)")
    if "m" not in st.session_state: st.session_state.m = datetime.today().month
    if "y" not in st.session_state: st.session_state.y = datetime.today().year
    
    nav1, nav2, nav3 = st.columns(3)
    if nav1.button(" Bulan Lalu"):
        st.session_state.m = 12 if st.session_state.m == 1 else st.session_state.m - 1
        if st.session_state.m == 12: st.session_state.y -= 1
        st.rerun()
    if nav3.button("Bulan Depan "):
        st.session_state.m = 1 if st.session_state.m == 12 else st.session_state.m + 1
        if st.session_state.m == 1: st.session_state.y += 1
        st.rerun()
        
    nav2.markdown(f"<h3 style='text-align: center;'> 📅 {calendar.month_name[st.session_state.m]} {st.session_state.y}</h3>", unsafe_allow_html=True)
    
    html_cal = '<table style="width:100%; border-collapse: collapse; background-color: white; border: 2px solid #555;"><tr style="background-color: #e0e0e0; text-align: center; font-weight: bold;"><th style="padding: 10px; border: 2px solid #555;">Senin</th><th style="padding: 10px; border: 2px solid #555;">Selasa</th><th style="padding: 10px; border: 2px solid #555;">Rabu</th><th style="padding: 10px; border: 2px solid #555;">Kamis</th><th style="padding: 10px; border: 2px solid #555;">Jum\'at</th></tr>'
    
    df_cal = load_cloud_data()
    
    for week in calendar.Calendar(firstweekday=0).monthdayscalendar(st.session_state.y, st.session_state.m):
        if any(d != 0 for d in week[:5]):
            html_cal += "<tr style='height: 110px; vertical-align: top;'>"
            for d in week[:5]:
                if d == 0:
                    html_cal += "<td style='border: 2px solid #555; background-color: #f7f7f7;'></td>"
                else:
                    tgl_cek = f"{st.session_state.y}-{st.session_state.m:02d}-{d:02d}"
                    df_hari = df_cal[df_cal["Tanggal"] == tgl_cek]
