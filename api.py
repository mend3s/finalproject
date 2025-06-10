
import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
<<<<<<< Updated upstream
import plotly.express as px
import plotly.graph_objects as go
from matplotlib.patches import Patch
=======
import folium
import streamlit as st
from streamlit_folium import st_folium
from streamlit_folium import folium_static

>>>>>>> Stashed changes

conn = sqlite3.connect("dados_voo.db")
cursor = conn.cursor()

<<<<<<< Updated upstream
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
     
=======
      
>>>>>>> Stashed changes
if 'aba_ativa' not in st.session_state:
    st.session_state.aba_ativa = 'home'  # valor inicial padrão
    st.session_state.aba_ativa = 'home'  
    
st.sidebar.button("📌 Análises Operacionais", on_click=lambda: st.session_state.update(aba_ativa='home'))
st.sidebar.button("🔍 Filtros", on_click=lambda: st.session_state.update(aba_ativa='filtros'))
st.sidebar.button("⛽ Eficiencia Combustivel", on_click=lambda: st.session_state.update(aba_ativa='eficiencia_comb'))
st.sidebar.button("📊 Gráficos Clientes", on_click=lambda: st.session_state.update(aba_ativa='graficos_clientes'))
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
    with col1:
        st.markdown("""
        <div style='background-color: white; padding: 2rem; border-radius: 0.75rem; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); margin: 1rem 0;'>
            <h3 style='color: #1e40af; text-align: center; margin-bottom: 1.5rem; font-size: 1.5rem;'>🇧🇷 Voos Nacionais</h3>
        """, unsafe_allow_html=True)
        if not df_nacional.empty:
            st.metric("Total Voos", f"{int(df_nacional['total_voos'].iloc[0]):,}")
            st.metric("Passageiros Pagos", f"{int(df_nacional['total_passageiros_pagos'].iloc[0]):,}")
            st.metric("Distância Total (km)", f"{df_nacional['total_distancia_km'].iloc[0]:,.0f}")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style='background-color: white; padding: 2rem; border-radius: 0.75rem; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); margin: 1rem 0;'>
            <h3 style='color: #1e40af; text-align: center; margin-bottom: 1.5rem; font-size: 1.5rem;'>🌐 Voos Internacionais</h3>
        """, unsafe_allow_html=True)
        if not df_internacional.empty:
            st.metric("Total Voos", f"{int(df_internacional['total_voos'].iloc[0]):,}")
            st.metric("Passageiros Pagos", f"{int(df_internacional['total_passageiros_pagos'].iloc[0]):,}")
            st.metric("Distância Total (km)", f"{df_internacional['total_distancia_km'].iloc[0]:,.0f}")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("#### 📋 Tabela Comparativa")
    df_comparacao_display = df_comparacao.copy()
    df_comparacao_display.columns = [
        'Tipo de Voo', 'Total Voos', 'Total Decolagens', 'Distância Total (km)',
        'Combustível Total (L)', 'Horas Voadas', 'Passageiros Pagos', 
        'Passageiros Grátis', 'Média Distância (km)', 'Média Combustível (L)'
    ]
    st.dataframe(df_comparacao_display, use_container_width=True)

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
        st.markdown("#### 🏆 Top Empresas por Número de Voos")
        top_10_voos = df_empresas.head(10)
        fig_voos = plt.figure(figsize=(12, 8))
        plt.barh(top_10_voos['empresa_sigla'], top_10_voos['total_voos'], color="#00BFFF")
        plt.gca().invert_yaxis()
        plt.title("Top 10 Empresas por Voos")
        st.pyplot(fig_voos)

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

    # --- Nova seção: Total de Decolagens por Mês ---
    st.markdown("### 🛫 Total de Decolagens por Mês")
    
    # Filtros para decolagens
    col_filtro1, col_filtro2 = st.columns(2)
    
    with col_filtro1:
        empresas_disponiveis = pd.read_sql_query("SELECT DISTINCT empresa_sigla FROM voo ORDER BY empresa_sigla", conn)['empresa_sigla'].tolist()
        empresa_selecionada = st.selectbox("Empresa:", ['Todas'] + empresas_disponiveis, key="empresa_decolagem")
    
    with col_filtro2:
        tipos_voo = ['Todos', 'DOMESTICA', 'INTERNACIONAL']
        tipo_voo_selecionado = st.selectbox("Tipo de Voo:", tipos_voo, key="tipo_voo_decolagem")
    
    # Construir query para decolagens
    where_conditions_dec = []
    if empresa_selecionada != 'Todas':
        where_conditions_dec.append(f"v.empresa_sigla = '{empresa_selecionada}'")
    if tipo_voo_selecionado != 'Todos':
        where_conditions_dec.append(f"v.natureza = '{tipo_voo_selecionado}'")
    
    where_clause_dec = "WHERE " + " AND ".join(where_conditions_dec) if where_conditions_dec else ""
    
    query_decolagens = f"""
    SELECT 
        v.ano,
        v.mes,
        SUM(v.decolagens) as total_decolagens,
        COUNT(*) as total_voos,
        AVG(v.decolagens) as media_decolagens_por_voo
    FROM voo v
    {where_clause_dec}
    GROUP BY v.ano, v.mes
    ORDER BY v.ano, v.mes
    """
    
    df_decolagens = pd.read_sql_query(query_decolagens, conn)
    
    if not df_decolagens.empty:
        # Gráfico de linha temporal para decolagens
        col1, col2 = st.columns([3, 1])
        
        with col1:
            fig_decolagens = plt.figure(figsize=(14, 6))
            
            # Criar labels para o eixo X (sem usar pd.to_datetime)
            df_decolagens['mes_ano_label'] = df_decolagens['mes'].astype(str).str.zfill(2) + '/' + df_decolagens['ano'].astype(str)
            
            # Usar range numérico para o eixo X
            x_values = range(len(df_decolagens))
            
            plt.plot(x_values, df_decolagens['total_decolagens'], 
                    marker='o', linewidth=2, markersize=6, color='#FF6B6B')
            plt.title('Evolução das Decolagens por Mês', fontsize=14, fontweight='bold')
            plt.xlabel('Mês/Ano')
            plt.ylabel('Total de Decolagens')
            plt.grid(True, alpha=0.3)
            
            # Configurar labels do eixo X
            plt.xticks(x_values, df_decolagens['mes_ano_label'], rotation=45)
            
            # Adicionar valores nos pontos
            for i, (idx, row) in enumerate(df_decolagens.iterrows()):
                plt.annotate(f"{int(row['total_decolagens']):,}", 
                           (i, row['total_decolagens']),
                           textcoords="offset points", xytext=(0,10), ha='center', fontsize=8)
            
            plt.tight_layout()
            st.pyplot(fig_decolagens)
        
        with col2:
            st.markdown("**Resumo Decolagens:**")
            total_decolagens_periodo = df_decolagens['total_decolagens'].sum()
            media_mensal = df_decolagens['total_decolagens'].mean()
            mes_maior = df_decolagens.loc[df_decolagens['total_decolagens'].idxmax()]
            
            st.metric("Total no Período", f"{int(total_decolagens_periodo):,}")
            st.metric("Média Mensal", f"{int(media_mensal):,}")
            st.write(f"**Pico:** {int(mes_maior['mes'])}/{int(mes_maior['ano'])}")
            st.write(f"**Valor:** {int(mes_maior['total_decolagens']):,}")
        
        # Tabela de decolagens
        st.markdown("#### 📋 Tabela de Decolagens por Mês")
        df_decolagens_display = df_decolagens[['ano', 'mes', 'total_decolagens', 'total_voos', 'media_decolagens_por_voo']].copy()
        df_decolagens_display.columns = ['Ano', 'Mês', 'Total Decolagens', 'Total Voos', 'Média Decolagens/Voo']
        df_decolagens_display['Total Decolagens'] = df_decolagens_display['Total Decolagens'].apply(lambda x: f"{int(x):,}")
        df_decolagens_display['Total Voos'] = df_decolagens_display['Total Voos'].apply(lambda x: f"{int(x):,}")
        df_decolagens_display['Média Decolagens/Voo'] = df_decolagens_display['Média Decolagens/Voo'].apply(lambda x: f"{x:.2f}")
        
        st.dataframe(df_decolagens_display, use_container_width=True)
    else:
        st.warning("⚠️ Nenhum dado de decolagens encontrado para os filtros selecionados.")

    # --- Nova seção: Distância Total por Rota/Empresa ---
    st.markdown("### 🗺️ Distância Total Voada por Rota e Empresa")
    
    # Filtros para distância
    col_filtro1, col_filtro2 = st.columns(2)
    
    with col_filtro1:
        empresas_dist = pd.read_sql_query("SELECT DISTINCT empresa_sigla FROM voo ORDER BY empresa_sigla", conn)['empresa_sigla'].tolist()
        empresa_selecionada_dist = st.selectbox("Empresa:", ['Todas'] + empresas_dist, key="empresa_distancia")
    
    with col_filtro2:
        tipos_voo_dist = ['Todos', 'DOMESTICA', 'INTERNACIONAL']
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
                           color=['#FF6B6B' if nat == 'DOMESTICA' else '#4ECDC4' for nat in top_15_empresas['natureza']])
            
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
                           color=['#FF6B6B' if nat == 'DOMESTICA' else '#4ECDC4' for nat in top_20_rotas['natureza']])
            
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

<<<<<<< Updated upstream
# Fechar conexão
conn.close()
=======


            
>>>>>>> Stashed changes
