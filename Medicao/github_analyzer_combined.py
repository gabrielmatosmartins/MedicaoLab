import requests
import json
import time
import pandas as pd
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import seaborn as sns
import random
import traceback

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
        
    def get_top_repositories(self, limit=100, max_retries=5, custom_query=None):
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
        
        return repositories
    
    def analyze_repositories(self, repositories):
        """Analisa os dados dos repositórios"""
        
        # Converter para DataFrame
        df = pd.DataFrame(repositories)
        
        # Converter strings de data para objetos datetime
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['updated_at'] = pd.to_datetime(df['updated_at'])
        
        # Calcular métricas adicionais
        df['age_days'] = (datetime.now() - df['created_at']).dt.days
        df['days_since_update'] = (datetime.now() - df['updated_at']).dt.days
        
        # Calcular percentual de issues fechadas
        df['closed_issues_ratio'] = df['closed_issues'] / df['issues'].replace(0, 1)
        
        return df
    
    def generate_report(self, df):
        """Gera um relatório com as métricas principais"""
        
        report = []
        report.append("ANÁLISE DE REPOSITÓRIOS GITHUB")
        report.append("=" * 50)
        report.append(f"Total de repositórios analisados: {len(df)}")
        report.append(f"Data da análise: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # RQ01 - Idade dos repositórios
        median_age = df['age_days'].median()
        report.append(f"RQ01 - Idade dos repositórios:")
        report.append(f"  Mediana: {median_age:.0f} dias ({median_age/365:.1f} anos)")
        report.append(f"  Média: {df['age_days'].mean()/365:.1f} anos")
        report.append(f"  Mínimo: {df['age_days'].min()/365:.1f} anos")
        report.append(f"  Máximo: {df['age_days'].max()/365:.1f} anos")
        report.append("")
        
        # RQ02 - Pull requests aceitas
        median_prs = df['merged_prs'].median()
        report.append(f"RQ02 - Pull requests aceitas:")
        report.append(f"  Mediana: {median_prs:.0f} PRs aceitas")
        report.append(f"  Média: {df['merged_prs'].mean():.1f} PRs aceitas")
        report.append(f"  Mínimo: {df['merged_prs'].min():.0f} PRs aceitas")
        report.append(f"  Máximo: {df['merged_prs'].max():.0f} PRs aceitas")
        report.append("")
        
        # RQ03 - Total de releases
        median_releases = df['releases'].median()
        report.append(f"RQ03 - Total de releases:")
        report.append(f"  Mediana: {median_releases:.0f} releases")
        report.append(f"  Média: {df['releases'].mean():.1f} releases")
        report.append(f"  Mínimo: {df['releases'].min():.0f} releases")
        report.append(f"  Máximo: {df['releases'].max():.0f} releases")
        report.append("")
        
        # RQ04 - Tempo até última atualização
        median_days_update = df['days_since_update'].median()
        report.append(f"RQ04 - Tempo até última atualização:")
        report.append(f"  Mediana: {median_days_update:.0f} dias")
        report.append(f"  Média: {df['days_since_update'].mean():.1f} dias")
        report.append(f"  Mínimo: {df['days_since_update'].min():.0f} dias")
        report.append(f"  Máximo: {df['days_since_update'].max():.0f} dias")
        report.append("")
        
        # RQ05 - Linguagens mais populares
        language_counts = df['language'].value_counts()
        report.append(f"RQ05 - Linguagens mais populares:")
        for lang, count in language_counts.head(10).items():
            percentage = (count / len(df)) * 100
            report.append(f"  {lang}: {count} repositórios ({percentage:.1f}%)")
        report.append("")
        
        # RQ06 - Percentual de issues fechadas
        median_ratio = df['closed_issues_ratio'].median()
        report.append(f"RQ06 - Percentual de issues fechadas:")
        report.append(f"  Mediana: {median_ratio*100:.1f}%")
        report.append(f"  Média: {df['closed_issues_ratio'].mean()*100:.1f}%")
        report.append(f"  Mínimo: {df['closed_issues_ratio'].min()*100:.1f}%")
        report.append(f"  Máximo: {df['closed_issues_ratio'].max()*100:.1f}%")
        
        return "\n".join(report)
    
    def analyze_by_language(self, df):
        """Análise adicional por linguagem de programação"""
        
        report = []
        report.append("ANÁLISE POR LINGUAGEM DE PROGRAMAÇÃO")
        report.append("=" * 50)
        
        # Agrupar por linguagem
        grouped = df.groupby('language')
        
        # Filtrar apenas linguagens com pelo menos 3 repositórios
        filtered_groups = {lang: group for lang, group in grouped if len(group) >= 3}
        
        for lang, group in filtered_groups.items():
            report.append(f"\nLinguagem: {lang} ({len(group)} repositórios)")
            report.append("-" * 30)
            
            # Idade média
            avg_age = group['age_days'].mean() / 365
            report.append(f"Idade média: {avg_age:.1f} anos")
            
            # Estrelas médias
            avg_stars = group['stars'].mean()
            report.append(f"Estrelas médias: {avg_stars:.1f}")
            
            # PRs aceitas médias
            avg_prs = group['merged_prs'].mean()
            report.append(f"PRs aceitas médias: {avg_prs:.1f}")
            
            # Releases médias
            avg_releases = group['releases'].mean()
            report.append(f"Releases médias: {avg_releases:.1f}")
            
            # Percentual médio de issues fechadas
            avg_closed_ratio = group['closed_issues_ratio'].mean() * 100
            report.append(f"Percentual médio de issues fechadas: {avg_closed_ratio:.1f}%")
        
        return "\n".join(report)
    
    def create_visualizations(self, df):
        """Cria visualizações para as métricas principais"""
        
        # Configurar o estilo
        sns.set(style="whitegrid")
        plt.figure(figsize=(15, 12))
        
        # Criar subplots
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
        plt.close()  # Fecha a figura para evitar exibição interativa

def generate_sample_data(num_samples=100):
    """Gera dados de amostra para testes quando a API não está disponível"""
    
    # Linguagens populares
    languages = ['JavaScript', 'Python', 'Java', 'TypeScript', 'C++', 'Go', 'Rust', 'PHP', 'C#', 'Ruby']
    
    repositories = []
    
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

def main(use_sample_data=False, num_samples=100, query=None):
    """Função principal que executa a análise"""
    try:
        print("Iniciando análise de repositórios GitHub...")
        
        if use_sample_data:
            print("Usando dados simulados para análise...")
            repositories = generate_sample_data(num_samples=num_samples)
            print(f"Gerados {len(repositories)} repositórios simulados.")
            
            # Criar um analisador sem verificar o token (não será usado)
            try:
                analyzer = GitHubAnalyzer()
            except ValueError:
                # Se não tiver token, cria uma classe simplificada apenas para análise
                class SimpleAnalyzer:
                    def analyze_repositories(self, repos):
                        df = pd.DataFrame(repos)
                        df['created_at'] = pd.to_datetime(df['created_at'])
                        df['updated_at'] = pd.to_datetime(df['updated_at'])
                        df['age_days'] = (datetime.now() - df['created_at']).dt.days
                        df['days_since_update'] = (datetime.now() - df['updated_at']).dt.days
                        df['closed_issues_ratio'] = df['closed_issues'] / df['issues'].replace(0, 1)
                        return df
                    
                    def generate_report(self, df):
                        # Código simplificado do relatório
                        report = []
                        report.append("ANÁLISE DE REPOSITÓRIOS SIMULADOS")
                        report.append("=" * 50)
                        report.append(f"Total de repositórios analisados: {len(df)}")
                        report.append(f"Data da análise: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                        report.append("")
                        
                        # RQ01 - Idade dos repositórios
                        median_age = df['age_days'].median()
                        report.append(f"RQ01 - Idade dos repositórios:")
                        report.append(f"  Mediana: {median_age:.0f} dias ({median_age/365:.1f} anos)")
                        
                        # RQ02 - Pull requests aceitas
                        median_prs = df['merged_prs'].median()
                        report.append(f"RQ02 - Pull requests aceitas:")
                        report.append(f"  Mediana: {median_prs:.0f} PRs aceitas")
                        
                        # RQ03 - Total de releases
                        median_releases = df['releases'].median()
                        report.append(f"RQ03 - Total de releases:")
                        report.append(f"  Mediana: {median_releases:.0f} releases")
                        
                        # RQ04 - Tempo até última atualização
                        median_days_update = df['days_since_update'].median()
                        report.append(f"RQ04 - Tempo até última atualização:")
                        report.append(f"  Mediana: {median_days_update:.0f} dias")
                        
                        # RQ05 - Linguagens mais populares
                        language_counts = df['language'].value_counts()
                        report.append(f"RQ05 - Linguagens mais populares:")
                        for lang, count in language_counts.head(10).items():
                            percentage = (count / len(df)) * 100
                            report.append(f"  {lang}: {count} repositórios ({percentage:.1f}%)")
                        
                        # RQ06 - Percentual de issues fechadas
                        median_ratio = df['closed_issues_ratio'].median()
                        report.append(f"RQ06 - Percentual de issues fechadas:")
                        report.append(f"  Mediana: {median_ratio*100:.1f}%")
                        
                        return "\n".join(report)
                    
                    def analyze_by_language(self, df):
                        # Versão simplificada da análise por linguagem
                        report = []
                        report.append("ANÁLISE POR LINGUAGEM DE PROGRAMAÇÃO (DADOS SIMULADOS)")
                        report.append("=" * 50)
                        
                        # Agrupar por linguagem
                        grouped = df.groupby('language')
                        
                        # Filtrar apenas linguagens com pelo menos 3 repositórios
                        filtered_groups = {lang: group for lang, group in grouped if len(group) >= 3}
                        
                        for lang, group in filtered_groups.items():
                            report.append(f"\nLinguagem: {lang} ({len(group)} repositórios)")
                            report.append("-" * 30)
                            
                            # Idade média
                            avg_age = group['age_days'].mean() / 365
                            report.append(f"Idade média: {avg_age:.1f} anos")
                            
                            # Estrelas médias
                            avg_stars = group['stars'].mean()
                            report.append(f"Estrelas médias: {avg_stars:.1f}")
                        
                        return "\n".join(report)
                    
                    def create_visualizations(self, df):
                        # Versão simplificada das visualizações
                        sns.set(style="whitegrid")
                        plt.figure(figsize=(15, 12))
                        
                        # Criar subplots
                        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
                        
                        # RQ01: Distribuição de idade
                        axes[0, 0].hist(df['age_days'] / 365, bins=30, alpha=0.7)
                        axes[0, 0].set_title('RQ01: Distribuição de Idade (anos)')
                        axes[0, 0].set_xlabel('Idade (anos)')
                        axes[0, 0].set_ylabel('Frequência')
                        
                        # RQ05: Top 10 linguagens
                        top_langs = df['language'].value_counts().head(10)
                        axes[1, 1].barh(range(len(top_langs)), top_langs.values)
                        axes[1, 1].set_yticks(range(len(top_langs)))
                        axes[1, 1].set_yticklabels(top_langs.index)
                        axes[1, 1].set_title('RQ05: Top 10 Linguagens')
                        axes[1, 1].set_xlabel('Número de Repositórios')
                        
                        plt.tight_layout()
                        plt.savefig('github_analysis_sample.png', dpi=300, bbox_inches='tight')
                        plt.close()
                
                analyzer = SimpleAnalyzer()
        else:
            # Usar dados reais da API do GitHub
            try:
                analyzer = GitHubAnalyzer()
                print("Tentando coletar dados reais da API do GitHub...")
                repositories = analyzer.get_top_repositories(limit=100, max_retries=5, custom_query=query)
                print(f"Coletados {len(repositories)} repositórios com sucesso!")
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
        output_file = 'github_repositories_sample.csv' if use_sample_data else 'github_repositories.csv'
        df.to_csv(output_file, index=False)
        
        # Gerar relatório
        report = analyzer.generate_report(df)
        report_file = 'relatorio_amostra.txt' if use_sample_data else 'relatorio_github.txt'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        # Análise por linguagem (bônus)
        lang_analysis = analyzer.analyze_by_language(df)
        with open('analise_por_linguagem.txt', 'w', encoding='utf-8') as f:
            f.write(lang_analysis)
        
        # Criar visualizações
        analyzer.create_visualizations(df)
        
        print("\nAnálise concluída! Arquivos gerados:")
        print(f"- {output_file}: Dados brutos")
        print(f"- {report_file}: Relatório principal")
        print("- analise_por_linguagem.txt: Análise por linguagem")
        print("- github_analysis.png: Visualizações")
        
    except Exception as e:
        print(f"Erro durante a execução: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Analisador de repositórios GitHub')
    parser.add_argument('--sample', action='store_true', help='Usar dados simulados em vez da API do GitHub')
    parser.add_argument('--count', type=int, default=100, help='Número de repositórios a serem analisados')
    parser.add_argument('--query', type=str, help='Consulta personalizada para busca de repositórios')
    
    args = parser.parse_args()
    
    main(use_sample_data=args.sample, num_samples=args.count, query=args.query)