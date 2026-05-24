# 🏗️ BIM Simulation — Streamlit App

Aplikasi web **Building Information Modeling (BIM)** berbasis Streamlit untuk manajemen proyek konstruksi, mencakup Model 3D, Penjadwalan 4D, Estimasi Biaya 5D, dan Materi Pembelajaran.

---

## 📸 Fitur Utama

| Fitur | Deskripsi |
|---|---|
| 🔐 **Autentikasi** | Login & registrasi untuk Dosen dan Mahasiswa |
| 🏠 **Dashboard** | Ringkasan statistik dan grafik aktivitas bulanan |
| 📦 **Model 3D** | Manajemen pekerjaan dengan input dimensi & perhitungan dinamis |
| 📅 **Model 4D** | Penjadwalan pekerjaan dengan tampilan kalender & list |
| 💰 **Model 5D** | Analisis biaya, grafik estimasi, dan fitur diskusi/komentar |
| 📚 **Buku Pembelajaran** | Upload dan akses materi konstruksi (khusus Dosen) |
| 📊 **Laporan** | Rekap data, grafik, dan export CSV |

---

## 🚀 Cara Menjalankan

### 1. Clone / Download Project

```bash
git clone <repo_url>
cd bim_simulation
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Jalankan Aplikasi

```bash
streamlit run app.py
```

Aplikasi akan terbuka di browser: `http://localhost:8501`

---

## 🔑 Akun Demo

| Role | Email | Password |
|---|---|---|
| Mahasiswa | `dicka@bimsimulation.com` | `admin123` |
| Dosen | `dosen@bimsimulation.com` | `admin123` |

---

## 📁 Struktur Folder

```
bim_simulation/
│
├── app.py                  # Entry point utama
├── requirements.txt        # Dependencies Python
├── bim_simulation.db       # Database SQLite (auto-dibuat)
│
├── assets/
│   └── style.css           # Custom CSS styling
│
├── pages/
│   ├── dashboard.py        # Halaman dashboard
│   ├── model3d.py          # Manajemen model 3D
│   ├── model4d.py          # Penjadwalan (kalender)
│   ├── model5d.py          # Analisis biaya
│   ├── buku.py             # Buku pembelajaran
│   └── laporan.py          # Laporan & export
│
├── utils/
│   ├── auth.py             # Autentikasi (login/register/logout)
│   └── db.py               # Database SQLite helpers
│
└── .streamlit/
    └── config.toml         # Konfigurasi tema Streamlit
```

---

## 🛠️ Tech Stack

- **Frontend/Framework**: [Streamlit](https://streamlit.io/) >= 1.35
- **Database**: SQLite (built-in Python, tanpa setup tambahan)
- **Charts**: [Altair](https://altair-viz.github.io/)
- **Data**: [Pandas](https://pandas.pydata.org/)

---

## 📌 Catatan

- Database SQLite (`bim_simulation.db`) dibuat otomatis saat pertama kali dijalankan
- File upload materi tersimpan di folder `uploads/` (dibuat otomatis)
- Untuk production, disarankan mengganti SQLite dengan PostgreSQL/MySQL
- Fitur viewer 3D (.glb/.gltf) memerlukan integrasi library tambahan seperti `open3d` atau embedding iframe Three.js

---

## 🤝 Kontribusi

Pull request dan issue sangat disambut. Pastikan kode sesuai dengan standar Python dan struktur folder yang ada.
