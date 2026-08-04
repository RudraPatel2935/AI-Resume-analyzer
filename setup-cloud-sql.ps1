$ErrorActionPreference = "Stop"

$ProjectId = "YOUR_PROJECT_ID"
$Region = "us-central1"
$InstanceName = "ai-career-sql"
$DbName = "ai_career_db"
$DbUser = "ai_career_user"
$ServiceAccountName = "ai-career-runner"

function New-RandomPassword {
  param([int]$Length = 24)

  $chars = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789!@#$%^&*()-_=+"
  $bytes = New-Object byte[] $Length
  [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
  $passwordChars = for ($i = 0; $i -lt $Length; $i++) {
    $chars[$bytes[$i] % $chars.Length]
  }

  -join $passwordChars
}

$DbPassword = New-RandomPassword
$SettingsFile = Join-Path $PSScriptRoot "cloudsql-settings.ps1"
$ServiceAccountEmail = "$ServiceAccountName@$ProjectId.iam.gserviceaccount.com"

gcloud config set project $ProjectId
gcloud services enable sqladmin.googleapis.com run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com

& gcloud iam service-accounts describe $ServiceAccountEmail *> $null
if ($LASTEXITCODE -ne 0) {
  gcloud iam service-accounts create $ServiceAccountName --display-name="AI Career Intelligence Platform runtime"
}

gcloud projects add-iam-policy-binding $ProjectId `
  --member="serviceAccount:$ServiceAccountEmail" `
  --role="roles/cloudsql.client"

& gcloud sql instances describe $InstanceName *> $null
if ($LASTEXITCODE -ne 0) {
  gcloud sql instances create $InstanceName `
    --database-version=POSTGRES_15 `
    --tier=db-f1-micro `
    --region=$Region
}

& gcloud sql databases describe $DbName --instance=$InstanceName *> $null
if ($LASTEXITCODE -ne 0) {
  gcloud sql databases create $DbName --instance=$InstanceName
}

& gcloud sql users describe $DbUser --instance=$InstanceName *> $null
if ($LASTEXITCODE -ne 0) {
  gcloud sql users create $DbUser --instance=$InstanceName --password=$DbPassword
}

$ConnectionName = "$ProjectId:$Region:$InstanceName"
Write-Host "Cloud SQL connection name: $ConnectionName"

@"

$ProjectId = "$ProjectId"
$Region = "$Region"
$InstanceName = "$InstanceName"
$ConnectionName = "$ConnectionName"
$DbName = "$DbName"
$DbUser = "$DbUser"
$DbPassword = "$DbPassword"
$ServiceAccountEmail = "$ServiceAccountEmail"
$SecretKey = "$([Guid]::NewGuid().ToString('N'))"
"@ | Set-Content -Path $SettingsFile -Encoding UTF8

Write-Host "Saved Cloud SQL values to $SettingsFile"
Write-Host "Import them before deployment with: . .\cloudsql-settings.ps1"