param(
  [string]$TaskName = "EndpointAuditAgent",
  [string]$RepoDir = ""
)

$ErrorActionPreference = "Stop"

function Resolve-RepoDir([string]$RepoDirParam) {
  if ($RepoDirParam -and (Test-Path -LiteralPath $RepoDirParam)) {
    return (Resolve-Path -LiteralPath $RepoDirParam).Path
  }
  return (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
}

$repo = Resolve-RepoDir $RepoDir
$dotenv = Join-Path $repo ".env"

schtasks /Query /TN $TaskName *>$null
if ($LASTEXITCODE -eq 0) {
  schtasks /End /TN $TaskName *>$null
  schtasks /Delete /TN $TaskName /F | Out-Host
  Write-Host "Deleted Scheduled Task '$TaskName'."
} else {
  Write-Host "Scheduled Task '$TaskName' not found."
}

if (Test-Path -LiteralPath $dotenv) {
  Remove-Item -LiteralPath $dotenv -Force
  Write-Host "Removed $dotenv"
}

Write-Host "Uninstall complete."

