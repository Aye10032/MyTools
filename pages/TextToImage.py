import os

import requests
import urllib3

import streamlit as st
from loguru import logger

from ui.Component import side_bar_links

st.set_page_config(
    page_title='工具箱',
    page_icon='🔨',
    layout='wide',
)

with st.sidebar:
    side_bar_links()

    st.text_input('Api_key', type='password', key='api_key')

st.title('CogView 文生图')


def generate_image_url(prompt: str) -> str:
    from zhipuai import ZhipuAI

    api = st.session_state.get('api_key')
    if api != '':
        client = ZhipuAI(api_key=api)  # 请填写您自己的APIKey

        response = client.images.generations(
            model="cogview-3",
            prompt=prompt,
        )

        return response.data[0].url
    else:
        st.error('请先输入API！')


def download_img(img_url: str) -> str:
    r = requests.get(img_url, stream=True)
    if r.status_code == 200:
        filename = img_url.split('/')[-1]
        filepath = f'/home/aye/Service/MyTools/image/{filename}'
        open(filepath, 'wb').write(r.content)
        del r
        return filepath
    else:
        st.error('download fail')


if 'filepath' not in st.session_state:
    st.session_state['filepath'] = ''

if os.path.exists(st.session_state.get('filepath')):
    with st.chat_message('user'):
        st.write(st.session_state.get('image_prompt'))
    with st.chat_message('ai'):
        path: str = st.session_state.get('filepath')
        st.image(path)
        with open(path, "rb") as file:
            btn = st.download_button(
                label="下载",
                data=file,
                file_name=path.split('/')[-1],
                mime="image/png"
            )

if image_prompt := st.chat_input(key='image_prompt'):
    with st.chat_message('user'):
        logger.info(image_prompt)
        st.write(image_prompt)

    with st.spinner('正在生成图片...'):
        url = generate_image_url(image_prompt)
        logger.info(url)

    with st.spinner('正在下载图片...'):
        path = download_img(url)
        st.session_state['filepath'] = path

    with st.chat_message('ai'):
        st.image(path)
        with open(path, "rb") as file:
            btn = st.download_button(
                label="下载",
                data=file,
                file_name=url.split('/')[-1],
                mime="image/png"
            )
