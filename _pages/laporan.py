import streamlit as st
import pandas as pd
import altair as alt
from utils.db import query
import json


def show():
    st.markdown('<h2 class="page-title">📊 Laporan & Rekap</h2>', unsafe_allow_html=True)

    # Summary cards
    models_3d = query("SELECT COUNT(*) FROM model3d", fetchone=True)[0]
    jadwal = query("SELECT COUNT(*) FROM model4d", fetchone=True)[0]
    anggaran = query("SELECT SUM(total) FROM model5d", fetchone=True)[0] or 0
    users = query("SELECT COUNT(*) FROM users", fetchone=True)[0]

    col1, col2, col3, col4 = st.columns(4)
    for col, icon, label, val in [
        (col1, "📦", "Total Model 3D", models_3d),
        (col2, "📅", "Total Jadwal", jadwal),
        (col3, "💰", f"Total Anggaran", f"Rp {anggaran:,.0f}"),
        (col4, "👥", "Total Pengguna", users),
    ]:
        with col:
            st.markdown(f"""
            <div class="stat-card">
                <div>
                    <div style="font-size:0.7rem;font-weight:700;color:#888;letter-spacing:1px;">{label}</div>
                    <div style="font-size:1.3rem;font-weight:800;color:#1e293b;margin-top:0.2rem;">{val}</div>
                </div>
                <div style="font-size:2rem;background:#3b5bdb20;width:48px;height:48px;border-radius:12px;display:flex;align-items:center;justify-content:center;">{icon}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Charts
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown('<div class="chart-title">📦 Volume per Model 3D</div>', unsafe_allow_html=True)
        models = query("SELECT m.nama_pekerjaan, m5.volume FROM model3d m LEFT JOIN model5d m5 ON m.id=m5.model3d_id")
        if models:
            df = pd.DataFrame(models, columns=["Model", "Volume"]).dropna()
            if not df.empty:
                chart = alt.Chart(df).mark_bar(color="#3b5bdb").encode(
                    x=alt.X("Model:N", axis=alt.Axis(labelAngle=-30)),
                    y="Volume:Q", tooltip=["Model", "Volume"]
                ).properties(height=220)
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("Belum ada data volume.")
        else:
            st.info("Belum ada data.")

    with col_r:
        st.markdown('<div class="chart-title">💰 Biaya per Model</div>', unsafe_allow_html=True)
        cost_data = query("""
            SELECT m.nama_pekerjaan, SUM(m5.total) as total 
            FROM model3d m LEFT JOIN model5d m5 ON m.id=m5.model3d_id
            GROUP BY m.id, m.nama_pekerjaan
        """)
        if cost_data:
            df2 = pd.DataFrame(cost_data, columns=["Model", "Total"]).dropna()
            if not df2.empty:
                chart2 = alt.Chart(df2).mark_bar(color="#10b981").encode(
                    x=alt.X("Model:N", axis=alt.Axis(labelAngle=-30)),
                    y=alt.Y("Total:Q", title="Total (Rp)"),
                    tooltip=["Model", "Total"]
                ).properties(height=220)
                st.altair_chart(chart2, use_container_width=True)

    st.markdown("---")

    # Export section
    st.markdown("### 📥 Export Data")
    col_e1, col_e2, col_e3 = st.columns(3)

    with col_e1:
        if st.button("📥 Export Model 3D (CSV)", use_container_width=True):
            rows = query("SELECT id, nama_pekerjaan, created_at FROM model3d")
            df = pd.DataFrame(rows, columns=["ID", "Nama Pekerjaan", "Dibuat"])
            csv = df.to_csv(index=False)
            st.download_button("⬇️ Download CSV", csv, "model3d.csv", "text/csv")

    with col_e2:
        if st.button("📥 Export Jadwal (CSV)", use_container_width=True):
            rows = query("SELECT id, nama_pekerjaan, tanggal_mulai, tanggal_selesai, deskripsi FROM model4d")
            df = pd.DataFrame(rows, columns=["ID", "Pekerjaan", "Mulai", "Selesai", "Deskripsi"])
            csv = df.to_csv(index=False)
            st.download_button("⬇️ Download CSV", csv, "jadwal.csv", "text/csv")

    with col_e3:
        if st.button("📥 Export Biaya (CSV)", use_container_width=True):
            rows = query("""
                SELECT m.nama_pekerjaan, m5.volume, m5.satuan, m5.harga_satuan, m5.total
                FROM model5d m5 JOIN model3d m ON m5.model3d_id=m.id
            """)
            df = pd.DataFrame(rows, columns=["Pekerjaan", "Volume", "Satuan", "Harga Satuan", "Total"])
            csv = df.to_csv(index=False)
            st.download_button("⬇️ Download CSV", csv, "biaya.csv", "text/csv")

    st.markdown("---")

    # Daftar pengguna (only for dosen/admin)
    user = st.session_state.get("user", {})
    if user.get("role") == "Dosen":
        st.markdown("### 👥 Daftar Pengguna Terdaftar")
        users = query("SELECT name, email, role, program_study, semester, created_at FROM users ORDER BY id")
        df = pd.DataFrame(users, columns=["Nama", "Email", "Role", "Program Studi", "Semester", "Terdaftar"])
        st.dataframe(df, use_container_width=True, hide_index=True)
