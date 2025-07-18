# Importando as bibliotecas necessárias
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, datetime
from PIL import Image
import gspread
from google.oauth2.service_account import Credentials

# --- Configuração da Página ---
st.set_page_config(
    page_title="Dashboard de Fiscalização",
    page_icon="�",
    layout="wide"
)

# --- Carregamento e Limpeza dos Dados ---
@st.cache_data
def carregar_dados_de_gsheets(url_planilha):
    """
    Carrega os dados brutos da planilha do Google Sheets, limpa os nomes das colunas
    e garante que os nomes sejam únicos.
    """
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
        client = gspread.authorize(creds)
        sheet = client.open_by_url(url_planilha).sheet1
        all_values = sheet.get_all_values()
        
        if not all_values:
            st.error("A planilha parece estar vazia.")
            return None
        
        df = pd.DataFrame(all_values[1:], columns=all_values[0])
        df.columns = [col.strip() for col in df.columns]

        cols, counts = [], {}
        for col in df.columns:
            if col in counts:
                counts[col] += 1
                cols.append(f"{col}_{counts[col]}")
            else:
                counts[col] = 0
                cols.append(col)
        df.columns = cols
        return df
    except Exception as e:
        st.error(f"Ocorreu um erro ao carregar os dados do Google Sheets: {e}")
        return None

# --- Interface Principal ---
st.title("🔍 Dashboard Fiscalização")

URL_DA_PLANILHA = "https://docs.google.com/spreadsheets/d/1zI6BA_hPSMRRFj1u33Ot3xqPYBrSrnhqv_pSSxBRS6Q/edit?usp=sharing"
df_raw = carregar_dados_de_gsheets(URL_DA_PLANILHA)

