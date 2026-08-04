$ErrorActionPreference = "Stop"

$SettingsFile = Join-Path $PSScriptRoot "cloudsql-settings.ps1"

if (Test-Path $SettingsFile) {
  . $SettingsFile
} else {
  $ProjectId = "YOUR_PROJECT_ID"
  $Region = "us-central1"
  $ServiceName = "ai-career-intelligence-platform"
  $CloudSqlConnectionName = "YOUR_PROJECT:us-central1:YOUR_INSTANCE"
  $SecretKey = "your-secret-key"
  $DbName = "your_db_name"
  $DbUser = "your_db_user"
  $DbPassword = "your_db_password"
  $ServiceAccountEmail = "ai-career-runner@YOUR_PROJECT_ID.iam.gserviceaccount.com"
}

if (-not $ProjectId) { $ProjectId = "YOUR_PROJECT_ID" }
if (-not $Region) { $Region = "us-central1" }
if (-not $ServiceName) { $ServiceName = "ai-career-intelligence-platform" }
if (-not $ServiceAccountEmail) { $ServiceAccountEmail = "ai-career-runner@$ProjectId.iam.gserviceaccount.com" }

if (-not $CloudSqlConnectionName) {
  $CloudSqlConnectionName = "$ProjectId:$Region:ai-career-sql"
}

gcloud config set project $ProjectId
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com sqladmin.googleapis.com

gcloud run deploy $ServiceName `
  --source . `
  --region $Region `
  --allow-unauthenticated `
  --service-account $ServiceAccountEmail `
  --add-cloudsql-instances $CloudSqlConnectionName `
  --set-env-vars "SECRET_KEY=$SecretKey,DB_NAME=$DbName,DB_USER=$DbUser,DB_PASSWORD=$DbPassword,CLOUD_SQL_CONNECTION_NAME=$CloudSqlConnectionName"

Write-Host "Deployment command completed. Open the Cloud Run service URL shown by gcloud."