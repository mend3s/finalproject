import pandas as pd
import sqlite3

def carregar_dados():
    """
    Conecta ao banco de dados SQLite e carrega a tabela de transações.
    Esta função é o único ponto de contato com o banco de dados.
    """
    try:
        # Conecta ao banco de dados criado pelo script de preparação.
        conn = sqlite3.connect('analise_simples.db')
        # Carrega a tabela única que contém todos os dados.
        df = pd.read_sql_query("SELECT * FROM TransacoesCompletas", conn)
        conn.close()
        # Converte a coluna de data para o formato datetime, essencial para filtros.
        # Certifique-se de que o nome da coluna 'Timestamp' corresponde ao seu arquivo.
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        return df
    except Exception as e:
        # Retorna um DataFrame vazio se o banco ou a tabela não forem encontrados.
        print(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

def calcular_kpis_seguranca(df):
    """
    Calcula os principais indicadores de segurança (KPIs) a partir de um DataFrame.
    Recebe um DataFrame (geralmente já filtrado) e retorna um dicionário com os KPIs.
    """
    if df.empty:
        # Retorna valores padrão se o DataFrame estiver vazio para evitar erros.
        return {
            'total_transacoes': 0, 'total_fraudes': 0, 'taxa_fraude': 0,
            'valor_perdido': 0, 'alertas_ip': 0
        }

    total_transacoes = len(df)
    total_fraudes = int(df['Fraud_Label'].sum())
    taxa_fraude = (total_fraudes / total_transacoes * 100) if total_transacoes > 0 else 0
    valor_perdido = df[df['Fraud_Label'] == 1]['Transaction_Amount'].sum()
    alertas_ip = int(df['IP_Address_Flag'].sum())

    return {
        'total_transacoes': total_transacoes,
        'total_fraudes': total_fraudes,
        'taxa_fraude': taxa_fraude,
        'valor_perdido': valor_perdido,
        'alertas_ip': alertas_ip
    }

def preparar_dados_graficos(df):
    """
    Prepara e agrega os dados para os gráficos do dashboard.
    """
    if df.empty:
        # Retorna DataFrames vazios se não houver dados.
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    # Dados para o Gráfico de Barras: Fraudes por Tipo de Transação
    fraudes_por_tipo = df[df['Fraud_Label'] == 1]['Transaction_Type'].value_counts().reset_index()
    fraudes_por_tipo.columns = ['Tipo de Transação', 'Quantidade de Fraudes']

    # Dados para o Gráfico de Barras Horizontais: Top 10 Categorias de Mercante com Fraude
    fraudes_por_mercante = df[df['Fraud_Label'] == 1]['Merchant_Category'].value_counts().nlargest(10).reset_index()
    fraudes_por_mercante.columns = ['Categoria de Mercante', 'Quantidade de Fraudes']

    # Dados para o Gráfico de Linha: Transações e Fraudes ao Longo do Tempo
    df_temporal = df.set_index('Timestamp').resample('D').agg(
        total_transacoes=('Transaction_ID', 'count'),
        total_fraudes=('Fraud_Label', 'sum')
    ).reset_index()

    return fraudes_por_tipo, fraudes_por_mercante, df_temporal
