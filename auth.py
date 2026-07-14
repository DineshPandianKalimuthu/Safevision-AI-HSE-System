"""
auth.py
--------
Handles user authentication, session state, and role-based access control (RBAC).
"""

import streamlit as st
from database import get_connection, verify_password, log_activity

ROLE_PERMISSIONS = {
    "Admin": {"view", "create", "edit", "delete", "manage_users", "reports"},
    "Safety Officer": {"view", "create", "edit", "reports"},
    "Supervisor": {"view", "create", "reports"},
    "Viewer": {"view"},
}


def init_session():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user" not in st.session_state:
        st.session_state.user = None


def login(username: str, password: str) -> bool:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE username = ? AND is_active = 1", (username,)
    ).fetchone()
    conn.close()

    if row and verify_password(password, row["password_hash"]):
        st.session_state.authenticated = True
        st.session_state.user = {
            "id": row["id"],
            "username": row["username"],
            "full_name": row["full_name"],
            "role": row["role"],
            "department": row["department"],
        }
        log_activity(username, "Login", "Auth")
        return True
    return False


def logout():
    if st.session_state.get("user"):
        log_activity(st.session_state.user["username"], "Logout", "Auth")
    st.session_state.authenticated = False
    st.session_state.user = None


def require_login():
    init_session()
    if not st.session_state.authenticated:
        st.warning("Please log in from the Home page to access this module.")
        st.stop()


def has_permission(action: str) -> bool:
    if not st.session_state.get("user"):
        return False
    role = st.session_state.user["role"]
    return action in ROLE_PERMISSIONS.get(role, set())


def require_permission(action: str):
    if not has_permission(action):
        st.error(f"🚫 Your role does not have permission to perform this action ('{action}').")
        st.stop()
