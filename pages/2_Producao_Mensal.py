# Importando as bibliotecas necessárias
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, timedelta
import locale
import base64
import io

# --- Configuração da Página ---
st.set_page_config(
    page_title="Produção Mensal SOC - Maricá",
    page_icon="📊",
    layout="wide"
)

# --- Carregamento e Limpeza dos Dados a partir de um Secret ---
@st.cache_data
def carregar_dados_de_secret(base64_string):
    """
    Carrega dados a partir de uma string Base64 armazenada nos Secrets.
    """
    try:
        # Decodifica a string Base64 de volta para bytes
        decoded_bytes = base64.b64decode(base64_string)
        # Lê os bytes como um arquivo em memória
        df = pd.read_excel(io.BytesIO(decoded_bytes))
        
        # Padroniza as colunas de texto para maiúsculas e remove espaços extras
        colunas_para_padronizar = ['Setor', 'Chefe/Responsável de Equipe', 'Resultado', 'Serviço', 'Tipo Operação']
        
        for col in colunas_para_padronizar:
            if col in df.columns:
                df[col] = df[col].astype(str)
                df[col] = df[col].str.strip().str.replace(r'\s+', ' ', regex=True).str.upper()   
        return df
    except Exception as e:
        st.error(f"Ocorreu um erro ao processar os dados do secret: {e}")
        return None

# --- Interface Principal do Dashboard ---

# Define o locale para português do Brasil para obter o nome do mês corretamente
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except locale.Error:
    st.warning("Locale 'pt_BR.UTF-8' não encontrado. O nome do mês pode aparecer em inglês.")

# Calcula o mês anterior
hoje = date.today()
primeiro_dia_mes_atual = hoje.replace(day=1)
mes_anterior_date = primeiro_dia_mes_atual - timedelta(days=1)
mes_referencia = mes_anterior_date.strftime("%B/%Y").capitalize()

st.title(f"SOC Maricá - Produção Mensal")
st.title(f"{mes_referencia})")
# --- Carregamento a partir dos Secrets do Streamlit ---
df_original = None
try:
    # Tenta carregar os dados a partir do secret "EXCEL_BASE64"
    df_original = carregar_dados_de_secret(st.secrets["EXCEL_BASE64"])
except (KeyError, FileNotFoundError):
    st.error("Secret 'EXCEL_BASE64' não encontrado. Por favor, configure os secrets nas configurações do seu app no Streamlit Cloud.")

