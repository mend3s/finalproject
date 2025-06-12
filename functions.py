# Arquivo: functions.py
import pandas as pd
import numpy as np
import streamlit as st
from sqlalchemy import create_engine
import folium
from folium.plugins import MarkerCluster
import plotly.express as px

# --- Conexão com o Banco de Dados (Centralizada) ---
DB_URL = "sqlite:///creditdata.db"
NOME_TABELA_OTIMIZADA = "analytics_dashboard" # Nome da tabela criada pelo ETL

@st.cache_resource
def _get_db_connection():
    """Cria e armazena em cache uma conexão com o banco de dados."""
    return create_engine(DB_URL)

@st.cache_data
def carregar_dados_otimizados():
    """Carrega os dados da tabela já processada pelo ETL."""
    try:
        engine = _get_db_connection()
        # A consulta agora é muito mais rápida!
        df = pd.read_sql(f"SELECT * FROM {NOME_TABELA_OTIMIZADA}", engine, parse_dates=['Timestamp'])
        return df
    except Exception as e:
        # Erro comum: a tabela ainda não foi criada.
        st.error(
            f"Falha ao carregar dados da tabela otimizada: {e}\n\n"
            "**Você já executou o script `etl.py` primeiro?**"
        )
        return pd.DataFrame()

# As outras funções (calcular_kpis, criar_mapa, etc.) continuam as mesmas,
# pois já esperam um DataFrame limpo para trabalhar.

def calcular_kpis_gerais(df: pd.DataFrame):
    """Calcula KPIs a partir do DataFrame já processado."""
    if df.empty:
        return {k: 0 for k in ['valor_total', 'num_transacoes', 'ticket_medio', 'num_fraudes', 'valor_fraudes', 'taxa_fraude_vol', 'risco_medio_fraudes', 'risco_medio_legitimas']}

    num_transacoes = df['Transaction_ID'].nunique()
    valor_total = df['Transaction_Amount'].sum()
    df_fraude = df[df['Fraud_Label'] == 1]
    df_legitima = df[df['Fraud_Label'] == 0]
    num_fraudes = len(df_fraude)

    kpis = {
        'valor_total': valor_total,
        'num_transacoes': num_transacoes,
        'ticket_medio': df['Transaction_Amount'].mean(),
        'num_fraudes': num_fraudes,
        'valor_fraudes': df_fraude['Transaction_Amount'].sum(),
        'taxa_fraude_vol': (num_fraudes / num_transacoes) * 100 if num_transacoes > 0 else 0,
        'risco_medio_fraudes': df_fraude['Risk_Score'].mean() if num_fraudes > 0 else 0,
        'risco_medio_legitimas': df_legitima['Risk_Score'].mean() if not df_legitima.empty else 0
    }
    return kpis


# Substitua a função de mapa antiga por esta em seu arquivo func/functions.py

def criar_mapa_agregado_por_localizacao(df: pd.DataFrame):
    """
    Cria um mapa de performance extremamente alta agregando os dados por localização.
    O tamanho do círculo representa o volume de transações.
    A cor do círculo representa a taxa de fraude.
    """
    colunas_necessarias = ['Location', 'Latitude', 'Longitude', 'Transaction_ID', 'Fraud_Label']
    if df.empty or not all(col in df.columns for col in colunas_necessarias):
        return None

    df_mapa = df.copy()
    df_mapa.dropna(subset=['Latitude', 'Longitude', 'Location'], inplace=True)
    if df_mapa.empty:
        return None

    # --- AGREGAÇÃO POR LOCALIZAÇÃO ---
    df_agregado = df_mapa.groupby('Location').agg(
        Latitude=('Latitude', 'mean'),
        Longitude=('Longitude', 'mean'),
        Total_Transacoes=('Transaction_ID', 'count'),
        Total_Fraudes=('Fraud_Label', 'sum')
    ).reset_index()

    # Calcula a taxa de fraude e define uma cor
    df_agregado['Taxa_Fraude'] = (df_agregado['Total_Fraudes'] / df_agregado['Total_Transacoes']) * 100
    
    def get_color(taxa_fraude):
        if taxa_fraude > 10:
            return '#d84315' # Vermelho escuro
        elif taxa_fraude > 5:
            return '#f4511e' # Laranja
        elif taxa_fraude > 0:
            return '#ffb300' # Ambar
        return '#2e7d32' # Verde
        
    df_agregado['Cor'] = df_agregado['Taxa_Fraude'].apply(get_color)

    # Cria o mapa
    mapa = folium.Map(
        location=[df_agregado['Latitude'].mean(), df_agregado['Longitude'].mean()], 
        zoom_start=4, 
        tiles="CartoDB positron"
    )

    # Adiciona os círculos agregados
    for _, row in df_agregado.iterrows():
        raio = np.log(row['Total_Transacoes'] + 1) * 3 # Escala logarítmica para o raio
        
        popup_text = f"""
        <b>Localização:</b> {row['Location']}<br>
        <b>Total de Transações:</b> {row['Total_Transacoes']:,}<br>
        <b>Total de Fraudes:</b> {row['Total_Fraudes']:,}<br>
        <b>Taxa de Fraude:</b> {row['Taxa_Fraude']:.2f}%
        """
        
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=raio,
            popup=folium.Popup(popup_text, max_width=300),
            color=row['Cor'],
            fill=True,
            fill_color=row['Cor'],
            fill_opacity=0.6
        ).add_to(mapa)

    return mapa