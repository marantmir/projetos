# 🏗️ Infraestrutura como Código (IaC)

Este diretório contém a configuração de infraestrutura para deploy do MedVision AI no Google Cloud Platform usando Terraform.

## 📋 Pré-requisitos

- [Terraform](https://www.terraform.io/downloads) >= 1.5
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
- Conta GCP com billing ativado
- Projeto GCP criado

## 🚀 Setup Inicial

### 1. Configurar GCP CLI

```bash
# Autenticar
gcloud auth login
gcloud auth application-default login

# Configurar projeto
gcloud config set project YOUR_PROJECT_ID
```

### 2. Criar Bucket para Terraform State

```bash
# Criar bucket para armazenar state do Terraform
gsutil mb -p YOUR_PROJECT_ID -l us-central1 gs://medvision-terraform-state/

# Habilitar versionamento
gsutil versioning set on gs://medvision-terraform-state/
```

### 3. Configurar Variáveis

```bash
# Copiar arquivo de exemplo
cp terraform.tfvars.example terraform.tfvars

# Editar com seus valores
nano terraform.tfvars
```

**terraform.tfvars:**
```hcl
project_id = "seu-projeto-gcp"
region     = "us-central1"
```

## 📦 Deploy

### Opção A: Deploy Completo

```bash
# Inicializar Terraform
terraform init

# Ver plano de execução
terraform plan

# Aplicar mudanças (será solicitado a API Key do Gemini)
terraform apply
```

### Opção B: Deploy com Variável de Ambiente

```bash
# Definir API Key via variável de ambiente
export TF_VAR_gemini_api_key="sua-chave-gemini-aqui"

# Aplicar
terraform apply -auto-approve
```

### Opção C: CI/CD (GitHub Actions)

O deploy automático é acionado no push para `main`. Configure os secrets:

- `GCP_PROJECT_ID`
- `GCP_SA_KEY` (Service Account JSON completo)
- `GEMINI_API_KEY`

## 🏗️ Recursos Criados

| Recurso | Tipo | Descrição |
|---------|------|-----------|
| **medvision-backend** | Cloud Run Service | Backend FastAPI containerizado |
| **gemini-api-key** | Secret Manager | API Key do Gemini (criptografado) |
| **medvision-backend-sa** | Service Account | Identidade para Cloud Run |
| **Container Registry** | GCR | Armazenamento de imagens Docker |

## 🔧 Configuração do Cloud Run

- **CPU**: 2 vCPUs
- **Memória**: 4 GB
- **Timeout**: 1 hora (para vídeos grandes)
- **Concurrency**: 80 requisições simultâneas
- **Auto-scaling**: 0-10 instâncias
- **Cold Start**: ~10-15 segundos

## 💰 Estimativa de Custos

| Item | Custo Mensal (USD) |
|------|-------------------|
| Cloud Run (100 req/dia) | ~$5-10 |
| Secret Manager | <$1 |
| Container Registry | ~$2-5 |
| **Total Estimado** | **~$8-16** |

*Baseado em uso moderado. Custos reais variam com tráfego.*

## 🔐 Segurança

### Secrets Management

- ✅ API Keys armazenadas no Secret Manager
- ✅ Criptografia automática em repouso
- ✅ Acesso via IAM roles granulares
- ✅ Auditoria via Cloud Logging

### IAM

```bash
# Verificar permissões da Service Account
gcloud projects get-iam-policy YOUR_PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:medvision-backend-sa@*"
```

## 📊 Monitoramento

### Logs

```bash
# Ver logs do Cloud Run
gcloud run services logs read medvision-backend \
  --region us-central1 \
  --limit 50

# Logs de erros
gcloud run services logs read medvision-backend \
  --region us-central1 \
  --filter="severity>=ERROR"
```

### Métricas

Acesse no GCP Console:
- **Cloud Run > medvision-backend > Metrics**
- Latência de requisições
- Taxa de erros
- Uso de CPU/memória
- Número de instâncias ativas

## 🔄 Atualizações

### Deploy de Nova Versão

```bash
# Build e push da imagem
cd backend
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/medvision-backend:latest

# Terraform aplicará automaticamente a nova imagem
terraform apply
```

### Rollback

```bash
# Listar revisões
gcloud run revisions list --service medvision-backend --region us-central1

# Reverter para revisão anterior
gcloud run services update-traffic medvision-backend \
  --region us-central1 \
  --to-revisions REVISION_NAME=100
```

## 🧹 Cleanup

```bash
# Destruir toda infraestrutura
terraform destroy

# Remover bucket de state (CUIDADO!)
gsutil rm -r gs://medvision-terraform-state/
```

## 🐛 Troubleshooting

### Erro: "Permission Denied"

```bash
# Verificar autenticação
gcloud auth list

# Re-autenticar
gcloud auth application-default login
```

### Erro: "API not enabled"

```bash
# Habilitar APIs manualmente
gcloud services enable run.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### Erro: "Insufficient quota"

- Aumentar quotas no [GCP Console](https://console.cloud.google.com/iam-admin/quotas)
- Solicitar aumento de limite para Cloud Run

## 📚 Referências

- [Terraform Google Provider](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Secret Manager Best Practices](https://cloud.google.com/secret-manager/docs/best-practices)

## 💡 Dicas de Produção

1. **Use múltiplos ambientes**: dev, staging, prod
2. **Habilite Cloud CDN**: Para assets estáticos
3. **Configure alertas**: Cloud Monitoring
4. **Backup do state**: Versioning no bucket GCS
5. **Use Workload Identity**: Para maior segurança
6. **Implemente rate limiting**: Cloud Armor
7. **Configure logs estruturados**: Para melhor observability

---

Para dúvidas ou issues, abra um ticket no GitHub.
