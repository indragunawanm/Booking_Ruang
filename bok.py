import streamlit as st
import pandas as pd
import hashlib
from datetime import datetime, time, date
from streamlit_gsheets import GSheetsConnection

# ==============================================================================
# 1. KONFIGURASI UTAMA & DATABASE CLOUD GOOGLE SHEETS
# ==============================================================================
RUANGAN = {"Training 1": "45 Orang", "Training 2": "15 Orang", "Training 3": "15 Orang"}

st.set_page_config(page_title="Booking Ruangan Cloud", layout="wide")

# Menggunakan fitur bawaan resmi Streamlit untuk terhubung langsung ke Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def hash_password(password_teks):
    """Mengubah password teks biasa menjadi kode enkripsi SHA-256 aman"""
    return hashlib.sha256(str(password_teks).encode()).hexdigest()

def load_cloud_data():
    """Membaca daftar booking ruangan dari Google Sheets secara real-time"""
    try:
        df = conn.read(worksheet="data_booking_v3", ttl=0)
        return df.fillna("").astype(str)
    except:
        return pd.DataFrame(columns=["Departemen", "Ruangan", "Tanggal", "Jam Mulai", "Jam Selesai", "Keperluan", "Nama Pemesan"])

def load_user_data():
    """Membaca data akun pengguna dari Google Sheets secara real-time"""
    try:
        df = conn.read(worksheet="data_user_cloud", ttl=0)
        return df.fillna("").astype(str)
    except:
        return pd.DataFrame(columns=["Username", "Password", "Nama Lengkap", "Departemen"])

# Initialize state management aplikasi agar anti-looping
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "page_control" not in st.session_state:
    st.session_state.page_control = "login"

# ==============================================================================
# 2. ALUR ANTARMUKA PENGGUNA (INTERFACE CONTROL)
# ==============================================================================
if not st.session_state.logged_in:
    # --------------------------------------------------------------------------
    # HALAMAN LOGIN UTAMA
    # --------------------------------------------------------------------------
    if st.session_state.page_control == "login":
        st.subheader("Silakan Masuk Menggunakan NIK dan Password Anda")
        
        with st.form("form_masuk_akun_utama"):
            u = st.text_input("Masukkan NIK Anda").strip()
            p = st.text_input("Masukkan Password", type="password").strip()
            tombol_masuk = st.form_submit_button("Masuk Aplikasi")
            
            if tombol_masuk:
                if u and p:
                    df_user = load_user_data()
                    p_hashed = hash_password(p)
                    
                    user_match = df_user[(df_user["Username"].str.upper() == u.upper()) & (df_user["Password"] == p_hashed)]
                    
                    if not user_match.empty:
                        st.session_state.logged_in = True
                        st.session_state.username = u.upper()
                        st.session_state.fullname = str(user_match["Nama Lengkap"].values)
                        st.session_state.user_dept = str(user_match["Departemen"].values)
                        st.session_state.user_role = "admin" if u.upper() == "ADMIN" else "user"
                        st.success(f"Selamat Datang, {st.session_state.fullname}!")
                        st.rerun()
                    else:
                        st.error("NIK atau Password salah! Silakan coba lagi.")
                else:
                    st.warning("Mohon isi seluruh kolom login terlebih dahulu.")
        
        st.write("---")
        if st.button("Daftar Akun Baru", key="tombol_pindah_ke_registrasi"):
            st.session_state.page_control = "daftar"
            st.rerun()

    # --------------------------------------------------------------------------
    # HALAMAN DAFTAR AKUN BARU (DEPARTEMEN KETIK SENDIRI)
    # --------------------------------------------------------------------------
    elif st.session_state.page_control == "daftar":
        st.subheader("Formulir Registrasi Pengguna Baru")
        
        with st.form("form_pendaftaran_user_baru"):
            reg_nik = st.text_input("Masukkan NIK Baru").strip()
            reg_name = st.text_input("Masukkan Nama Lengkap Anda").strip()
            reg_dept = st.text_input("Masukkan Departemen/Section Anda").strip()
            reg_p = st.text_input("Buat Password Anda", type="password").strip()
            reg_p_confirm = st.text_input("Konfirmasi Password Anda", type="password").strip()
            
            tombol_daftar = st.form_submit_button("Daftar Sekarang")
            
            if tombol_daftar:
                if reg_nik and reg_name and reg_dept and reg_p and reg_p_confirm:
                    if reg_p != reg_p_confirm:
                        st.error("Konfirmasi password tidak cocok!")
                    else:
                        df_user_lama = load_user_data()
                        if not df_user_lama.empty and reg_nik.upper() in df_user_lama["Username"].str.upper().values:
                            st.error("NIK tersebut sudah terdaftar di sistem!")
                        else:
                            new_user_row = pd.DataFrame([[reg_nik.upper(), hash_password(reg_p), reg_name, reg_dept.upper()]], 
                                                        columns=["Username", "Password", "Nama Lengkap", "Departemen"])
                            df_user_baru = pd.concat([df_user_lama, new_user_row], ignore_index=True)
                            conn.update(worksheet="data_user_cloud", data=df_user_baru)
                            
                            st.success("Registrasi Berhasil! Silakan masuk kembali.")
                            st.session_state.page_control = "login"
                            st.rerun()
                else:
                    st.warning("Semua kolom registrasi wajib diisi!")
        
        st.write("---")
        if st.button("Kembali ke Menu Login", key="tombol_kembali_ke_login"):
            st.session_state.page_control = "login"
            st.rerun()
