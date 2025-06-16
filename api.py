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
import streamlit_pills as stp
from geopy.geocoders import Nominatim
import pydeck as pdk
import streamlit_pills as stp

conn = sqlite3.connect("dados_voo.db")
cursor = conn.cursor()

st.set_page_config(
    page_title="Análise de Dados de Voos",
    page_icon="✈️",
    layout="wide"
)


home_css = """
<style>
    /* Metrics styling */
    [data-testid="metric-container"] {
        background-color: #f8fafc;
        border: 1px solid #A4C4F5;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        text-align: center;
    }
/* Big numbers styling */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        border: 0.5px solid #A4C4F5;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border-left: 8px solid #a4c4f5; /* Borda padrão, será sobrescrita pela cor específica */
        align: center;
    }
    
    .metric-card h3 {
        margin: 1.0rem 0;
        font-size: 24px;
        font-weight: 700;
        color: #275cbd;
        text-align: center;
        align: center;
    }
    
    .metric-card p {
        margin: 0.5rem 0 0 0;
        font-size: 1rem;
        opacity: 0.9;
        color: #275cbd;
        align: center;
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
        background-color: #f9f9f9;
        padding: 1.5rem;
        border-radius: 0.75rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
    }
    
    .chart-container h4 {
        color: #1e40af;
        border: 0.1px solid #A4C4F5; 
        text-align: center;
        margin-bottom: 1rem;
    }
</style>"""

st.markdown("""
<style>
/* A classe principal para TODOS os cards */
.custom-card {
    /* Estrutura e Sombra */
    background-color: white;
    padding: 1.5rem;
    border-radius: 0.75rem;
    border: 0.5px solid #A4C4F5;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    margin: 0.5rem 0;

    /* A MÁGICA DO ALINHAMENTO E TAMANHO */
    display: flex;
    flex-direction: column;
    align-items: center;      /* Centraliza horizontalmente */
    justify-content: center;    /* Centraliza verticalmente */
    height: 100%;             /* Força a mesma altura para cards na mesma linha */
    text-align: center;       /* Garante que o texto dentro dos elementos também seja centralizado */
}

/* Estilos para textos específicos dentro dos cards */
.card-title {
    color: #275cbd;
    font-size: 1.2rem;
    font-weight: bold;
    margin-bottom: 1rem;
}

.card-rank {
    color: #275cbd;
    font-size: 1.1rem;
    font-weight: bold;
    margin-bottom: 0.5rem;
}

.card-main-text {
    font-weight: bold;
    font-size: 1rem;
    margin: 0.25rem 0;
}

.card-sub-text {
    font-size: 0.8rem;
    color: #275cbd;
    margin: 0.25rem 0;
}

.card-metric-value {
    font-size: 1.75rem;
    font-weight: 600;
    color: #275cbd;
    margin: 0;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* A classe principal para TODOS os cards */
.custom-card-section {
    /* Estrutura e Sombra */
    background-color: white;
    padding: 1.0rem;
    border-radius: 0.75rem;
    border: 0.5px solid #f9f9f9;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    margin: 0.5rem 0;

    /* A MÁGICA DO ALINHAMENTO E TAMANHO */
    display: flex;
    flex-direction: column;
    align-items: center;      /* Centraliza horizontalmente */
    justify-content: center;    /* Centraliza verticalmente */
    height: 100%;             /* Força a mesma altura para cards na mesma linha */
    text-align: center;       /* Garante que o texto dentro dos elementos também seja centralizado */
}
</style>
""", unsafe_allow_html=True)


# classe para o headers de titulo dentro
st.markdown("""
<style>
.title-card {
    /* Estrutura e Fundo */
    background-color: #F0F8FF; /* Um azul super claro (AliceBlue) */
    padding: 0.75rem 1.5rem;   /* Espaçamento interno (vertical e horizontal) */
    border-radius: 0.5rem;    /* Cantos arredondados */
    box-shadow: 0 2px 4px rgba(0,0,0,0.05); /* Sombra sutil */
    
    /* Espaçamento Externo */
    margin-top: 2rem;         /* Espaço acima do título */
    margin-bottom: 1.5rem;   /* Espaço abaixo do título */
}

/* Estilo para o texto do título dentro do card */
.title-card h2, .title-card h3, .title-card h4 {
    margin: 0;                /* Remove a margem padrão dos títulos */
    color: #1e40af;           /* Cor do texto (azul escuro do seu tema) */
    text-align: center;       /* Centraliza o texto */
    font-weight: 600;         /* Peso da fonte */
}
            
.title-header p{ margin: 0; color: #275cbd; text-align: center; font-weight: 400;}
            
.filter-card {
    background-color: #f8fafc; /* Um cinza/azul muito claro */
    border: 1px solid #e2e8f0;
    border-radius: 1rem;      /* Cantos mais arredondados */
    padding: 1.5rem;          /* Mais espaçamento interno */
    margin-bottom: 2rem;      /* Espaço abaixo do card */
    box-shadow: 0 4px 12px 0 rgba(0, 0, 0, 0.05); /* Sombra suave */
}
</style>
""", unsafe_allow_html=True)


opcoes_menu = [
    "Análises Operacionais", "Painel de eficiência", "Eficiência Combustível",
    "Análise de Voos Improdutivos Combustivel", "Análise de Voos Improdutivos Passageiros/Bagagem",
    "Rota e Geografia", "KPIs Gerenciais","Aeroportos"
]

icones_menu = ["📌", "🔍", "⛽", "🚫", "🚫", "🌎", "📊","✈️"]

pagina_atual = stp.pills(
    label="Categorias",
    options=opcoes_menu,
    icons=icones_menu
)

# Inicializa o rastreador da página anterior, se não existir
if 'pagina_anterior' not in st.session_state:
    st.session_state.pagina_anterior = pagina_atual

# Verifica se o usuário trocou de página
if st.session_state.pagina_anterior != pagina_atual:
    # Se trocou, limpa o estado dos filtros da página de "Análises Operacionais"
    # para evitar conflitos quando voltar.
    keys_para_limpar = ['empresa_distancia', 'tipo_voo_distancia']
    for key in keys_para_limpar:
        if key in st.session_state:
            del st.session_state[key]
   
    # Atualiza o rastreador para a página atual
    st.session_state.pagina_anterior = pagina_atual

