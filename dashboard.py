# Importando as bibliotecas necessárias
import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuração da Página ---
st.set_page_config(
    page_title="Parcial SOC - Maricá",
    page_icon="📊",
    layout="wide"
)

# --- Carregamento dos Dados ---
@st.cache_data
def carregar_dados(arquivo_carregado):
    """
    Carrega dados de um arquivo Excel carregado pelo usuário.
    """
    try:
        df = pd.read_excel(arquivo_carregado)
        return df
    except Exception as e:
        st.error(f"Ocorreu um erro ao carregar o arquivo: {e}")
        return None

# --- Interface Principal do Dashboard ---
st.title("📊 SOC Maricá - Produção Diária")

# --- BARRA LATERAL E UPLOAD DE ARQUIVO ---
st.sidebar.header("Controles")
uploaded_file = st.sidebar.file_uploader("Carregue sua planilha Excel aqui", type=['xlsx'])

# A execução do script continua apenas se um arquivo for carregado.
if uploaded_file is not None:
    df_original = carregar_dados(uploaded_file)

    # A execução continua apenas se o dataframe for carregado com sucesso.
    if df_original is not None:
        st.sidebar.success("Planilha carregada com sucesso!")
        # --- FILTROS GLOBAIS NA BARRA LATERAL ---
        st.sidebar.header("Filtros Globais")
        
        # Filtro por Setor
        setores_disponiveis = ['Todos'] + df_original['Setor'].dropna().unique().tolist()
        setores_selecionados = st.sidebar.multiselect("Setor", setores_disponiveis, default=['Todos'])

        # Filtro por Equipe
        equipes_disponiveis = ['Todos'] + df_original['Chefe/Responsável de Equipe'].dropna().unique().tolist()
        equipes_selecionadas = st.sidebar.multiselect("Equipe", equipes_disponiveis, default=['Todos'])

        # Filtro por Resultado
        resultados_disponiveis = ['Todos'] + df_original['Resultado'].dropna().unique().tolist()
        resultados_selecionados = st.sidebar.multiselect("Resultado", resultados_disponiveis, default=['Todos'])

        # Aplica os filtros ao dataframe
        df_filtrado = df_original.copy()
        if 'Todos' not in setores_selecionados:
            df_filtrado = df_filtrado[df_filtrado['Setor'].isin(setores_selecionados)]
        if 'Todos' not in equipes_selecionadas:
            df_filtrado = df_filtrado[df_filtrado['Chefe/Responsável de Equipe'].isin(equipes_selecionadas)]
        if 'Todos' not in resultados_selecionados:
            df_filtrado = df_filtrado[df_filtrado['Resultado'].isin(resultados_selecionados)]

        # st.multiselect para o usuário escolher as colunas para visualizar na tabela
        with st.expander("Exibir/Ocultar Tabela de Dados Filtrados"):
            st.dataframe(df_filtrado)

        st.markdown("---")
        # --- CARTÕES DE INDICADORES (KPIs) ---
        total_atividades = len(df_filtrado)
        total_produtivo = df_filtrado[df_filtrado['Resultado'] == 'Produtivo'].shape[0]
        total_improdutivo = df_filtrado[df_filtrado['Resultado'] == 'Improdutivo'].shape[0]
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
                
                lista_equipes_grafico = ['Todas as Equipes'] + df_filtrado['Chefe/Responsável de Equipe'].dropna().unique().tolist()
                equipe_selecionada_grafico = st.selectbox('Detalhar por Equipe:', options=lista_equipes_grafico, key='select_equipe_individual')

                df_para_grafico_equipe = df_filtrado
                if equipe_selecionada_grafico != 'Todas as Equipes':
                    df_para_grafico_equipe = df_filtrado[df_filtrado['Chefe/Responsável de Equipe'] == equipe_selecionada_grafico]

                produtividade_equipe = df_para_grafico_equipe.groupby('Chefe/Responsável de Equipe')['Resultado'].value_counts().unstack().fillna(0)
                fig = px.bar(produtividade_equipe, barmode='group', text_auto=True, color_discrete_map={'Produtivo': 'royalblue', 'Improdutivo': 'darkorange'}, title="Produtividade por Equipe")
                fig.update_layout(xaxis_title=None, yaxis_title="Qtd. Atividades", legend_title="Resultado")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Nenhum dado para exibir com os filtros atuais.")

        # Coluna 2: Gráfico de Produtividade por Setor (com filtro individual)
        with col2:
            st.subheader("Produtividade por Setor")
            if not df_filtrado.empty and 'Setor' in df_filtrado.columns:

                lista_setores_grafico = ['Todos os Setores'] + df_filtrado['Setor'].dropna().unique().tolist()
                setor_selecionado_grafico = st.selectbox('Detalhar por Setor:', options=lista_setores_grafico, key='select_setor_individual')

                df_para_grafico_setor = df_filtrado
                if setor_selecionado_grafico != 'Todos os Setores':
                    df_para_grafico_setor = df_filtrado[df_filtrado['Setor'] == setor_selecionado_grafico]
                
                titulo_grafico = f'Produtividade para: {setor_selecionado_grafico}' if setor_selecionado_grafico != 'Todos os Setores' else 'Produtividade (Todos os Setores Filtrados)'
                
                produtividade_setor = df_para_grafico_setor['Resultado'].value_counts().reset_index()
                produtividade_setor.columns = ['Resultado', 'Contagem']

                fig = px.pie(produtividade_setor, names='Resultado', values='Contagem', title=titulo_grafico, color='Resultado', color_discrete_map={'Produtivo': 'royalblue', 'Improdutivo': 'darkorange'})
                fig.update_traces(textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Nenhum dado para exibir com os filtros atuais.")

        st.markdown("---")

        # --- Layout em Colunas para as Tabelas de Resumo ---
        col3, col4 = st.columns(2)

        # Coluna 3: Tabela de Resumo por Equipe e Setor
        with col3:
            st.subheader("Resumo por Equipe e Setor")
            if not df_filtrado.empty and all(col in df_filtrado.columns for col in ['Chefe/Responsável de Equipe', 'Setor', 'Resultado']):
                resumo_equipe = pd.pivot_table(df_filtrado, index=['Chefe/Responsável de Equipe', 'Setor'], columns='Resultado', aggfunc='size', fill_value=0)
                if 'Produtivo' not in resumo_equipe: resumo_equipe['Produtivo'] = 0
                if 'Improdutivo' not in resumo_equipe: resumo_equipe['Improdutivo'] = 0
                resumo_equipe['Total Geral'] = resumo_equipe.sum(axis=1)
                
                # Calcula a altura da tabela dinamicamente para exibir todas as linhas
                altura_tabela = (len(resumo_equipe.index) + 1) * 35 + 3
                st.dataframe(resumo_equipe[['Produtivo', 'Improdutivo', 'Total Geral']], height=altura_tabela)
            else:
                st.warning("Nenhum dado para exibir com os filtros atuais.")

        # Coluna 4: Tabela de Resumo por Serviço
        with col4:
            st.subheader("Resumo por Serviço")
            if not df_filtrado.empty and all(col in df_filtrado.columns for col in ['Serviço', 'Resultado']):
                resumo_servico = pd.pivot_table(df_filtrado, index=['Serviço'], columns='Resultado', aggfunc='size', fill_value=0)
                if 'Produtivo' not in resumo_servico: resumo_servico['Produtivo'] = 0
                if 'Improdutivo' not in resumo_servico: resumo_servico['Improdutivo'] = 0
                resumo_servico['Total Geral'] = resumo_servico.sum(axis=1)
                total_geral_servico = resumo_servico.sum().to_frame('Total Geral').T
                st.dataframe(resumo_servico[['Produtivo', 'Improdutivo', 'Total Geral']])
                st.dataframe(total_geral_servico)
            else:
                st.warning("Nenhum dado para exibir ou colunas 'Serviço' e 'Resultado' não encontradas.")

else:
    st.info("⬅️ Por favor, carregue uma planilha no formato .xlsx para começar a análise.")