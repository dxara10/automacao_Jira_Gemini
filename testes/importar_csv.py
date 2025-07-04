# importar_csv.py (Versão Nativa - Final)

import os
import requests
import json
import csv
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

def detectar_formato(headers):
    """Analisa os cabeçalhos do CSV e retorna o formato."""
    if "Endpoint" in headers:
        print("✅ Formato 'API' detectado.")
        return "API"
    elif "Funcionalidade" in headers:
        print("✅ Formato 'WEB' detectado.")
        return "WEB"
    elif "User Story" in headers:
        print("✅ Formato 'User Story' detectado.")
        return "DETALHADO"
    else:
        print(f"❌ ERRO: Formato de tabela não reconhecido. Cabeçalho encontrado: {headers}")
        return None

def construir_payload_jira(linha_csv, formato):
    """Cria o título, descrição e etiquetas para o Jira a partir de uma linha do CSV."""
    
    if formato == "API":
        titulo = linha_csv.get("Nome do Caso de Teste", "")
        descricao = f"""
*Endpoint:* {linha_csv.get("Endpoint", "N/A")}

*Passos:* {linha_csv.get("Passos", "N/A")}

*Resultado Esperado:* {linha_csv.get("Resultado Esperado", "N/A")}
"""
        labels = [
            f"risco-{linha_csv.get('Risco', '').lower()}",
            f"prioridade-{linha_csv.get('Prioridade', '').lower()}",
            f"tipo-{linha_csv.get('Tipo', '').lower()}",
            f"endpoint:{linha_csv.get('Endpoint', 'N/A').replace(' ', '').lower()}"
        ]
    elif formato == "WEB":
        titulo = linha_csv.get("Nome do Caso de Teste", "")
        descricao = f"""
*Funcionalidade:* {linha_csv.get("Funcionalidade", "N/A")}

*Passos:* {linha_csv.get("Passos", "N/A")}

*Resultado Esperado:* {linha_csv.get("Resultado Esperado", "N/A")}
"""
        labels = [
            f"risco-{linha_csv.get('Risco', '').lower()}",
            f"prioridade-{linha_csv.get('Prioridade', '').lower()}",
            f"tipo-{linha_csv.get('Tipo', '').lower()}",
            f"funcionalidade:{linha_csv.get('Funcionalidade', 'N/A').replace(' ', '').lower()}"
        ]
    elif formato == "DETALHADO":
        titulo = linha_csv.get("Caso de Teste", "")
        descricao = f"""
*User Story Relacionada:* {linha_csv.get("User Story", "N/A")}

*Pré-condições:* {linha_csv.get("Pré-condições", "N/A")}

*Passos:* {linha_csv.get("Passos", "N/A")}

*Resultado Esperado:* {linha_csv.get("Resultado Esperado", "N/A")}
"""
        labels = [f"story:{linha_csv.get('User Story', 'N/A').lower()}"]
    
    labels = [l for l in labels if not l.endswith('-')]

    return {
        "fields": {
            "project": {"key": JIRA_PROJECT_KEY},
            "summary": titulo,
            "description": {
                "type": "doc", "version": 1,
                "content": [{"type": "paragraph", "content": [{"type": "text", "text": descricao}]}]
            },
            # A CORREÇÃO MAIS IMPORTANTE ESTÁ AQUI
            "issuetype": {"name": "Caso de Teste"},
            "labels": labels
        }
    }

def criar_issue_no_jira(payload):
    """Envia a requisição para criar a issue no Jira."""
    api_url = f"{JIRA_URL}/rest/api/3/issue"
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    auth = (JIRA_USER_EMAIL, JIRA_API_TOKEN)
    
    try:
        response = requests.post(api_url, headers=headers, auth=auth, data=json.dumps(payload))
        response.raise_for_status()
        issue_key = response.json()['key']
        print(f"   🎉 SUCESSO! Criado com o ID: {issue_key}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"   ❌ ERRO ao criar issue.")
        if e.response:
            print(f"      Resposta: {e.response.text}")
        return False

def main():
    nome_arquivo = input("➡️ Qual o nome do seu arquivo CSV a ser importado? (ex: api_tests.csv): ")
    caminho_arquivo = script_dir / nome_arquivo
    
    try:
        with open(caminho_arquivo, mode='r', encoding='utf-8-sig') as f:
            leitor = csv.DictReader(f)
            linhas = list(leitor)
            formato = detectar_formato(leitor.fieldnames)
    except FileNotFoundError:
        print(f"❌ ERRO: Arquivo '{nome_arquivo}' não encontrado. Verifique se ele está na mesma pasta que o script.")
        return
    except Exception as e:
        print(f"❌ ERRO ao ler o arquivo CSV: {e}")
        return

    if not formato or not linhas:
        print("❌ ERRO: Não foi possível determinar o formato ou o arquivo está vazio.")
        return

    print(f"\n--- Processando {len(linhas)} Casos de Teste ---")
    
    for i, linha_csv in enumerate(linhas):
        titulo_preview = linha_csv.get("Nome do Caso de Teste") or linha_csv.get("Caso de Teste")
        print(f"\nProcessando linha #{i+2}: {titulo_preview}")
        
        payload = construir_payload_jira(linha_csv, formato)
        criar_issue_no_jira(payload)
        
    print("\n--- Importação Finalizada ---")

if __name__ == "__main__":
    main()