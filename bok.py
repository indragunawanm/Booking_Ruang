import streamlit as st
import pandas as pd
import hashlib
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, time, date

# ==============================================================================
# 1. KONFIGURASI UTAMA & KONEKSI SECURE DATABASE GSPREAD
# ==============================================================================
RUANGAN = {"Training 1": "45 Orang", "Training 2": "15 Orang", "Training 3": "15 Orang"}

st.set_page_config(page_title="Booking Ruangan Cloud", layout="wide")

# Menginisialisasi koneksi gspread dengan metode injeksi kunci langsung
scope = ["https://googleapis.com", "https://googleapis.com"]

# Menggabungkan data info Secrets dasar dengan kunci privat dari internal teks
info_kredensial = dict(st.secrets["gspread"])

# Masukkan seluruh kunci panjang asli Anda dari baris 5 VS Code ke dalam tanda kutip di bawah ini:
info_kredensial["private_key"] = "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDFle1TXkz1h2we\nVyBvzUD9BRrZd5dwGH30pD2IlxvrsI6wKEmOniEdpNbkBdHfjMsw3ktm8TNTjnKq\n0FbZZpDWpktngLnYvUZUBk9Kjs8TxsViU5DjRf68WZUojAIXEQLHs4DtI5w9SpSg\nFuQXwDEk0IPJnvBMuwuI/4HawjuOXf1a4YfhyRK0jqgvtLraOorVb4EmvRG1ZdFL\n/CK3yaTRDHKAoXFFX32e3QYrqXTkwwrYbzGrrb7ROUpQPLfELUlOz0SOMgmDowYy\nlG9KgbJkD0lOay1wBmDrQ5ONZACjkw9Au8VgsFReBxx0zPowkmX2Hn68OyuDfug2\nqJuwA1vtAgMBAAECggEAAII+EfKidphibCKTzA3mfrBKbShsbKa3fk+E9ArVkNIL\n0ALOi643Dh08S2qDa5Swej/8SDfTRsINZAi0zIsB0PetJodTky4LlhBNGHdNK7Md\nk379FsS5nvEJHAleQQJzdCGvcYzfrF26i737WN9PERXzXOvKmRv7L99ejXpmDlwI\n7kW4eYX1Hq+2ZTOrzAIx70EOLtWrqZz7eDavunNFJRvY0hdX2b2A6hgLn0MK2Ezs\n7Z2seTtT84gw2Hkgy3hLH7JWaLaj3ZuVgZcqtRzuWafQC2mwa+oyEzCSgxsge455\nC2ZcivhWZHFj1Kqf0pgyzIrR3doPuQ/cZDCmQUD4iQKBgQD8LfDzgqd2oY4BhYW+\nUhYinVAUVM50HV2MsPieoAH1GQn4YqXwHEBdPOMgqK3JER8y08l5Jc8KhoYM2pfY\ncqyxxCgQWHkqcx87a3Po7GhLKmOIiXdpwt3sDVsrCp6mYht3lgp9aFNXjfxxhAth\nvWVRvn/GEpTWkZvuPcLpn0fo+QKBgQDIlD94UNKBr+QVKMFh5pcHldCidl+jnF0Y\nsYhYRUslF/l7WUcQxfoai8FwO8/k9Dmu/s3JWo5nIqmQpdmP544aZq6g+tzH7tZM\nOENYDXxyF6tzDu60ukEftRqLIdlRoj7t86cgyGD9JVNzGor/p9x1Ul4BmXNl0woc\naFZrSmqblQKBgQDwbZCjafbliOPOGZJIwRRvjhJyP+TSGck+QN/YxG75UhUKZmsU\nwKqw+kMFuSxvXc6j8/3Lbju2KkmV6bcJ21NA7ObRprhmu3mUej75XKOWvmRFIeLi\nx7IzwwwfvjFCKplLa5a2uAd1m16Kj70WQ69cv0Ys/zw+UncbLnEtsfmqaQKBgQC7\nhp6whh/JUAEWJzxlo4igdtjQi4tvE8mWRKUMofxXecquIBHpBK+IEhGQNNtxW0Ry\n75bGIfvxQN73dZeqivq4hDfQGbpA0nNYX2HW+QTYRnjs4ZEbNuecFV3zpnnfcKkV\nHy+p3q2O/0691psN2oqqxY9OP4E8OcrCNGpXdQOm4QKBgFgxZLnt89ew2wx82Nge\nkpl+zqhiXrpApOQwN5DwcObi0jYpqU5J1kzXX1KjtNL6NZLtudoIhHBhYpi8xtn6\nlS/sHLqg88V/OyEo1p8faVhtTDFp5Dzwk03Of4eWIpNQ1+DywBxqXNKwrU+V0Gth\nvb6TazDyYUQmoPWh5DoceYjN\n-----END PRIVATE KEY-----\n"

