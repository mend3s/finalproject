# app.py
import numpy as np
# Importa o nosso arquivo 'api_dados.py' e o apelida de 'api'
import func.functions as api
import pandas as pd
import streamlit as st
import streamlit_pills as stp
import seaborn as sns
import matplotlib.pyplot as plt
from func import functions
import plotly.express as px
import plotly.graph_objects as go
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from xgboost import XGBClassifier

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
opcoes_menu = ["Visão Geral", "Analise Exploratoria", "Análise Direcionada", "Resumo Estratégico"]
icones_menu = ["💡", "🔬", "🎯", "🏆"] # 4 opções, 4 ícones

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
    st.markdown("Investigação focada em responder perguntas de negócio específicas sobre os padrões de fraude.")
    
    st.markdown(
            "Analisamos se transações fraudulentas de **alto valor** (`Transaction_Amount`) são mais comuns em "
            "certos **tipos de transação** (`Transaction_Type`), como 'Online', 'POS' (Ponto de Venda) ou 'ATM Withdrawal' (Saque em Caixa Eletrônico)."
        )

    df = api.carregar_dados()
        
    tipos_disponiveis = df['Transaction_Type'].unique()
    tipos_selecionados = st.multiselect(
            'Selecione os tipos de transação para comparar:',
            options=tipos_disponiveis,
            default=list(tipos_disponiveis[:3]) # Padrão para os três primeiros tipos encontrados
    )

    if tipos_selecionados:
        df_filtrado_tipo = df[df['Transaction_Type'].isin(tipos_selecionados)]
            
        fig_tipo = px.box(
            df_filtrado_tipo,
            x='Transaction_Type',
            y='Transaction_Amount',
            color='Fraud_Label',
            title='Distribuição do Valor da Transação por Tipo e Fraude',
            labels={
                "Transaction_Amount": "Valor da Transação (R$)",
                "Transaction_Type": "Tipo da Transação",
                "Fraud_Label": "É Fraude? (0 = Não, 1 = Sim)"
                },
            color_discrete_map={0: '#636EFA', 1: '#EF553B'} # Cores Azul e Vermelho
            )
        fig_tipo.update_layout(yaxis_title="Valor da Transação (R$)")
        st.plotly_chart(fig_tipo, use_container_width=True)
        st.info("💡 **Insight:** Use este gráfico para ver se fraudes de alto valor se concentram em um tipo específico. Por exemplo, fraudes do tipo 'Online' podem ter valores sistematicamente maiores do que as de 'POS'.")

        st.divider()

        # --- Hipótese 2: Existe um "horário nobre" da fraude? ---
        st.subheader("Hipótese 2: As fraudes ocorrem em horários específicos do dia?")
        st.markdown(
            "Verificamos se existe um padrão temporal, investigando se a **ocorrência de fraudes** se concentra "
            "em determinados períodos do dia, como de madrugada, quando a vigilância do titular do cartão é menor."
        )

        df['Hora_do_Dia'] = df['Timestamp'].dt.hour
        
        fig_hora = px.histogram(
            df,
            x='Hora_do_Dia',
            color='Fraud_Label',
            barmode='group',
            title='Contagem de Transações por Hora do Dia',
            labels={
                "Hora_do_Dia": "Hora do Dia (0-23h)",
                "Fraud_Label": "É Fraude? (0 = Não, 1 = Sim)"
            },
            color_discrete_map={0: '#636EFA', 1: '#EF553B'}
        )
        fig_hora.update_layout(xaxis_title="Hora do Dia (0-23h)", yaxis_title="Número de Transações")
        st.plotly_chart(fig_hora, use_container_width=True)
        st.info("💡 **Insight:** Um pico de fraudes na madrugada (ex: entre 1h e 4h da manhã), quando as transações legítimas são baixas, é um forte sinal de atividade suspeita que o modelo pode aprender.")

        st.divider()

        # --- Hipótese 3: A combinação de risco e comportamento indica fraude? ---
        st.subheader("Hipótese 3: Como o risco se relaciona com a frequência de transações?")
        st.markdown(
            "Analisamos a relação entre a **pontuação de risco** (`Risk_Score`) da transação e o **número de transações diárias** "
            "(`Daily_Transaction_Count`) do usuário, para identificar se fraudes ocorrem em um quadrante específico."
        )

        fig_risco_freq = px.scatter(
            df,
            x='Daily_Transaction_Count',
            y='Risk_Score',
            color='Fraud_Label',
            title='Relação entre Frequência Diária e Pontuação de Risco',
            labels={
                "Daily_Transaction_Count": "Nº de Transações no Dia",
                "Risk_Score": "Pontuação de Risco da Transação",
                "Fraud_Label": "É Fraude? (0 = Não, 1 = Sim)"
            },
            color_discrete_map={0: 'rgba(99, 110, 250, 0.5)', 1: 'rgba(239, 85, 59, 0.8)'}, # Azul e Vermelho com transparência
            hover_data=['Transaction_Amount'] # Adiciona informação extra ao passar o mouse
        )
        st.plotly_chart(fig_risco_freq, use_container_width=True)
        st.info("💡 **Insight:** Procure por agrupamentos. É comum que transações fraudulentas (pontos vermelhos) se concentrem na área de alto risco e alta frequência de transações, indicando um comportamento anômalo do usuário.")

