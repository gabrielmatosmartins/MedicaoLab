import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import warnings

# Ignorar avisos para manter a saída limpa
warnings.filterwarnings('ignore')

# Configurar o estilo dos gráficos
sns.set(style="whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 12

def carregar_dados(arquivo_csv):
    """Carrega os dados do arquivo CSV e realiza pré-processamento."""
    print(f"Carregando dados do arquivo {arquivo_csv}...")
    
    # Verificar se o arquivo existe
    if not os.path.exists(arquivo_csv):
        print(f"Erro: O arquivo {arquivo_csv} não foi encontrado.")
        print("Execute primeiro o script main.py para coletar os dados.")
        return None
    
    # Carregar os dados
    df = pd.read_csv(arquivo_csv)
    print(f"Dados carregados com sucesso. Total de {len(df)} repositórios.")
    
    # Converter datas para datetime
    for col in ['criado_em', 'atualizado_em', 'ultimo_push']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])
    
    # Calcular idade em dias (caso não esteja já calculada)
    if 'idade_dias' not in df.columns:
        df['idade_dias'] = (datetime.now() - df['criado_em']).dt.days
    
    # Calcular tempo desde a última atualização em dias
    df['dias_desde_atualizacao'] = (datetime.now() - df['atualizado_em']).dt.days
    
    # Converter colunas numéricas
    colunas_numericas = ['estrelas', 'forks', 'watchers', 'commits', 
                        'issues_abertas', 'issues_fechadas', 'prs_abertos', 
                        'prs_fechados', 'prs_mesclados', 'releases']
    
    for col in colunas_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Contar tópicos
    if 'topicos' in df.columns:
        df['num_topicos'] = df['topicos'].apply(lambda x: 0 if x == 'Nenhum' else len(str(x).split(', ')))
    
    # Contar linguagens
    if 'linguagens' in df.columns:
        df['num_linguagens'] = df['linguagens'].apply(lambda x: 0 if x == 'N/A' else len(str(x).split(', ')))
    
    return df

def analisar_h1(df):
    """Analisa H1: Sistemas populares são maduros/antigos?"""
    print("\n--- Análise H1: Sistemas populares são maduros/antigos? ---")
    
    # Estatísticas descritivas da idade
    idade_anos = df['idade_dias'] / 365.25
    print(f"Idade média dos repositórios: {idade_anos.mean():.2f} anos")
    print(f"Idade mediana dos repositórios: {idade_anos.median():.2f} anos")
    print(f"Desvio padrão da idade: {idade_anos.std():.2f} anos")
    print(f"Idade mínima: {idade_anos.min():.2f} anos")
    print(f"Idade máxima: {idade_anos.max():.2f} anos")
    
    # Criar pasta para resultados se não existir
    os.makedirs('resultados', exist_ok=True)
    
    # Histograma da idade dos repositórios
    plt.figure(figsize=(12, 6))
    sns.histplot(idade_anos, bins=30, kde=True)
    plt.title('Distribuição da Idade dos Repositórios Populares')
    plt.xlabel('Idade (anos)')
    plt.ylabel('Número de Repositórios')
    plt.axvline(x=5, color='red', linestyle='--', label='Hipótese: 5 anos')
    plt.axvline(x=idade_anos.median(), color='green', linestyle='-', label=f'Mediana: {idade_anos.median():.2f} anos')
    plt.legend()
    plt.savefig('resultados/h1_idade_repositorios.png')
    
    # Verificar a hipótese
    hipotese_confirmada = idade_anos.median() > 5
    print(f"Hipótese H1 {'confirmada' if hipotese_confirmada else 'refutada'}: ")
    print(f"A idade mediana dos repositórios populares é {'superior' if hipotese_confirmada else 'inferior'} a 5 anos.")
    
    return hipotese_confirmada

