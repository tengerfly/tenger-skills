[CmdletBinding()]
param([string]$ProjectRoot='')
$ErrorActionPreference='Stop'; . (Join-Path $PSScriptRoot 'python-runtime.ps1'); $python = Get-TengerPython; if([string]::IsNullOrWhiteSpace($ProjectRoot)){$ProjectRoot=Split-Path -Parent $PSScriptRoot}; & $python (Join-Path $PSScriptRoot 'validate_core.py') registry --project-root $ProjectRoot; exit $LASTEXITCODE
