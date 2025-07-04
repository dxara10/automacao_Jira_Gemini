# atualizar_teste.py (v4 - Com Edição de Endpoint/Funcionalidade)

import os
import requests
import json
import subprocess
import tempfile
from dotenv import load_dotenv
from pathlib import Path

# --- Configuração ---
script_dir = Path(__file__).parent
env_path = script_dir.parent / '.env'
load_dotenv(dotenv_path=env_path)

JIRA_URL = os.getenv("JIRA_URL")
JIRA_USER_EMAIL = os.getenv("JIRA_USER_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

def buscar_dados_teste(issue_key):
    """Busca os dados atuais de uma issue, incluindo transições e labels."""
    print(f"\n🔎 Buscando dados para o teste {issue_key}...")
    # Expandimos para buscar transições e pedimos os campos de labels e descrição
    api_url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}?expand=transitions&fields=summary,status,description,labels"
    auth = (JIRA_USER_EMAIL, JIRA_API_TOKEN)
    try:
        response = requests.get(api_url, auth=auth)
        response.raise_for_status()
        print("✅ Dados encontrados.")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ ERRO ao buscar o teste: {e.response.text if e.response else str(e)}")
        return None

def adicionar_comentario(issue_key, comentario):
    """Adiciona um comentário a uma issue."""
    print(f"   ...adicionando comentário ao teste '{issue_key}'...")
    api_url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}/comment"
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    auth = (JIRA_USER_EMAIL, JIRA_API_TOKEN)
    payload = {"body": {"type": "doc", "version": 1, "content": [{"type": "paragraph", "content": [{"type": "text", "text": comentario}]}]}}
    try:
        r = requests.post(api_url, headers=headers, auth=auth, json=payload)
        r.raise_for_status()
        print("   ✅ Comentário adicionado com sucesso.")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Falha ao adicionar comentário: {e.response.text if e.response else str(e)}")

def mudar_status_do_teste(issue_key, transicoes_disponiveis):
    """Mostra as transições e permite ao usuário mudar o status."""
    print("\n--- Mudar Status ---")
    if not transicoes_disponiveis:
        print("⚠️ Não há transições de status disponíveis para este teste no momento.")
        return
        
    print("Status disponíveis para este teste:")
    for i, transicao in enumerate(transicoes_disponiveis):
        print(f"  [{i+1}] {transicao['name']}")
    
    try:
        escolha = int(input("  ➡️ Para qual status você quer mover o teste? (digite o número): ")) - 1
        if not 0 <= escolha < len(transicoes_disponiveis):
            print("❌ Opção inválida."); return
    except ValueError:
        print("❌ Entrada inválida. Por favor, insira um número."); return

    transicao_escolhida = transicoes_disponiveis[escolha]
    id_transicao, nome_transicao = transicao_escolhida['id'], transicao_escolhida['name']
    
    comentario = ""
    if any(palavra in nome_transicao.lower() for palavra in ["reprovado", "falhou", "bloqueado", "failed", "blocked"]):
        comentario = input(f"  ➡️ Por favor, adicione um comentário explicando o motivo para '{nome_transicao}': ")

    print(f"\n🚀 Movendo teste {issue_key} para '{nome_transicao}'...")
    api_url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}/transitions"
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    auth = (JIRA_USER_EMAIL, JIRA_API_TOKEN)
    payload = {"transition": {"id": id_transicao}}

    try:
        r = requests.post(api_url, headers=headers, auth=auth, json=payload)
        r.raise_for_status()
        print(f"✅ Status do teste {issue_key} atualizado para '{nome_transicao}'.")
        if comentario: adicionar_comentario(issue_key, comentario)
    except requests.exceptions.RequestException as e:
        print(f"❌ ERRO ao mudar o status: {e.response.text if e.response else str(e)}")

def editar_descricao(descricao_atual_adf):
    """Abre um editor de texto para o usuário editar a descrição."""
    texto_simples = ""
    if descricao_atual_adf and descricao_atual_adf.get('content'):
        for block in descricao_atual_adf['content']:
            if block.get('type') == 'paragraph':
                for content in block.get('content', []):
                    if content.get('type') == 'text':
                        texto_simples += content.get('text', '')
                texto_simples += "\n\n" # Adiciona parágrafos entre os blocos
    
    with tempfile.NamedTemporaryFile(mode='w+', suffix=".txt", delete=False, encoding='utf-8') as tf:
        tf.write(texto_simples.strip())
        temp_file_path = tf.name
    
    editor = os.environ.get('EDITOR', 'nano')
    print(f"\n📝 Abrindo o editor '{editor}'... Salve e feche para continuar.")
    subprocess.run([editor, temp_file_path])

    with open(temp_file_path, 'r', encoding='utf-8') as f:
        texto_modificado = f.read()
    os.remove(temp_file_path)

    novo_adf = {"type": "doc", "version": 1, "content": [{"type": "paragraph", "content": [{"type": "text", "text": texto_modificado.strip()}]}]}
    return novo_adf

