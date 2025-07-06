import streamlit as st

page1 = st.Page("1_Producao_Diaria.py")
page2 = st.Page("2_Producao_Mensal.py")

pg = st.navigation([page1,page2])
pg.run()
