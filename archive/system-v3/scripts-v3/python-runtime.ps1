# Shared interpreter selection; works in Windows PowerShell 5 and PowerShell 7.
function Get-TengerPython {
    if ($env:TENGER_PYTHON) { return $env:TENGER_PYTHON }
    $root = Split-Path -Parent $PSScriptRoot
    foreach ($relative in @('.venv/Scripts/python.exe', '.venv/bin/python')) {
        $candidate = Join-Path $root $relative
        if (Test-Path -LiteralPath $candidate -PathType Leaf) { return $candidate }
    }
    return 'python'
}
