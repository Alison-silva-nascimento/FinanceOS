# FinanceOS no Cloudflare Pages

Esta pasta publica uma moldura estática para o FinanceOS hospedado no Streamlit Community Cloud. Ela usa o modo oficial de incorporação e recorta apenas a barra promocional externa do embed.

## Configuração no Cloudflare Pages

- Framework preset: `None`
- Build command: deixe vazio
- Build output directory: `cloudflare-pages`
- Root directory: deixe como a raiz do repositório

Depois do primeiro deploy, o Cloudflare fornecerá um endereço no formato `https://<projeto>.pages.dev`.

O FinanceOS e o PostgreSQL continuam hospedados no Streamlit e no Supabase. Esta pasta não contém senhas, dados financeiros ou conexão com o banco.
