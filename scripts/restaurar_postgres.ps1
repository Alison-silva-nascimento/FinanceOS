param(
    [Parameter(Mandatory = $true)][string]$Arquivo,
    [string]$DatabaseUrl = $env:DATABASE_URL,
    [switch]$Confirmar
)

$ErrorActionPreference = "Stop"
if (-not $Confirmar) {
    throw "Restauracao nao executada. Revise o destino e use -Confirmar conscientemente."
}
if ([string]::IsNullOrWhiteSpace($DatabaseUrl)) {
    throw "Defina DATABASE_URL no ambiente. Nunca informe a senha na linha de comando."
}
if (-not (Test-Path -LiteralPath $Arquivo -PathType Leaf)) {
    throw "Arquivo de backup nao encontrado."
}
if (-not (Get-Command pg_restore -ErrorAction SilentlyContinue)) {
    throw "pg_restore nao encontrado. Instale o cliente PostgreSQL e tente novamente."
}

$resolvido = (Resolve-Path -LiteralPath $Arquivo).Path
if (Test-Path "$resolvido.sha256") {
    $esperado = ((Get-Content "$resolvido.sha256" -Raw).Trim() -split "\s+")[0]
    $atual = (Get-FileHash -Algorithm SHA256 -LiteralPath $resolvido).Hash.ToLower()
    if ($esperado.ToLower() -ne $atual) { throw "Hash SHA-256 invalido; restauracao cancelada." }
}

& pg_restore --dbname=$DatabaseUrl --clean --if-exists --no-owner --no-privileges --exit-on-error $resolvido
    if ($LASTEXITCODE -ne 0) { throw "A restauracao do PostgreSQL falhou." }
Write-Output "Restauracao concluida. Reinicie o FinanceOS e execute os testes funcionais."
