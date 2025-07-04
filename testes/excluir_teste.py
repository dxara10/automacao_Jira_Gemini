# excluir_teste.py

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

def excluir_caso_de_teste(issue_key):
    """
    Exclui permanentemente um Caso de Teste do Jira.
    """
    print(f"🔥 Tentando excluir o Caso de Teste '{issue_key}'...")

    confirmacao = input(f"🔴 ATENÇÃO: Esta ação é IRREVERSÍVEL. Tem certeza que deseja excluir o {issue_key}? (digite 'sim' para confirmar): ")
    
    if confirmacao.lower() != 'sim':
        print("🛑 Exclusão cancelada.")
        return

    api_url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}"
    auth = (JIRA_USER_EMAIL, JIRA_API_TOKEN)

    try:
        response = requests.delete(api_url, auth=auth)
        response.raise_for_status()
        print(f"✅ Caso de Teste {issue_key} excluído permanentemente.")

    except requests.exceptions.RequestException as e:
        print(f"\n❌ ERRO ao excluir o Caso de Teste.")
        if e.response:
            print(f"   Verifique se o ID '{issue_key}' está correto e se você tem permissão para excluir.")
            print(f"   Resposta: {e.response.text}")

if __name__ == "__main__":
    issue_id = input("➡️ Qual o ID do Caso de Teste a ser EXCLUÍDO? (ex: AC-123): ")
    
    if issue_id:
        excluir_caso_de_teste(issue_id.strip())
    else:
        print("ID do Caso de Teste não pode ser vazio.")