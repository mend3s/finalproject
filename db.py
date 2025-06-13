import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns


conn = sqlite3.connect("dados_voo.db")
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS empresa (
    empresa_sigla TEXT PRIMARY KEY,
    empresa_nome TEXT NOT NULL,
    empresa_nacionalidade TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS aeroporto (
    aeroporto_sigla TEXT PRIMARY KEY,
    aeroporto_nome TEXT NOT NULL,
    aeroporto_uf TEXT,
    aeroporto_regiao TEXT,
    aeroporto_pais TEXT NOT NULL,
    aeroporto_continente TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS voo (
    voo_id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_sigla TEXT NOT NULL,
    ano INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    aeroporto_origem_sigla TEXT NOT NULL,
    aeroporto_destino_sigla TEXT NOT NULL,
    natureza TEXT NOT NULL,
    grupo_voo TEXT NOT NULL,
    distancia_voada_km REAL NOT NULL,
    combustivel_litros REAL NOT NULL,
    decolagens INTEGER NOT NULL,
    horas_voadas REAL NOT NULL,
    FOREIGN KEY (empresa_sigla) REFERENCES empresa(empresa_sigla),
    FOREIGN KEY (aeroporto_origem_sigla) REFERENCES aeroporto(aeroporto_sigla),
    FOREIGN KEY (aeroporto_destino_sigla) REFERENCES aeroporto(aeroporto_sigla)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS voo_nacional (
    voo_id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_sigla TEXT NOT NULL,
    ano INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    aeroporto_origem_sigla TEXT NOT NULL,
    aeroporto_destino_sigla TEXT NOT NULL,
    grupo_voo TEXT NOT NULL,
    distancia_voada_km REAL NOT NULL,
    combustivel_litros REAL NOT NULL,
    decolagens INTEGER NOT NULL,
    horas_voadas REAL NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS voo_internacional (
    voo_id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_sigla TEXT NOT NULL,
    ano INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    aeroporto_origem_sigla TEXT NOT NULL,
    aeroporto_destino_sigla TEXT NOT NULL,
    grupo_voo TEXT NOT NULL,
    distancia_voada_km REAL NOT NULL,
    combustivel_litros REAL NOT NULL,
    decolagens INTEGER NOT NULL,
    horas_voadas REAL NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS carga_passageiros (
    voo_id INTEGER PRIMARY KEY AUTOINCREMENT,
    passageiros_pagos INTEGER NOT NULL,
    passageiros_gratis INTEGER NOT NULL,
    bagagem_kg REAL NOT NULL,
    carga_paga_kg REAL NOT NULL,
    carga_gratis_kg REAL NOT NULL,
    correio_kg REAL NOT NULL,
    carga_paga_km REAL NOT NULL,
    carga_gratis_km REAL NOT NULL,
    correio_km REAL NOT NULL,
    FOREIGN KEY (voo_id) REFERENCES voo(voo_id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS metricas_desempenho (
    voo_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ASK REAL NOT NULL,
    RPK REAL NOT NULL,
    ATK REAL NOT NULL,
    RTK REAL NOT NULL,
    assentos INTEGER NOT NULL,
    payload REAL NOT NULL,
    FOREIGN KEY (voo_id) REFERENCES voo(voo_id)
)
''')

# Carregando dados
df = pd.read_csv("resumo_anual_2025_tratado.csv", delimiter=';', encoding='utf-8')

df.fillna({
    'DISTÂNCIA VOADA (KM)': 0, 
    'COMBUSTÍVEL (LITROS)': 0,
    'DECOLAGENS': 0,
    'HORAS VOADAS': 0,
    'PASSAGEIROS PAGOS': 0,
    'PASSAGEIROS GRÁTIS': 0,
    'BAGAGEM (KG)': 0,
    'CARGA PAGA (KG)': 0,
    'CARGA GRÁTIS (KG)': 0,
    'CORREIO (KG)': 0,
    'CARGA PAGA KM': 0,
    'CARGA GRATIS KM': 0,
    'CORREIO KM': 0,
    'ASK': 0,
    'RPK': 0,
    'ATK': 0,
    'RTK': 0,
    'ASSENTOS': 0,
    'PAYLOAD': 0
}, inplace=True)

# Populando tabelas
for _, row in df.iterrows():
    cursor.execute('''
    INSERT OR IGNORE INTO empresa (empresa_sigla, empresa_nome, empresa_nacionalidade)
    VALUES (?, ?, ?)
    ''', (row['EMPRESA (SIGLA)'], row['EMPRESA (NOME)'], row['EMPRESA (NACIONALIDADE)']))

for _, row in df.iterrows():
    cursor.execute('''
    INSERT OR IGNORE INTO aeroporto (aeroporto_sigla, aeroporto_nome, aeroporto_uf, aeroporto_regiao, aeroporto_pais, aeroporto_continente)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (row['AEROPORTO DE ORIGEM (SIGLA)'], row['AEROPORTO DE ORIGEM (NOME)'], row['AEROPORTO DE ORIGEM (UF)'], 
          row['AEROPORTO DE ORIGEM (REGIÃO)'], row['AEROPORTO DE ORIGEM (PAÍS)'], row['AEROPORTO DE ORIGEM (CONTINENTE)']))

    cursor.execute('''
    INSERT OR IGNORE INTO aeroporto (aeroporto_sigla, aeroporto_nome, aeroporto_uf, aeroporto_regiao, aeroporto_pais, aeroporto_continente)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (row['AEROPORTO DE DESTINO (SIGLA)'], row['AEROPORTO DE DESTINO (NOME)'], row['AEROPORTO DE DESTINO (UF)'], 
          row['AEROPORTO DE DESTINO (REGIÃO)'], row['AEROPORTO DE DESTINO (PAÍS)'], row['AEROPORTO DE DESTINO (CONTINENTE)']))

for _, row in df.iterrows():
    cursor.execute('''
    INSERT INTO voo (empresa_sigla, ano, mes, aeroporto_origem_sigla, aeroporto_destino_sigla, natureza, grupo_voo, distancia_voada_km, combustivel_litros, decolagens, horas_voadas)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (row['EMPRESA (SIGLA)'], row['ANO'], row['MÊS'], row['AEROPORTO DE ORIGEM (SIGLA)'], row['AEROPORTO DE DESTINO (SIGLA)'], row['NATUREZA'],
          row['GRUPO DE VOO'], row['DISTÂNCIA VOADA (KM)'], row['COMBUSTÍVEL (LITROS)'], row['DECOLAGENS'], row['HORAS VOADAS']))

for _, row in df.iterrows():
    cursor.execute('''
    INSERT INTO carga_passageiros (passageiros_pagos, passageiros_gratis, bagagem_kg, carga_paga_kg, carga_gratis_kg, correio_kg, carga_paga_km, carga_gratis_km, correio_km)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?,?)
    ''', (row['PASSAGEIROS PAGOS'], row['PASSAGEIROS GRÁTIS'], row['BAGAGEM (KG)'], row['CARGA PAGA (KG)'], row['CARGA GRÁTIS (KG)'], row['CORREIO (KG)'],
          row['CARGA PAGA KM'], row['CARGA GRATIS KM'], row['CORREIO KM']))

for _, row in df.iterrows():
    cursor.execute('''
    INSERT INTO metricas_desempenho (ASK, RPK, ATK, RTK, assentos, payload)
    VALUES (?, ?, ?, ?, ?, ? )
    ''', (row['ASK'], row['RPK'], row['ATK'], row['RTK'], row['ASSENTOS'], row['PAYLOAD']))


for _, row in df.iterrows():
    if row['NATUREZA'] == 'DOMÉSTICA':
        cursor.execute('''
        INSERT INTO voo_nacional (empresa_sigla, ano, mes, aeroporto_origem_sigla, aeroporto_destino_sigla, grupo_voo, distancia_voada_km, combustivel_litros, decolagens, horas_voadas)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (row['EMPRESA (SIGLA)'], row['ANO'], row['MÊS'], row['AEROPORTO DE ORIGEM (SIGLA)'], row['AEROPORTO DE DESTINO (SIGLA)'], 
              row['GRUPO DE VOO'], row['DISTÂNCIA VOADA (KM)'], row['COMBUSTÍVEL (LITROS)'], row['DECOLAGENS'], row['HORAS VOADAS']))
    
    elif row['NATUREZA'] == 'INTERNACIONAL':
        cursor.execute('''
        INSERT INTO voo_internacional (empresa_sigla, ano, mes, aeroporto_origem_sigla, aeroporto_destino_sigla, grupo_voo, distancia_voada_km, combustivel_litros, decolagens, horas_voadas)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (row['EMPRESA (SIGLA)'], row['ANO'], row['MÊS'], row['AEROPORTO DE ORIGEM (SIGLA)'], row['AEROPORTO DE DESTINO (SIGLA)'], 
              row['GRUPO DE VOO'], row['DISTÂNCIA VOADA (KM)'], row['COMBUSTÍVEL (LITROS)'], row['DECOLAGENS'], row['HORAS VOADAS']))


conn.commit()
conn.close()