def analisar_h2(df):
    """Analisa H2: Sistemas populares recebem muita contribuição externa?"""
    print("\n--- Análise H2: Sistemas populares recebem muita contribuição externa? ---")
    
    # Estatísticas descritivas dos PRs mesclados
    print(f"Média de PRs mesclados: {df['prs_mesclados'].mean():.2f}")
    print(f"Mediana de PRs mesclados: {df['prs_mesclados'].median():.2f}")
    print(f"Desvio padrão de PRs mesclados: {df['prs_mesclados'].std():.2f}")
    print(f"Mínimo de PRs mesclados: {df['prs_mesclados'].min():.2f}")
    print(f"Máximo de PRs mesclados: {df['prs_mesclados'].max():.2f}")
    
    # Histograma dos PRs mesclados
    plt.figure(figsize=(12, 6))
    sns.histplot(df['prs_mesclados'], bins=30, kde=True)
    plt.title('Distribuição de Pull Requests Mesclados em Repositórios Populares')
    plt.xlabel('Número de PRs Mesclados')
    plt.ylabel('Número de Repositórios')
    plt.axvline(x=100, color='red', linestyle='--', label='Hipótese: 100 PRs')
    plt.axvline(x=df['prs_mesclados'].median(), color='green', linestyle='-', label=f'Mediana: {df["prs_mesclados"].median():.2f} PRs')
    plt.legend()
    plt.savefig('resultados/h2_prs_mesclados.png')
    
    # Gráfico de dispersão entre estrelas e PRs mesclados
    plt.figure(figsize=(12, 6))
    sns.scatterplot(x='estrelas', y='prs_mesclados', data=df)
    plt.title('Relação entre Número de Estrelas e Pull Requests Mesclados')
    plt.xlabel('Número de Estrelas')
    plt.ylabel('Número de PRs Mesclados')
    plt.savefig('resultados/h2_estrelas_vs_prs.png')
    
    # Verificar a hipótese
    hipotese_confirmada = df['prs_mesclados'].median() > 100
    print(f"Hipótese H2 {'confirmada' if hipotese_confirmada else 'refutada'}: ")
    print(f"A mediana de PRs mesclados em repositórios populares é {'superior' if hipotese_confirmada else 'inferior'} a 100.")
    
    return hipotese_confirmada

def analisar_h3(df):
    """Analisa H3: Sistemas populares lançam releases com frequência?"""
    print("\n--- Análise H3: Sistemas populares lançam releases com frequência? ---")
    
    # Estatísticas descritivas das releases
    print(f"Média de releases: {df['releases'].mean():.2f}")
    print(f"Mediana de releases: {df['releases'].median():.2f}")
    print(f"Desvio padrão de releases: {df['releases'].std():.2f}")
    print(f"Mínimo de releases: {df['releases'].min():.2f}")
    print(f"Máximo de releases: {df['releases'].max():.2f}")
    
    # Histograma das releases
    plt.figure(figsize=(12, 6))
    sns.histplot(df['releases'], bins=30, kde=True)
    plt.title('Distribuição de Releases em Repositórios Populares')
    plt.xlabel('Número de Releases')
    plt.ylabel('Número de Repositórios')
    plt.axvline(x=10, color='red', linestyle='--', label='Hipótese: 10 releases')
    plt.axvline(x=df['releases'].median(), color='green', linestyle='-', label=f'Mediana: {df["releases"].median():.2f} releases')
    plt.legend()
    plt.savefig('resultados/h3_releases.png')
    
    # Gráfico de dispersão entre idade e número de releases
    plt.figure(figsize=(12, 6))
    sns.scatterplot(x='idade_dias', y='releases', data=df)
    plt.title('Relação entre Idade do Repositório e Número de Releases')
    plt.xlabel('Idade (dias)')
    plt.ylabel('Número de Releases')
    plt.savefig('resultados/h3_idade_vs_releases.png')
    
    # Verificar a hipótese
    hipotese_confirmada = df['releases'].median() > 10
    print(f"Hipótese H3 {'confirmada' if hipotese_confirmada else 'refutada'}: ")
    print(f"A mediana de releases em repositórios populares é {'superior' if hipotese_confirmada else 'inferior'} a 10.")
    
    return hipotese_confirmada

