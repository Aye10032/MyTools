import re

import streamlit as st

from ui.Component import side_bar_links

st.set_page_config(
    page_title='工具箱',
    page_icon='🔨',
    layout='wide',
)

with st.sidebar:
    side_bar_links()

st.title("格式化工具")


def re_format(origin_str: str) -> str:
    new_str = origin_str.replace('\r', '').replace('\n', '')

    matches = re.findall(r'\[\s*\d+(?:,\s*\d+)*]', new_str)

    for match in matches:
        match_str: str = match
        new_ref = ''.join([
            f"[^{ind.replace(' ', '')}]"
            for ind in match_str.replace('[', '').replace(']', '').split(',')
        ])
        new_str = new_str.replace(match, new_ref)

    return new_str


col1, col2 = st.columns([1, 1], gap="medium")

if 'markdown_text' not in st.session_state:
    st.session_state.markdown_text = ''

with col1.container(height=520, border=True):
    st.markdown(st.session_state.markdown_text)

with col2:
    st.code(st.session_state.markdown_text, language='markdown')

if prompt := st.chat_input():
    response = re_format(prompt)

    st.session_state.markdown_text = response

    st.rerun()
