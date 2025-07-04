# 📊 Dashboard de Análise de Produção - SOC Maricá

Este repositório contém o código-fonte de um dashboard interativo desenvolvido em Python com a biblioteca Streamlit. A aplicação foi criada para analisar dados operacionais de equipes, permitindo a visualização de indicadores de produtividade de forma dinâmica e intuitiva.

O projeto transforma uma planilha Excel padrão em uma ferramenta de análise visual, substituindo a necessidade de criar gráficos e tabelas dinâmicas manualmente.

## ✨ Funcionalidades Principais

* **Upload Dinâmico:** Permite que o usuário carregue sua própria planilha (`.xlsx`), tornando a ferramenta flexível para diferentes períodos de análise.
* **Limpeza e Padronização de Dados:** O código realiza um pré-processamento automático dos dados, removendo espaços extras e padronizando o texto para garantir a precisão das contagens e análises.
* **Filtros Globais e Individuais:** A barra lateral oferece filtros globais (por equipe, setor, resultado) que atualizam todo o dashboard, enquanto cada gráfico possui seus próprios filtros para uma análise mais detalhada.
* **KPIs em Destaque:** Apresenta os principais indicadores (Total de Atividades, Total Produtivo, Taxa de Produtividade) em cartões de fácil visualização.
* **Visualizações Interativas:**
    * Gráfico de barras para análise de produtividade por equipe.
    * Gráfico de pizza para visualizar a distribuição de resultados por setor.
    * Tabelas de resumo detalhadas que simulam o comportamento de tabelas dinâmicas.

## 🚀 Como Executar o Projeto Localmente

Para executar este dashboard no seu computador, siga os passos abaixo:

1.  **Clone o repositório:**
    ```bash
    git clone [https://docs.github.com/articles/referencing-and-citing-content](https://docs.github.com/articles/referencing-and-citing-content)
    cd [nome-da-pasta-do-repositorio]
    ```

2.  **Crie um ambiente virtual (recomendado):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # No Windows, use `venv\Scripts\activate`
    ```

3.  **Crie o arquivo `requirements.txt`:**
    Na raiz do seu projeto, crie um arquivo chamado `requirements.txt` com o seguinte conteúdo:
    ```text
    streamlit
    pandas
    plotly
    openpyxl
    ```

4.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Execute a aplicação:**
    ```bash
    streamlit run seu_script.py  # Substitua 'seu_script.py' pelo nome do seu arquivo Python
    ```
    A aplicação será aberta automaticamente no seu navegador.

## 🎓 Como Este Projeto Agrega aos Seus Estudos

Este projeto é um excelente case prático que demonstra habilidades essenciais na área de Dados e desenvolvimento de software:

* **Análise e Manipulação de Dados com `pandas`:** Você está aplicando na prática a limpeza de dados (`.strip()`, `.str.replace()`, `.str.upper()`), agrupamentos (`.groupby()`), e criação de tabelas dinâmicas (`.pivot_table()`), que são tarefas fundamentais no dia a dia de um analista de dados.

* **Data Visualization com `plotly`:** A criação de gráficos interativos e visualmente agradáveis é uma habilidade muito valorizada. Este projeto mostra que você sabe como transformar dados brutos em insights visuais claros e objetivos.

* **Desenvolvimento de Aplicações Web com `streamlit`:** Você construiu uma aplicação web funcional do zero. Isso demonstra sua capacidade de não apenas analisar dados, mas também de criar ferramentas que outras pessoas podem usar. O uso de layouts, colunas, filtros interativos e gerenciamento de estado (`st.sidebar`, `st.columns`) são conceitos importantes.

* **Engenharia de Software e Boas Práticas:** A estruturação do código em funções, o tratamento de erros (`try-except`) e a criação de um `README` demonstram uma mentalidade de desenvolvedor, focada em criar código legível, reutilizável e bem documentado.

Ter um projeto como este no seu portfólio mostra a potenciais empregadores que você consegue ir além da teoria, aplicando seus conhecimentos para resolver um problema real e entregar uma solução completa e funcional.
