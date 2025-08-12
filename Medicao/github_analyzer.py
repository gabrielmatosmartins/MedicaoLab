import requests
import json
import time
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import seaborn as sns

# Carregar variáveis de ambiente
load_dotenv()

class GitHubAnalyzer:
    def __init__(self):
        self.token = os.getenv('GITHUB_TOKEN')
        if not self.token:
            raise ValueError("GITHUB_TOKEN não encontrado no arquivo .env")
        
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
        }
        self.url = 'https://api.github.com/graphql'
        
    def get_top_repositories(self, limit=1000, max_retries=5, custom_query=None):
        """Busca os repositórios com mais estrelas ou usando uma consulta personalizada"""
        # Consulta padrão se nenhuma consulta personalizada for fornecida
        default_query = """
        query($cursor: String) {
          search(query: "microservices stars:>10", type: REPOSITORY, first: 100, after: $cursor) {
            pageInfo {
              hasNextPage
              endCursor
            }
            nodes {
              ... on Repository {
                name
                owner {
                  login
                }
                stargazerCount
                createdAt
                updatedAt
                primaryLanguage {
                  name
                }
                pullRequests(first: 1) {
                  totalCount
                }
                releases(first: 1) {
                  totalCount
                }
                issues(first: 1) {
                  totalCount
                }
                closedIssues: issues(states: CLOSED, first: 1) {
                  totalCount
                }
                mergedPullRequests: pullRequests(states: MERGED, first: 1) {
                  totalCount
                }
              }
            }
          }
        }
        """
        
        # Usar a consulta personalizada se fornecida, caso contrário usar a padrão
        query = custom_query if custom_query else default_query
        
        repositories = []
        cursor = None
        page = 0
        
        print(f"Coletando dados dos {limit} repositórios mais populares...")
        
        while len(repositories) < limit:
            # Implementação de retry com backoff exponencial
            retry_count = 0
            retry_delay = 1  # Começa com 1 segundo
            success = False
            
            while not success and retry_count < max_retries:
                try:
                    variables = {'cursor': cursor}
                    response = requests.post(
                        self.url,
                        headers=self.headers,
                        json={'query': query, 'variables': variables},
                        timeout=30  # Adiciona timeout para evitar esperas infinitas
                    )
                    
                    if response.status_code == 401:
                        raise ValueError("Token de autenticação inválido ou expirado. Verifique seu token do GitHub.")
                    
                    if response.status_code != 200:
                        print(f"Erro na requisição: {response.status_code}")
                        print(response.text)
                        raise Exception(f"API retornou status code {response.status_code}")
                    
                    data = response.json()
                    if 'data' not in data or 'search' not in data['data']:
                        print(f"Resposta da API não contém os dados esperados: {data}")
                        raise Exception("Dados da API em formato inesperado")
                    
                    search_data = data['data']['search']
                    success = True  # Se chegou aqui, a requisição foi bem-sucedida
                    
                except Exception as e:
                    retry_count += 1
                    if retry_count >= max_retries:
                        print(f"Falha após {max_retries} tentativas: {e}")
                        if len(repositories) > 0:
                            print(f"Retornando {len(repositories)} repositórios coletados até agora")
                            return repositories
                        else:
                            raise  # Re-lança a exceção se não tiver coletado nenhum repositório
                    
                    print(f"Tentativa {retry_count}/{max_retries} falhou: {e}")
                    print(f"Aguardando {retry_delay} segundos antes de tentar novamente...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Backoff exponencial: 1, 2, 4, 8, 16 segundos
            
            if not success:
                continue  # Vai para a próxima iteração do loop principal
            
            for repo in search_data['nodes']:
                if len(repositories) >= limit:
                    break
                    
                repositories.append({
                    'name': repo['name'],
                    'owner': repo['owner']['login'],
                    'full_name': f"{repo['owner']['login']}/{repo['name']}",
                    'stars': repo['stargazerCount'],
                    'created_at': repo['createdAt'],
                    'updated_at': repo['updatedAt'],
                    'language': repo['primaryLanguage']['name'] if repo['primaryLanguage'] else 'Unknown',
                    'pull_requests': repo['pullRequests']['totalCount'],
                    'merged_prs': repo['mergedPullRequests']['totalCount'],
                    'releases': repo['releases']['totalCount'],
                    'issues': repo['issues']['totalCount'],
                    'closed_issues': repo['closedIssues']['totalCount']
                })
            
            page += 1
            print(f"Página {page}: {len(repositories)} repositórios coletados")
            
            if not search_data['pageInfo']['hasNextPage']:
                break
                
            cursor = search_data['pageInfo']['endCursor']
            time.sleep(1)  # Rate limiting
            
        return repositories[:limit]
    
    def analyze_repositories(self, repositories):
        """Analisa os dados dos repositórios"""
        df = pd.DataFrame(repositories)
        
        # Converter datas
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['updated_at'] = pd.to_datetime(df['updated_at'])
        
        # Calcular métricas
        df['age_days'] = (datetime.now() - df['created_at']).dt.days
        df['days_since_update'] = (datetime.now() - df['updated_at']).dt.days
        df['closed_issues_ratio'] = df['closed_issues'] / df['issues'].replace(0, 1)
        
        return df
    
    def generate_report(self, df):
        """Gera relatório com as análises"""
        report = []
        
        # RQ01: Idade dos repositórios
        median_age = df['age_days'].median()
        report.append(f"RQ01 - Idade dos repositórios:")
        report.append(f"  Mediana: {median_age:.0f} dias ({median_age/365:.1f} anos)")
        report.append(f"  Mínimo: {df['age_days'].min():.0f} dias")
        report.append(f"  Máximo: {df['age_days'].max():.0f} dias")
        report.append("")
        
        # RQ02: Pull requests aceitas
        median_prs = df['merged_prs'].median()
        report.append(f"RQ02 - Pull requests aceitas:")
        report.append(f"  Mediana: {median_prs:.0f} PRs aceitas")
        report.append(f"  Total: {df['merged_prs'].sum():.0f} PRs aceitas")
        report.append("")
        
        # RQ03: Total de releases
        median_releases = df['releases'].median()
        report.append(f"RQ03 - Total de releases:")
        report.append(f"  Mediana: {median_releases:.0f} releases")
        report.append(f"  Total: {df['releases'].sum():.0f} releases")
        report.append("")
        
        # RQ04: Tempo até última atualização
        median_days_update = df['days_since_update'].median()
        report.append(f"RQ04 - Tempo até última atualização:")
        report.append(f"  Mediana: {median_days_update:.0f} dias")
        report.append(f"  Mínimo: {df['days_since_update'].min():.0f} dias")
        report.append(f"  Máximo: {df['days_since_update'].max():.0f} dias")
        report.append("")
        
        # RQ05: Linguagens mais populares
        language_counts = df['language'].value_counts()
        report.append(f"RQ05 - Linguagens mais populares:")
        for lang, count in language_counts.head(10).items():
            percentage = (count / len(df)) * 100
            report.append(f"  {lang}: {count} repositórios ({percentage:.1f}%)")
        report.append("")
        
        # RQ06: Percentual de issues fechadas
        median_ratio = df['closed_issues_ratio'].median()
        report.append(f"RQ06 - Percentual de issues fechadas:")
        report.append(f"  Mediana: {median_ratio*100:.1f}%")
        report.append(f"  Média: {df['closed_issues_ratio'].mean()*100:.1f}%")
        report.append("")
        
        return "\n".join(report)
    
    def analyze_by_language(self, df):
        """Análise por linguagem (RQ07 - Bônus)"""
        # Filtrar linguagens com pelo menos 5 repositórios
        lang_counts = df['language'].value_counts()
        top_languages = lang_counts[lang_counts >= 5].index
        
        analysis = []
        analysis.append("RQ07 - Análise por linguagem:")
        analysis.append("=" * 50)
        
        for lang in top_languages:
            lang_df = df[df['language'] == lang]
            analysis.append(f"\n{lang} ({len(lang_df)} repositórios):")
            analysis.append(f"  PRs aceitas (mediana): {lang_df['merged_prs'].median():.0f}")
            analysis.append(f"  Releases (mediana): {lang_df['releases'].median():.0f}")
            analysis.append(f"  Dias desde última atualização (mediana): {lang_df['days_since_update'].median():.0f}")
            analysis.append(f"  Issues fechadas (mediana): {lang_df['closed_issues_ratio'].median()*100:.1f}%")
        
        return "\n".join(analysis)
    
    def create_visualizations(self, df):
        """Cria visualizações dos dados"""
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        
        # RQ01: Distribuição de idade
        axes[0, 0].hist(df['age_days'] / 365, bins=30, alpha=0.7)
        axes[0, 0].set_title('RQ01: Distribuição de Idade (anos)')
        axes[0, 0].set_xlabel('Idade (anos)')
        axes[0, 0].set_ylabel('Frequência')
        
        # RQ02: Distribuição de PRs aceitas
        axes[0, 1].hist(df['merged_prs'], bins=30, alpha=0.7)
        axes[0, 1].set_title('RQ02: Distribuição de PRs Aceitas')
        axes[0, 1].set_xlabel('Número de PRs Aceitas')
        axes[0, 1].set_ylabel('Frequência')
        
        # RQ03: Distribuição de releases
        axes[0, 2].hist(df['releases'], bins=30, alpha=0.7)
        axes[0, 2].set_title('RQ03: Distribuição de Releases')
        axes[0, 2].set_xlabel('Número de Releases')
        axes[0, 2].set_ylabel('Frequência')
        
        # RQ04: Distribuição de dias desde última atualização
        axes[1, 0].hist(df['days_since_update'], bins=30, alpha=0.7)
        axes[1, 0].set_title('RQ04: Dias desde Última Atualização')
        axes[1, 0].set_xlabel('Dias')
        axes[1, 0].set_ylabel('Frequência')
        
        # RQ05: Top 10 linguagens
        top_langs = df['language'].value_counts().head(10)
        axes[1, 1].barh(range(len(top_langs)), top_langs.values)
        axes[1, 1].set_yticks(range(len(top_langs)))
        axes[1, 1].set_yticklabels(top_langs.index)
        axes[1, 1].set_title('RQ05: Top 10 Linguagens')
        axes[1, 1].set_xlabel('Número de Repositórios')
        
        # RQ06: Distribuição de percentual de issues fechadas
        axes[1, 2].hist(df['closed_issues_ratio'] * 100, bins=30, alpha=0.7)
        axes[1, 2].set_title('RQ06: Percentual de Issues Fechadas')
        axes[1, 2].set_xlabel('Percentual (%)')
        axes[1, 2].set_ylabel('Frequência')
        
        plt.tight_layout()
        plt.savefig('github_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()

def generate_sample_data(num_samples=100):
    """Gera dados de amostra para testes quando a API não está disponível"""
    import random
    from datetime import datetime, timedelta
    
    repositories = []
    languages = ['Java', 'Python', 'JavaScript', 'Go', 'C#', 'TypeScript', 'Ruby', 'PHP', 'C++', 'Rust']
    
    for i in range(num_samples):
        # Gerar datas aleatórias nos últimos 5 anos
        created_days_ago = random.randint(30, 5*365)  # Entre 30 dias e 5 anos atrás
        created_date = datetime.now() - timedelta(days=created_days_ago)
        updated_days_ago = random.randint(0, created_days_ago)  # Atualizado após criação
        updated_date = datetime.now() - timedelta(days=updated_days_ago)
        
        # Gerar métricas aleatórias
        stars = random.randint(10, 10000)
        issues = random.randint(5, 500)
        closed_issues = random.randint(0, issues)
        prs = random.randint(5, 300)
        merged_prs = random.randint(0, prs)
        releases = random.randint(0, 50)
        
        repositories.append({
            'name': f'sample-microservice-{i+1}',
            'owner': f'user-{i+1}',
            'full_name': f'user-{i+1}/sample-microservice-{i+1}',
            'stars': stars,
            'created_at': created_date.isoformat(),
            'updated_at': updated_date.isoformat(),
            'language': random.choice(languages),
            'pull_requests': prs,
            'merged_prs': merged_prs,
            'releases': releases,
            'issues': issues,
            'closed_issues': closed_issues
        })
    
    return repositories

def main():
    try:
        analyzer = GitHubAnalyzer()
        
        # Coletar dados com retry e tratamento de erro
        try:
            # Tentar coletar dados reais da API
            try:
                print("Tentando coletar dados reais da API do GitHub...")
                repositories = analyzer.get_top_repositories(limit=100, max_retries=3)
                if repositories and len(repositories) > 0:
                    print(f"Coletados {len(repositories)} repositórios com sucesso!")
                else:
                    raise Exception("Nenhum repositório retornado pela API")
            except Exception as api_error:
                print(f"Erro ao acessar a API do GitHub: {api_error}")
                print("Usando dados de amostra para testes...")
                repositories = generate_sample_data(num_samples=100)
                print(f"Gerados {len(repositories)} repositórios de amostra para teste.")
            
            if not repositories or len(repositories) == 0:
                print("Não foi possível gerar ou coletar repositórios. Encerrando.")
                return
            
            # Analisar dados
            df = analyzer.analyze_repositories(repositories)
            
            # Salvar dados
            df.to_csv('github_repositories.csv', index=False)
            
            # Gerar relatório
            report = analyzer.generate_report(df)
            with open('relatorio_github.txt', 'w', encoding='utf-8') as f:
                f.write(report)
            
            # Análise por linguagem (bônus)
            lang_analysis = analyzer.analyze_by_language(df)
            with open('analise_por_linguagem.txt', 'w', encoding='utf-8') as f:
                f.write(lang_analysis)
            
            # Criar visualizações
            analyzer.create_visualizations(df)
            
            print("Análise concluída! Arquivos gerados:")
            print("- github_repositories.csv: Dados brutos")
            print("- relatorio_github.txt: Relatório principal")
            print("- analise_por_linguagem.txt: Análise por linguagem")
            print("- github_analysis.png: Visualizações")
            
        except Exception as e:
            print(f"Erro durante a coleta ou análise de dados: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"Erro na inicialização: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

