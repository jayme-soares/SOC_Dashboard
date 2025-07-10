import streamlit as st
from datetime import datetime
import pytz
from PIL import Image

# --- Configuração da Página ---
st.set_page_config(
    page_title="Home",
    page_icon="📊",
    layout="wide"
)
image = Image.open("imagens/ceneged_cover.jpeg")
st.image(image, use_container_width =True)

col1, col2, col3 = st.columns(3)

with col1:
    data_atual = datetime.now().strftime("%d-%m-%y")
    st.subheader(data_atual)
with col2:
    st.empty()
with col2:
    st.empty()
with col3:
    timezone = pytz.timezone('America/Sao_Paulo')
    hora_atual = datetime.now(timezone).strftime("%H:%M")
    st.subheader(hora_atual)
st.markdown("----")
    
st.title("Seja bem-vindo(a)!")
st.subheader("Use o menu ao lado para navegar...")

