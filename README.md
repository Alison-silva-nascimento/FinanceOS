# FinanceOS

Aplicação local de gestão financeira pessoal criada com Python, Streamlit e SQLite.

## Funcionalidades atuais

- Cadastro, edição, exclusão e pesquisa de receitas e despesas.
- Dashboard com saldo, indicadores, gráficos e últimas movimentações.
- Gestão de cartões: limite, fechamento e vencimento.
- Gestão de contas bancárias: cadastro, edição e exclusão.

Os módulos Patrimônio e Metas estão planejados e são exibidos como funcionalidades em desenvolvimento.

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

Os dados são armazenados localmente. Na primeira execução, crie o usuário administrador pela tela inicial; a senha é armazenada como hash PBKDF2, nunca em texto puro. Não exponha a aplicação na internet. Faça cópias de segurança periódicas de `database/finance.db` antes de atualizações.

## Próximos passos

- Compras e faturas de cartão, incluindo parcelas.
- Filtros por mês e lançamentos recorrentes.
- Transferências e conciliação bancária.
- Metas, patrimônio e relatórios exportáveis.
