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



Este projeto foi um excelente case prático para desenvolver habilidades essenciais na área de Dados e desenvolvimento de software como:

* **Análise e Manipulação de Dados com `pandas`:  e tabelas dinâmicas , que são tarefas fundamentais no dia a dia de um analista de dados.

* **Data Visualization com `plotly`:** Para a criação de gráficos interativos e visualmente agradáveis.

* **Desenvolvimento de Aplicações Web com `streamlit`:** Construção de uma aplicação web funcional do zero, demonstrando a capacidade de não apenas analisar dados, mas também de criar ferramentas que outras pessoas podem usar. O uso de layouts, colunas, filtros interativos e gerenciamento de estado.
