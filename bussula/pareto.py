# pareto.py (v5 - Análise de Volume de Teste Corrigida)

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

def buscar_issues(jql, mensagem):
    """Função genérica para buscar issues no Jira."""
    print(f"🔎 {mensagem}")
    api_url = f"{JIRA_URL}/rest/api/3/search"
    headers = {"Accept": "application/json"}
    auth = (JIRA_USER_EMAIL, JIRA_API_TOKEN)
    params = {'jql': jql, 'fields': 'labels', 'maxResults': 1000}

    try:
        response = requests.get(api_url, headers=headers, auth=auth, params=params)
        response.raise_for_status()
        return response.json().get('issues', [])
    except requests.exceptions.RequestException as e:
        print(f"\n❌ ERRO ao buscar dados do Jira: {e}")
        if e.response: print(f"   Resposta do servidor: {e.response.text}")
        return None

def realizar_analise_pareto(issues, titulo_analise, titulo_foco, titulo_outros):
    """Função genérica que realiza e imprime a análise de Pareto."""
    if not issues:
        print("\nNenhum item foi encontrado para analisar.")
        return

    total_itens = len(issues)
    agrupador = defaultdict(int)

    for item in issues:
        labels = item['fields'].get('labels', [])
        chave_grupo = "Outros (Sem Contexto)"
        label_encontrada = next((l for l in labels if l.startswith('funcionalidade:') or l.startswith('endpoint:')), None)
        if label_encontrada:
            chave_grupo = label_encontrada.replace('funcionalidade:', '').replace('endpoint:', '')
        agrupador[chave_grupo] += 1

    print("\n\n" + "="*60)
    print(f"📊 {titulo_analise}")
    print("="*60)
    print(f"Base de análise: {total_itens} itens encontrados no total.\n")
    grupos_ordenados = sorted(agrupador.items(), key=lambda item: item[1], reverse=True)
    percentual_acumulado = 0
    focos_identificados = False

    print(f"🔥 {titulo_foco}")
    print("-"*60)
    for chave, contagem in grupos_ordenados:
        percentual_individual = (contagem / total_itens) * 100
        if percentual_acumulado < 80 and not focos_identificados:
            percentual_acumulado += percentual_individual
        else:
            if not focos_identificados:
                print("-"*60)
                print(f"🎯 As áreas acima representam {percentual_acumulado:.1f}% de todos os itens.")
                print(f"\nⓘ {titulo_outros}")
                print("-"*60)
                focos_identificados = True
        print(f"- {chave.upper():<35} | Contagem: {contagem:<3} ({percentual_individual:.1f}%)")
    if not focos_identificados and percentual_acumulado > 0:
        print("-"*60)
        print(f"🎯 As áreas acima representam {percentual_acumulado:.1f}% de todos os itens.")
    print("\n" + "="*60)

def analisar_bugs():
    """Prepara e executa a análise de Pareto para o VOLUME de Bugs."""
    jql = f'project = "{JIRA_PROJECT_KEY}" AND issuetype = Bug'
    mensagem = f"Analisando todos os Bugs no projeto '{JIRA_PROJECT_KEY}'..."
    bugs = buscar_issues(jql, mensagem)
    realizar_analise_pareto(
        bugs,
        "ANÁLISE DE PARETO POR VOLUME DE BUGS",
        "FOCOS DE PROBLEMAS (Funcionalidades com mais bugs reportados)",
        "Outras áreas com bugs"
    )

def analisar_cobertura_de_testes():
    """
    Prepara e executa a análise de Pareto para o VOLUME de Casos de Teste.
    """
    # JQL SIMPLES: Busca todos os casos de teste, exatamente como o mapa_cobertura.py
    jql = f'project = "{JIRA_PROJECT_KEY}" AND issuetype = "Caso de Teste"'
    mensagem = f"Analisando todos os Casos de Teste do projeto '{JIRA_PROJECT_KEY}'..."
    todos_os_testes = buscar_issues(jql, mensagem)

    # Executa a análise de Pareto com a lista COMPLETA de testes, sem filtrar por status.
    realizar_analise_pareto(
        todos_os_testes,
        "ANÁLISE DE PARETO POR VOLUME DE CASOS DE TESTE",
        "FOCOS DE COBERTURA (Funcionalidades com mais Casos de Teste)",
        "Outras áreas com cobertura de testes"
    )

def menu_principal():
    """Exibe o menu principal para o usuário escolher a análise."""
    while True:
        print("\n--- Análise de Pareto (Princípio 80/20) ---")
        print("Qual análise você deseja realizar?")
        print("[1] Análise por VOLUME DE BUGS (Onde há mais bugs reportados?)")
        print("[2] Análise por VOLUME DE TESTES (Onde há mais Casos de Teste escritos?)")
        print("\n[0] Sair")

        escolha = input("➡️ Escolha uma opção: ")

        if escolha == '1':
            analisar_bugs()
        elif escolha == '2':
            analisar_cobertura_de_testes()
        elif escolha == '0':
            print("👋 Saindo.")
            break
        else:
            print("❌ Opção inválida. Tente novamente.")

if __name__ == "__main__":
    menu_principal()