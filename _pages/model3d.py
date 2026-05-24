import streamlit as st
import json
from utils.db import query, execute


def eval_formula(formula, context={}):
    try:
        allowed = {k: v for k, v in context.items()}
        result = eval(formula, {"__builtins__": {}}, allowed)
        return round(float(result), 4)
    except:
        return None


def show():
    st.markdown('<h2 class="page-title">📦 Daftar Model 3D</h2>', unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("➕ Tambah Model", use_container_width=True):
            st.session_state["show_add_model3d"] = True
            st.session_state["edit_model3d_id"] = None

    # ── Add/Edit Form ─────────────────────────────────────
    if st.session_state.get("show_add_model3d") or st.session_state.get("edit_model3d_id"):
        edit_id = st.session_state.get("edit_model3d_id")
        existing = None
        if edit_id:
            row = query("SELECT * FROM model3d WHERE id=?", (edit_id,), fetchone=True)
            if row:
                existing = {
                    "id": row[0], "nama": row[1],
                    "dimensi": json.loads(row[2] or "[]"),
                    "perhitungan": json.loads(row[3] or "[]"),
                }

        with st.expander("📝 Form Model 3D", expanded=True):
            nama = st.text_input("Nama Pekerjaan", value=existing["nama"] if existing else "")

            st.markdown("#### 📏 Dimensi")
            if "dimensi_rows" not in st.session_state or not st.session_state.get("_dimensi_init"):
                st.session_state["dimensi_rows"] = existing["dimensi"] if existing else [{"label": "", "value": 0, "satuan": "m"}]
                st.session_state["_dimensi_init"] = True

            dimensi_rows = st.session_state["dimensi_rows"]
            new_dimensi = []
            for i, d in enumerate(dimensi_rows):
                c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
                with c1:
                    lbl = st.text_input(f"Label Dimensi", value=d["label"], key=f"dlbl_{i}", label_visibility="collapsed", placeholder="Nama dimensi")
                with c2:
                    val = st.number_input(f"Nilai", value=float(d["value"]), key=f"dval_{i}", label_visibility="collapsed")
                with c3:
                    sat = st.selectbox("Satuan", ["m", "cm", "mm", "m2", "m3"], index=["m","cm","mm","m2","m3"].index(d["satuan"]) if d["satuan"] in ["m","cm","mm","m2","m3"] else 0, key=f"dsat_{i}", label_visibility="collapsed")
                with c4:
                    if st.button("➖", key=f"drem_{i}") and len(dimensi_rows) > 1:
                        st.session_state["dimensi_rows"].pop(i)
                        st.rerun()
                new_dimensi.append({"label": lbl, "value": val, "satuan": sat})
            st.session_state["dimensi_rows"] = new_dimensi

            if st.button("➕ Tambah Dimensi"):
                st.session_state["dimensi_rows"].append({"label": "", "value": 0, "satuan": "m"})
                st.rerun()

            st.markdown("#### 🧮 Perhitungan Dimensi")
            if "perh_rows" not in st.session_state or not st.session_state.get("_perh_init"):
                st.session_state["perh_rows"] = existing["perhitungan"] if existing else [{"label": "", "formula": "", "hasil": 0, "satuan": "m2"}]
                st.session_state["_perh_init"] = True

            perh_rows = st.session_state["perh_rows"]
            new_perh = []

            # Build context from dimensi
            ctx = {d["label"].replace(" ", "_"): d["value"] for d in st.session_state["dimensi_rows"] if d["label"]}

            for i, p in enumerate(perh_rows):
                c1, c2, c3, c4 = st.columns([3, 3, 2, 1])
                with c1:
                    plbl = st.text_input("Label Perhitungan", value=p["label"], key=f"plbl_{i}", label_visibility="collapsed", placeholder="Label")
                with c2:
                    pform = st.text_input("Formula", value=p["formula"], key=f"pform_{i}", label_visibility="collapsed", placeholder="Contoh: 20*10")
                with c3:
                    psat = st.text_input("Satuan", value=p["satuan"], key=f"psat_{i}", label_visibility="collapsed", placeholder="m2")
                with c4:
                    if st.button("➖", key=f"prem_{i}") and len(perh_rows) > 1:
                        st.session_state["perh_rows"].pop(i)
                        st.rerun()
                hasil = eval_formula(pform, ctx)
                if pform:
                    st.markdown(f"<small style='color:#10b981'>✅ Hasil: <b>{hasil} {psat}</b></small>", unsafe_allow_html=True)
                new_perh.append({"label": plbl, "formula": pform, "hasil": hasil or 0, "satuan": psat})
            st.session_state["perh_rows"] = new_perh

            if st.button("➕ Tambah Perhitungan"):
                st.session_state["perh_rows"].append({"label": "", "formula": "", "hasil": 0, "satuan": "m2"})
                st.rerun()

            st.markdown("---")
            st.markdown("**📌 Panduan Rumus:**  `+ Tambah` &nbsp; `- Kurang` &nbsp; `* Kali` &nbsp; `/ Bagi` &nbsp; `** Pangkat`")

            c_save, c_cancel = st.columns([1, 1])
            with c_save:
                if st.button("💾 Simpan Model", use_container_width=True):
                    if not nama:
                        st.error("Nama pekerjaan wajib diisi!")
                    else:
                        user_id = st.session_state["user"]["id"]
                        d_json = json.dumps(st.session_state["dimensi_rows"])
                        p_json = json.dumps(st.session_state["perh_rows"])
                        if edit_id:
                            execute("UPDATE model3d SET nama_pekerjaan=?, dimensi=?, perhitungan=? WHERE id=?",
                                    (nama, d_json, p_json, edit_id))
                            st.success("Model diperbarui!")
                        else:
                            execute("INSERT INTO model3d (nama_pekerjaan, dimensi, perhitungan, created_by) VALUES (?,?,?,?)",
                                    (nama, d_json, p_json, user_id))
                            st.success("Model berhasil ditambahkan!")
                        st.session_state["show_add_model3d"] = False
                        st.session_state["edit_model3d_id"] = None
                        st.session_state["_dimensi_init"] = False
                        st.session_state["_perh_init"] = False
                        st.rerun()
            with c_cancel:
                if st.button("❌ Batal", use_container_width=True):
                    st.session_state["show_add_model3d"] = False
                    st.session_state["edit_model3d_id"] = None
                    st.session_state["_dimensi_init"] = False
                    st.session_state["_perh_init"] = False
                    st.rerun()

    # ── Search & List ──────────────────────────────────────
    st.markdown("---")
    col_s, col_p = st.columns([3, 1])
    with col_s:
        search = st.text_input("🔍", placeholder="Cari nama pekerjaan...", label_visibility="collapsed")
    with col_p:
        per_page = st.selectbox("Per halaman", [5, 10, 20], index=1, label_visibility="collapsed")

    rows = query("SELECT id, nama_pekerjaan, created_at FROM model3d ORDER BY id DESC")
    if search:
        rows = [r for r in rows if search.lower() in r[1].lower()]

    st.markdown(f'<div class="found-badge">🔍 {len(rows)} Model Ditemukan</div>', unsafe_allow_html=True)

    if rows:
        st.markdown('<div class="table-header">📋 Data Pekerjaan 3D</div>', unsafe_allow_html=True)
        col_n, col_nm, col_ak = st.columns([0.5, 5, 2])
        with col_n: st.markdown("**#**")
        with col_nm: st.markdown("**Nama Pekerjaan**")
        with col_ak: st.markdown("**Aksi**")
        st.markdown('<hr style="margin:0.3rem 0"/>', unsafe_allow_html=True)

        for i, row in enumerate(rows[:per_page]):
            c1, c2, c3 = st.columns([0.5, 5, 2])
            with c1: st.write(i + 1)
            with c2: st.write(row[1])
            with c3:
                b1, b2, b3 = st.columns(3)
                with b1:
                    if st.button("ℹ️", key=f"info_{row[0]}", help="Detail"):
                        st.session_state[f"detail_model3d"] = row[0]
                with b2:
                    if st.button("✏️", key=f"edit_{row[0]}", help="Edit"):
                        st.session_state["edit_model3d_id"] = row[0]
                        st.session_state["show_add_model3d"] = False
                        st.session_state["_dimensi_init"] = False
                        st.session_state["_perh_init"] = False
                        st.rerun()
                with b3:
                    if st.button("🗑️", key=f"del_{row[0]}", help="Hapus"):
                        execute("DELETE FROM model3d WHERE id=?", (row[0],))
                        st.success(f"Model '{row[1]}' dihapus.")
                        st.rerun()

            # Detail inline
            if st.session_state.get("detail_model3d") == row[0]:
                detail = query("SELECT dimensi, perhitungan FROM model3d WHERE id=?", (row[0],), fetchone=True)
                if detail:
                    dim = json.loads(detail[0] or "[]")
                    perh = json.loads(detail[1] or "[]")
                    with st.expander(f"📐 Detail: {row[1]}", expanded=True):
                        c_l, c_r = st.columns(2)
                        with c_l:
                            st.markdown("**Dimensi:**")
                            for d in dim:
                                st.markdown(f"- {d['label']}: `{d['value']} {d['satuan']}`")
                        with c_r:
                            st.markdown("**Perhitungan:**")
                            for p in perh:
                                st.markdown(f"- {p['label']}: `{p['formula']} = {p['hasil']} {p['satuan']}`")
                        if st.button("Tutup Detail", key=f"close_detail_{row[0]}"):
                            st.session_state["detail_model3d"] = None
                            st.rerun()
    else:
        st.info("Belum ada data model 3D.")
