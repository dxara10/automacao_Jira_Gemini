# panorama.py (v2 - Com Priorização)

import os
import requests
from dotenv import load_dotenv
from pathlib import Path
from collections import Counter

# --- Configuração Padrão ---
script_dir = Path(__file__).parent
env_path = script_dir.parent / '.env'
load_dotenv(dotenv_path=env_path)

JIRA_URL = os.getenv("JIRA_URL")
JIRA_USER_EMAIL = os.getenv("JIRA_USER_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")

# --- Lógica de Priorização (podemos ajustar aqui) ---
# Damos um "peso" para cada etiqueta, quanto maior, mais importante
RISK_ORDER = {"risco-critico": 4, "risco-alto": 3, "risco-medio": 2, "risco-baixo": 1}
PRIORITY_ORDER = {"prioridade-alta": 3, "prioridade-media": 2, "prioridade-baixa": 1}
# Status dos casos de teste que não significam "pronto"
TEST_STATUS_ORDER = {"reprovado": 4, "bloqueado": 3, "em andamento": 2, "a fazer": 1}
STATUS_CONCLUIDO = ["concluído", "feito", "done", "aprovado"]


def buscar_issues_por_tipo(issue_type):
    """Função genérica para buscar todas as issues de um determinado tipo no projeto."""
    print(f"🔎 Buscando dados para '{issue_type}'...")
    jql_query = f'project = "{JIRA_PROJECT_KEY}" AND issuetype = "{issue_type}"'
    api_url = f"{JIRA_URL}/rest/api/3/search"
    headers = {"Accept": "application/json"}
    auth = (JIRA_USER_EMAIL, JIRA_API_TOKEN)
    params = {'jql': jql_query, 'fields': '*all', 'maxResults': 1000}

    try:
        response = requests.get(api_url, headers=headers, auth=auth, params=params)
        response.raise_for_status()
        return response.json().get('issues', [])
    except requests.exceptions.RequestException as e:
        print(f"\n❌ ERRO ao buscar dados do Jira para '{issue_type}': {e}")
        return None

def gerar_panorama():
    """Coleta todos os dados e imprime o relatório do panorama do projeto."""
    bugs = buscar_issues_por_tipo("Bug")
    casos_de_teste = buscar_issues_por_tipo("Caso de Teste")

    print("\n\n" + "="*60)
    print(f"📊 PANORAMA DO PROJETO: App Cinema ({JIRA_PROJECT_KEY})")
    print(f"   Data: {os.popen('date').read().strip()}")
    print("="*60)

    # --- Seção de Destaques de Bugs ---
    if bugs:
        # Filtra apenas bugs que não estão concluídos
        bugs_abertos = [b for b in bugs if b['fields']['status']['name'].lower() not in STATUS_CONCLUIDO]
        
        # Calcula o "score" de criticidade de cada bug
        def get_bug_score(bug):
            labels = bug['fields']['labels']
            risk_score = max([RISK_ORDER.get(l, 0) for l in labels] or [0])
            priority_score = max([PRIORITY_ORDER.get(l, 0) for l in labels] or [0])
            # Damos um peso maior para o Risco
            return (risk_score * 10) + priority_score

        bugs_abertos.sort(key=get_bug_score, reverse=True)

        print("\n🔥 BUGS CRÍTICOS ABERTOS (TOP 5)")
        print("-"*35)
        if not bugs_abertos:
            print("   Nenhum bug aberto. Bom trabalho!")
        else:
            for bug in bugs_abertos[:5]:
                labels = bug['fields']['labels']
                risk = next((l.replace('risco-', '') for l in labels if l in RISK_ORDER), 'N/D')
                priority = next((l.replace('prioridade-', '') for l in labels if l in PRIORITY_ORDER), 'N/D')
                print(f"- [{bug['key']}] {bug['fields']['summary']}")
                print(f"  (Risco: {risk.capitalize()} | Prioridade: {priority.capitalize()})")

    # --- Seção de Destaques de Testes ---
    if casos_de_teste:
        testes_pendentes = [t for t in casos_de_teste if t['fields']['status']['name'].lower() not in STATUS_CONCLUIDO]

        def get_test_score(test):
            status = test['fields']['status']['name'].lower()
            return TEST_STATUS_ORDER.get(status, 0)
        
        testes_pendentes.sort(key=get_test_score, reverse=True)

        print("\n⚠️ CASOS DE TESTE QUE REQUEREM ATENÇÃO")
        print("-"*35)
        if not testes_pendentes:
            print("   Todos os testes foram aprovados!")
        else:
            for teste in testes_pendentes[:5]:
                print(f"- [{teste['key']}] {teste['fields']['summary']} (Status: {teste['fields']['status']['name']})")


    print("\n\n--- Resumo Geral ---")
    
    # --- Seção de Resumo de Bugs ---
    if bugs is not None:
        print("\n🐞 ANÁLISE GERAL DE BUGS")
        print("-"*30)
        print(f"- Total de Bugs: {len(bugs)}")
        status_counts = Counter(bug['fields']['status']['name'] for bug in bugs)
        print("- Bugs por Status:")
        for status, count in status_counts.items():
            print(f"  - {status}: {count}")

    # --- Seção de Resumo de Casos de Teste ---
    if casos_de_teste is not None:
        print("\n✅ ANÁLISE GERAL DE CASOS DE TESTE")
        print("-"*30)
        print(f"- Total de Casos de Teste: {len(casos_de_teste)}")
        status_counts_testes = Counter(teste['fields']['status']['name'] for teste in casos_de_teste)
        print("- Testes por Status:")
        for status, count in status_counts_testes.items():
            print(f"  - {status}: {count}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    gerar_panorama()