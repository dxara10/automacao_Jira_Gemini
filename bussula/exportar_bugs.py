import os
import pandas as pd
from jira import JIRA
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# --- Configurações da Conexão com o Jira ---
JIRA_SERVER = os.getenv("JIRA_URL")
JIRA_USERNAME = os.getenv("JIRA_USER_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")

# Verifica se as variáveis foram carregadas
if not all([JIRA_SERVER, JIRA_USERNAME, JIRA_API_TOKEN, JIRA_PROJECT_KEY]):
    print("Erro: Verifique se as variáveis JIRA_URL, JIRA_USER_EMAIL, JIRA_API_TOKEN, JIRA_PROJECT_KEY estão no arquivo .env.")
    exit()

# Conecta-se ao Jira
try:
    jira_client = JIRA(
        server=JIRA_SERVER,
        basic_auth=(JIRA_USERNAME, JIRA_API_TOKEN)
    )
    print(f"Conexão com o Jira ({JIRA_SERVER}) bem-sucedida!")
except Exception as e:
    print(f"Erro ao conectar com o Jira: {e}")
    exit()

# --- Definição da Busca (JQL) ---
jql_query = f'project = "{JIRA_PROJECT_KEY}" AND issuetype = Bug ORDER BY created DESC'
print(f"Buscando bugs com a query: {jql_query}")

issues = jira_client.search_issues(jql_query, maxResults=False)

# --- Extração e Processamento dos Dados ---
bugs_list = []
for issue in issues:
    labels = issue.fields.labels
    
    criticidade_encontrada = 'Não definida'
    endpoint_encontrado = 'Não definido'
    outras_etiquetas = []

    # Primeiro, classifica as etiquetas em listas separadas
    etiquetas_criticidade = []
    etiquetas_endpoint_explicito = []
    etiquetas_candidatas = []

    for label in labels:
        if label.lower().startswith(('gravidade-', 'criticidade-')):
            etiquetas_criticidade.append(label)
        elif label.lower().startswith(('funcionalidade_', 'endpoint_')):
            etiquetas_endpoint_explicito.append(label)
        else:
            etiquetas_candidatas.append(label)

    # Processa a criticidade (pega a primeira que encontrar)
    if etiquetas_criticidade:
        criticidade_encontrada = etiquetas_criticidade[0].split('-', 1)[1].replace('_', ' ').capitalize()

    # Processa o endpoint: prioriza o explícito, senão pega o primeiro candidato
    if etiquetas_endpoint_explicito:
        endpoint_encontrado = etiquetas_endpoint_explicito[0].split('_', 1)[1]
        outras_etiquetas.extend(etiquetas_candidatas) # O que sobrou vai para outras
        outras_etiquetas.extend(etiquetas_endpoint_explicito[1:]) # Se houver mais de um explícito
    elif etiquetas_candidatas:
        # Pega o primeiro candidato como endpoint e o resto vai para "outras"
        endpoint_encontrado = etiquetas_candidatas[0]
        outras_etiquetas.extend(etiquetas_candidatas[1:])

    bugs_list.append({
        'Chave': issue.key,
        'Resumo': issue.fields.summary,
        'Status': issue.fields.status.name,
        'Criticidade': criticidade_encontrada,
        'Endpoint/Módulo': endpoint_encontrado,
        'Outras Etiquetas': ', '.join(outras_etiquetas),
        'Responsável': issue.fields.assignee.displayName if issue.fields.assignee else 'Não atribuído',
        'Relator': issue.fields.reporter.displayName,
        'Criado em': issue.fields.created.split('T')[0],
    })

if not bugs_list:
    print("Nenhum bug encontrado com os critérios fornecidos.")
else:
    # --- Criação e Exportação para EXCEL ---
    df_bugs = pd.DataFrame(bugs_list)
    output_filename = 'relatorio_de_bugs.xlsx'
    
    colunas_ordenadas = [
        'Chave', 'Resumo', 'Status', 'Criticidade', 'Endpoint/Módulo', 
        'Responsável', 'Relator', 'Criado em', 'Outras Etiquetas'
    ]
    df_bugs = df_bugs[colunas_ordenadas]

    df_bugs.to_excel(output_filename, index=False)

    print(f"\nRelatório de bugs exportado com sucesso!")
    print(f"{len(bugs_list)} bugs foram salvos no arquivo Excel '{output_filename}'")