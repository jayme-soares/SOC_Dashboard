import streamlit as st

page1 = st.Page("Producao_Diaria.py", title="Produção Diária", icon="📊", layout="wide")
page2 = st.Page("Producao_Mensal.py", title="Produção Mensal", icon="📊", layout="wide")

pg = st.navigation([page1,page2])
pg.run()
