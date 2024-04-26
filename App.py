import streamlit as st

from ui.Component import side_bar_links

st.set_page_config(
    page_title='工具箱',
    page_icon='🔨',
    layout='wide',
)

with st.sidebar:
    side_bar_links()
