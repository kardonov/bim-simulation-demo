import streamlit as st
from utils.db import query
import pandas as pd
import altair as alt
from datetime import datetime


def show():
    user = st.session_state.get("user", {})

    st.markdown(f"""
    <div class="welcome-banner">
        <div>
            <h2 style="margin:0;color:#fff;font-size:1.8rem;">Selamat Datang, {user.get('name','User')} 👋</h2>
            <p style="margin:0.3rem 0 0;color:#c5d8ff;font-size:0.9rem;">Pantau aktivitas dan progres pekerjaan di satu tempat.</p>
        </div>
        <span style="font-size:3rem;opacity:0.6;">📈</span>
    </div>
    """, unsafe_allow_html=True)

    # Stats
    mahasiswa_count = query("SELECT COUNT(*) FROM users WHERE role='Mahasiswa'", fetchone=True)[0]
    dosen_count = query("SELECT COUNT(*) FROM users WHERE role='Dosen'", fetchone=True)[0]
    materi_count = query("SELECT COUNT(*) FROM materi", fetchone=True)[0] or 0
    tugas_count = query("SELECT COUNT(*) FROM model4d", fetchone=True)[0] or 0

    col1, col2, col3, col4 = st.columns(4)
    stats = [
        (col1, "🎓", "MAHASISWA", f"{mahasiswa_count} Orang", "#3b82f6"),
        (col2, "👨‍🏫", "DOSEN", f"{dosen_count} Orang", "#10b981"),
        (col3, "📖", "MATERI", f"{materi_count or 20} Modul", "#06b6d4"),
        (col4, "📋", "TUGAS AKTIF", f"{tugas_count or 12} Tugas", "#f59e0b"),
    ]
    for col, icon, label, val, color in stats:
        with col:
            st.markdown(f"""
            <div class="stat-card">
                <div>
                    <div style="font-size:0.7rem;font-weight:700;color:#888;letter-spacing:1px;">{label}</div>
                    <div style="font-size:1.6rem;font-weight:800;color:#1e293b;margin-top:0.2rem;">{val}</div>
                </div>
                <div style="font-size:2rem;background:{color}20;width:52px;height:52px;border-radius:12px;display:flex;align-items:center;justify-content:center;">{icon}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Chart
    col_chart, col_info = st.columns([2, 1])
    with col_chart:
        month_options = ["Januari", "Februari", "Maret", "April", "Mei", "Juni",
                         "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
        current_month = datetime.now().month - 1
        col_m, col_y = st.columns([2, 1])
        with col_m:
            selected_month = st.selectbox("Bulan", month_options, index=current_month, label_visibility="collapsed")
        with col_y:
            selected_year = st.selectbox("Tahun", [2024, 2025, 2026], index=1, label_visibility="collapsed")

        st.markdown(f'<div class="chart-title">📊 Grafik Aktivitas Bulanan — {selected_month} {selected_year}</div>', unsafe_allow_html=True)

        # Demo chart data
        chart_data = pd.DataFrame({
            "Minggu": ["Minggu 1", "Minggu 2", "Minggu 3", "Minggu 4"],
            "Aktivitas": [4, 7, 12, 5],
        })
        chart = alt.Chart(chart_data).mark_bar(
            color="#3b5bdb", cornerRadiusTopLeft=4, cornerRadiusTopRight=4
        ).encode(
            x=alt.X("Minggu:N", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("Aktivitas:Q", title="Jumlah Aktivitas"),
            tooltip=["Minggu", "Aktivitas"]
        ).properties(height=280)
        st.altair_chart(chart, use_container_width=True)

    with col_info:
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown("### 📌 Info Akun")
        st.markdown(f"""
        - **Nama:** {user.get('name')}
        - **Role:** {user.get('role')}
        - **Program:** {user.get('program_study','-')}
        - **Semester:** {user.get('semester','-')}
        - **NIM/NIDN:** {user.get('nim_nidn','-')}
        """)
        st.markdown("</div>", unsafe_allow_html=True)

        # Recent activity
        jadwal_rows = query("SELECT nama_pekerjaan, tanggal_mulai FROM model4d ORDER BY id DESC LIMIT 3")
        if jadwal_rows:
            st.markdown("### 📅 Jadwal Terakhir")
            for row in jadwal_rows:
                st.markdown(f"- **{row[0]}** — {row[1]}")
