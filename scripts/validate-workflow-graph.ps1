[CmdletBinding()]
param([string]$WorkflowRegistry='',[string]$SkillRegistry='',[string]$StateRegistry='')
$ErrorActionPreference='Stop'; if ($WorkflowRegistry -or $SkillRegistry -or $StateRegistry) { throw 'Registry overrides are unsupported: validate the coherent registry set in governance/.' }; . (Join-Path $PSScriptRoot 'python-runtime.ps1'); $python = Get-TengerPython; $root=Split-Path -Parent $PSScriptRoot; & $python (Join-Path $PSScriptRoot 'validate_core.py') graph --project-root $root; exit $LASTEXITCODE
