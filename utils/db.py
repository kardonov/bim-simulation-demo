import sqlite3
import os

DB_PATH = "bim_simulation.db"


def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'Mahasiswa',
            nim_nidn TEXT,
            program_study TEXT,
            semester TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS model3d (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_pekerjaan TEXT NOT NULL,
            dimensi TEXT,
            perhitungan TEXT,
            glb_path TEXT,
            excel_path TEXT,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS model4d (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_pekerjaan TEXT NOT NULL,
            tanggal_mulai TEXT,
            tanggal_selesai TEXT,
            deskripsi TEXT,
            model3d_id INTEGER,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS model5d (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model3d_id INTEGER,
            volume REAL,
            satuan TEXT,
            harga_satuan REAL,
            total REAL,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS komentar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model5d_id INTEGER,
            user_id INTEGER,
            komentar TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS materi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            judul TEXT NOT NULL,
            deskripsi TEXT,
            file_path TEXT,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Seed demo user
    try:
        import hashlib
        pw = hashlib.sha256("admin123".encode()).hexdigest()
        c.execute("INSERT OR IGNORE INTO users (email, password, name, role, nim_nidn, program_study, semester) VALUES (?,?,?,?,?,?,?)",
                  ("dicka@bimsimulation.com", pw, "Dicka", "Mahasiswa", "123456789", "Teknik Sipil", "Semester 7"))
        c.execute("INSERT OR IGNORE INTO users (email, password, name, role, nim_nidn, program_study, semester) VALUES (?,?,?,?,?,?,?)",
                  ("dosen@bimsimulation.com", pw, "Prof. Budi", "Dosen", "NIDN001", "Teknik Sipil", "-"))
    except:
        pass

    # Seed demo model3d
    try:
        import json
        demo_dimensi = json.dumps([
            {"label": "Panjang Ruang", "value": 20, "satuan": "m"},
            {"label": "Lebar Ruang", "value": 10, "satuan": "m"},
        ])
        demo_perhitungan = json.dumps([
            {"label": "Luas Pasang Plafond", "formula": "20*10", "hasil": 200, "satuan": "m2"},
        ])
        c.execute("INSERT OR IGNORE INTO model3d (id, nama_pekerjaan, dimensi, perhitungan, created_by) VALUES (1,'Pelat Beton',?,?,1)", (demo_dimensi, demo_perhitungan))
        c.execute("INSERT OR IGNORE INTO model3d (id, nama_pekerjaan, dimensi, perhitungan, created_by) VALUES (2,'Plafond',?,?,1)", (demo_dimensi, demo_perhitungan))
    except:
        pass

    # Seed demo jadwal
    try:
        c.execute("INSERT OR IGNORE INTO model4d (id, nama_pekerjaan, tanggal_mulai, tanggal_selesai, deskripsi, model3d_id, created_by) VALUES (1,'Pelat Beton','2025-10-13','2025-10-15','Membuat Struktur Beton Anti Ambrol',1,1)")
    except:
        pass

    # Seed demo 5d
    try:
        c.execute("INSERT OR IGNORE INTO model5d (id, model3d_id, volume, satuan, harga_satuan, total, created_by) VALUES (1,1,3.636,'kg',150000,545400,1)")
    except:
        pass

    conn.commit()
    conn.close()


def query(sql, params=(), fetchone=False):
    conn = get_conn()
    c = conn.cursor()
    c.execute(sql, params)
    result = c.fetchone() if fetchone else c.fetchall()
    conn.close()
    return result


def execute(sql, params=()):
    conn = get_conn()
    c = conn.cursor()
    c.execute(sql, params)
    last_id = c.lastrowid
    conn.commit()
    conn.close()
    return last_id
