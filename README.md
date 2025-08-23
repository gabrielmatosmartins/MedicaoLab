# Coleta de Dados de Repositórios GitHub

Este projeto coleta dados de repositórios do GitHub usando a API GraphQL para análise de métricas relacionadas a microserviços.

## Configuração

1. Clone o repositório
2. Instale as dependências:
   ```
   pip install requests python-dotenv
   ```
3. Crie um arquivo `.env` na raiz do projeto com seu token do GitHub:
   ```
   GITHUB_TOKEN="seu_token_aqui"
   ```
   
   > **Nota**: Nunca compartilhe seu token do GitHub. O arquivo `.env` está incluído no `.gitignore` para evitar que seja acidentalmente compartilhado.

## Sprint 1


### Execução

Execute o script relacionado à Sprint 1 para coletar dados de 100 repositórios relacionados a microserviços:

```
python main_sprint_1.py
```

Os dados serão salvos no arquivo `repo_grathQL.txt`.

### Arquivos

- `main.py`: Script principal para coleta de dados
- `.env`: Arquivo de configuração com o token do GitHub (não incluído no repositório)
- `repo_grathQL.txt`: Arquivo de saída com os dados coletados
- `test_with_sample_data.py`: Script para gerar e analisar dados de amostra

### Métricas Coletadas

- Nome e proprietário do repositório
- URL e homepage
- Contagem de estrelas, forks e watchers
- Descrição
- Contagem de commits
- Issues (abertas e fechadas)
- Pull Requests (abertos, fechados e mesclados)
- Releases
- Datas de criação, atualização e último push
- Linguagem principal e todas as linguagens
- Informações de licença
- Tamanho do repositório
- Branch principal
- Status (arquivado, fork, template)
- Tópicos


## Sprint 2

### Execução
```
main python_sprint_2.py
```

Os dados coletados de 1000 repositórios serão salvos no arquivo `repositorios_populares_github.csv`.

Documentacão de padrão de dados coletados: https://github.com/gabrielmatosmartins/MedicaoLab/blob/main/Medicao/padrao_dados_csv.md
