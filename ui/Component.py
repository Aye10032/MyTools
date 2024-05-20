import streamlit as st


def side_bar_links():
    st.header('工具箱')

    st.page_link('App.py', label='Home', icon='🏠')
    st.page_link('pages/Reformat.py', label='文本格式化', icon='📖')
    st.page_link('pages/Reference.py', label='引用文献生成', icon='📙')
    st.page_link('pages/Translate.py', label='翻译总结工具', icon='🌐')
    st.page_link('pages/TextToImage.py', label='文生图', icon='🎨')

    st.divider()
