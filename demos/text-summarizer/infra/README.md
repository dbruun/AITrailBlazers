# Deploying AI Text Summarizer

The app is a single Python process with no third-party dependencies, so it runs anywhere
Python 3.8+ or Docker is available. All commands below are run from `demos/text-summarizer/`.

## Options

| Target | Steps |
|---|---|
| Local (Python) | `cd src && python app.py` → open <http://127.0.0.1:8000> |
| Local (Docker) | `docker build -t text-summarizer src && docker run --rm -p 8000:8000 text-summarizer` |
| Azure Container Apps | See below |

### Azure Container Apps

Requires the [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) and an Azure subscription.

```bash
az login
az group create --name rg-text-summarizer --location eastus

# Builds src/Dockerfile in Azure (no local Docker needed) and deploys it.
az containerapp up \
  --name text-summarizer \
  --resource-group rg-text-summarizer \
  --source src \
  --ingress external \
  --target-port 8000
```

To use Azure OpenAI instead of the offline summarizer, store the key as a secret and set the
environment variables:

```bash
az containerapp secret set -n text-summarizer -g rg-text-summarizer \
  --secrets aoai-key=<your-azure-openai-key>
az containerapp update -n text-summarizer -g rg-text-summarizer \
  --set-env-vars AZURE_OPENAI_ENDPOINT=https://<resource>.openai.azure.com \
                 AZURE_OPENAI_DEPLOYMENT=<deployment-name> \
                 AZURE_OPENAI_API_KEY=secretref:aoai-key
```

## Configuration

| Variable | Required | Description |
|---|---|---|
| `HOST` | No | Bind address. Defaults to `127.0.0.1` (`0.0.0.0` in the container). |
| `PORT` | No | Port to listen on. Defaults to `8000`. |
| `AZURE_OPENAI_ENDPOINT` | No | Azure OpenAI resource endpoint. Enables `azure-openai` mode with the two below. |
| `AZURE_OPENAI_API_KEY` | No | Azure OpenAI key. Never commit it – use secrets / environment variables. |
| `AZURE_OPENAI_DEPLOYMENT` | No | Name of a chat model deployment, e.g. `gpt-4o-mini`. |
| `AZURE_OPENAI_API_VERSION` | No | API version. Defaults to `2024-06-01`. |

## Clean up

```bash
az group delete --name rg-text-summarizer --yes --no-wait
```
