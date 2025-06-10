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
st.sidebar.button("⛽ Eficiencia Combustivel", on_click=lambda: st.session_state.update(aba_ativa='eficiencia_comb'))
st.sidebar.button("📊 Gráficos Clientes", on_click=lambda: st.session_state.update(aba_ativa='graficos_clientes'))
st.sidebar.button("🧑 Cliente", on_click=lambda: st.session_state.update(aba_ativa='cliente'))
st.sidebar.button("📦 Produtos", on_click=lambda: st.session_state.update(aba_ativa='produtos'))


if st.session_state.aba_ativa == 'eficiencia_comb':

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
    query = '''
        SELECT 
            v.empresa_sigla,
            e.empresa_nome,
            SUM(v.distancia_voada_km) AS total_km,
            SUM(v.combustivel_litros) AS total_combustivel
        FROM voo v
        JOIN empresa e ON v.empresa_sigla = e.empresa_sigla
        GROUP BY v.empresa_sigla
        HAVING total_combustivel > 0
        '''

    df = pd.read_sql_query(query, conn)

    # Calcular eficiência
    df['eficiencia_km_por_litro'] = df['total_km'] / df['total_combustivel']

    # Eficiência média geral
    media_eficiencia = df['eficiencia_km_por_litro'].mean()

    # Top 3 empresas
    top3 = df.sort_values(by='eficiencia_km_por_litro', ascending=False).head(3)
    botton3 = df.sort_values(by='eficiencia_km_por_litro', ascending=False).tail(3)
    # Layout no Streamlit
    st.title("⛽ Eficiência de Combustível das Empresas Aéreas")
    st.metric(label="Média Geral de Eficiência (km/l)", value=f"{media_eficiencia:.2f}")


    st.subheader("Top 3 Empresas em Eficiência")
    col1, col2, col3 = st.columns(3)
    col1.metric(label=top3.iloc[0]['empresa_nome'], value=f"{top3.iloc[0]['eficiencia_km_por_litro']:.2f} km/l")
    col2.metric(label=top3.iloc[1]['empresa_nome'], value=f"{top3.iloc[1]['eficiencia_km_por_litro']:.2f} km/l")
    col3.metric(label=top3.iloc[2]['empresa_nome'], value=f"{top3.iloc[2]['eficiencia_km_por_litro']:.2f} km/l")

    st.subheader("Top 3 Empresas com menos Eficiência")
    col1, col2, col3 = st.columns(3)
    col1.metric(label=botton3.iloc[0]['empresa_nome'], value=f"{botton3.iloc[0]['eficiencia_km_por_litro']:.2f} km/l")
    col2.metric(label=botton3.iloc[1]['empresa_nome'], value=f"{botton3.iloc[1]['eficiencia_km_por_litro']:.2f} km/l")
    col3.metric(label=botton3.iloc[2]['empresa_nome'], value=f"{botton3.iloc[2]['eficiencia_km_por_litro']:.2f} km/l")

    st.subheader("Média Geral de Eficiência")
    st.metric(label="Média Geral (km/l)", value=f"{media_eficiencia:.2f}")



            