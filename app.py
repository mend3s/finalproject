import pandas as pd
import streamlit as st
import streamlit_pills as stp
import seaborn as sns
import matplotlib.pyplot as plt
from func import functions 
import sqlite3
import plotly.express as px
import plotly.graph_objects as go


st.set_page_config(
    page_title="Credit Card Analises",
    page_icon="📊",
    layout="wide",
)

#ESTILIZANDO OS CARDS DE DASHBOARD
st.markdown("""
<style>
/* --- ESTILO BASE DO CARD --- */
.kpi-card {
    position: relative; /* Necessário para o tooltip */
    background-color: #FFFFFF;
    padding: 20px;
    border-radius: 10px;
    border-left: 8px solid #000; /* Borda padrão, será sobrescrita pela cor específica */
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.5); /* Sombra mais destacada */
    height: 160px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    transition: all 0.3s ease;
    color: #333333; /* Cor do texto padrão escura para contraste com fundo branco */
}
.kpi-card:hover {
    transform: translateY(-5px); /* Efeito de "levantar" ao passar o mouse */
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
}
/* Estilo dos textos dentro do card */
.kpi-card h3 { margin: 0; font-size: 1.1em; text-transform: uppercase; font-weight: 600; color: #666666; }
.kpi-card h2 { margin: 5px 0; font-size: 2.1em; font-weight: bolder; color: #2A2A2A; }

/* --- PALETA DE CORES PARA AS BORDAS --- */
/* Cores da primeira fileira (baseadas na cor do texto do seu código) */
.kpi-card.color-1 { border-left-color: #0d47a1; } /* Receita Total */      
            


/* --- ESTILO DO TOOLTIP (DICA NO HOVER) --- */
.kpi-card .tooltip-text {
    visibility: hidden;
    width: 220px;
    background-color: #333;
    color: #fff;
    text-align: center;
    border-radius: 6px;
    padding: 8px;
    position: absolute;
    z-index: 1;
    bottom: 110%;
    left: 50%;
    margin-left: -110px;
    opacity: 0;
    transition: opacity 0.3s;
}
.kpi-card:hover .tooltip-text {
    visibility: visible;
    opacity: 1;
}
</style>
""", unsafe_allow_html=True)


st.title("DASHBOARD")
opcoes_menu = ["Visão Geral", "Analise Exploratoria", "Análise Temporal"]
icones_menu = ["💡", "💰", "⌛"] # Ícones são usados apenas para display nos pills

if 'pagina_selecionada' not in st.session_state:
    if opcoes_menu: # Garante que há opções
        st.session_state.pagina_selecionada = opcoes_menu[0]
    else:
        st.session_state.pagina_selecionada = None

pagina_atual = None

default_index = 0
if st.session_state.pagina_selecionada and opcoes_menu:
    try:
        default_index = opcoes_menu.index(st.session_state.pagina_selecionada)
    except ValueError:
        if opcoes_menu:
            st.session_state.pagina_selecionada = opcoes_menu[0]
            default_index = 0
        else:
            st.session_state.pagina_selecionada = None

# Renderiza os pills
if opcoes_menu:
    pagina_atual = stp.pills(
        label="Navegue pelo Dashboard:",
        options=opcoes_menu,
        icons=icones_menu,
        index=default_index,
        key="menu_pills_dashboard_acai"
    )
    # Atualiza o session_state com a nova seleção do usuário
    st.session_state.pagina_selecionada = pagina_atual
else:
    st.info("Nenhuma seção disponível para navegação.")
    # Garante que pagina_atual seja o que está em session_state se não houver pills para renderizar
    pagina_atual = st.session_state.get('pagina_selecionada')


# --- Conteúdo das Páginas ---
if pagina_atual == "Visão Geral":
    st.header(f"Visão Geral do Negócio 💡")

elif pagina_atual == "Análise Exploratoria":
    st.header(f"Graficos para análise exploratoria💰")