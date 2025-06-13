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
        border: 1px solid #e2e8f0;
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
        border: 0.5px solid #e2e8f0;
        border-left: 8px solid #6648E6; /* Borda padrão, será sobrescrita pela cor específica */
        align: center;
    }
    
    .metric-card h3 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: bold;
        color: #6648E6;
        align: center;
    }
    
    .metric-card p {
        margin: 0.5rem 0 0 0;
        font-size: 1rem;
        opacity: 0.9;
        color: #6648E6;
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
    border: 1px solid #e2e8f0;
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
    color: #1e40af;
    font-size: 1.2rem;
    font-weight: bold;
    margin-bottom: 1rem;
}

.card-rank {
    color: #1e40af;
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
    color: #64748b;
    margin: 0.25rem 0;
}

.card-metric-value {
    font-size: 1.75rem;
    font-weight: 600;
    color: #1f2937;
    margin: 0;
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

# --- FIM DO BLOCO CORRETIVO ---

# Função para criar big numbers
def create_big_number_card(title, value, subtitle=""):
    st.markdown(f"""
    <div class="metric-card">
        <h3>{value}</h3>
        <p>{title}</p>
        {f'<small style="opacity: 0.95; color: white;">{subtitle}</small>' if subtitle else ''}
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
   
    # Estilo personalizado da página 'home'
    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"] {
            background-color: #f9fafb;
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
    st.markdown("""<hr style="border: none; margin: 20px auto;">""",unsafe_allow_html=True)
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
    col1, col2 = st.columns(2)
    col1, col2 = st.columns(2)

    # Card de Voos Nacionais
    with col1:
        # Adicionada uma checagem para evitar erro se não houver dados
        if not df_nacional.empty and pd.notna(df_nacional['total_voos'].iloc[0]):
            # Prepara as variáveis
            voos = f"{(df_nacional['total_voos'].iloc[0]):,}"
            passageiros = f"{(df_nacional['total_passageiros_pagos'].iloc[0]):,}"
            distancia = f"{df_nacional['total_distancia_km'].iloc[0]:,.0f}"

            # --- NOVO HTML PARA O CARD ---
            html_card_nacional = f"""
            <div class="custom-card">
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
            # Mostra um card de aviso se não houver dados
            st.markdown("<div class='custom-card'><h3 class='card-title'>🇧🇷 Voos Nacionais</h3><p>Dados não disponíveis.</p></div>", unsafe_allow_html=True)

    # Card de Voos Internacionais
    with col2:
        if not df_internacional.empty and pd.notna(df_internacional['total_voos'].iloc[0]):
            # Prepara as variáveis
            voos_int = f"{int(df_internacional['total_voos'].iloc[0]):,}"
            passageiros_int = f"{int(df_internacional['total_passageiros_pagos'].iloc[0]):,}"
            distancia_int = f"{int(df_internacional['total_distancia_km'].iloc[0]):,.0f}"

            html_card_internacional = f"""
            <div class="custom-card">
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
            # Mostra um card de aviso se não houver dados
            st.markdown("<div class='custom-card'><h3 class='card-title'>🌐 Voos Internacionais</h3><p>Dados não disponíveis.</p></div>", unsafe_allow_html=True)
           
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
        <div style='background-color: white; padding: 1.5rem; border-radius: 0.75rem; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); margin: 1rem 0;  border: 0.5px solid #e2e8f0;'>
            <h4 style='color: #1e40af; text-align: center; font-size: 1.2rem;'>🏢 Top 10 Empresas por Voos</h4>
        """, unsafe_allow_html=True)
        st.markdown("""<br>""",unsafe_allow_html=True)
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
        <div style='background-color: white; padding: 1.5rem; border-radius: 0.75rem; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); margin: 1rem 0; border: 0.5px solid #e2e8f0;'>
            <h4 style='color: #1e40af; text-align: center; font-size: 1.2rem;'>👥 Passageiros por Empresa</h4>
        """, unsafe_allow_html=True)
        st.markdown("""<br>""",unsafe_allow_html=True)
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
    st.markdown("""<br>""",unsafe_allow_html=True)
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
       
        # A query continua a mesma, buscando os dados detalhados
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

        # --- NOVA LÓGICA DE AGREGAÇÃO CONDICIONAL ---
       
        df_para_exibir = pd.DataFrame() # Cria um DataFrame vazio para começar

        if tipo_voo_selecionado_dist == 'Todas':
            # Se o filtro for "Todas", agrupamos os dados por empresa para somar os valores
            df_agregado = df_distancia_empresa.groupby(['empresa_sigla', 'empresa_nome']).agg(
                distancia_total=('distancia_total', 'sum'),
                total_voos=('total_voos', 'sum')
            ).reset_index()
            # Adiciona uma coluna 'natureza' para indicar que é o total
            df_agregado['natureza'] = 'Total (Nac + Int)'
            # Ordena pelo novo total de distância
            df_para_exibir = df_agregado.sort_values(by='distancia_total', ascending=False)
        else:
            # Se um tipo de voo específico foi selecionado, usamos o DataFrame como está
            df_para_exibir = df_distancia_empresa

        # O restante do código agora usa 'df_para_exibir', que tem os dados corretos
        if not df_para_exibir.empty:
            st.markdown("#### 🏆 Top 5 Empresas por Distância")
            top_empresas = df_para_exibir.head(5)
           
            num_resultados = len(top_empresas)
            cols = st.columns(num_resultados) if num_resultados > 0 else []

            for i, (_, row) in enumerate(top_empresas.iterrows()):
                with cols[i]:
                    # Ajuste na lógica do pill para incluir a nova categoria 'Total'
                    if row['natureza'] == 'DOMÉSTICA':
                        pill_style = "background-color: #275CBD; color: white;"
                    elif row['natureza'] == 'INTERNACIONAL':
                        pill_style = "background-color: #6E45DF; color: white;"
                    else: # Estilo para a categoria 'Total (Nac + Int)'
                        pill_style = "background-color: #1a2233; color: white;"

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

            # Gráfico de barras também usará os dados corretos
            st.markdown("<br>", unsafe_allow_html=True)
            top_15_empresas = df_para_exibir.head(15)
           
            fig_dist_empresa = px.bar(
                top_15_empresas, x='distancia_total', y='empresa_sigla',
                orientation='h', color='natureza',
                title='<b>Top 15 Empresas por Distância Total Voada</b>',
                # ... resto dos parâmetros do gráfico ...
                color_discrete_map={
                    'DOMÉSTICA': "#275CBD",
                    'INTERNACIONAL': "#6E45DF",
                    'Total (Nac + Int)': "#1a2233"
                }
            )
            fig_dist_empresa.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_dist_empresa, use_container_width=True)

            # A tabela de resumo também usará os dados corretos
            st.markdown("#### 📋 Resumo por Empresa")
            st.dataframe(df_para_exibir, use_container_width=True)
        else:
            st.warning("⚠️ Nenhum dado encontrado para os filtros selecionados.")
   
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
                    if row['natureza'] == 'DOMÉSTICA':
                        pill_style = "background-color: #275CBD; color: white;"
                    else:
                        pill_style = "background-color: #6E45DF; color: white;"

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
                # Gráfico de barras para rotas
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
                # Usando as mesmas cores do seu código Matplotlib original
                color_discrete_map={
                    'DOMÉSTICA': '#275CBD',
                    'INTERNACIONAL': '#704DE6'
                },
                # Informações extras que aparecerão ao passar o mouse
                hover_data={
                    'nome_origem': True,
                    'nome_destino': True,
                    'total_voos': True,
                    'distancia_total': ':.0f' # Formata o número no hover
                }
            )

            # --- Ajustes Finos no Layout do Gráfico ---
            fig_dist_rota.update_layout(
                # Garante que a barra com maior valor fique no topo
                yaxis={'categoryorder':'total ascending'},
                # Aumenta a altura para as 20 rotas caberem confortavelmente
                height=700,
                # Posiciona a legenda de forma elegante acima do gráfico
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.01,
                    xanchor="right",
                    x=1
                )
            )

            # --- AJUSTE NO TEXTO E NO LAYOUT ---
            fig_dist_rota.update_traces(textposition='inside', insidetextanchor='middle', texttemplate='%{text:,.0f} km', textfont=dict(size=24, color='white'))

            # Exibe o novo gráfico interativo no Streamlit
            st.plotly_chart(fig_dist_rota, use_container_width=True)
           
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
elif pagina_atual == 'Painel de eficiência':

    # Aplicar CSS customizado apenas na home
    st.markdown(home_css, unsafe_allow_html=True)
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


    st.markdown("""
    <style>
    .metric-card {
        background: linear-gradient(135deg, #3b82f6, #8b5cf6);
        padding: 1.5rem;
        border-radius: 1.25rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        color: white;
        font-family: 'Segoe UI', sans-serif;
        margin-bottom: 1rem;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
    }
    .metric-label {
        font-size: 1rem;
        margin-top: 0.25rem;
        opacity: 0.9;
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

            eficiencia = None
            if tem_dados_combustivel:
                df_com_combustivel = df_empresa[df_empresa['combustivel_litros'] > 0]
                eficiencia = df_com_combustivel['distancia_voada_km'].sum() / df_com_combustivel['combustivel_litros'].sum()

            # Cards principais com estilo gradiente
            with st.container():
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"""
                        <div class="metric-card" style="background: linear-gradient(135deg, #4f46e5, #a855f7); color: white; border-radius: 8px; padding: 20px; text-align:center;">
                            <div style="font-size: 2.5rem; font-weight: 700;">{total_voos:,}</div>
                            <div style="font-size: 1rem; opacity: 0.8;">Total de Voos</div>
                        </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                        <div class="metric-card" style="background: linear-gradient(135deg, #4338ca, #7e22ce); color: white; border-radius: 8px; padding: 20px; text-align:center;">
                            <div style="font-size: 2.5rem; font-weight: 700;">{distancia_total:,.0f}</div>
                            <div style="font-size: 1rem; opacity: 0.8;">Distância Total (km)</div>
                        </div>
                    """, unsafe_allow_html=True)
                with col3:
                    if eficiencia is not None:
                        st.markdown(f"""
                            <div class="metric-card" style="background: linear-gradient(135deg, #6d28d9, #a78bfa); color: white; border-radius: 8px; padding: 20px; text-align:center;">
                                <div style="font-size: 2.5rem; font-weight: 700;">{eficiencia:.2f}</div>
                                <div style="font-size: 1rem; opacity: 0.8;">Eficiência (km/l)</div>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                            <div class="metric-card" style="background: #e0e7ff; border-radius: 8px; padding: 20px; text-align:center; color: #9ca3af;">
                                <div style="font-size: 2.5rem; font-weight: 700;">N/D</div>
                                <div style="font-size: 1rem;">Eficiência (sem dados)</div>
                            </div>
                        """, unsafe_allow_html=True)

            # Outras estatísticas com estilo igual aos anteriores (gradiente azul/roxo)
            st.subheader("Outras Estatísticas")
            with st.container():
                col4, col5 = st.columns(2)
                with col4:
                    media_distancia = distancia_total / total_voos if total_voos > 0 else 0
                    st.markdown(f"""
                        <div class="metric-card" style="background: linear-gradient(135deg, #4338ca, #7e22ce); color: white; border-radius: 8px; padding: 20px; text-align:center;">
                            <div style="font-size: 2.25rem; font-weight: 700;">{media_distancia:,.0f}</div>
                            <div style="font-size: 1rem; opacity: 0.8;">Média Distância por Voo (km)</div>
                        </div>
                    """, unsafe_allow_html=True)
                with col5:
                    horas_totais = df_empresa['horas_voadas'].sum()
                    st.markdown(f"""
                        <div class="metric-card" style="background: linear-gradient(135deg, #4f46e5, #a855f7); color: white; border-radius: 8px; padding: 20px; text-align:center;">
                            <div style="font-size: 2.25rem; font-weight: 700;">{horas_totais:,.1f}</div>
                            <div style="font-size: 1rem; opacity: 0.8;">Horas Totais de Voo</div>
                        </div>
                    """, unsafe_allow_html=True)

            meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

            # Dados para o gráfico de eficiência mensal
            df_combustivel = df_empresa[df_empresa['combustivel_litros'] > 0]

            # Layout dos gráficos: primeiro e terceiro lado a lado, segundo embaixo
            with st.container():
                col_graf1, col_graf3 = st.columns(2)

                # Gráfico 1: Eficiência Mensal (km/l)
                with col_graf1:
                    if df_combustivel.empty:
                        st.info("ℹ️ Esta empresa não possui dados de combustível disponíveis. Talvez opere apenas voos internacionais ou os dados não estão registrados.")
                    else:
                        df_empresa_mes = df_combustivel.groupby('mes').apply(
                            lambda x: x['distancia_voada_km'].sum() / x['combustivel_litros'].sum()
                        ).reset_index(name='eficiencia_km_l')

                        fig_ef = px.line(
                            df_empresa_mes,
                            x='mes',
                            y='eficiencia_km_l',
                            markers=True,
                            title='📊 Eficiência Mensal (km/l)',
                            color_discrete_sequence=['#6366f1']
                        )
                        fig_ef.update_layout(
                            xaxis=dict(
                                tickmode='array',
                                tickvals=df_empresa_mes['mes'],
                                ticktext=[meses[m-1] for m in df_empresa_mes['mes']]
                            ),
                            yaxis_title='Eficiência (km/l)',
                            xaxis_title='Mês',
                            plot_bgcolor='#ffffff',
                            font=dict(color='#1f2937'),
                            margin=dict(t=50, b=40, l=40, r=40)
                        )
                        st.plotly_chart(fig_ef, use_container_width=True)

                # Gráfico 3: Média de Horas e Km por Voo
                with col_graf3:
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
                        line=dict(color='#6366f1'),
                        yaxis='y1'
                    ))
                    fig_mix.add_trace(go.Scatter(
                        x=df_horas_mes['mes'],
                        y=df_horas_mes['media_km_por_voo'],
                        name='Km por Voo',
                        mode='lines+markers',
                        line=dict(color='#a855f7'),
                        yaxis='y2'
                    ))

                    fig_mix.update_layout(
                        title='Média de Horas e Km por Voo ao Longo dos Meses',
                        xaxis=dict(
                            tickmode='array',
                            tickvals=df_horas_mes['mes'],
                            ticktext=[meses[m-1] for m in df_horas_mes['mes']],
                            title='Mês'
                        ),
                        yaxis=dict(
                            title='Horas por Voo',
                            tickfont=dict(color='#6366f1')
                        ),
                        yaxis2=dict(
                            title='Km por Voo',
                            overlaying='y',
                            side='right',
                            tickfont=dict(color='#a855f7')
                        ),
                        plot_bgcolor='#ffffff',
                        font=dict(color='#1f2937'),
                        margin=dict(t=50, b=40, l=40, r=40),
                        legend=dict(x=0.01, y=0.99)
                    )
                    st.plotly_chart(fig_mix, use_container_width=True)

            # Gráfico 2: Distância Voada x Combustível por Mês (fica embaixo)
            df_mes = df_empresa.groupby('mes').agg({
                'distancia_voada_km': 'sum',
                'combustivel_litros': 'sum'
            }).reset_index()

            fig_bar = px.bar(
                df_mes.melt(id_vars='mes', value_vars=['distancia_voada_km', 'combustivel_litros']),
                x='mes',
                y='value',
                color='variable',
                barmode='group',
                color_discrete_map={
                    'distancia_voada_km': '#4f46e5',
                    'combustivel_litros': '#a855f7'
                },
                title='Distância Voada e Combustível Consumido por Mês'
            )
            fig_bar.update_layout(
                xaxis=dict(
                    tickmode='array',
                    tickvals=df_mes['mes'],
                    ticktext=[meses[m-1] for m in df_mes['mes']]
                ),
                yaxis_title='Quantidade',
                xaxis_title='Mês',
                plot_bgcolor='#ffffff',
                font=dict(color='#1f2937'),
                margin=dict(t=50, b=40, l=40, r=40)
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.warning("Nenhum dado encontrado para a empresa selecionada.")




    
    # --- ABA 2 ---
    with tab2:
        # CSS customizado para o estilo azul/roxo limpo e organizado
        css_custom = """
        <style>
        /* Container geral da aba */
        .tab2-container {
            padding: 1rem 1rem 2rem 1rem;
            background-color: #f9fafb;  /* fundo suave */
            border-radius: 10px;
            box-shadow: 0 2px 8px rgb(99 102 241 / 0.2);
            margin-bottom: 2rem;
        }

        /* Cards big numbers */
        .big-number-card {
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgb(99 102 241 / 0.4);
            text-align: center;
            font-weight: 700;
            font-size: 2.2rem;
            margin-bottom: 1rem;
            user-select: none;
        }

        /* Títulos dos cards */
        .big-number-label {
            font-size: 1.1rem;
            font-weight: 500;
            opacity: 0.85;
            margin-bottom: 0.3rem;
        }

        /* Ajuste do container dos filtros */
        .stMultiSelect > div[role="listbox"] {
            max-height: 150px !important;
            overflow-y: auto !important;
        }

        /* Layout dos gráficos: grid com espaçamento */
        .graphs-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
            gap: 1.5rem;
            margin-top: 1rem;
            margin-bottom: 3rem;
        }

        /* Estilo dos títulos subtítulos */
        h2, h3, h4 {
            color: #4c51bf;  /* azul roxo escuro */
            font-weight: 700;
        }

        /* Estilo das tabelas Streamlit */
        .stDataFrameWrapper table {
            border-radius: 8px !important;
            overflow: hidden !important;
            box-shadow: 0 2px 8px rgb(99 102 241 / 0.2);
        }

        /* Scroll para tabelas grandes */
        .stDataFrameWrapper {
            overflow-x: auto !important;
        }

        /* Ajuste do espaço entre colunas */
        .stColumns > div {
            padding: 0 1rem 1rem 0;
        }
        </style>
        """
        st.markdown(css_custom, unsafe_allow_html=True)

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

        # Preparação dados gráficos
        df_com_combustivel_geral = df[df['combustivel_litros'] > 0]
        df_eficiencia_geral_mes = df_com_combustivel_geral.groupby('mes').apply(
            lambda x: x['distancia_voada_km'].sum() / x['combustivel_litros'].sum()
        ).reset_index(name='eficiencia')

        meses_labels = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        ticks_labels = [meses_labels[m - 1] for m in df_eficiencia_geral_mes['mes']]
        # Gráfico 1: Eficiência Média por Mês
        fig_eficiencia_mes = px.line(
            df_eficiencia_geral_mes,
            x="mes",
            y="eficiencia",
            markers=True,
            color_discrete_sequence=["#6366f1"]  # azul
        )
        fig_eficiencia_mes.update_layout(
            xaxis=dict(
                tickmode='array',
                tickvals=df_eficiencia_geral_mes['mes'],
                ticktext=ticks_labels
            ),
            yaxis_title="Eficiência (km/l)",
            plot_bgcolor="#ffffff",
            font=dict(color="#1f2937"),
            margin=dict(t=40, b=30, l=20, r=20)
        )

        # Gráfico 2: Top 10 Empresas Mais Eficientes
        df_top10 = (
            df_com_combustivel_geral
            .groupby(['empresa_nome'])
            .apply(lambda x: x['distancia_voada_km'].sum() / x['combustivel_litros'].sum())
            .reset_index(name='eficiencia_km_l')
            .sort_values(by='eficiencia_km_l', ascending=False)
            .head(10)
        )

        fig_top10_eficiencia = px.bar(
            df_top10,
            x='eficiencia_km_l',
            y='empresa_nome',
            orientation='h',
            color='eficiencia_km_l',
            color_continuous_scale='Purples'
        )
        fig_top10_eficiencia.update_layout(
            xaxis_title='Eficiência (km/l)',
            yaxis_title='',
            plot_bgcolor='#ffffff',
            font=dict(color='#1f2937'),
            margin=dict(t=40, b=30, l=20, r=20)
        )

        # Gráfico 3: Top 10 Empresas com Maior Velocidade Média
        df_velocidade = df.groupby('empresa_nome').agg({
            'distancia_voada_km': 'sum',
            'horas_voadas': 'sum'
        }).reset_index()
        df_velocidade['velocidade_media_kmh'] = df_velocidade['distancia_voada_km'] / df_velocidade['horas_voadas']
        df_velocidade_top10 = df_velocidade.sort_values(by='velocidade_media_kmh', ascending=False).head(10)

        fig_top10_velocidade = px.bar(
            df_velocidade_top10,
            x='velocidade_media_kmh',
            y='empresa_nome',
            orientation='h',
            color='velocidade_media_kmh',
            color_continuous_scale='Blues'
        )
        fig_top10_velocidade.update_layout(
            xaxis_title='Velocidade Média (km/h)',
            yaxis_title='',
            plot_bgcolor='#ffffff',
            font=dict(color='#1f2937'),
            margin=dict(t=40, b=30, l=20, r=20)
        )

        # Gráfico 4: Volume de Decolagens e Consumo de Combustível por Mês
        df_volume = df.groupby('mes').agg({
            'decolagens': 'sum',
            'combustivel_litros': 'sum'
        }).reset_index()

        fig_volume = go.Figure()
        fig_volume.add_trace(go.Scatter(
            x=df_volume['mes'],
            y=df_volume['decolagens'],
            name='Total Decolagens',
            mode='lines+markers',
            line=dict(color='#6366f1'),
            yaxis='y1'
        ))
        fig_volume.add_trace(go.Scatter(
            x=df_volume['mes'],
            y=df_volume['combustivel_litros'],
            name='Total Combustível (L)',
            mode='lines+markers',
            line=dict(color='#8b5cf6'),
            yaxis='y2'
        ))
        fig_volume.update_layout(
            xaxis=dict(
                tickmode='array',
                tickvals=df_volume['mes'],
                ticktext=[meses_labels[m - 1] for m in df_volume['mes']]
            ),
            yaxis=dict(
                title='Decolagens',
                tickfont=dict(color='#6366f1')
            ),
            yaxis2=dict(
                title='Combustível (L)',
                tickfont=dict(color='#8b5cf6'),
                overlaying='y',
                side='right'
            ),
            legend=dict(x=0.01, y=0.99),
            plot_bgcolor='#ffffff',
            font=dict(color='#1f2937'),
            height=500,
            margin=dict(t=60, b=40, l=40, r=40)
        )

        # Exibição dos gráficos em layout grid
        st.markdown("#### 📈 Eficiência Média por Mês")
        st.plotly_chart(fig_eficiencia_mes, use_container_width=True)

        st.markdown("---")

        cols1 = st.columns(2)
        with cols1[0]:
            st.markdown("#### 🏆 Top 10 Empresas Mais Eficientes vs. Velocidade")
            st.plotly_chart(fig_top10_eficiencia, use_container_width=True)
        with cols1[1]:
            st.markdown("#### 🚀 Top 10 Empresas com Maior Velocidade Média de Voo")
            st.plotly_chart(fig_top10_velocidade, use_container_width=True)

        st.markdown("---")

        st.markdown("#### 📦 Volume de Operações e Consumo por Mês")
        st.plotly_chart(fig_volume, use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

elif pagina_atual == 'Eficiência Combustível':

    # Aplicar CSS customizado
    st.markdown(home_css, unsafe_allow_html=True)
    
    # Estilo personalizado da página
    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"] {
            background-color: #f9fafb;
        }
        
        /* CSS para mudar a cor das tabs selecionadas para azul */
        .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
            color: #0066cc !important;
            border-bottom-color: #0066cc !important;
        }
        
        .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] p {
            color: #0066cc !important;
        }
        
        .stTabs [data-baseweb="tab-highlight"] {
            background-color: #0066cc !important;
        }
        
        div[data-testid="stTabs"] > div[data-baseweb="tab-list"] button[aria-selected="true"] {
            color: #0066cc !important;
        }
        
        </style>
        """,
        unsafe_allow_html=True
    )
    st.title("⛽ Análise de Eficiência de Combustível")

    tab1, tab2 = st.tabs(["🏢 Por Empresa", "✈️ Por Rota"])

    with tab1:
        st.markdown("### 📊 Eficiência por Empresa")

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
        bottom3 = df.sort_values(by='eficiencia_km_por_litro', ascending=False).tail(3)

        # KPIs principais usando o padrão do projeto
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            create_big_number_card(
                "Média Geral de Eficiência",
                f"{media_eficiencia:.2f} km/l",
                f"{len(df)} empresas analisadas"
            )
        
        with col2:
            create_big_number_card(
                "Melhor Eficiência",
                f"{top3.iloc[0]['eficiencia_km_por_litro']:.2f} km/l",
                f"{top3.iloc[0]['empresa_sigla']}"
            )
        
        with col3:
            create_big_number_card(
                "Pior Eficiência",
                f"{bottom3.iloc[0]['eficiencia_km_por_litro']:.2f} km/l",
                f"{bottom3.iloc[0]['empresa_sigla']}"
            )
        
        with col4:
            total_combustivel = df['total_combustivel'].sum()
            create_big_number_card(
                "Total Combustível",
                f"{total_combustivel:,.0f} L",
                f"{df['total_km'].sum():,.0f} km voados"
            )

        # Top 3 Empresas Mais Eficientes
        st.markdown("---")
        st.markdown("### 🏆 Top 3 Empresas Mais Eficientes")
        
        cols = st.columns(3)
        for i, (_, row) in enumerate(top3.iterrows()):
            with cols[i]:
                st.markdown(f"""
                <div class="custom-card">
                    <p class="card-rank">{i+1}º Lugar</p>
                    <p class="card-main-text" style="color: #1e40af; font-size: 1.1rem;">{row['empresa_sigla']}</p>
                    <p class="card-sub-text">{row['empresa_nome']}</p>
                    <h3 class="card-metric-value" style="color: #16a34a;">{row['eficiencia_km_por_litro']:.2f} km/l</h3>
                    <p class="card-sub-text">{row['total_km']:,.0f} km voados</p>
                    <p class="card-sub-text">{row['total_combustivel']:,.0f} L consumidos</p>
                </div>
                """, unsafe_allow_html=True)

        # Top 3 Empresas Menos Eficientes
        st.markdown("### ⚠️ Top 3 Empresas Menos Eficientes")
        
        cols = st.columns(3)
        for i, (_, row) in enumerate(bottom3.iterrows()):
            with cols[i]:
                st.markdown(f"""
                <div class="custom-card">
                    <p class="card-rank">{i+1}º Menos Eficiente</p>
                    <p class="card-main-text" style="color: #1e40af; font-size: 1.1rem;">{row['empresa_sigla']}</p>
                    <p class="card-sub-text">{row['empresa_nome']}</p>
                    <h3 class="card-metric-value" style="color: #dc2626;">{row['eficiencia_km_por_litro']:.2f} km/l</h3>
                    <p class="card-sub-text">{row['total_km']:,.0f} km voados</p>
                    <p class="card-sub-text">{row['total_combustivel']:,.0f} L consumidos</p>
                </div>
                """, unsafe_allow_html=True)

        # Gráficos em containers estilizados
        st.markdown("---")
        st.markdown("### 📊 Análises Visuais")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="chart-container">
                <h4 style='color: #1e40af; text-align: center; font-size: 1.2rem;'>📈 Ranking de Eficiência por Empresa</h4>
            """, unsafe_allow_html=True)
            
            # Gráfico de barras horizontal com Plotly
            df_sorted = df.sort_values('eficiencia_km_por_litro', ascending=True)
            fig_eficiencia = px.bar(
                df_sorted,
                x='eficiencia_km_por_litro',
                y='empresa_sigla',
                orientation='h',
                title='',
                color='eficiencia_km_por_litro',
                color_continuous_scale=['#1f77b4', '#6a0dad'],
                labels={'eficiencia_km_por_litro': 'Eficiência (km/l)', 'empresa_sigla': 'Empresa'}
            )
            fig_eficiencia.update_layout(
                height=400, 
                showlegend=False,
                margin=dict(l=0, r=0, t=0, b=0)
            )
            # Adicionar linha da média
            fig_eficiencia.add_vline(
                x=media_eficiencia, 
                line_dash="dash", 
                line_color="blue",
                annotation_text=f"Média: {media_eficiencia:.2f}"
            )
            st.plotly_chart(fig_eficiencia, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="chart-container">
                <h4 style='color: #1e40af; text-align: center; font-size: 1.2rem;'>🥧 Distribuição da Eficiência</h4>
            """, unsafe_allow_html=True)
            
            # Gráfico de pizza com Plotly
            fig_pie = px.pie(
                df, 
                values='eficiencia_km_por_litro', 
                names='empresa_sigla',
                title='',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_pie.update_layout(height=400, margin=dict(l=0, r=0, t=0, b=0))
            fig_pie.update_traces(textinfo='percent+label', textfont_size=10)
            st.plotly_chart(fig_pie, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # Seletor de empresa individual
        st.markdown("---")
        st.markdown("### 🔍 Análise Individual por Empresa")
        
        empresa_selecionada = st.selectbox(
            "Selecione uma empresa para análise detalhada:",
            df['empresa_nome'].unique(),
            key="empresa_combustivel"
        )
        
        dados_empresa = df[df['empresa_nome'] == empresa_selecionada]
        if not dados_empresa.empty:
            empresa_eficiencia = dados_empresa['eficiencia_km_por_litro'].iloc[0]
            diferenca_media = empresa_eficiencia - media_eficiencia
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    "Eficiência da Empresa", 
                    f"{empresa_eficiencia:.2f} km/l",
                    delta=f"{diferenca_media:+.2f} vs média"
                )
            with col2:
                percentil = (df['eficiencia_km_por_litro'] < empresa_eficiencia).mean() * 100
                st.metric(
                    "Posição no Ranking", 
                    f"{percentil:.0f}º percentil",
                    delta="Melhor que média" if diferenca_media > 0 else "Pior que média"
                )
            with col3:
                economia = (empresa_eficiencia - media_eficiencia) * dados_empresa['total_combustivel'].iloc[0]
                st.metric(
                    "Economia vs Média", 
                    f"{economia:+.0f} L",
                    delta="Economia" if economia > 0 else "Desperdício"
                )

    with tab2:
        st.markdown("### 🛣️ Eficiência por Rota")
        
        query_rota = '''
            SELECT 
                v.aeroporto_origem_sigla,
                v.aeroporto_destino_sigla,
                a1.aeroporto_nome AS origem_nome,
                a2.aeroporto_nome AS destino_nome,
                SUM(v.distancia_voada_km) AS total_km,
                SUM(v.combustivel_litros) AS total_combustivel,
                COUNT(*) as total_voos
            FROM voo v
            JOIN aeroporto a1 ON v.aeroporto_origem_sigla = a1.aeroporto_sigla
            JOIN aeroporto a2 ON v.aeroporto_destino_sigla = a2.aeroporto_sigla
            WHERE v.combustivel_litros > 0
            GROUP BY v.aeroporto_origem_sigla, v.aeroporto_destino_sigla
            HAVING total_combustivel > 0
        '''

        df_rota = pd.read_sql_query(query_rota, conn)
        df_rota['eficiencia_km_por_litro'] = df_rota['total_km'] / df_rota['total_combustivel']
        df_rota['rota'] = df_rota['aeroporto_origem_sigla'] + " → " + df_rota['aeroporto_destino_sigla']
        df_rota['rota_nome'] = df_rota['origem_nome'] + " → " + df_rota['destino_nome']

        # Filtrar rotas com eficiência mínima de 1 km/l para evitar outliers
        df_rota_filtrado = df_rota[df_rota['eficiencia_km_por_litro'] >= 1]
        
        top_rotas = df_rota_filtrado.sort_values(by='eficiencia_km_por_litro', ascending=False).head(5)
        worst_rotas = df_rota_filtrado.sort_values(by='eficiencia_km_por_litro', ascending=True).head(5)

        # KPIs das rotas
        col1, col2, col3 = st.columns(3)
        
        with col1:
            create_big_number_card(
                "Total de Rotas Analisadas",
                f"{len(df_rota_filtrado)}",
                f"Com eficiência ≥ 1 km/l"
            )
        
        with col2:
            create_big_number_card(
                "Rota Mais Eficiente",
                f"{top_rotas.iloc[0]['eficiencia_km_por_litro']:.2f} km/l",
                f"{top_rotas.iloc[0]['rota']}"
            )
        
        with col3:
            create_big_number_card(
                "Rota Menos Eficiente",
                f"{worst_rotas.iloc[0]['eficiencia_km_por_litro']:.2f} km/l",
                f"{worst_rotas.iloc[0]['rota']}"
            )

        # Top 5 Rotas Mais Eficientes
        st.markdown("---")
        st.markdown("### 🏆 Top 5 Rotas Mais Eficientes")
        
        cols = st.columns(5)
        for i, (_, row) in enumerate(top_rotas.iterrows()):
            with cols[i]:
                st.markdown(f"""
                <div class="custom-card">
                    <p class="card-rank">{i+1}º Lugar</p>
                    <p class="card-main-text" style="color: #1e40af; font-size: 0.9rem;">{row['rota']}</p>
                    <h3 class="card-metric-value" style="color: #16a34a; font-size: 1.5rem;">{row['eficiencia_km_por_litro']:.2f}</h3>
                    <p class="card-sub-text">km/l</p>
                    <p class="card-sub-text">{row['total_voos']} voos</p>
                </div>
                """, unsafe_allow_html=True)

        # Top 5 Rotas Menos Eficientes
        st.markdown("### ⚠️ Top 5 Rotas Menos Eficientes")
        
        cols = st.columns(5)
        for i, (_, row) in enumerate(worst_rotas.iterrows()):
            with cols[i]:
                st.markdown(f"""
                <div class="custom-card">
                    <p class="card-rank">{i+1}º Menos Eficiente</p>
                    <p class="card-main-text" style="color: #1e40af; font-size: 0.9rem;">{row['rota']}</p>
                    <h3 class="card-metric-value" style="color: #dc2626; font-size: 1.5rem;">{row['eficiencia_km_por_litro']:.2f}</h3>
                    <p class="card-sub-text">km/l</p>
                    <p class="card-sub-text">{row['total_voos']} voos</p>
                </div>
                """, unsafe_allow_html=True)

        # Gráfico das rotas
        st.markdown("---")
        st.markdown("### 📊 Análise Visual das Rotas")
        
        # Top 20 rotas para o gráfico
        top_20_rotas = df_rota_filtrado.sort_values(by='eficiencia_km_por_litro', ascending=False).head(20)
        
        st.markdown("""
        <div class="chart-container">
            <h4 style='color: #1e40af; text-align: center; font-size: 1.2rem;'>📈 Top 20 Rotas por Eficiência de Combustível</h4>
        """, unsafe_allow_html=True)
        
        fig_rotas = px.bar(
            top_20_rotas.sort_values('eficiencia_km_por_litro', ascending=True),
            x='eficiencia_km_por_litro',
            y='rota',
            orientation='h',
            title='',
            color='eficiencia_km_por_litro',
            color_continuous_scale=['#1f77b4', '#6a0dad'],      
            labels={'eficiencia_km_por_litro': 'Eficiência (km/l)', 'rota': 'Rota'},
            hover_data={'total_voos': True, 'total_km': True}
        )
        fig_rotas.update_layout(
            height=600, 
            showlegend=False,
            margin=dict(l=0, r=0, t=0, b=0)
        )
        st.plotly_chart(fig_rotas, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Tabela detalhada das rotas
        st.markdown("---")
        st.markdown("### 📋 Dados Detalhados das Rotas")
        
        df_rota_display = df_rota_filtrado.copy()
        df_rota_display = df_rota_display.sort_values('eficiencia_km_por_litro', ascending=False)
        df_rota_display = df_rota_display.rename(columns={
            'rota': 'Rota (Siglas)',
            'rota_nome': 'Rota (Nomes)',
            'eficiencia_km_por_litro': 'Eficiência (km/l)',
            'total_voos': 'Total Voos',
            'total_km': 'Distância Total (km)',
            'total_combustivel': 'Combustível Total (L)'
        })
        
        # Formatar números
        df_rota_display['Eficiência (km/l)'] = df_rota_display['Eficiência (km/l)'].round(2)
        df_rota_display['Distância Total (km)'] = df_rota_display['Distância Total (km)'].apply(lambda x: f"{x:,.0f}")
        df_rota_display['Combustível Total (L)'] = df_rota_display['Combustível Total (L)'].apply(lambda x: f"{x:,.0f}")
        
        colunas_exibir = ['Rota (Siglas)', 'Rota (Nomes)', 'Eficiência (km/l)', 'Total Voos', 'Distância Total (km)', 'Combustível Total (L)']
        st.dataframe(df_rota_display[colunas_exibir], use_container_width=True, height=400)
elif pagina_atual == 'Análise de Voos Improdutivos Combustivel':
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
            st.title("Análise de Voos Com Alto Gasto De Combustível")

            total_voos = len(df)
            total_voos_improdutivos = len(df[(df["natureza"] != "INTERNACIONAL") & 
                                            (df["combustivel_litros"] / df["distancia_voada_km"] > 1)])
            percentual_improdutivo = (total_voos_improdutivos / total_voos) * 100 if total_voos > 0 else 0
            media_distancia = df["distancia_voada_km"].mean()
            media_combustivel = df["combustivel_litros"].mean()

            st.markdown("""
            <style>
            .custom-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

                padding: 1.5rem;
                border-radius: 0.75rem;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
                margin: 0.5rem 0;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100%;
                text-align: center;
                color: white;
                font-family: 'Segoe UI', sans-serif;
            }
            .metric-title {
                font-size: 1.1rem;
                margin-bottom: 0.5rem;
            }
            .metric-value {
                font-size: 2rem;
                font-weight: bold;
            }
            </style>
            """, unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(f"""
                <div class="custom-card">
                    <div class="metric-title">✈️ Total de Voos</div>
                    <div class="metric-value">{total_voos:,}</div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div class="custom-card">
                    <div class="metric-title">⛽ Voos Improdutivos</div>
                    <div class="metric-value">{total_voos_improdutivos:,}</div>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                <div class="custom-card">
                    <div class="metric-title">⚠️ % Voos Improdutivos</div>
                    <div class="metric-value">{percentual_improdutivo:.2f}%</div>
                </div>
                """, unsafe_allow_html=True)


            st.write("Selecione uma empresa para visualizar os dados.")
            empresas_domesticas = df[df["natureza"].str.upper() == "DOMÉSTICA"]
            empresas_disponiveis = empresas_domesticas["empresa_nome"].unique()
            empresa_selecionada = st.selectbox("Escolha uma empresa:", empresas_disponiveis)

            df_filtrado = df[df["empresa_nome"] == empresa_selecionada]

            if "natureza" not in df_filtrado.columns:
                st.error("Coluna 'natureza' não encontrada no conjunto de dados.")
            else:
                df_domestico = df_filtrado[df_filtrado["natureza"].str.upper() == "DOMÉSTICA"]

                if df_domestico.empty:
                    st.error("Não há dados disponíveis para combustivel desta empresa.")
                else:
                    voos_internacionais = df_filtrado[df_filtrado["natureza"].str.upper() == "INTERNACIONAL"]
                    if not voos_internacionais.empty:
                        st.warning("Os dados de combustível não são fornecidos para voos INTERNACIONAIS. Apenas DOMÉSTICOS foram considerados.")

                    st.bar_chart(df_domestico[["distancia_voada_km", "combustivel_litros"]])

                    filtro_improdutivo = df_domestico[
                        (df_domestico["combustivel_litros"] / df_domestico["distancia_voada_km"] > 1)
                    ]

                    total_voos = len(df_domestico)
                    total_improdutivos = len(filtro_improdutivo)
                    percentual_improdutivo = (total_improdutivos / total_voos) * 100 if total_voos > 0 else 0

                    st.markdown("""
                    <style>
                    .highlight-box {
                        background-color: #734cea;
                        padding: 1rem;
                        border-radius: 0.75rem;
                        color: white;
                        font-family: 'Segoe UI', sans-serif;
                        text-align: center;
                        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
                        font-size: 1.1rem;
                        height: 100%;
                    }
                    </style>
                    """, unsafe_allow_html=True)

                    # Criar colunas
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown(f"""
                        <div class="highlight-box">
                            ✈️ <strong>Total de voos DOMÉSTICOS:</strong> {total_voos:,}
                        </div>
                        """, unsafe_allow_html=True)

                    with col2:
                        st.markdown(f"""
                        <div class="highlight-box">
                            ⚠️ <strong>Percentual de voos improdutivos:</strong> {percentual_improdutivo:.2f}%
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)

                    st.markdown("""
                    <div style='text-align: center; font-size: 2rem; font-weight: 600; font-family: "Segoe UI", sans-serif;'>
                        Voos improdutivos (alto consumo de combustível em relação à distância voada):
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.dataframe(filtro_improdutivo)


                    with tab2:
                        st.title("Distribuição de Voos Improdutivos por Região")

                        if "aeroporto_regiao" not in df_domestico.columns:
                            st.warning("A coluna 'aeroporto_regiao' não está disponível para análise regional.")
                        else:
                            regioes_improdutivas = filtro_improdutivo["aeroporto_regiao"].value_counts()
                            if regioes_improdutivas.empty:
                                st.info("Nenhum voo improdutivo foi identificado para análise por região.")
                            else:
                                st.write("Voos improdutivos por região:")
                                st.bar_chart(regioes_improdutivas)                  
elif pagina_atual == 'Análise de Voos Improdutivos Passageiros/Bagagem':
    def consulta_carga_passageiros_por_empresa(empresa_sigla=None):
        query = '''
        SELECT 
            c.voo_id, 
            c.passageiros_pagos, 
            c.passageiros_gratis, 
            c.bagagem_kg, 
            c.carga_paga_kg, 
            c.carga_gratis_kg, 
            c.correio_kg,
            c.carga_paga_km,
            c.carga_gratis_km,
            v.ano, 
            v.mes,
            v.empresa_sigla,
            v.aeroporto_origem_sigla,
            v.aeroporto_destino_sigla
        FROM carga_passageiros c
        JOIN voo v ON c.voo_id = v.voo_id
        '''
        
        if empresa_sigla:
            query += f" WHERE v.empresa_sigla = '{empresa_sigla}'"

        return pd.read_sql(query, conn)

    # Função para calcular totais
    def calcula_totais(df):
        totais = {
            'total_passageiros_pagos': df['passageiros_pagos'].sum(),
            'total_passageiros_gratis': df['passageiros_gratis'].sum(),
            'total_bagagem': df['bagagem_kg'].sum(),
            'total_carga_paga': df['carga_paga_kg'].sum(),
            'total_carga_gratis': df['carga_gratis_kg'].sum(),
            'total_correio': df['correio_kg'].sum(),
        }
        return totais

    # Carregar todas as empresas para o filtro
    def carregar_empresas():
        query = "SELECT empresa_sigla, empresa_nome FROM empresa"
        return pd.read_sql(query, conn)

    def filtrar_voos_com_50_porcento_gratis(df):
        df['percentual_gratis'] = df['passageiros_gratis'] / (df['passageiros_pagos'] + df['passageiros_gratis']) * 100
        return df[df['percentual_gratis'] >= 50]

    # Carregar dados de empresas
    empresas = carregar_empresas()

    # Adicionar a opção 'Todos' ao filtro de seleção
    todos_empresa = pd.DataFrame({'empresa_sigla': ['todos'], 'empresa_nome': ['Todos']})
    empresas_com_todos = pd.concat([empresas, todos_empresa], ignore_index=True)

    # Adicionar filtro de seleção para a empresa
    empresa_selecionada = st.selectbox(
        "Selecione a empresa",
        empresas_com_todos['empresa_nome'].tolist()
    )

    # Obter a sigla da empresa selecionada
    if empresa_selecionada == 'Todos':
        empresa_sigla_selecionada = None
    else:
        empresa_sigla_selecionada = empresas_com_todos[empresas_com_todos['empresa_nome'] == empresa_selecionada]['empresa_sigla'].values[0]

    # Carregar dados filtrados de carga e passageiros para a empresa selecionada
    df_carga_passageiros = consulta_carga_passageiros_por_empresa(empresa_sigla_selecionada)

    # Exibir totais de passageiros e carga
    totais = calcula_totais(df_carga_passageiros)

    # Iniciar a aplicação Streamlit
    st.title('Análise de Passageiros e Carga por Empresa')

    # Exibir os dados na mesma linha usando colunas
    if empresa_selecionada == 'Todos':
        st.subheader(f'Totais de Passageiros e Carga para todas as empresas')
    else:
        st.subheader(f'Totais de Passageiros e Carga para a empresa: {empresa_selecionada}')

    # Criar 6 colunas para exibir os dados na mesma linha
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    st.markdown("""
    <style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 0.75rem;
        color: white;
        font-family: 'Segoe UI', sans-serif;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
        height: 100%;
    }
    .metric-label {
        font-size: 1rem;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

    # Layout em 6 colunas
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Passageiros Pagos</div>
            <div class="metric-value">{totais['total_passageiros_pagos']:,}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Passageiros Grátis</div>
            <div class="metric-value">{totais['total_passageiros_gratis']:,}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Bagagem (kg)</div>
            <div class="metric-value">{totais['total_bagagem']:,}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Carga Paga (kg)</div>
            <div class="metric-value">{totais['total_carga_paga']:,}</div>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Carga Grátis (kg)</div>
            <div class="metric-value">{totais['total_carga_gratis']:,}</div>
        </div>
        """, unsafe_allow_html=True)

    with col6:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Correio (kg)</div>
            <div class="metric-value">{totais['total_correio']:,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)

    if empresa_selecionada == 'Todos':
        st.subheader("Distribuição de Passageiros e Carga - Todas as Empresas")
    else:
        st.subheader(f"Distribuição de Passageiros e Carga - Empresa: {empresa_selecionada}")

    # Gráfico de distribuição dos passageiros
    fig_passageiros = px.bar(
        df_carga_passageiros,
        x=["passageiros_pagos", "passageiros_gratis"],
        title="Distribuição de Passageiros Pagos e Grátis",
        labels={"value": "Quantidade", "variable": "Tipo de Passageiro"},
        barmode="stack",
    )
    st.plotly_chart(fig_passageiros)

    # Gráfico de distribuição de bagagem e carga
    fig_carga_bagagem = px.bar(
        df_carga_passageiros,
        x=["bagagem_kg", "carga_paga_kg", "carga_gratis_kg", "correio_kg"],
        title="Distribuição de Bagagem, Carga Paga, Carga Grátis e Correio",
        labels={"value": "Peso (kg)", "variable": "Tipo de Carga"},
        barmode="stack",
    )
    st.plotly_chart(fig_carga_bagagem)
    


    st.subheader('Detalhes dos Voos com 50% ou Mais de Passageiros Grátis')
    
    # Filtrar voos com 50% ou mais de passageiros grátis
    df_50_gratis = filtrar_voos_com_50_porcento_gratis(df_carga_passageiros)
    
    # Exibir dados filtrados
    st.write("Voos com 50% ou mais de passageiros grátis:")
    st.dataframe(df_50_gratis[['ano', 'mes', 'empresa_sigla', 'aeroporto_origem_sigla', 'aeroporto_destino_sigla', 'passageiros_pagos', 'passageiros_gratis', 'percentual_gratis']])
elif pagina_atual == 'Rota e Geografia':
    st.title("Rotas")
    conn = sqlite3.connect("dados_voo.db")

    query = '''
    SELECT 
        vo.aeroporto_origem_sigla,
        ao.aeroporto_nome AS aeroporto_origem_nome,
        vo.aeroporto_destino_sigla,
        ad.aeroporto_nome AS aeroporto_destino_nome,
        COUNT(*) AS total_voos
    FROM voo vo
    JOIN aeroporto ao ON vo.aeroporto_origem_sigla = ao.aeroporto_sigla
    JOIN aeroporto ad ON vo.aeroporto_destino_sigla = ad.aeroporto_sigla
    GROUP BY vo.aeroporto_origem_sigla, vo.aeroporto_destino_sigla
    ORDER BY total_voos DESC
    LIMIT 200
    '''

    df = pd.read_sql_query(query, conn)

    st.title("✈️ Principais Rotas de Voo")

    total_voos_top_200 = df["total_voos"].sum()

    rota_mais_movimentada = df.iloc[0]
    rota_mais_sigla = f"{rota_mais_movimentada['aeroporto_origem_sigla']} → {rota_mais_movimentada['aeroporto_destino_sigla']}"
    rota_mais_nome = f"{rota_mais_movimentada['aeroporto_origem_nome']} → {rota_mais_movimentada['aeroporto_destino_nome']}"
    rota_mais_voos = rota_mais_movimentada["total_voos"]

    num_rotas = df.shape[0]

    st.markdown("""
    <style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 0.75rem;
        color: white;
        font-family: 'Segoe UI', sans-serif;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
        height: 100%;
    }
    .metric-label {
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: bold;
    }
    .metric-delta {
        font-size: 0.9rem;
        color: #e0e0e0;
        margin-top: 0.25rem;
    }
    .metric-subtext {
        font-size: 0.9rem;
        margin-top: 0.5rem;
        color: #ddd;
    }
    </style>
    """, unsafe_allow_html=True)

    # Colunas
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🔥 Rota Mais Movimentada</div>
            <div class="metric-value">{rota_mais_sigla}</div>
            <div class="metric-delta">{rota_mais_voos:,} voos</div>
            <div class="metric-subtext">{rota_mais_nome}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <br> 
            <div class="metric-label">📍 Rotas Apresentadas</div>
            <div class="metric-value">{num_rotas}</div>
            <br> 
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <br> 
            <div class="metric-label">✈️ Total de Voos (Top 200 Rotas)</div>
            <div class="metric-value">{total_voos_top_200:,}</div>
            <br> 
        </div>
        """, unsafe_allow_html=True)


    localizacoes_aeroportos = {
        "SBCT": {"nome": "Curitiba", "latitude": -25.5285, "longitude": -49.1758},
        "SBKP": {"nome": "Campinas", "latitude": -23.0074, "longitude": -47.1344},
        "SBGR": {"nome": "São Paulo", "latitude": -23.4319, "longitude": -46.4679},
        "SAEZ": {"nome": "Buenos Aires", "latitude": -34.8222, "longitude": -58.5358},
        "KMIA": {"nome": "Miami", "latitude": 25.7959, "longitude": -80.2870},
        "SBEG": {"nome": "Manaus", "latitude": -3.0386, "longitude": -60.0497},
        "SCEL": {"nome": "Santiago", "latitude": -33.3930, "longitude": -70.7858},
        "SBCF": {"nome": "Belo Horizonte", "latitude": -19.6244, "longitude": -43.9719},
        "SBRF": {"nome": "Recife", "latitude": -8.1265, "longitude": -34.9233},
        "SBBR": {"nome": "Brasília", "latitude": -15.8692, "longitude": -47.9208},
        "SEQM": {"nome": "Quito", "latitude": -0.1279, "longitude": -78.3575},
        "SBPA": {"nome": "Porto Alegre", "latitude": -29.9944, "longitude": -51.1714},
        "SBFL": {"nome": "Florianópolis", "latitude": -27.6702, "longitude": -48.5525},
        "SBSV": {"nome": "Salvador", "latitude": -12.9086, "longitude": -38.3225},
        "SBPS": {"nome": "Porto Seguro", "latitude": -16.4386, "longitude": -39.0808},
        "SUMU": {"nome": "Montevidéu", "latitude": -34.8384, "longitude": -56.0308},
        "SBBE": {"nome": "Belém", "latitude": -1.3793, "longitude": -48.4763},
        "SBFN": {"nome": "Fernando de Noronha", "latitude": -3.8549, "longitude": -32.4232},
        "SBVT": {"nome": "Vitória", "latitude": -20.2581, "longitude": -40.2864},
        "SGAS": {"nome": "Assunção", "latitude": -25.2396, "longitude": -57.5191},
        "SPJC": {"nome": "Lima", "latitude": -12.0219, "longitude": -77.1143},
        "SBSP": {"nome": "Congonhas", "latitude": -23.6267, "longitude": -46.6564},
        "SBMQ": {"nome": "Macapá", "latitude": 0.0506, "longitude": -51.0722},
        "KJFK": {"nome": "Nova York - JFK", "latitude": 40.6413, "longitude": -73.7781},
        "SBMO": {"nome": "Maceió - Zumbi dos Palmares", "latitude": -9.5106, "longitude": -35.7917},
        "SBCY": {"nome": "Cuiabá", "latitude": -15.6529, "longitude": -56.1167},
        "SBJP": {"nome": "João Pessoa", "latitude": -7.1458, "longitude": -34.9509},
        "SBRP": {"nome": "Ribeirão Preto", "latitude": -21.1364, "longitude": -47.7767},
        "SGES": {"nome": "Encarnación", "latitude": -27.2272, "longitude": -55.8375},
        "SBGO": {"nome": "Goiânia", "latitude": -16.6319, "longitude": -49.2262},
        "DNMM": {"nome": "Lagos, Nigéria", "latitude": 6.5774, "longitude": 3.3219},
        "EDDF": {"nome": "Frankfurt", "latitude": 50.0333, "longitude": 8.5706},
        "LPPT": {"nome": "Lisboa", "latitude": 38.7813, "longitude": -9.1359}
    }

    rotas_voo = [
    ("EDDF", "SBGR", 13), ("LPPT", "SBGR", 13), ("DNMM", "SBGR", 14),
    ("KJFK", "SBGR", 17), ("SBKP", "SUMU", 17), ("SBMQ", "SBBE", 17),
    ("SBPA", "SBKP", 17), ("SBRF", "SBSV", 17), ("SBSG", "SBBR", 17),
    ("SBSP", "SBGL", 17), ("SBSV", "SBKP", 17), ("SUMU", "SBGR", 17),
    ("SUMU", "SCEL", 17), ("KMIA", "SGAS", 18), ("SAEZ", "SBFL", 18),
    ("SBCF", "SBKP", 18), ("SBFL", "SBCT", 18), ("SBFL", "SBSP", 18),
    ("SBFZ", "SBRF", 18), ("SBGL", "SBSP", 18), ("SBRF", "SBGL", 18),
    ("SBRF", "SBKP", 18), ("SBSP", "SBRJ", 18), ("SBGR", "SBCF", 30),
    ("SBGR", "SBRF", 30), ("SBKP", "SBCT", 31), ("SBGR", "SBGL", 31),
    ("SBBR", "SBKP", 31), ("SBKP", "SEQM", 32), ("SBCF", "SBGR", 32),
    ("SBRF", "SBGR", 33), ("SAEZ", "SBGR", 34), ("SBGL", "SBKP", 36),
    ("SBGL", "SBGR", 38), ("SCEL", "SBGR", 38), ("KMIA", "SBEG", 38),
    ("SBKP", "SBGR", 39), ("SBGR", "SCEL", 41), ("SBGL", "SAEZ", 41),
    ("KMIA", "SBKP", 41), ("SBGR", "SAEZ", 43), ("SBCT", "SBKP", 43)
]


    def definir_cor_voo(num_voos):
        if num_voos <= 10:
            return "blue"
        elif num_voos <= 20:
            return "green"
        elif num_voos <= 30:
            return "orange"
        elif num_voos <= 40:
            return "purple"
        else:
            return "red"

    m = folium.Map(location=[-15.7801, -47.9292], zoom_start=5)

    # Marcadores de aeroportos
    for codigo, dados in localizacoes_aeroportos.items():
        folium.Marker(
            location=[dados["latitude"], dados["longitude"]],
            popup=f"{dados['nome']} ({codigo})",
            tooltip=codigo,
            icon=folium.Icon(color="blue", icon="plane")
        ).add_to(m)

    # Linhas das rotas
    for origem, destino, num_voos in rotas_voo:
        if origem in localizacoes_aeroportos and destino in localizacoes_aeroportos:
            origem_coords = [localizacoes_aeroportos[origem]["latitude"], localizacoes_aeroportos[origem]["longitude"]]
            destino_coords = [localizacoes_aeroportos[destino]["latitude"], localizacoes_aeroportos[destino]["longitude"]]
            
            folium.PolyLine(
                [origem_coords, destino_coords],
                color=definir_cor_voo(num_voos),
                opacity=0.8,
                tooltip=f"{origem} → {destino}: {num_voos} voos"
            ).add_to(m)
            
        
    # Título e descrição centralizados
    st.markdown("<h1 style='text-align: center;'>Mapa de Rotas Aéreas</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Este mapa exibe os principais aeroportos e suas conexões de voo, com cor e espessura proporcional ao número de voos.</p>", unsafe_allow_html=True)

    # Centralização do mapa usando colunas
    col_espaco1, col_mapa, col_espaco2 = st.columns([2, 3, 2])

    with col_mapa:
        folium_static(m)


    st.markdown("""
    <style>
    .legend-card {
        background-color: #ffffff; /* Branco */
        padding: 0.5rem; /* Reduz o padding para um card menor */
        border-radius: 0.5rem;
        color: black; /* Preto */
        font-family: 'Segoe UI', sans-serif;
        text-align: left; /* Alinhado à esquerda */
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        width: 250px; /* Define uma largura menor */
    }
    .legend-label {
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 0.3rem;
    }
    .legend-value {
        font-size: 1.2rem;
        font-weight: bold;
    }
    .legend-subtext {
        font-size: 0.8rem;
        margin-top: 0.3rem;
        color: #555; /* Cinza escuro para detalhes */
    }
    </style>

    <div class="legend-card">
        <div class="legend-label">Legenda das Cores das Rotas:</div>
        <div class="legend-value">🔴 <strong>Vermelho</strong>: 41+ voos</div>
        <div class="legend-value">🟣 <strong>Roxo</strong>: 31-40 voos</div>
        <div class="legend-value">🟠 <strong>Laranja</strong>: 21-30 voos</div>
        <div class="legend-value">🟢 <strong>Verde</strong>: 11-20 voos</div>
        <div class="legend-value">🔵 <strong>Azul</strong>: 0-10 voos</div>
    </div>
    """, unsafe_allow_html=True)






    df = pd.read_sql_query(query, conn)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("<h3 style='text-align: center;'>📉 Gráfico de Rotas por Total de Voos</h3>", unsafe_allow_html=True)

    df['rota_nome'] = df['aeroporto_origem_nome'] + " → " + df['aeroporto_destino_nome']

    df_sorted = df.sort_values("total_voos", ascending=True)

    fig_bar = px.bar(
        df_sorted,
        x="total_voos",
        y="rota_nome",
        orientation="h",
        labels={"total_voos": "Total de Voos", "rota_nome": "Rota"},
        height=800,
        title="Top Rotas com Maior Volume de Voos"
    )

    fig_bar.update_layout(
        title_x=1, 
        margin=dict(l=100, r=100, t=50, b=50)  
    )

    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>🔁 Fluxo entre Regiões (Sankey)</h3>", unsafe_allow_html=True)

    region_query = '''
    SELECT 
        vo.aeroporto_origem_sigla,
        ao.aeroporto_regiao AS regiao_origem,
        vo.aeroporto_destino_sigla,
        ad.aeroporto_regiao AS regiao_destino,
        COUNT(*) AS total_voos
    FROM voo vo
    JOIN aeroporto ao ON vo.aeroporto_origem_sigla = ao.aeroporto_sigla
    JOIN aeroporto ad ON vo.aeroporto_destino_sigla = ad.aeroporto_sigla
    GROUP BY regiao_origem, regiao_destino
    ORDER BY total_voos DESC
    '''

    df_regioes = pd.read_sql_query(region_query, conn)

    nodes = list(set(df_regioes['regiao_origem']).union(set(df_regioes['regiao_destino'])))
    nodes = [r for r in nodes if r]  

    node_dict = {name: i for i, name in enumerate(nodes)}
    source = df_regioes['regiao_origem'].map(node_dict)
    target = df_regioes['regiao_destino'].map(node_dict)
    value = df_regioes['total_voos']

    fig_sankey = go.Figure(data=[go.Sankey(
        node=dict(
            pad=20,  
            thickness=30,
            label=nodes,
            color="blue"
        ),
        link=dict(
            source=source,
            target=target,
            value=value
        ))])

    fig_sankey.update_layout(
        title_text="Fluxo de Voos entre Regiões",
        title_x=1,  
        font_size=20
    )

    st.plotly_chart(fig_sankey, use_container_width=True)

    
    st.markdown("""
    <style>
    .legend-card2 {
        background-color: #ffffff; /* Branco */
        padding: 0.8rem; /* Reduz o padding para um card menor */
        border-radius: 0.5rem;
        color: black; /* Preto */
        font-family: 'Segoe UI', sans-serif;
        text-align: left; /* Alinhado à esquerda */
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        width: 800px; /* Define uma largura menor */
    }
    .legend-label {
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 0.3rem;
    }
    .legend-value {
        font-size: 1.2rem;
        font-weight: bold;
    }
    .legend-subtext {
        font-size: 0.8rem;
        margin-top: 0.3rem;
        color: #555; /* Cinza escuro para detalhes */
    }
    </style>

    <div class="legend-card2">
        <div class="legend-label">ℹ️ Legenda do Gráfico Sankey: Fluxo de Voos entre Regiões</div>
        <div class="legend-value">✈️ <strong>Cada bloco (nó)</strong> representa uma **região**.</div>
        <div class="legend-value">➡️ <strong>Setas</strong> mostram os voos **de uma região para outra**.</div>
        <div class="legend-value">📊 <strong>Espessura das setas</strong> = quantidade de voos.</div>
        <div class="legend-value">🔎 Exemplo: fluxo grosso de *Sudeste → Nordeste* = muitos voos nessa rota.</div>
    </div>
    """, unsafe_allow_html=True)
