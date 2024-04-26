import streamlit as st
import yaml

from ui.Component import side_bar_links

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
        'pmid': st.session_state.get('pmid').replace(' ', ''),
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


def anal_ml():
    nlm_str: str = st.session_state.get('nlm_text')
    nlm_list = nlm_str.split('.', 4)
    title = nlm_list[1]
    id_list = nlm_list[-1].split('; ')
    if len(id_list) > 1:
        pmc = id_list[-1]
    else:
        pmc = ''
    base_list = id_list[0].split('. ')
    doi = base_list[0]
    pmid = base_list[1]

    _data = {
        'title': title[1:] if title.startswith(' ') else title,
        'pmid': pmid.replace('PMID:', '').replace(' ', ''),
        'pmc': pmc.replace('PMCID:', '').replace(' ', '').replace('.', ''),
        'doi': doi.replace('doi:', '').replace(' ', ''),
    }

    ref_list: list = st.session_state.get('reference_list')

    if _data in ref_list:
        st.toast('already exist')
    else:
        ref_list.append(_data)
        st.session_state.reference_list = ref_list
        yaml_str = yaml.dump(ref_list)
        st.session_state.reference_text = yaml_str

    st.session_state['nlm_text'] = ''


st.title("引用格式化")

col1, col2 = st.columns([1, 1], gap="medium")

if 'reference_list' not in st.session_state:
    st.session_state.reference_list = []

if 'reference_text' not in st.session_state:
    st.session_state.reference_text = ''

with col1:
    st.text_input('title', key='title')

    col1_1, col1_2 = st.columns([1, 1], gap="small")
    col1_1.text_input('pmid', key='pmid')
    col1_2.text_input('pmc', key='pmc')

    st.text_input('doi', key='doi')

    col2_1, col2_2 = st.columns([1, 1], gap="small")
    col2_1.button('add', use_container_width=True, type='primary', on_click=add)
    col2_2.button('reset', use_container_width=True, on_click=reset)

    st.text_area('NLM', key='nlm_text', height=10)
    st.button('add', use_container_width=True, on_click=anal_ml)
    info_container = st.empty()

with col2:
    with st.container(height=486, border=True):
        st.write(st.session_state.get('reference_list'))

st.code(st.session_state.reference_text, language='yaml')
