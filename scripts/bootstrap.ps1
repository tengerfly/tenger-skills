[CmdletBinding()]
param([switch]$StrictKnowledge)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw 'Python 3.10+ is required. Install it and rerun bootstrap.ps1.'
}
$venv = Join-Path $root '.venv'
$relativePython = if ($env:OS -eq 'Windows_NT') { 'Scripts/python.exe' } else { 'bin/python' }
$venvPython = Join-Path $venv $relativePython
if (-not (Test-Path -LiteralPath $venvPython -PathType Leaf)) {
    python -m venv $venv
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
# Recover a venv whose creation was interrupted before ensurepip completed.
& $venvPython -c "import importlib.util, sys; sys.exit(0 if importlib.util.find_spec('pip') else 1)"
if ($LASTEXITCODE -ne 0) {
    & $venvPython -m ensurepip --upgrade --default-pip
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
& $venvPython -m pip install --disable-pip-version-check --requirement (Join-Path $root 'requirements.txt')
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
$previousPython = $env:TENGER_PYTHON
try {
    $env:TENGER_PYTHON = $venvPython
    $invoke = @{ProjectRoot=$root}
    if ($StrictKnowledge) { $invoke.StrictKnowledge=$true }
    & (Join-Path $PSScriptRoot 'validate.ps1') @invoke
    $result = $LASTEXITCODE
} finally {
    $env:TENGER_PYTHON = $previousPython
}
exit $result
