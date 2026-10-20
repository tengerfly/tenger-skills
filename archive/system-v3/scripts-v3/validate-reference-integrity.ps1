[CmdletBinding()]
param([string]$ProjectRoot='')
$ErrorActionPreference='Stop'; . (Join-Path $PSScriptRoot 'python-runtime.ps1'); $python = Get-TengerPython; if([string]::IsNullOrWhiteSpace($ProjectRoot)){$ProjectRoot=Split-Path -Parent $PSScriptRoot}; & $python (Join-Path $PSScriptRoot 'validate_core.py') refs --project-root $ProjectRoot; if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}; & $python (Join-Path $PSScriptRoot 'check-installed-refs.py') --project-root $ProjectRoot --quiet; exit $LASTEXITCODE
