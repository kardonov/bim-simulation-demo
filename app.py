import streamlit as st
from utils.auth import init_session, login_user, register_user, logout_user
from utils.db import init_db

st.set_page_config(
    page_title="BIM Simulation",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="collapsed",  # collapsed saat login page
)

# Load CSS
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

init_db()
init_session()


def set_body_class(logged_in: bool):
    """Inject class ke <body> untuk kontrol CSS sidebar."""
    css_class = "bim-app" if logged_in else "bim-guest"
    st.markdown(
        f"""
        <script>
            (function applyClass() {{
                document.body.classList.remove("bim-guest", "bim-app");
                document.body.classList.add("{css_class}");
            }})();
            setTimeout(function() {{
                document.body.classList.remove("bim-guest", "bim-app");
                document.body.classList.add("{css_class}");
            }}, 80);
        </script>
        """,
        unsafe_allow_html=True,
    )


def open_sidebar_once():
    """
    Klik tombol toggle sidebar secara programatis — hanya sekali
    saat pertama kali user berhasil login (flag _sidebar_opened).
    Setelah itu flag di-set True agar tidak repeat.
    """
    if st.session_state.get("_sidebar_opened"):
        return  # sudah pernah dibuka, skip

    st.markdown(
        """
        <script>
            // Tunggu DOM siap lalu klik tombol collapse/expand sidebar
            function openSidebar() {
                // Selector tombol toggle sidebar Streamlit
                var btn = window.parent.document.querySelector(
                    '[data-testid="collapsedControl"]'
                );
                if (btn) {
                    btn.click();
                } else {
                    // Retry jika DOM belum siap
                    setTimeout(openSidebar, 150);
                }
            }
            setTimeout(openSidebar, 200);
        </script>
        """,
        unsafe_allow_html=True,
    )
    st.session_state["_sidebar_opened"] = True


