import os
import sys
import time
from dotenv import load_dotenv

# Importar a função de paginação do main.py
from main import get_top_starred_repos_graphql

# Carregar o token do GitHub do arquivo .env
load_dotenv()
token = os.getenv("GITHUB_TOKEN")

def test_paginacao():
    print("Testando a implementação da paginação...")
    
    # Teste 1: Verificar se consegue buscar 50 repositórios com batch_size=10
    print("\nTeste 1: Buscar 50 repositórios com batch_size=10")
    test_repos = 50
    test_batch_size = 10
    
    try:
        start_time = time.time()
        repos = get_top_starred_repos_graphql(test_repos, "", test_batch_size)
        end_time = time.time()
        
        print(f"Tempo de execução: {end_time - start_time:.2f} segundos")
        print(f"Número de repositórios retornados: {len(repos)}")
        
        if len(repos) == test_repos:
            print("✅ Teste 1 passou: Número correto de repositórios retornados")
        else:
            print(f"❌ Teste 1 falhou: Esperado {test_repos}, obtido {len(repos)}")
            
    except Exception as e:
        print(f"❌ Teste 1 falhou com erro: {str(e)}")
    
    # Teste 2: Verificar se consegue buscar 100 repositórios com batch_size=50
    print("\nTeste 2: Buscar 100 repositórios com batch_size=50")
    test_repos = 100
    test_batch_size = 50
    
    try:
        start_time = time.time()
        repos = get_top_starred_repos_graphql(test_repos, "", test_batch_size)
        end_time = time.time()
        
        print(f"Tempo de execução: {end_time - start_time:.2f} segundos")
        print(f"Número de repositórios retornados: {len(repos)}")
        
        if len(repos) == test_repos:
            print("✅ Teste 2 passou: Número correto de repositórios retornados")
        else:
            print(f"❌ Teste 2 falhou: Esperado {test_repos}, obtido {len(repos)}")
            
    except Exception as e:
        print(f"❌ Teste 2 falhou com erro: {str(e)}")
    
    print("\nTestes de paginação concluídos.")

if __name__ == "__main__":
    if not token:
        print("Erro: Token do GitHub não encontrado no arquivo .env")
        print("Por favor, configure o token conforme as instruções no README.md")
        sys.exit(1)
        
    test_paginacao()