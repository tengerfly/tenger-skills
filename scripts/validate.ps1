[CmdletBinding()]
param(
    [string]$ProjectRoot = (Split-Path -Parent $PSScriptRoot),
    [switch]$StrictKnowledge,
    [switch]$SkipFixtures,
    [switch]$SkipKnowledge
)
$ErrorActionPreference = 'Stop'
$invoke = @{ProjectRoot=$ProjectRoot}
if ($StrictKnowledge) { $invoke.StrictKnowledge=$true }
if ($SkipFixtures) { $invoke.SkipFixtures=$true }
if ($SkipKnowledge) { $invoke.SkipKnowledge=$true }
& (Join-Path $PSScriptRoot 'validate-system.ps1') @invoke
exit $LASTEXITCODE
