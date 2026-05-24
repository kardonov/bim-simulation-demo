import streamlit as st
from utils.db import query, execute
import os


def show():
    st.markdown('<h2 class="page-title">📚 Buku Pembelajaran</h2>', unsafe_allow_html=True)

    user = st.session_state.get("user", {})
    is_dosen = user.get("role") == "Dosen"

    if is_dosen:
        if st.button("➕ Tambah Materi", use_container_width=False):
            st.session_state["show_add_materi"] = True

        if st.session_state.get("show_add_materi"):
            with st.expander("📝 Tambah Materi Baru", expanded=True):
                judul = st.text_input("Judul Materi")
                deskripsi = st.text_area("Deskripsi")
                uploaded = st.file_uploader("Upload File (PDF/PPT/Video)", type=["pdf", "pptx", "mp4"])

                c1, c2 = st.columns(2)
                with c1:
                    if st.button("💾 Simpan Materi", use_container_width=True):
                        if not judul:
                            st.error("Judul wajib diisi!")
                        else:
                            file_path = None
                            if uploaded:
                                os.makedirs("uploads", exist_ok=True)
                                file_path = f"uploads/{uploaded.name}"
                                with open(file_path, "wb") as f:
                                    f.write(uploaded.read())
                            execute("INSERT INTO materi (judul, deskripsi, file_path, created_by) VALUES (?,?,?,?)",
                                    (judul, deskripsi, file_path, user["id"]))
                            st.success("Materi berhasil ditambahkan!")
                            st.session_state["show_add_materi"] = False
                            st.experimental_rerun()
                with c2:
                    if st.button("❌ Batal", use_container_width=True):
                        st.session_state["show_add_materi"] = False
                        st.experimental_rerun()

    st.markdown("---")
    search = st.text_input("🔍 Cari materi...", placeholder="Cari judul materi...", label_visibility="collapsed")

    rows = query("SELECT id, judul, deskripsi, file_path, created_at FROM materi ORDER BY id DESC")
    if search:
        rows = [r for r in rows if search.lower() in r[1].lower()]

    # Demo materi jika kosong
    if not rows:
        demo_materi = [
            ("Pengenalan BIM", "Dasar-dasar Building Information Modeling"),
            ("Model 3D dalam BIM", "Teknik pembuatan model 3D struktural"),
            ("Penjadwalan Konstruksi", "Manajemen jadwal dengan model 4D"),
            ("Estimasi Biaya (5D)", "Analisis biaya berbasis BIM"),
            ("Revit Fundamental", "Penggunaan Autodesk Revit"),
            ("Kolaborasi Tim BIM", "Standar dan protokol kolaborasi"),
        ]
        st.info("Menampilkan konten demo. Dosen dapat menambahkan materi nyata.")
        cols = st.columns(3)
        for i, (judul, desk) in enumerate(demo_materi):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="materi-card">
                    <div class="materi-icon">📖</div>
                    <div class="materi-title">{judul}</div>
                    <div class="materi-desc">{desk}</div>
                </div>
                """, unsafe_allow_html=True)
        return

    cols = st.columns(3)
    for i, row in enumerate(rows):
        with cols[i % 3]:
            file_icon = "📄" if row[3] and row[3].endswith(".pdf") else "📊" if row[3] and row[3].endswith(".pptx") else "🎬" if row[3] and row[3].endswith(".mp4") else "📖"
            st.markdown(f"""
            <div class="materi-card">
                <div class="materi-icon">{file_icon}</div>
                <div class="materi-title">{row[1]}</div>
                <div class="materi-desc">{row[2] or ''}</div>
                <div class="materi-date">📅 {row[4][:10] if row[4] else ''}</div>
            </div>
            """, unsafe_allow_html=True)

            if row[3] and os.path.exists(row[3]) and is_dosen:
                with open(row[3], "rb") as f:
                    st.download_button("⬇️ Download", f, file_name=os.path.basename(row[3]), key=f"dl_{row[0]}")

            if is_dosen:
                if st.button("🗑️ Hapus", key=f"del_materi_{row[0]}"):
                    execute("DELETE FROM materi WHERE id=?", (row[0],))
                    st.experimental_rerun()
