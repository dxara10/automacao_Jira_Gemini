# reportar_bug.py (Versão 5 - Integração com Funcionalidade e Robot Framework)

import os
import requests
import json
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env para o ambiente
load_dotenv()

# --- Carregando credenciais de forma segura ---
JIRA_URL = os.getenv("JIRA_URL")
JIRA_USER_EMAIL = os.getenv("JIRA_USER_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")

# --- Verificação inicial ---
if not all([JIRA_URL, JIRA_USER_EMAIL, JIRA_API_TOKEN, JIRA_PROJECT_KEY]):
    print("ERRO: Verifique se JIRA_URL, JIRA_USER_EMAIL, JIRA_API_TOKEN e JIRA_PROJECT_KEY estão no .env")
    # A verificação da GEMINI_API_KEY foi removida daqui pois não é usada neste script.
    # Se for usar, adicione-a de volta.

def reportar_bug(resumo, passos, esperado, atual, gravidade, funcionalidade=None):
    """
    Cria um card de bug no Jira com base nos parâmetros fornecidos.
    Esta função é projetada para ser importada e usada por outros scripts (ex: Robot Framework).
    Retorna a chave do bug (ex: 'AC-124') em caso de sucesso, ou None em caso de falha.
    """
    # Formata a descrição
    passos_formatados = "\n".join([f"{i+1}. {passo.strip()}" for i, passo in enumerate(passos.split(';'))])
    descricao_texto = f"""
*Passos para Reproduzir:*
{passos_formatados}

*Resultado Esperado:*
{esperado}

*Resultado Atual:*
{atual}

*Ambiente:*
- Ferramenta: Automação com Robot Framework
"""

    # Monta a lista de etiquetas (labels)
    labels = [gravidade]
    if funcionalidade:
        # Formata a etiqueta de funcionalidade para ser compatível com o script de mapa
        label_func = f"funcionalidade:{funcionalidade.lower().replace(' ', '_')}"
        labels.append(label_func)
    
    print(f"\n🚀 Reportando bug para a funcionalidade '{funcionalidade}' com a etiqueta '{labels}'...")
    
    api_url = f"{JIRA_URL}/rest/api/3/issue"
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    auth = (JIRA_USER_EMAIL, JIRA_API_TOKEN)
    
    payload = {
        "fields": {
            "project": {"key": JIRA_PROJECT_KEY},
            "summary": resumo,
            "description": {
                "type": "doc",
                "version": 1,
                "content": [{"type": "paragraph", "content": [{"type": "text", "text": descricao_texto}]}]
            },
            "issuetype": {"name": "Bug"},
            "labels": labels
        }
    }
    
    try:
        response = requests.post(api_url, headers=headers, auth=auth, data=json.dumps(payload))
        response.raise_for_status()
        
        issue_data = response.json()
        issue_key = issue_data['key']
        issue_url = f"{JIRA_URL}/browse/{issue_key}"
        
        print("\n" + "="*50)
        print("🎉 SUCESSO! Bug criado.")
        print(f"   ID do Bug: {issue_key}")
        print(f"   URL: {issue_url}")
        print("="*50)
        return issue_key

    except requests.exceptions.RequestException as e:
        print(f"\n❌ ERRO: Falha ao criar o bug no Jira.")
        print(f"   Status Code: {e.response.status_code if e.response else 'N/A'}")
        print(f"   Resposta: {e.response.text if e.response else str(e)}")
        return None

def obter_detalhes_pela_entrevista():
    """
    Conduz uma entrevista com o usuário para coletar os detalhes do bug para reporte manual.
    """
    print("\n--- Entrevista para Reporte de Bug ---")
    resumo = input("➡️ Resumo do bug (título): ")
    funcionalidade = input("➡️ Funcionalidade/Endpoint afetado (ex: login, extrato): ")
    passos = input("➡️ Passos para Reproduzir (separe com ';'): ")
    esperado = input("➡️ Resultado Esperado: ")
    atual = input("➡️ Resultado Atual (o erro): ")
    
    print("\n➡️ Selecione o Nível de Gravidade:")
    niveis = {"1": "Crítico", "2": "Alto", "3": "Médio", "4": "Baixo"}
    for key, value in niveis.items():
        print(f"   [{key}] {value}")
    
    escolha_gravidade = input("   Escolha (1-4): ")
    mapa_gravidade = {
        "1": "gravidade-critico", "2": "gravidade-alto",
        "3": "gravidade-medio", "4": "gravidade-baixo"
    }
    label_gravidade = mapa_gravidade.get(escolha_gravidade, "gravidade-indefinida")

    # Validar se os campos essenciais foram preenchidos
    if not all([resumo, passos, esperado, atual, funcionalidade]):
        print("\nTodos os campos são obrigatórios. Abortando.")
        return None

    return {
        "resumo": resumo,
        "passos": passos,
        "esperado": esperado,
        "atual": atual,
        "gravidade": label_gravidade,
        "funcionalidade": funcionalidade
    }

def main_interativo():
    """
    Função principal para execução interativa via terminal.
    """
    detalhes = obter_detalhes_pela_entrevista()
    
    if detalhes:
        reportar_bug(
            resumo=detalhes['resumo'],
            passos=detalhes['passos'],
            esperado=detalhes['esperado'],
            atual=detalhes['atual'],
            gravidade=detalhes['gravidade'],
            funcionalidade=detalhes['funcionalidade']
        )

# Este bloco só é executado quando você roda o script diretamente (python reportar_bug.py)
if __name__ == "__main__":
    main_interativo()