import pandas as pd
import numpy as np
import streamlit as st
from sqlalchemy import create_engine, text
import folium
from folium.plugins import MarkerCluster
import plotly.express as px

# Importa o mapa de nomes de um arquivo de configuração central
from func.config import MAPA_NOMES_COLUNAS

# --- Conexão com o Banco de Dados (Centralizada) ---
DB_URL = "sqlite:///creditdata.db"
NOME_DA_VIEW = "Vw_Dashboard_Principal"

@st.cache_resource
def _get_db_connection():
    """Cria e armazena em cache uma conexão com o banco de dados para evitar múltiplas conexões."""
    return create_engine(DB_URL)

# --- Funções de Carga e Processamento de Dados ---

@st.cache_data
def carregar_dados_gerais():
    """
    Carrega o conjunto de dados completo da view principal.
    Os dados são retornados com os nomes de coluna originais para processamento interno.
    """
    try:
        engine = _get_db_connection()
        # Seleciona todas as colunas da view especificada
        query = f"SELECT * FROM {NOME_DA_VIEW}"
        # Converte a coluna 'Timestamp' para datetime durante a leitura
        df = pd.read_sql(query, engine, parse_dates=['Timestamp'])
        return df
    except Exception as e:
        st.error(f"Falha ao carregar dados gerais: {e}")
        return pd.DataFrame()

def obter_transacoes_por_usuario(user_id: str):
    """
    Busca todas as transações de um usuário específico.
    Retorna um DataFrame com os nomes originais das colunas.
    """
    if not user_id:
        return pd.DataFrame()
    try:
        engine = _get_db_connection()
        query = text(f'SELECT * FROM {NOME_DA_VIEW} WHERE "User_ID" = :user_id')
        df = pd.read_sql(query, engine, params={"user_id": user_id}, parse_dates=['Timestamp'])
        return df
    except Exception as e:
        st.error(f"Falha ao carregar dados do cliente {user_id}: {e}")
        return pd.DataFrame()

def obter_resumo_agregado_periodo(data_inicio: str, data_fim_exclusiva: str):
    """
    Executa uma consulta agregada para obter um resumo de um período específico.
    Esta função é mais eficiente do que carregar todos os dados e filtrar depois.
    """
    try:
        engine = _get_db_connection()
        query = text(f"""
            SELECT
                COUNT("Transaction_ID") as total_transacoes,
                COALESCE(SUM(CASE WHEN "Fraud_Label" = 1 THEN 1 ELSE 0 END), 0) as total_fraudes,
                COALESCE(AVG("Transaction_Amount"), 0) as valor_medio
            FROM {NOME_DA_VIEW}
            WHERE "Timestamp" >= :data_inicio AND "Timestamp" < :data_fim
        """)
        params = {"data_inicio": data_inicio, "data_fim": data_fim_exclusiva}
        df_resumo = pd.read_sql(query, engine, params=params)

        if not df_resumo.empty:
            return df_resumo.iloc[0].to_dict()
        return {'total_transacoes': 0, 'total_fraudes': 0, 'valor_medio': 0}
    except Exception as e:
        st.error(f"Falha ao obter resumo do período: {e}")
        return None

# --- Funções de Análise e KPI ---

def calcular_kpis_gerais(df: pd.DataFrame):
    """
    Calcula um conjunto de KPIs a partir de um DataFrame.
    IMPORTANTE: Esta função espera um DataFrame com os nomes de coluna PADRONIZADOS.
    """
    if df.empty:
        return {k: 0 for k in [
            'valor_total', 'num_transacoes', 'ticket_medio', 'num_clientes',
            'num_fraudes', 'valor_fraudes', 'taxa_fraude_vol', 'taxa_fraude_val',
            'ticket_medio_fraude', 'risco_medio_fraudes', 'risco_medio_legitimas'
        ]}

    # Nomes padronizados a serem usados nos cálculos
    col_id_transacao = 'Transaction_ID'
    col_valor = 'Transaction_Amount'
    col_fraude = 'Fraud_Label'
    col_id_cliente = 'User_ID'
    col_risco = 'Risk_Score'

    # Cálculos base
    num_transacoes = df[col_id_transacao].nunique()
    valor_total = df[col_valor].sum()
    df_fraude = df[df[col_fraude] == 1]
    df_legitima = df[df[col_fraude] == 0]
    num_fraudes = len(df_fraude)

    # Dicionário de KPIs
    kpis = {
        'valor_total': valor_total,
        'num_transacoes': num_transacoes,
        'ticket_medio': df[col_valor].mean(),
        'num_clientes': df[col_id_cliente].nunique(),
        'num_fraudes': num_fraudes,
        'valor_fraudes': df_fraude[col_valor].sum(),
        'taxa_fraude_vol': (num_fraudes / num_transacoes) * 100 if num_transacoes > 0 else 0,
        'taxa_fraude_val': (df_fraude[col_valor].sum() / valor_total) * 100 if valor_total > 0 else 0,
        'ticket_medio_fraude': df_fraude[col_valor].mean() if num_fraudes > 0 else 0,
        'risco_medio_fraudes': df_fraude[col_risco].mean() if num_fraudes > 0 else 0,
        'risco_medio_legitimas': df_legitima[col_risco].mean() if not df_legitima.empty else 0
    }
    return kpis

