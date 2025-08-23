import requests
import time
import random
import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("GITHUB_TOKEN")
if not token:
    raise ValueError("Token do GitHub não encontrado. Verifique se o arquivo .env está configurado corretamente.")

def get_top_starred_repos_graphql(num_repos, keyword=None, batch_size=25):
    print("Consultando repositórios via GraphQL...")
    url = "https://api.github.com/graphql"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    search_query = f"stars:>1000" if not keyword else f"{keyword} stars:>100"
    
    query = """
    query ($searchQuery: String!, $numRepos: Int!, $cursor: String) {
      search(query: $searchQuery, type: REPOSITORY, first: $numRepos, after: $cursor) {
        repositoryCount
        pageInfo {
          hasNextPage
          endCursor
        }
        nodes {
          ... on Repository {
            name
            owner {
              login
              __typename
            }
            stargazerCount
            description
            url
            homepageUrl
            primaryLanguage {
              name
            }
            languages(first: 10) {
              nodes {
                name
              }
              totalCount
            }
            licenseInfo {
              name
              url
            }
            createdAt
            updatedAt
            pushedAt
            forks {
              totalCount
            }
            watchers {
              totalCount
            }
            openIssues: issues(states: OPEN) {
              totalCount
            }
            closedIssues: issues(states: CLOSED) {
              totalCount
            }
            openPullRequests: pullRequests(states: OPEN) {
              totalCount
            }
            closedPullRequests: pullRequests(states: CLOSED) {
              totalCount
            }
            mergedPullRequests: pullRequests(states: MERGED) {
              totalCount
            }
            releases {
              totalCount
            }
            defaultBranchRef {
              name
              target {
                ... on Commit {
                  history {
                    totalCount
                  }
                }
              }
            }
            diskUsage
            isArchived
            isFork
            isTemplate
            topics: repositoryTopics(first: 10) {
              nodes {
                topic {
                  name
                }
              }
            }
          }
        }
      }
    }
    """
    
    all_repos = []
    cursor = None
    remaining = num_repos
    
    while remaining > 0:
        current_batch = min(batch_size, remaining)
        print(f"Buscando lote de {current_batch} repositórios...")
        variables = {
            "numRepos": current_batch, 
            "searchQuery": search_query,
            "cursor": cursor
        }
        json_data = {"query": query, "variables": variables}
        
        max_retries = 5
        retry_count = 0
        success = False
        
        while not success and retry_count < max_retries:
            try:
                response = requests.post(url, headers=headers, json=json_data)
                if response.status_code == 200:
                    data = response.json()
                    
                    if "errors" in data:
                        print(f"GraphQL retornou erros: {data['errors']}")
                        raise Exception(f"GraphQL query returned errors: {data['errors']}")
                
                    repos_batch = data["data"]["search"]["nodes"]
                    all_repos.extend(repos_batch)
                    
                    page_info = data["data"]["search"]["pageInfo"]
                    has_next_page = page_info["hasNextPage"]
                    cursor = page_info["endCursor"]
                    
                    print(f"Obtidos {len(repos_batch)} repositórios neste lote")
                    success = True
                    
                elif response.status_code == 502 or response.status_code >= 500:
                    retry_count += 1
                    wait_time = 2 ** retry_count + random.uniform(0, 1)  # Backoff exponencial
                    print(f"Erro {response.status_code}, tentando novamente em {wait_time:.2f} segundos (tentativa {retry_count}/{max_retries})")
                    time.sleep(wait_time)
                    
                else:
                    raise Exception(f"Query failed with status code {response.status_code}: {response.text}")
                    
            except Exception as e:
                if "rate limit" in str(e).lower() or "abuse" in str(e).lower():
                    retry_count += 1
                    wait_time = 60 * retry_count 
                    print(f"Limite de taxa atingido, aguardando {wait_time} segundos...")
                    time.sleep(wait_time)
                elif retry_count < max_retries:
                    retry_count += 1
                    wait_time = 2 ** retry_count + random.uniform(0, 1)
                    print(f"Erro: {str(e)}\nTentando novamente em {wait_time:.2f} segundos (tentativa {retry_count}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    print(f"Falha após {max_retries} tentativas: {str(e)}")
                    raise
        
        if not success:
            print("Não foi possível obter dados após várias tentativas. Retornando os repositórios coletados até agora.")
            break
            
        remaining -= len(repos_batch)
        if not has_next_page or len(repos_batch) < current_batch:
            break
        time.sleep(1)
    
    print(f"Total de repositórios coletados: {len(all_repos)}")
    return all_repos


def get_top_starred_repos(num_repos):
    url = f"https://api.github.com/search/repositories?q=stars:>0&sort=stars&order=desc&per_page={num_repos}"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()["items"]
    else:
        raise Exception(f"Failed to fetch repositories: {response.status_code}")

def get_popular_repos(keyword, num_repos):
    url = f"https://api.github.com/search/repositories?q={keyword}&sort=stars&order=desc&per_page={num_repos}"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()["items"]
    else:
        raise Exception(f"Failed to fetch repositories: {response.status_code}")
def get_repo_details(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch repository details: {response.status_code}")

def get_pull_requests(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls?state=all"
    headers = {"Authorization": f"token {token}"}
    page = 1
    pull_requests = []
    while True:
        print("entrou while get_pull page: "+ str(page))
        response = requests.get(f"{url}&page={page}&per_page=100", headers=headers)
        if response.status_code == 200:
            page_pull_requests = response.json()
            if not page_pull_requests:
                print("caiu no break get_pull")
                break
            pull_requests.extend(page_pull_requests)
            page += 1
        else:
            raise Exception(f"Failed to fetch pull requests: {response.status_code}")
    return len(pull_requests)
def get_releases(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/releases"
    headers = {"Authorization": f"token {token}"}
    page = 1
    releases = []
    while True:
        print("entrou while get_release")
        response = requests.get(f"{url}?page={page}&per_page=100", headers=headers)
        if response.status_code == 200:
            page_releases = response.json()
            if not page_releases:
                print("caiu no break get_release")
                break
            releases.extend(page_releases)
            page += 1
        else:
            raise Exception(f"Failed to fetch releases: {response.status_code}")
    return len(releases)
def get_closed_issues(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/issues?state=closed"
    headers = {"Authorization": f"token {token}"}
    page = 1
    closed_issues = []
    while True:
        print("entrou while get_closed")
        response = requests.get(f"{url}&page={page}&per_page=100", headers=headers)
        if response.status_code == 200:
            page_closed_issues = response.json()
            if not page_closed_issues:
                print("caiu no break get_closed")
                break
            closed_issues.extend(page_closed_issues)
            page += 1
        else:
            raise Exception(f"Failed to fetch closed issues: {response.status_code}")
    return len(closed_issues)

def collect_and_print_repo_info(repos, filename):
    with open(filename, "w", encoding="utf-8") as f:
        for i, repo in enumerate(repos, 1):
            try:
                owner = repo["owner"]["login"]
                owner_type = repo["owner"]["__typename"]
                repo_name = repo["name"]
                
                languages = []
                if "languages" in repo and "nodes" in repo["languages"]:
                    languages = [lang["name"] for lang in repo["languages"]["nodes"]]
                
                topics = []
                if "topics" in repo and "nodes" in repo["topics"]:
                    topics = [node["topic"]["name"] for node in repo["topics"]["nodes"]]
            
                commit_count = 0
                if ("defaultBranchRef" in repo and repo["defaultBranchRef"] and 
                    "target" in repo["defaultBranchRef"] and 
                    "history" in repo["defaultBranchRef"]["target"]):
                    commit_count = repo["defaultBranchRef"]["target"]["history"]["totalCount"]
                
                f.write(f"Repositório #{i}\n")
                f.write(f"Nome: {repo_name}\n")
                f.write(f"Proprietário: {owner} (Tipo: {owner_type})\n")
                f.write(f"URL: {repo['url']}\n")
                f.write(f"Homepage: {repo.get('homepageUrl', 'N/A')}\n")
                f.write(f"Estrelas: {repo['stargazerCount']}\n")
                f.write(f"Descrição: {repo.get('description', 'N/A')}\n")
                
                f.write(f"Forks: {repo['forks']['totalCount']}\n")
                f.write(f"Watchers: {repo['watchers']['totalCount']}\n")
                f.write(f"Commits: {commit_count}\n")
                f.write(f"Issues abertas: {repo['openIssues']['totalCount']}\n")
                f.write(f"Issues fechadas: {repo['closedIssues']['totalCount']}\n")
                f.write(f"PRs abertos: {repo['openPullRequests']['totalCount']}\n")
                f.write(f"PRs fechados: {repo['closedPullRequests']['totalCount']}\n")
                f.write(f"PRs mesclados: {repo['mergedPullRequests']['totalCount']}\n")
                f.write(f"Releases: {repo['releases']['totalCount']}\n")
                
                f.write(f"Data de criação: {repo['createdAt']}\n")
                f.write(f"Última atualização: {repo['updatedAt']}\n")
                f.write(f"Último push: {repo['pushedAt']}\n")
                
                primary_language = "N/A"
                if repo["primaryLanguage"]:
                    primary_language = repo["primaryLanguage"]["name"]
                f.write(f"Linguagem principal: {primary_language}\n")
                f.write(f"Todas as linguagens: {', '.join(languages) if languages else 'N/A'}\n")
                
                license_info = "Sem licença"
                if repo["licenseInfo"]:
                    license_info = f"{repo['licenseInfo']['name']} ({repo['licenseInfo']['url']})"
                f.write(f"Licença: {license_info}\n")
                
                f.write(f"Tamanho: {repo.get('diskUsage', 'N/A')} KB\n")
                f.write(f"Branch principal: {repo['defaultBranchRef']['name'] if repo['defaultBranchRef'] else 'N/A'}\n")
                f.write(f"Arquivado: {'Sim' if repo.get('isArchived', False) else 'Não'}\n")
                f.write(f"É um fork: {'Sim' if repo.get('isFork', False) else 'Não'}\n")
                f.write(f"É um template: {'Sim' if repo.get('isTemplate', False) else 'Não'}\n")
                f.write(f"Tópicos: {', '.join(topics) if topics else 'Nenhum'}\n")
                
                f.write("-" * 100 + "\n")
            except Exception as e:
                f.write(f"Erro ao processar repositório {i}: {str(e)}\n")
                f.write("-" * 100 + "\n")

if __name__ == "__main__":
    num_repos = 100 
    batch_size = 25   
    keyword = "microservices"
    output_file = "repo_grathQL.txt"
    
    print(f"Iniciando coleta de dados para {num_repos} repositórios...")
    
    try:
        print(f"Buscando repositórios com a palavra-chave: {keyword}")
        repos = get_top_starred_repos_graphql(num_repos, keyword, batch_size)
        if not repos:
            print("Nenhum repositório encontrado!")
        else:
            print(f"Encontrados {len(repos)} repositórios. Coletando informações detalhadas...")
            collect_and_print_repo_info(repos, output_file)
            print(f"Dados salvos com sucesso em {output_file}")
            print(f"Total de repositórios processados: {len(repos)}")
        
            if num_repos < 100:
                print("\nPara coletar 100 repositórios, altere a variável 'num_repos' para 100 na função main.")
    except Exception as e:
        print(f"Erro durante a execução: {e}")
        import traceback
        traceback.print_exc()