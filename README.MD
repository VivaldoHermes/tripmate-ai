# Tripmate AI

## Instalar o Python

```powershell
winget install --id Python.Python.3.11 -e
```

## Instalar as dependências

```powershell
python -m pip install -r requirements.txt
```

## Iniciar o PostgreSQL

```powershell
docker compose up -d
```

## Consultar o estado

```powershell
docker compose ps
```

## Consultar os logs

```powershell
docker compose logs -f postgres
```

## Acessar o PostgreSQL

```powershell
docker compose exec postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
```

## Parar o PostgreSQL

```powershell
docker compose stop
```

GROQ
https://console.groq.com/keys

AVIATIONSTACK
https://aviationstack.com/

TAVILY
https://www.tavily.com/

LANGSMITH
https://docs.langchain.com/langsmith/create-account-api-key