import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

conn = sqlite3.connect("aviao.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
''')