def analisar_h4(df):
    """Analisa H4: Sistemas populares são atualizados com frequência?"""
    print("\n--- Análise H4: Sistemas populares são atualizados com frequência? ---")
    
    # Estatísticas descritivas do tempo desde a última atualização
    print(f"Média de dias desde a última atualização: {df['dias_desde_atualizacao'].mean():.2f}")
    print(f"Mediana de dias desde a última atualização: {df['dias_desde_atualizacao'].median():.2f}")
    print(f"Desvio padrão de dias desde a última atualização: {df['dias_desde_atualizacao'].std():.2f}")
    print(f"Mínimo de dias desde a última atualização: {df['dias_desde_atualizacao'].min():.2f}")
    print(f"Máximo de dias desde a última atualização: {df['dias_desde_atualizacao'].max():.2f}")
    
    # Histograma do tempo desde a última atualização
    plt.figure(figsize=(12, 6))
    sns.histplot(df['dias_desde_atualizacao'], bins=30, kde=True)
    plt.title('Distribuição do Tempo desde a Última Atualização em Repositórios Populares')
    plt.xlabel('Dias desde a Última Atualização')
    plt.ylabel('Número de Repositórios')
    plt.axvline(x=90, color='red', linestyle='--', label='Hipótese: 90 dias (3 meses)')
    plt.axvline(x=df['dias_desde_atualizacao'].median(), color='green', linestyle='-', 
               label=f'Mediana: {df["dias_desde_atualizacao"].median():.2f} dias')
    plt.legend()
    plt.savefig('resultados/h4_tempo_atualizacao.png')
    
    # Verificar a hipótese
    hipotese_confirmada = df['dias_desde_atualizacao'].median() < 90  # 3 meses = 90 dias
    print(f"Hipótese H4 {'confirmada' if hipotese_confirmada else 'refutada'}: ")
    print(f"A mediana de dias desde a última atualização em repositórios populares é {'inferior' if hipotese_confirmada else 'superior'} a 90 dias (3 meses).")
    
    return hipotese_confirmada

def analisar_h5(df):
    """Analisa H5: Sistemas populares são escritos nas linguagens mais populares?"""
    print("\n--- Análise H5: Sistemas populares são escritos nas linguagens mais populares? ---")
    
    # Contar as linguagens principais
    linguagens_count = df['linguagem_principal'].value_counts().reset_index()
    linguagens_count.columns = ['linguagem', 'contagem']
    linguagens_count = linguagens_count.sort_values('contagem', ascending=False)
    
    # Top 10 linguagens
    top_linguagens = linguagens_count.head(10)
    print("Top 10 linguagens mais utilizadas:")
    for i, row in top_linguagens.iterrows():
        print(f"{row['linguagem']}: {row['contagem']} repositórios ({row['contagem']/len(df)*100:.2f}%)")
    
    # Gráfico de barras das linguagens principais
    plt.figure(figsize=(14, 8))
    sns.barplot(x='linguagem', y='contagem', data=top_linguagens)
    plt.title('Top 10 Linguagens Principais em Repositórios Populares')
    plt.xlabel('Linguagem')
    plt.ylabel('Número de Repositórios')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('resultados/h5_linguagens_principais.png')
    
    # Verificar se JavaScript, Python e TypeScript estão entre as 3 linguagens mais populares
    top3_linguagens = set(top_linguagens.head(3)['linguagem'].tolist())
    hipotese_linguagens = {'JavaScript', 'Python', 'TypeScript'}
    linguagens_em_comum = top3_linguagens.intersection(hipotese_linguagens)
    
    hipotese_confirmada = len(linguagens_em_comum) >= 2  # Pelo menos 2 das 3 linguagens hipotéticas estão no top 3
    print(f"Hipótese H5 {'confirmada' if hipotese_confirmada else 'refutada'}: ")
    print(f"Das linguagens JavaScript, Python e TypeScript, {len(linguagens_em_comum)} estão entre as 3 mais populares.")
    
    return hipotese_confirmada

