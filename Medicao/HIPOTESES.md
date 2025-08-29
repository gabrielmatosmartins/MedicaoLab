# Hipóteses Informais e Metodologia de Análise

## Hipóteses Informais

Com base nas questões de pesquisa (RQs) definidas no laboratório, foram elaboradas as seguintes hipóteses informais:

### H1: Sistemas populares são maduros/antigos
**Hipótese**: Sistemas populares tendem a ser maduros, com idade média superior a 5 anos.
**Métrica**: Idade do repositório (calculada a partir da data de sua criação)
**Justificativa**: Repositórios mais antigos tiveram mais tempo para acumular estrelas, contribuições e estabelecer uma base de usuários sólida.

### H2: Sistemas populares recebem muita contribuição externa
**Hipótese**: Sistemas populares recebem contribuições externas significativas, com mediana de PRs aceitos superior a 100.
**Métrica**: Total de pull requests aceitas (mescladas)
**Justificativa**: Projetos populares atraem mais contribuidores, resultando em um número maior de pull requests aceitas.

### H3: Sistemas populares lançam releases com frequência
**Hipótese**: Sistemas populares lançam releases com frequência, com mediana superior a 10 releases por repositório.
**Métrica**: Total de releases
**Justificativa**: Projetos ativos e bem mantidos tendem a lançar novas versões regularmente para corrigir bugs e adicionar funcionalidades.

### H4: Sistemas populares são atualizados com frequência
**Hipótese**: Sistemas populares são atualizados regularmente, com última atualização em menos de 3 meses.
**Métrica**: Tempo até a última atualização (calculado a partir da data de última atualização)
**Justificativa**: Projetos populares tendem a ser mantidos ativamente, resultando em atualizações frequentes.

### H5: Sistemas populares são escritos nas linguagens mais populares
**Hipótese**: Sistemas populares são majoritariamente escritos em JavaScript, Python e TypeScript.
**Métrica**: Linguagem primária de cada um desses repositórios
**Justificativa**: As linguagens mais populares têm comunidades maiores, mais recursos e ferramentas, facilitando o desenvolvimento de projetos populares.


### H6: Sistemas populares possuem um alto percentual de issues fechadas
**Hipótese**: Repositórios populares apresentam um percentual elevado de issues fechadas (esperado >70%), refletindo boa manutenção e engajamento da comunidade.
**Métrica**: Percentual issues fechadas= issues_fechadas ÷ total_issues (cálculo por repositório e análise da mediana)
**Justificativa**: Métrica: Projetos mais populares tendem a ter uma comunidade ativa e equipes de manutenção mais organizadas, o que possibilita triagem, resolução e fechamento de issues de forma regular, garantindo maior qualidade do software.
​

## Metodologia de Análise

Para analisar as hipóteses acima, seguiremos a seguinte metodologia:

1. **Coleta de dados**: Utilizaremos a API GraphQL do GitHub para coletar dados dos 1.000 repositórios com maior número de estrelas.

2. **Processamento dos dados**: Os dados serão processados e armazenados em um arquivo CSV para facilitar a análise posterior.

3. **Análise estatística**: Para cada questão de pesquisa, calcularemos estatísticas descritivas (média, mediana, desvio padrão) para as métricas relevantes.

4. **Visualização**: Criaremos gráficos para visualizar a distribuição dos dados e identificar padrões.

5. **Teste das hipóteses**: Compararemos os resultados obtidos com as hipóteses informais para verificar se elas são confirmadas ou refutadas pelos dados.

6. **Análise adicional (bônus)**: Para a RQ07, dividiremos os resultados das RQs 02, 03 e 04 por linguagem de programação para analisar como esses valores se comportam de acordo com a linguagem de cada repositório.

## Ferramentas Utilizadas

- **Python**: Linguagem de programação utilizada para a coleta e análise dos dados.
- **Requests**: Biblioteca para fazer requisições HTTP à API do GitHub.
- **CSV**: Módulo para manipulação de arquivos CSV.
- **Pandas**: Biblioteca para análise de dados (a ser utilizada na análise posterior).
- **Matplotlib/Seaborn**: Bibliotecas para visualização de dados (a serem utilizadas na análise posterior).

## Resultados Esperados

Esperamos que a análise dos dados coletados nos permita responder às questões de pesquisa e verificar se as hipóteses informais são confirmadas ou refutadas. Os resultados serão apresentados em um relatório final, que incluirá:

1. Introdução com as hipóteses informais
2. Metodologia utilizada
3. Resultados obtidos para cada questão de pesquisa
4. Discussão sobre os resultados em relação às hipóteses
5. Conclusões

Para a análise bônus (RQ07), esperamos identificar se há diferenças significativas entre os repositórios escritos em diferentes linguagens de programação em termos de contribuição externa, frequência de releases e frequência de atualizações.