import random
from typing import Dict, Any

import requests
import streamlit as st
import yaml
from loguru import logger

from ui.Component import side_bar_links
from bs4 import BeautifulSoup

from utils.Decorator import retry

st.set_page_config(
    page_title='工具箱',
    page_icon='🔨',
    layout='wide',
)

with st.sidebar:
    side_bar_links()


def add():
    ref_list: list = st.session_state.get('reference_list')

    _data = {
        'title': st.session_state.get('title'),
        'pmid': st.session_state.get('pmid').replace('PMID:', '').replace(' ', ''),
        'pmc': st.session_state.get('pmc').replace('PMCID:', '').replace(' ', ''),
        'doi': st.session_state.get('doi').replace('DOI:', '').replace(' ', ''),
    }
    if _data in ref_list:
        st.toast('already exist')
    else:
        ref_list.append(_data)
        st.session_state.reference_list = ref_list
        yaml_str = yaml.dump(ref_list)
        st.session_state.reference_text = yaml_str

        st.session_state['title'] = ''
        st.session_state['pmid'] = ''
        st.session_state['pmc'] = ''
        st.session_state['doi'] = ''


def reset():
    st.session_state.reference_list = []
    st.session_state.reference_text = ''


# def anal_ml():
#     nlm_str: str = st.session_state.get('nlm_text')
#     nlm_list = nlm_str.split('.', 4)
#     title = nlm_list[1]
#     id_list = nlm_list[-1].split('; ')
#     if len(id_list) > 1:
#         pmc = id_list[-1]
#     else:
#         pmc = ''
#     base_list = id_list[0].split('. ')
#     doi = base_list[0]
#     pmid = base_list[1]
#
#     _data = {
#         'title': title[1:] if title.startswith(' ') else title,
#         'pmid': pmid.replace('PMID:', '').replace(' ', ''),
#         'pmc': pmc.replace('PMCID:', '').replace(' ', '').replace('.', ''),
#         'doi': doi.replace('doi:', '').replace(' ', ''),
#     }
#
#     ref_list: list = st.session_state.get('reference_list')
#
#     if _data in ref_list:
#         st.toast('already exist')
#     else:
#         ref_list.append(_data)
#         st.session_state.reference_list = ref_list
#         yaml_str = yaml.dump(ref_list)
#         st.session_state.reference_text = yaml_str
#
#     st.session_state['nlm_text'] = ''


def get_data():
    term: str = st.session_state.get('term_text')
    term = term.replace('\r', ' ').replace('\n', '')
    _data = __get_info(term)

    ref_list: list = st.session_state.get('reference_list')

    if _data in ref_list:
        st.toast('already exist')
    else:
        ref_list.append(_data)
        st.session_state.reference_list = ref_list
        yaml_str = yaml.dump(ref_list)
        st.session_state.reference_text = yaml_str

    st.session_state['nlm_text'] = ''


@retry(delay=random.uniform(2.0, 5.0))
def __get_info(pmid: str) -> Dict[str, Any]:
    url = f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&retmode=xml'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    response = requests.request("GET", url, headers=headers, timeout=10)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'xml')

        title = soup.find('Article').find('ArticleTitle').text if soup.find('Article') else None

        doi_block = soup.find('ArticleIdList').find('ArticleId', {'IdType': 'doi'})
        if doi_block:
            doi = doi_block.text
        else:
            doi = ''
            logger.warning('DOI not found')

        pmc_block = soup.find('ArticleIdList').find('ArticleId', {'IdType': 'pmc'})
        if pmc_block:
            pmc = pmc_block.text.replace('PMC', '')
        else:
            pmc = ''

        return {
            'title': title,
            'pmid': pmid,
            'pmc': pmc,
            'doi': doi
        }


def del_item():
    index: int = st.session_state.get('delete_id')
    ref_list: list = st.session_state.get('reference_list')

    ref_list.pop(index)

    yaml_str = yaml.dump(ref_list, width=999)
    st.session_state.reference_text = yaml_str
    st.session_state.reference_list = ref_list


st.title("引用格式化")

col1, col2 = st.columns([1, 1], gap="medium")

if 'reference_list' not in st.session_state:
    st.session_state.reference_list = []

if 'reference_text' not in st.session_state:
    st.session_state.reference_text = ''

with col1:
    with st.expander('manual'):
        st.text_input('title', key='title')

        col1_1, col1_2 = st.columns([1, 1], gap="small")
        col1_1.text_input('pmid', key='pmid')
        col1_2.text_input('pmc', key='pmc')

        st.text_input('doi', key='doi')

        col2_1, col2_2 = st.columns([1, 1], gap="small")
        col2_1.button('add', use_container_width=True, type='primary', on_click=add)
        col2_2.button('reset', use_container_width=True, on_click=reset)

    st.text_input('Search', key='term_text')
    st.button('add', use_container_width=True, on_click=get_data)

    if len(st.session_state.get('reference_list')) > 0:
        st.divider()

        st.write('共有', len(st.session_state.get('reference_list')), '条引用')

        col3_1, col3_2 = st.columns([2, 1], gap='small')
        col3_1.number_input(
            'id',
            min_value=0,
            max_value=len(st.session_state.get('reference_list')) - 1,
            key='delete_id',
            label_visibility='collapsed'
        )
        col3_2.button('delete', type='primary', on_click=del_item)

with col2:
    with st.container(height=486, border=True):
        st.write(st.session_state.get('reference_list'))

st.code(st.session_state.get('reference_text'), language='yaml')
