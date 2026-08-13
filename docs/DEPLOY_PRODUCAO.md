# Deploy do FinanceOS em produção

Este guia publica o FinanceOS em um servidor Linux com Docker Compose, volume
persistente e HTTPS automático pelo Caddy.

## Requisitos

- Servidor Linux com Docker Engine e o plugin Docker Compose.
- Domínio apontando para o IP público do servidor.
- Portas TCP 80 e 443 liberadas no firewall.
- Acesso SSH restrito por chave.

## Preparar e iniciar

```bash
git clone <URL-DO-REPOSITORIO> financeos
cd financeos
cp .env.example .env
chmod 600 .env
docker compose config
docker compose build --pull
docker compose up -d
docker compose ps
docker compose logs --tail=100 financeos
```

Edite `.env` antes de iniciar. Informe o domínio real e o usuário administrador,
que deve seguir o formato `nome.sobrenome`. O Caddy solicita e renova o
certificado HTTPS automaticamente quando DNS e portas públicas estão corretos.
Mantenha `FINANCEOS_ALLOW_REGISTRATION=false`; habilite-o somente durante uma
janela controlada para criar uma nova conta e desative-o novamente em seguida.

Antes do primeiro push, retire bancos e caches que tenham sido rastreados em
commits antigos, sem apagar os arquivos locais:

```bash
git rm --cached database/finance.db
git rm -r --cached components/__pycache__ database/__pycache__ services/__pycache__
python scripts/check_release.py
```

`git rm --cached` não remove dados de commits anteriores. Se
`scripts/check_git_history.py` encontrar um banco, preserve um backup privado e
reescreva o histórico com `git filter-repo` antes de fazer o envio forçado. Essa
operação altera os identificadores dos commits e deve ser coordenada com todos
os clones do repositório.

## Primeiro acesso

1. Abra `https://SEU_DOMINIO`.
2. Crie a conta indicada em `FINANCEOS_ADMIN_USER`.
3. Use uma senha única, preferencialmente gerada por um gerenciador de senhas.
4. Confirme que a área Administração aparece somente nessa conta.
5. Teste uma importação pequena, um backup manual e seu download.

## PostgreSQL e RLS

Não use a role proprietária do projeto na conexão diária da aplicação. Crie uma
role exclusiva, sem `SUPERUSER`, `BYPASSRLS` ou propriedade das tabelas, conceda
somente as operações necessárias e use sua URI em `DATABASE_URL`. Ativar RLS sem
políticas compatíveis ou conectar como proprietário não cria isolamento efetivo.
Os papéis públicos `anon` e `authenticated` não precisam de acesso direto porque
o FinanceOS conversa com o PostgreSQL somente pelo servidor Streamlit.

## Persistência e escalabilidade

Banco e backups ficam no volume `financeos_data`, montado em `/data`. Não use
`docker compose down -v`, pois `-v` remove os volumes.

Enquanto o FinanceOS usar SQLite:

- mantenha exatamente uma réplica do contêiner `financeos`;
- não monte o SQLite simultaneamente em dois servidores;
- não use armazenamento de rede sem locking adequado;
- migre para PostgreSQL antes de escalar horizontalmente.

## Backup externo

O backup interno não substitui uma cópia fora do servidor. Exporte o volume
periodicamente para armazenamento criptografado:

```bash
mkdir -p exportados
docker run --rm \
  -v financeos_financeos_data:/data:ro \
  -v "$PWD/exportados:/backup" \
  alpine sh -c 'tar czf /backup/financeos-data-$(date +%Y%m%d-%H%M%S).tgz -C /data .'
```

Teste a restauração regularmente em outro volume ou servidor.

## Atualização e rollback

Antes de atualizar, gere um backup pela interface e exporte o volume:

```bash
git pull --ff-only
docker compose build --pull
docker compose up -d
docker compose ps
docker compose logs --tail=100 financeos
```

Se necessário, volte ao commit anterior e reconstrua:

```bash
git checkout <COMMIT_ANTERIOR>
docker compose build
docker compose up -d
```

Restaure dados somente quando necessário e preserve o volume atual. A
restauração pela interface valida o SQLite e cria uma cópia anterior.

## Monitoramento e segurança

- Monitore healthcheck, reinicializações, disco, volume e certificados.
- Guarde backups externos criptografados e teste sua restauração.
- Não publique a porta 8501 diretamente.
- Não armazene `.env`, bancos, backups ou logs no Git.
- Restrinja SSH, aplique firewall e mantenha o servidor atualizado.
- Use disco ou volume criptografado para proteção dos dados em repouso.
- Consulte os eventos de bloqueio e atividade na área Administração.
