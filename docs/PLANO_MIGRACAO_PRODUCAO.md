# Plano futuro — banco persistente para produção

## Decisão

- **Base de teste/local:** permanece com SQLite em `database/finance.db`.
- **Produção na Streamlit Cloud:** migrará futuramente para PostgreSQL, com
  preferência por Supabase, para que os dados não dependam do sistema de
  arquivos temporário do deploy.

## Motivo

SQLite atende bem ao uso local de uma pessoa. Na produção web, porém, novos
deploys e reinicializações podem recriar o ambiente. Um banco persistente
mantém usuários, receitas, despesas, cartões, faturas, holerites e logs entre
essas atualizações.

## Estratégia de migração

1. Criar o projeto Supabase/PostgreSQL e configurar as credenciais como
   secrets da Streamlit Cloud.
2. Criar as tabelas e índices equivalentes ao schema atual do FinanceOS.
3. Exportar uma cópia consistente do SQLite de produção.
4. Migrar os dados em transação, mantendo os IDs e o vínculo por `usuario_id`.
5. Validar quantidades e totais por usuário: receitas, despesas, compras,
   faturas, holerites, recorrências e eventos de segurança.
6. Ativar a produção no novo banco e manter o SQLite antigo apenas como backup
   de leitura até a confirmação final.
7. Remover `database/finance.db` do rastreamento do Git somente após a
   validação da produção persistente.

## Regras de segurança

- Nunca enviar senha, URL de banco ou chave de serviço para o Git.
- Usar os Secrets da Streamlit Cloud para as credenciais.
- Executar backup antes e depois da migração.
- A migração não altera a base local de teste.
