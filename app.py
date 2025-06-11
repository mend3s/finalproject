# app.py
import numpy as np
# Importa o nosso arquivo 'api_dados.py' e o apelida de 'api'
import func.functions as api
# --- Configuração da Página ---
import pandas as pd
import streamlit as st
import streamlit_pills as stp
import seaborn as sns
import matplotlib.pyplot as plt
from func import functions  # Removido se 'functions' não estiver sendo usado ainda
import sqlite3
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
opcoes_menu = ["Visão Geral", "Analise Exploratoria", "Análise Direcionada", "Modelagem Preditiva"]
icones_menu = ["💡", "🔬", "🎯", "⚙️"] # 4 opções, 4 ícones

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


# --- Conteúdo das Páginas (Estrutura Corrigida e Completa) ---
# CORREÇÃO 2: A estrutura if/elif agora corresponde exatamente às opções do menu.
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
        
        # --------------------------------------------------------------------------
        # ADAPTAÇÃO PARA OS CARDS CUSTOMIZADOS
        # --------------------------------------------------------------------------
        
        col1, col2, col3, col4 = st.columns(4)
        
        # --- Cálculo das métricas ---
        total_transacoes = df.shape[0]
        total_variaveis = df.shape[1]
        total_fraudes = df['Fraud_Label'].sum()
        taxa_fraude = (total_fraudes / total_transacoes) * 100 if total_transacoes > 0 else 0
        
        # --- Renderização dos cards usando st.markdown e f-strings ---
        
        # Card 1: Total de Transações
        with col1:
            st.markdown(f"""
            <div class='kpi-card color-1'>
                <h3>Total de Transações</h3>
                <h2>{total_transacoes:,}</h2>
            </div>
            """, unsafe_allow_html=True)

        # Card 2: Total de Variáveis
        with col2:
            st.markdown(f"""
            <div class='kpi-card color-2'>
                <h3>Total de Variáveis</h3>
                <h2>{total_variaveis}</h2>
            </div>
            """, unsafe_allow_html=True)

        # Card 3: Total de Fraudes
        with col3:
            st.markdown(f"""
            <div class='kpi-card color-3'>
                <h3>Total de Fraudes</h3>
                <h2>{total_fraudes:,}</h2>
            </div>
            """, unsafe_allow_html=True)

        # Card 4: Taxa de Fraude
        with col4:
            st.markdown(f"""
            <div class='kpi-card color-4'>
                <h3>Taxa de Fraude</h3>
                <h2>{taxa_fraude:.2f}%</h2>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        
        # --- Detalhes Técnicos em Expanders ---
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
        
            # A melhor forma de visualizar é agregar as transações ao longo do tempo.
                st.info("Para variáveis de tempo, visualizamos a contagem de transações por dia.")
        
            # Agrupa as transações por dia
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
    st.info("Espaço reservado para os gráficos da Análise Direcionada: Análise por Canal, Contexto, Comportamento, etc.")

elif pagina_atual == "Modelagem Preditiva":
    # Adicionada a condição que faltava.
    st.header("⚙️ Modelagem Preditiva")
    st.markdown("Construção e avaliação de modelos de Machine Learning para prever transações fraudulentas.")
    st.info("Espaço reservado para os resultados da Modelagem Preditiva: Matriz de Confusão, Curva ROC, etc.")