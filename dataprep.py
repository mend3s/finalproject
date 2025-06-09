import sqlite3
import pandas as pd


csv_file_path = r'C:\Users\mendes\Documents\GitHub\finalproject\datafile\synthetic_fraud_dataset.csv'

# Nome do banco de dados que será criado.
db_file_path = 'creditdata.db'

# Nome da tabela única que conterá todos os dados.
table_name = 'TransacoesCompletas'
 # --- Passo 1: Puxar os dados do CSV ---
print(f"Lendo dados do arquivo '{csv_file_path}'...")
    # Adicionado encoding='latin-1' para compatibilidade.
df = pd.read_csv(csv_file_path, encoding='latin-1')
print("Dados lidos com sucesso!")

    # --- Passo 2: Conectar ao banco de dados ---
    # O arquivo do banco será criado se ele não existir.
conn = sqlite3.connect(db_file_path)
print(f"Conexão com o banco de dados '{db_file_path}' estabelecida.")

    # --- Passo 3: Criar a tabela e popular com os dados ---
    # O comando 'to_sql' faz tudo de uma vez:
    # - Cria a tabela com as colunas do arquivo CSV.
    # - Insere todos os dados na tabela.
    # if_exists='replace': se a tabela já existir, ela será substituída.
print(f"Criando e populando a tabela única '{table_name}'...")
df.to_sql(table_name, conn, if_exists='replace', index=False)
    
    # Confirma a gravação dos dados no arquivo do banco.
conn.commit()
print("Tabela populada com sucesso!")

    # Verificação final (opcional).
num_rows = pd.read_sql(f'SELECT COUNT(*) FROM {table_name}', conn).iloc[0,0]
print(f"Verificação: A tabela '{table_name}' agora contém {num_rows} linhas.")