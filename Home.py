
import streamlit as st
from src.auth import require_login
# ==========================================
# BIZSTART SG - MAIN APPLICATION
# ==========================================

# Page configuration
st.set_page_config(
    page_title="BizStart SG",
    page_icon="🚀",
    layout="wide"
)

require_login()

# Application header
st.title("🚀 BizStart SG")

st.subheader(
    "Your starting point for understanding "
    "business setup in Singapore"
)

st.write(
    """
    BizStart SG is an LLM-powered educational prototype
    that helps aspiring business owners understand the
    steps involved in starting a business in Singapore.

    Explore the two features below to get started.
    """
)

st.divider()

# Two main use cases
col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 Business Setup Navigator")

    st.write(
        """
        Generate a personalised checklist of business
        setup steps and requirements based on your
        intended business activity.
        """
    )

    st.page_link(
        "pages/3_Business_Setup_Navigator.py",
        label="Explore Setup Navigator",
        icon="📋",
        width="stretch"
    )

with col2:
    st.subheader("💬 Business Requirements Assistant")

    st.write(
        """
        Ask questions about starting a business in
        Singapore and receive plain-language explanations
        based on official government information.
        """
    )

    st.page_link(
        "pages/4_Business_Requirements_Assistant.py",
        label="Explore Requirements Assistant",
        icon="💬",
        width="stretch"
    )

st.divider()

# Mandatory educational disclaimer
st.warning(
    """
    **IMPORTANT NOTICE:** This web application is a prototype developed for
    **educational purposes only.** The information provided here is
    **NOT intended for real-world usage** and should not be relied upon
    for making any decisions, especially those related to financial,
    legal, or healthcare matters.

    **Furthermore, please be aware that the LLM may generate inaccurate
    or incorrect information. You assume full responsibility for how
    you use any generated output.**

    Always consult with qualified professionals for accurate and
    personalised advice.
    """
)