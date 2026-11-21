import streamlit as st
from style import inject_css, navbar

st.set_page_config(page_title="Nifty Portfolio Lab", page_icon=":material/show_chart:",
                   layout="wide", initial_sidebar_state="collapsed")
inject_css()

pages = [
    st.Page("dashboard.py", title="Dashboard", default=True),
    st.Page("about.py", title="About", url_path="about"),
]
nav = st.navigation(pages, position="hidden")
navbar(pages)
nav.run()