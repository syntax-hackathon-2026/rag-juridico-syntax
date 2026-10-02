# Reproduce el pipeline completo en Windows desde cero (repo + .txt del corpus).
#   powershell -ExecutionPolicy Bypass -File reproducir.ps1 -Corpus C:\ruta\corpus
#   powershell -ExecutionPolicy Bypass -File reproducir.ps1 --hasta indice
# Todo lo que no sea un parametro propio se pasa a src\reproducibilidad\reproducir.py (ver --help).
# Solo instala Python 3.13 (winget) si falta; el resto (venv, torch CUDA, llama.cpp, GGUF) lo hace reproducir.py.
param([string]$Corpus, [Parameter(ValueFromRemainingArguments = $true)][string[]]$Resto)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONUTF8 = "1"

$req = (Select-String -Path requirements.txt -Pattern '^#\s*python:\s*(\d+\.\d+)').Matches[0].Groups[1].Value

function Buscar-Python {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        & py "-$req" -c "import sys" 2>$null
        if ($LASTEXITCODE -eq 0) { return @("py", "-$req") }
    }
    $p = Get-Command "python$req" -ErrorAction SilentlyContinue
    if ($p) { return @($p.Source) }
    return $null
}

$py = Buscar-Python
if (-not $py) {
    Write-Host "Python $req no encontrado; instalando con winget..."
    winget install -e --id "Python.Python.$req" --accept-package-agreements --accept-source-agreements
    # refrescar PATH de esta sesion
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
    $py = Buscar-Python
    if (-not $py) { throw "Python $req instalado pero no visible; abrir una terminal nueva y repetir." }
}

$argumentos = @()
if ($Corpus) { $argumentos += @("--corpus", $Corpus) }
$argumentos += $Resto
$exe = $py[0]; $pre = @(); if ($py.Count -gt 1) { $pre = $py[1..($py.Count - 1)] }
& $exe @pre src\reproducibilidad\reproducir.py @argumentos
exit $LASTEXITCODE
