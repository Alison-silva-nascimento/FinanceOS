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

## Segurança e dados

Os dados são armazenados localmente e associados ao usuário autenticado. A conta `alison.nascimento` é a única com perfil de administrador; todas as novas contas são usuários comuns. A senha é armazenada como hash PBKDF2, nunca em texto puro. O FinanceOS cria um backup consistente por dia em `backups/` e, no Windows, restringe o acesso ao banco e aos backups ao usuário que executa o app e ao sistema. O login bloqueia a conta por 10 minutos após cinco falhas consecutivas. PDFs são validados localmente (até 10 MB e 50 páginas), e imagens de perfil são verificadas antes de serem salvas. Não exponha a aplicação na internet.

## Próximos passos

- Baixa de faturas de cartão e conciliação bancária.
- Edição e arquivamento de metas, patrimônio e recorrências.
- Relatórios exportáveis mais completos.
