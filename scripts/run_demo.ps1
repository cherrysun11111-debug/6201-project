$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot
$env:PYTHONPATH = "src"

Write-Host "Starting demo at http://127.0.0.1:8000"
python -m ecrisk.app

