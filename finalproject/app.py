# app.py
import numpy as np
import func.functions as api
import pandas as pd
import streamlit as st
import streamlit_pills as stp
from streamlit_folium import st_folium
from func import functions
import plotly.express as px
from xgboost import XGBClassifier

# --- Configuração da Página ---
st.set_page_config(
    page_title="Credit Card Analyses",
    page_icon="🕵️",
    layout="wide",
)

# --- Estilos CSS ---
st.markdown("""
<style>
/* --- ESTILO BASE DO CARD --- */
.kpi-card {
    position: relative;
    background-color: #FFFFFF;
    padding: 20px;
    border: 0.5px solid #DDDDDD;
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
.kpi-card h3 { font-size: 1.1em; text-transform: uppercase; font-weight: 600; color: #666666; }
.kpi-card h2 { font-size: 2.1em; font-weight: bolder; color: #2A2A2A; }
.kpi-card.color-1 { border-left-color: #0d47a1; }
.kpi-card.color-2 { border-left-color: #2e7d32; }
.kpi-card.color-4 { border-left-color: #d84315; }
</style>
""", unsafe_allow_html=True)


# --- Título Principal ---
st.title("🕵️ DASHBOARD DE ANÁLISE DE FRAUDES")

opcoes_menu = ["Visão Geral","Análise Geográfica", "Analise Exploratoria", "Análise Direcionada", "Resumo Estratégico"]
icones_menu = ["💡", "🗺️", "🔬", "🎯", "🏆"] 

if 'pagina_selecionada' not in st.session_state:
    st.session_state.pagina_selecionada = opcoes_menu[0]

pagina_atual = stp.pills(
    label="Navegue pelas fases do projeto:",
    options=opcoes_menu,
    icons=icones_menu,
    
    key="menu_navegacao",
    
    index=opcoes_menu.index(st.session_state.pagina_selecionada)
)

st.session_state.pagina_selecionada = pagina_atual

if pagina_atual == "Visão Geral":
    st.header("💡 Resumo Executivo de Segurança e Operações")
    df_principal = api.carregar_dados()
    
    col1, col2 = st.columns(2)
    with col1:
        # Garante que o valor padrão não cause erro se o df for vazio no primeiro carregamento
        data_minima = df_principal['Timestamp'].min().date() if not df_principal.empty else None
        data_inicio = st.date_input("Data de Início", data_minima)
    with col2:
        data_maxima = df_principal['Timestamp'].max().date() if not df_principal.empty else None
        data_fim = st.date_input("Data de Fim", data_maxima)
    
    if data_inicio and data_fim:
        data_inicio_dt = pd.to_datetime(data_inicio)
        # Adiciona 1 dia para incluir a data final na seleção
        data_fim_dt = pd.to_datetime(data_fim) + pd.Timedelta(days=1)
        
        # Filtra o DataFrame com base no período selecionado
        df_filtrado = df_principal[(df_principal['Timestamp'] >= data_inicio_dt) & (df_principal['Timestamp'] < data_fim_dt)]

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
        
elif pagina_atual == "Análise Geográfica":
    df_principal = api.carregar_dados()
    st.header("🗺️ Análise Geográfica Agregada")
    st.info("Explore o volume e a taxa de fraude por localização. O tamanho do círculo indica o volume de transações e a cor indica o risco de fraude.")
    
    col1, col2 = st.columns(2)
    with col1:
        tipos_transacao = ['Todos'] + sorted(df_principal['Transaction_Type'].unique())
        tipo_selecionado = st.selectbox("Filtrar por Tipo de Transação:", tipos_transacao)
    with col2:
        status_fraude = {'Todos': None, 'Apenas Fraudes': 1, 'Apenas Legítimas': 0}
        status_selecionado_key = st.selectbox("Filtrar por Status:", options=list(status_fraude.keys()))
        status_selecionado_value = status_fraude[status_selecionado_key]

    # Aplica os filtros
    df_filtrado = df_principal.copy()
    if tipo_selecionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Transaction_Type'] == tipo_selecionado]
    if status_selecionado_value is not None:
        df_filtrado = df_filtrado[df_filtrado['Fraud_Label'] == status_selecionado_value]

    # Chama a função de mapa agregado
    mapa_agregado = api.criar_mapa_agregado_por_localizacao(df_filtrado)

    # ** LINHAS ADICIONADAS PARA EXIBIR O MAPA **
    if mapa_agregado:
        st_folium(mapa_agregado, use_container_width=True)
    else:
        # Mostra um aviso se não houver dados ou se o mapa não puder ser gerado
        st.warning("Não há dados para exibir com os filtros selecionados.")
    

