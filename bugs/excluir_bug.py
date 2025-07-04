# excluir_bug.py

import os
import requests
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()
JIRA_URL = os.getenv("JIRA_URL")
JIRA_USER_EMAIL = os.getenv("JIRA_USER_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

def excluir_bug(issue_key):
    """
    Exclui permanentemente uma issue (bug) do Jira.
    """
    print(f"🔥 Tentando excluir o bug '{issue_key}'...")

    # Confirmação de segurança
    confirmacao = input(f"🔴 ATENÇÃO: Esta ação é IRREVERSÍVEL. Tem certeza que deseja excluir o bug {issue_key}? (digite 'sim' para confirmar): ")
    
    if confirmacao.lower() != 'sim':
        print("🛑 Exclusão cancelada.")
        return

    api_url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}"
    auth = (JIRA_USER_EMAIL, JIRA_API_TOKEN)

    try:
        response = requests.delete(api_url, auth=auth)
        response.raise_for_status() # Lança erro se status for 4xx ou 5xx
        print(f"✅ Bug {issue_key} excluído permanentemente.")

    except requests.exceptions.RequestException as e:
        print(f"\n❌ ERRO ao excluir o bug: {e}")
        print(f"   Verifique se o ID '{issue_key}' está correto e se você tem permissão para excluir.")
        print(f"   Resposta: {e.response.text}")

if __name__ == "__main__":
    issue_id = input("➡️ Qual o ID do bug a ser EXCLUÍDO? (ex: AC-123): ")
    
    if issue_id:
        excluir_bug(issue_id)
    else:
        print("ID do bug não pode ser vazio.")