
import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from matplotlib.patches import Patch
import folium
import streamlit as st
from streamlit_folium import st_folium
from streamlit_folium import folium_static


conn = sqlite3.connect("dados_voo.db")
cursor = conn.cursor()

#pageconfig
st.set_page_config(
    page_title="Análise de Dados de Voos",
    page_icon="✈️",
    layout="wide"
)

# CSS customizado apenas para a aba home
home_css = """
<style>
    /* Metrics styling */
    [data-testid="metric-container"] {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
    }
    
    /* Big numbers styling */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .metric-card h3 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: bold;
        color: white;
    }
    
    .metric-card p {
        margin: 0.5rem 0 0 0;
        font-size: 1rem;
        opacity: 0.9;
        color: white;
    }
    
    /* Section headers */
    .section-header {
        background: linear-gradient(90deg, #1e40af 0%, #3b82f6 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 2rem 0 1rem 0;
        text-align: center;
    }
    
    /* Chart containers */
    .chart-container {
        background-color: white;
        padding: 1.5rem;
        border-radius: 0.75rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
    }
    
    .chart-container h4 {
        color: #1e40af;
        text-align: center;
        margin-bottom: 1rem;
    }
</style>
"""

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
    st.session_state.aba_ativa = 'home'  
    
st.sidebar.button("📌 Análises Operacionais", on_click=lambda: st.session_state.update(aba_ativa='home'))
st.sidebar.button("🔍 Painel de eficiência", on_click=lambda: st.session_state.update(aba_ativa='painel_eficiencia'))
st.sidebar.button("⛽ Eficiencia Combustivel", on_click=lambda: st.session_state.update(aba_ativa='eficiencia_comb'))
st.sidebar.button("📊 KPIs e Métricas Gerenciais", on_click=lambda: st.session_state.update(aba_ativa='kpis'))
st.sidebar.button("🧑 Cliente", on_click=lambda: st.session_state.update(aba_ativa='cliente'))
st.sidebar.button("🚫 Análise de Voos Improdutivos Combustivel", on_click=lambda: st.session_state.update(aba_ativa='voos_impro'))
st.sidebar.button("🚫 Análise de Voos Improdutivos Passageiros/Bagagem", on_click=lambda: st.session_state.update(aba_ativa='voos_impro_pas'))
st.sidebar.button("🌎 Rota e Geografia", on_click=lambda: st.session_state.update(aba_ativa='rotas'))
st.sidebar.button("📦 Produtos", on_click=lambda: st.session_state.update(aba_ativa='produtos'))

