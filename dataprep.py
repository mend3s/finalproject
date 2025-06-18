import sqlite3
import pandas as pd


csv_file_path = r'C:\Users\mendes\Documents\GitHub\finalproject\datafile\synthetic_fraud_dataset.csv'

# Nome do banco de dados
db_file_path = 'creditdata.db'

# Nome da tabela
table_name = 'TransacoesCompletas'
 #Puxar os dados do CSV
print(f"Lendo dados do arquivo '{csv_file_path}'...")
  
df = pd.read_csv(csv_file_path, encoding='latin-1')
print("Dados lidos com sucesso!")

# O arquivo do banco será criado se ele não existir.
conn = sqlite3.connect(db_file_path) #esse connect liga o banco
print(f"Conexão com o banco de dados '{db_file_path}' estabelecida.")


# O comando 'to_sql' faz tudo (cria e popula os dados) 
# if_exists='replace': se a tabela já existir, ela será substituída.
print(f"Criando e populando a tabela única '{table_name}'...")
df.to_sql(table_name, conn, if_exists='replace', index=False)
    
    # Confirma a gravação 
conn.commit()
print("Tabela populada com sucesso!")

