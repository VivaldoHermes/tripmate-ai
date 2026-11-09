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

Envie uma solicitação na interface, por exemplo: `Plan a trip from GRU to NRT including hotels and sightseeing`, preenchendo também **Data de ida** e **Data de volta**. Os campos permanecem preenchidos após uma resposta ou erro. O resumo do período exibe as datas, os dias e as noites calculados pelo servidor. As datas dos campos prevalecem sobre durações conflitantes no texto do pedido.

A integração atual de voos consulta dados de voos e status, sem cotação de passagens. A geração do roteiro depende das APIs externas configuradas.

Para encerrar a aplicação, pressione `Ctrl+C` no terminal.

## Datas da viagem na API

O `POST /api/travel` recebe as datas obrigatórias em formato `YYYY-MM-DD`, além de `message` e do `thread_id` opcional:

```json
{
  "message": "Planeje uma viagem de GRU para NRT com hospedagem e passeios",
  "departure_date": "2026-12-10",
  "return_date": "2026-12-15"
}
```

Em caso de sucesso, a resposta inclui `trip_period`, junto aos campos existentes do planejamento:

```json
{
  "departure_date": "2026-12-10",
  "return_date": "2026-12-15",
  "days": 6,
  "nights": 5
}
```

Os dias incluem a ida e a volta; as noites correspondem à diferença entre as datas. Ida e volta no mesmo dia resultam em 1 dia e 0 noites, sem hospedagem para pernoite. O período orienta a pesquisa de hospedagem (check-in e check-out) e a geração do roteiro.

Volta anterior à ida retorna HTTP 422 antes de chamar os agentes ou serviços externos:

```json
{
  "success": false,
  "error": "A data de volta deve ser igual ou posterior à data de ida."
}
```

Conferência manual pela interface, com a aplicação e suas integrações disponíveis:

| Ação | Resultado esperado |
| --- | --- |
| Informar ida em 10/12/2026 e volta em 15/12/2026 e gerar. | Resumo com as datas, 6 dias e 5 noites. |
| Alterar a volta para 12/12/2026 e gerar novamente. | Resumo atualizado para 3 dias e 2 noites. |
| Alterar a volta para 09/12/2026 e gerar novamente. | O envio é permitido; a API retorna 422 e a tela exibe a mensagem acima, preservando as datas para correção. |
| Corrigir a volta para 15/12/2026 e reenviar. | O erro desaparece e o planejamento volta a exibir 6 dias e 5 noites. |
| Informar ida e volta em 10/12/2026 e gerar. | Resumo com 1 dia e 0 noites. |

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
