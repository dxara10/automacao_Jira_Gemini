# atualizar_bug.py (Versão Final com Menu para Funcionalidade)

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

# --- Verificação inicial ---
if not all([JIRA_URL, JIRA_USER_EMAIL, JIRA_API_TOKEN]):
    print("❌ ERRO: Verifique se as variáveis JIRA_URL, JIRA_USER_EMAIL e JIRA_API_TOKEN estão no arquivo .env.")
    exit()

def get_issue_details(issue_key):
    """Busca os detalhes atuais de uma issue no Jira."""
    print(f"🔎 Buscando detalhes do bug '{issue_key}'...")
    api_url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}?fields=summary,status,labels,description"
    headers = {"Accept": "application/json"}
    auth = (JIRA_USER_EMAIL, JIRA_API_TOKEN)
    
    try:
        response = requests.get(api_url, headers=headers, auth=auth)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"\n❌ ERRO ao buscar o bug: {e}")
        if e.response and e.response.status_code == 404:
            print(f"   O bug com a chave '{issue_key}' não foi encontrado.")
        else:
            print(f"   Resposta: {e.response.text if e.response else 'Sem resposta do servidor.'}")
        return None

def update_issue_fields(issue_key, fields_to_update):
    """Atualiza os campos de uma issue com base no payload fornecido."""
    if not fields_to_update:
        print("🤷 Nenhum campo para atualizar.")
        return True

    print(f"\n🚀 Atualizando campos do bug '{issue_key}'...")
    api_url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}"
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    auth = (JIRA_USER_EMAIL, JIRA_API_TOKEN)
    payload = {"fields": fields_to_update}

    try:
        response = requests.put(api_url, headers=headers, auth=auth, data=json.dumps(payload))
        response.raise_for_status()
        print("✅ Campos atualizados com sucesso!")
        return True
    except requests.exceptions.RequestException as e:
        print(f"\n❌ ERRO ao atualizar campos: {e}")
        print(f"   Resposta: {e.response.text if e.response else str(e)}")
        return False

def add_comment(issue_key):
    """Adiciona um comentário a uma issue."""
    comentario = input("➡️ Digite o comentário: ")
    if not comentario:
        print("Comentário não pode ser vazio.")
        return

    api_url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}/comment"
    auth = (JIRA_USER_EMAIL, JIRA_API_TOKEN)
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    payload = {
        "body": {"type": "doc", "version": 1, "content": [{"type": "paragraph", "content": [{"type": "text", "text": comentario}]}]}
    }
    try:
        response = requests.post(api_url, headers=headers, auth=auth, data=json.dumps(payload))
        response.raise_for_status()
        print("✅ Comentário adicionado com sucesso!")
    except requests.exceptions.RequestException as e:
        print(f"\n❌ ERRO ao adicionar comentário: {e}")

def change_status(issue_key):
    """Busca e permite a mudança de status (transição) de uma issue."""
    api_url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}/transitions"
    auth = (JIRA_USER_EMAIL, JIRA_API_TOKEN)
    try:
        response = requests.get(api_url, headers={"Accept": "application/json"}, auth=auth)
        response.raise_for_status()
        transitions = response.json().get('transitions', [])
        
        if not transitions:
            print("🤷 Nenhuma transição de status disponível.")
            return

        print("\n➡️ Selecione o novo status para o bug:")
        for i, trans in enumerate(transitions):
            print(f"   [{i+1}] {trans['name']}")
        
        escolha = input("   Escolha uma opção: ")
        if not escolha.isdigit() or not 1 <= int(escolha) <= len(transitions):
            print("Opção inválida.")
            return
            
        transition_id = transitions[int(escolha)-1]['id']
        payload = {"transition": {"id": transition_id}}
        
        response_exec = requests.post(api_url, headers={"Content-Type": "application/json"}, auth=auth, data=json.dumps(payload))
        response_exec.raise_for_status()
        print(f"✅ Status do bug alterado com sucesso!")
    except requests.exceptions.RequestException as e:
        print(f"\n❌ ERRO ao mudar o status: {e}")

