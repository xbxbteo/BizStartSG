
import hmac
import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


def require_login():
    """Protect a Streamlit page with a shared password."""

    if st.session_state.get("authenticated", False):
        return

    st.title("🔒 BizStart SG")
    st.info("This educational prototype requires an access password.")

    with st.form("bizstart_login"):
        entered_password = st.text_input(
            "Access password",
            type="password",
        )
        submitted = st.form_submit_button("Log in")

    if submitted:
        expected_password = os.getenv("APP_PASSWORD", "")

        if not expected_password:
            st.error("The application password is not configured.")

        elif hmac.compare_digest(
            entered_password,
            expected_password,
        ):
            st.session_state["authenticated"] = True
            st.rerun()

        else:
            st.error("Incorrect password.")

    st.stop()
