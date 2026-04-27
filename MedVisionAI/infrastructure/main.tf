# Terraform configuration for MedVision AI Infrastructure
# Deploys backend to Cloud Run with required services

terraform {
  required_version = ">= 1.5"
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }

  backend "gcs" {
    bucket = "medvision-terraform-state"
    prefix = "terraform/state"
  }
}

# Variables
variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "gemini_api_key" {
  description = "Google Gemini API Key"
  type        = string
  sensitive   = true
}

# Provider
provider "google" {
  project = var.project_id
  region  = var.region
}

# Enable Required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "run.googleapis.com",
    "secretmanager.googleapis.com",
    "cloudbuild.googleapis.com",
    "containerregistry.googleapis.com",
  ])
  
  service            = each.key
  disable_on_destroy = false
}

# Secret Manager - Gemini API Key
resource "google_secret_manager_secret" "gemini_api_key" {
  secret_id = "gemini-api-key"
  
  replication {
    auto {}
  }

  depends_on = [google_project_service.required_apis]
}

resource "google_secret_manager_secret_version" "gemini_api_key_version" {
  secret      = google_secret_manager_secret.gemini_api_key.id
  secret_data = var.gemini_api_key
}

# Service Account for Cloud Run
resource "google_service_account" "cloud_run_sa" {
  account_id   = "medvision-backend-sa"
  display_name = "MedVision Backend Service Account"
  description  = "Service account for MedVision AI backend on Cloud Run"
}

# Grant Secret Manager access to Service Account
resource "google_secret_manager_secret_iam_member" "cloud_run_secret_access" {
  secret_id = google_secret_manager_secret.gemini_api_key.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

# Cloud Run Service - Backend
resource "google_cloud_run_service" "backend" {
  name     = "medvision-backend"
  location = var.region

  template {
    spec {
      service_account_name = google_service_account.cloud_run_sa.email
      
      containers {
        image = "gcr.io/${var.project_id}/medvision-backend:latest"
        
        resources {
          limits = {
            cpu    = "2000m"
            memory = "4Gi"
          }
        }

        ports {
          container_port = 8000
        }

        env {
          name  = "ENVIRONMENT"
          value = "production"
        }

        env {
          name  = "LOG_LEVEL"
          value = "INFO"
        }

        env {
          name = "GEMINI_API_KEY"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.gemini_api_key.secret_id
              key  = "latest"
            }
          }
        }
      }

      container_concurrency = 80
      timeout_seconds       = 3600
    }

    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale" = "10"
        "autoscaling.knative.dev/minScale" = "0"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  depends_on = [
    google_project_service.required_apis,
    google_secret_manager_secret_version.gemini_api_key_version,
  ]
}

# Allow unauthenticated access (for MVP)
resource "google_cloud_run_service_iam_member" "public_access" {
  service  = google_cloud_run_service.backend.name
  location = google_cloud_run_service.backend.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Outputs
output "backend_url" {
  description = "URL do backend no Cloud Run"
  value       = google_cloud_run_service.backend.status[0].url
}

output "service_account_email" {
  description = "Email da Service Account"
  value       = google_service_account.cloud_run_sa.email
}
