# listar_bugs.py (Versão 2 - Lógica Aprimorada pelo Usuário)

import os
import requests
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()
JIRA_URL = os.getenv("JIRA_URL")
JIRA_USER_EMAIL = os.getenv("JIRA_USER_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")

def listar_todos_os_bugs():
    """
    Busca TODOS os bugs no projeto Jira e exibe uma lista com seus status.
    """
    print(f"🔎 Buscando todos os bugs no projeto '{JIRA_PROJECT_KEY}'...")

    # JQL (Jira Query Language) simplificada para buscar todas as issues do tipo Bug
    # Ordena pelos mais recentes primeiro
    jql_query = f'project = "{JIRA_PROJECT_KEY}" AND issuetype = Bug ORDER BY created DESC'
    
    api_url = f"{JIRA_URL}/rest/api/3/search"
    headers = {"Accept": "application/json"}
    auth = (JIRA_USER_EMAIL, JIRA_API_TOKEN)
    params = {'jql': jql_query, 'maxResults': 25} # Aumentei o limite para 25

    try:
        response = requests.get(api_url, headers=headers, auth=auth, params=params)
        response.raise_for_status()
        
        issues = response.json().get('issues', [])
        
        if not issues:
            print("✅ Nenhum bug encontrado no projeto.")
            return

        print("\n--- LISTA DE BUGS DO PROJETO ---")
        for issue in issues:
            issue_key = issue['key']
            issue_summary = issue['fields']['summary']
            # O status é um objeto, então pegamos o 'name' de dentro dele
            issue_status = issue['fields']['status']['name']
            issue_url = f"{JIRA_URL}/browse/{issue_key}"
            
            # Formatação para alinhar as colunas
            print(f"🔑 ID: {issue_key:<10} |  Status: {issue_status:<15} | Título: {issue_summary}")
            print(f"   🔗 Link: {issue_url}\n")
        print("="*30)

    except requests.exceptions.RequestException as e:
        print(f"\n❌ ERRO ao buscar bugs no Jira: {e}")
        # Se o erro for 4xx ou 5xx, a resposta pode conter mais detalhes
        if e.response is not None:
            print(f"   Resposta do Servidor: {e.response.text}")

if __name__ == "__main__":
    listar_todos_os_bugs()