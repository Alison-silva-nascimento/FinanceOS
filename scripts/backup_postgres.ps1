param(
    [string]$Destino = ".\backups-postgres",
    [string]$DatabaseUrl = $env:DATABASE_URL
)

$ErrorActionPreference = "Stop"
if ([string]::IsNullOrWhiteSpace($DatabaseUrl)) {
    throw "Defina DATABASE_URL no ambiente. Nunca informe a senha na linha de comando."
}
if (-not (Get-Command pg_dump -ErrorAction SilentlyContinue)) {
    throw "pg_dump nao encontrado. Instale o cliente PostgreSQL e tente novamente."
}

$pasta = [IO.Path]::GetFullPath($Destino)
New-Item -ItemType Directory -Path $pasta -Force | Out-Null
$arquivo = Join-Path $pasta ("financeos-{0}.dump" -f (Get-Date -Format "yyyyMMdd-HHmmss"))

& pg_dump --dbname=$DatabaseUrl --format=custom --no-owner --no-privileges --file=$arquivo
if ($LASTEXITCODE -ne 0 -or -not (Test-Path $arquivo)) {
    throw "O backup do PostgreSQL falhou."
}

$hash = Get-FileHash -Algorithm SHA256 -LiteralPath $arquivo
"$($hash.Hash.ToLower())  $([IO.Path]::GetFileName($arquivo))" | Set-Content -Encoding ascii "$arquivo.sha256"
Write-Output "Backup criado: $arquivo"
Write-Output "Proteja e criptografe o arquivo antes de copia-lo para armazenamento externo."
