<#
write_env.ps1 - PowerShell wrapper for write_env.py
Usage:
    .\write_env.ps1 -Key "gems_hub:YOUR_KEY"
    .\write_env.ps1 (will prompt for key)
#>

param(
    [string]$Key
)

if (-not $Key) {
    $Key = Read-Host -Prompt 'Enter GEMDB API key (e.g. gems_hub:KEY)'
}

# Check Python availability
$pyCmd = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $pyCmd) {
    $pyCmd = (Get-Command py -ErrorAction SilentlyContinue).Source
}
if (-not $pyCmd) {
    Write-Host 'Python not found in PATH. Please install Python or add it to PATH.' -ForegroundColor Red
    exit 1
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$scriptPath = Join-Path $scriptDir 'write_env.py'
if (-not (Test-Path $scriptPath)) {
    Write-Host "Could not find write_env.py at $scriptPath" -ForegroundColor Red
    exit 1
}

& $pyCmd $scriptPath --key $Key
if ($LASTEXITCODE -ne 0) {
    Write-Host "write_env.py failed with exit code $LASTEXITCODE" -ForegroundColor Yellow
    exit $LASTEXITCODE
}
Write-Host "Wrote $scriptDir\.env (do not commit this file to VCS)" -ForegroundColor Green
