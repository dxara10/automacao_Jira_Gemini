# adicionar_teste.py (Versão Aprimorada com Endpoint e para Automação)

import os
import requests
import json
from dotenv import load_dotenv
from pathlib import Path

# --- Configuração ---
script_dir = Path(__file__).parent
env_path = script_dir.parent / '.env'
load_dotenv(dotenv_path=env_path)

JIRA_URL = os.getenv("JIRA_URL")
JIRA_USER_EMAIL = os.getenv("JIRA_USER_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")

# Nome do tipo de vínculo que conecta um Caso de Teste a uma Estória.
# Ex: "Test", "Relates", "Tests". Verifique na sua configuração do Jira.
JIRA_LINK_TYPE = "Test"

def buscar_chave_por_titulo(titulo):
    """Busca a chave de uma issue (ex: AC-2) pelo seu título (ex: US-AUTH-001)."""
    jql = f'project = "{JIRA_PROJECT_KEY}" AND summary ~ \'"{titulo}"\''
    url = f"{JIRA_URL}/rest/api/3/search"
    auth = (JIRA_USER_EMAIL, JIRA_API_TOKEN)
    headers = {"Accept": "application/json"}
    params = {'jql': jql, 'fields': 'key', 'maxResults': 1}
    try:
        r = requests.get(url, headers=headers, params=params, auth=auth)
        r.raise_for_status()
        issues = r.json().get('issues', [])
        return issues[0]['key'] if issues else None
    except requests.exceptions.RequestException as e:
        print(f"ERRO ao buscar issue '{titulo}': {e}")
        return None

def criar_caso_de_teste(titulo, passos, resultado_esperado, pre_condicoes=None, endpoint=None, id_estoria=None):
    """
    Cria um 'Caso de Teste' no Jira e o vincula a uma Estória se especificado.
    Função projetada para ser importada e usada por automações.
    """
    print(f"\n🚀 Criando o Caso de Teste '{titulo}' no Jira...")
    
    # Formata a descrição usando o markup do Jira
    passos_formatados = "\n".join([f"# {p.strip()}" for p in passos])
    descricao_texto = (
        f"*Pré-condições:*\n{pre_condicoes if pre_condicoes else 'Nenhuma'}\n\n"
        f"*Passos de Teste:*\n{passos_formatados}\n\n"
        f"*Resultado Esperado:*\n{resultado_esperado}"
    )
    
    # Prepara o payload para a criação da issue
    fields = {
        "project": {"key": JIRA_PROJECT_KEY},
        "summary": titulo,
        "description": {
            "type": "doc",
            "version": 1,
            "content": [{"type": "paragraph", "content": [{"type": "text", "text": descricao_texto}]}]
        },
        "issuetype": {"name": "Caso de Teste"}
    }
    
    # Adiciona a etiqueta de endpoint se ela for fornecida
    if endpoint:
        endpoint_label = f"endpoint:{endpoint.lower().replace(' ', '_')}"
        fields['labels'] = [endpoint_label]
        print(f"   Adicionando etiqueta de endpoint: {endpoint_label}")

    payload = {"fields": fields}
    
    # Envia a requisição para criar o Caso de Teste
    api_url = f"{JIRA_URL}/rest/api/3/issue"
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    auth = (JIRA_USER_EMAIL, JIRA_API_TOKEN)
    
    try:
        response = requests.post(api_url, headers=headers, auth=auth, json=payload)
        response.raise_for_status()
        issue_data = response.json()
        issue_key = issue_data['key']
        issue_url = f"{JIRA_URL}/browse/{issue_key}"
        
        print("\n" + "="*50)
        print("🎉 SUCESSO! O Caso de Teste foi criado.")
        print(f"   ID: {issue_key}")
        print(f"   Link: {issue_url}")
        
        # Se um ID de estória foi fornecido, tenta fazer o vínculo
        if id_estoria:
            print(f"   Buscando a chave da Estória '{id_estoria}' para vincular...")
            chave_estoria_real = buscar_chave_por_titulo(id_estoria)
            
            if not chave_estoria_real:
                print(f"   ⚠️ Falha ao vincular: Estória com título '{id_estoria}' não encontrada.")
            else:
                print(f"   Vinculando {issue_key} ao requisito {chave_estoria_real}...")
                link_payload = {
                    "outwardIssue": {"key": issue_key},
                    "inwardIssue": {"key": chave_estoria_real},
                    "type": {"name": JIRA_LINK_TYPE}
                }
                link_api_url = f"{JIRA_URL}/rest/api/3/issueLink"
                link_response = requests.post(link_api_url, headers=headers, auth=auth, json=link_payload)
                if link_response.status_code == 201:
                    print(f"   ✅ Vinculado com sucesso!")
                else:
                    print(f"   ⚠️ Falha ao vincular: {link_response.text}")
        print("="*50)
        return issue_key

    except requests.exceptions.RequestException as e:
        print(f"\n❌ ERRO ao criar o Caso de Teste: {e.response.text if e.response else str(e)}")
        return None

def main_interativo():
    """Coleta os detalhes do teste via terminal e chama a função de criação."""
    print("\n--- Novo Caso de Teste ---")
    titulo = input("➡️ Título do Caso de Teste (ex: CT-API-030): ")
    endpoint = input("➡️ Endpoint/Funcionalidade coberto? (ex: login_api, opcional): ")
    id_estoria = input("➡️ ID da Estória de Usuário a vincular? (ex: US-AUTH-001, opcional): ")
    pre_condicoes = input("➡️ Pré-condições (opcional): ")
    
    passos_lista = []
    i = 1
    while True:
        passo = input(f"   ➡️ Ação do Passo #{i} (deixe em branco para finalizar): ")
        if not passo:
            break
        passos_lista.append(passo)
        i += 1
        
    resultado_esperado = input("➡️ Resultado Esperado Final: ")

    if not all([titulo, passos_lista, resultado_esperado]):
        print("\nTítulo, pelo menos um passo e resultado esperado são obrigatórios. Abortando.")
        return

    criar_caso_de_teste(
        titulo=titulo,
        passos=passos_lista,
        resultado_esperado=resultado_esperado,
        pre_condicoes=pre_condicoes,
        endpoint=endpoint,
        id_estoria=id_estoria
    )

# Este bloco só é executado quando você roda o script diretamente.
if __name__ == "__main__":
    main_interativo()