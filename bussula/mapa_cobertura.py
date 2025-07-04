# mapa_cobertura.py

import os
import requests
from dotenv import load_dotenv
from pathlib import Path
from collections import defaultdict

# --- Configuração Padrão ---
script_dir = Path(__file__).parent
env_path = script_dir.parent / '.env'
load_dotenv(dotenv_path=env_path)

JIRA_URL = os.getenv("JIRA_URL")
JIRA_USER_EMAIL = os.getenv("JIRA_USER_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")

# --- Lógica de Ordenação (quanto maior o número, mais importante) ---
TEST_STATUS_ORDER = {
    "reprovado": 5, 
    "bloqueado": 4, 
    "em andamento": 3, 
    "a fazer": 2, 
    "aprovado": 1
}

def buscar_casos_de_teste():
    """Busca todos os Casos de Teste do projeto."""
    print(f"🔎 Buscando todos os Casos de Teste no projeto '{JIRA_PROJECT_KEY}' para mapeamento...")
    jql_query = f'project = "{JIRA_PROJECT_KEY}" AND issuetype = "Caso de Teste" ORDER BY created DESC'
    api_url = f"{JIRA_URL}/rest/api/3/search"
    headers = {"Accept": "application/json"}
    auth = (JIRA_USER_EMAIL, JIRA_API_TOKEN)
    params = {'jql': jql_query, 'fields': 'summary,status,labels', 'maxResults': 1000}

    try:
        response = requests.get(api_url, headers=headers, auth=auth, params=params)
        response.raise_for_status()
        return response.json().get('issues', [])
    except requests.exceptions.RequestException as e:
        print(f"\n❌ ERRO ao buscar dados do Jira: {e}")
        return None

def gerar_mapa_de_cobertura():
    """
    Coleta e agrupa os casos de teste por endpoint, exibindo um relatório.
    """
    casos_de_teste = buscar_casos_de_teste()

    if casos_de_teste is None:
        return

    # Usamos defaultdict para facilitar o agrupamento
    endpoints = defaultdict(list)

    # Processa e agrupa os testes
    for teste in casos_de_teste:
        fields = teste['fields']
        labels = fields.get('labels', [])
        
        endpoint_label = next((l for l in labels if l.startswith('endpoint:')), None)
        
        # Se não encontrar a etiqueta de endpoint, agrupa em "Sem Endpoint Definido"
        endpoint_name = endpoint_label.replace('endpoint:', '') if endpoint_label else "Sem Endpoint Definido"

        risco_label = next((l.replace('risco-', '') for l in labels if l.startswith('risco-')), 'N/D')
        
        status_name = fields['status']['name']
        status_score = TEST_STATUS_ORDER.get(status_name.lower(), 0)

        endpoints[endpoint_name].append({
            "id": teste['key'],
            "titulo": fields['summary'],
            "status": status_name,
            "risco": risco_label.capitalize(),
            "score": status_score
        })

    print("\n\n" + "="*60)
    print("🗺️  MAPA DE COBERTURA DE TESTES POR ENDPOINT")
    print("="*60)

    if not endpoints:
        print("Nenhum caso de teste com etiqueta de endpoint encontrado.")
        return
        
    # Imprime o relatório agrupado e ordenado
    for endpoint, testes in sorted(endpoints.items()):
        print(f"\n➡️ Endpoint: {endpoint}")
        print("-"*50)
        
        # Ordena os testes dentro do grupo pelo score de status (mais importante primeiro)
        testes_ordenados = sorted(testes, key=lambda t: t['score'], reverse=True)
        
        for teste in testes_ordenados:
            print(f"  - [{teste['status']:<11}] [Risco: {teste['risco']:<7}] {teste['id']}: {teste['titulo']}")
            
    print("\n" + "="*60)

if __name__ == "__main__":
    gerar_mapa_de_cobertura()