elif pagina_atual == "Resumo Estratégico":
    st.header("🏆 Resumo Estratégico e Recomendações")
    st.markdown(
        "Esta seção consolida todos os insights gerados nas fases anteriores. "
        "Aqui, apresentamos o perfil claro da atividade fraudulenta e sugerimos ações "
        "estratégicas para mitigar os riscos identificados."
    )
    st.divider()

    # --- 1. O "Retrato Falado" da Fraude ---
    st.subheader("O 'Retrato Falado' da Fraude")
    with st.container(border=True):
        st.markdown("""
        Com base na análise dos dados, o perfil de uma transação fraudulenta se distingue claramente do comportamento de um cliente legítimo. As principais características são:

        - **Padrão Temporal Anômalo:** A atividade fraudulenta é constante (24/7), o que faz com que sua **proporção seja drasticamente maior durante a madrugada** (entre 0h e 6h), quando a atividade de clientes genuínos é mínima.

        - **Valores Enganosos:** Contrariando a intuição, a maioria das fraudes **não busca valores exorbitantes**. A mediana do valor fraudulento é consistentemente **inferior** à das transações legítimas, possivelmente uma tática para evitar a detecção por sistemas de alerta baseados em limites de valor.

        - **Sinal de Risco Confiável:** A `Pontuação de Risco` (`Risk_Score`) pré-calculada demonstrou ser o **indicador individual mais forte e confiável**. Transações fraudulentas quase invariavelmente apresentam uma pontuação de risco elevada.
        """)

    st.divider()

    # --- 2. Principais Fatores de Risco Identificados ---
    st.subheader("Principais Fatores de Risco em Destaque")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class='kpi-card color-4' style='height: 220px;'>
                <h3>⏰ HORÁRIO CRÍTICO</h3>
                <h2>Madrugada (0h-6h)</h2>
                <p style='font-size: 0.9em;'>Neste período, a atividade legítima cai drasticamente, tornando qualquer transação inerentemente mais suspeita.</p>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown(
            """
            <div class='kpi-card color-3' style='height: 220px;'>
                <h3>🚨 SINAL DE ALERTA</h3>
                <h2>Risk Score Elevado</h2>
                <p style='font-size: 0.9em;'>A Pontuação de Risco é o previsor mais fiel. Valores acima de 0.7 são um forte indicativo de fraude iminente.</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(
            """
            <div class='kpi-card color-2' style='height: 220px;'>
                <h3>💰 PADRÃO INVERTIDO</h3>
                <h2>Valores Baixos/Médios</h2>
                <p style='font-size: 0.9em;'>A estratégia parece ser "voar abaixo do radar" com valores que não chamam atenção imediata.</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()

    # --- 3. Recomendações Acionáveis para o Negócio ---
    st.subheader("Recomendações Acionáveis para o Negócio")

    with st.expander("**Ação 1: Revisar Regras de Alerta para a Madrugada**"):
        st.markdown("""
        **O Problema:** Regras de alerta baseadas apenas em valores altos são ineficazes durante a madrugada, pois as fraudes nesse horário podem ter valores baixos.
        
        **A Solução Sugerida:**
        - Implementar regras de negócio dinâmicas que **aumentem a sensibilidade durante a madrugada**.
        - Exemplo: Uma transação 'Online' de R$150,00 às 14h pode ser normal, mas a mesma transação às 3h da manhã deve, automaticamente, ter seu risco elevado e, potencialmente, ser direcionada para uma verificação adicional (como envio de OTP).
        """)

    with st.expander("**Ação 2: Adotar a Pontuação de Risco como Fator Crítico de Decisão**"):
        st.markdown("""
        **A Observação:** A variável `Risk_Score` é o indicador mais confiável encontrado nesta análise.
        
        **A Solução Sugerida:**
        - **Priorização de Revisão:** A equipe de análise de fraude deve usar o `Risk_Score` como principal critério de fila. Todas as transações com score acima de um limiar (ex: 0.75) devem ser revisadas primeiro.
        - **Bloqueio Automático:** Considerar a implementação de bloqueios automáticos para transações que excedam um limiar de risco extremo (ex: 0.95), prevenindo a perda antes mesmo da revisão humana.
        """)

    with st.expander("**Ação 3: Desenvolver Estratégias de Prevenção por Canal**"):
        st.markdown("""
        **O Contexto:** A análise mostrou que os padrões de valor, embora sigam uma tendência geral, têm nuances diferentes para cada tipo de transação ('POS', 'Online', etc.).
        
        **A Solução Sugerida:**
        - Não tratar todos os canais da mesma forma. A equipe de produto ou risco deve analisar estes insights para criar políticas de segurança específicas por canal.
        - Exemplo: Para transações 'Online', onde os outliers de fraude foram mais altos, pode ser necessário um passo de autenticação adicional (biometria, OTP) com mais frequência do que para transações 'POS'.
        """)