kredensial = Credentials.from_service_account_info(info_kredensial, scopes=scope)
gc = gspread.authorize(kredensial)

# Membuka file spreadsheet berdasarkan URL dari Secrets
sh = gc.open_by_url("https://docs.google.com/spreadsheets/d/16BP4tZ57ot6isrNCUt1h-MQkq0GmQBGhz6nVdw9He-4/edit?gid=0#gid=0")

def hash_password(password_teks):
    """Mengubah password teks biasa menjadi kode enkripsi SHA-256 aman"""
    return hashlib.sha256(str(password_teks).encode()).hexdigest()

def load_cloud_data():
    """Membaca daftar booking ruangan dari Google Sheets secara real-time"""
    try:
        worksheet = sh.worksheet("data_booking_v3")
        records = worksheet.get_all_records()
        return pd.DataFrame(records).fillna("").astype(str)
    except:
        return pd.DataFrame(columns=["Departemen", "Ruangan", "Tanggal", "Jam Mulai", "Jam Selesai", "Keperluan", "Nama Pemesan"])

def load_user_data():
    """Membaca data akun pengguna dari Google Sheets secara real-time"""
    try:
        worksheet = sh.worksheet("data_user_cloud")
        records = worksheet.get_all_records()
        return pd.DataFrame(records).fillna("").astype(str)
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
                    
                    # Pencocokan data login ke Google Sheets
                    user_match = df_user[(df_user["Username"].str.upper() == u.upper()) & (df_user["Password"] == p_hashed)]
                    
                    if not user_match.empty:
                        st.session_state.logged_in = True
                        st.session_state.username = u.upper()
                        st.session_state.fullname = str(user_match["Nama Lengkap"].values[0])
                        st.session_state.user_dept = str(user_match["Departemen"].values[0])
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
                            # Menambahkan data user baru menggunakan gspread append_row
                            worksheet_user = sh.worksheet("data_user_cloud")
                            worksheet_user.append_row([reg_nik.upper(), hash_password(reg_p), reg_name, reg_dept.upper()])
                            
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
    k_kiri, k_kanan = st.columns()
    
    with k_kiri:
        st.markdown(f"### 👤 Logged in as: **{fullname_clean}** ({st.session_state.user_role.upper()})")
        st.markdown(f"🏢 Dept: **{user_dept_clean}**")
        
        st.subheader("Formulir Pemesanan Ruangan")
        with st.form("form_pemesanan_ruangan_cloud_gspread"):
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
                        
                        # Filter bentrokan jadwal ruangan pada tanggal yang sama
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
                                st.error(f"❌ JADWAL BENTROK! Ruangan telah dipesan oleh Dept. {baris['Departemen']} (Jam {baris['Jam Mulai']} - {baris['Jam Selesai']})")
                                break
                        
                        if bisa_simpan:
                            # Menambahkan baris pemesanan menggunakan gspread append_row
                            worksheet_booking = sh.worksheet("data_booking_v3")
                            worksheet_booking.append_row([
                                user_dept_clean.upper(), 
                                r_pilih, 
                                tgl_str, 
                                j_mulai.strftime("%H:%M"), 
                                j_selesai.strftime("%H:%M"), 
                                keperluan, 
                                fullname_clean
                            ])
                            
                            st.success("🎉 Ruangan Berhasil Dipesan di Cloud Database!")
                            st.rerun()
                else:
                    st.warning("Mohon tuliskan keperluan agenda acara Anda.")
        
        st.write("")
        if st.button("🚪 Keluar Aplikasi (Logout)", key="tombol_logout_sistem_gspread"):
            st.session_state.logged_in = False
            st.session_state.page_control = "login"
            st.rerun()

    with k_kanan:
        st.subheader("📅 Jadwal Penggunaan Ruangan Terkini")
        
        if st.button("🔄 Segarkan Data (Refresh)", key="tombol_refresh_tabel_gspread"):
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
                
                if st.button("🔥 Batalkan & Hapus Pesanan", key="tombol_hapus_admin_gspread"):
                    if pilihan_hapus != "-- Pilih Jadwal --":
                        idx_asli = int(pilihan_hapus.split("]")[0].replace("[", ""))
                        worksheet_booking = sh.worksheet("data_booking_v3")
                        
                        # Ditambah 2 karena indeks dataframe dari 0 dan Baris 1 di Sheets dipakai Judul Kolom
                        worksheet_booking.delete_rows(idx_asli + 2)
                        
                        st.success("🗑️ Jadwal pemesanan berhasil dibatalkan dan dihapus dari Cloud!")
                        st.rerun()
                    else:
                        st.warning("Silakan pilih salah satu jadwal terlebih dahulu sebelum menghapus.")
                st.markdown("---")
            
            st.dataframe(df_display, use_container_width=True, hide_index=True)
