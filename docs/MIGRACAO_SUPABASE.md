# Migração para Supabase (produção)

O FinanceOS continua usando SQLite por padrão na base de teste. Na produção,
quando `DATABASE_URL` estiver definida nos Secrets, ele passa a usar PostgreSQL.

## Segurança

- Não envie a URI com senha por chat, e-mail, GitHub ou commit.
- Não remova a regra `database/*.db` do `.gitignore`.
- Faça uma cópia do arquivo local `database/finance.db` antes da migração.
- A migração não apaga nada no Supabase por padrão. A opção `--substituir` é
  destinada somente a uma nova tentativa conscientemente autorizada.

## Preparar o ambiente local

No PowerShell, dentro de `C:\PROJETOFINANCE\FinanceOS`:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:DATABASE_URL = Read-Host "Cole a URI do Supabase"
.venv\Scripts\python.exe scripts\migrar_sqlite_para_supabase.py --confirmar
```

Use a URI do **Session pooler** do Supabase. Ela funciona em conexões IPv4,
como Streamlit Cloud. O script preserva IDs e copia usuários, dados financeiros,
faturas, importações, holerites e logs de segurança.

Se a primeira migração for interrompida e for necessário reiniciar do zero:

```powershell
.venv\Scripts\python.exe scripts\migrar_sqlite_para_supabase.py --confirmar --substituir
```

`--substituir` apaga os dados presentes no banco remoto antes da cópia.

## Configurar o Streamlit Cloud

No app de produção, abra **Settings > Secrets** e adicione somente:

```toml
DATABASE_URL = "postgresql://..."
```

Salve os Secrets e reinicie/redeploy o app. O Streamlit Cloud não deve receber
o arquivo `finance.db`: ele usará o Supabase a partir dessa configuração.

## Validar

1. Entre com `alison.nascimento` na produção.
2. Confira receitas, despesas, cartões e holerites.
3. Cadastre um lançamento de teste e confirme que ele continua presente após
   reiniciar o app.
