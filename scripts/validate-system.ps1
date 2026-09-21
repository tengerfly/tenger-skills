[CmdletBinding()]
param([string]$ProjectRoot='',[switch]$SkipFixtures,[switch]$SkipKnowledge,[switch]$StrictKnowledge)
$ErrorActionPreference='Stop'; . (Join-Path $PSScriptRoot 'python-runtime.ps1'); $python = Get-TengerPython; if([string]::IsNullOrWhiteSpace($ProjectRoot)){$ProjectRoot=Split-Path -Parent $PSScriptRoot}; $args=@('system','--project-root',$ProjectRoot); if($SkipFixtures){$args+='--skip-fixtures'}; if($SkipKnowledge){$args+='--skip-knowledge'}; if($StrictKnowledge){$args+='--strict'}; & $python (Join-Path $PSScriptRoot 'validate_core.py') @args; exit $LASTEXITCODE
