# FinanceOS no Cloudflare Workers

Esta pasta publica uma moldura estática para o FinanceOS hospedado no Streamlit Community Cloud. Ela usa o modo oficial de incorporação e recorta apenas a barra promocional externa do embed. O arquivo `wrangler.jsonc` na raiz aponta para estes arquivos estáticos.

## Configuração no Cloudflare Workers

- Build command: deixe vazio
- Deploy command: `npx wrangler deploy`
- Root directory: deixe como a raiz do repositório

Depois do primeiro deploy, o Cloudflare fornecerá um endereço no formato `https://financeos.<subdominio>.workers.dev`.

O FinanceOS e o PostgreSQL continuam hospedados no Streamlit e no Supabase. Esta pasta não contém senhas, dados financeiros ou conexão com o banco.
