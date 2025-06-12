# Arquivo: etl.py
import pandas as pd
from sqlalchemy import create_engine
import time

# --- CONFIGURAÇÕES ---
DB_URL = "sqlite:///creditdata.db"
NOME_TABELA_ORIGEM = "TransacoesCompletas"  # Nome da sua tabela com dados brutos
NOME_TABELA_DESTINO = "analytics_dashboard" # Tabela otimizada que o dashboard vai usar

def extrair_dados(engine):
    """Extrai os dados da tabela de origem."""
    print("Iniciando Extração (Extract)...")
    try:
        df = pd.read_sql(f"SELECT * FROM {NOME_TABELA_ORIGEM}", engine)
        print(f"Sucesso! {len(df)} registros extraídos.")
        return df
    except Exception as e:
        print(f"ERRO na extração: {e}")
        return None

def transformar_dados(df):
    """Aplica todas as transformações e cálculos pesados aqui."""
    if df is None or df.empty:
        print("Nenhum dado para transformar.")
        return None
        
    print("Iniciando Transformação (Transform)...")
    
    # Garante que a coluna de data é do tipo datetime
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    
    # --- Feature Engineering: Crie aqui todas as colunas que seu dashboard precisa ---
    df['Hora_do_Dia'] = df['Timestamp'].dt.hour
    df['Dia_da_Semana'] = df['Timestamp'].dt.dayofweek # 0=Segunda, 6=Domingo
    df['Mes'] = df['Timestamp'].dt.month
    
    # Exemplo de uma transformação mais complexa: Média de gastos do usuário até aquela data
    # ATENÇÃO: pode ser lento para datasets muito grandes
    # df.sort_values(by=['User_ID', 'Timestamp'], inplace=True)
    # df['Media_Gasto_Usuario'] = df.groupby('User_ID')['Transaction_Amount'].expanding().mean().reset_index(level=0, drop=True)

    # Garante que a coluna de fraude seja numérica
    if 'Fraud_Label' in df.columns:
        df['Fraud_Label'] = df['Fraud_Label'].astype(int)

    print("Sucesso! Dados transformados e enriquecidos.")
    return df

def carregar_dados(df, engine):
    """Carrega o DataFrame transformado em uma nova tabela no banco."""
    if df is None:
        print("Nenhum dado para carregar.")
        return
        
    print(f"Iniciando Carga (Load) para a tabela '{NOME_TABELA_DESTINO}'...")
    try:
        # O parâmetro if_exists='replace' apaga a tabela antiga e cria uma nova.
        # Isso garante que os dados estejam sempre atualizados após a execução do script.
        df.to_sql(NOME_TABELA_DESTINO, engine, if_exists='replace', index=False)
        print("Sucesso! Tabela otimizada criada/atualizada.")
    except Exception as e:
        print(f"ERRO na carga: {e}")

if __name__ == "__main__":
    print("--- Iniciando processo de ETL ---")
    start_time = time.time()
    
    db_engine = create_engine(DB_URL)
    
    # Executa os 3 passos
    dados_brutos = extrair_dados(db_engine)
    dados_transformados = transformar_dados(dados_brutos)
    carregar_dados(dados_transformados, db_engine)
    
    end_time = time.time()
    print(f"--- Processo de ETL concluído em {end_time - start_time:.2f} segundos ---")