import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_sample_data(n_repos=100):
    """Gera dados simulados para teste"""
    
    # Linguagens populares
    languages = ['JavaScript', 'Python', 'Java', 'TypeScript', 'C++', 'Go', 'Rust', 'PHP', 'C#', 'Ruby']
    
    # Gerar dados simulados
    data = []
    base_date = datetime.now() - timedelta(days=365*5)  # 5 anos atrás
    
    for i in range(n_repos):
        # Idade aleatória entre 1 mês e 10 anos
        age_days = random.randint(30, 3650)
        created_at = datetime.now() - timedelta(days=age_days)
        
        # Última atualização entre 1 dia e 1 ano atrás
        days_since_update = random.randint(1, 365)
        updated_at = datetime.now() - timedelta(days=days_since_update)
        
        # Número de estrelas (mais repositórios antigos têm mais estrelas)
        stars = int(random.gauss(1000 + age_days/2, 500))
        stars = max(100, stars)
        
        # PRs aceitas (correlacionado com idade e estrelas)
        merged_prs = int(random.gauss(age_days/10, 50))
        merged_prs = max(0, merged_prs)
        
        # Releases (correlacionado com idade)
        releases = int(random.gauss(age_days/100, 5))
        releases = max(0, releases)
        
        # Issues
        total_issues = int(random.gauss(100, 50))
        total_issues = max(10, total_issues)
        closed_issues = int(total_issues * random.uniform(0.6, 0.9))
        
        data.append({
            'name': f'repo_{i+1}',
            'owner': f'owner_{i+1}',
            'full_name': f'owner_{i+1}/repo_{i+1}',
            'stars': stars,
            'created_at': created_at.isoformat(),
            'updated_at': updated_at.isoformat(),
            'language': random.choice(languages),
            'pull_requests': merged_prs + random.randint(0, 50),
            'merged_prs': merged_prs,
            'releases': releases,
            'issues': total_issues,
            'closed_issues': closed_issues
        })
    
    return data

def analyze_sample_data():
    """Analisa os dados simulados"""
    
    print("Gerando dados simulados para demonstração...")
    repositories = generate_sample_data(100)
    
    # Converter para DataFrame
    df = pd.DataFrame(repositories)
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['updated_at'] = pd.to_datetime(df['updated_at'])
    
    # Calcular métricas
    df['age_days'] = (datetime.now() - df['created_at']).dt.days
    df['days_since_update'] = (datetime.now() - df['updated_at']).dt.days
    df['closed_issues_ratio'] = df['closed_issues'] / df['issues'].replace(0, 1)
    
    # Salvar dados
    df.to_csv('github_repositories_sample.csv', index=False)
    
    # Gerar relatório
    report = []
    report.append("ANÁLISE DE DADOS SIMULADOS")
    report.append("=" * 50)
    report.append(f"Total de repositórios: {len(df)}")
    report.append("")
    
    # RQ01
    median_age = df['age_days'].median()
    report.append(f"RQ01 - Idade dos repositórios:")
    report.append(f"  Mediana: {median_age:.0f} dias ({median_age/365:.1f} anos)")
    report.append("")
    
    # RQ02
    median_prs = df['merged_prs'].median()
    report.append(f"RQ02 - Pull requests aceitas:")
    report.append(f"  Mediana: {median_prs:.0f} PRs aceitas")
    report.append("")
    
    # RQ03
    median_releases = df['releases'].median()
    report.append(f"RQ03 - Total de releases:")
    report.append(f"  Mediana: {median_releases:.0f} releases")
    report.append("")
    
    # RQ04
    median_days_update = df['days_since_update'].median()
    report.append(f"RQ04 - Tempo até última atualização:")
    report.append(f"  Mediana: {median_days_update:.0f} dias")
    report.append("")
    
    # RQ05
    language_counts = df['language'].value_counts()
    report.append(f"RQ05 - Linguagens mais populares:")
    for lang, count in language_counts.head(5).items():
        percentage = (count / len(df)) * 100
        report.append(f"  {lang}: {count} repositórios ({percentage:.1f}%)")
    report.append("")
    
    # RQ06
    median_ratio = df['closed_issues_ratio'].median()
    report.append(f"RQ06 - Percentual de issues fechadas:")
    report.append(f"  Mediana: {median_ratio*100:.1f}%")
    report.append("")
    
    # Salvar relatório
    with open('relatorio_amostra.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print("Análise de dados simulados concluída!")
    print("Arquivos gerados:")
    print("- github_repositories_sample.csv")
    print("- relatorio_amostra.txt")
    
    return df

if __name__ == "__main__":
    analyze_sample_data()
