# exportar_testes_excel.py (v2.1 - Com filtro de etiquetas 'endpoint')

import os
import pandas as pd
import requests
from dotenv import load_dotenv
from pathlib import Path

# --- Configuração Padrão ---
script_dir = Path(__file__).parent
env_path = script_dir.parent / '.env'
load_dotenv(dotenv_path=env_path)

JIRA_URL = os.getenv("JIRA_URL")
JIRA_USER_EMAIL = os.getenv("JIRA_USER_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")

def parse_adf_description(description_adf):
    """Converte a descrição em formato ADF do Jira para texto simples."""
    if not description_adf or not description_adf.get('content'):
        return ""
    
    text_parts = []
    for content_block in description_adf['content']:
        if content_block.get('type') == 'paragraph':
            for text_content in content_block.get('content', []):
                if text_content.get('type') == 'text':
                    text_parts.append(text_content.get('text', ''))
            text_parts.append('\n')
            
    return "".join(text_parts).strip()

def extract_criticidade(labels):
    """Extrai a criticidade (risco ou prioridade) da lista de etiquetas."""
    for label in labels:
        if label.lower().startswith(('risco-', 'prioridade-')):
            return label
    return "N/A"

def gerar_relatorio_excel():
    """Busca os casos de teste do Jira e gera um relatório em Excel formatado como Tabela."""
    print(f"🔎 Buscando todos os Casos de Teste do projeto '{JIRA_PROJECT_KEY}'...")
    
    jql = f'project = "{JIRA_PROJECT_KEY}" AND issuetype = "Caso de Teste"'
    fields = "summary,description,labels,status"
    
    api_url = f"{JIRA_URL}/rest/api/3/search"
    auth = (JIRA_USER_EMAIL, JIRA_API_TOKEN)
    headers = {"Accept": "application/json"}
    params = {'jql': jql, 'fields': fields, 'maxResults': 1000}

    try:
        response = requests.get(api_url, headers=headers, params=params, auth=auth)
        response.raise_for_status()
        issues = response.json().get('issues', [])
        print(f"✅ {len(issues)} Casos de Teste encontrados.")
    except requests.exceptions.RequestException as e:
        print(f"❌ ERRO ao buscar dados do Jira: {e}")
        if e.response: print(f"   Resposta: {e.response.text}")
        return

    print("🔄 Processando os dados para o relatório...")
    dados_para_relatorio = []
    for issue in issues:
        fields = issue.get('fields', {})
        todas_as_etiquetas = fields.get('labels', [])
        
        # --- LÓGICA DE FILTRO DAS ETIQUETAS ---
        # Cria uma nova lista contendo apenas as etiquetas que começam com 'endpoint:'
        etiquetas_de_endpoint = [
            label for label in todas_as_etiquetas if label.lower().startswith('endpoint:')
        ]
        
        dados_para_relatorio.append({
            "ID": issue.get('key'),
            "Nome": fields.get('summary'),
            "Descrição": parse_adf_description(fields.get('description')),
            # Usa a lista filtrada para esta coluna
            "Etiquetas": ", ".join(etiquetas_de_endpoint),
            # Usa a lista completa para encontrar a criticidade
            "Criticidade": extract_criticidade(todas_as_etiquetas),
            "Status": fields.get('status', {}).get('name', 'N/A')
        })

    df = pd.DataFrame(dados_para_relatorio)
    df["User Story"] = ""
    ordem_colunas = ["ID", "Nome", "Status", "Criticidade", "User Story", "Descrição", "Etiquetas"]
    df = df[ordem_colunas]

    nome_arquivo = "relatorio_casos_de_teste.xlsx"
    print(f"🚀 Gerando arquivo Excel formatado como Tabela: {nome_arquivo}...")
    try:
        writer = pd.ExcelWriter(nome_arquivo, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Casos de Teste', index=False)
        
        workbook  = writer.book
        worksheet = writer.sheets['Casos de Teste']
        
        (num_rows, num_cols) = df.shape
        tabela_range = f'A1:{chr(ord("A") + num_cols - 1)}{num_rows + 1}'
        
        worksheet.add_table(tabela_range, {'columns': [{'header': col} for col in df.columns]})
        
        # Ajusta a largura das colunas
        worksheet.set_column('A:A', 10) # ID
        worksheet.set_column('B:B', 45) # Nome
        worksheet.set_column('C:C', 15) # Status
        worksheet.set_column('D:D', 20) # Criticidade
        worksheet.set_column('E:E', 25) # User Story
        worksheet.set_column('F:F', 50) # Descrição
        worksheet.set_column('G:G', 30) # Etiquetas

        writer.close()

        print("\n" + "="*50)
        print(f"🎉 SUCESSO! Relatório gerado em '{os.path.abspath(nome_arquivo)}'")
        print("   A coluna 'Etiquetas' agora contém apenas os endpoints.")
        print("="*50)
    except Exception as e:
        print(f"\n❌ ERRO ao gerar o arquivo Excel: {e}")

if __name__ == "__main__":
    gerar_relatorio_excel()