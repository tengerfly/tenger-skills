[CmdletBinding()]
param([string[]]$SkillPath=@(), [switch]$IncludeLegacy)
$ErrorActionPreference = 'Stop'
if ($SkillPath.Count -gt 0) { throw 'SkillPath filtering is unsupported; validate the registered repository Skill set.' }
. (Join-Path $PSScriptRoot 'python-runtime.ps1')
$python = Get-TengerPython
$arguments = @('skill-contract', '--project-root', (Split-Path -Parent $PSScriptRoot))
if ($IncludeLegacy) { $arguments += '--include-legacy' }
& $python (Join-Path $PSScriptRoot 'validate_core.py') @arguments
exit $LASTEXITCODE