else:
    # ==============================================================================
    # 3. HALAMAN UTAMA APLIKASI (SETELAH BERHASIL LOGIN)
    # ==============================================================================
    fullname_clean = str(st.session_state.fullname).replace("['", "").replace("']", "")
    user_dept_clean = str(st.session_state.user_dept).replace("['", "").replace("']", "")
    
    # Membuat 2 kolom layout utama (Kiri: Form Input, Kanan: Informasi Status)
    k_kiri, k_kanan = st.columns(2)
    
    with k_kiri:
        st.markdown(f"### 👤 Logged in as: **{fullname_clean}** ({st.session_state.user_role.upper()})")
        st.markdown(f"🏢 Dept: **{user_dept_clean}**")
        
        st.subheader("Formulir Pemesanan Ruangan")
        with st.form("form_pemesanan_ruangan_cloud_gsheets"):
            r_pilih = st.selectbox("Pilih Ruangan yang Akan Digunakan", list(RUANGAN.keys()))
            tgl_pilih = st.date_input("Pilih Tanggal Acara", min_value=date.today())
            j_mulai = st.time_input("Jam Mulai Penggunaan", time(8, 0))
            j_selesai = st.time_input("Jam Selesai Penggunaan", time(17, 0))
            keperluan = st.text_area("Tuliskan Keperluan/Nama Agenda Acara").strip()
            
            tombol_booking = st.form_submit_button("Kirim Formulir Pemesanan")
            
            if tombol_booking:
                if keperluan:
                    if j_mulai >= j_selesai:
                        st.error("Waktu mulai tidak boleh sama dengan atau melampaui waktu selesai!")
                    else:
                        tgl_str = tgl_pilih.strftime("%Y-%m-%d")
                        df_booking = load_cloud_data()
                        
                        if not df_booking.empty and "Ruangan" in df_booking.columns:
                            df_hari_ini = df_booking[(df_booking["Ruangan"] == r_pilih) & (df_booking["Tanggal"] == tgl_str)]
                        else:
                            df_hari_ini = pd.DataFrame()
                        
                        bisa_simpan = True
                        for _, baris in df_hari_ini.iterrows():
                            b_mulai = datetime.strptime(baris["Jam Mulai"], "%H:%M").time()
                            b_selesai = datetime.strptime(baris["Jam Selesai"], "%H:%M").time()
                            
                            # Logika validasi tabrakan jam
                            if not (j_selesai <= b_mulai or j_mulai >= b_selesai):
                                bisa_simpan = False
                                st.error(f"❌ JADWAL BENTROK! Di-booking oleh Dept. {baris['Departemen']} (Jam {baris['Jam Mulai']} - {baris['Jam Selesai']})")
                                break
                        
                        if bisa_simpan:
                            new_row = pd.DataFrame([[
                                user_dept_clean.upper(), r_pilih, tgl_str, 
                                j_mulai.strftime("%H:%M"), j_selesai.strftime("%H:%M"), 
                                keperluan, fullname_clean
                            ]], columns=["Departemen", "Ruangan", "Tanggal", "Jam Mulai", "Jam Selesai", "Keperluan", "Nama Pemesan"])
                            
                            df_booking_baru = pd.concat([df_booking, new_row], ignore_index=True)
                            conn.update(worksheet="data_booking_v3", data=df_booking_baru)
                            
                            st.success("🎉 Ruangan Berhasil Dipesan!")
                            st.rerun()
                else:
                    st.warning("Mohon tuliskan keperluan agenda acara Anda.")
        
        st.write("")
        if st.button("🚪 Keluar Aplikasi (Logout)", key="tombol_logout_sistem_gsheets"):
            st.session_state.logged_in = False
            st.session_state.page_control = "login"
            st.rerun()

    with k_kanan:
        st.subheader("📅 Jadwal Penggunaan Ruangan Terkini")
        
        if st.button("🔄 Segarkan Data (Refresh)", key="tombol_refresh_tabel_gsheets"):
            st.rerun()
            
        df_display = load_cloud_data()
        
        if df_display.empty or len(df_display) == 0:
            st.info("Belum ada jadwal pemesanan ruangan terdaftar saat ini.")
        else:
            try:
                df_display = df_display.sort_values(by=["Tanggal", "Jam Mulai"], ascending=[True, True])
            except:
                pass
                
            # Filter Menu Admin untuk Menghapus Data Pemesanan
            if st.session_state.user_role == "admin":
                st.markdown("---")
                st.markdown("### 🛠️ Menu Manajemen Admin")
                
                opsi_hapus = [f"[{idx}] {row['Tanggal']} | {row['Ruangan']} ({row['Jam Mulai']}-{row['Jam Selesai']}) - {row['Departemen']}" for idx, row in df_display.iterrows()]
                pilihan_hapus = st.selectbox("Pilih Jadwal yang Ingin Dibatalkan/Dihapus", ["-- Pilih Jadwal --"] + opsi_hapus)
                
                if st.button("🔥 Batalkan & Hapus Pesanan", key="tombol_hapus_admin_gsheets"):
                    if pilihan_hapus != "-- Pilih Jadwal --":
                        idx_asli = int(pilihan_hapus.split("]").replace("[", ""))
                        df_display_baru = df_display.drop(idx_asli).reset_index(drop=True)
                        conn.update(worksheet="data_booking_v3", data=df_display_baru)
                        st.success("🗑️ Jadwal pemesanan berhasil dihapus!")
                        st.rerun()
            
            st.dataframe(df_display, use_container_width=True, hide_index=True)