# Função para criar big numbers
def create_big_number_card(title, value, subtitle=""):
    st.markdown(f"""
    <div class="metric-card">
        <h3>{value}</h3>
        <p>{title}</p>
        {f'<small style="opacity: 0.8; color: white;">{subtitle}</small>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)

if st.session_state.aba_ativa == 'home':
    def criar_selectbox_empresa(label, key, conn):
        """
        Cria um selectbox com nomes de empresas formatados e retorna a sigla selecionada
        """
        empresas_query = """
        SELECT DISTINCT e.empresa_sigla, e.empresa_nome 
        FROM voo v 
        JOIN empresa e ON v.empresa_sigla = e.empresa_sigla 
        ORDER BY e.empresa_nome
        """
        empresas_df = pd.read_sql_query(empresas_query, conn)
        
        # Criar dicionário para mapear display -> sigla
        empresa_map = {'Todas': 'Todas'}
        opcoes_display = ['Todas']
        
        for _, row in empresas_df.iterrows():
            display_name = f"{row['empresa_nome']} ({row['empresa_sigla']})"
            empresa_map[display_name] = row['empresa_sigla']
            opcoes_display.append(display_name)
        
        # Selectbox
        selecionada_display = st.selectbox(label, opcoes_display, key=key)
        
        # Retornar sigla
        return empresa_map[selecionada_display]
    
    # Aplicar CSS customizado apenas na home
    st.markdown(home_css, unsafe_allow_html=True)
    
    # Estilo personalizado da página 'home'
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

    # Header principal
    st.markdown("""
    <div class="section-header">
        <h1 style='margin: 0; font-size: 2.5rem;'>✈️ Dashboard de Análise de Voos</h1>
        <p style='margin: 0.5rem 0 0 0; opacity: 0.9;'>Visão geral dos dados operacionais</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Big Numbers - KPIs principais
    st.markdown("### 📊 Indicadores Principais")
    
    # Buscar dados para os KPIs
    query_kpis = """
    SELECT 
        COUNT(*) as total_voos,
        SUM(v.decolagens) as total_decolagens,
        SUM(v.distancia_voada_km) as total_distancia,
        SUM(v.combustivel_litros) as total_combustivel,
        SUM(v.horas_voadas) as total_horas,
        SUM(COALESCE(c.passageiros_pagos, 0)) as total_passageiros_pagos,
        SUM(COALESCE(c.passageiros_gratis, 0)) as total_passageiros_gratis,
        COUNT(DISTINCT v.empresa_sigla) as total_empresas,
        COUNT(DISTINCT v.aeroporto_origem_sigla) as total_aeroportos_origem
    FROM voo v
    LEFT JOIN carga_passageiros c ON v.voo_id = c.voo_id
    """
    
    kpis = pd.read_sql_query(query_kpis, conn).iloc[0]
    
    # Layout dos big numbers
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        create_big_number_card(
            "Total de Voos", 
            f"{int(kpis['total_voos']):,}",
            f"{int(kpis['total_decolagens']):,} decolagens"
        )
    
    with col2:
        total_passageiros = int(kpis['total_passageiros_pagos'] + kpis['total_passageiros_gratis'])
        create_big_number_card(
            "Total Passageiros", 
            f"{total_passageiros:,}",
            f"{int(kpis['total_passageiros_pagos']):,} pagos"
        )
    
    with col3:
        create_big_number_card(
            "Distância Total", 
            f"{int(kpis['total_distancia']/1000):,}K km",
            f"{int(kpis['total_horas']):,} horas voadas"
        )
    
    with col4:
        create_big_number_card(
            "Empresas Ativas", 
            f"{int(kpis['total_empresas'])}",
            f"{int(kpis['total_aeroportos_origem'])} aeroportos"
        )

    # --- Comparação Nacionais x Internacionais ---
    st.markdown("---")
    st.markdown("### 🌍 Comparação de Voos Nacionais vs Internacionais")

    query_nacional = """
        SELECT 
            'NACIONAL' as tipo_voo,
            COUNT(*) as total_voos,
            SUM(v.decolagens) as total_decolagens,
            SUM(v.distancia_voada_km) as total_distancia_km,
            SUM(v.combustivel_litros) as total_combustivel_litros,
            SUM(v.horas_voadas) as total_horas_voadas,
            SUM(c.passageiros_pagos) as total_passageiros_pagos,
            SUM(c.passageiros_gratis) as total_passageiros_gratis,
            AVG(v.distancia_voada_km) as media_distancia_km,
            AVG(v.combustivel_litros) as media_combustivel_litros
        FROM voo_nacional v
        LEFT JOIN carga_passageiros c ON v.voo_id = c.voo_id
        """
    query_internacional = """
        SELECT 
            'INTERNACIONAL' as tipo_voo,
            COUNT(*) as total_voos,
            SUM(v.decolagens) as total_decolagens,
            SUM(v.distancia_voada_km) as total_distancia_km,
            SUM(v.combustivel_litros) as total_combustivel_litros,
            SUM(v.horas_voadas) as total_horas_voadas,
            SUM(c.passageiros_pagos) as total_passageiros_pagos,
            SUM(c.passageiros_gratis) as total_passageiros_gratis,
            AVG(v.distancia_voada_km) as media_distancia_km,
            AVG(v.combustivel_litros) as media_combustivel_litros
        FROM voo_internacional v
        LEFT JOIN carga_passageiros c ON v.voo_id = c.voo_id
        """
    df_nacional = pd.read_sql_query(query_nacional, conn)
    df_internacional = pd.read_sql_query(query_internacional, conn)
    df_comparacao = pd.concat([df_nacional, df_internacional], ignore_index=True)

    col1, col2 = st.columns(2)
    col1, col2 = st.columns(2)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div style='background-color: white; padding: 1rem; border-radius: 0.75rem; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); margin: 0.5rem 0;'>
            <h3 style='color: #1e40af; text-align: center; margin-bottom: 0.8rem; font-size: 1.2rem;'>🇧🇷 Voos Nacionais</h3>
        """, unsafe_allow_html=True)
        if not df_nacional.empty:
            st.metric("Total Voos", f"{int(df_nacional['total_voos'].iloc[0]):,}")
            st.metric("Passageiros", f"{int(df_nacional['total_passageiros_pagos'].iloc[0]):,}")
            st.metric("Distância (km)", f"{df_nacional['total_distancia_km'].iloc[0]:,.0f}")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style='background-color: white; padding: 1rem; border-radius: 0.75rem; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); margin: 0.5rem 0;'>
            <h3 style='color: #1e40af; text-align: center; margin-bottom: 0.8rem; font-size: 1.2rem;'>🌐 Voos Internacionais</h3>
        """, unsafe_allow_html=True)
        if not df_internacional.empty:
            st.metric("Total Voos", f"{int(df_internacional['total_voos'].iloc[0]):,}")
            st.metric("Passageiros", f"{int(df_internacional['total_passageiros_pagos'].iloc[0]):,}")
            st.metric("Distância (km)", f"{df_internacional['total_distancia_km'].iloc[0]:,.0f}")
        st.markdown("</div>", unsafe_allow_html=True)
    # Gráficos principais com plotly
    st.markdown("---")
    st.markdown("### 📈 Análises Visuais")
    
    # Top empresas por voos
    query_top_empresas = """
    SELECT 
        e.empresa_sigla,
        e.empresa_nome,
        COUNT(*) as total_voos,
        SUM(COALESCE(c.passageiros_pagos, 0) + COALESCE(c.passageiros_gratis, 0)) as total_passageiros
    FROM voo v
    JOIN empresa e ON v.empresa_sigla = e.empresa_sigla
    LEFT JOIN carga_passageiros c ON v.voo_id = c.voo_id
    GROUP BY e.empresa_sigla, e.empresa_nome
    ORDER BY total_voos DESC
    LIMIT 10
    """
    
    df_top_empresas = pd.read_sql_query(query_top_empresas, conn)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style='background-color: white; padding: 1.5rem; border-radius: 0.75rem; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); margin: 1rem 0;'>
            <h4 style='color: #1e40af; text-align: center; margin-bottom: 1rem; font-size: 1.2rem;'>🏢 Top 10 Empresas por Voos</h4>
        """, unsafe_allow_html=True)
        
        fig_empresas = px.bar(
            df_top_empresas, 
            x='total_voos', 
            y='empresa_sigla',
            orientation='h',
            color='total_voos',
            color_continuous_scale='Blues',
            height=300
        )
        fig_empresas.update_layout(
            showlegend=False,
            margin=dict(l=0, r=0, t=0, b=0),
            font=dict(size=10)
        )
        fig_empresas.update_yaxes(categoryorder="total ascending")
        st.plotly_chart(fig_empresas, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background-color: white; padding: 1.5rem; border-radius: 0.75rem; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); margin: 1rem 0;'>
            <h4 style='color: #1e40af; text-align: center; margin-bottom: 1rem; font-size: 1.2rem;'>👥 Passageiros por Empresa</h4>
        """, unsafe_allow_html=True)
        
        fig_passageiros = px.bar(
            df_top_empresas, 
            x='total_passageiros', 
            y='empresa_sigla',
            orientation='h',
            color='total_passageiros',
            color_continuous_scale='Greens',
            height=300
        )
        fig_passageiros.update_layout(
            showlegend=False,
            margin=dict(l=0, r=0, t=0, b=0),
            font=dict(size=10)
        )
        fig_passageiros.update_yaxes(categoryorder="total ascending")
        st.plotly_chart(fig_passageiros, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # --- Filtros e análise por empresa (seção original mantida) ---
    st.markdown("---")
    st.markdown("### 🏢 Análise por Empresa Aérea")
    col_filtro1, col_filtro2 = st.columns(2)
    with col_filtro1:
        mes_selecionado = st.selectbox("Mês:", ['Todos'] + list(range(1, 13)), key="mes_empresa")

    with col_filtro2:
        nacionalidades = pd.read_sql_query("SELECT DISTINCT empresa_nacionalidade FROM empresa ORDER BY empresa_nacionalidade", conn)['empresa_nacionalidade'].tolist()
        nacionalidade_selecionada = st.selectbox("Nacionalidade:", ['Todas'] + nacionalidades, key="nacionalidade_empresa")

    # Query dinâmica
    where_conditions = []
    if mes_selecionado != 'Todos':
        where_conditions.append(f"v.mes = {mes_selecionado}")
    if nacionalidade_selecionada != 'Todas':
        where_conditions.append(f"e.empresa_nacionalidade = '{nacionalidade_selecionada}'")
    where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""

    query_empresas = f"""
        SELECT 
            e.empresa_sigla,
            e.empresa_nome,
            e.empresa_nacionalidade,
            COUNT(*) as total_voos,
            SUM(v.decolagens) as total_decolagens,
            SUM(c.passageiros_pagos + c.passageiros_gratis) as total_passageiros,
            AVG(c.passageiros_pagos + c.passageiros_gratis) as media_passageiros_por_voo,
            SUM(v.distancia_voada_km) as total_distancia,
            SUM(v.combustivel_litros) as total_combustivel
        FROM voo v
        JOIN empresa e ON v.empresa_sigla = e.empresa_sigla
        LEFT JOIN carga_passageiros c ON v.voo_id = c.voo_id
        {where_clause}
        GROUP BY e.empresa_sigla, e.empresa_nome, e.empresa_nacionalidade
        ORDER BY total_voos DESC
        """
    df_empresas = pd.read_sql_query(query_empresas, conn)

    if not df_empresas.empty:
        

        st.markdown("#### 📊 Tabela Resumo")
        df_display = df_empresas.copy()
        df_display = df_display.rename(columns={
            'empresa_sigla': 'Sigla',
            'empresa_nome': 'Nome da Empresa',
            'empresa_nacionalidade': 'Nacionalidade',
            'total_voos': 'Total Voos',
            'total_passageiros': 'Total Passageiros',
            'media_passageiros_por_voo': 'Média Pax/Voo',
            'total_distancia': 'Distância Total (km)'
        })
        st.dataframe(df_display[['Sigla', 'Nome da Empresa', 'Nacionalidade', 'Total Voos', 'Total Passageiros', 'Média Pax/Voo']], use_container_width=True)
    else:
        st.warning("⚠️ Nenhum dado encontrado para os filtros selecionados.")

    # # --- Nova seção: Total de Decolagens por Mês ---
    # st.markdown("### 🛫 Total de Decolagens por Mês")
    
    # # Filtros para decolagens
    # col_filtro1, col_filtro2 = st.columns(2)
    
    
    # with col_filtro1:
    #     # Buscar empresas para o selectbox
    #     empresas_query = """
    #     SELECT DISTINCT e.empresa_sigla, e.empresa_nome 
    #     FROM voo v 
    #     JOIN empresa e ON v.empresa_sigla = e.empresa_sigla 
    #     ORDER BY e.empresa_nome
    #     """
    #     empresas_df = pd.read_sql_query(empresas_query, conn)
    #     opcoes_empresas = ['Todas'] + [f"{row['empresa_nome']} ({row['empresa_sigla']})" for _, row in empresas_df.iterrows()]
    #     empresa_selecionada_display = st.selectbox("Empresa:", opcoes_empresas, key="empresa_decolagem")
    
    # # Extrair a sigla selecionada para usar nas queries
    # if empresa_selecionada_display != 'Todas':
    #     # Extrair sigla entre parênteses
    #     empresa_selecionada = empresa_selecionada_display.split('(')[1].replace(')', '')
    # else:
    #     empresa_selecionada = 'Todas'
    
    # with col_filtro2:
    #     tipos_voo = ['Todos', 'DOMÉSTICA', 'INTERNACIONAL']
    #     tipo_voo_selecionado = st.selectbox("Tipo de Voo:", tipos_voo, key="tipo_voo_decolagem")
    
    # # Construir query para decolagens
    # where_conditions_dec = []
    # if empresa_selecionada != 'Todas':
    #     where_conditions_dec.append(f"v.empresa_sigla = '{empresa_selecionada}'")
    # if tipo_voo_selecionado != 'Todos':
    #     where_conditions_dec.append(f"v.natureza = '{tipo_voo_selecionado}'")
    
    # where_clause_dec = "WHERE " + " AND ".join(where_conditions_dec) if where_conditions_dec else ""
    
    # query_decolagens = f"""
    # SELECT 
    #     v.ano,
    #     v.mes,
    #     SUM(v.decolagens) as total_decolagens,
    #     COUNT(*) as total_voos,
    #     AVG(v.decolagens) as media_decolagens_por_voo
    # FROM voo v
    # {where_clause_dec}
    # GROUP BY v.ano, v.mes
    # ORDER BY v.ano, v.mes
    # """
    
    # df_decolagens = pd.read_sql_query(query_decolagens, conn)
    
    # if not df_decolagens.empty:
    #     # Gráfico de linha temporal para decolagens
    #     col1, col2 = st.columns([3, 1])
        
    #     with col1:
    #         fig_decolagens = plt.figure(figsize=(14, 6))
            
    #         # Criar labels para o eixo X (sem usar pd.to_datetime)
    #         df_decolagens['mes_ano_label'] = df_decolagens['mes'].astype(str).str.zfill(2) + '/' + df_decolagens['ano'].astype(str)
            
    #         # Usar range numérico para o eixo X
    #         x_values = range(len(df_decolagens))
            
    #         plt.plot(x_values, df_decolagens['total_decolagens'], 
    #                 marker='o', linewidth=2, markersize=6, color='#FF6B6B')
    #         plt.title('Evolução das Decolagens por Mês', fontsize=14, fontweight='bold')
    #         plt.xlabel('Mês/Ano')
    #         plt.ylabel('Total de Decolagens')
    #         plt.grid(True, alpha=0.3)
            
    #         # Configurar labels do eixo X
    #         plt.xticks(x_values, df_decolagens['mes_ano_label'], rotation=45)
            
    #         # Adicionar valores nos pontos
    #         for i, (idx, row) in enumerate(df_decolagens.iterrows()):
    #             plt.annotate(f"{int(row['total_decolagens']):,}", 
    #                        (i, row['total_decolagens']),
    #                        textcoords="offset points", xytext=(0,10), ha='center', fontsize=8)
            
    #         plt.tight_layout()
    #         st.pyplot(fig_decolagens)
        
    #     with col2:
    #         st.markdown("**Resumo Decolagens:**")
    #         total_decolagens_periodo = df_decolagens['total_decolagens'].sum()
    #         media_mensal = df_decolagens['total_decolagens'].mean()
    #         mes_maior = df_decolagens.loc[df_decolagens['total_decolagens'].idxmax()]
            
    #         st.metric("Total no Período", f"{int(total_decolagens_periodo):,}")
    #         st.metric("Média Mensal", f"{int(media_mensal):,}")
    #         st.write(f"**Pico:** {int(mes_maior['mes'])}/{int(mes_maior['ano'])}")
    #         st.write(f"**Valor:** {int(mes_maior['total_decolagens']):,}")
        
    #     # Tabela de decolagens
    #     st.markdown("#### 📋 Tabela de Decolagens por Mês")
    #     df_decolagens_display = df_decolagens[['ano', 'mes', 'total_decolagens', 'total_voos', 'media_decolagens_por_voo']].copy()
    #     df_decolagens_display.columns = ['Ano', 'Mês', 'Total Decolagens', 'Total Voos', 'Média Decolagens/Voo']
    #     df_decolagens_display['Total Decolagens'] = df_decolagens_display['Total Decolagens'].apply(lambda x: f"{int(x):,}")
    #     df_decolagens_display['Total Voos'] = df_decolagens_display['Total Voos'].apply(lambda x: f"{int(x):,}")
    #     df_decolagens_display['Média Decolagens/Voo'] = df_decolagens_display['Média Decolagens/Voo'].apply(lambda x: f"{x:.2f}")
        
    #     st.dataframe(df_decolagens_display, use_container_width=True)
    # else:
    #     st.warning("⚠️ Nenhum dado de decolagens encontrado para os filtros selecionados.")

    # --- Nova seção: Distância Total por Rota/Empresa ---
    st.markdown("### 🗺️ Distância Total Voada por Rota e Empresa")
    
    # Filtros para distância
    col_filtro1, col_filtro2 = st.columns(2)
    
    with col_filtro1:
        # Buscar empresas com nome e sigla para distância
        empresas_dist_query = """
        SELECT DISTINCT e.empresa_sigla, e.empresa_nome 
        FROM voo v 
        JOIN empresa e ON v.empresa_sigla = e.empresa_sigla 
        ORDER BY e.empresa_nome
        """
        empresas_dist_df = pd.read_sql_query(empresas_dist_query, conn)
        
        # Criar lista de opções formatadas
        opcoes_empresas_dist = ['Todas'] + [f"{row['empresa_nome']} ({row['empresa_sigla']})" for _, row in empresas_dist_df.iterrows()]
        empresa_selecionada_dist_display = st.selectbox("Empresa:", opcoes_empresas_dist, key="empresa_distancia")
        
        # Extrair a sigla selecionada
        if empresa_selecionada_dist_display != 'Todas':
            empresa_selecionada_dist = empresa_selecionada_dist_display.split('(')[1].replace(')', '')
        else:
            empresa_selecionada_dist = 'Todas'
    
    with col_filtro2:
        tipos_voo_dist = ['Todos', 'DOMÉSTICA', 'INTERNACIONAL']
        tipo_voo_selecionado_dist = st.selectbox("Tipo de Voo:", tipos_voo_dist, key="tipo_voo_distancia")
    
    # Tabs para diferentes análises
    tab1, tab2 = st.tabs(["📊 Por Empresa", "🛣️ Por Rota"])
    
    with tab1:
        # Análise por empresa
        where_conditions_dist = []
        if empresa_selecionada_dist != 'Todas':
            where_conditions_dist.append(f"v.empresa_sigla = '{empresa_selecionada_dist}'")
        if tipo_voo_selecionado_dist != 'Todos':
            where_conditions_dist.append(f"v.natureza = '{tipo_voo_selecionado_dist}'")
        
        where_clause_dist = "WHERE " + " AND ".join(where_conditions_dist) if where_conditions_dist else ""
        
        query_distancia_empresa = f"""
        SELECT 
            v.empresa_sigla,
            e.empresa_nome,
            v.natureza,
            SUM(v.distancia_voada_km) as distancia_total,
            COUNT(*) as total_voos,
            AVG(v.distancia_voada_km) as distancia_media_por_voo
        FROM voo v
        JOIN empresa e ON v.empresa_sigla = e.empresa_sigla
        {where_clause_dist}
        GROUP BY v.empresa_sigla, e.empresa_nome, v.natureza
        ORDER BY distancia_total DESC
        """
        
        df_distancia_empresa = pd.read_sql_query(query_distancia_empresa, conn)
        
        if not df_distancia_empresa.empty:
            # Top 5 empresas em formato horizontal
            st.markdown("#### 🏆 Top 5 Empresas por Distância")
            top_5_empresas = df_distancia_empresa.head(5)
            
            cols = st.columns(5)
            for i, (_, row) in enumerate(top_5_empresas.iterrows()):
                with cols[i]:
                    st.markdown(f"""
                    <div style='background-color: #f8fafc; padding: 1rem; border-radius: 0.5rem; text-align: center; margin: 0.5rem 0;'>
                        <h4 style='color: #1e40af; margin: 0; font-size: 1rem;'>{i+1}º</h4>
                        <p style='margin: 0.25rem 0; font-weight: bold; font-size: 0.9rem;'>{row['empresa_sigla']}</p>
                        <p style='margin: 0; font-size: 0.8rem; color: #64748b;'>{row['natureza']}</p>
                        <p style='margin: 0.25rem 0; font-weight: bold; color: #1e40af; font-size: 0.9rem;'>{row['distancia_total']:,.0f} km</p>
                        <p style='margin: 0; font-size: 0.8rem; color: #64748b;'>{int(row['total_voos']):,} voos</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Gráfico de barras para distância por empresa
            top_15_empresas = df_distancia_empresa.head(15)
            
            fig_dist_empresa = plt.figure(figsize=(12, 6))
            bars = plt.barh(range(len(top_15_empresas)), 
                           top_15_empresas['distancia_total'], 
                           color=['#FF6B6B' if nat == 'DOMÉSTICA' else '#4ECDC4' for nat in top_15_empresas['natureza']])
            
            plt.yticks(range(len(top_15_empresas)), 
                      [f"{row['empresa_sigla']}\n({row['natureza']})" for _, row in top_15_empresas.iterrows()])
            plt.xlabel('Distância Total (km)')
            plt.title('Top 15 Empresas por Distância Total Voada')
            plt.gca().invert_yaxis()
            
            # Adicionar valores nas barras
            for i, bar in enumerate(bars):
                width = bar.get_width()
                plt.text(width + 0.01 * max(top_15_empresas['distancia_total']), 
                        bar.get_y() + bar.get_height()/2, 
                        f'{width:,.0f}', ha='left', va='center', fontsize=8)
            
            # Legenda
            legend_elements = [Patch(facecolor='#FF6B6B', label='Doméstica'),
                             Patch(facecolor='#4ECDC4', label='Internacional')]
            plt.legend(handles=legend_elements, loc='lower right')
            
            plt.tight_layout()
            st.pyplot(fig_dist_empresa)
            
            # Tabela resumo empresas
            st.markdown("#### 📋 Resumo por Empresa")
            df_empresa_display = df_distancia_empresa.copy()
            df_empresa_display['distancia_total'] = df_empresa_display['distancia_total'].apply(lambda x: f"{x:,.0f}")
            df_empresa_display['total_voos'] = df_empresa_display['total_voos'].apply(lambda x: f"{int(x):,}")
            df_empresa_display['distancia_media_por_voo'] = df_empresa_display['distancia_media_por_voo'].apply(lambda x: f"{x:,.0f}")
            
            df_empresa_display = df_empresa_display.rename(columns={
                'empresa_sigla': 'Sigla',
                'empresa_nome': 'Nome',
                'natureza': 'Tipo',
                'distancia_total': 'Distância Total (km)',
                'total_voos': 'Total Voos',
                'distancia_media_por_voo': 'Média km/Voo'
            })
            
            st.dataframe(df_empresa_display, use_container_width=True)
    
    with tab2:
        # Análise por rota
        where_conditions_rota = []
        if empresa_selecionada_dist != 'Todas':
            where_conditions_rota.append(f"v.empresa_sigla = '{empresa_selecionada_dist}'")
        if tipo_voo_selecionado_dist != 'Todos':
            where_conditions_rota.append(f"v.natureza = '{tipo_voo_selecionado_dist}'")
        
        where_clause_rota = "WHERE " + " AND ".join(where_conditions_rota) if where_conditions_rota else ""
        
        query_distancia_rota = f"""
        SELECT 
            v.aeroporto_origem_sigla,
            v.aeroporto_destino_sigla,
            ao.aeroporto_nome as nome_origem,
            ad.aeroporto_nome as nome_destino,
            v.natureza,
            SUM(v.distancia_voada_km) as distancia_total,
            COUNT(*) as total_voos,
            AVG(v.distancia_voada_km) as distancia_media,
            COUNT(DISTINCT v.empresa_sigla) as num_empresas
        FROM voo v
        LEFT JOIN aeroporto ao ON v.aeroporto_origem_sigla = ao.aeroporto_sigla
        LEFT JOIN aeroporto ad ON v.aeroporto_destino_sigla = ad.aeroporto_sigla
        {where_clause_rota}
        GROUP BY v.aeroporto_origem_sigla, v.aeroporto_destino_sigla, v.natureza
        ORDER BY distancia_total DESC
        """
        
        df_distancia_rota = pd.read_sql_query(query_distancia_rota, conn)
        
        if not df_distancia_rota.empty:
            # Criar coluna de rota
            df_distancia_rota['rota'] = df_distancia_rota['aeroporto_origem_sigla'] + ' → ' + df_distancia_rota['aeroporto_destino_sigla']
            
            # Top 5 rotas em formato horizontal
            st.markdown("#### 🛣️ Top 5 Rotas por Distância")
            top_5_rotas = df_distancia_rota.head(5)
            
            cols = st.columns(5)
            for i, (_, row) in enumerate(top_5_rotas.iterrows()):
                with cols[i]:
                    st.markdown(f"""
                    <div style='background-color: #f8fafc; padding: 1rem; border-radius: 0.5rem; text-align: center; margin: 0.5rem 0;'>
                        <h4 style='color: #1e40af; margin: 0; font-size: 1rem;'>{i+1}º</h4>
                        <p style='margin: 0.25rem 0; font-weight: bold; font-size: 0.9rem;'>{row['rota']}</p>
                        <p style='margin: 0; font-size: 0.8rem; color: #64748b;'>{row['natureza']}</p>
                        <p style='margin: 0.25rem 0; font-weight: bold; color: #1e40af; font-size: 0.9rem;'>{row['distancia_total']:,.0f} km</p>
                        <p style='margin: 0; font-size: 0.8rem; color: #64748b;'>{int(row['total_voos']):,} voos</p>
                        <p style='margin: 0; font-size: 0.8rem; color: #64748b;'>{int(row['num_empresas'])} empresas</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Gráfico de barras para rotas
            top_20_rotas = df_distancia_rota.head(20)
            
            fig_dist_rota = plt.figure(figsize=(12, 8))
            bars = plt.barh(range(len(top_20_rotas)), 
                           top_20_rotas['distancia_total'],
                           color=['#FF6B6B' if nat == 'DOMÉSTICA' else '#4ECDC4' for nat in top_20_rotas['natureza']])
            
            plt.yticks(range(len(top_20_rotas)), 
                      [f"{row['rota']}\n({row['natureza']})" for _, row in top_20_rotas.iterrows()])
            plt.xlabel('Distância Total (km)')
            plt.title('Top 20 Rotas por Distância Total Voada')
            plt.gca().invert_yaxis()
            
            # Adicionar valores nas barras
            for i, bar in enumerate(bars):
                width = bar.get_width()
                plt.text(width + 0.01 * max(top_20_rotas['distancia_total']), 
                        bar.get_y() + bar.get_height()/2, 
                        f'{width:,.0f}', ha='left', va='center', fontsize=7)
            
            # Legenda
            legend_elements = [Patch(facecolor='#FF6B6B', label='Doméstica'),
                             Patch(facecolor='#4ECDC4', label='Internacional')]
            plt.legend(handles=legend_elements, loc='lower right')
            
            plt.tight_layout()
            st.pyplot(fig_dist_rota)
            
            # Tabela resumo rotas
            st.markdown("#### 📋 Resumo por Rota")
            df_rota_display = df_distancia_rota.copy()
            df_rota_display['distancia_total'] = df_rota_display['distancia_total'].apply(lambda x: f"{x:,.0f}")
            df_rota_display['total_voos'] = df_rota_display['total_voos'].apply(lambda x: f"{int(x):,}")
            df_rota_display['distancia_media'] = df_rota_display['distancia_media'].apply(lambda x: f"{x:,.0f}")
            df_rota_display['num_empresas'] = df_rota_display['num_empresas'].apply(lambda x: f"{int(x)}")
            
            df_rota_display = df_rota_display.rename(columns={
                'rota': 'Rota',
                'natureza': 'Tipo',
                'distancia_total': 'Distância Total (km)',
                'total_voos': 'Total Voos',
                'distancia_media': 'Distância Média (km)',
                'num_empresas': 'Nº Empresas'
            })
            
            colunas_rota = ['Rota', 'Tipo', 'Distância Total (km)', 'Total Voos', 'Distância Média (km)', 'Nº Empresas']
            st.dataframe(df_rota_display[colunas_rota], use_container_width=True)
        else:
            st.warning("⚠️ Nenhum dado de rota encontrado para os filtros selecionados.")


if st.session_state.aba_ativa == 'painel_eficiencia':
    query = '''
        SELECT 
            v.empresa_sigla,
            e.empresa_nome,
            v.distancia_voada_km,
            v.combustivel_litros,
            v.decolagens,
            v.horas_voadas,
            v.mes
        FROM voo v
        JOIN empresa e ON v.empresa_sigla = e.empresa_sigla
        '''

    df = pd.read_sql_query(query, conn)

    st.markdown("""
        <style>
        html, body, [data-testid="stAppViewContainer"] {
            font-family: 'Inter', sans-serif;
            color: #1f2937;
            background-color: #f9fafb;
        }

        [data-testid="stAppViewContainer"] > .main {
            padding-left: 40px;
            padding-right: 40px;
            padding-top: 24px;
            padding-bottom: 48px;
            max-width: 1200px;
            margin: auto;
        }

        h1, h2, h3, h4 {
            color: #1e3a8a;
            font-weight: 800;
            margin-bottom: 0.5em;
        }

        .big-number {
            font-size: 2.6rem;
            font-weight: 800;
            color: #0f172a;
            margin-bottom: 4px;
            line-height: 1.2;
        }

        .small-label {
            font-size: 1rem;
            color: #475569;
            font-weight: 600;
            margin-bottom: 20px;
        }

        .metric-container {
            margin-bottom: 40px;
        }

        div.stSelectbox > div {
            background-color: #ffffff;
            padding: 16px 20px;
            border-radius: 12px;
            border: 1.2px solid #d1d5db;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
            transition: 0.3s;
        }
        div.stSelectbox > div:hover {
            border-color: #3b82f6;
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
        }

        div.stSelectbox div[role="combobox"]::after {
            content: "▾";
            position: absolute;
            right: 20px;
            top: 50%;
            transform: translateY(-50%);
            pointer-events: none;
            font-size: 14px;
            color: #6b7280;
        }

        .stAlert {
            font-size: 1rem;
            background-color: #e0f2fe !important;
            border-left: 4px solid #0284c7 !important;
            color: #1e3a8a !important;
            padding: 16px;
            border-radius: 8px;
            margin-top: 20px;
            margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)


    # Cria as abas
    tab1, tab2 = st.tabs(["🔎 Métricas da Empresa", "📈 Análises e Filtros Avançados"])

    # --- ABA 1 ---
    with tab1:
        st.header("📊 Métricas por Empresa")

        empresa_selecionada = st.selectbox(
            "Selecione uma empresa:",
            options=sorted(df['empresa_nome'].unique()),
            index=0
        )

        df_empresa = df[df['empresa_nome'] == empresa_selecionada]

        if not df_empresa.empty:
            total_voos = df_empresa['decolagens'].sum()
            distancia_total = df_empresa['distancia_voada_km'].sum()
            tem_dados_combustivel = 'combustivel_litros' in df_empresa.columns and (df_empresa['combustivel_litros'] > 0).any()

            if tem_dados_combustivel:
                df_com_combustivel = df_empresa[df_empresa['combustivel_litros'] > 0]
                eficiencia = df_com_combustivel['distancia_voada_km'].sum() / df_com_combustivel['combustivel_litros'].sum()
            else:
                eficiencia = None

            with st.container():
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f'<div class="big-number">{total_voos:,}</div>', unsafe_allow_html=True)
                    st.markdown('<div class="small-label">Total de Voos</div>', unsafe_allow_html=True)
                with col2:
                    st.markdown(f'<div class="big-number">{distancia_total:,.0f}</div>', unsafe_allow_html=True)
                    st.markdown('<div class="small-label">Distância Total (km)</div>', unsafe_allow_html=True)
                with col3:
                    if eficiencia is not None:
                        st.markdown(f'<div class="big-number">{eficiencia:.2f}</div>', unsafe_allow_html=True)
                        st.markdown('<div class="small-label">Eficiência (km/l)</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="big-number" style="color:#9ca3af;">N/D</div>', unsafe_allow_html=True)
                        st.markdown('<div class="small-label">Eficiência (sem dados)</div>', unsafe_allow_html=True)

            st.subheader("Outras Estatísticas")
            with st.container():
                col4, col5 = st.columns(2)
                with col4:
                    media_distancia = df_empresa['distancia_voada_km'].sum() / df_empresa['decolagens'].sum()
                    st.markdown(f'<div class="big-number" style="font-size: 2.8rem; color:#16a34a;">{media_distancia:,.0f}</div>', unsafe_allow_html=True)
                    st.markdown('<div class="small-label">Média de Distância por Voo (km)</div>', unsafe_allow_html=True)
                with col5:
                    horas_totais = df_empresa['horas_voadas'].sum()
                    st.markdown(f'<div class="big-number" style="font-size: 2.8rem; color:#dc2626;">{horas_totais:,.1f}</div>', unsafe_allow_html=True)
                    st.markdown('<div class="small-label">Horas Totais de Voo</div>', unsafe_allow_html=True)
        else:
            st.warning("Nenhum dado disponível para a empresa selecionada.")

        meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

    
        df_combustivel = df_empresa[df_empresa['combustivel_litros'] > 0]

        if df_combustivel.empty:
            st.info("ℹ️ Esta empresa não possui dados de combustível disponíveis. Talvez opere apenas voos internacionais ou os dados não estão registrados.")
        else:
            df_empresa_mes = df_combustivel.groupby('mes').apply(
                lambda x: x['distancia_voada_km'].sum() / x['combustivel_litros'].sum()
            ).reset_index(name='eficiencia_km_l')

            fig, ax = plt.subplots(figsize=(8, 4))
            sns.lineplot(data=df_empresa_mes, x='mes', y='eficiencia_km_l', marker='o', color='#2563eb', linewidth=2, ax=ax)
            ax.set_title('📊 Eficiência Mensal (km/l)', fontsize=14)
            ax.set_ylabel('Eficiência (km/l)')
            ax.set_xlabel('Mês')
            ax.grid(True, linestyle='--', alpha=0.4)

            meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
            ax.set_xticks(df_empresa_mes['mes'])
            ax.set_xticklabels([meses[m-1] for m in df_empresa_mes['mes']])

            st.pyplot(fig)

        
        df_mes = df_empresa.groupby('mes').agg({
            'distancia_voada_km': 'sum',
            'combustivel_litros': 'sum'
        }).reset_index()


        fig, ax = plt.subplots(figsize=(10,5))
        width = 0.4

        ax.bar(df_mes['mes'] - width/2, df_mes['distancia_voada_km'], width=width, label='Distância Voada (km)', color='#2563eb')
        ax.bar(df_mes['mes'] + width/2, df_mes['combustivel_litros'], width=width, label='Combustível Consumido (L)', color='#f97316')

        ax.set_xticks(df_mes['mes'])
        ax.set_xticklabels([meses[m-1] for m in df_mes['mes']])
        ax.set_xlabel('Mês')
        ax.set_ylabel('Quantidade')
        ax.set_title('Distância Voada x Combustível Consumido por Mês')
        ax.legend()

        # Adicionar os valores nas barras
        def add_labels(bars):
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'{height:,.0f}',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),
                            textcoords="offset points",
                            ha='center', va='bottom', fontsize=8)

        bars1 = ax.bar(df_mes['mes'] - width/2, df_mes['distancia_voada_km'], width=width, color='#2563eb')
        bars2 = ax.bar(df_mes['mes'] + width/2, df_mes['combustivel_litros'], width=width, color='#f97316')

        add_labels(bars1)
        add_labels(bars2)

        st.pyplot(fig)


        # Agrupando os dados por mês
        df_horas_mes = df_empresa.groupby('mes').agg({
            'horas_voadas': 'sum',
            'decolagens': 'sum',
            'distancia_voada_km': 'sum'
        }).reset_index()

        # Calculando as médias
        df_horas_mes['media_horas_por_voo'] = df_horas_mes['horas_voadas'] / df_horas_mes['decolagens']
        df_horas_mes['media_km_por_voo'] = df_horas_mes['distancia_voada_km'] / df_horas_mes['decolagens']

        # Verificar se as colunas estão no dataframe
        print(df_horas_mes.columns)
        print(df_horas_mes.head())

        # Plot com dois eixos y
        fig, ax1 = plt.subplots(figsize=(10,5))

        color1 = '#8b5cf6'
        color2 = '#22d3ee'

        ax1.set_xlabel('Mês')
        ax1.set_ylabel('Horas por Voo', color=color1)
        sns.lineplot(data=df_horas_mes, x='mes', y='media_horas_por_voo', marker='o', color=color1, ax=ax1)
        ax1.tick_params(axis='y', labelcolor=color1)

        ax2 = ax1.twinx()
        ax2.set_ylabel('Km por Voo', color=color2)
        sns.lineplot(data=df_horas_mes, x='mes', y='media_km_por_voo', marker='o', color=color2, ax=ax2)
        ax2.tick_params(axis='y', labelcolor=color2)

        ax1.set_xticks(df_horas_mes['mes'])
        ax1.set_xticklabels([meses[m-1] for m in df_horas_mes['mes']])

        plt.title('Média de Horas e Km por Voo ao Longo dos Meses')
        plt.grid(True, linestyle='--', alpha=0.3)
        st.pyplot(fig)

    # --- ABA 2 ---
    with tab2:
        st.markdown("### 🔍 Análise Resumida por Empresa com Filtros")

        col1, col2 = st.columns(2)
        empresas = sorted(df['empresa_nome'].unique())
        meses = sorted(df['mes'].unique())

        with col1:
            empresa_filtro = st.multiselect("Filtrar por Empresa:", options=empresas)

        with col2:
            meses_filtro = st.multiselect("Filtrar por Mês:", options=meses)

        if empresa_filtro and meses_filtro:
            df_filtros = df[
                (df['empresa_nome'].isin(empresa_filtro)) & (df['mes'].isin(meses_filtro))
            ]

            if df_filtros.empty:
                st.warning("Nenhum dado encontrado com os filtros selecionados.")
            else:
                resumo = (
                    df_filtros.groupby('empresa_nome')
                    .agg({
                        'distancia_voada_km': 'sum',
                        'combustivel_litros': 'sum',
                        'horas_voadas': 'sum',
                        'decolagens': 'sum'
                    })
                    .reset_index()
                )
                resumo['eficiencia_km_l'] = resumo.apply(
                    lambda row: row['distancia_voada_km'] / row['combustivel_litros']
                    if row['combustivel_litros'] > 0 else None,
                    axis=1
                )
                resumo['velocidade_kmh'] = resumo.apply(
                    lambda row: row['distancia_voada_km'] / row['horas_voadas']
                    if row['horas_voadas'] > 0 else None,
                    axis=1
                )
                resumo['media_km_por_voo'] = resumo['distancia_voada_km'] / resumo['decolagens']
                resumo = resumo.sort_values(by='eficiencia_km_l', ascending=False)

                st.markdown("#### 📋 Resumo por Empresa")
                st.dataframe(
                    resumo[['empresa_nome', 'decolagens', 'distancia_voada_km', 'horas_voadas', 'combustivel_litros',
                            'media_km_por_voo', 'eficiencia_km_l', 'velocidade_kmh']].rename(columns={
                                'empresa_nome': 'Empresa',
                                'decolagens': 'Voos',
                                'distancia_voada_km': 'Distância (km)',
                                'horas_voadas': 'Horas Voadas',
                                'combustivel_litros': 'Combustível (L)',
                                'media_km_por_voo': 'Média km/Voo',
                                'eficiencia_km_l': 'Eficiência (km/l)',
                                'velocidade_kmh': 'Velocidade Média (km/h)'
                            }),
                    use_container_width=True,
                    hide_index=True
                )

                st.markdown("#### 📎 Dados Detalhados por Voo")
                st.dataframe(
                    df_filtros[['empresa_nome', 'mes', 'distancia_voada_km', 'horas_voadas', 'combustivel_litros', 'decolagens']],
                    use_container_width=True,
                    height=400
                )
        else:
            st.info("Selecione ao menos uma empresa e um mês para visualizar os dados.")

        st.header("📊 Análises Gráficas")

        df_com_combustivel_geral = df[df['combustivel_litros'] > 0]
        df_eficiencia_geral_mes = df_com_combustivel_geral.groupby('mes').apply(
            lambda x: x['distancia_voada_km'].sum() / x['combustivel_litros'].sum()
        ).reset_index(name='eficiencia')

        meses_labels = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        ticks_labels = [meses_labels[m - 1] for m in df_eficiencia_geral_mes['mes']]

        fig, ax = plt.subplots(figsize=(10, 5))
        sns.lineplot(data=df_eficiencia_geral_mes, x='mes', y='eficiencia', marker='o', color='#2563eb', linewidth=2.5, ax=ax)
        ax.set_title('📈 Eficiência Média Geral por Mês em 2025', fontsize=16, fontweight='bold', color='#1e3a8a')
        ax.set_xlabel('Mês')
        ax.set_ylabel('Eficiência (km/l)')
        ax.set_xticks(df_eficiencia_geral_mes['mes'])
        ax.set_xticklabels(ticks_labels)
        ax.grid(True, linestyle='--', alpha=0.3)
        st.pyplot(fig)

        df_top10 = (
            df_com_combustivel_geral
            .groupby(['empresa_nome'])
            .apply(lambda x: x['distancia_voada_km'].sum() / x['combustivel_litros'].sum())
            .reset_index(name='eficiencia_km_l')
            .sort_values(by='eficiencia_km_l', ascending=False)
            .head(10)
        )

        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(data=df_top10, x='eficiencia_km_l', y='empresa_nome', palette='Blues_d', ax=ax)
        ax.set_title('🏆 Top 10 Empresas Mais Eficientes (km/l)', fontsize=16, fontweight='bold', color='#1e3a8a')
        ax.set_xlabel('Eficiência (km/l)')
        ax.set_ylabel('')
        st.pyplot(fig)

        st.subheader("⏱️ Top 10 Empresas com Maior Velocidade Média de Voo")
        df_velocidade = df.groupby('empresa_nome').agg({
            'distancia_voada_km': 'sum',
            'horas_voadas': 'sum'
        }).reset_index()
        df_velocidade['velocidade_media_kmh'] = df_velocidade['distancia_voada_km'] / df_velocidade['horas_voadas']
        df_velocidade_top10 = df_velocidade.sort_values(by='velocidade_media_kmh', ascending=False).head(10)

        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(data=df_velocidade_top10, x='velocidade_media_kmh', y='empresa_nome', palette='viridis', ax=ax)
        ax.set_title('🚀 Top 10 Empresas com Maior Velocidade Média de Voo', fontsize=16, fontweight='bold', color='#1e3a8a')
        ax.set_xlabel('Velocidade Média (km/h)')
        ax.set_ylabel('')
        st.pyplot(fig)





        df_volume = df.groupby('mes').agg({
            'decolagens': 'sum',
            'combustivel_litros': 'sum'
        }).reset_index()

        fig, ax1 = plt.subplots(figsize=(12,6))
        width = 0.35
        x = list(range(len(df_volume['mes'])))

        # Barras de decolagens
        bars1 = ax1.bar([pos - width/2 for pos in x], df_volume['decolagens'], width=width, label='Total decolagens', color='#2563eb')
        ax1.set_ylabel('Total decolagens', color='#2563eb')
        ax1.tick_params(axis='y', labelcolor='#2563eb')

        # Eixo X
        meses_labels = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        ax1.set_xticks(x)
        ax1.set_xticklabels([meses_labels[m-1] for m in df_volume['mes']])
        ax1.set_xlabel('Mês')

        # Barras combustível eixo direito
        ax2 = ax1.twinx()
        bars2 = ax2.bar([pos + width/2 for pos in x], df_volume['combustivel_litros'], width=width, label='Total combustível (L)', color='#f97316')
        ax2.set_ylabel('Total combustível (L)', color='#f97316')
        ax2.tick_params(axis='y', labelcolor='#f97316')

        ax1.set_title('Volume de Operações e Consumo de Combustível por Mês')

        # Função para formatar número em estilo brasileiro
        def format_brl(value):
            return f'{value:,.0f}'.replace(',', 'v').replace('.', ',').replace('v', '.')

        # Adiciona os números acima das barras
        def add_labels(bars, ax):
            for bar in bars:
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    height * 1.01,
                    format_brl(height),
                    ha='center',
                    va='bottom',
                    fontsize=9,
                    fontweight='bold'
                )

        add_labels(bars1, ax1)
        add_labels(bars2, ax2)

        # Legenda combinada
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

        plt.tight_layout()
        st.pyplot(fig)

# Manter as outras abas como estavam originalmente
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

        tab1, tab2 = st.tabs(["Combustivel", "Linhas Areas"])

        with tab1:
            st.subheader("Combustivel", divider=True)

            query = '''
                SELECT 
                    v.empresa_sigla,
                    e.empresa_nome,
                    SUM(v.distancia_voada_km) AS total_km,
                    SUM(v.combustivel_litros) AS total_combustivel
                FROM voo v
                JOIN empresa e ON v.empresa_sigla = e.empresa_sigla
                    WHERE v.combustivel_litros > 0
                GROUP BY v.empresa_sigla
                HAVING total_combustivel > 0
                
                '''

            df = pd.read_sql_query(query, conn)
            df['eficiencia_km_por_litro'] = df['total_km'] / df['total_combustivel']
            media_eficiencia = df['eficiencia_km_por_litro'].mean()
            top3 = df.sort_values(by='eficiencia_km_por_litro', ascending=False).head(3)
            botton3 = df.sort_values(by='eficiencia_km_por_litro', ascending=False).tail(3)

            st.title("⛽ Eficiência de Combustível das Empresas Aéreas Nacionais")
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


            fig, ax = plt.subplots(figsize=(10,6))
            ax.scatter(top3['empresa_nome'], top3['eficiencia_km_por_litro'], color='green', label='Top 3')
            ax.scatter(botton3['empresa_nome'], botton3['eficiencia_km_por_litro'], color='red', label='Bottom 3')
            ax.axhline(y=media_eficiencia, color='blue', linestyle='--', label=f'Média ({media_eficiencia:.2f} km/l)')

            # Configurando rótulos e título
            ax.set_xlabel("Empresas")
            ax.set_ylabel("Eficiência (km/l)")
            ax.set_title("Top 3 e Bottom 3 em Eficiência de Combustível")
            ax.set_xticks(range(len(top3) + len(botton3)))
            ax.set_xticklabels(list(top3['empresa_sigla']) + list(botton3['empresa_sigla']), rotation=45)
            ax.legend()
            ax.grid(True)

            # Exibindo gráfico no Streamlit
            st.pyplot(fig)
            empresa_selecionada = st.selectbox("Selecione uma empresa", df['empresa_nome'].unique())
            dados_empresa = df[df['empresa_nome'] == empresa_selecionada]
            media_empresa = dados_empresa['eficiencia_km_por_litro'].mean()
            st.metric(label="Média de Eficiência (km/l)", value=f"{media_empresa:.2f}")


            fig, ax = plt.subplots(figsize=(8,8))
            ax.pie(df['eficiencia_km_por_litro'], labels=df['empresa_nome'], autopct='%1.1f%%', startangle=90)
            ax.set_title("Participação das Empresas na Eficiência de Combustível")
            st.pyplot(fig)

        with tab2:
            st.subheader("Linhas Areas", divider=True)
            query = '''
                SELECT 
                    v.aeroporto_origem_sigla,
                    v.aeroporto_destino_sigla,
                    a1.aeroporto_nome AS origem_nome,
                    a2.aeroporto_nome AS destino_nome,
                    SUM(v.distancia_voada_km) AS total_km,
                    SUM(v.combustivel_litros) AS total_combustivel
                FROM voo v
                JOIN aeroporto a1 ON v.aeroporto_origem_sigla = a1.aeroporto_sigla
                JOIN aeroporto a2 ON v.aeroporto_destino_sigla = a2.aeroporto_sigla
                WHERE v.combustivel_litros > 0
                GROUP BY v.aeroporto_origem_sigla, v.aeroporto_destino_sigla
            '''

            df = pd.read_sql_query(query, conn)
            df['eficiencia_km_por_litro'] = df['total_km'] / df['total_combustivel']
            df['rota'] = df['origem_nome'] + " → " + df['destino_nome']

            top_rotas = df.sort_values(by='eficiencia_km_por_litro', ascending=False).head(3)
            worst_rotas = df[df['eficiencia_km_por_litro'] > 1].sort_values(by='eficiencia_km_por_litro', ascending=True).head(3) 
            st.title("⛽ Eficiência de Combustível por Rota")

            st.subheader("Top 3 Rotas Mais Eficientes")
            col1, col2, col3 = st.columns(3)
            col1.metric(label=top_rotas.iloc[0]['rota'], value=f"{top_rotas.iloc[0]['eficiencia_km_por_litro']:.2f} km/l")
            col2.metric(label=top_rotas.iloc[1]['rota'], value=f"{top_rotas.iloc[1]['eficiencia_km_por_litro']:.2f} km/l")
            col3.metric(label=top_rotas.iloc[2]['rota'], value=f"{top_rotas.iloc[2]['eficiencia_km_por_litro']:.2f} km/l")

            st.subheader("Top 3 Rotas Mais Ineficientes (Min 1km/l)")
            col1, col2, col3 = st.columns(3)
            col1.metric(label=worst_rotas.iloc[0]['rota'], value=f"{worst_rotas.iloc[0]['eficiencia_km_por_litro']:.2f} km/l")
            col2.metric(label=worst_rotas.iloc[1]['rota'], value=f"{worst_rotas.iloc[1]['eficiencia_km_por_litro']:.2f} km/l")
            col3.metric(label=worst_rotas.iloc[2]['rota'], value=f"{worst_rotas.iloc[2]['eficiencia_km_por_litro']:.2f} km/l")

if st.session_state.aba_ativa == 'voos_impro':
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

        def carregar_dados():
            query = """
            SELECT v.*, e.empresa_nome, a.aeroporto_regiao 
            FROM voo v
            JOIN empresa e ON v.empresa_sigla = e.empresa_sigla
            JOIN aeroporto a ON v.aeroporto_origem_sigla = a.aeroporto_sigla
            """
            df = pd.read_sql_query(query, conn)
            return df

        df = carregar_dados()


        tab1, tab2 = st.tabs(["Análise por Empresa", "Distribuição por Região"])

        with tab1:
            st.title("Análise de Voos Improdutivos (Combustível)")
            st.write("Selecione uma empresa para visualizar os dados.")


            empresas_disponiveis = df["empresa_nome"].unique()
            empresa_selecionada = st.selectbox("Escolha uma empresa:", empresas_disponiveis)


            df_filtrado = df[df["empresa_nome"] == empresa_selecionada]

            if "natureza" in df_filtrado.columns:
                voos_internacionais = df_filtrado[df_filtrado["natureza"] == "INTERNACIONAL"]
                if not voos_internacionais.empty:
                    st.warning("Os dados de combustível não são fornecidos para voos internacionais.")

            st.bar_chart(df_filtrado[["distancia_voada_km", "combustivel_litros"]])
            filtro_improdutivo = df_filtrado[
                (df_filtrado["natureza"] != "INTERNACIONAL") &
                (df_filtrado["combustivel_litros"] / df_filtrado["distancia_voada_km"] > 1)
            ]
            if "natureza" in df_filtrado.columns:
                voos_internacionais = df_filtrado[df_filtrado["natureza"] == "INTERNACIONAL"]
                if not voos_internacionais.empty:
                    st.warning("Os dados de combustível não são fornecidos para voos internacionais.")

            st.write("Voos improdutivos (alto consumo de combustível em relação à distância voada):")
            st.dataframe(filtro_improdutivo)


            total_voos = len(df_filtrado)
            total_improdutivos = len(filtro_improdutivo)
            percentual_improdutivo = (total_improdutivos / total_voos) * 100 if total_voos > 0 else 0
            st.write(f"**Total voos:** {total_voos}")
            st.write(f"**Percentual de voos improdutivos:** {percentual_improdutivo:.2f}%")

            with tab2:
                st.title("Distribuição de Voos Improdutivos por Região")

                if "natureza" in df_filtrado.columns and any(df_filtrado["natureza"].str.upper() == "INTERNACIONAL"):
                    st.warning("Os dados de região não se aplicam para voos internacionais.")
                if "natureza" in df_filtrado.columns and any(df_filtrado["natureza"].str.upper() == "DOMÉSTICA"):
                    regioes_improdutivas = filtro_improdutivo["aeroporto_regiao"].value_counts()
                    st.write("Voos improdutivos por região:")
                    st.bar_chart(regioes_improdutivas)

if st.session_state.aba_ativa == 'voos_impro_pas':
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
        def carregar_dados():
            query = """
            SELECT v.*, e.empresa_nome, a.aeroporto_regiao, cp.passageiros_pagos, cp.bagagem_kg 
            FROM voo v
            JOIN empresa e ON v.empresa_sigla = e.empresa_sigla
            JOIN aeroporto a ON v.aeroporto_origem_sigla = a.aeroporto_sigla
            JOIN carga_passageiros cp ON v.voo_id = cp.voo_id
            """
            df = pd.read_sql_query(query, conn)
            return df

        df = carregar_dados()

        tab1, tab2 = st.tabs(["Análise por Empresa", "Distribuição por Região"])
        with tab1:
            st.title("Análise de Voos Com poucos Passageiros & Bagagem")
            st.write("Selecione uma empresa para visualizar os dados.")

            empresas_disponiveis = df["empresa_nome"].unique()
            empresa_selecionada = st.selectbox("Escolha uma empresa:", empresas_disponiveis)

            df_filtrado = df[df["empresa_nome"] == empresa_selecionada]

            st.bar_chart(df_filtrado[["bagagem_kg","passageiros_pagos" ]])

            filtro_improdutivo_passageiros = df_filtrado[df_filtrado["passageiros_pagos"] < 10] 
            st.write("Voos com baixo número de passageiros pagos:")
            st.dataframe(filtro_improdutivo_passageiros)

            filtro_improdutivo_bagagem = df_filtrado[df_filtrado["bagagem_kg"] > 2000]  
            st.write("Voos com muita bagagem transportada com poucos passageiros):")
            st.dataframe(filtro_improdutivo_bagagem)

            total_voos = len(df_filtrado)
            total_improdutivos_passageiros = len(filtro_improdutivo_passageiros)
            total_improdutivos_bagagem = len(filtro_improdutivo_bagagem)

            percentual_improdutivo_passageiros = (total_improdutivos_passageiros / total_voos) * 100 if total_voos > 0 else 0
            percentual_improdutivo_bagagem = (total_improdutivos_bagagem / total_voos) * 100 if total_voos > 0 else 0

            st.subheader(f"**Percentual de voos com poucos passageiros:** {percentual_improdutivo_passageiros:.2f}%")
            st.subheader(f"**Percentual de voos com poucos passageiros e muita bagagem:** {percentual_improdutivo_bagagem:.2f}%")


        with tab2:
            st.title("Distribuição de Voos Improdutivos por Região")
            
            regioes_improdutivas_passageiros = filtro_improdutivo_passageiros["aeroporto_regiao"].value_counts()
            regioes_improdutivas_bagagem = filtro_improdutivo_bagagem["aeroporto_regiao"].value_counts()

            st.write("Distribuição de voos improdutivos por passageiros:")
            st.bar_chart(regioes_improdutivas_passageiros)

            st.write("Distribuição de voos improdutivos por bagagem:")
            st.bar_chart(regioes_improdutivas_bagagem)
if st.session_state.aba_ativa == 'rotas':
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
#aba de kpis gerenciais
if st.session_state.aba_ativa == 'kpis':
    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"] {
            background-color: #000000;
        }
        
        .kpi-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem;
            border-radius: 1rem;
            color: white;
            text-align: center;
            margin: 0.5rem 0;
        }
        
        .kpi-card h3 {
            margin: 0;
            font-size: 2.5rem;
            font-weight: bold;
            color: white;
        }
        
        .kpi-card p {
            margin: 0.5rem 0 0 0;
            font-size: 1rem;
            opacity: 0.9;
            color: white;
        }
        
        .chart-container {
            background-color: white;
            padding: 1.5rem;
            border-radius: 0.75rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            margin: 1rem 0;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Criar a VIEW SQL para KPIs (se não existir)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE VIEW IF NOT EXISTS vw_kpis_voo AS
        SELECT 
            v.voo_id,
            v.empresa_sigla,
            v.ano,
            v.mes,
            v.aeroporto_origem_sigla,
            v.aeroporto_destino_sigla,
            v.natureza,
            v.grupo_voo,
            v.distancia_voada_km,
            v.combustivel_litros,
            v.decolagens,
            v.horas_voadas,
            e.empresa_nome,
            COALESCE(cp.passageiros_pagos, 0) + COALESCE(cp.passageiros_gratis, 0) as total_passageiros,
            COALESCE(cp.bagagem_kg, 0) as bagagem_kg,
            -- Simular métricas ASK e RPK baseadas nos dados disponíveis
            CASE 
                WHEN v.distancia_voada_km > 0 THEN 
                    -- ASK = Assentos disponíveis estimados * distância
                    (COALESCE(cp.passageiros_pagos, 0) + COALESCE(cp.passageiros_gratis, 0)) * 1.3 * v.distancia_voada_km
                ELSE 0 
            END as ASK_estimado,
            CASE 
                WHEN v.distancia_voada_km > 0 THEN 
                    -- RPK = Passageiros reais * distância
                    (COALESCE(cp.passageiros_pagos, 0) + COALESCE(cp.passageiros_gratis, 0)) * v.distancia_voada_km
                ELSE 0 
            END as RPK_real,
            -- Payload = bagagem + peso estimado dos passageiros
            COALESCE(cp.bagagem_kg, 0) + ((COALESCE(cp.passageiros_pagos, 0) + COALESCE(cp.passageiros_gratis, 0)) * 80) as payload_total,
            -- KPIs Calculados
            CASE 
                WHEN (COALESCE(cp.passageiros_pagos, 0) + COALESCE(cp.passageiros_gratis, 0)) * 1.3 > 0 THEN 
                    ((COALESCE(cp.passageiros_pagos, 0) + COALESCE(cp.passageiros_gratis, 0)) / 
                     ((COALESCE(cp.passageiros_pagos, 0) + COALESCE(cp.passageiros_gratis, 0)) * 1.3)) * 100
                ELSE 0 
            END as taxa_ocupacao_pct,
            CASE 
                WHEN v.decolagens > 0 THEN 
                    (COALESCE(cp.bagagem_kg, 0) + ((COALESCE(cp.passageiros_pagos, 0) + COALESCE(cp.passageiros_gratis, 0)) * 80)) / v.decolagens
                ELSE 0 
            END as payload_medio_por_voo,
            CASE 
                WHEN v.distancia_voada_km > 0 THEN 
                    (COALESCE(cp.passageiros_pagos, 0) + COALESCE(cp.passageiros_gratis, 0)) / v.distancia_voada_km * 100
                ELSE 0 
            END as passageiros_por_km,
            (COALESCE(cp.passageiros_pagos, 0) + COALESCE(cp.passageiros_gratis, 0)) * 1.3 as assentos_disponivel_estimado
        FROM voo v
        JOIN empresa e ON v.empresa_sigla = e.empresa_sigla
        LEFT JOIN carga_passageiros cp ON v.voo_id = cp.voo_id
    ''')
    conn.commit()
    
    # Função para criar cards de KPIs
    def create_kpi_card(title, value, subtitle=""):
        st.markdown(f"""
        <div class="kpi-card">
            <h3>{value}</h3>
            <p>{title}</p>
            {f'<small style="opacity: 0.8; color: white;">{subtitle}</small>' if subtitle else ''}
        </div>
        """, unsafe_allow_html=True)
    
    # Header principal
    st.title("📊 KPIs e Métricas Gerenciais")
    st.write("Análise detalhada das métricas de performance das operações de voo")
    
    # Filtros principais
    st.markdown("### 🔍 Filtros")
    col_filter1, col_filter2 = st.columns(2)
    
    with col_filter1:
        # Filtro por empresa
        empresas_query = "SELECT DISTINCT empresa_sigla, empresa_nome FROM empresa ORDER BY empresa_nome"
        empresas_df = pd.read_sql_query(empresas_query, conn)
        opcoes_empresas = ['Todas'] + [f"{row['empresa_nome']} ({row['empresa_sigla']})" for _, row in empresas_df.iterrows()]
        empresa_selecionada_display = st.selectbox("Empresa:", opcoes_empresas, key="kpi_empresa")
        
        if empresa_selecionada_display != 'Todas':
            empresa_selecionada = empresa_selecionada_display.split('(')[1].replace(')', '')
        else:
            empresa_selecionada = 'Todas'
    
    with col_filter2:
        tipos_voo = ['Todos', 'DOMÉSTICA', 'INTERNACIONAL']
        tipo_voo_selecionado = st.selectbox("Tipo de Voo:", tipos_voo, key="kpi_tipo")
    
    # Construir query com filtros
    where_conditions = []
    if empresa_selecionada != 'Todas':
        where_conditions.append(f"empresa_sigla = '{empresa_selecionada}'")
    if tipo_voo_selecionado != 'Todos':
        where_conditions.append(f"natureza = '{tipo_voo_selecionado}'")
    
    where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
    
    # Carregar dados filtrados
    query_kpis = f"""
    SELECT * FROM vw_kpis_voo
    {where_clause}
    ORDER BY ano DESC, mes DESC
    """
    
    df_kpis = pd.read_sql_query(query_kpis, conn)
    
    if df_kpis.empty:
        st.warning("⚠️ Nenhum dado encontrado para os filtros selecionados.")
    else:
        # Calcular métricas agregadas
        total_ask = df_kpis['ASK_estimado'].sum()
        total_rpk = df_kpis['RPK_real'].sum()
        taxa_ocupacao_media = (total_rpk / total_ask * 100) if total_ask > 0 else 0
        payload_medio_geral = df_kpis['payload_medio_por_voo'].mean()
        passageiros_km_medio = df_kpis['passageiros_por_km'].mean()
        
        # Cards de KPIs principais
        st.markdown("### 📈 Indicadores Principais")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            create_kpi_card(
                "Taxa Média de Ocupação",
                f"{taxa_ocupacao_media:.1f}%",
                "RPK / ASK"
            )
        
        with col2:
            create_kpi_card(
                "Payload Médio por Voo",
                f"{payload_medio_geral:.0f} kg",
                "Peso transportado por voo"
            )
        
        with col3:
            create_kpi_card(
                "Passageiros por 100km",
                f"{passageiros_km_medio:.1f}",
                "Densidade de passageiros"
            )
        
        # Gráficos dos KPIs
        st.markdown("---")
        st.markdown("### 📊 Análises Visuais")
        
        tab1, tab2, tab3 = st.tabs(["📈 Por Empresa", "📅 Evolução Temporal", "🛣️ Por Rota"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Taxa de Ocupação por Empresa")
                ocupacao_empresa = df_kpis.groupby(['empresa_sigla', 'empresa_nome']).agg({
                    'ASK_estimado': 'sum',
                    'RPK_real': 'sum'
                }).reset_index()
                ocupacao_empresa['taxa_ocupacao'] = (ocupacao_empresa['RPK_real'] / ocupacao_empresa['ASK_estimado']) * 100
                ocupacao_empresa = ocupacao_empresa.sort_values('taxa_ocupacao', ascending=True)
                
                fig_ocupacao = px.bar(
                    ocupacao_empresa,
                    x='taxa_ocupacao',
                    y='empresa_sigla',
                    orientation='h',
                    title='Taxa de Ocupação por Empresa (%)',
                    color='taxa_ocupacao',
                    color_continuous_scale='Viridis',
                    labels={'taxa_ocupacao': 'Taxa de Ocupação (%)', 'empresa_sigla': 'Empresa'}
                )
                fig_ocupacao.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig_ocupacao, use_container_width=True)
            
            with col2:
                st.markdown("#### Payload Médio por Empresa")
                payload_empresa = df_kpis.groupby(['empresa_sigla', 'empresa_nome']).agg({
                    'payload_medio_por_voo': 'mean'
                }).reset_index()
                payload_empresa = payload_empresa.sort_values('payload_medio_por_voo', ascending=True)
                
                fig_payload = px.bar(
                    payload_empresa,
                    x='payload_medio_por_voo',
                    y='empresa_sigla',
                    orientation='h',
                    title='Payload Médio por Empresa (kg)',
                    color='payload_medio_por_voo',
                    color_continuous_scale='Blues',
                    labels={'payload_medio_por_voo': 'Payload Médio (kg)', 'empresa_sigla': 'Empresa'}
                )
                fig_payload.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig_payload, use_container_width=True)
            
            # Gráfico de capacidade vs utilização
            st.markdown("#### Assentos Disponíveis vs Passageiros Reais")
            capacidade = df_kpis.groupby(['empresa_sigla', 'empresa_nome']).agg({
                'assentos_disponivel_estimado': 'sum',
                'total_passageiros': 'sum'
            }).reset_index()
            
            fig_capacidade = go.Figure()
            fig_capacidade.add_trace(go.Bar(
                name='Assentos Disponíveis (estimado)',
                x=capacidade['empresa_sigla'],
                y=capacidade['assentos_disponivel_estimado'],
                marker_color='lightblue'
            ))
            fig_capacidade.add_trace(go.Bar(
                name='Passageiros Reais',
                x=capacidade['empresa_sigla'],
                y=capacidade['total_passageiros'],
                marker_color='darkblue'
            ))
            fig_capacidade.update_layout(
                title='Capacidade vs Utilização por Empresa',
                barmode='group',
                height=400,
                xaxis_title='Empresa',
                yaxis_title='Quantidade'
            )
            st.plotly_chart(fig_capacidade, use_container_width=True)
        
        with tab2:
            st.markdown("#### Evolução da Taxa de Ocupação ao Longo do Tempo")
            
            evolucao_temporal = df_kpis.groupby(['ano', 'mes']).agg({
                'ASK_estimado': 'sum',
                'RPK_real': 'sum',
                'payload_medio_por_voo': 'mean'
            }).reset_index()
            evolucao_temporal['taxa_ocupacao'] = (evolucao_temporal['RPK_real'] / evolucao_temporal['ASK_estimado']) * 100
            evolucao_temporal['periodo'] = evolucao_temporal['ano'].astype(str) + '-' + evolucao_temporal['mes'].astype(str).str.zfill(2)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_evolucao = px.line(
                    evolucao_temporal,
                    x='periodo',
                    y='taxa_ocupacao',
                    title='Taxa de Ocupação Mensal (%)',
                    markers=True,
                    line_shape='spline'
                )
                fig_evolucao.update_layout(height=400)
                fig_evolucao.update_xaxes(title='Período')
                fig_evolucao.update_yaxes(title='Taxa de Ocupação (%)')
                st.plotly_chart(fig_evolucao, use_container_width=True)
            
            with col2:
                fig_payload_tempo = px.line(
                    evolucao_temporal,
                    x='periodo',
                    y='payload_medio_por_voo',
                    title='Payload Médio por Voo Mensal (kg)',
                    markers=True,
                    line_shape='spline',
                    color_discrete_sequence=['#FF6B6B']
                )
                fig_payload_tempo.update_layout(height=400)
                fig_payload_tempo.update_xaxes(title='Período')
                fig_payload_tempo.update_yaxes(title='Payload Médio (kg)')
                st.plotly_chart(fig_payload_tempo, use_container_width=True)
        
        with tab3:
            st.markdown("#### Análise por Rota")
            
            # Top rotas por volume de passageiros
            rotas_analise = df_kpis.groupby(['aeroporto_origem_sigla', 'aeroporto_destino_sigla']).agg({
                'total_passageiros': 'sum',
                'taxa_ocupacao_pct': 'mean',
                'payload_medio_por_voo': 'mean',
                'voo_id': 'count'
            }).reset_index()
            rotas_analise.rename(columns={'voo_id': 'total_voos'}, inplace=True)
            rotas_analise['rota'] = rotas_analise['aeroporto_origem_sigla'] + ' → ' + rotas_analise['aeroporto_destino_sigla']
            rotas_analise = rotas_analise.sort_values('total_passageiros', ascending=False).head(15)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_rotas_pass = px.bar(
                    rotas_analise,
                    x='total_passageiros',
                    y='rota',
                    orientation='h',
                    title='Top 15 Rotas por Volume de Passageiros',
                    color='taxa_ocupacao_pct',
                    color_continuous_scale='RdYlGn',
                    labels={'total_passageiros': 'Total Passageiros', 'rota': 'Rota'}
                )
                fig_rotas_pass.update_layout(height=500)
                fig_rotas_pass.update_yaxes(categoryorder="total ascending")
                st.plotly_chart(fig_rotas_pass, use_container_width=True)
            
            with col2:
                fig_scatter_rotas = px.scatter(
                    rotas_analise,
                    x='taxa_ocupacao_pct',
                    y='payload_medio_por_voo',
                    size='total_passageiros',
                    hover_data=['rota', 'total_voos'],
                    title='Taxa de Ocupação vs Payload por Rota',
                    labels={
                        'taxa_ocupacao_pct': 'Taxa de Ocupação (%)',
                        'payload_medio_por_voo': 'Payload Médio (kg)'
                    }
                )
                fig_scatter_rotas.update_layout(height=500)
                st.plotly_chart(fig_scatter_rotas, use_container_width=True)
        
        # Tabela de dados detalhados
        st.markdown("---")
        st.markdown("### 📋 Dados Detalhados")
        
        # Seletor de colunas para exibir
        colunas_disponiveis = [
            'empresa_sigla', 'empresa_nome', 'ano', 'mes', 'natureza',
            'taxa_ocupacao_pct', 'payload_medio_por_voo', 'passageiros_por_km',
            'total_passageiros', 'distancia_voada_km', 'decolagens'
        ]
        
        colunas_selecionadas = st.multiselect(
            "Selecione as colunas para exibir:",
            colunas_disponiveis,
            default=['empresa_sigla', 'ano', 'mes', 'taxa_ocupacao_pct', 'payload_medio_por_voo', 'total_passageiros'],
            key="kpi_colunas"
        )
        
        if colunas_selecionadas:
            df_display = df_kpis[colunas_selecionadas].copy()
            
            # Formatação dos dados para exibição
            if 'taxa_ocupacao_pct' in df_display.columns:
                df_display['taxa_ocupacao_pct'] = df_display['taxa_ocupacao_pct'].round(1)
            if 'payload_medio_por_voo' in df_display.columns:
                df_display['payload_medio_por_voo'] = df_display['payload_medio_por_voo'].round(0)
            if 'passageiros_por_km' in df_display.columns:
                df_display['passageiros_por_km'] = df_display['passageiros_por_km'].round(2)
            
            st.dataframe(df_display, use_container_width=True, height=400)
conn.close()
