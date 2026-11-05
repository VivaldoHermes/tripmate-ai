# Tripmate AI

Assistente de planejamento de viagens com interface web em FastAPI. Usa LangGraph e Groq para gerar roteiros, Tavily para pesquisar hospedagens e AviationStack para consultar informações de voos. O PostgreSQL armazena o estado das conversas.

## Pré-requisitos

- Python 3.11 (versão indicada para o ambiente local).
- Docker com Docker Compose disponível e em execução, por exemplo, pelo Docker Desktop.
- Chaves de API da Groq, Tavily e AviationStack. Os links estão na seção de referências ao final.
- LangSmith é opcional, para rastreamento das chamadas.

Os comandos abaixo devem ser executados no PowerShell, na pasta raiz do projeto.

## 1. Instalar o Python

Caso ainda não esteja instalado:

```powershell
winget install --id Python.Python.3.11 -e
```

Após a instalação, abra um novo terminal e confira:

```powershell
py -3.11 --version
docker compose version
```

## 2. Criar o ambiente virtual e instalar as dependências

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Os comandos usam diretamente o Python do ambiente virtual, sem precisar ativá-lo.

## 3. Configurar o ambiente

Se ainda não existir um `.env`, copie o exemplo:

```powershell
Copy-Item .env.example .env
```

Edite o `.env` e preencha as chaves de API. O exemplo contém apenas valores fictícios; o `.env` com as credenciais locais é ignorado pelo Git.

| Variável | Uso |
| --- | --- |
| `POSTGRES_USER` | Usuário criado pelo contêiner PostgreSQL. |
| `POSTGRES_PASSWORD` | Senha do usuário do banco. |
| `POSTGRES_DB` | Nome do banco criado pelo contêiner. |
| `POSTGRES_PORT` | Porta local do banco; o exemplo usa `5432`. |
| `DATABASE_URL` | Conexão usada pela aplicação; deve corresponder aos valores do PostgreSQL. |
| `GROQ_API_KEY` | Chave da Groq, necessária para carregar o modelo. |
| `GROQ_MODEL` | Modelo usado pela aplicação; o padrão é `openai/gpt-oss-120b`. Precisa estar disponível para sua chave. |
| `TAVILY_API_KEY` | Chave da Tavily para pesquisa de hospedagens. |
| `AVIATIONSTACK_API_KEY` | Chave da AviationStack para consulta de voos. |
| `DEFAULT_ORIGIN_IATA` | Origem quando a consulta identifica apenas um destino. O exemplo usa `GRU` (Guarulhos); sem a variável, o código usa `DAC` (Dhaka). |
| `LANGSMITH_TRACING` | Ativa o rastreamento quando definido como `true`; o exemplo usa `false`. |
| `LANGSMITH_ENDPOINT` | Endpoint HTTPS do LangSmith. |
| `LANGSMITH_API_KEY` | Chave do LangSmith, necessária se o rastreamento estiver ativo. |
| `LANGSMITH_PROJECT` | Projeto que recebe os rastreamentos no LangSmith. |

Se alterar usuário, senha, banco ou porta, atualize também a `DATABASE_URL`. Caracteres especiais no usuário ou na senha precisam estar codificados para URL nessa conexão.

## 4. Iniciar o PostgreSQL

```powershell
docker compose up -d --wait
```

Esse comando inicia o banco e aguarda o healthcheck. O Compose executa somente o PostgreSQL; a aplicação Python roda localmente.

As tabelas de persistência do LangGraph são criadas automaticamente quando o backend inicia. Os dados do banco ficam no volume `tripmate_pgdata`. As variáveis de criação de usuário, senha e banco são aplicadas apenas na primeira inicialização de um volume vazio; editar o `.env` não altera as credenciais de um banco já existente.

## 5. Iniciar a aplicação

Com o PostgreSQL disponível:

```powershell
.\.venv\Scripts\python.exe app.py
```

Acesse:

- Interface: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Documentação da API: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Status da aplicação: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

Envie uma solicitação na interface, por exemplo: `Plan a 5 day trip from GRU to NRT including hotels and sightseeing`.

A integração atual de voos consulta dados de voos e status, sem cotação de passagens. A geração do roteiro depende das APIs externas configuradas.

Para encerrar a aplicação, pressione `Ctrl+C` no terminal.

## Comandos úteis do PostgreSQL

Consultar o estado:

```powershell
docker compose ps
```

Acompanhar os logs (`Ctrl+C` encerra apenas a visualização):

```powershell
docker compose logs -f postgres
```

Abrir o terminal SQL com o usuário e banco configurados no contêiner:

```powershell
docker compose exec postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
```

Use `\q` para sair do terminal SQL.

Parar o banco preservando os dados:

```powershell
docker compose stop
```

Para voltar a trabalhar, execute `docker compose up -d --wait` e depois `.\.venv\Scripts\python.exe app.py`.

## Sites de referência

- [Groq — chaves de API](https://console.groq.com/keys)
- [AviationStack — API de voos](https://aviationstack.com/)
- [Tavily — pesquisa web](https://www.tavily.com/)
- [LangSmith — criação de conta e chave de API](https://docs.langchain.com/langsmith/create-account-api-key)
