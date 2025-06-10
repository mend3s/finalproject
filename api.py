import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

conn = sqlite3.connect("dados_voo.db")
cursor = conn.cursor()


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
    
st.sidebar.button("📌 Home", on_click=lambda: st.session_state.update(aba_ativa='home'))
st.sidebar.button("🔍 Filtros", on_click=lambda: st.session_state.update(aba_ativa='filtros'))
st.sidebar.button("⛽ Eficiencia Combustivel", on_click=lambda: st.session_state.update(aba_ativa='eficiencia_comb'))
st.sidebar.button("📊 Gráficos Clientes", on_click=lambda: st.session_state.update(aba_ativa='graficos_clientes'))
st.sidebar.button("🧑 Cliente", on_click=lambda: st.session_state.update(aba_ativa='cliente'))
st.sidebar.button("📦 Produtos", on_click=lambda: st.session_state.update(aba_ativa='produtos'))


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


    
if st.session_state.aba_ativa == 'filtros':
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
        /* Container principal do conteúdo para espaçar da sidebar */
        [data-testid="stAppViewContainer"] > .main {
            padding-left: 32px;
            padding-right: 32px;
            padding-top: 24px;
            padding-bottom: 48px;
            max-width: 900px;
            margin: auto;
        }

        /* Container do selectbox */
        div.stSelectbox > div {
            background-color: #ffffff;
            padding: 14px 18px;
            border-radius: 10px;
            border: 1.2px solid #ddd;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
            margin-bottom: 36px;
            position: relative;
            font-family: 'Inter', sans-serif;
            transition: border-color 0.3s ease, box-shadow 0.3s ease;
        }
        div.stSelectbox > div:hover {
            border-color: #2563eb;
            box-shadow: 0 4px 14px rgba(37, 99, 235, 0.15);
        }

        div.stSelectbox select {
            appearance: none;
            -webkit-appearance: none;
            -moz-appearance: none;
            border: none;
            background: transparent;
            width: 100%;
            padding: 10px 38px 10px 10px;
            font-size: 16px;
            font-weight: 600;
            color: #1f2937;
            cursor: pointer;
            outline: none;
        }

        div.stSelectbox div[role="combobox"]::after {
            content: "▾";
            position: absolute;
            right: 18px;
            top: 50%;
            transform: translateY(-50%);
            pointer-events: none;
            font-size: 13px;
            color: #6b7280;
            font-weight: 700;
        }

        label[data-testid="stMarkdownContainer"] {
            font-weight: 700;
            margin-bottom: 12px;
            display: block;
            font-size: 17px;
            color: #111827;
            font-family: 'Inter', sans-serif;
        }

        /* Métricas mais clean */
        .big-number {
            font-size: 2.4rem;  /* menor que antes */
            font-weight: 700;
            color: #333;
            margin-bottom: 4px;
            font-family: 'Inter', sans-serif;
            line-height: 1.2;
        }

        .small-label {
            font-size: 1rem;
            color: #555;
            font-weight: 600;
            font-family: 'Inter', sans-serif;
            margin-bottom: 20px;
        }

        .stColumns > div {
            padding: 0 12px !important;
        }

        .metric-container {
            margin-bottom: 40px;
        }

        h2, h3, h4 {
            font-family: 'Inter', sans-serif;
            color: #111827;
            font-weight: 700;
            margin-bottom: 20px;
        }

        .stAlert {
            font-family: 'Inter', sans-serif;
            font-size: 1rem;
            color: #374151;
            margin-top: 24px;
            margin-bottom: 36px;
        }
        </style>
    """, unsafe_allow_html=True)


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
            consumo_medio = df_com_combustivel['distancia_voada_km'].sum() / df_com_combustivel['combustivel_litros'].sum()
            eficiencia = consumo_medio
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

        if 'combustivel_litros' in df_empresa.columns and not tem_dados_combustivel:
            st.info("Esta empresa não possui dados de consumo de combustível registrados.")
    else:
        st.warning("Nenhum dado disponível para a empresa selecionada.")


    st.header("📊 Análises Gráficas")

    # Filtra o DataFrame geral para considerar apenas registros com combustível > 0
    df_com_combustivel_geral = df[df['combustivel_litros'] > 0]

    # Agrupa por mês e calcula a eficiência média (km/l) no geral
    df_eficiencia_geral_mes = df_com_combustivel_geral.groupby('mes').apply(
        lambda x: x['distancia_voada_km'].sum() / x['combustivel_litros'].sum()
    ).reset_index(name='eficiencia')

    # Meses presentes nos dados
    meses_presentes = df_eficiencia_geral_mes['mes'].tolist()
    meses_labels = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    ticks_labels = [meses_labels[m - 1] for m in meses_presentes]

    # Criar o gráfico
    fig, ax = plt.subplots()
    sns.lineplot(data=df_eficiencia_geral_mes, x='mes', y='eficiencia', marker='o', ax=ax)
    ax.set_title('Eficiência Média Geral por Mês em 2025')
    ax.set_xlabel('Mês')
    ax.set_ylabel('Eficiência (km/l)')
    ax.set_xticks(meses_presentes)
    ax.set_xticklabels(ticks_labels)
    ax.grid(True)

    # Exibir no Streamlit
    st.pyplot(fig)

    # Agrupa e calcula a eficiência
    df_top10 = (
        df_com_combustivel_geral
        .groupby(['empresa_nome'])
        .apply(lambda x: x['distancia_voada_km'].sum() / x['combustivel_litros'].sum())
        .reset_index(name='eficiencia_km_l')
        .sort_values(by='eficiencia_km_l', ascending=False)
        .head(10)
    )

    # Gráfico de barras horizontal
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=df_top10, x='eficiencia_km_l', y='empresa_nome', ax=ax, palette='Blues_r')
    ax.set_title('Top 10 Empresas Mais Eficientes (km/l)')
    ax.set_xlabel('Eficiência (km/l)')
    ax.set_ylabel('Empresa')

    st.pyplot(fig)

    st.subheader("⏱️ Top 10 Empresas com Maior Velocidade Média de Voo")

    # Agrupa por empresa: soma distância e horas voadas
    df_velocidade = df.groupby('empresa_nome').agg({
        'distancia_voada_km': 'sum',
        'horas_voadas': 'sum'
    }).reset_index()

    # Calcula a velocidade média km/h
    df_velocidade['velocidade_media_kmh'] = df_velocidade['distancia_voada_km'] / df_velocidade['horas_voadas']

    # Ordena para pegar as top 10 empresas com maior velocidade média
    df_velocidade_top10 = df_velocidade.sort_values(by='velocidade_media_kmh', ascending=False).head(10)

    # Plot do gráfico de barras horizontal
    fig, ax = plt.subplots(figsize=(8,5))
    sns.barplot(data=df_velocidade_top10, x='velocidade_media_kmh', y='empresa_nome', palette='plasma', ax=ax)
    ax.set_xlabel('Velocidade Média (km/h)')
    ax.set_ylabel('Empresa')
    ax.set_title('Top 10 Empresas com Maior Velocidade Média de Voo')
    st.pyplot(fig)








