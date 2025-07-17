# Importando as bibliotecas necessárias
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, timedelta
import gspread
from google.oauth2.service_account import Credentials
from PIL import Image

# --- Configuração da Página ---
st.set_page_config(
    page_title="Dashboard de Fiscalização",
    page_icon="🔍",
    layout="wide"
)

try:
    image = Image.open("imagens/ceneged_cover.jpeg")
    st.image(image, use_container_width =True)
except FileNotFoundError:
    st.warning("Arquivo de imagem 'imagens/ceneged_cover.jpeg' não encontrado. A imagem do cabeçalho não será exibida.")


# --- Carregamento e Limpeza dos Dados a partir do Google Sheets ---
@st.cache_data
def carregar_dados_de_gsheets(url_planilha):
    """
    Carrega os dados brutos da planilha do Google Sheets.
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
        
        # Cria o DataFrame
        df = pd.DataFrame(all_values[1:], columns=all_values[0])

        # Limpa os nomes das colunas para remover espaços em branco
        df.columns = [col.strip() for col in df.columns]

        # Renomeia colunas duplicadas para garantir unicidade
        cols = []
        counts = {}
        for col in df.columns:
            if col in counts:
                counts[col] += 1
                new_col_name = f"{col}_{counts[col]}"
                cols.append(new_col_name)
            else:
                counts[col] = 0
                cols.append(col)
        df.columns = cols
        
        return df
    except gspread.exceptions.SpreadsheetNotFound:
        st.error(f"Planilha não encontrada na URL fornecida. Verifique o link e se a planilha foi compartilhada com o e-mail de serviço.")
        return None
    except Exception as e:
        st.error(f"Ocorreu um erro ao carregar os dados do Google Sheets: {e}")
        return None

# --- Interface Principal do Dashboard ---
st.title("🔍 Dashboard Fiscalização")

# --- Carregamento dos Dados ---
URL_DA_PLANILHA = "https://docs.google.com/spreadsheets/d/1zI6BA_hPSMRRFj1u33Ot3xqPYBrSrnhqv_pSSxBRS6Q/edit?usp=sharing" 
df_raw = carregar_dados_de_gsheets(URL_DA_PLANILHA)

# A execução do script continua apenas se o dataframe for carregado com sucesso.
if df_raw is not None:
    
    # --- PREPARAÇÃO DOS DADOS ---
    df_prepared = df_raw.copy()
    
    # 1. Verifica se as colunas essenciais existem
    colunas_essenciais = ['Status', 'Erro', 'Agente', 'Data da analise', 'Responsável', 'Status Plano Ação']
    for col in colunas_essenciais:
        if col not in df_prepared.columns:
            st.error(f"Erro Crítico: A coluna '{col}' não foi encontrada na sua planilha. Verifique se o nome na planilha é exatamente este.")
            st.stop() # Interrompe a execução se uma coluna essencial faltar

    # 2. Padroniza colunas de texto
    colunas_para_padronizar = ['Status', 'Erro', 'Agente', 'Responsável', 'Status Plano Ação']
    for col in colunas_para_padronizar:
        df_prepared[col] = df_prepared[col].astype(str).str.strip().str.upper()
    
    # 3. Converte a coluna de data, tratando erros
    df_prepared['Data da analise'] = pd.to_datetime(df_prepared['Data da analise'], errors='coerce')

    # 4. CORREÇÃO: Cria a base de dados principal removendo linhas onde o Status é vazio
    df_original = df_prepared[df_prepared['Status'].isin(['PROCEDENTE', 'IMPROCEDENTE'])].copy()

    # --- BARRA LATERAL COM FILTROS GLOBAIS ---
    st.sidebar.header("Filtros")

    # Filtro por Agente
    agentes_disponiveis = ['TODOS'] + sorted(df_original['Agente'].dropna().unique().tolist())
    agente_selecionado = st.sidebar.selectbox("Agente", agentes_disponiveis)

    # Filtro por Status
    status_disponiveis = ['TODOS'] + sorted(df_original['Status'].dropna().unique().tolist())
    status_selecionado = st.sidebar.selectbox("Status", status_disponiveis)
    
    # Filtro por Responsável
    responsaveis_disponiveis = ['TODOS'] + sorted(df_original['Responsável'].dropna().unique().tolist())
    responsavel_selecionado = st.sidebar.selectbox("Responsável", responsaveis_disponiveis)

    # --- Lógica de Filtro de Data Automático ---
    df_datas_validas = df_original.dropna(subset=['Data da analise'])
    data_min = df_datas_validas['Data da analise'].min().date()
    data_max = df_datas_validas['Data da analise'].max().date()

    data_inicio = st.sidebar.date_input('Data de Início', data_min, min_value=data_min, max_value=data_max, format="DD-MM-YYYY")
    data_fim = st.sidebar.date_input('Data de Fim', data_max, min_value=data_min, max_value=data_max, format="DD-MM-YYYY")

    # --- Aplicação dos Filtros ---
    # Começa com a base de dados já limpa e com status válidos
    df_filtrado = df_original.copy()

    # 1. Aplica o filtro de data (remove linhas com data inválida para o período)
    df_filtrado_com_data = df_filtrado.dropna(subset=['Data da analise'])
    df_filtrado = df_filtrado_com_data[
        (df_filtrado_com_data['Data da analise'].dt.date >= data_inicio) &
        (df_filtrado_com_data['Data da analise'].dt.date <= data_fim)
    ]

    # 2. Aplica os filtros categóricos ao resultado do filtro de data
    if agente_selecionado != 'TODOS':
        df_filtrado = df_filtrado[df_filtrado['Agente'] == agente_selecionado]
    if status_selecionado != 'TODOS':
        df_filtrado = df_filtrado[df_filtrado['Status'] == status_selecionado]
    if responsavel_selecionado != 'TODOS':
        df_filtrado = df_filtrado[df_filtrado['Responsável'] == responsavel_selecionado]
        
    # --- KPIs ---
    st.markdown("### Resumo do Período")
    
    total_fiscalizado = len(df_filtrado)
    df_com_erros = df_filtrado[df_filtrado['Erro'].str.strip() != '']
    total_erros = len(df_com_erros)
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
            status_counts = df_filtrado['Status'].value_counts()
            fig_donut = px.pie(
                status_counts, 
                values=status_counts.values, 
                names=status_counts.index, 
                title="Proporção Procedente vs. Improcedente",
                hole=0.4,
                color=status_counts.index,
                color_discrete_map={'PROCEDENTE':'royalblue', 'IMPROCEDENTE':'darkorange'}
            )
            fig_donut.update_traces(textinfo='percent+label')
            st.plotly_chart(fig_donut, use_container_width=True)
        else:
            st.warning("Nenhum dado para exibir com os filtros atuais.")

    with col2:
        st.subheader("Tipos de Erro Encontrados")
        if not df_com_erros.empty:
            erros_counts = df_com_erros['Erro'].value_counts()
            fig_bar = px.bar(
                erros_counts,
                x=erros_counts.index,
                y=erros_counts.values,
                title="Quantidade por Tipo de Erro",
                text=erros_counts.values,
                labels={'x': 'Tipo de Erro', 'y': 'Quantidade'}
            )
            fig_bar.update_layout(
                    showlegend=False,
                    yaxis_range=[0, erros_counts.values.max() * 1.15]
                )
            fig_bar.update_traces(textposition='outside')
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Nenhum erro encontrado no período selecionado.")

    col3,col4 = st.columns(2)
    
    with col3:
        st.subheader("Pendências Plano de Ação")
        
        # Cria um dataframe específico para este gráfico, começando pelo df_filtrado
        df_plano_acao_filtrado = df_filtrado[df_filtrado['Status Plano Ação'].isin(['PENDENTE', 'REALIZADO'])]

        if not df_plano_acao_filtrado.empty:
            status_acao = df_plano_acao_filtrado['Status Plano Ação'].value_counts()
            
            fig_bar2 = px.bar(
                status_acao,
                x=status_acao.index,
                y=status_acao.values,
                title="Pendências por Status do Plano de Ação",
                text=status_acao.values,
                labels={'x': 'Status Plano de Ação', 'y': 'Quantidade'},
                color=status_acao.index,
                color_discrete_map={'REALIZADO':'#90ee90', 'PENDENTE':'#f08080'}
            )
            fig_bar2.update_layout(
                showlegend=False,
                yaxis_range=[0, status_acao.values.max() * 1.15] if status_acao.values.max() > 0 else [0, 1]
            )
            fig_bar2.update_traces(textposition='outside')
            st.plotly_chart(fig_bar2, use_container_width=True)
        else:
            st.info("Nenhuma pendência de plano de ação para os filtros selecionados.")
        

    with col4:
        st.subheader("Ranking de Improcedentes por Agente")
        df_improcedentes = df_filtrado[df_filtrado['Status'] == 'IMPROCEDENTE']
        
        if not df_improcedentes.empty:
            ranking_agentes = df_improcedentes['Agente'].value_counts().sort_values(ascending=False)
            
            fig_ranking = px.bar(
                ranking_agentes,
                x=ranking_agentes.values,
                y=ranking_agentes.index,
                orientation='h',
                title="Top Agentes com Improcedentes",
                text=ranking_agentes.values,
                labels={'x': 'Quantidade de Improcedentes', 'y': 'Agente'}
            )
            fig_ranking.update_layout(
                showlegend=False,
                xaxis_range=[0, ranking_agentes.values.max() * 1.15],
                yaxis={'categoryorder':'total ascending'}
            )
            fig_ranking.update_traces(textposition='outside')
            st.plotly_chart(fig_ranking, use_container_width=True)
        else:
            st.info("Nenhum erro encontrado para gerar o ranking.")
            
    # --- Tabela de Dados Detalhada ---
    with st.expander("Ver dados detalhados da fiscalização"):
        st.dataframe(df_filtrado)

else:
    st.warning("Aguardando dados da planilha... Verifique a URL e as configurações de partilha.")