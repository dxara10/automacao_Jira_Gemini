# 🚀 Ferramenta de Automação e Gestão para Jira (Projeto Bússola)

Bem-vindo à ferramenta de Automação para Jira! Este projeto foi desenvolvido para otimizar e automatizar a interação com o Atlassian Jira, focando na gestão de bugs, extração de métricas de testes e geração de relatórios estratégicos, apelidados de "Módulos Bússola".

## ✨ Apresentação da Ferramenta

A `automacao_JIRA_GEMINI` é um conjunto de scripts e ferramentas desenvolvidos em Python e TypeScript que se conectam à API do Jira para realizar tarefas que, de outra forma, seriam manuais e repetitivas. A solução é dividida em dois núcleos principais:

1.  **Gestão de Bugs:** Scripts para criar, atualizar, listar e excluir bugs de forma programática, agilizando o trabalho de equipes de QA e Desenvolvimento.
2.  **Módulo Bússola:** Uma suíte de relatórios e exportadores que fornecem uma visão clara (uma "bússola") sobre a saúde do projeto, incluindo mapas de cobertura de testes, panorama de bugs e exportação de dados para análise em Excel.

## 🏆 Principais Benefícios

* **Agilidade e Eficiência:** Reduza drasticamente o tempo gasto em tarefas manuais no Jira. Reporte um bug ou atualize dezenas de tarefas com um único comando.
* **Centralização e Visualização de Dados:** Exporte relatórios complexos, como planos de cobertura e listas de casos de teste, para formatos acessíveis como `.xlsx` e `.csv`, permitindo análises mais profundas.
* **Tomada de Decisão Baseada em Dados:** Com os relatórios do "Módulo Bússola" (mapa de bugs, panorama, etc.), gestores e líderes de equipe podem identificar gargalos, tendências de bugs e pontos críticos de cobertura de testes com mais facilidade.
* **Integração e Flexibilidade:** Por ser baseada em scripts, a ferramenta pode ser facilmente integrada a pipelines de CI/CD (Jenkins, GitLab CI, etc.) para automatizar a criação de tarefas após um build ou deploy com falha.
* **Padronização:** Garante que todos os bugs e tarefas sejam criados seguindo um mesmo padrão, melhorando a organização do projeto no Jira.

## ⚙️ Guia Completo de Instalação e Uso

Siga os passos abaixo para configurar e executar o projeto em seu ambiente local.

### Pré-requisitos

Antes de começar, garanta que você tenha os seguintes softwares instalados:
* [Git](https://git-scm.com/)
* [Python](https://www.python.org/downloads/) (versão 3.8 ou superior)
* [Node.js e npm](https://nodejs.org/en/) (versão 18 ou superior)
* Acesso a uma instância Jira (Cloud ou Server) e um Token de API.

### Passo 1: Clonar o Repositório

Abra seu terminal e clone este repositório para sua máquina local.

```bash
git clone <URL_DO_SEU_REPOSITORIO_GIT>
cd automacao_JIRA_GEMINI
```

### Passo 2: Configurar o Ambiente Python

É altamente recomendável usar um ambiente virtual (`venv`) para isolar as dependências do projeto.

```bash
# Criar o ambiente virtual (faça isso apenas uma vez)
python -m venv .venv

# Ativar o ambiente virtual
# No Windows:
.venv\Scripts\activate
# No macOS/Linux:
source .venv/bin/activate
```

Agora, instale as bibliotecas Python necessárias. Crie um arquivo `requirements.txt` na raiz do projeto com o seguinte conteúdo:

```txt
# requirements.txt
python-dotenv
jira
pandas
openpyxl
```

E então, instale-as com o pip:
```bash
pip install -r requirements.txt
```

### Passo 3: Configurar o Ambiente Node.js/TypeScript

Esta etapa é necessária para as ferramentas auxiliares ou interfaces construídas com TypeScript.

```bash
# Instalar as dependências do package.json
npm install

# Compilar os arquivos TypeScript para JavaScript (se necessário)
npx tsc
```

### Passo 4: Configurar as Variáveis de Ambiente

Para se conectar ao Jira de forma segura, a ferramenta usa variáveis de ambiente. Crie um arquivo chamado `.env` na raiz do projeto. **Nunca envie este arquivo para o repositório Git!**

Copie o conteúdo abaixo para o seu arquivo `.env` e preencha com suas credenciais:

```env
# .env
JIRA_SERVER="[https://sua-empresa.atlassian.net](https://sua-empresa.atlassian.net)"
JIRA_USERNAME="seu-email@empresa.com"
JIRA_API_TOKEN="SEU_TOKEN_DA_API_AQUI"
```
> **Como gerar um Token de API do Jira:** [Siga a documentação oficial da Atlassian](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/).

### Passo 5: Executando a Ferramenta

Com o ambiente virtual ativado (`source .venv/bin/activate`), você pode executar os scripts.

**Exemplo 1: Reportar um novo bug**
```bash
python bugs/reportar_bug.py --projeto "PROJ" --titulo "Botão de login não funciona" --descricao "O botão de login na página principal não responde ao clique."
```

**Exemplo 2: Exportar casos de teste para Excel**
```bash
python bussola/exportar_testes_excel.py --projeto "PROJ" --output "relatorio_final.xlsx"
```

**Exemplo 3: Listar bugs abertos**
```bash
python bugs/listar_bug.py --projeto "PROJ" --status "Em Aberto"
```

---
Feito com ❤️ por Douglas