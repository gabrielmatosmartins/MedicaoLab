import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.stats.proportion import proportion_confint
import scipy.stats as stats

plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def bootstrap_stat(series, statfunc=np.median, n_boot=5000, random_state=42):
    rng = np.random.RandomState(random_state)
    arr = series.dropna().values
    if len(arr) == 0:
        return np.array([np.nan, np.nan, np.nan])
    boots = [statfunc(rng.choice(arr, size=len(arr), replace=True)) for _ in range(n_boot)]
    return np.percentile(boots, [2.5, 50, 97.5])

def to_datetime_naive(series):
    dt = pd.to_datetime(series, errors='coerce', utc=True)
    return dt.dt.tz_convert(None)

def find_default_csv():

    candidates = [
        "repositorios_populares_github.csv",
        "repos.csv",
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    for f in os.listdir("."):
        if f.lower().endswith(".csv"):
            return f
    return None

def load_and_process_data(csv_path=None):
    import os

    if csv_path is None:
        for c in ["repositorios_populares_github.csv", "repos.csv"]:
            if os.path.isfile(c):
                csv_path = c
                break
        if csv_path is None:
            for f in os.listdir("."):
                if f.lower().endswith(".csv"):
                    csv_path = f
                    break
    if csv_path is None or not os.path.isfile(csv_path):
        raise FileNotFoundError("CSV não encontrado. Coloque o arquivo na pasta ou passe o caminho como argumento.")

    df = pd.read_csv(csv_path)
    print(df.columns)

    if 'data_criacao' in df.columns:
        df['created_at'] = pd.to_datetime(df['data_criacao'], errors='coerce', utc=True).dt.tz_convert(None)
    if 'ultimo_push' in df.columns:
        df['pushed_at'] = pd.to_datetime(df['ultimo_push'], errors='coerce', utc=True).dt.tz_convert(None)
    if 'ultima_atualizacao' in df.columns:
        df['updated_at'] = pd.to_datetime(df['ultima_atualizacao'], errors='coerce', utc=True).dt.tz_convert(None)

    now = pd.Timestamp.now(tz='UTC').tz_convert(None)

    if 'created_at' in df.columns:
        df['age_years'] = (now - df['created_at']).dt.days / 365.25
    if 'pushed_at' in df.columns:
        df['last_update'] = df['pushed_at']
    elif 'updated_at' in df.columns:
        df['last_update'] = df['updated_at']
    if 'last_update' in df.columns:
        df['days_since_update'] = (now - df['last_update']).dt.days

    rename_map = {
        'prs_mesclados': 'merged_pr_count',
        'releases': 'releases_count',
        'linguagem_principal': 'primary_language',
        'issues_fechadas': 'issues_closed',
        'issues_abertas': 'issues_open',
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    for col in ['merged_pr_count', 'releases_count', 'issues_closed', 'issues_open']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    if 'issues_closed' in df.columns and 'issues_open' in df.columns:
        df['total_issues'] = df['issues_closed'] + df['issues_open']
        df['issues_ratio'] = np.where(df['total_issues'] > 0,
                                      df['issues_closed'] / df['total_issues'],
                                      np.nan)

    missing = [c for c in ['age_years','days_since_update','merged_pr_count','releases_count','primary_language'] if c not in df.columns]
    if missing:
        print(f"Aviso: colunas ausentes (alguns gráficos podem ser pulados): {missing}")

    return df

def plot_h1_age_analysis(df):
    if 'age_years' not in df.columns:
        print("H1: pulado (coluna 'age_years' ausente).")
        return
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
    sns.histplot(df['age_years'], bins=30, ax=ax1, alpha=0.7)
    ax1.axvline(5, color='red', linestyle='--', label='5 anos')
    ax1.axvline(df['age_years'].median(), color='green', linestyle='-', label=f"Mediana: {df['age_years'].median():.1f}")
    ax1.set_title('H1: Idade dos Repositórios'); ax1.legend()
    sns.boxplot(y=df['age_years'], ax=ax2)
    ax2.axhline(5, color='red', linestyle='--'); ax2.set_title('Boxplot - Idade')
    plt.tight_layout(); plt.savefig('h1_idade_repositorios.png', dpi=300, bbox_inches='tight'); plt.show()

def plot_h2_prs_analysis(df):
    if 'merged_pr_count' not in df.columns:
        print("H2: pulado (coluna 'merged_pr_count' ausente).")
        return
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
    prs = df['merged_pr_count']
    sns.histplot(np.log1p(prs[prs > 0]), bins=30, ax=ax1, alpha=0.7)
    ax1.axvline(np.log1p(100), color='red', linestyle='--', label='100 PRs')
    ax1.axvline(np.log1p(prs.median()), color='green', label=f"Mediana {prs.median():.0f}")
    ax1.set_title("H2: PRs Mescladas (log)"); ax1.legend()
    sns.boxplot(x=np.log1p(prs), ax=ax2)
    ax2.axvline(np.log1p(100), color='red', linestyle='--'); ax2.set_title("Boxplot de PRs")
    plt.tight_layout(); plt.savefig("h2_prs_mescladas.png", dpi=300, bbox_inches='tight'); plt.show()
    ic = bootstrap_stat(prs, np.median)
    print(f"H2 - Mediana: {prs.median():.0f}, IC95% [{ic[0]:.0f}, {ic[2]:.0f}]")

def plot_h3_releases_analysis(df):
    if 'releases_count' not in df.columns:
        print("H3: pulado (coluna 'releases_count' ausente).")
        return
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
    releases = df['releases_count']
    sns.histplot(releases, bins=30, ax=ax1, alpha=0.7)
    ax1.axvline(10, color='red', linestyle='--', label='10 releases')
    ax1.axvline(releases.median(), color='green', label=f"Mediana {releases.median():.0f}")
    ax1.legend(); ax1.set_title("H3: Distribuição de Releases")
    sns.boxplot(x=releases, ax=ax2); ax2.axvline(10, color='red', linestyle='--'); ax2.set_title("Boxplot - Releases")
    plt.tight_layout(); plt.savefig("h3_releases.png", dpi=300, bbox_inches='tight'); plt.show()
    ic = bootstrap_stat(releases, np.median)
    print(f"H3 - Mediana: {releases.median():.0f}, IC95% [{ic[0]:.0f}, {ic[2]:.0f}]")

def plot_h4_updates_analysis(df):
    if 'days_since_update' not in df.columns:
        print("H4: pulado (coluna 'days_since_update' ausente).")
        return
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
    days = df['days_since_update']
    sns.histplot(days, bins=30, ax=ax1, alpha=0.7)
    ax1.axvline(90, color='red', linestyle='--', label='90 dias')
    ax1.legend(); ax1.set_title('H4: Dias desde última atualização')
    sorted_days = np.sort(days.dropna()); y = np.arange(1,len(sorted_days)+1)/len(sorted_days)
    ax2.plot(sorted_days, y); ax2.axvline(90, color='red', linestyle='--'); ax2.set_title("CDF Atualizações")
    plt.tight_layout(); plt.savefig("h4_atualizacoes.png", dpi=300, bbox_inches='tight'); plt.show()
    k = (days <= 90).sum(); n = days.notna().sum()
    if n > 0:
        ci_low, ci_upp = proportion_confint(k, n, method='wilson')
        print(f"H4 - Atualizados ≤90d: {k}/{n} ({k/n*100:.1f}%) | IC95% [{ci_low*100:.1f}%, {ci_upp*100:.1f}%]")

def plot_h5_languages_analysis(df):
    if 'primary_language' not in df.columns:
        print("H5: pulado (coluna 'primary_language' ausente).")
        return
    fig, axes = plt.subplots(2, 2, figsize=(16,12))
    top_langs = df['primary_language'].value_counts().head(10)
    sns.barplot(x=top_langs.values, y=top_langs.index, ax=axes[0,0])
    axes[0,0].set_title("H5: Top 10 Linguagens")
    axes[0,1].pie(list(top_langs.head(5).values) + [top_langs.iloc[5:].sum()],
                  labels=list(top_langs.head(5).index) + ['Outras'],
                  autopct="%1.1f%%", startangle=90)
    axes[0,1].set_title("Top 5 Linguagens")
    top5 = df[df['primary_language'].isin(top_langs.head(5).index)]
    if 'merged_pr_count' in df.columns:
        sns.boxplot(data=top5, x="primary_language", y="merged_pr_count", ax=axes[1,0])
        axes[1,0].set_yscale("log"); axes[1,0].set_title("PRs por Linguagem")
    else:
        axes[1,0].set_visible(False)
    if 'releases_count' in df.columns:
        sns.boxplot(data=top5, x="primary_language", y="releases_count", ax=axes[1,1])
        axes[1,1].set_yscale("log"); axes[1,1].set_title("Releases por Linguagem")
    else:
        axes[1,1].set_visible(False)
    plt.tight_layout(); plt.savefig("h5_linguagens.png", dpi=300, bbox_inches='tight'); plt.show()
    js_py_ts = df['primary_language'].isin(['JavaScript','Python','TypeScript']).sum()
    total = len(df)
    print(f"H5 - JS+Py+TS: {js_py_ts}/{total} ({js_py_ts/total*100:.1f}%)")

def plot_h6_issues_analysis(df):
    if 'issues_ratio' not in df.columns:
        print("H6: pulado (colunas de issues ausentes).")
        return
    fig,(ax1,ax2)=plt.subplots(1,2,figsize=(15,5))
    sns.histplot(df['issues_ratio'], bins=30, ax=ax1, alpha=0.7)
    ax1.axvline(0.7, color='red', linestyle='--', label='70%')
    ax1.axvline(df['issues_ratio'].median(), color='green', label=f"Mediana {df['issues_ratio'].median():.2f}")
    ax1.legend(); ax1.set_title("H6: % Issues Fechadas")
    sns.boxplot(y=df['issues_ratio'], ax=ax2); ax2.axhline(0.7, color='red', linestyle='--'); ax2.set_title("Boxplot - Issues")
    plt.tight_layout(); plt.savefig("h6_issues.png",dpi=300,bbox_inches='tight'); plt.show()
    ic = bootstrap_stat(df['issues_ratio'].dropna(), np.median)
    print(f"H6 - Mediana: {df['issues_ratio'].median():.2f}, IC95% [{ic[0]:.2f},{ic[2]:.2f}]")

def plot_rq07_bonus(df):
    if 'primary_language' not in df.columns:
        print("RQ07: pulado (coluna 'primary_language' ausente).")
        return
    top_langs=df['primary_language'].value_counts().head(5).index
    subset=df[df['primary_language'].isin(top_langs)]
    fig,axes=plt.subplots(1,3,figsize=(18,6))
    if 'merged_pr_count' in df.columns:
        sns.boxplot(data=subset,x="primary_language",y="merged_pr_count",ax=axes[0]); axes[0].set_yscale("log")
        axes[0].set_title("PRs por linguagem")
    else:
        axes[0].set_visible(False)
    if 'releases_count' in df.columns:
        sns.boxplot(data=subset,x="primary_language",y="releases_count",ax=axes[1]); axes[1].set_yscale("log")
        axes[1].set_title("Releases por linguagem")
    else:
        axes[1].set_visible(False)
    if 'days_since_update' in df.columns:
        sns.boxplot(data=subset,x="primary_language",y="days_since_update",ax=axes[2]); axes[2].set_yscale("log")
        axes[2].set_title("Atualizações por linguagem")
    else:
        axes[2].set_visible(False)
    plt.tight_layout(); plt.savefig("rq07_por_linguagem.png",dpi=300,bbox_inches='tight'); plt.show()
    print("RQ07 - Kruskal-Wallis:")
    for var in ["merged_pr_count","releases_count","days_since_update"]:
        if var in df.columns:
            groups=[g[var].values for _,g in subset.groupby("primary_language")]
            if all(len(g)>0 for g in groups):
                p=stats.kruskal(*groups).pvalue
                print(f"{var}: p-value={p:.4f}")

def generate_summary_report(df):
    print("="*60, "\nRESUMO HIPÓTESES\n", "="*60)
    if 'age_years' in df.columns:
        print(f"H1 Média idade={df['age_years'].mean():.2f} anos | >5 anos={(df['age_years']>5).mean()*100:.1f}%")
    if 'merged_pr_count' in df.columns:
        ic = bootstrap_stat(df['merged_pr_count'], np.median)
        print(f"H2 Mediana PRs={df['merged_pr_count'].median():.0f} | IC95% [{ic[0]:.0f},{ic[2]:.0f}]")
    if 'releases_count' in df.columns:
        ic = bootstrap_stat(df['releases_count'], np.median)
        print(f"H3 Mediana Releases={df['releases_count'].median():.0f} | IC95% [{ic[0]:.0f},{ic[2]:.0f}]")
    if 'days_since_update' in df.columns:
        pct = (df['days_since_update']<=90).mean()*100
        print(f"H4 Atualizados ≤90d={pct:.1f}%")
    if 'primary_language' in df.columns:
        js_py_ts=(df['primary_language'].isin(['JavaScript','Python','TypeScript']).mean()*100)
        print(f"H5 Linguagens JS+Py+TS={js_py_ts:.1f}%")
    if 'issues_ratio' in df.columns:
        ic = bootstrap_stat(df['issues_ratio'].dropna(), np.median)
        print(f"H6 Issues fechadas (mediana)={df['issues_ratio'].median():.2f} | IC95% [{ic[0]:.2f},{ic[2]:.2f}]")
    print("="*60)

def main():
    csv_arg = sys.argv[1] if len(sys.argv) > 1 else None
    print("Carregando dados...")
    df = load_and_process_data(csv_arg)

    print(f"Dataset carregado: {len(df)} repositórios\n\nGerando gráficos das hipóteses...")

    plot_h1_age_analysis(df)
    plot_h2_prs_analysis(df)
    plot_h3_releases_analysis(df)
    plot_h4_updates_analysis(df)
    plot_h5_languages_analysis(df)
    plot_h6_issues_analysis(df)
    plot_rq07_bonus(df)

    generate_summary_report(df)

    print("\nGráficos salvos como PNG:")
    print("- h1_idade_repositorios.png")
    print("- h2_prs_mescladas.png")
    print("- h3_releases.png")
    print("- h4_atualizacoes.png")
    print("- h5_linguagens.png")
    print("- h6_issues.png")
    print("- rq07_por_linguagem.png")

if __name__ == "__main__":
    main()