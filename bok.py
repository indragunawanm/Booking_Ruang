import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime, time, date

# ==============================================================================
# 1. KONFIGURASI UTAMA & DATABASE CLOUD PERMANEN (FIXED ANTI REFRESH)
# ==============================================================================
RUANGAN = {"Training 1": "45 Orang", "Training 2": "15 Orang", "Training 3": "15 Orang"}
CLOUD_DB = "data_booking_v3.csv" 
USER_DB = "data_user_cloud.csv"

st.set_page_config(page_title="Booking Ruangan Cloud", layout="wide")

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
        return df.fillna("").astype(str)
    except:
        return pd.DataFrame(columns=["Departemen", "Ruangan", "Tanggal", "Jam Mulai", "Jam Selesai", "Keperluan", "Nama Pemesan"])

def load_user_data():
    return pd.read_csv(USER_DB).fillna("") if os.path.exists(USER_DB) else pd.DataFrame()

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
            u = st.text_input("Masukkan NIK Anda").strip()
            p = st.text_input("Masukkan Password", type="password").strip()
            if st.form_submit_button("Masuk Aplikasi"):
                df_user = load_user_data()
                p_hashed = hash_password(p)
                user_match = df_user[(df_user["Username"].astype(str).str.upper() == u.upper()) & (df_user["Password"].astype(str) == p_hashed)]
                if not user_match.empty:
                    st.session_state.logged_in = True
                    st.session_state.username = u.upper()
                    st.session_state.fullname = str(user_match["Nama Lengkap"].values)
                    st.session_state.user_dept = str(user_match["Departemen"].values)
                    st.session_state.user_role = "admin" if u.upper() == "ADMIN" else "user"
                    st.rerun()
                else:
                    st.error(" NIK atau Password salah!")
        if st.button("Daftar Akun Baru"):
            st.session_state.page_control = "daftar"
            st.rerun()
            
    elif st.session_state.page_control == "daftar":
        st.subheader("Form Pendaftaran Akun Karyawan Baru")
        with st.form("form_daftar", clear_on_submit=True):
            reg_dept = st.text_input("Departemen / Section (Misal: PPC, QA)").strip()
            reg_name = st.text_input("Nama Lengkap Karyawan").strip()
            reg_nik = st.text_input("Nomor NIK Karyawan").strip()
            reg_p = st.text_input("Buat Password Baru", type="password").strip()
            confirm_p = st.text_input("Ulangi Password", type="password").strip()
            if st.form_submit_button("Daftar Sekarang"):
                df_user = load_user_data()
                if not reg_dept or not reg_name or not reg_nik or not reg_p:
                    st.error(" Seluruh kolom wajib diisi!")
                elif reg_p != confirm_p:
                    st.error(" Konfirmasi password tidak cocok.")
                else:
                    new_user_row = pd.DataFrame([[reg_nik.upper(), hash_password(reg_p), reg_name, reg_dept.upper()]], columns=["Username", "Password", "Nama Lengkap", "Departemen"])
                    new_user_row.to_csv(USER_DB, mode='a', header=False, index=False)
                    st.success(" Registrasi Sukses!")
                    st.session_state.page_control = "login"
                    st.rerun()
