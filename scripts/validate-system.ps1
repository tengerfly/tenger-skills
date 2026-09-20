[CmdletBinding()]
param(
  [string]$ProjectRoot = '',
  [switch]$SkipFixtures
)

$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) { $ProjectRoot = Split-Path -Parent $PSScriptRoot }
$root = (Resolve-Path -LiteralPath $ProjectRoot).Path
$errors = [System.Collections.Generic.List[string]]::new()

function Read-Yaml([string]$Path) {
  $code = 'import sys,yaml,json,pathlib; print(json.dumps(yaml.safe_load(pathlib.Path(sys.argv[1]).read_text(encoding=chr(117)+chr(116)+chr(102)+chr(45)+chr(56))), ensure_ascii=False, default=str))'
  $output = & python -c $code $Path 2>&1
  if ($LASTEXITCODE -ne 0) {
    throw ('Cannot parse YAML: ' + $Path + [Environment]::NewLine + ($output -join [Environment]::NewLine))
  }
  return ($output -join [Environment]::NewLine) | ConvertFrom-Json
}

function Invoke-Check([string]$Path, [hashtable]$Arguments) {
  & $Path @Arguments
  if ($LASTEXITCODE -ne 0) { $errors.Add("check failed: $([IO.Path]::GetFileName($Path))") }
}
$skillRegistry = Join-Path $root 'governance/skill-registry.yaml'
$workflowRegistry = Join-Path $root 'governance/workflow-registry.yaml'
$stateRegistry = Join-Path $root 'governance/state-registry.yaml'
foreach ($path in @($skillRegistry, $workflowRegistry, $stateRegistry)) {
  if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { $errors.Add("registry not found: $path") }
}

$skills = $null
if ($errors.Count -eq 0) {
  try {
    $skills = Read-Yaml $skillRegistry
    [void](Read-Yaml $workflowRegistry)
    [void](Read-Yaml $stateRegistry)
  } catch { $errors.Add($_.Exception.Message) }
}

$skillIds = [System.Collections.Generic.HashSet[string]]::new()
if ($skills) {
  foreach ($entry in @($skills.skills)) {
    if (-not $entry.id) { $errors.Add('skill registry entry missing id'); continue }
    if (-not $skillIds.Add([string]$entry.id)) { $errors.Add("duplicate skill id: $($entry.id)") }
    if ($entry.status -eq 'active') {
      if (-not $entry.path) { $errors.Add("active skill missing path: $($entry.id)"); continue }
      $skillDir = Join-Path $root ([string]$entry.path)
      if (-not (Test-Path -LiteralPath $skillDir -PathType Container)) { $errors.Add("active skill directory not found: $($entry.path)") }
      elseif (-not (Test-Path -LiteralPath (Join-Path $skillDir 'SKILL.md') -PathType Leaf)) { $errors.Add("active skill SKILL.md not found: $($entry.path)") }
    }
  }
}

$scriptRoot = Join-Path $root 'scripts'
Invoke-Check -Path (Join-Path $scriptRoot 'validate-skill-contract.ps1') -Arguments @{}
Invoke-Check -Path (Join-Path $scriptRoot 'validate-workflow-graph.ps1') -Arguments @{}
Invoke-Check -Path (Join-Path $scriptRoot 'validate-artifact-manifest.ps1') -Arguments @{ ProjectRoot = $root }
Invoke-Check -Path (Join-Path $scriptRoot 'validate-traceability.ps1') -Arguments @{ ProjectRoot = $root }

if (-not $SkipFixtures) {
  $fixtureRoot = Join-Path $scriptRoot 'fixtures'
  foreach ($fixture in Get-ChildItem -LiteralPath $fixtureRoot -Directory -ErrorAction SilentlyContinue) {
    Invoke-Check -Path (Join-Path $scriptRoot 'validate-artifact-manifest.ps1') -Arguments @{ ProjectRoot = $fixture.FullName; RequireManifest = $true }
    Invoke-Check -Path (Join-Path $scriptRoot 'validate-traceability.ps1') -Arguments @{ ProjectRoot = $fixture.FullName; RequireTraceability = $true }
  }
}

if ($errors.Count -gt 0) {
  $errors | ForEach-Object { Write-Error $_ }
  Write-Output "System validation failed: $($errors.Count) error(s)"
  exit 1
}
Write-Output 'System validation passed'
exit 0