elif pagina_atual == 'KPIs Gerenciais':
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
                    color_continuous_scale=['#1f77b4', '#6a0dad'],  # Azul para roxo
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
                    color_discrete_sequence=['#1f77b4']
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
                    color_continuous_scale=['#1f77b4', '#6a0dad'],
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
    def get_empresas(conn):
        query = '''
            SELECT DISTINCT e.empresa_nome
            FROM empresa e
            JOIN voo v ON v.empresa_sigla = e.empresa_sigla
            ORDER BY e.empresa_nome
        '''
        return pd.read_sql_query(query, conn)['empresa_nome'].tolist()

    def get_destaques(conn):
        query = '''
            WITH todos_aeroportos AS (
                SELECT aeroporto_origem_sigla AS sigla FROM voo
                UNION
                SELECT aeroporto_destino_sigla FROM voo
            ),
            movimentacao_total AS (
                SELECT sigla, aeroporto_nome, SUM(total_voos) AS total FROM (
                    SELECT vo.aeroporto_origem_sigla AS sigla, ap.aeroporto_nome, COUNT(*) AS total_voos
                    FROM voo vo
                    JOIN aeroporto ap ON vo.aeroporto_origem_sigla = ap.aeroporto_sigla
                    GROUP BY vo.aeroporto_origem_sigla

                    UNION ALL

                    SELECT vo.aeroporto_destino_sigla AS sigla, ap.aeroporto_nome, COUNT(*) AS total_voos
                    FROM voo vo
                    JOIN aeroporto ap ON vo.aeroporto_destino_sigla = ap.aeroporto_sigla
                    GROUP BY vo.aeroporto_destino_sigla
                )
                GROUP BY sigla
                ORDER BY total DESC
                LIMIT 1
            ),
            rotas_unicas AS (
                SELECT COUNT(*) AS total FROM (
                    SELECT DISTINCT aeroporto_origem_sigla, aeroporto_destino_sigla FROM voo
                )
            )
            SELECT
                (SELECT COUNT(DISTINCT sigla) FROM todos_aeroportos) AS total_aeroportos,
                (SELECT aeroporto_nome FROM movimentacao_total) AS aeroporto_top,
                (SELECT total FROM movimentacao_total) AS total_movimentado,
                (SELECT total FROM rotas_unicas) AS total_rotas
        '''
        return pd.read_sql_query(query, conn)

    def get_rotas_por_empresa(conn, empresa_nome):
        query = '''
            SELECT 
                e.empresa_nome,
                vo.aeroporto_origem_sigla,
                ao.aeroporto_nome AS aeroporto_origem_nome,
                vo.aeroporto_destino_sigla,
                ad.aeroporto_nome AS aeroporto_destino_nome,
                COUNT(*) AS total_voos
            FROM voo vo
            JOIN empresa e ON vo.empresa_sigla = e.empresa_sigla
            JOIN aeroporto ao ON vo.aeroporto_origem_sigla = ao.aeroporto_sigla
            JOIN aeroporto ad ON vo.aeroporto_destino_sigla = ad.aeroporto_sigla
            WHERE e.empresa_nome = ?
            GROUP BY e.empresa_nome, vo.aeroporto_origem_sigla, vo.aeroporto_destino_sigla
            ORDER BY total_voos DESC
            LIMIT 200
        '''
        return pd.read_sql_query(query, conn, params=(empresa_nome,))

    # --- Títulos e Big Numbers ---
    st.title("📍 Destaques sobre Aeroportos")

    st.markdown("""
    <style>
    .custom-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 0.75rem;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
        margin: 0.5rem 0;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100%;
        text-align: center;
        color: white;
        font-family: 'Segoe UI', sans-serif;
    }
    .metric-title {
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

    destaques = get_destaques(conn)
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="custom-card">
            <div class="metric-title">🛫 Total de Aeroportos</div>
            <div class="metric-value">{destaques['total_aeroportos'][0]}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="custom-card">
            <div class="metric-title">🌐 Aeroporto +Movimentado</div>
            <div class="metric-value">{destaques['aeroporto_top'][0]}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="custom-card">
            <div class="metric-title">✈️ Total de Rotas Únicas</div>
            <div class="metric-value">{destaques['total_rotas'][0]}</div>
        </div>
        """, unsafe_allow_html=True)


    # --- Interface e dados por empresa ---
    st.title("✈️ Principais Aeroportos por Empresa")

    empresas = get_empresas(conn)
    empresa_selecionada = st.selectbox("Selecione uma empresa aérea:", empresas)

    top3_query = '''
        WITH uso_aeroportos AS (
            SELECT aeroporto_origem_sigla AS sigla, COUNT(*) AS total
            FROM voo v
            JOIN empresa e ON v.empresa_sigla = e.empresa_sigla
            WHERE e.empresa_nome = ?
            GROUP BY aeroporto_origem_sigla

            UNION ALL

            SELECT aeroporto_destino_sigla AS sigla, COUNT(*) AS total
            FROM voo v
            JOIN empresa e ON v.empresa_sigla = e.empresa_sigla
            WHERE e.empresa_nome = ?
            GROUP BY aeroporto_destino_sigla
        )
        SELECT a.aeroporto_nome, SUM(u.total) AS total_uso
        FROM uso_aeroportos u
        JOIN aeroporto a ON u.sigla = a.aeroporto_sigla
        GROUP BY a.aeroporto_nome
        ORDER BY total_uso DESC
        LIMIT 3
    '''
    top3_df = pd.read_sql_query(top3_query, conn, params=(empresa_selecionada, empresa_selecionada))

    # Exibir em formato Big Number
    st.subheader("🏆 Top 3 Aeroportos Mais Utilizados")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="custom-card">
            <div class="metric-title">🌍 {top3_df.iloc[0]['aeroporto_nome']}</div>
            <div class="metric-value">{top3_df.iloc[0]['total_uso']:,} voos</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="custom-card">
            <div class="metric-title">🌍 {top3_df.iloc[1]['aeroporto_nome']}</div>
            <div class="metric-value">{top3_df.iloc[1]['total_uso']:,} voos</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="custom-card">
            <div class="metric-title">🌍 {top3_df.iloc[2]['aeroporto_nome']}</div>
            <div class="metric-value">{top3_df.iloc[2]['total_uso']:,} voos</div>
        </div>
        """, unsafe_allow_html=True)



    df_rotas = get_rotas_por_empresa(conn, empresa_selecionada)

    st.subheader(f"📍 Rotas mais frequentes da empresa: {empresa_selecionada}")
    st.dataframe(df_rotas)

    query = '''
    SELECT 
        ao.aeroporto_nome AS cidade_origem,
        ad.aeroporto_nome AS cidade_destino,
        COUNT(*) AS total_voos
    FROM voo vo
    JOIN empresa e ON vo.empresa_sigla = e.empresa_sigla
    JOIN aeroporto ao ON vo.aeroporto_origem_sigla = ao.aeroporto_sigla
    JOIN aeroporto ad ON vo.aeroporto_destino_sigla = ad.aeroporto_sigla
    WHERE e.empresa_nome = ?
    GROUP BY cidade_origem, cidade_destino
    ORDER BY total_voos DESC
    '''

    df = pd.read_sql_query(query, conn, params=(empresa_selecionada,))

    # Geocodificação com cache
    @st.cache_data
    def geocode_city(city):
        geolocator = Nominatim(user_agent="geo_app")
        try:
            location = geolocator.geocode(city)
            if location:
                return location.latitude, location.longitude
        except:
            return None, None
        return None, None

    # Obter coordenadas de origem e destino
    df[['lat_origem', 'lon_origem']] = df['cidade_origem'].apply(lambda x: pd.Series(geocode_city(x)))
    df[['lat_destino', 'lon_destino']] = df['cidade_destino'].apply(lambda x: pd.Series(geocode_city(x)))

    # Filtrar apenas linhas com coordenadas válidas
    df = df.dropna(subset=['lat_origem', 'lon_origem', 'lat_destino', 'lon_destino'])

    # Exibir no Streamlit
    st.title("🗺️ Mapa de Rotas Aéreas por Cidade")

    # Exibir mapa com linhas de voo
    layer = pdk.Layer(
        "ArcLayer",
        data=df,
        get_source_position=["lon_origem", "lat_origem"],
        get_target_position=["lon_destino", "lat_destino"],
        get_width=2,
        get_tilt=15,
        get_source_color=[255, 0, 0, 160],
        get_target_color=[0, 0, 255, 160],
        auto_highlight=True,
        pickable=True,
    )

    view_state = pdk.ViewState(latitude=-14, longitude=-52, zoom=3.5, pitch=30)

    r = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"text": "De: {cidade_origem}\nPara: {cidade_destino}\nVoos: {total_voos}"},
    )

    st.pydeck_chart(r)



conn.close()
