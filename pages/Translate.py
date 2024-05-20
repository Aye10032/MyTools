import os

import httpx
import streamlit as st
import yaml
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from loguru import logger

from ui.Component import side_bar_links

st.set_page_config(
    page_title='工具箱',
    page_icon='🔨',
    layout='wide',
)

st.title("一键生成翻译总结")

with st.sidebar:
    side_bar_links()

    st.toggle('去除换行', key='trans_reformat')
    st.toggle('总结', key='trans_conclusion')

    st.toggle('输出格式', key='trans_text_mode')
    if st.session_state.get('trans_text_mode'):
        st.caption('markdown')
    else:
        st.caption('latex')


def get_translate_and_conclude(question: str, step: int):
    if step == 0:
        _prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage("You are an AI academic assistant and should answer user questions rigorously."),
                ("human",
                 "你将收到一个论文的片段。首先，将这段文本以学术风格**翻译为中文**，不要漏句。对于所有的特殊符号和latex代码，请保持原样不要改变。"
                 "对于文中一些显得与上下文突兀的数字，很大可能是引用文献，请使用latex语法将它们表示为一个上标，并使用美元符号包围，如$^2$。这是你要翻译的文献片段:\n{question}"),
            ]
        )
    elif step == 1:
        _prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content="You are an AI academic assistant and should answer user questions rigorously."),
                HumanMessage(
                    content=f"""首先，将这段文本**翻译为中文**，不要漏句。对于所有的特殊符号和latex代码，请保持原样不要改变:
                    {st.session_state.translate_messages[-3]}"""
                ),
                AIMessage(content=str(st.session_state.translate_messages[-2])),
                HumanMessage(content=question),
            ]
        )
    else:
        raise Exception("Wrong step value")

    with open('/home/aye/Service/MyTools/config.yaml', 'r') as f:
        data = yaml.load(f.read(), yaml.FullLoader)
    http_client = httpx.Client(proxies='http://127.0.0.1:7890')
    llm = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        http_client=http_client,
        temperature=0,
        openai_api_key=data['llm']['openai']['api_key'],
        streaming=True
    )

    chain = _prompt | llm

    if step == 0:
        llm_result = chain.stream({"question": question})
    else:
        llm_result = chain.stream({"question": question})

    return llm_result


col1, col2 = st.columns([1, 1], gap="medium")

if 'translate_messages' not in st.session_state:
    st.session_state.translate_messages = []

if 'markdown_text' not in st.session_state:
    st.session_state.markdown_text = ''

chat_container = col1.container(height=610, border=False)

with chat_container:
    for message in st.session_state.translate_messages:
        icon = 'logo.png' if message['role'] != 'user' else None
        with st.chat_message(message['role']):
            st.markdown(message['content'])

with col2:
    if st.session_state.markdown_text != '':
        with st.container(height=520, border=True):
            st.markdown(st.session_state.markdown_text)
        if st.session_state.get('trans_text_mode'):
            st.code(st.session_state.markdown_text, language='markdown')
        else:
            st.code(st.session_state.markdown_text, language='latex')

if prompt := st.chat_input():
    st.session_state.translate_messages = []
    if st.session_state.get('trans_reformat'):
        prompt = prompt.replace("\n", " ").replace("\r", "")

    logger.info(f'[translate]: {prompt}')
    prompt = prompt.replace('$', r'\$')

    chat_container.chat_message("human").write(prompt)
    st.session_state.translate_messages.append({'role': 'user', 'content': prompt})

    response = get_translate_and_conclude(prompt, 0)
    translate_result = chat_container.chat_message("ai").write_stream(response)
    st.session_state.translate_messages.append({'role': 'assistant', 'content': translate_result})

    if st.session_state.get('trans_conclusion'):
        query = "接下来，请用两到四句话总结一下这段文本的内容"
        chat_container.chat_message("human").write(query)
        st.session_state.translate_messages.append({'role': 'user', 'content': query})

        response = get_translate_and_conclude(query, 1)
        conclusion_result = chat_container.chat_message("ai").write_stream(response)
        logger.info(f"(conclude): {conclusion_result}")
        st.session_state.translate_messages.append({'role': 'assistant', 'content': conclusion_result})

        if st.session_state.get('trans_text_mode'):
            markdown_text = f"""{prompt}\t\r\n{translate_result}\t\r\n> {conclusion_result}"""
        else:
            markdown_text = f"""{prompt}\n\n{translate_result}\n\n\\tbox{{ {conclusion_result} }}"""
            markdown_text = markdown_text.replace('%', r'\%')
        st.session_state.markdown_text = markdown_text
    else:
        markdown_text = f"""{prompt}\t\r\n{translate_result}"""
        st.session_state.markdown_text = markdown_text

    st.rerun()