# Função para criar big numbers
def create_big_number_card(title, value, subtitle=""):
    st.markdown(f"""
    <div class="metric-card">
        <h3>{value}</h3>
        <p>{title}</p>
        {f'<small style="opacity: 0.75; color: #64748b;">{subtitle}</small>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)

if pagina_atual == 'Análises Operacionais':
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
    

    # Header principal
    st.markdown("""
    <div class="section-header">
        <h1 style='margin: 0; font-size: 2.5rem;'>✈️ Dashboard de Análise de Voos</h1>
        <p style='margin: 0.5rem 0 0 0; opacity: 0.9;'>Visão geral dos dados operacionais</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Seção de Indicadores com o novo card de título
    st.markdown("""
    <div class="title-card">
        <h2>📊 Indicadores Principais</h2>
    </div>
    """, unsafe_allow_html=True)
    
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
    st.markdown("""
    <div class="title-card">
        <h2>🌍 Comparação de Voos Nacionais vs Internacionais</h2>
    </div>
    """, unsafe_allow_html=True)

    # As suas queries para buscar os dados
    query_nacional = """
        SELECT
            'NACIONAL' as tipo_voo, COUNT(*) as total_voos, SUM(v.decolagens) as total_decolagens,
            SUM(v.distancia_voada_km) as total_distancia_km, SUM(v.combustivel_litros) as total_combustivel_litros,
            SUM(v.horas_voadas) as total_horas_voadas, SUM(c.passageiros_pagos) as total_passageiros_pagos,
            SUM(c.passageiros_gratis) as total_passageiros_gratis, AVG(v.distancia_voada_km) as media_distancia_km,
            AVG(v.combustivel_litros) as media_combustivel_litros
        FROM voo_nacional v
        LEFT JOIN carga_passageiros c ON v.voo_id = c.voo_id
    """
    query_internacional = """
        SELECT
            'INTERNACIONAL' as tipo_voo, COUNT(*) as total_voos, SUM(v.decolagens) as total_decolagens,
            SUM(v.distancia_voada_km) as total_distancia_km, SUM(v.combustivel_litros) as total_combustivel_litros,
            SUM(v.horas_voadas) as total_horas_voadas, SUM(c.passageiros_pagos) as total_passageiros_pagos,
            SUM(c.passageiros_gratis) as total_passageiros_gratis, AVG(v.distancia_voada_km) as media_distancia_km,
            AVG(v.combustivel_litros) as media_combustivel_litros
        FROM voo_internacional v
        LEFT JOIN carga_passageiros c ON v.voo_id = c.voo_id
    """
    df_nacional = pd.read_sql_query(query_nacional, conn)
    df_internacional = pd.read_sql_query(query_internacional, conn)
    df_comparacao = pd.concat([df_nacional, df_internacional], ignore_index=True)

    col1, col2 = st.columns(2)

    # Card de Voos Nacionais
    with col1:
        if not df_nacional.empty and pd.notna(df_nacional['total_voos'].iloc[0]):
            voos = f"{(df_nacional['total_voos'].iloc[0]):,}"
            passageiros = f"{(df_nacional['total_passageiros_pagos'].iloc[0]):,}"
            distancia = f"{df_nacional['total_distancia_km'].iloc[0]:,.0f}"

            html_card_nacional = f"""
            <div class="custom-card-section">
            <h3 class="card-title">🇧🇷 Voos Nacionais</h3>
            <hr style="width: 80%; text-align: center; border: none; border-top: 1px solid #e2e8f0; margin: 0 0 1rem 0;">
            
            <div style="display: flex; width: 100%; justify-content: space-around; margin-bottom: 1rem;">
                <div>
                    <p class="card-sub-text">Total Voos</p>
                    <h2 class="card-metric-value" style="font-size: 1.5rem;">{voos}</h2>
                    </div>
                    <div>
                        <p class="card-sub-text">Passageiros</p>
                        <h2 class="card-metric-value" style="font-size: 1.5rem;">{passageiros}</h2>
                    </div>
                    <div>
                        <p class="card-sub-text">Distância Total (km)</p>
                        <h2 class="card-metric-value" style="font-size: 1.5rem;">{distancia}</h2>
                    </div>
                </div>
            </div>"""
            st.markdown(html_card_nacional, unsafe_allow_html=True)
        else:
            st.markdown("<div class='custom-card'><h3 class='card-title'>🇧🇷 Voos Nacionais</h3><p>Dados não disponíveis.</p></div>", unsafe_allow_html=True)

    # Card de Voos Internacionais
    with col2:
        if not df_internacional.empty and pd.notna(df_internacional['total_voos'].iloc[0]):
            voos_int = f"{int(df_internacional['total_voos'].iloc[0]):,}"
            passageiros_int = f"{int(df_internacional['total_passageiros_pagos'].iloc[0]):,}"
            distancia_int = f"{int(df_internacional['total_distancia_km'].iloc[0]):,.0f}"

            html_card_internacional = f"""
            <div class="custom-card-section">
            <h3 class="card-title">🌐 Voos Internacionais</h3>
            <hr style="width: 80%; text-align: center; border: none; border-top: 1px solid #e2e8f0; margin: 0 0 1rem 0;">
            
            <div style="display: flex; width: 100%; justify-content: space-around; margin-bottom: 1rem;">
                <div>
                    <p class="card-sub-text">Total Voos</p>
                    <h2 class="card-metric-value" style="font-size: 1.5rem;">{voos_int}</h2>
                    </div>
                    <div>
                        <p class="card-sub-text">Passageiros</p>
                        <h2 class="card-metric-value" style="font-size: 1.5rem;">{passageiros_int}</h2>
                    </div>
                    <div>
                        <p class="card-sub-text">Distância Total (km)</p>
                        <h2 class="card-metric-value" style="font-size: 1.5rem;">{distancia_int}</h2>
                    </div>
                </div>
            </div>"""
            st.markdown(html_card_internacional, unsafe_allow_html=True)
        else:
            st.markdown("<div class='custom-card'><h3 class='card-title'>🌐 Voos Internacionais</h3><p>Dados não disponíveis.</p></div>", unsafe_allow_html=True)
            
    # Gráficos principais com plotly
    st.markdown("---")
    st.markdown("""
    <div class="title-card">
        <h2>📈 Análises Visuais</h2>
    </div>
    """, unsafe_allow_html=True)
        
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
        # Refatorado para usar st.container com borda nativa
        with st.container(border=True):
            st.markdown("<h4 style='color: #1e40af; text-align: center; font-size: 1.2rem;'>🏢 Top 10 Empresas por Voos</h4>", unsafe_allow_html=True)
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
                margin=dict(l=10, r=10, t=10, b=10),
                font=dict(size=10)
            )
            fig_empresas.update_yaxes(categoryorder="total ascending")
            st.plotly_chart(fig_empresas, use_container_width=True)
    
    with col2:
        # Refatorado para usar st.container com borda nativa
        with st.container(border=True):
            st.markdown("<h4 style='color: #1e40af; text-align: center; font-size: 1.2rem;'>👥 Passageiros por Empresa</h4>", unsafe_allow_html=True)
            fig_passageiros = px.bar(
                df_top_empresas,
                x='total_passageiros',
                y='empresa_sigla',
                orientation='h',
                color='total_passageiros',
                color_continuous_scale='Purples', # Alterado para 'Purples' para consistência
                height=300
            )
            fig_passageiros.update_layout(
                showlegend=False,
                margin=dict(l=10, r=10, t=10, b=10),
                font=dict(size=10)
            )
            fig_passageiros.update_yaxes(categoryorder="total ascending")
            st.plotly_chart(fig_passageiros, use_container_width=True)

    # --- Filtros e análise por empresa (seção original mantida) ---
    st.markdown("---")
    st.markdown("""
    <div class="title-card">
        <h2>🏢 Análise por Empresa Aérea</h2>
    </div>
    """, unsafe_allow_html=True)

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

    
    # --- Nova seção: Distância Total por Rota/Empresa ---
    st.markdown("---")
    st.markdown("""
    <div class="title-card">
        <h2>🗺️ Distância Total Voada por Rota e Empresa</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Filtros para distância
    col_filtro1, col_filtro2 = st.columns(2)
    
    with col_filtro1:
        empresas_dist_query = """
        SELECT DISTINCT e.empresa_sigla, e.empresa_nome
        FROM voo v
        JOIN empresa e ON v.empresa_sigla = e.empresa_sigla
        ORDER BY e.empresa_nome
        """
        empresas_dist_df = pd.read_sql_query(empresas_dist_query, conn)
        opcoes_empresas_dist = ['Todas'] + [f"{row['empresa_nome']} ({row['empresa_sigla']})" for _, row in empresas_dist_df.iterrows()]
        empresa_selecionada_dist_display = st.selectbox("Empresa:", opcoes_empresas_dist, key="empresa_distancia")
        
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
        where_conditions_dist = []
        if empresa_selecionada_dist != 'Todas':
            where_conditions_dist.append(f"v.empresa_sigla = '{empresa_selecionada_dist}'")
        if tipo_voo_selecionado_dist != 'Todos':
            where_conditions_dist.append(f"v.natureza = '{tipo_voo_selecionado_dist}'")
        
        where_clause_dist = "WHERE " + " AND ".join(where_conditions_dist) if where_conditions_dist else ""
        
        query_distancia_empresa = f"""
        SELECT
            v.empresa_sigla, e.empresa_nome, v.natureza,
            SUM(v.distancia_voada_km) as distancia_total,
            COUNT(*) as total_voos
        FROM voo v
        JOIN empresa e ON v.empresa_sigla = e.empresa_sigla
        {where_clause_dist}
        GROUP BY v.empresa_sigla, e.empresa_nome, v.natureza
        ORDER BY distancia_total DESC
        """
        df_distancia_empresa = pd.read_sql_query(query_distancia_empresa, conn)

        df_para_exibir = pd.DataFrame() 

        if tipo_voo_selecionado_dist == 'Todas':
            df_agregado = df_distancia_empresa.groupby(['empresa_sigla', 'empresa_nome']).agg(
                distancia_total=('distancia_total', 'sum'),
                total_voos=('total_voos', 'sum')
            ).reset_index()
            df_agregado['natureza'] = 'Total (Nac + Int)'
            df_para_exibir = df_agregado.sort_values(by='distancia_total', ascending=False)
        else:
            df_para_exibir = df_distancia_empresa

        if not df_para_exibir.empty:
            st.markdown("#### 🏆 Top 5 Empresas por Distância")
            top_empresas = df_para_exibir.head(5)
            
            num_resultados = len(top_empresas)
            cols = st.columns(num_resultados) if num_resultados > 0 else []

            for i, (_, row) in enumerate(top_empresas.iterrows()):
                with cols[i]:
                    if row['natureza'] == 'DOMÉSTICA':
                        pill_style = "background-color: #275CBD; color: white;"
                    else:
                        pill_style = "background-color: #A4C4F5; color: #1c1b1f;"
                    
                    st.markdown(f"""
                    <div class="custom-card">
                        <p class="card-main-text" style="font-size: 1.1rem; color: #1e40af; margin-bottom: 0.5rem;"> {i+1}º {row['empresa_sigla']} </p>
                        <span style='{pill_style} padding: 0.2rem 0.8rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; margin: 0.5rem 0;'>
                            {row['natureza']}
                        </span>
                        <p class="card-main-text" style="color: #1e40af;">{row['distancia_total']:,.0f} km</p>
                        <p class="card-sub-text">{int(row['total_voos']):,} voos</p>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            top_15_empresas = df_para_exibir.head(15)
            
            fig_dist_empresa = px.bar(
                top_15_empresas, 
                x='distancia_total', 
                y='empresa_sigla',
                orientation='h', 
                color='natureza',
                title='<b>Top 15 Empresas por Distância Total Voada</b>',
                text='distancia_total',
                color_discrete_map={
                    'DOMÉSTICA': "#275CBD",
                    'INTERNACIONAL': "#A4C4F5",
                    'Total (Nac + Int)': "#3b82f6"
                }
            )
            fig_dist_empresa.update_layout(yaxis={'categoryorder':'total ascending'})
            fig_dist_empresa.update_traces(
                texttemplate='%{text:,.0f} km',
                textposition='inside',
                insidetextanchor='middle',
                textfont_size=14 # Reduzido para melhor visualização
            )
            for trace in fig_dist_empresa.data:
                if trace.name == 'DOMÉSTICA' or trace.name == 'Total (Nac + Int)':
                    trace.textfont.color = 'white'
                elif trace.name == 'INTERNACIONAL':
                    trace.textfont.color = '#1c1b1f'

            st.plotly_chart(fig_dist_empresa, use_container_width=True)
            
            st.markdown("#### 📋 Resumo por Empresa")
            st.dataframe(df_para_exibir, use_container_width=True)
        else:
            st.warning("⚠️ Nenhum dado encontrado para os filtros selecionados.")
    
    with tab2:
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
            df_distancia_rota['rota'] = df_distancia_rota['aeroporto_origem_sigla'] + ' → ' + df_distancia_rota['aeroporto_destino_sigla']
            
            st.markdown("#### 🛣️ Top 5 Rotas por Distância")
            top_5_rotas = df_distancia_rota.head(5)
            
            cols = st.columns(5)
            for i, (_, row) in enumerate(top_5_rotas.iterrows()):
                with cols[i]:
                    if row['natureza'] == 'DOMÉSTICA':
                        pill_style = "background-color: #275CBD; color: white;"
                    else:
                        pill_style = "background-color: #A4C4F5; color: #1c1b1f;"

                    st.markdown(f"""
                    <div class="custom-card">
                        <p class="card-main-text" style="font-size: 1.1rem; color: #1e40af; margin-bottom: 0.5rem;"> {i+1}º {row['rota']} </p>
                        <span style='{pill_style} padding: 0.2rem 0.8rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; margin: 0.5rem 0;'>
                            {row['natureza']}
                        </span>
                        <p class="card-main-text" style="color: #1e40af;">{row['distancia_total']:,.0f} km</p>
                        <p class="card-sub-text">{int(row['total_voos']):,} voos</p>
                        <p class="card-sub-text">{int(row['num_empresas']):,} empresas</p>
                    </div>
                    """, unsafe_allow_html=True)

            top_20_rotas = df_distancia_rota.head(20)
            
            fig_dist_rota = px.bar(
                top_20_rotas,
                x='distancia_total',
                y='rota',
                orientation='h',
                color='natureza',
                title='<b>Top 20 Rotas por Distância Total Voada</b>',
                text='distancia_total',
                labels={
                    "distancia_total": "Distância Total (km)",
                    "rota": "Rota",
                    "natureza": "Tipo de Voo"
                },
                color_discrete_map={
                    'DOMÉSTICA': '#275CBD',
                    'INTERNACIONAL': '#A4C4F5'
                },
                hover_data={
                    'nome_origem': True,
                    'nome_destino': True,
                    'total_voos': True,
                    'distancia_total': ':.0f'
                }
            )
            fig_dist_rota.update_layout(
                yaxis={'categoryorder':'total ascending'},
                height=700,
                legend=dict(
                    orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1
                )
            )
            fig_dist_rota.update_traces(
                textposition='inside', 
                insidetextanchor='middle', 
                texttemplate='%{text:,.0f} km', 
                textfont_size=12
            )
            for trace in fig_dist_rota.data:
                if trace.name == 'DOMÉSTICA':
                    trace.textfont.color = 'white'
                elif trace.name == 'INTERNACIONAL':
                    trace.textfont.color = '#1c1b1f'

            st.plotly_chart(fig_dist_rota, use_container_width=True)
            
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

elif pagina_atual == 'Painel de eficiência':

    # Os blocos de <style> específicos desta página foram removidos.
    # Eles devem ser consolidados no seu bloco de estilos globais no início do script.
    st.markdown(home_css, unsafe_allow_html=True)
    # Header principal da página
    st.markdown("""
    <div class="section-header">
        <h1 style='margin: 0; font-size: 2.5rem;'>🔍 Painel de Eficiência por Empresa</h1>
    </div>
    """, unsafe_allow_html=True)

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

    # Abas da página
    tab1, tab2 = st.tabs(["🔎 Métricas por Empresa", "📈 Análise Comparativa"])

    # --- ABA 1: Métricas por Empresa ---
    with tab1:
        # Título da aba com o novo estilo
        st.markdown("""
        <div class="title-card">
            <h3>🔎 Métricas Detalhadas por Empresa</h3>
        </div>
        """, unsafe_allow_html=True)

        empresa_selecionada = st.selectbox(
            "Selecione uma empresa:",
            options=sorted(df['empresa_nome'].unique()),
            index=0,
            key="painel_eficiencia_selectbox_empresa_2" # Chave única
        )

        df_empresa = df[df['empresa_nome'] == empresa_selecionada]

        if not df_empresa.empty:
            # Cálculos
            total_voos = df_empresa['decolagens'].sum()
            distancia_total = df_empresa['distancia_voada_km'].sum()
            horas_totais = df_empresa['horas_voadas'].sum()
            media_distancia = distancia_total / total_voos if total_voos > 0 else 0
            
            eficiencia = None
            df_com_combustivel = df_empresa[df_empresa['combustivel_litros'] > 0]
            if not df_com_combustivel.empty:
                soma_combustivel = df_com_combustivel['combustivel_litros'].sum()
                if soma_combustivel > 0:
                    eficiencia = df_com_combustivel['distancia_voada_km'].sum() / soma_combustivel

            # VOLTANDO AO SEU CÓDIGO ORIGINAL PARA OS CARDS DE KPI
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                    st.markdown(f"""
                        <div class="metric-card" style="background: white; color: #275cbd; padding: 20px; text-align:center;">
                            <div style="font-size: 2.5rem; font-weight: 700;text-align:center;">{total_voos:,}</div>
                            <div style="font-size: 1rem; opacity: 0.8;text-align:center;">Total de Voos</div>
                        </div>
                    """, unsafe_allow_html=True)
            with col2:
                    st.markdown(f"""
                        <div class="metric-card" style="background: white; color: #275cbd; border-radius: 16px; padding: 20px; text-align:center;">
                            <div style="font-size: 2.5rem; font-weight: 700;">{distancia_total:,.0f}</div>
                            <div style="font-size: 1rem; opacity: 0.8;">Distância Total (km)</div>
                        </div>
                    """, unsafe_allow_html=True)
            with col3:
                    if eficiencia is not None:
                        st.markdown(f"""
                            <div class="metric-card" style="background: white; color: #275cbd; border-radius: 16px; padding: 20px; text-align:center;">
                                <div style="font-size: 2.5rem; font-weight: 700;">{eficiencia:.2f}</div>
                                <div style="font-size: 1rem; opacity: 0.8;">Eficiência (km/l)</div>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                            <div class="metric-card" style="background: white; color: #275cbd; border-radius: 16px; padding: 20px; text-align:center; color: #9ca3af;">
                                <div style="font-size: 2.5rem; font-weight: 700;">N/D</div>
                                <div style="font-size: 1rem;">Eficiência (sem dados)</div>
                            </div>
                        """, unsafe_allow_html=True)
            # Outras estatísticas com estilo igual aos anteriores (gradiente azul/roxo)
            with col4:
                    media_distancia = distancia_total / total_voos if total_voos > 0 else 0
                    st.markdown(f"""
                        <div class="metric-card" style="background: white; color: #275cbd; border-radius: 16px; padding: 20px; text-align:center;">
                            <div style="font-size: 2.25rem; font-weight: 700;">{media_distancia:,.0f}</div>
                            <div style="font-size: 1rem; opacity: 0.8;">Média Distância por Voo (km)</div>
                        </div>
                    """, unsafe_allow_html=True)
            with col5:
                    horas_totais = df_empresa['horas_voadas'].sum()
                    st.markdown(f"""
                        <div class="metric-card" style="background: white; color: #275cbd; border-radius: 16px; padding: 20px; text-align:center;">
                            <div style="font-size: 2.25rem; font-weight: 700;">{horas_totais:,.1f}</div>
                            <div style="font-size: 1rem; opacity: 0.8;">Horas Totais de Voo</div>
                        </div>
                    """, unsafe_allow_html=True)
            st.divider()
            # Título para a seção de gráficos
            st.markdown("""
            <div class="title-card">
                <h3>Visualizações Mensais da Empresa</h3>
            </div>
            """, unsafe_allow_html=True)
            
            meses_nomes = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
            
            col_graf1, col_graf2 = st.columns(2)

            with col_graf1:
                with st.container(border=True):
                    st.markdown("<h4 style='color: #1e40af; text-align: center;'>📊 Eficiência Mensal (km/l)</h4>", unsafe_allow_html=True)
                    st.markdown("""</br>""", unsafe_allow_html=True)
                    if df_com_combustivel.empty:
                        st.info("ℹ️ Esta empresa não possui dados de combustível disponíveis. Talvez opere apenas voos internacionais ou os dados não estão registrados.")
                    else:
                        df_empresa_mes = df_com_combustivel.groupby('mes').apply(
                            lambda x: x['distancia_voada_km'].sum() / x['combustivel_litros'].sum()
                        ).reset_index(name='eficiencia_km_l')

                        fig_ef = px.line(
                            df_empresa_mes,
                            x='mes',
                            y='eficiencia_km_l',
                            markers=True,
                            title='',
                            color_discrete_sequence=['#275cbd']
                        )
                        fig_ef.update_layout(
                            xaxis=dict(
                                tickmode='array',
                                tickvals=df_empresa_mes['mes'],
                                ticktext=[meses_nomes[m-1] for m in df_empresa_mes['mes']]
                            ),
                            yaxis_title='Eficiência (km/l)',
                            xaxis_title='Mês',
                            plot_bgcolor='#ffffff',
                            font=dict(color='#1f2937'),
                            margin=dict(t=50, b=40, l=40, r=40)
                        )
                        st.plotly_chart(fig_ef, use_container_width=True)
                    
            with col_graf2:
                with st.container(border=True):
                    st.markdown("<h4 style='color: #1e40af; text-align: center;'>✈️ Média de Horas e Km por Voo</h4>", unsafe_allow_html=True)
                    st.markdown("""</br>""", unsafe_allow_html=True)
                    df_horas_mes = df_empresa.groupby('mes').agg({
                        'horas_voadas': 'sum',
                        'decolagens': 'sum',
                        'distancia_voada_km': 'sum'
                    }).reset_index()

                    df_horas_mes['media_horas_por_voo'] = df_horas_mes.apply(
                        lambda row: row['horas_voadas'] / row['decolagens'] if row['decolagens'] > 0 else 0,
                        axis=1
                    )
                    df_horas_mes['media_km_por_voo'] = df_horas_mes.apply(
                        lambda row: row['distancia_voada_km'] / row['decolagens'] if row['decolagens'] > 0 else 0,
                        axis=1
                    )

                    fig_mix = go.Figure()
                    fig_mix.add_trace(go.Scatter(
                        x=df_horas_mes['mes'],
                        y=df_horas_mes['media_horas_por_voo'],
                        name='Horas por Voo',
                        mode='lines+markers',
                        line=dict(color='#275cbd'),
                        yaxis='y1'
                    ))
                    fig_mix.add_trace(go.Scatter(
                        x=df_horas_mes['mes'],
                        y=df_horas_mes['media_km_por_voo'],
                        name='Km por Voo',
                        mode='lines+markers',
                        line=dict(color="#a4c4f5"),
                        yaxis='y2'
                    ))

                    fig_mix.update_layout(
                        title='',
                        xaxis=dict(
                            tickmode='array',
                            tickvals=df_horas_mes['mes'],
                            ticktext=[meses_nomes[m-1] for m in df_horas_mes['mes']],
                            title='Mês'
                        ),
                        yaxis=dict(
                            title='Horas por Voo',
                            tickfont=dict(color="#1d1b1f")
                        ),
                        yaxis2=dict(
                            title='Km por Voo',
                            overlaying='y',
                            side='right',
                            tickfont=dict(color='#1f2937')
                        ),
                        plot_bgcolor='#ffffff',
                        font=dict(color='#1f2937'),
                        margin=dict(t=50, b=40, l=40, r=40),
                        legend=dict(x=0.01, y=0.99)
                    )
                    st.plotly_chart(fig_mix, use_container_width=True)

                    # Gráfico 2: Distância Voada x Combustível por Mês (fica embaixo)
                            
        else:
            st.warning("⚠️ Nenhum dado encontrado para a empresa selecionada.")

    with st.container(border=True):
                    st.markdown("<h4 style='color: #1e40af; text-align: center;'>Distância e Combustível por Mês</h4>", unsafe_allow_html=True)
                    df_mes_bar = df_empresa.groupby('mes').agg(distancia_voada_km=('distancia_voada_km', 'sum'), combustivel_litros=('combustivel_litros', 'sum')).reset_index()
                    fig_bar = px.bar(df_mes_bar.melt(id_vars='mes', value_vars=['distancia_voada_km', 'combustivel_litros']), x='mes', y='value', color='variable', barmode='group', color_discrete_map={'distancia_voada_km': '#275cbd', 'combustivel_litros': '#a4c4f5'})
                    fig_bar.update_layout(xaxis=dict(tickmode='array', tickvals=df_mes_bar['mes'], ticktext=[meses_nomes[m-1] for m in df_mes_bar['mes']]), yaxis_title='Quantidade', xaxis_title='Mês', plot_bgcolor='#ffffff', margin=dict(t=20, b=20, l=20, r=20))
                    st.plotly_chart(fig_bar, use_container_width=True)
    # Continuação do código para a página 'Eficiência Combustível'
    with tab2:
        # --- ABA 2 ---
    # Título principal da aba, usando o novo estilo
        st.markdown("""
        <div class="title-card">
            <h3>📈 Análise Comparativa e Geral</h3>
        </div>
        """, unsafe_allow_html=True)

        # --- Seção de Filtros ---
        st.markdown("#### Filtros para Comparação")
        col1, col2 = st.columns(2)
        empresas = sorted(df['empresa_nome'].unique())
        meses = sorted(df['mes'].unique())

        with col1:
            empresa_filtro = st.multiselect("Filtrar por Empresa:", options=empresas, placeholder="Selecione uma ou mais empresas")
        with col2:
            meses_filtro = st.multiselect("Filtrar por Mês:", options=meses, placeholder="Selecione um ou mais meses")

        # --- Lógica de exibição baseada nos filtros ---
        if empresa_filtro and meses_filtro:
            df_filtros = df[(df['empresa_nome'].isin(empresa_filtro)) & (df['mes'].isin(meses_filtro))]

            if df_filtros.empty:
                st.warning("Nenhum dado encontrado com os filtros selecionados.")
            else:
                resumo = df_filtros.groupby('empresa_nome').agg(
                    decolagens=('decolagens', 'sum'),
                    distancia_voada_km=('distancia_voada_km', 'sum'),
                    horas_voadas=('horas_voadas', 'sum'),
                    combustivel_litros=('combustivel_litros', 'sum')
                ).reset_index()
                
                resumo['eficiencia_km_l'] = resumo.apply(lambda r: r['distancia_voada_km'] / r['combustivel_litros'] if r['combustivel_litros'] > 0 else 0, axis=1)
                resumo['velocidade_kmh'] = resumo.apply(lambda r: r['distancia_voada_km'] / r['horas_voadas'] if r['horas_voadas'] > 0 else 0, axis=1)
                resumo['media_km_por_voo'] = resumo.apply(lambda r: r['distancia_voada_km'] / r['decolagens'] if r['decolagens'] > 0 else 0, axis=1)
                
                st.markdown("#### 📋 Resumo por Empresa (Filtro Aplicado)")
                st.dataframe(resumo.rename(columns={'empresa_nome': 'Empresa', 'decolagens': 'Voos', 'distancia_voada_km': 'Distância (km)', 'horas_voadas': 'Horas Voadas', 'combustivel_litros': 'Combustível (L)', 'media_km_por_voo': 'Média km/Voo', 'eficiencia_km_l': 'Eficiência (km/l)', 'velocidade_kmh': 'Velocidade Média (km/h)'}), use_container_width=True, hide_index=True)

                st.markdown("#### 📎 Dados Detalhados por Voo (Filtro Aplicado)")
                st.dataframe(df_filtros[['empresa_nome', 'mes', 'distancia_voada_km', 'horas_voadas', 'combustivel_litros', 'decolagens']], use_container_width=True, height=400)
        else:
            st.info("ℹ️ Selecione ao menos uma empresa e um mês para visualizar as análises comparativas.")

        # --- CONTEÚDO RESTAURADO: GRÁFICOS DE ANÁLISE GERAL ---
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("""
        <div class="title-card">
            <h3>🌐 Análise Geral (Todas as Empresas e Meses)</h3>
        </div>
        """, unsafe_allow_html=True)

        # Preparação dos dados para os gráficos gerais
        df_com_combustivel_geral = df[df['combustivel_litros'] > 0]
        df_eficiencia_geral_mes = df_com_combustivel_geral.groupby('mes').apply(lambda x: x['distancia_voada_km'].sum() / x['combustivel_litros'].sum() if x['combustivel_litros'].sum() > 0 else 0).reset_index(name='eficiencia')
        meses_labels = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        
        df_top10 = df_com_combustivel_geral.groupby(['empresa_nome']).apply(lambda x: x['distancia_voada_km'].sum() / x['combustivel_litros'].sum()).reset_index(name='eficiencia_km_l').sort_values(by='eficiencia_km_l', ascending=False).head(10)
        df_velocidade = df.groupby('empresa_nome').agg(distancia_voada_km=('distancia_voada_km', 'sum'), horas_voadas=('horas_voadas', 'sum')).reset_index()
        df_velocidade['velocidade_media_kmh'] = df_velocidade.apply(lambda r: r['distancia_voada_km'] / r['horas_voadas'] if r['horas_voadas'] > 0 else 0, axis=1)
        df_velocidade_top10 = df_velocidade.sort_values(by='velocidade_media_kmh', ascending=False).head(10)
        df_volume = df.groupby('mes').agg(decolagens=('decolagens', 'sum'), combustivel_litros=('combustivel_litros', 'sum')).reset_index()

        # Exibição dos gráficos gerais
        with st.container(border=True):
            st.markdown("<h4 style='color: #1e40af; text-align: center;'>📈 Eficiência Média Geral por Mês</h4>", unsafe_allow_html=True)
            fig_eficiencia_mes = px.line(df_eficiencia_geral_mes, x="mes", y="eficiencia", markers=True, color_discrete_sequence=["#6366f1"])
            ticks_labels = [meses_labels[m - 1] for m in df_eficiencia_geral_mes['mes']]
            fig_eficiencia_mes.update_layout(xaxis=dict(tickmode='array', tickvals=df_eficiencia_geral_mes['mes'], ticktext=ticks_labels), yaxis_title="Eficiência (km/l)", plot_bgcolor="#ffffff", margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(fig_eficiencia_mes, use_container_width=True)

        cols_gerais = st.columns(2)
        with cols_gerais[0]:
            with st.container(border=True):
                st.markdown("<h4 style='color: #1e40af; text-align: center;'>🏆 Top 10 Empresas Mais Eficientes</h4>", unsafe_allow_html=True)
                fig_top10_eficiencia = px.bar(df_top10.sort_values('eficiencia_km_l', ascending=True), x='eficiencia_km_l', y='empresa_nome', orientation='h', color='eficiencia_km_l', color_continuous_scale='ice')
                fig_top10_eficiencia.update_layout(xaxis_title='Eficiência (km/l)', yaxis_title='', plot_bgcolor='#ffffff', margin=dict(t=20, b=20, l=20, r=20))
                st.plotly_chart(fig_top10_eficiencia, use_container_width=True)
        with cols_gerais[1]:
            with st.container(border=True):
                st.markdown("<h4 style='color: #1e40af; text-align: center;'>🚀 Top 10 Empresas Mais Rápidas</h4>", unsafe_allow_html=True)
                fig_top10_velocidade = px.bar(df_velocidade_top10.sort_values('velocidade_media_kmh', ascending=True), x='velocidade_media_kmh', y='empresa_nome', orientation='h', color='velocidade_media_kmh', color_continuous_scale='Blues')
                fig_top10_velocidade.update_layout(xaxis_title='Velocidade Média (km/h)', yaxis_title='', plot_bgcolor='#ffffff', margin=dict(t=20, b=20, l=20, r=20))
                st.plotly_chart(fig_top10_velocidade, use_container_width=True)
        
        with st.container(border=True):
            st.markdown("<h4 style='color: #1e40af; text-align: center;'>📦 Volume de Operações e Consumo por Mês</h4>", unsafe_allow_html=True)
            fig_volume = go.Figure()
            fig_volume.add_trace(go.Scatter(x=df_volume['mes'], y=df_volume['decolagens'], name='Total Decolagens', mode='lines+markers', line=dict(color='#a4c4f5'), yaxis='y1'))
            fig_volume.add_trace(go.Scatter(x=df_volume['mes'], y=df_volume['combustivel_litros'], name='Total Combustível (L)', mode='lines+markers', line=dict(color='#275cbd'), yaxis='y2'))
            fig_volume.update_layout(xaxis=dict(title='Mês', tickmode='array', tickvals=df_volume['mes'], ticktext=[meses_labels[m-1] for m in df_volume['mes']]), yaxis=dict(title='Decolagens'), yaxis2=dict(title='Combustível (L)', overlaying='y', side='right'), legend=dict(x=0.01, y=0.99), plot_bgcolor='#ffffff', height=500, margin=dict(t=40, b=40, l=40, r=40))
            st.plotly_chart(fig_volume, use_container_width=True)

elif pagina_atual == 'Eficiência Combustível':

    # As definições de CSS locais foram removidas. 

    st.markdown(home_css, unsafe_allow_html=True)
    # Elas devem estar no bloco GLOBAL_STYLES no início do script.

    # Header principal da página (H1), mantido como está.
    st.markdown("""
    <div class="section-header">
        <h1 style='margin: 0; font-size: 2.5rem;'>⛽ Análise de Eficiência de Combustível</h1>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🏢 Por Empresa", "✈️ Por Rota"])

    with tab1:
        # Título da aba com o novo estilo de card
        st.markdown("""
        <div class="title-card">
            <h3>📊 Eficiência por Empresa</h3>
        </div>
        """, unsafe_allow_html=True)

        query = '''
            SELECT 
                v.empresa_sigla,
                e.empresa_nome,
                SUM(v.distancia_voada_km) AS total_km,
                SUM(v.combustivel_litros) AS total_combustivel
            FROM voo v
            JOIN empresa e ON v.empresa_sigla = e.empresa_sigla
            WHERE v.combustivel_litros > 0
            GROUP BY v.empresa_sigla, e.empresa_nome
            HAVING total_combustivel > 0
            '''
        df = pd.read_sql_query(query, conn)
        df['eficiencia_km_por_litro'] = df['total_km'] / df['total_combustivel']
        media_eficiencia = df['eficiencia_km_por_litro'].mean()
        top3 = df.sort_values(by='eficiencia_km_por_litro', ascending=False).head(3)
        # CORREÇÃO: Pegar os 3 piores corretamente
        bottom3 = df.sort_values(by='eficiencia_km_por_litro', ascending=True).head(3)

        # KPIs principais usando a sua função create_big_number_card, mantendo seu estilo.
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            create_big_number_card("Média Geral", f"{media_eficiencia:.2f} km/l", f"{len(df)} empresas")
        with col2:
            create_big_number_card("Melhor Eficiência", f"{top3.iloc[0]['eficiencia_km_por_litro']:.2f} km/l", top3.iloc[0]['empresa_sigla'])
        with col3:
            create_big_number_card("Pior Eficiência", f"{bottom3.iloc[0]['eficiencia_km_por_litro']:.2f} km/l", bottom3.iloc[0]['empresa_sigla'])
        with col4:
            total_combustivel = df['total_combustivel'].sum()
            create_big_number_card("Total Combustível", f"{total_combustivel/1e6:,.1f}M L", f"{df['total_km'].sum()/1e6:,.1f}M km")

        # Seção Top 3 Mais Eficientes
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("""
        <div class="title-card">
            <h3>🏆 Top 3 Empresas Mais Eficientes</h3>
        </div>
        """, unsafe_allow_html=True)
        cols = st.columns(3)
        for i, (_, row) in enumerate(top3.iterrows()):
            with cols[i]:
                st.markdown(f"""
                <div class="custom-card">
                    <p class="card-rank">{i+1}º Lugar</p>
                    <p class="card-main-text" style="color: #275cbd; font-size: 1.1rem;">{row['empresa_sigla']}</p>
                    <p class="card-sub-text">{row['empresa_nome']}</p>
                    <h3 class="card-metric-value" style="color: #16a34a;">{row['eficiencia_km_por_litro']:.2f} km/l</h3>
                    <p class="card-sub-text">{row['total_km']:,.0f} km voados</p>
                    <p class="card-sub-text">{row['total_combustivel']:,.0f} L consumidos</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Seção Top 3 Menos Eficientes
        st.markdown("""
        <div class="title-card">
            <h3>⚠️ Top 3 Empresas Menos Eficientes</h3>
        </div>
        """, unsafe_allow_html=True)
        cols = st.columns(3)
        for i, (_, row) in enumerate(bottom3.iterrows()):
            with cols[i]:
                st.markdown(f"""
                <div class="custom-card">
                    <p class="card-rank">{len(df)-i}º Lugar</p>
                    <p class="card-main-text" style="color: #1e40af; font-size: 1.1rem;">{row['empresa_sigla']}</p>
                    <p class="card-sub-text">{row['empresa_nome']}</p>
                    <h3 class="card-metric-value" style="color: #dc2626;">{row['eficiencia_km_por_litro']:.2f} km/l</h3>
                    <p class="card-sub-text">{row['total_km']:,.0f} km voados</p>
                    <p class="card-sub-text">{row['total_combustivel']:,.0f} L consumidos</p>
                </div>
                """, unsafe_allow_html=True)

        # Seção de Análises Visuais
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("""
        <div class="title-card">
            <h3>📊 Análises Visuais por Empresa</h3>
        </div>
        """, unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            with st.container(border=True):
                st.markdown("<h4 class='card-title' style='text-align:center;'>📈 Ranking de Eficiência</h4>", unsafe_allow_html=True)
                df_sorted = df.sort_values('eficiencia_km_por_litro', ascending=True)
                fig_eficiencia = px.bar(df_sorted, x='eficiencia_km_por_litro', y='empresa_sigla', orientation='h', title='', color='eficiencia_km_por_litro', color_continuous_scale= 'Blues', labels={'eficiencia_km_por_litro': 'Eficiência (km/l)', 'empresa_sigla': 'Empresa'})
                fig_eficiencia.update_layout(height=475, showlegend=False, margin=dict(l=0, r=0, t=0, b=0))
                fig_eficiencia.add_vline(x=media_eficiencia, line_dash="dash", line_color= "#0026FF", annotation_text=f"Média: {media_eficiencia:.2f}")
                st.plotly_chart(fig_eficiencia, use_container_width=True)
        with col2:
            with st.container(border=True):
                # Título restaurado para o correto
                st.markdown("<h4 class='card-title' style='text-align:center;'>🥧 Distribuição de Eficiência</h4>", unsafe_allow_html=True)
                
                # Gráfico de rosca
                fig_pie = px.pie(
                    df, 
                    # <<< A CORREÇÃO PRINCIPAL ESTÁ AQUI >>>
                    # Voltando a usar a coluna correta, como era no seu original.
                    values='eficiencia_km_por_litro', 
                    
                    names='empresa_sigla',
                    title='',
                    color_discrete_sequence=px.colors.sequential.ice, 
                    hole=0.4
                )
                fig_pie.update_layout(
                    height=475, # Aumentei um pouco para melhor visualização
                    showlegend=False, # Legenda é redundante com os labels no gráfico
                    margin=dict(l=10, r=10, t=30, b=10)
                )
                fig_pie.update_traces(
                    textinfo='percent+label', 
                    textfont_size=13,
                    insidetextorientation='radial'
                )
                st.plotly_chart(fig_pie, use_container_width=True)
        
        # Seção de Análise Individual
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("""
        <div class="title-card">
            <h3>🔍 Análise Individual por Empresa</h3>
        </div>
        """, unsafe_allow_html=True)
        
        empresa_selecionada = st.selectbox("Selecione uma empresa para análise detalhada:", df['empresa_nome'].unique(), key="empresa_combustivel")
        dados_empresa = df[df['empresa_nome'] == empresa_selecionada]
        if not dados_empresa.empty:
            empresa_eficiencia = dados_empresa['eficiencia_km_por_litro'].iloc[0]
            diferenca_media = empresa_eficiencia - media_eficiencia
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Eficiência da Empresa", f"{empresa_eficiencia:.2f} km/l", delta=f"{diferenca_media:+.2f} vs média")
            with col2:
                percentil = (df['eficiencia_km_por_litro'] < empresa_eficiencia).mean() * 100
                st.metric("Posição no Ranking", f"{percentil:.0f}º percentil", delta_color="off")
            with col3:
                economia = (empresa_eficiencia - media_eficiencia) * dados_empresa['total_combustivel'].iloc[0]
                st.metric("Economia vs Média", f"{economia:,.0f} L", delta_color=("inverse" if economia < 0 else "normal"))

    # Continuação...
    with tab2:
        st.markdown("""
        <div class="title-card">
            <h3>🛣️ Eficiência por Rota</h3>
        </div>
        """, unsafe_allow_html=True)
        
        query_rota = '''
            SELECT 
                v.aeroporto_origem_sigla, v.aeroporto_destino_sigla,
                a1.aeroporto_nome AS origem_nome, a2.aeroporto_nome AS destino_nome,
                SUM(v.distancia_voada_km) AS total_km,
                SUM(v.combustivel_litros) AS total_combustivel,
                COUNT(*) as total_voos
            FROM voo v
            JOIN aeroporto a1 ON v.aeroporto_origem_sigla = a1.aeroporto_sigla
            JOIN aeroporto a2 ON v.aeroporto_destino_sigla = a2.aeroporto_sigla
            WHERE v.combustivel_litros > 0 AND v.distancia_voada_km > 0
            GROUP BY v.aeroporto_origem_sigla, v.aeroporto_destino_sigla, a1.aeroporto_nome, a2.aeroporto_nome
            HAVING total_combustivel > 0
            '''
        df_rota = pd.read_sql_query(query_rota, conn)
        df_rota['eficiencia_km_por_litro'] = df_rota['total_km'] / df_rota['total_combustivel']
        df_rota['rota'] = df_rota['aeroporto_origem_sigla'] + " → " + df_rota['aeroporto_destino_sigla']
        df_rota['rota_nome'] = df_rota['origem_nome'] + " → " + df_rota['destino_nome']

        min_voos_rota = st.slider("Filtrar rotas com no mínimo de voos:", 1, 100, 10, key="min_voos_rota_2")
        df_rota_filtrado = df_rota[df_rota['total_voos'] >= min_voos_rota]
        
        if not df_rota_filtrado.empty:
            top_rotas = df_rota_filtrado.sort_values(by='eficiencia_km_por_litro', ascending=False).head(5)
            worst_rotas = df_rota_filtrado.sort_values(by='eficiencia_km_por_litro', ascending=True).head(5)

            col1, col2, col3 = st.columns(3)
            with col1:
                create_big_number_card("Rotas Analisadas", f"{len(df_rota_filtrado)}", f"Com ≥ {min_voos_rota} voos")
            with col2:
                create_big_number_card("Rota Mais Eficiente", f"{top_rotas.iloc[0]['eficiencia_km_por_litro']:.2f} km/l", f"{top_rotas.iloc[0]['rota']}")
            with col3:
                create_big_number_card("Rota Menos Eficiente", f"{worst_rotas.iloc[0]['eficiencia_km_por_litro']:.2f} km/l", f"{worst_rotas.iloc[0]['rota']}")
            
        
            st.markdown("""
            <div class="title-card">
                <h3>🏆 Top 5 Rotas Mais Eficientes</h3>
            </div>
            """, unsafe_allow_html=True)
            cols = st.columns(5)
            for i, (_, row) in enumerate(top_rotas.iterrows()):
                with cols[i]:
                    st.markdown(f"""<div class="custom-card"><p class="card-rank">{i+1}º Lugar</p><p class="card-main-text" style="color: #1e40af; font-size: 0.9rem;">{row['rota']}</p><h3 class="card-metric-value" style="color: #16a34a; font-size: 1.5rem;">{row['eficiencia_km_por_litro']:.2f}</h3><p class="card-sub-text">km/l</p><p class="card-sub-text">{row['total_voos']} voos</p></div>""", unsafe_allow_html=True)
            
            st.markdown("""
            <div class="title-card">
                <h3>⚠️ Top 5 Rotas Menos Eficientes</h3>
            </div>
            """, unsafe_allow_html=True)
            cols = st.columns(5)
            for i, (_, row) in enumerate(worst_rotas.iterrows()):
                with cols[i]:
                    st.markdown(f"""<div class="custom-card"><p class="card-rank">{len(df_rota_filtrado)-i}º Lugar</p><p class="card-main-text" style="color: #1e40af; font-size: 0.9rem;">{row['rota']}</p><h3 class="card-metric-value" style="color: #dc2626; font-size: 1.5rem;">{row['eficiencia_km_por_litro']:.2f}</h3><p class="card-sub-text">km/l</p><p class="card-sub-text">{row['total_voos']} voos</p></div>""", unsafe_allow_html=True)
            
        
            st.markdown("""
            <div class="title-card">
                <h3>📊 Análise Visual das Rotas</h3>
            </div>
            """, unsafe_allow_html=True)
            
            with st.container(border=True):
                st.markdown("<h5 style='text-align: center; color: #1e40af;'>Top 20 Rotas por Eficiência<h5>", unsafe_allow_html=True)
                top_20_rotas = df_rota_filtrado.sort_values('eficiencia_km_por_litro', ascending=False).head(20)
                fig_rotas = px.bar(top_20_rotas.sort_values('eficiencia_km_por_litro', ascending=True), x='eficiencia_km_por_litro', y='rota', orientation='h', title='', color='eficiencia_km_por_litro', color_continuous_scale=['#dbeafe', '#1e40af'], labels={'eficiencia_km_por_litro': 'Eficiência (km/l)', 'rota': 'Rota'}, hover_data={'total_voos': True, 'total_km': True})
                fig_rotas.update_layout(height=600, showlegend=False, margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig_rotas, use_container_width=True)


            st.markdown("""
            <div class="title-card">
                <h3>📋 Dados Detalhados das Rotas</h3>
            </div>
            """, unsafe_allow_html=True)
            df_rota_display = df_rota_filtrado.copy().sort_values('eficiencia_km_por_litro', ascending=False)
            df_rota_display['Eficiência (km/l)'] = df_rota_display['eficiencia_km_por_litro'].round(2)
            df_rota_display['Distância Total (km)'] = df_rota_display['total_km'].apply(lambda x: f"{x:,.0f}")
            df_rota_display['Combustível Total (L)'] = df_rota_display['total_combustivel'].apply(lambda x: f"{x:,.0f}")
            df_rota_display = df_rota_display.rename(columns={'rota': 'Rota (Siglas)', 'rota_nome': 'Rota (Nomes)', 'total_voos': 'Total Voos'})
            colunas_exibir = ['Rota (Siglas)', 'Rota (Nomes)', 'Eficiência (km/l)', 'Total Voos', 'Distância Total (km)', 'Combustível Total (L)']
            st.dataframe(df_rota_display[colunas_exibir], use_container_width=True, height=400)
        else:
            st.warning(f"Nenhuma rota encontrada com no mínimo {min_voos_rota} voos.")

elif pagina_atual == 'Análise de Voos Improdutivos Combustivel':
    
    st.markdown(home_css, unsafe_allow_html=True)
    # --- Funções e Carregamento de Dados ---
    def carregar_dados_improdutivos():
        query = """
        SELECT v.*, e.empresa_nome, a.aeroporto_regiao 
        FROM voo v
        JOIN empresa e ON v.empresa_sigla = e.empresa_sigla
        JOIN aeroporto a ON v.aeroporto_origem_sigla = a.aeroporto_sigla
        """
        df = pd.read_sql_query(query, conn)
        # Pre-calcular a improdutividade para evitar divisão por zero repetidamente
        df['improdutivo'] = (df['combustivel_litros'] > 0) & \
                            (df['distancia_voada_km'] > 0) & \
                            ((df['combustivel_litros'] / df['distancia_voada_km']) > 1)
        return df

    df = carregar_dados_improdutivos()
    
    # --- Layout da Página ---
    st.markdown("""
    <div class="section-header">
        <h1 style='margin: 0; font-size: 2.5rem;'>⛽ Análise de Voos Improdutivos (Combustível)</h1>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="title-card">
        <h3>Panorama Geral da Frota</h3>
    </div>
    """, unsafe_allow_html=True)
    
    total_voos = len(df)
    total_voos_improdutivos = df['improdutivo'].sum()
    percentual_improdutivo = (total_voos_improdutivos / total_voos) * 100 if total_voos > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card" style="color: #275cbd; text-align: center;">
            <div style="font-size: 1.70rem; font-weight: 700;">{total_voos:,}</div>
            <div style="font-size: 1rem; color: #1b1c1f; opacity: 0.8;">Total de Voos Analisados</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card" style="color: #275cbd; text-align: center;">
            <div style="font-size: 1.70rem; font-weight: 700;">{total_voos_improdutivos:,}</div>
            <div style="font-size: 1rem; color: #1b1c1f; opacity: 0.8;">Voos Improdutivos</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card" style="color: #275cbd; text-align: center;">
            <div style="font-size: 1.70rem; font-weight: 700;">{percentual_improdutivo:,.2f}</div>
            <div style="font-size: 1rem; color: #1b1c1f; opacity: 0.8;">% de Voos Improdutivos</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # --- Abas de Análise ---
    tab1, tab2 = st.tabs(["Análise por Empresa", "Distribuição por Região"])

    with tab1:
        st.markdown("""
        <div class="title-card">
            <h3>Análise Detalhada por Empresa</h3>
        </div>
        """, unsafe_allow_html=True)

        st.info("A análise de improdutividade de combustível considera apenas voos domésticos, pois os dados de combustível para voos internacionais não são fornecidos.")
        
        empresas_domesticas = df[df["natureza"].str.upper() == "DOMÉSTICA"]
        empresas_disponiveis = sorted(empresas_domesticas["empresa_nome"].unique())
        
        empresa_selecionada = st.selectbox("Escolha uma empresa:", empresas_disponiveis, key="improdutivo_comb_empresa_final_2")
        df_filtrado_empresa = empresas_domesticas[empresas_domesticas["empresa_nome"] == empresa_selecionada]

        if df_filtrado_empresa.empty:
            st.error("Não há dados de voos domésticos para esta empresa.")
        else:
            with st.container(border=True):
                st.markdown(f"<h4 style='text-align:center; color: #1e40af;'>Consumo vs. Distância para {empresa_selecionada}</h4>", unsafe_allow_html=True)
                st.bar_chart(df_filtrado_empresa[["distancia_voada_km", "combustivel_litros"]])

            voos_empresa = len(df_filtrado_empresa)
            improdutivos_empresa = df_filtrado_empresa['improdutivo'].sum()
            perc_improdutivo_empresa = (improdutivos_empresa / voos_empresa) * 100 if voos_empresa > 0 else 0

            # <<< CORREÇÃO APLICADA AQUI >>>
            # Substituindo st.metric por create_big_number_card para manter a consistência visual.
            st.markdown("<br>", unsafe_allow_html=True)
            col_kpi1, col_kpi2 = st.columns(2)
            with col_kpi1:
                st.markdown(f"""
        <div class="metric-card" style="color: #275cbd; text-align: center;">
            <div style="font-size: 1.70rem; font-weight: 700;">{voos_empresa:,}</div>
            <div style="font-size: 1rem; color: #1b1c1f; opacity: 0.8;">Voos Domésticos da Empresa</div>
        </div>
        """, unsafe_allow_html=True)
            with col_kpi2:
                
                st.markdown(f"""
        <div class="metric-card" style="color: #275cbd; text-align: center;">
            <div style="font-size: 1.70rem; font-weight: 700;">{perc_improdutivo_empresa:,.2f}</div>
            <div style="font-size: 1rem; color: #1b1c1f; opacity: 0.8;">% de Voos Improdutivos</div>
        </div>
        """, unsafe_allow_html=True)
            
            filtro_improdutivo = df_filtrado_empresa[df_filtrado_empresa['improdutivo']]
            if not filtro_improdutivo.empty:
                st.markdown("<hr>", unsafe_allow_html=True)
                st.markdown("""
                <div class="title-card">
                    <h3>🚨 Tabela de Voos Improdutivos Identificados</h3>
                </div>
                """, unsafe_allow_html=True)
                st.dataframe(filtro_improdutivo[['aeroporto_origem_sigla', 'aeroporto_destino_sigla', 'distancia_voada_km', 'combustivel_litros']])
            else:
                st.success(f"✅ Nenhum voo improdutivo identificado para a empresa {empresa_selecionada}.")

    with tab2:
        st.markdown("""
        <div class="title-card">
            <h3>🗺️ Distribuição Geográfica dos Voos Improdutivos</h3>
        </div>
        """, unsafe_allow_html=True)

        df_improdutivos_total = df[df['improdutivo']]
        if "aeroporto_regiao" not in df.columns:
            st.warning("A coluna 'aeroporto_regiao' não está disponível para análise regional.")
        else:
            regioes_improdutivas = df_improdutivos_total["aeroporto_regiao"].value_counts()
            if regioes_improdutivas.empty:
                st.info("Nenhum voo improdutivo foi identificado para análise por região.")
            else:
                with st.container(border=True):
                    st.markdown("<h4 style='text-align:center; color: #1e40af;'>Contagem de Voos Improdutivos por Região de Origem</h4>", unsafe_allow_html=True)
                    fig_regiao = px.bar(regioes_improdutivas, y=regioes_improdutivas.values, x=regioes_improdutivas.index, labels={'x':'Região de Origem', 'y':'Nº de Voos Improdutivos'}, color_discrete_sequence=['#667eea'])
                    st.plotly_chart(fig_regiao, use_container_width=True)

elif pagina_atual == 'Análise de Voos Improdutivos Passageiros/Bagagem':
    st.markdown(home_css, unsafe_allow_html=True)
    # --- Funções da Página ---
    def consulta_carga_passageiros_por_empresa(empresa_sigla=None):
        query = '''
        SELECT 
            c.voo_id, c.passageiros_pagos, c.passageiros_gratis, c.bagagem_kg, 
            c.carga_paga_kg, c.carga_gratis_kg, c.correio_kg, c.carga_paga_km,
            c.carga_gratis_km, v.ano, v.mes, v.empresa_sigla,
            v.aeroporto_origem_sigla, v.aeroporto_destino_sigla
        FROM carga_passageiros c
        JOIN voo v ON c.voo_id = v.voo_id
        '''
        if empresa_sigla:
            query += f" WHERE v.empresa_sigla = '{empresa_sigla}'"
        return pd.read_sql(query, conn)

    def calcula_totais(df):
        return {
            'total_passageiros_pagos': df['passageiros_pagos'].sum(),
            'total_passageiros_gratis': df['passageiros_gratis'].sum(),
            'total_bagagem': df['bagagem_kg'].sum(),
            'total_carga_paga': df['carga_paga_kg'].sum(),
            'total_carga_gratis': df['carga_gratis_kg'].sum(),
            'total_correio': df['correio_kg'].sum(),
        }

    def carregar_empresas():
        return pd.read_sql("SELECT empresa_sigla, empresa_nome FROM empresa ORDER BY empresa_nome", conn)

    def filtrar_voos_com_50_porcento_gratis(df):
        # MELHORIA: Previne divisão por zero e o SettingWithCopyWarning
        total_passageiros = df['passageiros_pagos'] + df['passageiros_gratis']
        df_copy = df.copy()
        df_copy['percentual_gratis'] = 0.0
        df_copy.loc[total_passageiros > 0, 'percentual_gratis'] = (df_copy['passageiros_gratis'] / total_passageiros) * 100
        return df_copy[df_copy['percentual_gratis'] >= 50]

    # --- Layout da Página ---
    
    # PADRONIZAÇÃO: Header principal da página
    st.markdown("""
    <div class="section-header">
        <h1 style='margin: 0; font-size: 2.5rem;'>🚫 Análise de Voos com Alta Gratuidade</h1>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""</br>""", unsafe_allow_html=True)
    # CORREÇÃO DE BUg: Lógica de filtro segura para evitar o IndexError
    empresas_df = carregar_empresas()
    with st.container(border=True):
        opcoes_empresas = ['Todas'] + empresas_df['empresa_nome'].tolist()
        empresa_selecionada_nome = st.selectbox(
            "Selecione a empresa para análise:",
            opcoes_empresas,
            key="passageiros_empresa_select_final_3"
        )
        
    empresa_sigla_selecionada = None
    if empresa_selecionada_nome != 'Todas':
        empresa_sigla_selecionada = empresas_df[empresas_df['empresa_nome'] == empresa_selecionada_nome]['empresa_sigla'].iloc[0]

    df_carga_passageiros = consulta_carga_passageiros_por_empresa(empresa_sigla_selecionada)
    totais = calcula_totais(df_carga_passageiros)

    # PADRONIZAÇÃO: Seção de Totais com título em card
    subtitulo = f'Totais de Passageiros e Carga para: {empresa_selecionada_nome}'
    st.markdown(f"""
    <div class="title-card">
        <h3>{subtitulo}</h3>
    </div>
    """, unsafe_allow_html=True)

    # PADRONIZAÇÃO: Bloco de KPIs usando o estilo padrão do dashboard
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.markdown(f"""
        <div class="metric-card" style="color: #275cbd; text-align: center;">
            <div style="font-size: 1.70rem; font-weight: 700;">{totais['total_passageiros_pagos']:,.0f}</div>
            <div style="font-size: 1rem; opacity: 0.8;">Passageiros Pagos</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card" style="color: #275cbd; text-align: center;">
            <div style="font-size: 1.70rem; font-weight: 700;">{totais['total_passageiros_gratis']:,.0f}</div>
            <div style="font-size: 1rem; opacity: 0.8;">Passageiros Grátis</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card" style="color: #275cbd; text-align: center;">
            <div style="font-size: 1.70rem; font-weight: 700;">{totais['total_bagagem']:,.0f}</div>
            <div style="font-size: 1rem; opacity: 0.8;">Bagagem (kg)</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card" style="color: #275cbd; text-align: center;">
            <div style="font-size: 1.70rem; font-weight:  700; text-align: center">{totais['total_carga_paga']:,.0f}</div>
            <div style="font-size: 1rem; opacity: 0.8;">Carga Paga (kg)</div>
        </div>
        """, unsafe_allow_html=True)
    with col5:
        st.markdown(f"""
        <div class="metric-card" style="color: #275cbd; text-align: center;">
            <div style="font-size: 1.70rem; font-weight: 700;">{totais['total_carga_gratis']:,.0f}</div>
            <div style="font-size: 1rem; opacity: 0.8;">Carga Grátis (kg)</div>
        </div>
        """, unsafe_allow_html=True)
    with col6:
        st.markdown(f"""
        <div class="metric-card" style="color: #275cbd; text-align: center;">
            <div style="font-size: 1.70rem; font-weight: 600; text-align: center">{totais['total_correio']:,.0f}</div>
            <div style="font-size: 1rem; opacity: 0.8;">Correio (kg)</div>
        </div>
        """, unsafe_allow_html=True)


    st.markdown("<hr>", unsafe_allow_html=True)
    
    # PADRONIZAÇÃO: Seção de Gráficos com título em card
    st.markdown("""
    <div class="title-card">
        <h3>Distribuição Visual</h3>
    </div>
    """, unsafe_allow_html=True)

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        with st.container(border=True):
            st.markdown("<h4 style='text-align:center; color: #1e40af;'>Passageiros Pagos vs. Grátis</h4>", unsafe_allow_html=True)
            df_passageiros_agg = pd.DataFrame({'Tipo': ['Pagos', 'Grátis'], 'Quantidade': [totais['total_passageiros_pagos'], totais['total_passageiros_gratis']]})
            fig_passageiros = px.pie(df_passageiros_agg, values='Quantidade', names='Tipo', hole=0.4, color_discrete_sequence=['#3b82f6', "#00418c"])
            fig_passageiros.update_layout(showlegend=False, margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(fig_passageiros, use_container_width=True)

    with col_g2:
        with st.container(border=True):
            st.markdown("<h4 style='text-align:center; color: #1e40af;'>Composição da Carga (kg)</h4>", unsafe_allow_html=True)
            df_carga_agg = pd.DataFrame({'Tipo': ['Bagagem', 'Carga Paga', 'Carga Grátis', 'Correio'], 'Peso (kg)': [totais['total_bagagem'], totais['total_carga_paga'], totais['total_carga_gratis'], totais['total_correio']]})
            fig_carga = px.bar(df_carga_agg.sort_values('Peso (kg)', ascending=False), x='Tipo', y='Peso (kg)', color='Tipo', labels={'value': 'Peso (kg)', 'variable': 'Tipo de Carga'}, color_discrete_sequence=px.colors.sequential.Plasma)
            fig_carga.update_layout(showlegend=False, xaxis_title=None, margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(fig_carga, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # PADRONIZAÇÃO: Seção de Voos Improdutivos com título em card
    st.markdown("""
    <div class="title-card">
        <h3>🚨 Análise de Voos com Alta Taxa de Gratuidade (≥50%)</h3>
    </div>
    """, unsafe_allow_html=True)
    
    df_50_gratis = filtrar_voos_com_50_porcento_gratis(df_carga_passageiros)
    
    if df_50_gratis.empty:
        st.success("✅ Nenhum voo com 50% ou mais de passageiros grátis encontrado para a seleção atual.")
    else:
        st.warning(f"Encontrados: {len(df_50_gratis)} voos com 50% ou mais de passageiros grátis.")
        st.dataframe(
            df_50_gratis[['ano', 'mes', 'empresa_sigla', 'aeroporto_origem_sigla', 'aeroporto_destino_sigla', 'passageiros_pagos', 'passageiros_gratis', 'percentual_gratis']].rename(columns={
                'ano':'Ano', 'mes':'Mês', 'empresa_sigla':'Empresa', 'aeroporto_origem_sigla':'Origem', 'aeroporto_destino_sigla':'Destino',
                'passageiros_pagos':'Pagos', 'passageiros_gratis':'Grátis', 'percentual_gratis':'% Grátis'
            }).style.format({'% Grátis': '{:.1f}%'}), 
            use_container_width=True
        )

elif pagina_atual == 'Rota e Geografia':
    # Limpeza: Removendo a conexão duplicada e o st.title() inicial
    st.markdown(home_css, unsafe_allow_html=True)
    # PADRONIZAÇÃO: Título principal da página usando o section-header
    st.markdown("""
    <div class="section-header">
        <h1 style='margin: 0; font-size: 2.5rem;'>🌎 Análise Geográfica e de Rotas</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # A query e os cálculos dos KPIs permanecem os mesmos
    query = '''
    SELECT 
        vo.aeroporto_origem_sigla, ao.aeroporto_nome AS aeroporto_origem_nome,
        vo.aeroporto_destino_sigla, ad.aeroporto_nome AS aeroporto_destino_nome,
        COUNT(*) AS total_voos
    FROM voo vo
    JOIN aeroporto ao ON vo.aeroporto_origem_sigla = ao.aeroporto_sigla
    JOIN aeroporto ad ON vo.aeroporto_destino_sigla = ad.aeroporto_sigla
    GROUP BY vo.aeroporto_origem_sigla, vo.aeroporto_destino_sigla, ao.aeroporto_nome, ad.aeroporto_nome
    ORDER BY total_voos DESC
    LIMIT 200
    '''
    df = pd.read_sql_query(query, conn)

    total_voos_top_200 = df["total_voos"].sum()
    rota_mais_movimentada = df.iloc[0]
    rota_mais_sigla = f"{rota_mais_movimentada['aeroporto_origem_sigla']} → {rota_mais_movimentada['aeroporto_destino_sigla']}"
    rota_mais_nome = f"{rota_mais_movimentada['aeroporto_origem_nome']} → {rota_mais_movimentada['aeroporto_destino_nome']}"
    rota_mais_voos = rota_mais_movimentada["total_voos"]
    num_rotas = df.shape[0]

    # PADRONIZAÇÃO: Título da seção de KPIs
    st.markdown("""
    <div class="title-card">
        <h2>✈️ Destaques das Principais Rotas</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # PADRONIZAÇÃO: KPIs usando a função create_big_number_card
    col1, col2, col3 = st.columns(3)
    
    with col1:
            st.markdown(f"""
            <div class="metric-card" style="color: #275cbd; text-align: center; height: 160px; display: flex; flex-direction: column; justify-content: center; padding: 1rem: border-radius: 10px;">
                <div style="font-size: 1.70rem; font-weight: 700;">{rota_mais_sigla}</div>
                <div style="font-size: 1rem; color: #1b1c1f; opacity: 0.8; margin-top: 0.5rem;">🔥 Rota Mais Movimentada</div>
                <div style="font-size: 0.9rem; color: #64748b;">{rota_mais_voos:,} voos</div>
            </div>
            """, unsafe_allow_html=True)
    with col2:
            st.markdown(f"""
            <div class="metric-card" style="color: #275cbd; text-align: center; height: 160px; display: flex; flex-direction: column; justify-content: center; padding: 1rem; border-radius: 10px;">
                <div style="font-size: 1.70rem; font-weight: 700;">{num_rotas}</div>
                <div style="font-size: 1rem; color: #1b1c1f; opacity: 0.8; margin-top: 0.5rem;">📍 Rotas Analisadas</div>
                <div style="font-size: 0.9rem; color: #64748b;">Dentro do Top 200</div>
            </div>
            """, unsafe_allow_html=True)
    with col3:
            st.markdown(f"""
            <div class="metric-card" style="color: #275cbd; text-align: center; height: 160px; display: flex; flex-direction: column; justify-content: center; padding: 1rem; border-radius: 10px;">
                <div style="font-size: 1.70rem; font-weight: 700;">{total_voos_top_200:,}</div>
                <div style="font-size: 1rem; color: #1b1c1f; opacity: 0.8; margin-top: 0.5rem;">✈️ Total de Voos</div>
                <div style="font-size: 0.9rem; color: #64748b;">Nas rotas analisadas</div>
            </div>
            """, unsafe_allow_html=True)
        
    st.markdown("<hr>", unsafe_allow_html=True)

    # PADRONIZAÇÃO: Seção do Mapa
    st.markdown("""
    <div class="title-card">
        <h2>🗺️ Mapa Interativo de Rotas</h2>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; margin-top: -1rem; margin-bottom: 1rem;'>As cores das linhas indicam o volume de voos na rota.</p>", unsafe_allow_html=True)

    # O código do mapa folium é mantido como está.
    # OBS: O dicionário e a lista de rotas estão hardcoded. O ideal seria puxá-los do banco de dados.
    localizacoes_aeroportos = {
        "SBCT": {"nome": "Curitiba", "latitude": -25.5285, "longitude": -49.1758}, "SBKP": {"nome": "Campinas", "latitude": -23.0074, "longitude": -47.1344},
        "SBGR": {"nome": "São Paulo", "latitude": -23.4319, "longitude": -46.4679}, "SAEZ": {"nome": "Buenos Aires", "latitude": -34.8222, "longitude": -58.5358},
        "KMIA": {"nome": "Miami", "latitude": 25.7959, "longitude": -80.2870}, "SBEG": {"nome": "Manaus", "latitude": -3.0386, "longitude": -60.0497},
        "SCEL": {"nome": "Santiago", "latitude": -33.3930, "longitude": -70.7858}, "SBCF": {"nome": "Belo Horizonte", "latitude": -19.6244, "longitude": -43.9719},
        "SBRF": {"nome": "Recife", "latitude": -8.1265, "longitude": -34.9233}, "SBBR": {"nome": "Brasília", "latitude": -15.8692, "longitude": -47.9208},
        "SEQM": {"nome": "Quito", "latitude": -0.1279, "longitude": -78.3575}, "SBPA": {"nome": "Porto Alegre", "latitude": -29.9944, "longitude": -51.1714},
        "SBFL": {"nome": "Florianópolis", "latitude": -27.6702, "longitude": -48.5525}, "SBSV": {"nome": "Salvador", "latitude": -12.9086, "longitude": -38.3225},
        "SBPS": {"nome": "Porto Seguro", "latitude": -16.4386, "longitude": -39.0808}, "SUMU": {"nome": "Montevidéu", "latitude": -34.8384, "longitude": -56.0308},
        "SBBE": {"nome": "Belém", "latitude": -1.3793, "longitude": -48.4763}, "SBFN": {"nome": "Fernando de Noronha", "latitude": -3.8549, "longitude": -32.4232},
        "SBVT": {"nome": "Vitória", "latitude": -20.2581, "longitude": -40.2864}, "SGAS": {"nome": "Assunção", "latitude": -25.2396, "longitude": -57.5191},
        "SPJC": {"nome": "Lima", "latitude": -12.0219, "longitude": -77.1143}, "SBSP": {"nome": "Congonhas", "latitude": -23.6267, "longitude": -46.6564},
        "SBMQ": {"nome": "Macapá", "latitude": 0.0506, "longitude": -51.0722}, "KJFK": {"nome": "Nova York - JFK", "latitude": 40.6413, "longitude": -73.7781},
        "SBMO": {"nome": "Maceió - Zumbi dos Palmares", "latitude": -9.5106, "longitude": -35.7917}, "SBCY": {"nome": "Cuiabá", "latitude": -15.6529, "longitude": -56.1167},
        "SBJP": {"nome": "João Pessoa", "latitude": -7.1458, "longitude": -34.9509}, "SBRP": {"nome": "Ribeirão Preto", "latitude": -21.1364, "longitude": -47.7767},
        "SGES": {"nome": "Encarnación", "latitude": -27.2272, "longitude": -55.8375}, "SBGO": {"nome": "Goiânia", "latitude": -16.6319, "longitude": -49.2262},
        "DNMM": {"nome": "Lagos, Nigéria", "latitude": 6.5774, "longitude": 3.3219}, "EDDF": {"nome": "Frankfurt", "latitude": 50.0333, "longitude": 8.5706},
        "LPPT": {"nome": "Lisboa", "latitude": 38.7813, "longitude": -9.1359}
    }
    rotas_voo = df[['aeroporto_origem_sigla', 'aeroporto_destino_sigla', 'total_voos']].values.tolist()

    def definir_cor_voo(num_voos):
        if num_voos <= 10: return "blue"
        elif num_voos <= 20: return "green"
        elif num_voos <= 30: return "orange"
        elif num_voos <= 40: return "purple"
        else: return "red"

    m = folium.Map(location=[-15.7801, -47.9292], zoom_start=4, tiles='CartoDB positron')
    
    for codigo, dados in localizacoes_aeroportos.items():
        if 'latitude' in dados and 'longitude' in dados: # Checagem de segurança
            folium.Marker(location=[dados["latitude"], dados["longitude"]], popup=f"{dados['nome']} ({codigo})", tooltip=codigo, icon=folium.Icon(color="darkblue", icon_color="white", icon="plane", prefix="fa")).add_to(m)
    
    for origem, destino, num_voos in rotas_voo:
        if origem in localizacoes_aeroportos and destino in localizacoes_aeroportos:
            origem_coords = [localizacoes_aeroportos[origem]["latitude"], localizacoes_aeroportos[origem]["longitude"]]
            destino_coords = [localizacoes_aeroportos[destino]["latitude"], localizacoes_aeroportos[destino]["longitude"]]
            folium.PolyLine([origem_coords, destino_coords], color=definir_cor_voo(num_voos), weight=2, opacity=0.8, tooltip=f"{origem} → {destino}: {num_voos} voos").add_to(m)
    
    with st.container(border=True):
        st_folium(m, width='100%', height=500, returned_objects=[])

    # A legenda foi mantida, mas poderia ser mais integrada ao layout.
    st.markdown("""
    <div style="position: relative; bottom: 80px; left: 20px; z-index: 1000; background-color: white; padding: 10px; border-radius: 5px; border: 1px solid #ccc; width: 200px;">
        <strong>Legenda (Nº de Voos)</strong><br>
        <span style="background-color:red; display:inline-block; width:12px; height:12px; margin-right:5px;"></span> 41+<br>
        <span style="background-color:purple; display:inline-block; width:12px; height:12px; margin-right:5px;"></span> 31-40<br>
        <span style="background-color:orange; display:inline-block; width:12px; height:12px; margin-right:5px;"></span> 21-30<br>
        <span style="background-color:green; display:inline-block; width:12px; height:12px; margin-right:5px;"></span> 11-20<br>
        <span style="background-color:blue; display:inline-block; width:12px; height:12px; margin-right:5px;"></span> 0-10
    </div>
    """, unsafe_allow_html=True)

    # PADRONIZAÇÃO: Seção do Gráfico de Barras
    st.markdown("""
    <div class="title-card">
        <h3>📉 Gráfico de Rotas por Total de Voos</h3>
    </div>
    """, unsafe_allow_html=True)

    with st.container(border=True):

        # A query não precisa ser executada de novo
        df['rota_nome'] = df['aeroporto_origem_nome'] + " → " + df['aeroporto_destino_nome']
        df_sorted = df.sort_values("total_voos", ascending=True)

        fig_bar = px.bar(
            df_sorted.tail(30),  # Mostrando as 30 rotas mais movimentadas
            x="total_voos",
            y="rota_nome",
            orientation="h",
            labels={"total_voos": "Total de Voos", "rota_nome": "Rota"},
            height=800,
            text="total_voos"  # <-- PASSO 1: Adiciona os valores da coluna 'total_voos' como texto
        )

        # PASSO 2: Atualiza a aparência e posição do texto
        fig_bar.update_traces(
            texttemplate='%{text:,}',
            textposition='inside',
            insidetextanchor='middle',
            constraintext='none',  # <-- A MUDANÇA PRINCIPAL
            textfont=dict(
                size=14,
                color='white'
            ),

            textangle=360
        )

        # Ajustes finais de layout
        fig_bar.update_layout(
            title_text='',              # Remove o título do gráfico
            yaxis=dict(
                tickfont=dict(size=10)  # Deixa o nome das rotas um pouco menor
            ),
            margin=dict(l=10, r=20, t=30, b=20)
        )

        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # PADRONIZAÇÃO: Seção do Gráfico Sankey
    st.markdown("""
    <div class="title-card">
        <h3>🔁 Fluxo de Voos entre Regiões</h3>
    </div>
    """, unsafe_allow_html=True)
    
    with st.container(border=True):
        region_query = '''
        SELECT 
            ao.aeroporto_regiao AS regiao_origem,
            ad.aeroporto_regiao AS regiao_destino,
            COUNT(*) AS total_voos
        FROM voo vo
        JOIN aeroporto ao ON vo.aeroporto_origem_sigla = ao.aeroporto_sigla
        JOIN aeroporto ad ON vo.aeroporto_destino_sigla = ad.aeroporto_sigla
        WHERE ao.aeroporto_regiao IS NOT NULL AND ad.aeroporto_regiao IS NOT NULL
        GROUP BY regiao_origem, regiao_destino
        ORDER BY total_voos DESC
        '''
        df_regioes = pd.read_sql_query(region_query, conn)

        nodes = list(set(df_regioes['regiao_origem']).union(set(df_regioes['regiao_destino'])))
        node_dict = {name: i for i, name in enumerate(nodes)}
        
        source = df_regioes['regiao_origem'].map(node_dict)
        target = df_regioes['regiao_destino'].map(node_dict)
        value = df_regioes['total_voos']

        fig_sankey = go.Figure(data=[go.Sankey(
            node=dict(
                pad=20,
                thickness=25,
                label=nodes,
                color="#3b82f6"  # Cor dos nós (barras)
                # 'labelfont' foi removido daqui, pois era o local incorreto
            ),
            link=dict(
                source=source,
                target=target,
                value=value,
                color='rgba(200, 200, 200, 0.6)'
            ),

            # --- CORREÇÃO APLICADA AQUI ---
            # O estilo da fonte é um argumento do próprio go.Sankey
            textfont=dict(
                color="#1e40af",  # A cor azul escura que você queria
                size=16
            )
        )])

        # O update_layout continua o mesmo
        fig_sankey.update_layout(
            title_text='',
            title_x=0.5, 
            font_size=14, # Este é um tamanho de fonte geral, o textfont acima é mais específico
            height=600,
            margin=dict(
                l=20,  # Margem esquerda
                r=20,  # Margem direita
                b=20,  # Margem inferior
                t=30   # Margem superior (deixe um pouco de espaço para não ficar colado)
            )
        )
    
        st.plotly_chart(fig_sankey, use_container_width=True)

        st.markdown("""
        <div style="border: 1px solid #e2e8f0; border-radius: 0.5rem; padding: 1rem; margin-top: 1rem; margin-bottom: 1rem">
            <strong>ℹ️ Legenda do Gráfico Sankey:</strong>
            <ul>
                <li><strong>Cada bloco (nó)</strong> representa uma <strong>região</strong>.</li>
                <li><strong>As faixas</strong> mostram o fluxo de voos <strong>de uma região para outra</strong>.</li>
                <li>A <strong>espessura da faixa</strong> é proporcional à <strong>quantidade de voos</strong> na rota.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)


elif pagina_atual == 'KPIs Gerenciais':
    st.markdown(home_css, unsafe_allow_html=True)
    # PADRONIZAÇÃO: Título principal da página usando o section-header

    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"] {
            background-color: #fffff;
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
    
    # Header principal
    st.markdown("""
    <div class="section-header">
        <h1 style='margin: 0; font-size: 2.5rem;'>📊 KPIs e Métricas Gerenciais</h1>
        <p>Análise detalhada das métricas de performance das operações de voo</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Filtros principais
    with st.container(border=True):
        st.markdown("""<div><h3 style='color: #1e40af;'>🔍 Filtros</h3></div>""", unsafe_allow_html=True)
        with st.container(border=True):
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
        st.markdown("""<div class="title-card">
                    <h3>📈 Indicadores Principais</h3>
                    </div>
        """, unsafe_allow_html=True)
   
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card" style="color: #275cbd; text-align: center; height: 160px; display: flex; flex-direction: column; justify-content: center; padding: 1rem; border-radius: 10px;">
                <div style="font-size: 1.70rem; font-weight: 700;">{taxa_ocupacao_media:,.1f}%</div>
                <div style="font-size: 1rem; color: #1b1c1f; opacity: 0.8; margin-top: 0.5rem;">Taxa Média de Ocupação</div>
                <div style="font-size: 0.9rem; opacity: 0.5; color: #64748b;">RPK / ASK</div>
            </div>
            """, unsafe_allow_html=True)
    
        with col2:

             st.markdown(f"""
            <div class="metric-card" style="color: #275cbd; text-align: center; height: 160px; display: flex; flex-direction: column; justify-content: center; padding: 1rem; border-radius: 10px;">
                <div style="font-size: 1.70rem; font-weight: 700;">{payload_medio_geral:,.0f} kg</div>
                <div style="font-size: 1rem; color: #1b1c1f; opacity: 0.8; margin-top: 0.5rem;">Payload Médio por Voo</div>
                <div style="font-size: 0.9rem; opacity: 0.5; color: #64748b;">Peso transportado por voo</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:

             st.markdown(f"""
            <div class="metric-card" style="color: #275cbd; text-align: center; height: 160px; display: flex; flex-direction: column; justify-content: center; padding: 1rem; border-radius: 10px;">
                <div style="font-size: 1.70rem; font-weight: 700;">{passageiros_km_medio:.1f}%</div>
                <div style="font-size: 1rem; color: #1b1c1f; opacity: 0.8; margin-top: 0.5rem;">Passageiros por 100km</div>
                <div style="font-size: 0.9rem; opacity: 0.5; color: #64748b;">Densidade de passageiros</div>
            </div>
            """, unsafe_allow_html=True)
        # Gráficos dos KPIs
        st.markdown("---")
        st.markdown("""
        <style>
            /* Tab ativa */
            .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
                color: #0066cc !important;
                border-bottom-color: #0066cc !important;
            }
            
            /* Tab ativa - texto */
            .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] p {
                color: #0066cc !important;
            }
            
            /* Linha indicadora da tab ativa */
            .stTabs [data-baseweb="tab-highlight"] {
                background-color: #0066cc !important;
            }
            
            /* Alternativa mais específica */
            div[data-testid="stTabs"] > div[data-baseweb="tab-list"] button[aria-selected="true"] {
                color: #0066cc !important;
            }
        </style>
        """, unsafe_allow_html=True)

        st.markdown("""<div class="title-card">
                    <h3>📊 Análises Visuais</h3>
                    </div>
        """, unsafe_allow_html=True)

        tab1, tab2, tab3 = st.tabs(["📈 Por Empresa", "📅 Evolução Temporal", "🛣️ Por Rota"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                with st.container(border=True):
                    st.markdown("""<div class="title-header">
                        <p>Taxa de Ocupação por Empresa</p>
                        </div>
                    """, unsafe_allow_html=True)

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
                        title='',
                        color='taxa_ocupacao',
                        color_continuous_scale='BuPu',  # Azul para roxo
                        labels={'taxa_ocupacao': 'Taxa de Ocupação (%)', 'empresa_sigla': 'Empresa'}
                    )
                    fig_ocupacao.update_layout(height=400, showlegend=False)
                    st.plotly_chart(fig_ocupacao, use_container_width=True)
            
            with col2:
                with st.container(border=True):
                    st.markdown("""<div class="title-header">
                        <p>Payload Médio por Empresa</p>
                        </div>
                    """, unsafe_allow_html=True)
                    payload_empresa = df_kpis.groupby(['empresa_sigla', 'empresa_nome']).agg({
                        'payload_medio_por_voo': 'mean'
                    }).reset_index()
                    payload_empresa = payload_empresa.sort_values('payload_medio_por_voo', ascending=True)
                    
                    fig_payload = px.bar(
                        payload_empresa,
                        x='payload_medio_por_voo',
                        y='empresa_sigla',
                        orientation='h',
                        title='',
                        color='payload_medio_por_voo',
                        color_continuous_scale='PuBu',
                        labels={'payload_medio_por_voo': 'Payload Médio (kg)', 'empresa_sigla': 'Empresa'}
                    )
                    fig_payload.update_layout(height=400, showlegend=False)
                    st.plotly_chart(fig_payload, use_container_width=True)
            
           
            # Gráfico de capacidade vs utilização
            st.markdown("""<div class="title-card">
                        <h4>Assentos Disponíveis vs Passageiros Reais</h4>
                        </div>
                    """, unsafe_allow_html=True)
            with st.container(border=True):
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
                    title='',
                    barmode='group',
                    height=400,
                    xaxis_title='Empresa',
                    yaxis_title='Quantidade'
                )
                st.plotly_chart(fig_capacidade, use_container_width=True)
        
        with tab2:
            st.markdown("""<div class="title-card">
                        <h4>Evolução da Taxa de Ocupação ao Longo do Tempo</h4>
                        </div>
                    """, unsafe_allow_html=True)
            
            
            evolucao_temporal = df_kpis.groupby(['ano', 'mes']).agg({
                'ASK_estimado': 'sum',
                'RPK_real': 'sum',
                'payload_medio_por_voo': 'mean'
            }).reset_index()
            evolucao_temporal['taxa_ocupacao'] = (evolucao_temporal['RPK_real'] / evolucao_temporal['ASK_estimado']) * 100
            evolucao_temporal['periodo'] = evolucao_temporal['ano'].astype(str) + '-' + evolucao_temporal['mes'].astype(str).str.zfill(2)
            
            col1, col2 = st.columns(2)
            
            with col1:
                with st.container(border=True):
                    st.markdown("""<div class="title-header">
                        <p>Taxa de Ocupação Mensal (%)</p>
                        </div>
                    """, unsafe_allow_html=True)
                    fig_evolucao = px.line(
                        evolucao_temporal,
                        x='periodo',
                        y='taxa_ocupacao',
                        title='',
                        markers=True,
                        line_shape='spline'
                    )
                    fig_evolucao.update_layout(height=400)
                    fig_evolucao.update_xaxes(title='Período')
                    fig_evolucao.update_yaxes(title='Taxa de Ocupação (%)')
                    st.plotly_chart(fig_evolucao, use_container_width=True)
            
            with col2:
                with st.container(border=True):
                    st.markdown("""<div class="title-header">
                        <p>Payload Médio por Voo Mensal (kg)</p>
                        </div>
                    """, unsafe_allow_html=True)   
                    fig_payload_tempo = px.line(
                        evolucao_temporal,
                        x='periodo',
                        y='payload_medio_por_voo',
                        title='',
                        markers=True,
                        line_shape='spline',
                        color_discrete_sequence=['#1f77b4']
                    )
                    fig_payload_tempo.update_layout(height=400)
                    fig_payload_tempo.update_xaxes(title='Período')
                    fig_payload_tempo.update_yaxes(title='Payload Médio (kg)')
                    st.plotly_chart(fig_payload_tempo, use_container_width=True)
        
        with tab3:
            st.markdown("""<div class="title-card">
                        <h4>Análise por Rota</h4>
                        </div>
                    """, unsafe_allow_html=True)
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
                with st.container(border=True):
                    st.markdown("""<div class="title-header">
                        <p>Top 15 Rotas por Volume de Passageiros</p>
                        </div>
                    """, unsafe_allow_html=True)
                    fig_rotas_pass = px.bar(
                        rotas_analise,
                        x='total_passageiros',
                        y='rota',
                        orientation='h',
                        title='',
                        color='taxa_ocupacao_pct',
                        color_continuous_scale=['#1f77b4', '#6a0dad'],
                        labels={'total_passageiros': 'Total Passageiros', 'rota': 'Rota'}
                    )
                    fig_rotas_pass.update_layout(height=500)
                    fig_rotas_pass.update_yaxes(categoryorder="total ascending")
                    st.plotly_chart(fig_rotas_pass, use_container_width=True)
            
            with col2:
                with st.container(border=True):
                    st.markdown("""<div class="title-header">
                        <p>Taxa de Ocupação vs Payload por Rota</p>
                        </div>
                    """, unsafe_allow_html=True)
                    fig_scatter_rotas = px.scatter(
                        rotas_analise,
                        x='taxa_ocupacao_pct',
                        y='payload_medio_por_voo',
                        size='total_passageiros',
                        hover_data=['rota', 'total_voos'],
                        title='',
                        labels={
                            'taxa_ocupacao_pct': 'Taxa de Ocupação (%)',
                            'payload_medio_por_voo': 'Payload Médio (kg)'
                        }
                    )
                    fig_scatter_rotas.update_layout(height=500)
                    st.plotly_chart(fig_scatter_rotas, use_container_width=True)
            
        # Tabela de dados detalhados    
        st.markdown("### 📋 Dados Detalhados")
        
        # Seletor de colunas para exibir
        colunas_disponiveis = [
            'empresa_sigla', 'empresa_nome', 'ano', 'mes', 'natureza',
            'taxa_ocupacao_pct', 'payload_medio_por_voo', 'passageiros_por_km',
            'total_passageiros', 'distancia_voada_km', 'decolagens'
        ]
        st.markdown("""
        <style>
            /* Seletor mais específico para tags do multiselect */
            div[data-testid="stMultiSelect"] div[data-baseweb="tag"] {
                background-color: #0066cc !important;
                color: white !important;
                border-color: #0066cc !important;
            }
            
            /* Texto dentro das tags */
            div[data-testid="stMultiSelect"] div[data-baseweb="tag"] span {
                color: white !important;
            }
            
            /* Botão X para remover */
            div[data-testid="stMultiSelect"] div[data-baseweb="tag"] button {
                color: white !important;
            }
            
            /* Hover no botão X */
            div[data-testid="stMultiSelect"] div[data-baseweb="tag"] button:hover {
                background-color: rgba(255, 255, 255, 0.2) !important;
            }
            
            /* Alternativa com seletor mais amplo */
            .stMultiSelect [data-baseweb="tag"] {
                background-color: #0066cc !important;
                color: white !important;
            }
            
            /* Outra alternativa */
            span[data-baseweb="tag"] {
                background-color: #0066cc !important;
                color: white !important;
            }
        </style>
        """, unsafe_allow_html=True)

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

elif pagina_atual == 'Aeroportos':
    st.markdown(home_css, unsafe_allow_html=True)
    # --- Funções da Página (mantidas como no original) ---
    def get_empresas(conn):
        query = '''
            SELECT DISTINCT e.empresa_nome FROM empresa e
            JOIN voo v ON v.empresa_sigla = e.empresa_sigla
            ORDER BY e.empresa_nome
        '''
        return pd.read_sql_query(query, conn)['empresa_nome'].tolist()

    def get_destaques(conn):
        query = '''
            WITH movimentacao_total AS (
                SELECT sigla, aeroporto_nome, SUM(total_voos) AS total FROM (
                    SELECT vo.aeroporto_origem_sigla AS sigla, ap.aeroporto_nome, COUNT(*) AS total_voos FROM voo vo JOIN aeroporto ap ON vo.aeroporto_origem_sigla = ap.aeroporto_sigla GROUP BY 1, 2
                    UNION ALL
                    SELECT vo.aeroporto_destino_sigla AS sigla, ap.aeroporto_nome, COUNT(*) AS total_voos FROM voo vo JOIN aeroporto ap ON vo.aeroporto_destino_sigla = ap.aeroporto_sigla GROUP BY 1, 2
                ) GROUP BY 1, 2 ORDER BY total DESC LIMIT 1
            ),
            rotas_unicas AS (
                SELECT COUNT(*) AS total FROM (SELECT DISTINCT aeroporto_origem_sigla, aeroporto_destino_sigla FROM voo)
            )
            SELECT
                (SELECT COUNT(DISTINCT sigla) FROM (SELECT aeroporto_origem_sigla AS sigla FROM voo UNION SELECT aeroporto_destino_sigla FROM voo)) AS total_aeroportos,
                (SELECT aeroporto_nome FROM movimentacao_total) AS aeroporto_top,
                (SELECT total FROM movimentacao_total) AS total_movimentado,
                (SELECT total FROM rotas_unicas) AS total_rotas
        '''
        return pd.read_sql_query(query, conn)

    def get_rotas_por_empresa(conn, empresa_nome):
        query = '''
            SELECT 
                e.empresa_nome, vo.aeroporto_origem_sigla, ao.aeroporto_nome AS aeroporto_origem_nome,
                vo.aeroporto_destino_sigla, ad.aeroporto_nome AS aeroporto_destino_nome,
                COUNT(*) AS total_voos
            FROM voo vo
            JOIN empresa e ON vo.empresa_sigla = e.empresa_sigla
            JOIN aeroporto ao ON vo.aeroporto_origem_sigla = ao.aeroporto_sigla
            JOIN aeroporto ad ON vo.aeroporto_destino_sigla = ad.aeroporto_sigla
            WHERE e.empresa_nome = ?
            GROUP BY 1, 2, 3, 4, 5 ORDER BY total_voos DESC LIMIT 200
        '''
        return pd.read_sql_query(query, conn, params=(empresa_nome,))

    # --- Layout da Página ---

    st.markdown("""
    <div class="section-header">
        <h1 style='margin: 0; font-size: 2.5rem;'>✈️ Análise de Aeroportos</h1>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="title-card">
        <h3>📍 Destaques Gerais</h3>
    </div>
    """, unsafe_allow_html=True)

    destaques = get_destaques(conn)
    
    # <<< BLOCO DE KPIs GERAIS ATUALIZADO PARA ESTILO MANUAL >>>
    if not destaques.empty:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-card" style="color: #275cbd; text-align: center">
                <div style="font-weight: 600; font-size: 1.2rem;">🛫 Total de Aeroportos</div>
                <div style="font-size: 2.5rem; font-weight: 700;">{destaques['total_aeroportos'].iloc[0]}</div>
                <div style="font-size: 0.9rem; opacity: 0.8;">aeroportos</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card" style="color: #275cbd; text-align: center">
                <div style="font-weight: 600; font-size: 1.2rem;">🌐 Aeroporto + Movimentado</div>
                <div style="font-size: 2.4rem; font-weight: 700;">{destaques['aeroporto_top'].iloc[0]}</div>
                <div style="font-size: 1rem; opacity: 0.8;">{destaques['total_movimentado'].iloc[0]:,} voos</div>
                
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-card" style="color: #275cbd; text-align: center">
                <div style="font-weight: 600; font-size: 1.2rem;">✈️ Total de Rotas Únicas</div>
                <div style="font-size: 2.5rem; font-weight: 700;">{destaques['total_rotas'].iloc[0]:,}</div>
                <div style="font-size: 0.9rem; opacity: 0.8;">rotas</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("Não foi possível carregar os dados de destaque.")

    st.markdown("""
    <div class="title-card">
        <h3>🏢 Análise por Empresa Aérea</h3>
    </div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        empresas = get_empresas(conn)
        empresa_selecionada = st.selectbox("Selecione uma empresa aérea:", empresas, key="aeroportos_empresa_select_2")

        top3_query = '''
            WITH uso_aeroportos AS (
                SELECT aeroporto_origem_sigla AS sigla, COUNT(*) AS total FROM voo v JOIN empresa e ON v.empresa_sigla = e.empresa_sigla WHERE e.empresa_nome = ? GROUP BY 1
                UNION ALL
                SELECT aeroporto_destino_sigla AS sigla, COUNT(*) AS total FROM voo v JOIN empresa e ON v.empresa_sigla = e.empresa_sigla WHERE e.empresa_nome = ? GROUP BY 1
            )
            SELECT a.aeroporto_nome, SUM(u.total) AS total_uso
            FROM uso_aeroportos u JOIN aeroporto a ON u.sigla = a.aeroporto_sigla
            GROUP BY a.aeroporto_nome ORDER BY total_uso DESC LIMIT 3
        '''
        top3_df = pd.read_sql_query(top3_query, conn, params=(empresa_selecionada, empresa_selecionada))

        st.markdown("<h4 style='text-align: center; color: #1e40af;'>🏆 Top 3 Aeroportos Mais Utilizados</h4>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        
        # <<< BLOCO TOP 3 ATUALIZADO PARA ESTILO MANUAL E COM LÓGICA ANTI-ERRO >>>
        # Card 1: 1º Lugar
        with col1:
            if len(top3_df) >= 1:
                st.markdown(f"""
                <div class="metric-card" style="color: #275cbd; text-align: center">
                    <div style="font-weight: 600; font-size: 1.1rem;">🥇 1º - {top3_df.iloc[0]['aeroporto_nome']}</div>
                    <div style="font-size: 1.8rem; font-weight: 700;">{top3_df.iloc[0]['total_uso']:,}</div>
                    <div style="font-size: 0.9rem; opacity: 0.8;">voos</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""<div class="metric-card" style="color: #275cbd; text-align: center; border-radius: 10px; border: 1px solid #e2e8f0; padding: 10px; height: 120px; display: flex; flex-direction: column; justify-content: center;"><div style="font-weight: 600; font-size: 1.1rem;">🥇 1º Lugar</div><div style="font-size: 1.8rem; font-weight: 700;">N/D</div></div>""", unsafe_allow_html=True)

        # Card 2: 2º Lugar
        with col2:
            if len(top3_df) >= 2:
                st.markdown(f"""
                <div class="metric-card" style="color: #275cbd; text-align: center">
                    <div style="font-weight: 600; font-size: 1.1rem;">🥈 2º - {top3_df.iloc[1]['aeroporto_nome']}</div>
                    <div style="font-size: 1.8rem; font-weight: 700;">{top3_df.iloc[1]['total_uso']:,}</div>
                    <div style="font-size: 0.9rem; opacity: 0.8;">voos</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""<div class="metric-card" style="color: #275cbd; text-align: center; border-radius: 10px; border: 1px solid #e2e8f0; padding: 10px; height: 120px; display: flex; flex-direction: column; justify-content: center;"><div style="font-weight: 600; font-size: 1.1rem;">🥈 2º Lugar</div><div style="font-size: 1.8rem; font-weight: 700;">N/D</div></div>""", unsafe_allow_html=True)

        # Card 3: 3º Lugar
        with col3:
            if len(top3_df) >= 3:
                st.markdown(f"""
                <div class="metric-card" style="color: #275cbd; text-align: center">
                    <div style="font-weight: 600; font-size: 1.1rem;">🥉 3º - {top3_df.iloc[2]['aeroporto_nome']}</div>
                    <div style="font-size: 1.8rem; font-weight: 700;">{top3_df.iloc[2]['total_uso']:,}</div>
                    <div style="font-size: 0.9rem; opacity: 0.8;">voos</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""<div class="metric-card" style="color: #275cbd; text-align: center; border-radius: 10px; border: 1px solid #e2e8f0; padding: 10px; height: 120px; display: flex; flex-direction: column; justify-content: center;"><div style="font-weight: 600; font-size: 1.1rem;">🥉 3º Lugar</div><div style="font-size: 1.8rem; font-weight: 700;">N/D</div></div>""", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        df_rotas = get_rotas_por_empresa(conn, empresa_selecionada)
        st.markdown(f"<h4 style='text-align: center; color: #1e40af;'>📍 Rotas mais frequentes da {empresa_selecionada}</h4>", unsafe_allow_html=True)
        st.dataframe(df_rotas, use_container_width=True)

    
    st.markdown("""
    <div class="title-card">
        <h3>🗺️ Mapa de Rotas por Cidade (para a empresa selecionada)</h3>
    </div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        query_cidades = '''
            SELECT 
                ao.aeroporto_nome AS cidade_origem, ad.aeroporto_nome AS cidade_destino,
                COUNT(*) AS total_voos
            FROM voo vo
            JOIN empresa e ON vo.empresa_sigla = e.empresa_sigla
            JOIN aeroporto ao ON vo.aeroporto_origem_sigla = ao.aeroporto_sigla
            JOIN aeroporto ad ON vo.aeroporto_destino_sigla = ad.aeroporto_sigla
            WHERE e.empresa_nome = ?
            GROUP BY cidade_origem, cidade_destino ORDER BY total_voos DESC
        '''
        df_mapa = pd.read_sql_query(query_cidades, conn, params=(empresa_selecionada,))

        # Geocodificação com cache
        @st.cache_data
        def geocode_city(city):
            geolocator = Nominatim(user_agent="geo_app_aeroportos_final") # User agent único
            try:
                location = geolocator.geocode(city, timeout=10)
                if location: return location.latitude, location.longitude
            except Exception as e:
                # Opcional: logar o erro
                # print(f"Erro de geocoding para {city}: {e}")
                return None, None
            return None, None

        # Obter coordenadas
        df_mapa[['lat_origem', 'lon_origem']] = df_mapa['cidade_origem'].apply(lambda x: pd.Series(geocode_city(x)))
        df_mapa[['lat_destino', 'lon_destino']] = df_mapa['cidade_destino'].apply(lambda x: pd.Series(geocode_city(x)))
        df_mapa = df_mapa.dropna(subset=['lat_origem', 'lon_origem', 'lat_destino', 'lon_destino'])

        if not df_mapa.empty:
            layer = pdk.Layer(
                "ArcLayer", 
                data=df_mapa, 
                get_source_position=["lon_origem", "lat_origem"],
                get_target_position=["lon_destino", "lat_destino"],
                get_width='total_voos',
                get_tilt=15, 
                get_source_color=[0, 104, 201, 160], # Azul
                get_target_color=[70, 20, 220, 160], # Roxo
                auto_highlight=True, 
                pickable=True,
                width_scale=0.8, # Deixa as linhas um pouco mais finas
            )
            view_state = pdk.ViewState(latitude=-14, longitude=-52, zoom=3.5, pitch=30)
            r = pdk.Deck(layers=[layer], initial_view_state=view_state, map_style='mapbox://styles/mapbox/light-v10', tooltip={"html": "<b>{total_voos} voos</b><br/>De: {cidade_origem}<br/>Para: {cidade_destino}"})
            st.pydeck_chart(r)
        else:
            st.info("Não há dados de rota suficientes para gerar o mapa para a empresa selecionada.")
    


conn.close()
