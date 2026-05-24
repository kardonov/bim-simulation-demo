import streamlit as st
import pandas as pd
import altair as alt
import json
from utils.db import query, execute


def show():
    st.markdown('<h2 class="page-title">💰 Analisis Model 5D</h2>', unsafe_allow_html=True)
    st.markdown('<p style="color:#888;font-size:0.9rem;">Pilih pekerjaan untuk menampilkan analisis biaya & jadwal</p>', unsafe_allow_html=True)

    models = query("SELECT id, nama_pekerjaan, perhitungan FROM model3d ORDER BY id")

    if not models:
        st.info("Belum ada model 3D. Tambahkan model terlebih dahulu.")
        return

    col_list, col_detail = st.columns([1, 3])

    with col_list:
        st.markdown("**Daftar Pekerjaan**")
        sel_id = st.session_state.get("sel_5d_id", models[0][0])
        for m in models:
            active = "🔵" if m[0] == sel_id else "⚪"
            if st.button(f"{active} {m[1]}", key=f"sel5d_{m[0]}", use_container_width=True):
                st.session_state["sel_5d_id"] = m[0]
                st.rerun()

    with col_detail:
        sel_model = next((m for m in models if m[0] == sel_id), models[0])
        st.markdown(f"### 📋 {sel_model[1]}")

        # Load perhitungan (volume items)
        perh = json.loads(sel_model[2] or "[]")

        # Get existing 5D entries
        existing_5d = query("SELECT id, volume, satuan, harga_satuan, total FROM model5d WHERE model3d_id=?", (sel_model[0],))

        # If none, create from perhitungan
        if not existing_5d and perh:
            user_id = st.session_state["user"]["id"]
            for p in perh:
                execute("INSERT INTO model5d (model3d_id, volume, satuan, harga_satuan, total, created_by) VALUES (?,?,?,?,?,?)",
                        (sel_model[0], p.get("hasil", 0), p.get("satuan", "m2"), 0, 0, user_id))
            existing_5d = query("SELECT id, volume, satuan, harga_satuan, total FROM model5d WHERE model3d_id=?", (sel_model[0],))

        # Table header
        st.markdown('<div class="table-header">📊 Analisis Biaya</div>', unsafe_allow_html=True)
        cols_h = st.columns([0.5, 3, 2, 2, 2, 2])
        for col, h in zip(cols_h, ["#", "Pekerjaan", "Volume", "Satuan", "Harga Satuan", "Total"]):
            with col: st.markdown(f"**{h}**")
        st.markdown("<hr/>", unsafe_allow_html=True)

        grand_total = 0
        updated_rows = []
        for i, (row_5d, p) in enumerate(zip(existing_5d, perh if perh else [{"label": f"Volume Pekerjaan {i+1}"}] * len(existing_5d))):
            c1, c2, c3, c4, c5, c6 = st.columns([0.5, 3, 2, 2, 2, 2])
            with c1: st.write(i + 1)
            with c2: st.write(p.get("label", f"Pekerjaan {i+1}"))
            with c3: st.write(row_5d[1])
            with c4: st.write(row_5d[2])
            with c5:
                harga = st.number_input(f"Harga", value=float(row_5d[3] or 0), min_value=0.0, step=1000.0,
                                        key=f"harga_{row_5d[0]}", label_visibility="collapsed", format="%.0f")
            total = row_5d[1] * harga
            grand_total += total
            with c6: st.markdown(f"**Rp {total:,.0f}**")
            updated_rows.append((harga, total, row_5d[0]))

        st.markdown(f"""
        <div style="background:#3b5bdb10;border:1px solid #3b5bdb30;border-radius:8px;padding:0.8rem 1rem;margin:0.5rem 0;display:flex;justify-content:space-between;align-items:center;">
            <span style="font-weight:700;color:#1e293b;">Total Keseluruhan</span>
            <span style="font-weight:800;font-size:1.2rem;color:#3b5bdb;">Rp {grand_total:,.0f}</span>
        </div>
        """, unsafe_allow_html=True)

        if st.button("💾 Update Harga Satuan", use_container_width=True):
            for harga, total, rid in updated_rows:
                execute("UPDATE model5d SET harga_satuan=?, total=? WHERE id=?", (harga, total, rid))
            st.success("Harga berhasil diperbarui!")
            st.rerun()

        st.markdown("---")

        # Chart & Comments
        col_chart, col_comment = st.columns([1, 1])

        with col_chart:
            st.markdown('<div class="chart-title">📊 Grafik Estimasi Biaya</div>', unsafe_allow_html=True)
            if existing_5d and perh:
                chart_data = pd.DataFrame({
                    "Pekerjaan": [p.get("label", f"Item {i+1}") for i, p in enumerate(perh[:len(existing_5d)])],
                    "Total": [r[4] for r in existing_5d],
                })
                chart = alt.Chart(chart_data).mark_bar(
                    color="#3b5bdb", cornerRadiusTopLeft=4, cornerRadiusTopRight=4
                ).encode(
                    x=alt.X("Pekerjaan:N", axis=alt.Axis(labelAngle=-30, labelLimit=150)),
                    y=alt.Y("Total:Q", title="Total (Rp)"),
                    tooltip=["Pekerjaan", "Total"]
                ).properties(height=250)
                st.altair_chart(chart, use_container_width=True)

        with col_comment:
            st.markdown('<div class="chart-title">💬 Diskusi & Komentar</div>', unsafe_allow_html=True)

            # Show existing comments
            comments = query("""
                SELECT k.komentar, k.created_at, u.name 
                FROM komentar k JOIN users u ON k.user_id=u.id 
                WHERE k.model5d_id=? ORDER BY k.created_at DESC LIMIT 10
            """, (existing_5d[0][0] if existing_5d else 0,))

            for c in comments:
                st.markdown(f"""
                <div class="comment-bubble">
                    <strong>{c[2]}</strong> <small style="color:#888">{c[1][:16]}</small><br/>
                    {c[0]}
                </div>
                """, unsafe_allow_html=True)

            komentar = st.text_area("Tulis komentar...", key="komentar_input", label_visibility="collapsed", placeholder="Tulis komentar Anda...")
            if st.button("📤 Kirim", use_container_width=True):
                if komentar.strip() and existing_5d:
                    user_id = st.session_state["user"]["id"]
                    execute("INSERT INTO komentar (model5d_id, user_id, komentar) VALUES (?,?,?)",
                            (existing_5d[0][0], user_id, komentar.strip()))
                    st.success("Komentar dikirim!")
                    st.rerun()