if df_raw is not None:
    # --- 1. PREPARAÇÃO CENTRALIZADA DOS DADOS ---
    df_prepared = df_raw.copy()
    
    colunas_essenciais = ['Status', 'Erro', 'Agente', 'Data da analise', 'Responsável', 'Status Plano Ação']
    for col in colunas_essenciais:
        if col not in df_prepared.columns:
            st.error(f"Erro Crítico: A coluna '{col}' não foi encontrada na sua planilha.")
            st.stop()

    for col in ['Status', 'Erro', 'Agente', 'Responsável', 'Status Plano Ação']:
        df_prepared[col] = df_prepared[col].astype(str).str.strip().str.upper()
    
    df_prepared['Data da analise'] = pd.to_datetime(df_prepared['Data da analise'], errors='coerce', dayfirst=True)
    df_prepared.dropna(subset=['Data da analise'], inplace=True)

    df_base = df_prepared[df_prepared['Status'].isin(['PROCEDENTE', 'IMPROCEDENTE'])].copy()
    df_base['Mês Ano'] = df_base['Data da analise'].dt.strftime('%m/%Y')

    # --- 2. BARRA LATERAL E FILTROS ---
    st.sidebar.header("Filtros")
    st.sidebar.subheader("Período da Análise")

    # Filtro de Mês Referência
    meses_disponiveis = sorted(df_base['Mês Ano'].unique(), reverse=True)
    mes_selecionado = st.sidebar.selectbox("Mês Referência", ['TODOS'] + meses_disponiveis)
    
    # Define o dataframe a ser usado pelo slider (ou todos os dados, ou os dados do mês selecionado)
    df_para_slider = df_base[df_base['Mês Ano'] == mes_selecionado] if mes_selecionado != 'TODOS' else df_base

    if not df_para_slider.empty:
        # Pega a data mínima e máxima do dataframe filtrado pelo mês
        data_min_slider = df_para_slider['Data da analise'].min().date()
        data_max_slider = df_para_slider['Data da analise'].max().date()
        
        # **NOVO: Lógica do Slider de Datas com st.slider para melhor visualização**
        # Cria o slider de intervalo de datas. st.slider com datas evita a repetição do valor.
        data_selecionada = st.sidebar.slider(
            "Selecione o intervalo de datas:",
            min_value=data_min_slider,
            max_value=data_max_slider,
            value=(data_min_slider, data_max_slider),
            format="DD/MM/YYYY"
        )
        
        # Extrai data de início e fim do slider
        data_inicio, data_fim = data_selecionada
    else:
        # Caso não haja dados para o mês, desabilita o slider
        st.sidebar.info("Não há dados para o mês selecionado.")
        data_inicio, data_fim = None, None

    st.sidebar.subheader("Outros Filtros")
    agente_selecionado = st.sidebar.selectbox("Agente", ['TODOS'] + sorted(df_base['Agente'].unique()))
    status_selecionado = st.sidebar.selectbox("Status", ['TODOS'] + sorted(df_base['Status'].unique()))
    responsavel_selecionado = st.sidebar.selectbox("Responsável", ['TODOS'] + sorted(df_base['Responsável'].unique()))

    # --- 3. APLICAÇÃO SEQUENCIAL DOS FILTROS ---
    df_filtrado = df_base.copy()

    # Aplicação do filtro de data do slider
    if data_inicio and data_fim:
        # Garante que a comparação seja feita apenas com a parte da data
        df_filtrado = df_filtrado[df_filtrado['Data da analise'].dt.date.between(data_inicio, data_fim)]

    # Filtros Categóricos
    if agente_selecionado != 'TODOS':
        df_filtrado = df_filtrado[df_filtrado['Agente'] == agente_selecionado]
    if status_selecionado != 'TODOS':
        df_filtrado = df_filtrado[df_filtrado['Status'] == status_selecionado]
    if responsavel_selecionado != 'TODOS':
        df_filtrado = df_filtrado[df_filtrado['Responsável'] == responsavel_selecionado]

    # --- 4. KPIs E GRÁFICOS ---
    if data_inicio and data_fim:
        st.markdown(f"### Resumo do Período ({data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')})")
    else:
        st.markdown("### Resumo Geral do Período")

    if df_filtrado.empty:
        st.warning("Nenhum dado encontrado para os filtros selecionados. Por favor, ajuste os filtros.")
    else:
        total_fiscalizado = len(df_filtrado)
        df_com_erros = df_filtrado[df_filtrado['Erro'] != '']
        total_erros = len(df_com_erros)
        percentual_erro = (total_erros / total_fiscalizado * 100) if total_fiscalizado > 0 else 0

        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("Total Fiscalizado", total_fiscalizado)
        kpi2.metric("Total de Erros", total_erros)
        kpi3.metric("Percentual de Erro", f"{percentual_erro:.2f}%")

        st.markdown("---")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Status das Fiscalizações")
            status_counts = df_filtrado['Status'].value_counts()
            fig_donut = px.pie(status_counts, values=status_counts.values, names=status_counts.index, 
                                 title="Proporção Procedente vs. Improcedente", hole=0.4,
                                 color=status_counts.index, color_discrete_map={'PROCEDENTE':'royalblue', 'IMPROCEDENTE':'darkorange'})
            fig_donut.update_traces(textinfo='percent+label')
            st.plotly_chart(fig_donut, use_container_width=True)

        with col2:
            st.subheader("Tipos de Erro Encontrados")
            if not df_com_erros.empty:
                erros_counts = df_com_erros['Erro'].value_counts()
                fig_bar = px.bar(erros_counts, x=erros_counts.index, y=erros_counts.values,
                                   title="Quantidade por Tipo de Erro", text=erros_counts.values,
                                   labels={'x': 'Tipo de Erro', 'y': 'Quantidade'})
                fig_bar.update_layout(showlegend=False, yaxis_range=[0, erros_counts.values.max() * 1.15])
                fig_bar.update_traces(textposition='outside')
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("Nenhum erro encontrado no período selecionado.")

        col3, col4 = st.columns(2)
        
        with col3:
            st.subheader("Pendências Plano de Ação")
            df_plano_acao = df_filtrado[df_filtrado['Status Plano Ação'].isin(['PENDENTE', 'REALIZADO'])]
            if not df_plano_acao.empty:
                status_acao = df_plano_acao['Status Plano Ação'].value_counts()
                fig_bar2 = px.bar(status_acao, x=status_acao.index, y=status_acao.values,
                                    title="Pendências por Status do Plano de Ação", text=status_acao.values,
                                    labels={'x': 'Status Plano de Ação', 'y': 'Quantidade'},
                                    color=status_acao.index, color_discrete_map={'REALIZADO':'#90ee90', 'PENDENTE':'#f08080'})
                fig_bar2.update_layout(showlegend=False, yaxis_range=[0, status_acao.values.max() * 1.15 if not status_acao.empty else 1])
                fig_bar2.update_traces(textposition='outside')
                st.plotly_chart(fig_bar2, use_container_width=True)
            else:
                st.info("Nenhuma pendência de plano de ação para os filtros selecionados.")

        with col4:
            st.subheader("Ranking de Improcedentes por Agente")
            df_improcedentes = df_filtrado[df_filtrado['Status'] == 'IMPROCEDENTE']
            if not df_improcedentes.empty:
                ranking_agentes = df_improcedentes['Agente'].value_counts().sort_values(ascending=False)
                fig_ranking = px.bar(ranking_agentes, x=ranking_agentes.values, y=ranking_agentes.index,
                                       orientation='h', title="Top Agentes com Improcedentes",
                                       text=ranking_agentes.values, labels={'x': 'Quantidade de Improcedentes', 'y': 'Agente'})
                fig_ranking.update_layout(showlegend=False, xaxis_range=[0, ranking_agentes.values.max() * 1.15],
                                            yaxis={'categoryorder':'total ascending'})
                fig_ranking.update_traces(textposition='outside')
                st.plotly_chart(fig_ranking, use_container_width=True)
            else:
                st.info("Nenhum erro encontrado para gerar o ranking.")

        with st.expander("Ver dados detalhados da fiscalização"):
            df_display = df_filtrado.copy()
            df_display['Data da analise'] = df_display['Data da analise'].dt.strftime('%d/%m/%Y')
            st.dataframe(df_display.drop(columns=['Mês Ano'])) # Remove a coluna auxiliar
else:
    st.warning("Aguardando dados da planilha... Verifique a URL e as configurações de partilha.")