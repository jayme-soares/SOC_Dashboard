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
        
        # Cria o DataFrame
        df = pd.DataFrame(all_values[1:], columns=all_values[0])

        # --- Limpeza e Padronização dos Dados ---
        
        # 1. Limpa os nomes das colunas para remover espaços em branco
        df.columns = [col.strip() for col in df.columns]

        # 2. Renomeia colunas duplicadas para garantir unicidade
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

        # 3. Verifica se as colunas essenciais existem
        colunas_essenciais = ['Status', 'Erro', 'Agente', 'Data da analise', 'Responsável', 'Status Plano Ação']
        for col in colunas_essenciais:
            if col not in df.columns:
                st.error(f"Erro Crítico: A coluna '{col}' não foi encontrada na sua planilha. Verifique se o nome na planilha é exatamente este.")
                return None

        # 4. Padroniza colunas de texto (sem converter data ainda)
        colunas_para_padronizar = ['Status', 'Erro', 'Agente', 'Responsável', 'Status Plano Ação']
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
st.title("🔍 Dashboard Fiscalização")

# --- Carregamento dos Dados ---
# IMPORTANTE: Cole aqui a URL da sua Planilha Google de fiscalização
URL_DA_PLANILHA = "https://docs.google.com/spreadsheets/d/1zI6BA_hPSMRRFj1u33Ot3xqPYBrSrnhqv_pSSxBRS6Q/edit?usp=sharing" 
df_original = carregar_dados_de_gsheets(URL_DA_PLANILHA)

# A execução do script continua apenas se o dataframe for carregado com sucesso.
if df_original is not None:
    
    # --- Processamento de Datas (feito aqui para não afetar o df_original) ---
    df_com_data = df_original.copy()
    df_com_data['Data da analise'] = df_com_data['Data da analise'].replace('', pd.NaT)
    df_com_data['Data da analise'] = pd.to_datetime(df_com_data['Data da analise'], errors='coerce')
    df_com_data_valida = df_com_data.dropna(subset=['Data da analise'])

    # --- BARRA LATERAL COM FILTROS GLOBAIS ---
    st.sidebar.header("Filtros")

    # Filtro de Data
    data_min = df_com_data_valida['Data da analise'].min().date()
    data_max = df_com_data_valida['Data da analise'].max().date()
    data_inicio = st.sidebar.date_input('Data de Início', data_min, min_value=data_min, max_value=data_max, format="DD-MM-YYYY")
    data_fim = st.sidebar.date_input('Data de Fim', data_max, min_value=data_min, max_value=data_max, format="DD-MM-YYYY")

    # Filtro por Agente
    agentes_disponiveis = ['TODOS'] + sorted(df_original['Agente'].dropna().unique().tolist())
    agente_selecionado = st.sidebar.selectbox("Agente", agentes_disponiveis)

    # Filtro por Status
    status_disponiveis = ['TODOS'] + sorted(df_original['Status'].dropna().unique().tolist())
    status_selecionado = st.sidebar.selectbox("Status", status_disponiveis)
    
    # Filtro por Responsável
    responsaveis_disponiveis = ['TODOS'] + sorted(df_original['Responsável'].dropna().unique().tolist())
    responsavel_selecionado = st.sidebar.selectbox("Responsável", responsaveis_disponiveis)

    # --- Aplicação dos Filtros ---
    # DataFrame principal, que respeita TODOS os filtros
    df_filtrado = df_com_data_valida[
        (df_com_data_valida['Data da analise'].dt.date >= data_inicio) &
        (df_com_data_valida['Data da analise'].dt.date <= data_fim)
    ]
    if agente_selecionado != 'TODOS':
        df_filtrado = df_filtrado[df_filtrado['Agente'] == agente_selecionado]
    if status_selecionado != 'TODOS':
        df_filtrado = df_filtrado[df_filtrado['Status'] == status_selecionado]
    if responsavel_selecionado != 'TODOS':
        df_filtrado = df_filtrado[df_filtrado['Responsável'] == responsavel_selecionado]
        
    # --- KPIs ---
    st.markdown("### Resumo do Período")
    total_fiscalizado = len(df_filtrado)
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
        df_erros = df_filtrado[df_filtrado['Status'] == 'IMPROCEDENTE']
        if not df_erros.empty:
            erros_counts = df_erros['Erro'].value_counts()
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
        
        df_plano_acao_filtrado = df_com_data_valida[
            (df_com_data_valida['Data da analise'].dt.date >= data_inicio) &
            (df_com_data_valida['Data da analise'].dt.date <= data_fim)
        ]
        
        if agente_selecionado != 'TODOS':
            df_plano_acao_filtrado = df_plano_acao_filtrado[df_plano_acao_filtrado['Agente'] == agente_selecionado]
        if responsavel_selecionado != 'TODOS':
            df_plano_acao_filtrado = df_plano_acao_filtrado[df_plano_acao_filtrado['Responsável'] == responsavel_selecionado]


        if not df_plano_acao_filtrado.empty:
            df_plano_acao = df_plano_acao_filtrado[df_plano_acao_filtrado['Status Plano Ação'].str.strip() != '']
            
            if not df_plano_acao.empty:
                status_acao = df_plano_acao['Status Plano Ação'].value_counts()
                
                fig_bar2 = px.bar(
                    status_acao,
                    x=status_acao.index,
                    y=status_acao.values,
                    title="Pendências por Status do Plano de Ação",
                    text=status_acao.values,
                    labels={'x': 'Status Plano de Ação', 'y': 'Quantidade'},
                    color=status_acao.index,
                    color_discrete_map={'REALIZADO':'#90ee90', 'PENDENTE':'#f08080'} # Verde e Vermelho suaves
                )
                fig_bar2.update_layout(
                    showlegend=False,
                    yaxis_range=[0, status_acao.values.max() * 1.15]
                )
                fig_bar2.update_traces(textposition='outside')
                st.plotly_chart(fig_bar2, use_container_width=True)
            else:
                st.info("Nenhuma pendência de plano de ação para os filtros selecionados.")
        else:
            st.warning("Nenhum dado para exibir com os filtros atuais.")
            
    # --- NOVO GRÁFICO: Ranking de Improcedentes por Agente ---
    with col4:
        st.subheader("Improcedentes por Agente")
        df_improcedentes = df_filtrado[df_filtrado['Status'] == 'IMPROCEDENTE']
        
        if not df_improcedentes.empty:
            ranking_agentes = df_improcedentes['Agente'].value_counts().sort_values(ascending=True)
            
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
                xaxis_range=[0, ranking_agentes.values.max() * 1.15]
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
