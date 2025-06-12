# Arquivo: app.py
import pandas as pd
import streamlit as st
import streamlit_pills as stp
import func.functions as api
from streamlit_folium import st_folium
import plotly.express as px

# --- Configuração da Página e CSS ---
st.set_page_config(page_title="Análise de Fraudes", page_icon="🕵️", layout="wide")
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

# --- CARREGAMENTO OTIMIZADO ---
# A chamada agora é para a função que lê a tabela pré-processada
df_completo = api.carregar_dados_otimizados()
if df_completo.empty:
    st.stop()

# --- NAVEGAÇÃO ---
opcoes_menu = ["Visão Geral", "Análise Geográfica", "Análise Exploratória"]
icones_menu = ["💡", "🗺️", "🔬"]
pagina_atual = stp.pills(label="Navegue pelas fases do projeto:", options=opcoes_menu, icons=icones_menu)

# --- PÁGINAS ---

if pagina_atual == "Visão Geral":
    st.header("💡 Resumo Executivo de Segurança e Operações")

    # --- Filtro de Data ---
    col1, col2 = st.columns(2)
    with col1:
        # Garante que o valor padrão não cause erro se o df for vazio no primeiro carregamento
        data_minima = df_completo['Timestamp'].min().date() if not df_completo.empty else None
        data_inicio = st.date_input("Data de Início", data_minima)
    with col2:
        data_maxima = df_completo['Timestamp'].max().date() if not df_completo.empty else None
        data_fim = st.date_input("Data de Fim", data_maxima)

    # Converte datas para datetime para filtragem
    if data_inicio and data_fim:
        data_inicio_dt = pd.to_datetime(data_inicio)
        # Adiciona 1 dia para incluir a data final na seleção
        data_fim_dt = pd.to_datetime(data_fim) + pd.Timedelta(days=1)
        
        # Filtra o DataFrame com base no período selecionado
        df_filtrado = df_completo[(df_completo['Timestamp'] >= data_inicio_dt) & (df_completo['Timestamp'] < data_fim_dt)]

        if df_filtrado.empty:
            st.warning("Não há dados para o período selecionado.")
        else:
            # Calcula os KPIs com base nos dados filtrados
            kpis = api.calcular_kpis_gerais(df_filtrado)

            # --- ALTERADO: KPIs de volta para o formato HTML ---
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        with kpi1:
                st.markdown(f"<div class='kpi-card color-1'><h3>Valor Total Transacionado</h3><h2>R$ {kpis['valor_total']:,.2f}</h2></div>", unsafe_allow_html=True)
        with kpi2:
                st.markdown(f"<div class='kpi-card color-4'><h3>Volume de Fraudes</h3><h2>{kpis['num_fraudes']:}</h2></div>", unsafe_allow_html=True)
        with kpi3:
                st.markdown(f"<div class='kpi-card color-4'><h3>Taxa de Fraude (%)</h3><h2>{kpis['taxa_fraude_vol']:.2f}%</h2></div>", unsafe_allow_html=True)
        with kpi4:
                st.markdown(f"<div class='kpi-card color-4'><h3>Valor Perdido</h3><h2>R$ {kpis['valor_fraudes']:,.2f}</h2></div>", unsafe_allow_html=True)

        st.divider()

            # --- Gráfico de Tendência (MANTIDO) ---
        st.subheader("Tendência de Transações e Fraudes")
            
        @st.cache_data
        def criar_grafico_tendencia(df):
            df_diario = df.set_index('Timestamp').resample('D').agg(
                Total_Transacoes=('Transaction_ID', 'count'),
                Total_Fraudes=('Fraud_Label', 'sum')
            ).reset_index()
                
            fig = px.line(df_diario, x='Timestamp', y=['Total_Transacoes', 'Total_Fraudes'],
                              title="Transações Totais vs. Fraudes por Dia",
                              labels={'Timestamp': 'Data', 'value': 'Número de Transações'},
                              color_discrete_map={'Total_Transacoes': '#0d47a1', 'Total_Fraudes': '#d84315'})
            return fig

            fig_tendencia = criar_grafico_tendencia(df_filtrado)
            st.plotly_chart(fig_tendencia, use_container_width=True)
    else:
        st.error("Por favor, selecione uma data de início e fim.")
# Outras páginas (Análise Geográfica, etc.) podem continuar como estavam...
elif pagina_atual == "Análise Geográfica":
    st.header("🗺️ Análise Geográfica Agregada")
    st.info("Explore o volume e a taxa de fraude por localização. O tamanho do círculo indica o volume de transações e a cor indica o risco de fraude.")

    # --- Filtros para o mapa ---
    col1, col2 = st.columns(2)
    with col1:
        tipos_transacao = ['Todos'] + sorted(df_completo['Transaction_Type'].unique())
        tipo_selecionado = st.selectbox("Filtrar por Tipo de Transação:", tipos_transacao)
    with col2:
        status_fraude = {'Todos': None, 'Apenas Fraudes': 1, 'Apenas Legítimas': 0}
        status_selecionado_key = st.selectbox("Filtrar por Status:", options=list(status_fraude.keys()))
        status_selecionado_value = status_fraude[status_selecionado_key]

    # Aplica os filtros
    df_filtrado = df_completo.copy()
    if tipo_selecionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Transaction_Type'] == tipo_selecionado]
    if status_selecionado_value is not None:
        df_filtrado = df_filtrado[df_filtrado['Fraud_Label'] == status_selecionado_value]

    # Chama a NOVA função de mapa agregado
    mapa_agregado = api.criar_mapa_agregado_por_localizacao(df_filtrado)
    
    if mapa_agregado:
        st.success(f"Exibindo dados agregados de {len(df_filtrado):,} transações.")
        st_folium(mapa_agregado, use_container_width=True, height=600)
    else:
        st.warning("Não há dados para exibir no mapa com os filtros selecionados.")