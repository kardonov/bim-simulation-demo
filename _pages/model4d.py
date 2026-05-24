import streamlit as st
from utils.db import query, execute
from datetime import datetime, timedelta, date
import calendar


def show():
    st.markdown('<h2 class="page-title">📅 Penjadwalan Pekerjaan (Model 4D)</h2>', unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col2:
        view_mode = st.radio("Tampilan", ["Kalender", "List"], horizontal=True, label_visibility="collapsed")

    col_add, col_space = st.columns([1, 3])
    with col_add:
        if st.button("➕ Tambah Jadwal", use_container_width=True):
            st.session_state["show_add_4d"] = True

    # ── Add Form ───────────────────────────────────────────
    if st.session_state.get("show_add_4d"):
        with st.expander("📝 Tambah Jadwal Pekerjaan", expanded=True):
            model3d_rows = query("SELECT id, nama_pekerjaan FROM model3d ORDER BY id")
            model3d_options = {r[1]: r[0] for r in model3d_rows}

            nama_pek = st.text_input("Nama Pekerjaan")
            c1, c2 = st.columns(2)
            with c1:
                tgl_mulai = st.date_input("Tanggal Mulai", value=date.today())
            with c2:
                tgl_selesai = st.date_input("Tanggal Selesai", value=date.today() + timedelta(days=3))
            deskripsi = st.text_area("Deskripsi Kegiatan")
            linked_model = st.selectbox("Link ke Model 3D (opsional)", ["-- Tidak Ada --"] + list(model3d_options.keys()))

            c_save, c_cancel = st.columns(2)
            with c_save:
                if st.button("💾 Simpan Jadwal", use_container_width=True):
                    if not nama_pek:
                        st.error("Nama pekerjaan wajib diisi!")
                    else:
                        model3d_id = model3d_options.get(linked_model)
                        user_id = st.session_state["user"]["id"]
                        execute("INSERT INTO model4d (nama_pekerjaan, tanggal_mulai, tanggal_selesai, deskripsi, model3d_id, created_by) VALUES (?,?,?,?,?,?)",
                                (nama_pek, str(tgl_mulai), str(tgl_selesai), deskripsi, model3d_id, user_id))
                        st.success("Jadwal ditambahkan!")
                        st.session_state["show_add_4d"] = False
                        st.experimental_rerun()
            with c_cancel:
                if st.button("❌ Batal", use_container_width=True):
                    st.session_state["show_add_4d"] = False
                    st.experimental_rerun()

    # ── Filter ─────────────────────────────────────────────
    st.markdown("---")
    month_names = ["Januari", "Februari", "Maret", "April", "Mei", "Juni",
                   "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    col_s, col_m, col_y = st.columns([3, 2, 1])
    with col_s:
        search = st.text_input("🔍", placeholder="Cari nama pekerjaan...", label_visibility="collapsed")
    with col_m:
        sel_month = st.selectbox("Bulan", month_names, index=datetime.now().month - 1, label_visibility="collapsed")
    with col_y:
        sel_year = st.selectbox("Tahun", [2024, 2025, 2026], index=1, label_visibility="collapsed")

    month_num = month_names.index(sel_month) + 1

    rows = query("SELECT id, nama_pekerjaan, tanggal_mulai, tanggal_selesai, deskripsi FROM model4d ORDER BY tanggal_mulai")
    filtered = []
    for r in rows:
        try:
            tgl = datetime.strptime(r[2], "%Y-%m-%d")
            if tgl.month == month_num and tgl.year == sel_year:
                if not search or search.lower() in r[1].lower():
                    filtered.append(r)
        except:
            pass

    st.markdown(f'<div class="found-badge">📋 {len(filtered)} Jadwal ditemukan</div>', unsafe_allow_html=True)

    if view_mode == "Kalender":
        _show_calendar_view(filtered, month_num, sel_year, sel_month)
    else:
        _show_list_view(filtered)


def _show_calendar_view(filtered, month_num, year, month_name):
    # Build event map {date: [names]}
    event_map = {}
    for r in filtered:
        try:
            start = datetime.strptime(r[2], "%Y-%m-%d").date()
            end = datetime.strptime(r[3], "%Y-%m-%d").date()
            current = start
            while current <= end:
                key = current.strftime("%Y-%m-%d")
                event_map.setdefault(key, []).append(r[1])
                current += timedelta(days=1)
        except:
            pass

    # Get weeks
    cal = calendar.monthcalendar(year, month_num)
    day_names = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]

    for week_idx, week in enumerate(cal):
        # Week header
        week_dates = [date(year, month_num, d) if d != 0 else None for d in week]
        non_zero = [d for d in week if d != 0]
        if not non_zero:
            continue

        # Get ISO week number from first valid date
        first_valid = next((date(year, month_num, d) for d in week if d != 0), None)
        week_num = first_valid.isocalendar()[1] if first_valid else "?"

        st.markdown(f'<div class="calendar-week-header">◀ Minggu {week_num} ({month_name} {year}) ▶</div>', unsafe_allow_html=True)

        cols = st.columns(7)
        for col_idx, (col, day) in enumerate(zip(cols, week)):
            with col:
                if day == 0:
                    st.markdown('<div class="cal-cell-empty"></div>', unsafe_allow_html=True)
                else:
                    d_obj = date(year, month_num, day)
                    key = d_obj.strftime("%Y-%m-%d")
                    events = event_map.get(key, [])
                    day_name = day_names[col_idx]
                    is_weekend = col_idx >= 5

                    cell_class = "cal-cell-weekend" if is_weekend else "cal-cell"
                    events_html = "".join([f'<div class="cal-event">{e}</div>' for e in events]) if events else '<div class="cal-no-event">Tidak Ada Kegiatan</div>'

                    st.markdown(f"""
                    <div class="{cell_class}">
                        <div class="cal-day-label">{day_name} {day}</div>
                        {events_html}
                    </div>
                    """, unsafe_allow_html=True)


def _show_list_view(filtered):
    if not filtered:
        st.info("Tidak ada jadwal di bulan ini.")
        return

    st.markdown('<div class="table-header">📋 Daftar Jadwal</div>', unsafe_allow_html=True)
    cols = st.columns([0.5, 3, 2, 2, 3, 1])
    headers = ["#", "Nama Pekerjaan", "Mulai", "Selesai", "Deskripsi", "Aksi"]
    for col, h in zip(cols, headers):
        with col: st.markdown(f"**{h}**")
    st.markdown('<hr/>', unsafe_allow_html=True)

    for i, row in enumerate(filtered):
        c1, c2, c3, c4, c5, c6 = st.columns([0.5, 3, 2, 2, 3, 1])
        with c1: st.write(i + 1)
        with c2: st.write(row[1])
        with c3: st.write(row[2])
        with c4: st.write(row[3])
        with c5: st.write(row[4] or "-")
        with c6:
            if st.button("🗑️", key=f"del4d_{row[0]}", help="Hapus"):
                execute("DELETE FROM model4d WHERE id=?", (row[0],))
                st.experimental_rerun()
