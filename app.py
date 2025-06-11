import pandas as pd
import streamlit as st
import streamlit_pills as stp
import func.functions as api
from streamlit_folium import st_folium
import plotly.express as px

# --- Configuração da Página ---
st.set_page_config(page_title="Análise de Fraudes", page_icon="🕵️", layout="wide")

# --- Estilos CSS ---
st.markdown("""
<style>
.kpi-card {
    position: relative; background-color: #FFFFFF; padding: 20px; border-radius: 10px; border: 0.5px solid #DDDDDD;  
    border-left: 8px solid #000; box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);  
    height: 160px; display: flex; flex-direction: column; justify-content: center;
}
.kpi-card h3 { font-size: 1.1em; text-transform: uppercase; font-weight: 600; color: #666666; }
.kpi-card h2 { font-size: 2.1em; font-weight: bolder; color: #2A2A2A; }
.kpi-card.color-1 { border-left-color: #0d47a1; } /* Azul - Neutro/Info */
.kpi-card.color-2 { border-left-color: #2e7d32; } /* Verde - Bom Desempenho */
.kpi-card.color-4 { border-left-color: #d84315; } /* Laranja/Vermelho - Alerta/Ruim */
</style>
""", unsafe_allow_html=True)

st.title("🕵️ DASHBOARD DE ANÁLISE DE FRAUDES")

# --- CARREGAMENTO CENTRALIZADO ---
# A função agora carrega os dados brutos, sem traduções.
df_completo = api.carregar_dados_gerais()
if df_completo.empty:
    st.error("Não foi possível carregar os dados. Verifique a conexão com o banco.")
    st.stop()

# --- NAVEGAÇÃO PRINCIPAL ---
opcoes_menu = ["Visão Geral", "Análise Geográfica", "Análise Exploratória"]
icones_menu = ["💡", "🗺️", "🔬"]
pagina_atual = stp.pills(label="Navegue pelas fases do projeto:", options=opcoes_menu, icons=icones_menu)

# --- CONTEÚDO DAS PÁGINAS ---

if pagina_atual == "Visão Geral":
    st.header("💡 Resumo Executivo de Segurança e Operações")
    
    # A função de KPIs agora trabalha com os dados brutos
    kpis = api.calcular_kpis_gerais(df_completo)
    
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='kpi-card color-1'><h3>Valor Total Transacionado</h3><h2>R$ {kpis['valor_total']:,.2f}</h2></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='kpi-card color-1'><h3>Nº Total de Transações</h3><h2>{kpis['num_transacoes']:,}</h2></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='kpi-card color-4'><h3>Fraudes Confirmadas</h3><h2>{kpis['num_fraudes']:,}</h2></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div class='kpi-card color-4'><h3>Valor Perdido</h3><h2>R$ {kpis['valor_fraudes']:,.2f}</h2></div>", unsafe_allow_html=True)
    
    st.markdown("<hr style='border:1px solid #FFFFFF20'>", unsafe_allow_html=True)
    
    col5, col6, col7, col8 = st.columns(4)
    with col5:
        st.markdown(f"<div class='kpi-card color-1'><h3>Ticket Médio Geral</h3><h2>R$ {kpis['ticket_medio']:,.2f}</h2></div>", unsafe_allow_html=True)
    with col6:
        st.markdown(f"<div class='kpi-card color-4'><h3>Taxa de Fraude (Volume)</h3><h2>{kpis['taxa_fraude_vol']:.2f}%</h2></div>", unsafe_allow_html=True)
    with col7:
        st.markdown(f"<div class='kpi-card color-2'><h3>Score Médio (Fraudes)</h3><h2>{kpis['risco_medio_fraudes']:.2f}</h2></div>", unsafe_allow_html=True)
    with col8:
        st.markdown(f"<div class='kpi-card color-2'><h3>Score Médio (Legítimas)</h3><h2>{kpis['risco_medio_legitimas']:.2f}</h2></div>", unsafe_allow_html=True)

elif pagina_atual == "Análise Geográfica":
    st.header("🗺️ Análise de Transações por Cliente")
    st.info("Selecione um cliente para visualizar suas transações.")

    # Usa o nome da coluna diretamente do banco
    lista_clientes = sorted(df_completo['User_ID'].unique())
    
    cliente_selecionado = st.selectbox(
        'Selecione o cliente (User_ID):',
        options=lista_clientes,
        placeholder="Digite ou selecione um User_ID",
        index=None
    )

    if cliente_selecionado:
        # Filtra o DataFrame principal, não precisa de nova busca no banco
        df_cliente = df_completo[df_completo['User_ID'] == cliente_selecionado]

        if not df_cliente.empty:
            st.success(f"Exibindo {len(df_cliente)} transações para o cliente selecionado.")
            
            map_tab, data_tab, chart_tab = st.tabs(["Mapa de Clusters", "Tabela de Dados", "Análise de Compras"])

            with map_tab:
                mapa_clusters = api.criar_mapa_cluster(df_cliente)
                if mapa_clusters:
                    st_folium(mapa_clusters, use_container_width=True, height=500)
            
            with data_tab:
                st.dataframe(df_cliente, use_container_width=True, hide_index=True)

            with chart_tab:
                fig_dispersao = api.criar_grafico_dispersao_cliente(df_cliente)
                if fig_dispersao:
                    st.plotly_chart(fig_dispersao, use_container_width=True)
        else:
            st.warning("Nenhuma transação encontrada para este cliente.")
