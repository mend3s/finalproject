# func/api_dados.py

import pandas as pd
import numpy as np
import streamlit as st
from sqlalchemy import create_engine
import plotly.express as px

@st.cache_data
def carregar_dados():
    """
    Conecta ao banco 'creditdata.db' e carrega a tabela principal.
    Retorna um DataFrame.
    """
    NOME_DA_TABELA = 'TransacoesCompletas' # VERIFIQUE SE ESTE É O NOME CORRETO!
    
    try:
        engine = create_engine('sqlite:///creditdata.db')
        df = pd.read_sql(f"SELECT * FROM {NOME_DA_TABELA}", engine, parse_dates=['Timestamp'])
        return df
    except Exception as e:
        if f"no such table: {NOME_DA_TABELA}" in str(e):
             st.error(f"ERRO: A tabela '{NOME_DA_TABELA}' não foi encontrada. Verifique o nome na linha 15 do arquivo 'func/api_dados.py'.")
        else:
            st.error(f"Falha ao carregar dados: {e}")
        return pd.DataFrame()

# ---- FUNÇÕES PARA A PÁGINA 'VISÃO GERAL' ----

def identificar_outliers(df, coluna):
    """
    Identifica outliers em uma coluna usando o método IQR.
    Retorna um dataframe com os outliers, a contagem e o limite superior.
    """
    if coluna not in df.columns:
        return pd.DataFrame(), 0, 0

    Q1 = df[coluna].quantile(0.25)
    Q3 = df[coluna].quantile(0.75)
    IQR = Q3 - Q1
    
    limite_inferior = Q1 - 1.5 * IQR
    limite_superior = Q3 + 1.5 * IQR
    
    df_outliers = df[(df[coluna] < limite_inferior) | (df[coluna] > limite_superior)]
    
    return df_outliers, len(df_outliers), limite_superior

def criar_boxplot_interativo(df, coluna):
    """Cria um gráfico de boxplot interativo com Plotly."""
    fig = px.box(df, y=coluna, title=f'Análise de Outliers para {coluna}', points="all", height=500)
    fig.update_layout(title_x=0.5, template="plotly_white")
    return fig


# ---- FUNÇÕES PARA A PÁGINA 'ANÁLISE EXPLORATÓRIA' ----

def criar_grafico_distribuicao(df, coluna):
    """Cria um histograma interativo para uma coluna numérica."""
    fig = px.histogram(df, x=coluna, title=f'Distribuição de {coluna}', nbins=50, template='plotly_white')
    fig.update_layout(bargap=0.1, title_x=0.5)
    return fig

def criar_grafico_contagem(df, coluna):
    """Cria um gráfico de barras interativo para uma coluna categórica."""
    contagem = df[coluna].value_counts().reset_index()
    fig = px.bar(contagem, x=contagem.columns[0], y=contagem.columns[1], title=f'Contagem por {coluna}', template='plotly_white', text_auto=True)
    fig.update_layout(title_x=0.5)
    return fig