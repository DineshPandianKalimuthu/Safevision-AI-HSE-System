"""
app.py
-------
SafeVision AI - Main entry point.
Handles login and routes users into the multipage Streamlit app.
Run with: streamlit run app.py
"""

import streamlit as st
from database import init_db
from auth import init_session, login, logout

st.set_page_config(
    page_title="SafeVision AI | HSE Management System",
    page_icon="🦺",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()
init_session()

# ---------------- Global styling ----------------
st.markdown("""
<style>
    .main { background-color: #f7f9fb; }
    .stMetric { background-color: white; padding: 12px; border-radius: 10px;
                box-shadow: 0 1px 4px rgba(0,0,0,0.08); }
    .app-title { font-size: 2.2rem; font-weight: 800; color: #0f4c75; margin-bottom: 0; }
    .app-subtitle { color: #4b6584; font-size: 1.05rem; margin-top: 0; }
    .login-card { background: white; padding: 2rem; border-radius: 14px;
                  box-shadow: 0 2px 10px rgba(0,0,0,0.08); max-width: 420px; }
    .role-badge { background-color: #eaf4fb; color: #0f4c75; padding: 3px 10px;
                  border-radius: 12px; font-size: 0.8rem; font-weight: 600; }
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


def login_screen():
    col1, col2, col3 = st.columns([1, 1.3, 1])
    with col2:
        st.markdown('<p class="app-title">🦺 SafeVision AI</p>', unsafe_allow_html=True)
        st.markdown('<p class="app-subtitle">HSE Inspection & Incident Management System</p>', unsafe_allow_html=True)
        st.write("")

        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("🔐 Log In", use_container_width=True)

        if submitted:
            if login(username, password):
                st.success(f"Welcome, {st.session_state.user['full_name']}!")
                st.rerun()
            else:
                st.error("Invalid username or password.")

        with st.expander("🧪 Demo credentials"):
            st.markdown("""
            | Role | Username | Password |
            |---|---|---|
            | Admin | `admin` | `Admin@123` |
            | Safety Officer | `safety.officer` | `Safety@123` |
            | Supervisor | `supervisor` | `Super@123` |
            | Viewer | `viewer` | `View@123` |
            """)


def landing_page():
    user = st.session_state.user
    st.markdown('<p class="app-title">🦺 SafeVision AI</p>', unsafe_allow_html=True)
    st.markdown('<p class="app-subtitle">Comprehensive Health, Safety & Environment Management System</p>', unsafe_allow_html=True)

    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown(f"### Welcome back, {user['full_name']} 👋")
        st.markdown(f"<span class='role-badge'>{user['role']}</span> &nbsp; Department: **{user['department']}**", unsafe_allow_html=True)
    with c2:
        if st.button("🚪 Log Out", use_container_width=True):
            logout()
            st.rerun()

    st.divider()
    st.markdown("### 📌 Use the sidebar to navigate the modules")

    modules = [
        ("📊 Dashboard", "Real-time KPIs, safety analytics & AI risk insights"),
        ("🚨 Incidents", "Log, investigate, and track workplace incidents"),
        ("⚠️ Hazards", "Report and mitigate identified hazards"),
        ("🔍 Inspections", "Schedule and record safety inspections & audits"),
        ("🧮 Risk Assessment", "Likelihood x Severity risk matrix evaluations"),
        ("🧤 PPE Inventory", "Track PPE stock levels and reorder alerts"),
        ("🎓 Training", "Manage employee safety training & certifications"),
        ("✅ Corrective Actions", "Assign, track, and close out CAPA items"),
        ("📄 Reports", "Generate PDF / Excel HSE reports"),
        ("⚙️ Admin", "User management & system settings (Admin only)"),
    ]
    cols = st.columns(2)
    for i, (title, desc) in enumerate(modules):
        with cols[i % 2]:
            st.markdown(f"""
            <div style="background:white;padding:16px;border-radius:12px;margin-bottom:12px;
                        box-shadow:0 1px 4px rgba(0,0,0,0.08);">
                <b style="font-size:1.05rem;">{title}</b><br>
                <span style="color:#6b7280;">{desc}</span>
            </div>
            """, unsafe_allow_html=True)

    st.info("👈 Select a module from the sidebar (Pages) to get started.")


if not st.session_state.authenticated:
    login_screen()
else:
    landing_page()
