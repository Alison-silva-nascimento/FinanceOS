# Backup e restauração do PostgreSQL/Supabase

Os backups devem permanecer fora do Git, preferencialmente criptografados e em
dois locais independentes. Os scripts nunca recebem a senha pela linha de
comando: eles leem `DATABASE_URL` somente do ambiente do processo.

## Criar backup

Instale as ferramentas cliente do PostgreSQL, abra um PowerShell privado e
defina temporariamente a URI atual. O comando abaixo solicita o valor de forma
oculta e o converte em texto somente na memória do processo.

```powershell
$segredo = Read-Host "Cole temporariamente a URI do Session Pooler" -AsSecureString
$env:DATABASE_URL = [System.Net.NetworkCredential]::new('', $segredo).Password
.\scripts\backup_postgres.ps1
Remove-Item Env:DATABASE_URL
```

O script produz um arquivo no formato customizado do `pg_dump` e seu hash
SHA-256. Mova ambos para armazenamento privado e criptografado. Nunca envie a
pasta `backups-postgres` ao GitHub.

## Testar restauração

Teste primeiro em outro projeto/banco PostgreSQL vazio. A opção `--clean`
remove objetos existentes no banco de destino; portanto confira rigorosamente a
URI antes de confirmar.

```powershell
$segredo = Read-Host "Cole a URI do banco de TESTE" -AsSecureString
$env:DATABASE_URL = [System.Net.NetworkCredential]::new('', $segredo).Password
.\scripts\restaurar_postgres.ps1 -Arquivo ".\backups-postgres\financeos-AAAAMMDD-HHMMSS.dump" -Confirmar
Remove-Item Env:DATABASE_URL
```

Após restaurar, inicie o FinanceOS no banco de teste e valide login, receitas,
despesas, cartões, faturas e Administração. Só considere um backup confiável
depois de uma restauração de teste bem-sucedida.
