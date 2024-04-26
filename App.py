import streamlit as st

from ui.Component import side_bar_links

st.set_page_config(
    page_title='工具箱',
    page_icon='🔨',
)

with st.sidebar:
    side_bar_links()

st.markdown("""
# 自用小工具

## 文本格式化

将PDF中直接复制的文本中的换行符去除，并将引用转化为markdown格式。

## 引用文献生成

处理PUBMED的NLM格式的引用文献，并转化为yaml格式，方便存储在markdown文件中
""")
