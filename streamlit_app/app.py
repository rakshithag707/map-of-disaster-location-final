"""Entry point. Run with:  streamlit run app.py"""
import streamlit as st

import theme
from filters import sidebar

st.set_page_config(page_title="Disaster Monitor", layout="wide", initial_sidebar_state="expanded")
theme.apply()

df, label = sidebar()
st.session_state["df"] = df
st.session_state["label"] = label

pages = st.navigation([
    st.Page("views/overview.py", title="Overview", default=True),
    st.Page("views/disaster_map.py", title="Disaster Map"),
    st.Page("views/analytics.py", title="Analytics"),
    st.Page("views/regional.py", title="Regional Analysis"),
], position="top")
pages.run()
