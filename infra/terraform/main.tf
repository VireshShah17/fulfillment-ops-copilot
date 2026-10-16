resource "google_cloud_run_v2_service" "ops_copilot" {
  name     = "ops-copilot-api"
  location = "us-central1"

  template {
    scaling {
      min_instance_count = 0
      max_instance_count = 5
    }

    containers {
      image = "gcr.io/your-gcp-project-id/ops-copilot:latest"

      env {
        name  = "GEMINI_MODEL"
        value = "gemini-2.5-flash"
      }

      env {
        name = "GEMINI_API_KEY"
        value_source {
          secret_key_ref {
            secret  = "projects/your-gcp-project-id/secrets/gemini-api-key"
            version = "latest"
          }
        }
      }
    }
  }
}