# FinanceOS

Aplicação local de gestão financeira pessoal criada com Python, Streamlit e SQLite.

## Funcionalidades atuais

- Cadastro, edição, exclusão e pesquisa de receitas e despesas.
- Dashboard por mês com saldo, gráficos, vencimentos, metas, contas e patrimônio.
- Gestão de cartões, compras, faturas e parcelamentos.
- Gestão de contas bancárias e transferências entre contas.
- Orçamentos mensais, lançamentos recorrentes, metas e patrimônio.
- Importação de holerite em PDF, com leitura assistida de salário bruto, INSS, IRRF, consignado e salário líquido.
- Pagamento de faturas, conciliação de extrato CSV, central de alertas e relatórios CSV.
- Importação assistida de fatura Nubank em PDF, com prévia, identificação de parcelas e proteção contra duplicidade.
- Importação de faturas Mercado Pago, PicPay e outros emissores, com revisão de lançamentos ambíguos.
- Central Financeira com histórico e desfazer importações, fechamento mensal, regras de categoria, parcelas futuras e alertas.
- Conciliação bancária com prevenção de duplicidades e sugestões por valor/data.
- Backup SQLite consistente e restauração validada com cópia automática de segurança.
- Interface responsiva para desktop, ultrawide, tablet e celular, com ajustes para Chrome e Safari.
- Metadados de instalação web, áreas seguras do iPhone, acessibilidade e aviso de conexão perdida.
- Projeção mensal baseada em lançamentos e recorrências pendentes.
- Dados separados por usuário autenticado; senhas protegidas com PBKDF2.

## Como executar

Requer Python 3.11 ou superior.

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
streamlit run app.py
```

O banco SQLite é criado automaticamente em `database/finance.db` na primeira execução.

Para instalações próprias, é possível definir `FINANCEOS_DB_FILE` e
`FINANCEOS_BACKUP_DIR` antes de iniciar o Streamlit. Isso permite colocar o
banco e os backups em um volume persistente. O `compose.yaml` incluído usa o
volume `financeos_data`. O administrador e o tempo de sessão são configuráveis
por `FINANCEOS_ADMIN_USER` e `FINANCEOS_SESSION_TIMEOUT_MINUTES`.

## Segurança e dados

Os dados são associados ao usuário autenticado. A conta configurada em `FINANCEOS_ADMIN_USER` é a única administradora; todas as novas contas são usuários comuns. A senha é armazenada como hash PBKDF2, nunca em texto puro. O FinanceOS cria um backup consistente por dia, encerra sessões inativas e bloqueia a conta por 10 minutos após cinco falhas consecutivas. PDFs são validados localmente (até 10 MB e 50 páginas), e imagens de perfil são verificadas antes de serem salvas. Para publicação na internet, use o proxy HTTPS e siga o [guia de produção](docs/DEPLOY_PRODUCAO.md).

## Docker

```bash
cp .env.example .env
docker compose config
docker compose build --pull
docker compose up -d
```

Leia [docs/DEPLOY_PRODUCAO.md](docs/DEPLOY_PRODUCAO.md) antes de publicar.

Antes de cada release, execute `python scripts/check_release.py`. A verificação
bloqueia bancos, `.env`, secrets, caches e outros artefatos locais rastreados.

## Testes

```bash
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Os testes usam um banco temporário e não alteram os dados financeiros locais.

## Próximos passos

- Baixa de faturas de cartão e conciliação bancária.
- Edição e arquivamento de metas, patrimônio e recorrências.
- Relatórios exportáveis mais completos.
