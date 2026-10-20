[CmdletBinding()]
param([string]$ProjectRoot='',[switch]$Strict)
$ErrorActionPreference='Stop'; . (Join-Path $PSScriptRoot 'python-runtime.ps1'); $python = Get-TengerPython; if([string]::IsNullOrWhiteSpace($ProjectRoot)){$ProjectRoot=Split-Path -Parent $PSScriptRoot}; $args=@('knowledge','--project-root',$ProjectRoot); if($Strict){$args+='--strict'}; & $python (Join-Path $PSScriptRoot 'validate_core.py') @args; exit $LASTEXITCODE
