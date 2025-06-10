# app.py
import numpy as np
# Importa o nosso arquivo 'api_dados.py' e o apelida de 'api'
import func.functions as api
# --- Configuração da Página ---
import pandas as pd
import streamlit as st
import streamlit_pills as stp
import seaborn as sns
import matplotlib.pyplot as plt
#from func import functions  # Removido se 'functions' não estiver sendo usado ainda
import sqlite3
import plotly.express as px
import plotly.graph_objects as go

# --- Configuração da Página ---
st.set_page_config(
    page_title="Credit Card Analyses",
    page_icon="🕵️",
    layout="wide",
)

# --- Estilos CSS ---
# (Seu código CSS continua o mesmo, omitido aqui para brevidade)
st.markdown("""
<style>
/* --- ESTILO BASE DO CARD --- */
.kpi-card {
    position: relative;
    background-color: #FFFFFF;
    padding: 20px;
    border-radius: 10px;
    border-left: 8px solid #000;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.5);
    height: 160px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    transition: all 0.3s ease;
    color: #333333;
}
.kpi-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
}
.kpi-card h3 { margin: 0; font-size: 1.1em; text-transform: uppercase; font-weight: 600; color: #666666; }
.kpi-card h2 { margin: 5px 0; font-size: 2.1em; font-weight: bolder; color: #2A2A2A; }
.kpi-card.color-1 { border-left-color: #0d47a1; }
/* (Resto do seu CSS...) */
</style>
""", unsafe_allow_html=True)


# --- Título Principal ---
st.title("🕵️ DASHBOARD DE ANÁLISE DE FRAUDES")


# --- Lógica de Navegação ---
# CORREÇÃO 1: Adicionado um ícone para a quarta opção do menu.
opcoes_menu = ["Visão Geral", "Analise Exploratoria", "Análise Direcionada", "Modelagem Preditiva"]
icones_menu = ["💡", "🔬", "🎯", "⚙️"] # 4 opções, 4 ícones

# MELHORIA 1: Lógica de inicialização simplificada
if 'pagina_selecionada' not in st.session_state:
    st.session_state.pagina_selecionada = opcoes_menu[0]

# O componente 'pills' agora gerencia a seleção.
pagina_atual = stp.pills(
    label="Navegue pelas fases do projeto:",
    options=opcoes_menu,
    icons=icones_menu,
    # A chave do componente foi renomeada para ser mais descritiva.
    key="menu_navegacao",
    # Usamos o estado da sessão para manter a seleção consistente.
    index=opcoes_menu.index(st.session_state.pagina_selecionada)
)
# Atualiza o estado da sessão com a seleção atual do usuário.
st.session_state.pagina_selecionada = pagina_atual


# --- Conteúdo das Páginas (Estrutura Corrigida e Completa) ---
# CORREÇÃO 2: A estrutura if/elif agora corresponde exatamente às opções do menu.
if pagina_atual == "Visão Geral":
    st.header("💡 Visão Geral do Negócio")
    df_principal = api.carregar_dados()
     # 1. Análise e KPIs de Outliers
    df_outliers_valor, cont_outliers_valor, _ = api.identificar_outliers(df_principal, 'Transaction_Amount')
    df_outliers_dist, cont_outliers_dist, _ = api.identificar_outliers(df_principal, 'Transaction_Distance')

    st.subheader("Métricas de Anomalias")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_valor_anomalo = df_outliers_valor['Transaction_Amount'].sum() if not df_outliers_valor.empty else 0
        st.markdown(f"<div class='kpi-card color-4'><h3>Valor Anômalo Total</h3><h2>R$ {total_valor_anomalo:,.2f}</h2></div>", unsafe_allow_html=True)

    with col2:
        st.markdown(f"<div class='kpi-card color-4'><h3>Nº de Trans. Anômalas</h3><h2>{cont_outliers_valor}</h2></div>", unsafe_allow_html=True)

    with col3:
        maior_distancia = df_outliers_dist['Transaction_Distance'].max() if not df_outliers_dist.empty else 0
        st.markdown(f"<div class='kpi-card color-1'><h3>Maior Distância</h3><h2>{maior_distancia:,.1f} km</h2></div>", unsafe_allow_html=True)

    with col4:
        st.markdown(f"<div class='kpi-card color-1'><h3>Nº de Trans. Distantes</h3><h2>{cont_outliers_dist}</h2></div>", unsafe_allow_html=True)

    st.divider()

    # 2. Visualização Interativa de Outliers
    st.subheader("Visualização de Distribuição e Outliers")
    colunas_para_boxplot = ['Transaction_Amount', 'Transaction_Distance', 'Account_Balance', 'Daily_Transaction_Count']
    coluna_selecionada = st.selectbox("Selecione uma métrica para analisar:", colunas_para_boxplot)
    
    fig_boxplot = api.criar_boxplot_interativo(df_principal, coluna_selecionada)
    st.plotly_chart(fig_boxplot, use_container_width=True)

    st.divider()

    # 3. Tabela de Outliers para Ação
    st.subheader("Transações com Valor Anômalo para Investigação")
    st.info("A tabela abaixo lista as transações cujo valor foi identificado como um outlier estatístico.")
    
    colunas_para_exibir = ['Transaction_ID', 'User_ID', 'Transaction_Amount', 'Transaction_Distance', 'Risk_Score', 'Timestamp']
    st.dataframe(df_outliers_valor[colunas_para_exibir].sort_values('Transaction_Amount', ascending=False), use_container_width=True, hide_index=True)

elif pagina_atual == "Analise Exploratoria":
    # MELHORIA 2: Conteúdo da página agora está corretamente nomeado e estruturado.
    st.header("🔬 Análise Exploratória de Dados (EDA)")
    st.markdown("Diagnóstico dos dados para entender suas características, distribuições e relações iniciais.")
    # (Aqui você pode inserir o código da Análise Exploratória que desenvolvemos anteriormente)
    st.info("Espaço reservado para os gráficos da Análise Exploratória: Visão Geral do Dataset, Análise Univariada e Bivariada.")

elif pagina_atual == "Análise Direcionada":
    st.header("🎯 Análise Direcionada de Fraude")
    st.markdown("Investigação focada em responder perguntas de negócio específicas sobre os padrões de fraude.")
    st.info("Espaço reservado para os gráficos da Análise Direcionada: Análise por Canal, Contexto, Comportamento, etc.")

elif pagina_atual == "Modelagem Preditiva":
    # Adicionada a condição que faltava.
    st.header("⚙️ Modelagem Preditiva")
    st.markdown("Construção e avaliação de modelos de Machine Learning para prever transações fraudulentas.")
    st.info("Espaço reservado para os resultados da Modelagem Preditiva: Matriz de Confusão, Curva ROC, etc.")