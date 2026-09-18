$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot
$env:PYTHONPATH = "src"

python -m ecrisk.data --rows 420 --seed 6201
python -m ecrisk.train
python -m ecrisk.evaluate
python -m ecrisk.batch
python -m unittest discover -s tests

Write-Host ""
Write-Host "Pipeline complete. Reports are in the reports directory."