def main():
    issue_id = input("➡️ Qual o ID do Caso de Teste a ser atualizado? (ex: AC-6): ").strip()
    if not issue_id:
        print("ID não pode ser vazio."); return

    dados_iniciais = buscar_dados_teste(issue_id)
    if not dados_iniciais: return
        
    update_payload = {"fields": {}}
    # LÓGICA DE ATUALIZAÇÃO DE LABELS: Carrega as labels atuais para não as sobrescrever
    labels_para_atualizar = list(dados_iniciais.get('fields', {}).get('labels', []))
    
    while True:
        # Exibe o cabeçalho com informações atualizadas
        status_atual = dados_iniciais['fields']['status']['name']
        endpoint_atual = next((l.replace('endpoint:', '') for l in labels_para_atualizar if l.startswith('endpoint:')), "Nenhum")
        
        print("\n" + "="*50)
        print(f"Editando: {dados_iniciais['fields']['summary']} ({issue_id})")
        print(f"Status Atual: {status_atual} | Endpoint Atual: {endpoint_atual}")
        print("="*50)

        print("Opções:")
        print("[1] Mudar o Status (Ação imediata)")
        print("[2] Adicionar um Comentário Avulso (Ação imediata)")
        print("[3] Editar Descrição (Passos, etc.)")
        print("[4] Alterar Endpoint/Funcionalidade") # <<< NOVA OPÇÃO
        print("\n[S] Salvar Alterações e Sair")
        print("[C] Cancelar e Sair sem Salvar")
        
        escolha = input("➡️ O que você deseja fazer?: ").lower()

        if escolha == '1':
            transicoes = buscar_dados_teste(issue_id).get('transitions', [])
            mudar_status_do_teste(issue_id, transicoes)
            # Recarrega os dados após mudar o status
            dados_iniciais = buscar_dados_teste(issue_id)
        
        elif escolha == '2':
            comentario_texto = input("   Digite o comentário: ")
            if comentario_texto: adicionar_comentario(issue_id, comentario_texto)
        
        elif escolha == '3':
            descricao_adf_atual = dados_iniciais['fields'].get('description')
            nova_descricao_adf = editar_descricao(descricao_adf_atual)
            update_payload['fields']['description'] = nova_descricao_adf
            print("   ✅ Descrição preparada para atualização.")
            
        elif escolha == '4': # <<< LÓGICA DA NOVA OPÇÃO
            novo_endpoint = input("   ➡️ Qual o novo Endpoint/Funcionalidade? ").strip()
            if novo_endpoint:
                # Remove a etiqueta de endpoint antiga para evitar duplicatas
                labels_para_atualizar = [lbl for lbl in labels_para_atualizar if not lbl.startswith('endpoint:')]
                # Adiciona a nova
                nova_label = f"endpoint:{novo_endpoint.lower().replace(' ', '_')}"
                labels_para_atualizar.append(nova_label)
                # Adiciona a lista completa de labels ao payload que será salvo
                update_payload['fields']['labels'] = labels_para_atualizar
                print(f"   ✅ Endpoint '{novo_endpoint}' preparado para atualização.")
            else:
                print("   ❌ O nome do endpoint não pode ser vazio.")
            
        elif escolha == 's':
            if not update_payload['fields']:
                print("Nenhuma alteração pendente para salvar. Saindo."); break
            
            api_url = f"{JIRA_URL}/rest/api/3/issue/{issue_id}"
            print(f"\n💾 Salvando alterações no teste {issue_id}...")
            try:
                r = requests.put(api_url, headers={"Accept": "application/json", "Content-Type": "application/json"}, auth=(JIRA_USER_EMAIL, JIRA_API_TOKEN), json=update_payload)
                r.raise_for_status()
                print(f"🎉 SUCESSO! O Caso de Teste foi atualizado.")
            except requests.exceptions.RequestException as e:
                print(f"❌ ERRO ao salvar as alterações: {e.response.text if e.response else str(e)}")
            break
            
        elif escolha == 'c':
            print("Alterações descartadas. Saindo."); break
        else:
            print("Opção inválida.")

if __name__ == "__main__":
    main()