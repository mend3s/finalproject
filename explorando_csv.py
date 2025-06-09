import pandas as pd

df = pd.read_csv('creditcard_2023.csv')

# Visualizar as 5 primeiras linhas para ter uma noção geral
print("\n 5 primeiras transações do dataset:")
print(df.head())

print("\n Informaçoes do dataframe, tipos de dados e contagem de não nulos")
df.info()

print(f"\nO dataset possui {df.shape[0]} linhas e {df.shape[1]} colunas.")

print("\n Contagem de valores nulos (ausentes) por coluna:")
print(df.isnull().sum())

num_duplicatas = df.duplicated().sum()
print(f"\n▶️ Número de transações duplicadas encontradas: {num_duplicatas}")

print("\n▶️ Estatísticas descritivas (ajuda a identificar outliers e problemas de escala):")
print(df.describe())

print("\n▶️ Distribuição das classes (0: Não Fraude, 1: Fraude):")
print(df['Class'].value_counts())