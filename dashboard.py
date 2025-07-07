import streamlit as st

st.set_page_config(
    page_title="Parcial SOC - Maricá",
    page_icon="📊",
    layout="wide"
)

page1 = st.Page("pages/Home.py")
page2 = st.Page("pages/1_Producao_Diaria.py")
page3 = st.Page("pages/2_Producao_Mensal.py")

pg = st.navigation([page1,page2, page3])
pg.run()
