[CmdletBinding()]
param(
  [string]$WorkflowRegistry = '',
  [string]$SkillRegistry = '',
  [string]$StateRegistry = ''
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$errors = [System.Collections.Generic.List[string]]::new()

function Read-Yaml([string]$Path) {
  $code = 'import sys,yaml,json,pathlib; print(json.dumps(yaml.safe_load(pathlib.Path(sys.argv[1]).read_text(encoding=chr(117)+chr(116)+chr(102)+chr(45)+chr(56))), ensure_ascii=False, default=str))'
  $output = & python -c $code $Path 2>&1
  if ($LASTEXITCODE -ne 0) {
    throw ('Cannot parse YAML: ' + $Path + [Environment]::NewLine + ($output -join [Environment]::NewLine))
  }
  return ($output -join [Environment]::NewLine) | ConvertFrom-Json
}

function Resolve-Registry([string]$Value, [string]$Default) {
  if ([string]::IsNullOrWhiteSpace($Value)) {
    return Join-Path $repoRoot $Default
  }
  if ([IO.Path]::IsPathRooted($Value)) {
    return $Value
  }
  return Join-Path (Get-Location).Path $Value
}

$WorkflowRegistry = Resolve-Registry $WorkflowRegistry 'governance/workflow-registry.yaml'
$SkillRegistry = Resolve-Registry $SkillRegistry 'governance/skill-registry.yaml'
$StateRegistry = Resolve-Registry $StateRegistry 'governance/state-registry.yaml'

foreach ($path in @($WorkflowRegistry, $SkillRegistry, $StateRegistry)) {
  if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
    $errors.Add("registry not found: $path")
  }
}
if ($errors.Count -gt 0) {
  $errors | ForEach-Object { Write-Error $_ }
  exit 1
}

try {
  $workflows = Read-Yaml $WorkflowRegistry
  $skills = Read-Yaml $SkillRegistry
  $states = Read-Yaml $StateRegistry
} catch {
  Write-Error $_
  exit 1
}

$knownSkills = [System.Collections.Generic.HashSet[string]]::new()
foreach ($entry in @($skills.skills) + @($skills.plannedSkills)) {
  if ($entry -and $entry.id) {
    [void]$knownSkills.Add([string]$entry.id)
  }
}

$knownStates = [System.Collections.Generic.HashSet[string]]::new()
foreach ($entry in @($states.states)) {
  if ($entry -and $entry.id) {
    [void]$knownStates.Add([string]$entry.id)
  }
}

$lifecycleModes = @($states.lifecycleModes | ForEach-Object { [string]$_ })
$knownGates = [System.Collections.Generic.HashSet[string]]::new()
foreach ($gate in @($states.gates)) {
  if ($gate) {
    [void]$knownGates.Add([string]$gate)
  }
}

$workflowList = @($workflows.workflows)
$workflowIds = [System.Collections.Generic.HashSet[string]]::new()
foreach ($workflow in $workflowList) {
  if (-not $workflow) { continue }
  $id = [string]$workflow.id
  if ([string]::IsNullOrWhiteSpace($id)) {
    $errors.Add('workflow missing id')
    continue
  }
  if (-not $workflowIds.Add($id)) {
    $errors.Add("duplicate workflow id: $id")
  }

  foreach ($skill in @($workflow.skills) + @($workflow.entrySkills)) {
    if ($skill -and -not $knownSkills.Contains([string]$skill)) {
      $errors.Add("$id references unregistered skill: $skill")
    }
  }
  foreach ($child in @($workflow.childWorkflows)) {
    if ($child -and -not ($workflowList | Where-Object { [string]$_.id -eq [string]$child })) {
      $errors.Add("$id references unknown child workflow: $child")
    }
  }
  foreach ($lifecycle in @($workflow.lifecycle) + @($workflow.entryLifecycle)) {
    if ($lifecycle -and $lifecycle -notin $lifecycleModes) {
      $errors.Add("$id has invalid lifecycle: $lifecycle")
    }
  }
  if ($workflow.exitGate -and -not $knownGates.Contains([string]$workflow.exitGate)) {
    $errors.Add("$id has unregistered exit gate: $($workflow.exitGate)")
  }
}

$stateIds = [System.Collections.Generic.HashSet[string]]::new()
foreach ($state in @($states.states)) {
  if ($state -and $state.id -and -not $stateIds.Add([string]$state.id)) {
    $errors.Add("duplicate state id: $($state.id)")
  }
}

$transitionIds = [System.Collections.Generic.HashSet[string]]::new()
foreach ($transition in @($states.transitions)) {
  if (-not $transition) { continue }
  $from = [string]$transition.from
  $to = [string]$transition.to
  if (-not $knownStates.Contains($from)) {
    $errors.Add("transition has unknown from state: $from")
  }
  if (-not $knownStates.Contains($to)) {
    $errors.Add("transition has unknown to state: $to")
  }
  $key = "$from->$to"
  if (-not $transitionIds.Add($key)) {
    $errors.Add("duplicate transition: $key")
  }
}

# v1 skills are part of the governed graph. Their State Changes section may not
# introduce undocumented states; this prevents documentation and registry drift.
foreach ($skill in @($skills.skills)) {
  if (-not $skill -or [string]$skill.contractLevel -ne 'v1' -or [string]$skill.status -ne 'active') {
    continue
  }
  $skillPath = Join-Path $repoRoot ([string]$skill.path)
  $skillFile = Join-Path $skillPath 'SKILL.md'
  if (-not (Test-Path -LiteralPath $skillFile -PathType Leaf)) {
    continue
  }
  $content = [IO.File]::ReadAllText($skillFile, [Text.UTF8Encoding]::new($false))
  $section = [regex]::Match($content, '(?ms)^##\s+State Changes\s*$([\s\S]*?)(?=^##\s+|\z)')
  if (-not $section.Success) {
    continue
  }
  $tokens = [regex]::Matches($section.Groups[1].Value, '\b[A-Z][A-Z0-9_]+\b') |
    ForEach-Object { $_.Value } |
    Sort-Object -Unique
  foreach ($token in $tokens) {
    if ($token -notin $lifecycleModes -and -not $knownStates.Contains($token)) {
      $errors.Add("$($skill.id) State Changes references unregistered state: $token")
    }
  }
}

if ($errors.Count -gt 0) {
  $errors | ForEach-Object { Write-Error $_ }
  Write-Output "Workflow graph validation failed: $($errors.Count) error(s)"
  exit 1
}

Write-Output "Workflow graph validation passed: $($workflowList.Count) workflow(s), $(@($states.transitions).Count) transition(s)"
exit 0

