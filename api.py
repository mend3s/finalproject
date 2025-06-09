import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

conn = sqlite3.connect("dados_voo.db")
cursor = conn.cursor()

st.sidebar.title("📋Menu")
st.sidebar.title("Categorias")
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        background-color: #003366;
    }
    </style>
    """,
    unsafe_allow_html=True
)        
if 'aba_ativa' not in st.session_state:
    st.session_state.aba_ativa = 'home'  # valor inicial padrão
    
st.sidebar.button("📌 Home", on_click=lambda: st.session_state.update(aba_ativa='home'))
st.sidebar.button("🔍 Filtros", on_click=lambda: st.session_state.update(aba_ativa='filtros'))
st.sidebar.button("📊 Gráficos Produtos", on_click=lambda: st.session_state.update(aba_ativa='graficos_produtos'))
st.sidebar.button("📊 Gráficos Clientes", on_click=lambda: st.session_state.update(aba_ativa='graficos_clientes'))
st.sidebar.button("🧑 Cliente", on_click=lambda: st.session_state.update(aba_ativa='cliente'))
st.sidebar.button("📦 Produtos", on_click=lambda: st.session_state.update(aba_ativa='produtos'))


if st.session_state.aba_ativa == 'home':

    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"] {
            background-color: #000000;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    tab1, tab2 = st.tabs(["Home", "Filtro Produtos"])

    with tab1:
        st.subheader("Home", divider=True)
