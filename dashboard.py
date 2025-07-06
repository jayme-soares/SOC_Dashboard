import streamlit as st

page1 = st.Page("Producao_Diaria.py")
page2 = st.Page("Producao_Mensal.py")

pg = st.navigation([page1,page2])
pg.run()
