import pandas as pd
import streamlit as st
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("resumo_anual_2025.csv", delimiter=';', encoding='latin')

print(df)