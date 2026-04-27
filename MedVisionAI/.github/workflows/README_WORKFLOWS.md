# ⚙️ Configuração de CI/CD - GitHub Actions

## 📌 Status Atual

Os workflows de CI/CD estão **desabilitados temporariamente** para evitar falhas durante a apresentação do MVP.

Para o MVP acadêmico, o CI/CD não é obrigatório. O código pode ser demonstrado localmente com Docker Compose.

---

## 🚀 Como Habilitar CI/CD (Opcional)

Se você quiser habilitar os pipelines de CI/CD para deploy automático no Google Cloud Run, siga os passos abaixo:

### Pré-requisitos

1. ✅ Conta no Google Cloud Platform (GCP)
2. ✅ Projeto GCP criado
3. ✅ APIs habilitadas:
   - Cloud Run API
   - Cloud Build API
   - Container Registry API
   - Secret Manager API

### Passo 1: Criar Service Account no GCP

```bash
# Criar Service Account
gcloud iam service-accounts create github-actions \
  --description="Service Account para GitHub Actions" \
  --display-name="GitHub Actions"

# Adicionar permissões
gcloud projects add-iam-policy-binding SEU_PROJECT_ID \
  --member="serviceAccount:github-actions@SEU_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding SEU_PROJECT_ID \
  --member="serviceAccount:github-actions@SEU_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding SEU_PROJECT_ID \
  --member="serviceAccount:github-actions@SEU_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Criar chave JSON
gcloud iam service-accounts keys create gcp-key.json \
  --iam-account=github-actions@SEU_PROJECT_ID.iam.gserviceaccount.com
```

### Passo 2: Configurar Secrets no GitHub

1. Vá para `https://github.com/Ferstuque/MedVisionAI/settings/secrets/actions`

2. Clique em **"New repository secret"** e adicione:

| Nome | Valor | Descrição |
|------|-------|-----------|
| `GCP_PROJECT_ID` | `seu-project-id` | ID do projeto GCP |
| `GCP_SA_KEY` | `{JSON completo do gcp-key.json}` | Chave da Service Account |
| `GEMINI_API_KEY` | `sua-chave-gemini` | API key do Gemini 2.5 Flash |

**Exemplo de GCP_SA_KEY:**

```json
{
  "type": "service_account",
  "project_id": "medvision-ai-prod",
  "private_key_id": "abc123...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "github-actions@medvision-ai-prod.iam.gserviceaccount.com",
  "client_id": "123456789",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/..."
}
```

### Passo 3: Criar Secrets no Secret Manager (GCP)

```bash
# Gemini API Key
echo -n "SUA_GEMINI_API_KEY" | gcloud secrets create gemini-api-key \
  --data-file=- \
  --replication-policy="automatic"

# AWS Access Key (se usar S3)
echo -n "SUA_AWS_ACCESS_KEY" | gcloud secrets create aws-access-key \
  --data-file=- \
  --replication-policy="automatic"

# AWS Secret Key (se usar S3)
echo -n "SUA_AWS_SECRET_KEY" | gcloud secrets create aws-secret-key \
  --data-file=- \
  --replication-policy="automatic"

# Dar acesso à Service Account
gcloud secrets add-iam-policy-binding gemini-api-key \
  --member="serviceAccount:github-actions@SEU_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### Passo 4: Habilitar Workflows

Edite os arquivos `.github/workflows/cd.yml` e `.github/workflows/ci.yml`:

**cd.yml:**
```yaml
name: CD Pipeline

on:
  push:
    branches: [ main ]  # Remover comentário
  workflow_dispatch:
```

**ci.yml:**
```yaml
name: CI Pipeline

on:
  push:
    branches: [ main, develop ]  # Remover comentário
  pull_request:
    branches: [ main, develop ]  # Remover comentário
  workflow_dispatch:
```

### Passo 5: Commit e Push

```bash
git add .github/workflows/
git commit -m "chore: Habilita workflows de CI/CD"
git push
```

---

## 📊 Workflows Disponíveis

### CI Pipeline (`.github/workflows/ci.yml`)

**Triggers:**
- Push em `main` ou `develop`
- Pull Requests para `main` ou `develop`
- Manual (workflow_dispatch)

**Jobs:**
- ✅ Lint Python (Ruff)
- ✅ Testes Backend (pytest)
- ✅ Lint Frontend (ESLint)
- ✅ Build Frontend

### CD Pipeline (`.github/workflows/cd.yml`)

**Triggers:**
- Push em `main`
- Manual (workflow_dispatch)

**Jobs:**
- 🚀 Build Docker images (backend + frontend)
- 🚀 Push para Google Container Registry
- 🚀 Deploy no Cloud Run
- 📊 Obter URLs dos serviços
- 🔄 Rollback automático se falhar

---

## 🧪 Testar Localmente

Antes de habilitar CI/CD, teste o deploy local:

### Com Docker Compose

```bash
docker-compose up --build
```

### Com Terraform (Simula deploy GCP)

```bash
cd infrastructure
terraform init
terraform plan
# terraform apply  (cuidado: cria recursos reais no GCP)
```

---

## ⚠️ Custos GCP

**Cloud Run Pricing (us-central1):**
- ✅ Free Tier: 2M requests/mês + 360k GB-segundos
- 💰 Depois: ~$0.00002400/request

**Container Registry:**
- ✅ Free Tier: 0.5 GB storage
- 💰 Depois: $0.026/GB/mês

**Secret Manager:**
- ✅ 6 secret versions gratuitas
- 💰 $0.06/secret/mês

**Estimativa mensal (uso moderado):** $5-15 USD

---

## 🐛 Troubleshooting

### Erro: "credentials_json not found"
✅ Verifique que o secret `GCP_SA_KEY` está configurado no GitHub

### Erro: "Permission denied"
✅ Verifique as IAM roles da Service Account

### Erro: "Secret not found"
✅ Crie as secrets no Secret Manager do GCP

### Erro: "Image not found"
✅ Habilite Container Registry API

### Deploy demora muito
✅ Normal na primeira vez (baixa imagens base). Depois usa cache.

---

## 📚 Recursos

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Google Cloud Run Docs](https://cloud.google.com/run/docs)
- [GCP Service Accounts](https://cloud.google.com/iam/docs/service-accounts)
- [Secret Manager](https://cloud.google.com/secret-manager/docs)

---

## 🎯 Para MVP Acadêmico

**Você NÃO precisa habilitar CI/CD para a apresentação!**

Demonstre o sistema localmente com:

```bash
docker-compose up
```

O CI/CD é um **extra** que mostra conhecimento de DevOps, mas não é obrigatório para o MVP funcional.

---

**Última atualização:** 2026-02-13