# --- Funções de Visualização ---

def criar_mapa_cluster(df_filtrado: pd.DataFrame):
    """Cria um mapa de clusters a partir de um DataFrame filtrado com nomes de colunas padronizados."""
    colunas_necessarias = ['Latitude', 'Longitude', 'Transaction_Amount', 'Risk_Score']
    if df_filtrado.empty or not all(col in df_filtrado.columns for col in colunas_necessarias):
        return None

    # Garante que as colunas de geolocalização são numéricas
    df_mapa = df_filtrado.copy()
    df_mapa['Latitude'] = pd.to_numeric(df_mapa['Latitude'], errors='coerce')
    df_mapa['Longitude'] = pd.to_numeric(df_mapa['Longitude'], errors='coerce')
    df_mapa.dropna(subset=['Latitude', 'Longitude'], inplace=True)

    if df_mapa.empty: return None

    mapa = folium.Map(location=[df_mapa['Latitude'].mean(), df_mapa['Longitude'].mean()], zoom_start=4, tiles="CartoDB positron")
    cluster = MarkerCluster().add_to(mapa)

    # Renomeia colunas para exibição no popup usando o MAPA_NOMES_COLUNAS
    df_renomeado = df_mapa.rename(columns=MAPA_NOMES_COLUNAS)
    col_valor_disp = MAPA_NOMES_COLUNAS.get('Transaction_Amount', 'Valor')
    col_risco_disp = MAPA_NOMES_COLUNAS.get('Risk_Score', 'Risco')

    for _, row in df_renomeado.iterrows():
        popup_text = f"<b>{col_valor_disp}:</b> {row[col_valor_disp]:.2f}<br><b>{col_risco_disp}:</b> {row[col_risco_disp]:.2f}"
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=folium.Popup(popup_text, max_width=200)
        ).add_to(cluster)
    return mapa

# --- Funções Utilitárias ---

# Adicione esta função ao seu arquivo func/functions.py

def criar_grafico_dispersao_cliente(df_cliente: pd.DataFrame):
    """
    Cria um gráfico de dispersão interativo das transações de um cliente,
    destacando outliers e mostrando uma linha de tendência.
    Espera um DataFrame com nomes de colunas originais do banco.
    """
    if df_cliente.empty:
        return None

    # Identifica outliers usando o método IQR na coluna 'Transaction_Amount'
    Q1 = df_cliente['Transaction_Amount'].quantile(0.25)
    Q3 = df_cliente['Transaction_Amount'].quantile(0.75)
    IQR = Q3 - Q1
    limite_superior = Q3 + 1.5 * IQR
    
    # Cria uma cópia do DataFrame para não alterar o original
    df_plot = df_cliente.copy()
    
    # Adiciona uma coluna 'Análise' para colorir os pontos
    df_plot['Análise'] = np.where(df_plot['Transaction_Amount'] > limite_superior, 'Outlier', 'Normal')

    # Cria o gráfico de dispersão com Plotly Express
    fig = px.scatter(
        df_plot,
        x='Timestamp',
        y='Transaction_Amount',
        color='Análise',
        color_discrete_map={
            'Normal': '#0d47a1',  # Azul para transações normais
            'Outlier': '#d84315'  # Vermelho/Laranja para outliers
        },
        trendline="ols",  # Adiciona uma linha de tendência
        title="Comportamento de Compra do Cliente e Outliers",
        labels={
            "Timestamp": "Data da Transação",
            "Transaction_Amount": "Valor da Transação (R$)"
        },
        hover_data=['Risk_Score', 'Transaction_Type'] # Mostra mais infos ao passar o mouse
    )
    
    fig.update_layout(
        title_x=0.5, 
        legend_title_text='Análise da Transação'
    )
    
    return fig

def paginar_dataframe(df: pd.DataFrame, page_size=10, key="pagination"):
    """Cria uma interface de paginação para um DataFrame no Streamlit."""
    if df.empty:
        st.warning("Não há dados para exibir.")
        return
    
    # Inicializa o estado da página se não existir
    if f'{key}_page' not in st.session_state:
        st.session_state[f'{key}_page'] = 0

    total_rows = len(df)
    total_pages = (total_rows // page_size) if total_rows % page_size == 0 else (total_rows // page_size) + 1
    
    # Garante que o número da página seja válido
    page_number = max(0, min(st.session_state[f'{key}_page'], total_pages - 1))
    
    start_idx = page_number * page_size
    end_idx = min(start_idx + page_size, total_rows)
    df_slice = df.iloc[start_idx:end_idx]

    # Exibe o DataFrame fatiado
    st.dataframe(df_slice)

    # Controles de Paginação
    col1, col2, col3 = st.columns([2, 3, 2])
    
    if col1.button("⬅️ Anterior", key=f"{key}_prev", disabled=(page_number == 0), use_container_width=True):
        st.session_state[f'{key}_page'] -= 1
        st.rerun()
        
    col2.markdown(f"<div style='text-align: center; margin-top: 5px;'>Página {page_number + 1} de {total_pages}</div>", unsafe_allow_html=True)

    if col3.button("Próximo ➡️", key=f"{key}_next", disabled=(page_number >= total_pages - 1), use_container_width=True):
        st.session_state[f'{key}_page'] += 1
        st.rerun()