def show_login():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("""
        <div class="login-card">
            <div class="logo-circle">
                <span style="font-size:2rem;">🏗️</span>
                <div style="font-size:0.85rem;font-weight:700;color:#fff;letter-spacing:1px;">BIM</div>
                <div style="font-size:0.6rem;color:#aac8ff;letter-spacing:2px;">SIMULATION</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.get("_login_error"):
            st.error(st.session_state.pop("_login_error"))

        with st.form("login_form"):
            email    = st.text_input("Email", placeholder="email@example.com", label_visibility="collapsed")
            password = st.text_input("Password", placeholder="Password", type="password", label_visibility="collapsed")
            col_a, col_b = st.columns([1, 1])
            with col_a:
                st.checkbox("Ingat Saya")
            with col_b:
                st.markdown(
                    '<div style="text-align:right">'
                    '<a href="#" style="color:#3b5bdb;font-size:0.85rem;">Lupa Password?</a>'
                    '</div>',
                    unsafe_allow_html=True,
                )
            submit = st.form_submit_button("Login", use_container_width=True)

        # Proses di LUAR blok form — aman untuk st.experimental_rerun()
        if submit:
            success, msg = login_user(email, password)
            if success:
                # Reset flag sidebar agar sidebar dibuka otomatis setelah login
                st.session_state["_sidebar_opened"] = False
                st.experimental_rerun()
            else:
                st.session_state["_login_error"] = msg
                st.experimental_rerun()

        st.markdown(
            '<p style="text-align:center;color:#666;font-size:0.9rem;margin-top:1rem;">'
            'Belum Punya Akun?</p>',
            unsafe_allow_html=True,
        )
        if st.button("→ Buat Akun Baru", use_container_width=True, key="go_register"):
            st.session_state["page"] = "register"
            st.experimental_rerun()


def show_register():
    col1, col2, col3 = st.columns([0.5, 3, 0.5])
    with col2:
        st.markdown("## Buat Akun Baru")

        if st.session_state.get("_reg_error"):
            st.error(st.session_state.pop("_reg_error"))
        if st.session_state.get("_reg_success"):
            st.success(st.session_state.pop("_reg_success"))

        role = st.radio("Peran", ["Dosen", "Mahasiswa"], horizontal=True)

        col_l, col_r = st.columns(2)
        with col_l:
            nim_nidn = st.text_input("NIDN/(NIM Bagi Mahasiswa)", placeholder="123456789")
            name     = st.text_input("Name", placeholder="Nama Lengkap")
            program  = st.selectbox(
                "Program Study",
                ["Teknik Sipil", "Arsitektur", "Teknik Lingkungan", "Teknik Elektro"],
            )
        with col_r:
            semester_options = [f"Semester {i}" for i in range(1, 9)]
            semester         = st.selectbox("Semester", semester_options, index=6)
            email            = st.text_input("Email address", placeholder="email@bimsimulation.com")
            password         = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm password", type="password")

        if st.button("Buat Akun", use_container_width=True):
            if password != confirm_password:
                st.session_state["_reg_error"] = "Password tidak cocok!"
                st.experimental_rerun()
            elif not all([nim_nidn, name, email, password]):
                st.session_state["_reg_error"] = "Harap isi semua field!"
                st.experimental_rerun()
            else:
                success, msg = register_user(email, password, name, role, nim_nidn, program, semester)
                if success:
                    st.session_state["_reg_success"] = "Akun berhasil dibuat! Silakan login."
                    st.session_state["page"] = "login"
                    st.experimental_rerun()
                else:
                    st.session_state["_reg_error"] = msg
                    st.experimental_rerun()

        if st.button("← Sudah punya akun? Masuk", key="go_login"):
            st.session_state["page"] = "login"
            st.experimental_rerun()


def show_sidebar():
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-header">
            <span style="font-size:1.5rem;">🏗️</span>
            <div>
                <div style="font-weight:700;font-size:1rem;color:#fff;">BIM</div>
                <div style="font-size:0.65rem;color:#aac8ff;letter-spacing:2px;">SIMULATION</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        pages = {
            "🏠 Dashboard"        : "dashboard",
            "📚 Buku Pembelajaran" : "buku",
            "📦 Model 3D"          : "model3d",
            "📅 Model 4D"          : "model4d",
            "💰 Model 5D"          : "model5d",
            "📊 Laporan"           : "laporan",
        }

        st.markdown(
            '<div style="margin-top:1rem;font-size:0.7rem;color:#8899bb;'
            'font-weight:600;letter-spacing:1px;padding:0 0.5rem;">INTERFACE</div>',
            unsafe_allow_html=True,
        )

        for label, key in pages.items():
            if st.button(label, key=f"nav_{key}", use_container_width=True):
                st.session_state["page"] = key
                st.experimental_rerun()

        st.markdown("---")
        user = st.session_state.get("user", {})
        st.markdown(
            f'<div style="color:#aac8ff;font-size:0.85rem;padding:0.5rem;">'
            f'👤 {user.get("name","User")}</div>',
            unsafe_allow_html=True,
        )
        if st.button("🚪 Logout", use_container_width=True):
            # Reset flag agar sidebar collapse lagi saat login berikutnya
            st.session_state["_sidebar_opened"] = False
            logout_user()
            st.experimental_rerun()


# ─── Routing ───────────────────────────────────────────────────────────────────
logged_in = st.session_state.get("logged_in", False)

set_body_class(logged_in)

if not logged_in:
    page = st.session_state.get("page", "login")
    if page == "register":
        show_register()
    else:
        show_login()
else:
    # Buka sidebar otomatis satu kali setelah login
    open_sidebar_once()

    show_sidebar()
    page = st.session_state.get("page", "dashboard")

    if page == "dashboard":
        from _pages.dashboard import show
        show()
    elif page == "model3d":
        from _pages.model3d import show
        show()
    elif page == "model4d":
        from _pages.model4d import show
        show()
    elif page == "model5d":
        from _pages.model5d import show
        show()
    elif page == "buku":
        from _pages.buku import show
        show()
    elif page == "laporan":
        from _pages.laporan import show
        show()
    else:
        from _pages.dashboard import show
        show()
