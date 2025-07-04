# buscar_teste.py

import os
import requests
import json
from dotenv import load_dotenv
from pathlib import Path

# --- Configuração Padrão ---
script_dir = Path(__file__).parent
env_path = script_dir.parent / '.env'
load_dotenv(dotenv_path=env_path)

JIRA_URL = os.getenv("JIRA_URL")
JIRA_USER_EMAIL = os.getenv("JIRA_USER_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

def buscar_e_exibir_teste(issue_key):
    """
    Busca uma issue específica pelo seu ID/Chave e exibe seus detalhes.
    """
    print(f"\n🔎 Buscando dados do Caso de Teste '{issue_key}'...")
    
    # Este é o endpoint da API para buscar uma issue específica
    api_url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}"
    auth = (JIRA_USER_EMAIL, JIRA_API_TOKEN)
    headers = {"Accept": "application/json"}
    
    try:
        response = requests.get(api_url, headers=headers, auth=auth)
        response.raise_for_status() # Lança um erro se a requisição falhar (ex: 404)
        
        data = response.json()
        fields = data.get('fields', {})
        
        # --- Extraindo os Dados ---
        titulo = fields.get('summary', 'N/D')
        status = fields.get('status', {}).get('name', 'N/D')
        criador = fields.get('creator', {}).get('displayName', 'N/D')
        responsavel = fields.get('assignee')
        if responsavel:
            responsavel_nome = responsavel.get('displayName', 'N/D')
        else:
            responsavel_nome = "Não atribuído"
            
        etiquetas = ", ".join(fields.get('labels', [])) or "Nenhuma"
        
        # Extrai o texto do campo Descrição, que está em um formato complexo (ADF)
        descricao = ""
        if fields.get('description') and fields['description'].get('content'):
            for content_block in fields['description']['content']:
                if content_block.get('type') == 'paragraph':
                    for text_content in content_block.get('content', []):
                        descricao += text_content.get('text', '')
                    descricao += "\n\n" # Adiciona uma quebra de linha entre parágrafos

        # --- Exibindo os Dados ---
        print("\n" + "="*60)
        print(f"🔍 DETALHES DO CASO DE TESTE: {issue_key}")
        print("="*60)
        
        print(f"➡️ Título: {titulo}")
        print(f"➡️ Status: {status}")
        print(f"➡️ Link: {JIRA_URL}/browse/{issue_key}")
        print(f"➡️ Criador: {criador}")
        print(f"➡️ Responsável: {responsavel_nome}")
        print(f"➡️ Etiquetas: [{etiquetas}]")
        
        print("\n--- DESCRIÇÃO ---")
        print(descricao.strip())
        print("\n" + "="*60)

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"❌ ERRO: Caso de Teste com o ID '{issue_key}' não encontrado.")
        else:
            print(f"❌ ERRO HTTP: {e}")
            print(f"   Resposta: {e.response.text}")
    except Exception as e:
        print(f"❌ Ocorreu um erro inesperado: {e}")


def main():
    issue_id = input("➡️ Por favor, informe o ID do Caso de Teste (ex: AC-6): ").strip()
    if issue_id:
        buscar_e_exibir_teste(issue_id)
    else:
        print("ID não pode ser vazio.")

if __name__ == "__main__":
    main()