# Importando as bibliotecas necessárias
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, timedelta
import gspread
from google.oauth2.service_account import Credentials

# --- Configuração da Página ---
st.set_page_config(
    page_title="Dashboard de Fiscalização",
    page_icon="🔍",
    layout="wide"
)

# --- Carregamento e Limpeza dos Dados a partir do Google Sheets ---
@st.cache_data
def carregar_dados_de_gsheets(url_planilha):
    """
    Carrega e processa os dados da planilha de fiscalização do Google Sheets a partir de uma URL.
    """
    try:
        # Autenticação e acesso à API
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
        client = gspread.authorize(creds)
        
        # Abre a planilha pela URL e pega a primeira aba
        sheet = client.open_by_url(url_planilha).sheet1
        
        # Lê todos os valores e cria o DataFrame com o Pandas para lidar com cabeçalhos duplicados.
        all_values = sheet.get_all_values()
        if not all_values:
            st.error("A planilha parece estar vazia.")
            return None
        df = pd.DataFrame(all_values[1:], columns=all_values[0])


        # --- Limpeza e Padronização dos Dados ---
        
        # CORREÇÃO: Atualizado o nome da coluna de status para "Status"
        colunas_essenciais = ['Status', 'Tipo de Erro', 'Eletricista', 'Data de baixa']
        for col in colunas_essenciais:
            if col not in df.columns:
                st.error(f"Erro Crítico: A coluna '{col}' não foi encontrada na sua planilha. O dashboard não pode continuar.")
                return None

        # Converte a coluna de data, tratando erros
        df['Data de baixa'] = pd.to_datetime(df['Data de baixa'], errors='coerce')
        df.dropna(subset=['Data de baixa'], inplace=True) # Remove linhas onde a data não pôde ser convertida

        # Padroniza colunas de texto
        colunas_para_padronizar = ['Status', 'Tipo de Erro', 'Eletricista']
        for col in colunas_para_padronizar:
            df[col] = df[col].astype(str).str.strip().str.upper()
        
        return df
    except gspread.exceptions.SpreadsheetNotFound:
        st.error(f"Planilha não encontrada na URL fornecida. Verifique o link e se a planilha foi compartilhada com o e-mail de serviço.")
        return None
    except Exception as e:
        st.error(f"Ocorreu um erro ao carregar os dados do Google Sheets: {e}")
        return None

# --- Interface Principal do Dashboard ---
st.title("🔍 Dashboard de Fiscalização de Serviços")

# --- Carregamento dos Dados ---
# IMPORTANTE: Cole aqui a URL da sua Planilha Google de fiscalização
URL_DA_PLANILHA = "https://docs.google.com/spreadsheets/d/1zI6BA_hPSMRRFj1u33Ot3xqPYBrSrnhqv_pSSxBRS6Q/edit?usp=sharing" 
df_original = carregar_dados_de_gsheets(URL_DA_PLANILHA)

# A execução do script continua apenas se o dataframe for carregado com sucesso.
if df_original is not None:
    
    # --- BARRA LATERAL COM FILTROS GLOBAIS ---
    st.sidebar.header("Filtros")

    # Filtro de Data
    data_min = df_original['Data de baixa'].min().date()
    data_max = df_original['Data de baixa'].max().date()
    data_inicio = st.sidebar.date_input('Data de Início', data_min, min_value=data_min, max_value=data_max)
    data_fim = st.sidebar.date_input('Data de Fim', data_max, min_value=data_min, max_value=data_max)

    # Filtro por Eletricista
    eletricistas_disponiveis = ['TODOS'] + sorted(df_original['Eletricista'].dropna().unique().tolist())
    eletricista_selecionado = st.sidebar.selectbox("Eletricista", eletricistas_disponiveis)

    # CORREÇÃO: Atualizado o nome da coluna e o label do filtro para "Status"
    status_disponiveis = ['TODOS'] + sorted(df_original['Status'].dropna().unique().tolist())
    status_selecionado = st.sidebar.selectbox("Status", status_disponiveis)

    # --- Aplicação dos Filtros ---
    df_filtrado = df_original[
        (df_original['Data de baixa'].dt.date >= data_inicio) &
        (df_original['Data de baixa'].dt.date <= data_fim)
    ]
    if eletricista_selecionado != 'TODOS':
        df_filtrado = df_filtrado[df_filtrado['Eletricista'] == eletricista_selecionado]
    # CORREÇÃO: Atualizado o nome da coluna no filtro
    if status_selecionado != 'TODOS':
        df_filtrado = df_filtrado[df_filtrado['Status'] == status_selecionado]

    # --- KPIs ---
    st.markdown("### Resumo do Período")
    total_fiscalizado = len(df_filtrado)
    # CORREÇÃO: Atualizado o valor para contar erros (IMPROCEDENTE) na coluna "Status"
    total_erros = df_filtrado[df_filtrado['Status'] == 'IMPROCEDENTE'].shape[0]
    percentual_erro = (total_erros / total_fiscalizado * 100) if total_fiscalizado > 0 else 0

    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Total Fiscalizado", total_fiscalizado)
    kpi2.metric("Total de Erros", total_erros)
    kpi3.metric("Percentual de Erro", f"{percentual_erro:.2f}%")

    st.markdown("---")

    # --- Gráficos Principais ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Status das Fiscalizações")
        if not df_filtrado.empty:
            # CORREÇÃO: Atualizado o nome da coluna
            status_counts = df_filtrado['Status'].value_counts()
            fig_donut = px.pie(
                status_counts, 
                values=status_counts.values, 
                names=status_counts.index, 
                title="Proporção Procedente vs. Improcedente",
                hole=0.4,
                color=status_counts.index,
                # CORREÇÃO: Atualizado o mapeamento de cores
                color_discrete_map={'PROCEDENTE':'royalblue', 'IMPROCEDENTE':'darkorange'}
            )
            fig_donut.update_traces(textinfo='percent+label')
            st.plotly_chart(fig_donut, use_container_width=True)
        else:
            st.warning("Nenhum dado para exibir com os filtros atuais.")

    with col2:
        st.subheader("Tipos de Erro Encontrados")
        # CORREÇÃO: Atualizado o nome da coluna e o valor
        df_erros = df_filtrado[df_filtrado['Status'] == 'IMPROCEDENTE']
        if not df_erros.empty:
            erros_counts = df_erros['Tipo de Erro'].value_counts()
            fig_bar = px.bar(
                erros_counts,
                x=erros_counts.index,
                y=erros_counts.values,
                title="Quantidade por Tipo de Erro",
                text=erros_counts.values,
                labels={'x': 'Tipo de Erro', 'y': 'Quantidade'}
            )
            fig_bar.update_traces(textposition='outside')
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Nenhum erro encontrado no período selecionado.")

    # --- Tabela de Dados Detalhada ---
    with st.expander("Ver dados detalhados da fiscalização"):
        st.dataframe(df_filtrado)
else:
    st.warning("Aguardando dados da planilha... Verifique a URL e as configurações de partilha.")