import streamlit as st

page1 = st.Page("Producao_Diaria.py", title="Produção Diária", icon="📊")
page2 = st.Page("Producao_Mensal.py", title="Produção Mensal", icon="📊")

pg = st.navigation([page1,page2])
pg.run()
