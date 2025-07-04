# listar_teste.py (Versão Nativa - Final)

import os
import requests
from dotenv import load_dotenv
from pathlib import Path

# --- Configuração de Caminho e Ambiente ---
script_dir = Path(__file__).parent
env_path = script_dir.parent / '.env'
load_dotenv(dotenv_path=env_path)

JIRA_URL = os.getenv("JIRA_URL")
JIRA_USER_EMAIL = os.getenv("JIRA_USER_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")

def listar_casos_de_teste():
    """
    Busca todos os Casos de Teste (issue type 'Caso de Teste') no projeto.
    """
    print(f"🔎 Buscando Casos de Teste no projeto '{JIRA_PROJECT_KEY}'...")

    # A MUDANÇA PRINCIPAL: Buscando pelo nosso tipo de item customizado
    jql_query = f'project = "{JIRA_PROJECT_KEY}" AND issuetype = "Caso de Teste" ORDER BY created DESC'
    
    api_url = f"{JIRA_URL}/rest/api/3/search"
    headers = {"Accept": "application/json"}
    auth = (JIRA_USER_EMAIL, JIRA_API_TOKEN)
    params = {'jql': jql_query, 'maxResults': 250}

    try:
        response = requests.get(api_url, headers=headers, auth=auth, params=params)
        response.raise_for_status()
        
        issues = response.json().get('issues', [])
        
        if not issues:
            print("\n✅ Nenhum Caso de Teste foi encontrado no projeto com o tipo 'Caso de Teste'.")
            return

        print("\n--- LISTA DE CASOS DE TESTE ---")
        for issue in issues:
            issue_key = issue['key']
            issue_summary = issue['fields']['summary']
            issue_status = issue['fields']['status']['name']
            issue_url = f"{JIRA_URL}/browse/{issue_key}"
            
            print(f"🔑 ID: {issue_key:<10} |  Status: {issue_status:<15} | Título: {issue_summary}")
            print(f"   🔗 Link: {issue_url}\n")
        print("="*30)

    except requests.exceptions.RequestException as e:
        print(f"\n❌ ERRO ao buscar casos de teste no Jira: {e}")
        if e.response is not None:
            print(f"   Resposta do Servidor: {e.response.text}")

if __name__ == "__main__":
    listar_casos_de_teste()