elif pagina_atual == "Analise Exploratoria":
    
    st.header("🔬 Análise Exploratória de Dados (EDA)")
    st.markdown("Esta é a **fundação** da nossa análise. Aqui, fazemos um diagnóstico completo dos dados para entender suas características, distribuições e relações iniciais.")
    
    # --- 1. CARREGAMENTO DOS DADOS ---
    df = functions.carregar_dados()
    
    if not df.empty:
        st.subheader("Nível 1: A Visão Geral do Dataset")
        
        st.markdown("### KPIs (Indicadores-Chave de Performance)")
        
        if 'Timestamp' in df.columns and pd.api.types.is_datetime64_any_dtype(df['Timestamp']) and not df['Timestamp'].empty:
            data_inicio = df['Timestamp'].min().strftime('%d/%m/%Y')
            data_fim = df['Timestamp'].max().strftime('%d/%m/%Y')
            st.info(f"Estas são as métricas essenciais que resumem o nosso banco de dados \n\n📅 **Período em Análise:** de {data_inicio} a {data_fim}")
        
        col1, col2, col3, col4 = st.columns(4)
        
        # --- Cálculo das métricas ---
        total_transacoes = df.shape[0]
        total_variaveis = df.shape[1]
        total_fraudes = df['Fraud_Label'].sum()
        taxa_fraude = (total_fraudes / total_transacoes) * 100 if total_transacoes > 0 else 0
        
        with col1:
            st.markdown(f"""
            <div class='kpi-card color-1'>
                <h3>Total de Transações</h3>
                <h2>{total_transacoes:,}</h2>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class='kpi-card color-2'>
                <h3>Total de Variáveis</h3>
                <h2>{total_variaveis}</h2>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class='kpi-card color-3'>
                <h3>Total de Fraudes</h3>
                <h2>{total_fraudes:,}</h2>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
            <div class='kpi-card color-4'>
                <h3>Taxa de Fraude</h3>
                <h2>{taxa_fraude:.2f}%</h2>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        
        st.markdown("#### Detalhes Técnicos do Dataset")
        
        with st.expander("👁️ Visualizar Amostra dos Dados"):
            st.dataframe(df.head(10))
            st.caption("As 10 primeiras linhas do conjunto de dados.")

        with st.expander("📊 Visualizar Resumo Estatístico (Colunas Numéricas)"):
            st.dataframe(df.describe())
            st.caption("Fornece insights como média, mediana e desvio padrão para cada variável numérica.")

        with st.expander("📄 Visualizar Estrutura e Tipos de Dados"):
            tipos_de_dados = pd.DataFrame(df.dtypes, columns=['Tipo de Dado']).reset_index().rename(columns={'index': 'Nome da Coluna'})
            st.dataframe(tipos_de_dados)
            st.caption("Lista de todas as colunas e seus respectivos tipos de dados.")
        
        st.markdown("---")
        
        st.subheader("Nível 2: Análise Univariada (Perfil de Cada Variável)")
        st.markdown("Selecione uma variável para investigar suas características, distribuição e outliers em detalhe.")
        
        colunas_numericas = df.select_dtypes(include=np.number).columns.tolist()
        colunas_categoricas = df.select_dtypes(include=['object', 'category']).columns.tolist()
        colunas_analisaveis = [col for col in df.columns if col != 'Fraud_Label']
        colunas_data = df.select_dtypes(include=['datetime', 'datetimetz', 'datetime64[ns]']).columns.tolist()
        
        coluna_selecionada = st.selectbox(
            "Selecione uma variável para uma análise detalhada:",
            options = colunas_analisaveis,
            index=None,
            placeholder="Escolha uma varíavel..."
        )
        
        if coluna_selecionada:
            if coluna_selecionada in colunas_numericas:
                st.markdown(f"**Analisando a variável numérica:** `{coluna_selecionada}`")
                
                col_grafico, col_stats = st.columns([2, 1])
                
                with col_grafico:
                    fig = px.histogram(df, x=coluna_selecionada, marginal="box", title=f"Distruibuição de '{coluna_selecionada}'")
                    st.plotly_chart(fig, use_container_width=True)
                with col_stats:
                    media = df[coluna_selecionada].mean()
                    mediana = df[coluna_selecionada].median()
                    desvio_pad = df[coluna_selecionada].std()
                    
                    q1 = df[coluna_selecionada].quantile(0.25)
                    q3 = df[coluna_selecionada].quantile(0.75)
                    iqr = q3 - q1
                    limite_inferior = q1 - 1.5 * iqr
                    limite_superior = q3 + 1.5 * iqr
                    outliers = df[(df[coluna_selecionada] < limite_inferior) | (df[coluna_selecionada] > limite_superior)]                    
                    
                    st.markdown(f"<div class='kpi-card color-1'><h3>Média</h3><h2>{media:,.2f}</h2></div>", unsafe_allow_html=True)
                    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='kpi-card color-2'><h3>Mediana</h3><h2>{mediana:,.2f}</h2></div>", unsafe_allow_html=True)
                    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='kpi-card color-3'><h3>Desvio Padrão</h3><h2>{desvio_pad:,.2f}</h2></div>", unsafe_allow_html=True)
                    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='kpi-card color-4'><h3>Nº de Outliers</h3><h2>{len(outliers):,}</h2></div>", unsafe_allow_html=True)
            
            elif coluna_selecionada in colunas_categoricas:
                st.markdown(f"**Analisando a variável categórica:** `{coluna_selecionada}`")
                
                col_grafico_cat, col_stats_cat = st.columns([2, 1])

                with col_grafico_cat:
                    contagem = df[coluna_selecionada].value_counts().nlargest(15).reset_index()
                    contagem.columns = [coluna_selecionada, 'Contagem']
                    fig = px.bar(contagem, x=coluna_selecionada, y='Contagem', title=f"Contagem das 15 categorias mais comuns em '{coluna_selecionada}'")
                    st.plotly_chart(fig, use_container_width=True)
                
                with col_stats_cat:
                    num_categorias = df[coluna_selecionada].nunique()
                    moda = df[coluna_selecionada].mode()[0]
                    
                    st.markdown(f"<div class='kpi-card color-1'><h3>Nº de Categorias Únicas</h3><h2>{num_categorias:,}</h2></div>", unsafe_allow_html=True)
                    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='kpi-card color-2'><h3>Categoria Mais Comum (Moda)</h3><h2>{moda}</h2></div>", unsafe_allow_html=True)
            
            elif coluna_selecionada in colunas_data:
                st.markdown(f"**Analisando a variável de data/hora:** `{coluna_selecionada}`")
        
                st.info("Para variáveis de tempo, visualizamos a contagem de transações por dia.")
        
                transacoes_por_dia = df.set_index(coluna_selecionada).resample('D').size().reset_index(name='Contagem')
        
                fig = px.line(transacoes_por_dia, x=coluna_selecionada, y='Contagem',
                      title=f'Volume de Transações por Dia',
                      labels={'Contagem': 'Número de Transações', coluna_selecionada: 'Data'})
                st.plotly_chart(fig, use_container_width=True)
                
        st.subheader("Nível 3: Investigação das Relações")
        st.markdown("Aqui, cruzamos as variáveis para encontrar padrões e relações, focando em como elas se conectam com a ocorrência de fraude.")
        
        st.markdown("#### Relação de Cada Variável com a Fraude")
        st.info("Selecione uma variável para ver como sua distribuição difere entre transações normais e fraudulentas.")
        
        opcoes_bivariada = [col for col in df.columns if col != 'Fraud_Label']
        feature_to_compare = st.selectbox("Selecione uma variável para comparar:", opcoes_bivariada, key='bivariada_select')

        if feature_to_compare:
            # Lógica para Gráficos Comparativos
            if feature_to_compare in colunas_numericas:
                fig = px.box(df, x='Fraud_Label', y=feature_to_compare, 
                             title=f"Distribuição de '{feature_to_compare}' por Classe de Fraude",
                             labels={'Fraud_Label': 'É Fraude?'}, color='Fraud_Label',
                             color_discrete_map={0: '#636EFA', 1: '#EF553B'})
                st.plotly_chart(fig, use_container_width=True)
            elif feature_to_compare in colunas_categoricas:
                # Usando abas para mostrar contagem absoluta e relativa
                tab1, tab2 = st.tabs(["Contagem Absoluta", "Proporção Relativa (%)"])
                with tab1:
                    fig_abs = px.histogram(df, x=feature_to_compare, color='Fraud_Label', 
                                           barmode='group', title=f"Contagem de '{feature_to_compare}' por Classe de Fraude")
                    st.plotly_chart(fig_abs, use_container_width=True)
                with tab2:
                    fig_rel = px.histogram(df, x=feature_to_compare, color='Fraud_Label', 
                                           barmode='relative', title=f"Proporção de Fraude em '{feature_to_compare}'",
                                           histnorm='percent')
                    st.plotly_chart(fig_rel, use_container_width=True)
            # --- 3.2 Mapa de Calor de Correlação ---
        st.markdown("#### Mapa de Calor de Correlação")
        st.info("Mostra como as variáveis numéricas se relacionam entre si. Valores próximos de 1 (vermelho) ou -1 (azul) indicam forte correlação.")
        
        corr_matrix = df.corr(numeric_only=True)
        fig_corr = px.imshow(corr_matrix, text_auto=".2f", aspect="auto", 
                             title="Mapa de Calor de Correlação", color_continuous_scale='RdBu_r')
        st.plotly_chart(fig_corr, use_container_width=True)

        st.markdown("---")
        st.subheader("Análise de Importância de Variáveis com XGBoost")
        
        def preparar_dados_para_modelo(df):
            df_processado = pd.get_dummies(df.drop(columns=['Transaction_ID', 'User_ID', 'Timestamp']))
            X = df_processado.drop(columns='Fraud_Label')
            y = df_processado['Fraud_Label']
            
            return X, y
        
        def treinar_modelo_xgboost_e_obter_importancias(df):
            X, y = preparar_dados_para_modelo(df)
            
            model = XGBClassifier(n_estimators=100, random_state=42, use_label_encoder=False, eval_metric='logloss')
            model.fit(X, y)
            
            importancias = pd.DataFrame({
                'Variavel': X.columns,
                'Importancia': model.feature_importances_
            }).sort_values(by='Importancia', ascending=False)
            
            return importancias
        
        with st.spinner("Treinando modelo XGBoost para analisar as variáveis..."):
            df_importancias = treinar_modelo_xgboost_e_obter_importancias(df)
        
        #st.success("Análise de importância com XGBoost concluída!")

        top_20_features = df_importancias.head(20)

        fig_importancia = px.bar(
            top_20_features,
            x='Importancia',
            y='Variavel',
            orientation='h',
            title='As 20 Variáveis Mais Importantes (Análise com XGBoost)',
            labels={'Importancia': 'Nível de Importância (Score)', 'Variavel': 'Variável'},
            height=600
        )
        fig_importancia.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_importancia, use_container_width=True)
        
            
elif pagina_atual == "Análise Direcionada":
    st.header("🎯 Análise Direcionada de Fraude")
    st.markdown(
        "Após as descobertas da Análise Exploratória, focamos esta investigação nas variáveis que o modelo "
        "XGBoost apontou como as mais importantes. Vamos aprofundar nosso entendimento sobre os verdadeiros "
        "indicadores de risco."
    )
    
    # --- Carregamento dos dados ---
    @st.cache_data
    def carregar_dados_direcionados():
        df = api.carregar_dados()
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        return df

    df = carregar_dados_direcionados()
    
    st.divider()

    # --- NOVA Hipótese 1: A Anatomia do "Card Testing" ---
    st.subheader("Hipótese 1: Qual o padrão exato das transações falhas?")
    st.markdown(
        "O `Failed_Transaction_Count_7d` foi o fator mais importante. Este gráfico mostra a distribuição "
        "dessa variável **apenas para as transações que foram confirmadas como fraude**, revelando o "
        "comportamento exato do fraudador."
    )
    
    df_fraudes = df[df['Fraud_Label'] == 1]
    
    fig_falhas = px.histogram(
        df_fraudes,
        x='Failed_Transaction_Count_7d',
        title='Distribuição de Falhas Anteriores em Transações Fraudulentas',
        labels={'Failed_Transaction_Count_7d': 'Nº de Transações Falhas nos Últimos 7 Dias'},
        text_auto=True # Mostra a contagem em cima das barras
    )
    fig_falhas.update_layout(yaxis_title="Contagem de Fraudes")
    st.plotly_chart(fig_falhas, use_container_width=True)
    st.info(
        "💡 **Insight:** O gráfico confirma a teoria do 'card testing'. A grande maioria das fraudes ocorre após "
        "exatamente **3 ou 4 tentativas falhas**, sugerindo um padrão de ataque automatizado e previsível."
    )

    st.divider()

    st.subheader("🔬 Análise Profunda do Risk Score: O Indicador Principal")
    st.markdown(
        "Vimos que o `Risk_Score` é uma das variáveis mais importantes. Para visualizar de forma simples "
        "como ele separa as transações, vamos sobrepor os histogramas das duas classes (fraude e não-fraude)."
    )

    # Usamos um histograma com sobreposição para comparar as distribuições
    fig_risk_hist = px.histogram(
        df,
        x="Risk_Score",
        color="Fraud_Label",
        barmode='overlay',
        histnorm='probability density', # Normaliza para comparar as formas das distribuições
        opacity=0.6, # Adiciona transparência para ver a sobreposição
        title="Distribuição da Pontuação de Risco por Classe de Fraude",
        labels={'Risk_Score': 'Pontuação de Risco', 'Fraud_Label': 'É Fraude?'},
        color_discrete_map={0: '#636EFA', 1: '#EF553B'}
    )

    fig_risk_hist.update_layout(
        yaxis_title="Densidade",
        legend_title_text='É Fraude?'
    )
    st.plotly_chart(fig_risk_hist, use_container_width=True)

    st.info(
        """
        💡 **Insight:** Este gráfico simplificado mostra a mesma história de forma direta:
        - **A "montanha" azul (Legítimas)** está quase inteiramente concentrada à esquerda, em valores de `Risk_Score` muito baixos.
        - **A "montanha" vermelha (Fraudes)** está claramente deslocada para a direita, concentrada em valores de `Risk_Score` altos.
        
        A pequena área roxa, onde as duas distribuições se cruzam, representa a "zona de confusão", onde a decisão é mais difícil. A clara separação entre os picos das duas "montanhas" confirma visualmente o imenso poder preditivo desta variável.
        """
    )

elif pagina_atual == "Resumo Estratégico":
    st.header("🏆 Resumo Estratégico e Recomendações Finais")
    st.markdown(
        "Esta seção consolida as descobertas finais do projeto. Após uma análise iterativa, "
        "identificamos os verdadeiros vetores de fraude e descartamos as hipóteses que se provaram "
        "irrelevantes, resultando em um perfil de risco claro e em recomendações estratégicas focadas."
    )
    st.divider()
    
    
    st.subheader("Principais Fatores de Risco e Considerações")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class='kpi-card color-4' style='height: 240px;'>
                <h3>👣 RASTRO COMPORTAMENTAL</h3>
                <h2>Testes de Cartão</h2>
                <p style='font-size: 0.9em;'>O número de falhas recentes é o indicador #1. Um usuário com 3+ falhas em 7 dias representa um alerta máximo de fraude iminente.</p>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown(
            """
            <div class='kpi-card color-3' style='height: 240px;'>
                <h3>🚨 SUPER-SINAL DE RISCO</h3>
                <h2>Risk Score Elevado</h2>
                <p style='font-size: 0.9em;'>Sendo o indicador #2, esta variável sintética é extremamente eficaz, mas sua origem deve ser conhecida para evitar data leakage.</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(
            """
            <div class='kpi-card color-1' style='height: 240px;'>
                <h3>📉 RISCO E DEPENDÊNCIA</h3>
                <h2>Concentração de Risco</h2>
                <p style='font-size: 0.9em;'>A forte dependência em apenas 2 variáveis é eficiente, mas arriscada. O sistema pode ser vulnerável a novos tipos de fraude não capturados por elas.</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()

    st.subheader("O 'Retrato Falado' da Fraude")
    with st.container(border=True):
        st.markdown("""
        A análise revelou um perfil de fraude com características muito específicas, que se concentram mais no **comportamento prévio** do que no contexto da transação em si:

        - **A Impressão Digital do Fraudador:** O sinal mais forte de uma fraude iminente é o comportamento de **'card testing'**. A grande maioria das fraudes é precedida por um número elevado de transações falhas recentes (`Failed_Transaction_Count_7d`), tipicamente entre 3 e 4 falhas.

        - **O Super-Sinal de Risco:** Quase toda transação fraudulenta carrega consigo uma alta **`Pontuação de Risco` (`Risk_Score`)**. Esta variável, provavelmente derivada de um outro modelo, age como um condensador de informações e é o segundo indicador mais poderoso.
        
        - **Fatores Secundários:** Características como o valor da transação e o horário, ao contrário da intuição inicial, provaram ter **baixa ou nenhuma relevância preditiva** isoladamente.
        """)

    st.divider()

    st.subheader("Recomendações Acionáveis para o Negócio")

    with st.expander("**Ação 1: Implementar Monitoramento de 'Card Testing' em Tempo Real**"):
        st.markdown("""
        **A Descoberta:** O número de transações falhas recentes é o indicador mais poderoso de fraude.
        
        **A Solução Sugerida:**
        - Criar regras de negócio que monitorem ativamente a contagem de falhas por cartão ou usuário em janelas curtas de tempo (ex: última hora, últimas 24h).
        - Após um limiar ser atingido (ex: 3 falhas), o sistema deve automaticamente aplicar mais fricção (ex: exigir autenticação de dois fatores - OTP) ou até mesmo bloquear temporariamente o cartão para novas tentativas, notificando o cliente.
        """)

    with st.expander("**Ação 2: Validar e Operacionalizar o `Risk_Score` com Cautela**"):
        st.markdown("""
        **A Observação:** O `Risk_Score` é um "super-sinal", mas sua natureza de "caixa-preta" representa um risco de **vazamento de dados (data leakage)** se não for bem compreendido.
        
        **A Solução Sugerida:**
        - **Auditoria:** Antes de usar este score em produção, é crucial auditar sua origem. A equipe deve garantir que ele seja calculado com dados disponíveis **antes** da transação ser aprovada e que não contenha informações sobre o resultado final da fraude.
        - **Operacionalização:** Se validado, ele deve ser o principal critério para priorizar revisões manuais e para regras de bloqueio automático de transações com scores extremos (ex: > 0.95).
        """)

    with st.expander("**Ação 3: Diversificar Fontes de Dados para Aumentar a Robustez**"):
        st.markdown("""
        **O Risco:** Depender de apenas duas variáveis torna o sistema vulnerável a novos tipos de fraude que não exibam esses dois sinais específicos.
        
        **A Solução Sugerida:**
        - **Engenharia de Features:** Priorizar, em futuras iterações, a criação de novas variáveis. Exemplos: "tempo desde a última transação", "frequência de uso de um novo dispositivo", "relação do valor da transação com a média histórica do usuário".
        - **Análise sem Super-Sinais:** Realizar uma nova rodada de análise **excluindo** `Risk_Score` e `Failed_Transaction_Count_7d` para forçar a descoberta de sinais secundários mais sutis, que podem ser úteis para capturar fraudes mais sofisticadas.
        """)