# A execução do script continua apenas se o dataframe for carregado com sucesso.
if df_original is not None:
    st.sidebar.header("Filtros Globais")
    
    # Filtro por Setor
    setores_disponiveis = ['TODOS'] + df_original['Setor'].dropna().unique().tolist()
    setores_selecionados = st.sidebar.multiselect("Setor", setores_disponiveis, default=['TODOS'])

    # Filtro por Equipe
    equipes_disponiveis = ['TODOS'] + df_original['Chefe/Responsável de Equipe'].dropna().unique().tolist()
    equipes_selecionadas = st.sidebar.multiselect("Equipe", equipes_disponiveis, default=['TODOS'])

    # Filtro por Resultado
    resultados_disponiveis = ['TODOS'] + df_original['Resultado'].dropna().unique().tolist()
    resultados_selecionados = st.sidebar.multiselect("Resultado", resultados_disponiveis, default=['TODOS'])

    # Aplica os filtros ao dataframe
    df_filtrado = df_original.copy()
    if 'TODOS' not in setores_selecionados:
        df_filtrado = df_filtrado[df_filtrado['Setor'].isin(setores_selecionados)]
    if 'TODOS' not in equipes_selecionadas:
        df_filtrado = df_filtrado[df_filtrado['Chefe/Responsável de Equipe'].isin(equipes_selecionadas)]
    if 'TODOS' not in resultados_selecionados:
        df_filtrado = df_filtrado[df_filtrado['Resultado'].isin(resultados_selecionados)]

    # Tabela de dados expansível
    with st.expander("Exibir/Ocultar Tabela de Dados"):
        st.dataframe(df_filtrado)

    st.markdown("---")
    # --- CARTÕES DE INDICADORES (KPIs) ---
    total_atividades = len(df_filtrado)
    total_produtivo = df_filtrado[df_filtrado['Resultado'] == 'PRODUTIVO'].shape[0]
    total_improdutivo = df_filtrado[df_filtrado['Resultado'] == 'IMPRODUTIVO'].shape[0]
    taxa_produtividade = (total_produtivo / total_atividades * 100) if total_atividades > 0 else 0

    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric(label="Total de Atividades", value=f"{total_atividades}")
    kpi2.metric(label="Total Produtivo", value=f"{total_produtivo}")
    kpi3.metric(label="Taxa de Produtividade", value=f"{taxa_produtividade:.2f}%")

    st.markdown("---")
    
    col1, col2 = st.columns(2)

    # Coluna 1: Gráfico de Produtividade por Equipe (com filtro individual)
    with col1:
        st.subheader("Produtividade por Equipe")
        if not df_filtrado.empty and 'Chefe/Responsável de Equipe' in df_filtrado.columns:
            
            lista_equipes_grafico = ['TODAS AS EQUIPES'] + df_filtrado['Chefe/Responsável de Equipe'].dropna().unique().tolist()
            equipe_selecionada_grafico = st.selectbox('Detalhar por Equipe:', options=lista_equipes_grafico, key='select_equipe_individual')

            df_para_grafico_equipe = df_filtrado
            if equipe_selecionada_grafico != 'TODAS AS EQUIPES':
                df_para_grafico_equipe = df_filtrado[df_filtrado['Chefe/Responsável de Equipe'] == equipe_selecionada_grafico]

            produtividade_equipe = df_para_grafico_equipe.groupby('Chefe/Responsável de Equipe')['Resultado'].value_counts().unstack().fillna(0)
            fig = px.bar(produtividade_equipe, barmode='group', text_auto=True, color_discrete_map={'PRODUTIVO': 'royalblue', 'IMPRODUTIVO': 'darkorange'}, title="Produtividade por Equipe")
            fig.update_layout(xaxis_title=None, yaxis_title="Qtd. Atividades", legend_title="Resultado")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Nenhum dado para exibir com os filtros atuais.")

    # Coluna 2: Gráfico de Produtividade por Setor (com filtro individual)
    with col2:
        st.subheader("Produtividade por Setor")
        if not df_filtrado.empty and 'Setor' in df_filtrado.columns:

            lista_setores_grafico = ['TODOS OS SETORES'] + df_filtrado['Setor'].dropna().unique().tolist()
            setor_selecionado_grafico = st.selectbox('Detalhar por Setor:', options=lista_setores_grafico, key='select_setor_individual')

            df_para_grafico_setor = df_filtrado
            if setor_selecionado_grafico != 'TODOS OS SETORES':
                df_para_grafico_setor = df_filtrado[df_filtrado['Setor'] == setor_selecionado_grafico]
            
            titulo_grafico = f'Produtividade para: {setor_selecionado_grafico}' if setor_selecionado_grafico != 'TODOS OS SETORES' else 'Produtividade (Todos os Setores Filtrados)'
            
            produtividade_setor = df_para_grafico_setor['Resultado'].value_counts().reset_index()
            produtividade_setor.columns = ['Resultado', 'Contagem']

            fig = px.pie(produtividade_setor, names='Resultado', values='Contagem', title=titulo_grafico, color='Resultado', color_discrete_map={'PRODUTIVO': 'royalblue', 'IMPRODUTIVO': 'darkorange'})
            fig.update_traces(textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Nenhum dado para exibir com os filtros atuais.")

    st.markdown("---")

    # --- Layout em Colunas para as Tabelas de Resumo ---
    col3, col4 = st.columns(2)

    # Coluna 3: Tabela de Resumo por Equipe
    with col3:
        st.subheader("Resumo por Equipe")
        if not df_filtrado.empty and all(col in df_filtrado.columns for col in ['Chefe/Responsável de Equipe', 'Resultado']):
            resumo_equipe = pd.pivot_table(df_filtrado, index=['Chefe/Responsável de Equipe'], columns='Resultado', aggfunc='size', fill_value=0)
            if 'PRODUTIVO' not in resumo_equipe: resumo_equipe['PRODUTIVO'] = 0
            if 'IMPRODUTIVO' not in resumo_equipe: resumo_equipe['IMPRODUTIVO'] = 0
            resumo_equipe['Total Geral'] = resumo_equipe.sum(axis=1)
            
            altura_tabela = (len(resumo_equipe.index) + 1) * 35 + 3
            st.dataframe(resumo_equipe[['PRODUTIVO', 'IMPRODUTIVO', 'Total Geral']], height=altura_tabela)
        else:
            st.warning("Nenhum dado para exibir com os filtros atuais.")

    # Coluna 4: Tabela de Resumo por Serviço
    with col4:
        st.subheader("Resumo por Serviço")
        if not df_filtrado.empty and all(col in df_filtrado.columns for col in ['Serviço', 'Resultado']):
            resumo_servico = pd.pivot_table(df_filtrado, index=['Serviço'], columns='Resultado', aggfunc='size', fill_value=0)
            if 'PRODUTIVO' not in resumo_servico: resumo_servico['PRODUTIVO'] = 0
            if 'IMPRODUTIVO' not in resumo_servico: resumo_servico['IMPRODUTIVO'] = 0
            resumo_servico['Total Geral'] = resumo_servico.sum(axis=1)
            total_geral_servico = resumo_servico.sum().to_frame('Total Geral').T
            st.dataframe(resumo_servico[['PRODUTIVO', 'IMPRODUTIVO', 'Total Geral']])
            st.dataframe(total_geral_servico)
        else:
            st.warning("Nenhum dado para exibir ou colunas 'Serviço' e 'Resultado' não encontradas.")