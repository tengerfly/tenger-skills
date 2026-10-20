[CmdletBinding()]
param()
$ErrorActionPreference='Stop'; $root=(Resolve-Path (Join-Path $PSScriptRoot '..')).Path; . (Join-Path $PSScriptRoot 'python-runtime.ps1'); $python = Get-TengerPython; & $python -m unittest discover -s (Join-Path $PSScriptRoot 'tests') -p 'test_*.py' -v; exit $LASTEXITCODE