def analisar_rq07(df):
    """Analisa RQ07: Sistemas escritos em linguagens mais populares recebem mais contribuição externa, 
    lançam mais releases e são atualizados com mais frequência?"""
    print("\n--- Análise RQ07 (Bônus): Relação entre linguagem e contribuições, releases e atualizações ---")
    
    # Obter as 5 linguagens mais populares
    top_linguagens = df['linguagem_principal'].value_counts().head(5).index.tolist()
    print(f"Analisando as 5 linguagens mais populares: {', '.join(top_linguagens)}")
    
    # Filtrar apenas repositórios com essas linguagens
    df_top_langs = df[df['linguagem_principal'].isin(top_linguagens)]
    
    # Análise de PRs mesclados por linguagem
    plt.figure(figsize=(14, 8))
    sns.boxplot(x='linguagem_principal', y='prs_mesclados', data=df_top_langs)
    plt.title('Pull Requests Mesclados por Linguagem Principal')
    plt.xlabel('Linguagem')
    plt.ylabel('Número de PRs Mesclados')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('resultados/rq07_prs_por_linguagem.png')
    
    # Análise de releases por linguagem
    plt.figure(figsize=(14, 8))
    sns.boxplot(x='linguagem_principal', y='releases', data=df_top_langs)
    plt.title('Número de Releases por Linguagem Principal')
    plt.xlabel('Linguagem')
    plt.ylabel('Número de Releases')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('resultados/rq07_releases_por_linguagem.png')
    
    # Análise de tempo desde a última atualização por linguagem
    plt.figure(figsize=(14, 8))
    sns.boxplot(x='linguagem_principal', y='dias_desde_atualizacao', data=df_top_langs)
    plt.title('Dias desde a Última Atualização por Linguagem Principal')
    plt.xlabel('Linguagem')
    plt.ylabel('Dias desde a Última Atualização')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('resultados/rq07_atualizacao_por_linguagem.png')
    
    # Estatísticas por linguagem
    print("\nEstatísticas por linguagem:")
    for lang in top_linguagens:
        df_lang = df[df['linguagem_principal'] == lang]
        print(f"\n{lang} ({len(df_lang)} repositórios):")
        print(f"  - PRs mesclados (mediana): {df_lang['prs_mesclados'].median():.2f}")
        print(f"  - Releases (mediana): {df_lang['releases'].median():.2f}")
        print(f"  - Dias desde última atualização (mediana): {df_lang['dias_desde_atualizacao'].median():.2f}")

def gerar_estatisticas_descritivas(df):
    """Gera estatísticas descritivas para as colunas numéricas."""
    print("\n--- Gerando estatísticas descritivas ---")
    
    # Selecionar colunas numéricas
    colunas_numericas = ['estrelas', 'forks', 'watchers', 'commits', 
                        'issues_abertas', 'issues_fechadas', 'prs_abertos', 
                        'prs_fechados', 'prs_mesclados', 'releases', 
                        'idade_dias', 'dias_desde_atualizacao']
    
    # Filtrar apenas colunas que existem no DataFrame
    colunas_existentes = [col for col in colunas_numericas if col in df.columns]
    
    # Calcular estatísticas
    estatisticas = df[colunas_existentes].describe()
    
    # Salvar estatísticas em CSV
    estatisticas.to_csv('resultados/estatisticas_descritivas.csv')
    print(f"Estatísticas descritivas salvas em 'resultados/estatisticas_descritivas.csv'")
    
    return estatisticas

def main():
    # Criar pasta para resultados
    os.makedirs('resultados', exist_ok=True)
    
    # Carregar dados
    arquivo_csv = "repositorios_github.csv"
    df = carregar_dados(arquivo_csv)
    
    if df is None:
        return
    
    # Gerar estatísticas descritivas
    estatisticas = gerar_estatisticas_descritivas(df)
    
    # Analisar hipóteses
    resultados = {
        'H1': analisar_h1(df),
        'H2': analisar_h2(df),
        'H3': analisar_h3(df),
        'H4': analisar_h4(df),
        'H5': analisar_h5(df)
    }
    
    # Análise bônus (RQ07)
    analisar_rq07(df)
    
    # Resumo dos resultados
    print("\n--- Resumo dos Resultados ---")
    for hipotese, confirmada in resultados.items():
        print(f"{hipotese}: {'Confirmada' if confirmada else 'Refutada'}")
    
    print("\nAnálise concluída! Os resultados foram salvos na pasta 'resultados/'")

if __name__ == "__main__":
    main()