def main_menu(issue_key):
    """Exibe o menu principal de ações para um bug."""
    issue_details = get_issue_details(issue_key)
    if not issue_details:
        return

    fields = issue_details.get('fields', {})
    fields_to_update = {}
    # Cria uma cópia mutável das labels para manipulação segura
    current_labels = list(fields.get('labels', []))

    while True:
        # Exibe os detalhes atuais a cada loop do menu
        print("-" * 60)
        func_label = next((l for l in current_labels if l.startswith('funcionalidade:')), "N/A")
        grav_label = next((l for l in current_labels if l.startswith('gravidade-')), "N/A")
        print(f"Bug: {issue_key} - {fields_to_update.get('summary', fields.get('summary'))}")
        print(f"Status: {fields.get('status', {}).get('name')} | Gravidade: {grav_label} | Funcionalidade: {func_label}")
        print("-" * 60)

        print("\n--- PAINEL DE CONTROLE DO BUG ---")
        print("[1] Alterar Título (Resumo)")
        print("[2] Alterar Descrição Completa")
        print("[3] Alterar Gravidade")
        print("[4] Alterar Funcionalidade") # NOVA OPÇÃO
        print("[5] Adicionar Comentário")
        print("[6] Mudar Status (Mover Card)")
        print("\n[0] Salvar Alterações e Sair")

        choice = input("➡️ Escolha uma ação: ")

        if choice == '1':
            novo_titulo = input("➡️ Novo Título: ")
            fields_to_update['summary'] = novo_titulo
            print("   (alteração pendente)")
        
        elif choice == '2':
            print("--- Editando Descrição ---")
            passos = input("➡️ Novos Passos para Reproduzir (separe com ';'): ")
            esperado = input("➡️ Novo Resultado Esperado: ")
            atual = input("➡️ Novo Resultado Atual (o erro): ")
            nova_descricao = f"*Passos para Reproduzir:*\n{passos}\n\n*Resultado Esperado:*\n{esperado}\n\n*Resultado Atual:*\n{atual}"
            fields_to_update['description'] = {"type": "doc", "version": 1, "content": [{"type": "paragraph", "content": [{"type": "text", "text": nova_descricao}]}]}
            print("   (alteração pendente)")

        elif choice == '3':
            print("➡️ Nova Gravidade: [1] Crítico [2] Alto [3] Médio [4] Baixo")
            mapa = {"1": "gravidade-critico", "2": "gravidade-alto", "3": "gravidade-medio", "4": "gravidade-baixo"}
            escolha_grav = input("   Escolha: ")
            if escolha_grav in mapa:
                # Remove a gravidade antiga e adiciona a nova, preservando outras labels
                current_labels = [lbl for lbl in current_labels if not lbl.startswith('gravidade-')]
                current_labels.append(mapa[escolha_grav])
                fields_to_update['labels'] = current_labels
                print("   (alteração de gravidade pendente)")
            else:
                print("Opção inválida.")
        
        elif choice == '4': # NOVA LÓGICA
            nova_func = input("➡️ Nova Funcionalidade/Endpoint (ex: login, extrato): ")
            if nova_func:
                # Remove a funcionalidade antiga e adiciona a nova, preservando outras labels
                current_labels = [lbl for lbl in current_labels if not lbl.startswith('funcionalidade:')]
                label_func = f"funcionalidade:{nova_func.lower().replace(' ', '_')}"
                current_labels.append(label_func)
                fields_to_update['labels'] = current_labels
                print("   (alteração de funcionalidade pendente)")
            else:
                print("Funcionalidade não pode ser vazia.")

        elif choice == '5':
            add_comment(issue_key)

        elif choice == '6':
            change_status(issue_key)
            # Recarrega os detalhes para mostrar o novo status
            issue_details = get_issue_details(issue_key)
            fields = issue_details.get('fields', {})
            current_labels = list(fields.get('labels', [])) # Atualiza as labels também

        elif choice == '0':
            update_issue_fields(issue_key, fields_to_update)
            print("\n👋 Saindo do painel de controle.")
            break
        
        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    issue_id = input("➡️ Qual o ID do bug a ser atualizado? (ex: AC-123): ")
    if issue_id:
        main_menu(issue_id)
    else:
        print("ID do bug não pode ser vazio.")