if st.session_state.logged_in:
    df_fresh_data = load_cloud_data()
    
    # 🛠️ AMANKAN STRING METADATA: Dibersihkan total di baris paling atas sebelum dibaca form
    f_raw = str(st.session_state.fullname)
    d_raw = str(st.session_state.user_dept)
    
    fullname_clean = "INDRA GM" if "INDRA GM" in f_raw or "indra gm" in f_raw.lower() else f_raw.replace("[", "").replace("]", "").replace("'", "").replace('"', '').strip()
    user_dept_clean = "TRAINING" if "TRAINING" in d_raw or "training" in d_raw.lower() else d_raw.replace("[", "").replace("]", "").replace("'", "").replace('"', '').strip()

    st.sidebar.markdown(f"### Nama: **{fullname_clean.upper()}**")
    st.sidebar.markdown(f"### Dept: **{user_dept_clean.upper()}**")
    if st.sidebar.button("Keluar (Logout)"):
        st.session_state.logged_in = False
        st.rerun()

    st.title(" Sistem Booking Ruangan Training Cloud")
    cols = st.columns(3)
    for i, (nama, kap) in enumerate(RUANGAN.items()):
        cols[i].metric(label=nama, value=kap)
    st.markdown("---")

    # ==============================================================================
    # 4. FORM BOOKING RUANGAN (VARIABEL BERSIH DAN REVISI PENGECEKAN TANGGAL)
    # ==============================================================================
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
                
                # Filter Minggu ISO: Mengambil elemen tuple indeks 1 (Nomor Minggu) dan indeks 0 (Tahun ISO)
                iso_ini = hari_ini.isocalendar()
                iso_booking = tanggal.isocalendar()
                bisa_simpan = True

                if not keperluan.strip():
                    st.error(" Isi keperluan training!")
                    bisa_simpan = False
                if bisa_simpan and j_mulai >= j_selesai:
                    st.error(" Jam Selesai harus lebih besar dari Jam Mulai.")
                    bisa_simpan = False
                if bisa_simpan and (tanggal.month != hari_ini.month or tanggal.year != hari_ini.year):
                    if (iso_booking[1] != iso_ini[1]) or (iso_booking[0] != iso_ini[0]):
                        st.error(f" Gagal! Diizinkan hanya untuk bulan berjalan atau dalam minggu berjalan yang sama.")
                        bisa_simpan = False

                if bisa_simpan:
                    df_db = load_cloud_data()
                    df_dept_hari = df_db[(df_db["Departemen"].astype(str).str.upper() == user_dept_clean.upper()) & (df_db["Tanggal"] == tgl_str)]
                    if not df_dept_hari.empty:
                        st.error(" Departemen Anda sudah melakukan booking di tanggal ini!")
                        bisa_simpan = False
                if bisa_simpan:
                    new_row = pd.DataFrame([[user_dept_clean.upper(), r_pilih, tgl_str, j_mulai.strftime("%H:%M"), j_selesai.strftime("%H:%M"), keperluan, fullname_clean]], columns=["Departemen", "Ruangan", "Tanggal", "Jam Mulai", "Jam Selesai", "Keperluan", "Nama Pemesan"])
                    new_row.to_csv(CLOUD_DB, mode='a', header=False, index=False)
                    st.success(" Berhasil dipesan!")
                    st.rerun()

    # ==============================================================================
    # 5. TAMPILAN KALENDER METODE LIST DATA (ANTI-CRASH TOTAL)
    # ==============================================================================
    st.markdown("---")
    st.subheader(" Kalender Pemakaian Ruang Training (Senin - Jumat)")
    if "m" not in st.session_state: st.session_state.m = datetime.today().month
    if "y" not in st.session_state: st.session_state.y = datetime.today().year

    nav1, nav2, nav3 = st.columns(3)
    if nav1.button("Bulan Lalu"):
        st.session_state.m = 12 if st.session_state.m == 1 else st.session_state.m - 1
        if st.session_state.m == 12: st.session_state.y -= 1
        st.rerun()
    if nav3.button("Bulan Depan"):
        st.session_state.m = 1 if st.session_state.m == 12 else st.session_state.m + 1
        if st.session_state.m == 1: st.session_state.y += 1
        st.rerun()

    nama_bulan = ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    nav2.markdown(f"<h3 style='text-align: center;'> 📅 {nama_bulan[st.session_state.m]} {st.session_state.y}</h3>", unsafe_allow_html=True)

    html_cal = '<table style="width:100%; border-collapse: collapse; background-color: white; border: 2px solid #555;"><tr style="background-color: #e0e0e0; text-align: center; font-weight: bold;"><th style="padding: 10px; border: 2px solid #555;">Senin</th><th style="padding: 10px; border: 2px solid #555;">Selasa</th><th style="padding: 10px; border: 2px solid #555;">Rabu</th><th style="padding: 10px; border: 2px solid #555;">Kamis</th><th style="padding: 10px; border: 2px solid #555;">Jum\'at</th></tr>'
    
    df_cal = load_cloud_data()
    raw_records = df_cal.to_dict(orient="records") if not df_cal.empty else []
    html_cal += "<tr style='height: 110px; vertical-align: top;'> "
    kolom_hari = 0
    
    for d in range(1, 32):
        try:
            valid_date = date(st.session_state.y, st.session_state.m, d)
            nama_hari_ke = valid_date.weekday()
            if nama_hari_ke > 4:
                continue
            tgl_cek = f"{st.session_state.y}-{st.session_state.m:02d}-{d:02d}"
            list_hari = [row for row in raw_records if str(row.get("Tanggal", "")).strip() == tgl_cek]
            bg = "#fff3e0" if len(list_hari) > 0 else "#ffffff"
            info = ""
            for r in list_hari:
                info += f"<div style='font-size: 11px; margin-top: 4px; background-color: #ffe0b2; color: #e65100; padding: 3px; border-radius:3px; border: 1px solid #ffcc80;'>• <b>{r.get('Jam Mulai')}</b> [{r.get('Ruangan')}] {str(r.get('Departemen')).upper()}</div>"
            html_cal += f'<td style="border: 2px solid #555; background-color: {bg}; padding: 6px; color:#000000; width: 20%;"><b>{d}</b>{info}</td>'
            kolom_hari += 1
            if kolom_hari == 5:
                html_cal += "</tr><tr style='height: 110px; vertical-align: top;'>"
                kolom_hari = 0
        except:
            break
            
    html_cal += "</tr></table>"
    st.markdown(html_cal, unsafe_allow_html=True)
