# mapa_bugs.py

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

# --- Lógica de Priorização (quanto maior o número, mais crítico) ---
RISK_ORDER = {"risco-critico": 4, "risco-alto": 3, "risco-medio": 2, "risco-baixo": 1}
PRIORITY_ORDER = {"prioridade-alta": 3, "prioridade-media": 2, "prioridade-baixa": 1}
STATUS_CONCLUIDO = ["concluído", "feito", "done", "resolvido"]

def buscar_bugs_do_projeto():
    """Busca todos os Bugs do projeto."""
    print(f"🔎 Buscando todos os Bugs no projeto '{JIRA_PROJECT_KEY}' para mapeamento...")
    jql_query = f'project = "{JIRA_PROJECT_KEY}" AND issuetype = Bug ORDER BY created DESC'
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

def gerar_mapa_de_bugs():
    """
    Coleta e agrupa os bugs por endpoint ou funcionalidade, exibindo um relatório de concentração.
    """
    bugs = buscar_bugs_do_projeto()

    if bugs is None:
        return

    agrupador = defaultdict(list)

    # Processa e agrupa os bugs
    for bug in bugs:
        fields = bug['fields']
        labels = fields.get('labels', [])
        
        # Procura por uma etiqueta de endpoint ou funcionalidade para agrupar
        endpoint_label = next((l for l in labels if l.startswith('endpoint:')), None)
        func_label = next((l for l in labels if l.startswith('funcionalidade:')), None)
        
        chave_grupo = "Outros Bugs (Sem Contexto)"
        if endpoint_label:
            chave_grupo = endpoint_label.replace('endpoint:', '')
        elif func_label:
            chave_grupo = func_label.replace('funcionalidade:', '')

        # Calcula o score de criticidade para ordenação
        risk_score = max([RISK_ORDER.get(l, 0) for l in labels] or [0])
        priority_score = max([PRIORITY_ORDER.get(l, 0) for l in labels] or [0])
        score = (risk_score * 10) + priority_score

        agrupador[chave_grupo].append({
            "id": bug['key'],
            "titulo": fields['summary'],
            "status": fields['status']['name'],
            "score": score
        })

    print("\n\n" + "="*60)
    print("🐞 MAPA DE CONCENTRAÇÃO DE BUGS POR FUNCIONALIDADE/ENDPOINT")
    print("="*60)

    if not agrupador:
        print("Nenhum bug encontrado.")
        return
        
    # Imprime o relatório, ordenando os grupos por quantidade de bugs
    for chave, bugs_do_grupo in sorted(agrupador.items(), key=lambda item: len(item[1]), reverse=True):
        total_bugs = len(bugs_do_grupo)
        bugs_abertos = len([b for b in bugs_do_grupo if b['status'].lower() not in STATUS_CONCLUIDO])
        
        print(f"\n➡️ Foco: {chave.upper()} (Total: {total_bugs} | Abertos: {bugs_abertos})")
        print("-"*55)
        
        # Ordena os bugs dentro do grupo pelo score de criticidade
        bugs_ordenados = sorted(bugs_do_grupo, key=lambda b: b['score'], reverse=True)
        
        for bug in bugs_ordenados:
            # Marca bugs resolvidos para clareza visual
            status_visual = f"✅ {bug['status']}" if bug['status'].lower() in STATUS_CONCLUIDO else f"🔥 {bug['status']}"
            print(f"  - [{status_visual:<15}] {bug['id']}: {bug['titulo']}")
            
    print("\n" + "="*60)

if __name__ == "__main__":
    gerar_mapa_de_bugs()