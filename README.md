# Backend Sistema GP

API FastAPI do Sistema GP. Este repositório é implantado separadamente do
frontend e usa PostgreSQL no Supabase.

## Configuração

O backend lê as variáveis `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD` e
`DB_NAME` do ambiente ou do arquivo local `.env`. O `.env` não deve ser usado
como mecanismo de distribuição de credenciais nem incluído em commits.
Configure também `AVALIADOR_CODIGO` com um código aleatório compartilhado de
alta entropia, e `ADMIN_CODIGO` para a administração. O backend exige pelo
menos 32 caracteres para ambos.
`ADMIN_TOKEN_SECRET` deve ser um segredo aleatório de pelo menos 32 caracteres,
usado para assinar as sessões administrativas e dos avaliadores. Não reutilize
os códigos publicados anteriormente; rotacione-os nos ambientes de produção.

Exemplo para gerar um valor seguro localmente no PowerShell:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Depois que um segredo ou credencial entrou no Git, removê-lo do arquivo atual
não apaga cópias dos commits antigos. Rotacione as credenciais no provedor do
banco e no ambiente de deploy; aplique também limite de tentativas no proxy ou
gateway que publica `/avaliadores/validar`.

O código compartilhado do evento autoriza o acesso à área de avaliação, mas não
prova a identidade individual de quem o utiliza. A identidade selecionada fica
assinada no token e não pode ser trocada na requisição de avaliação; ainda
assim, qualquer pessoa que conheça o código pode escolher outro avaliador. Para
validar identidade individual, será necessário migrar para credenciais por
avaliador.

## Migrations

Execute os comandos a partir da raiz deste repositório, depois de configurar o
ambiente:

```powershell
python -m pip install -r requirements.txt
alembic upgrade head
```

### PostgreSQL no Supabase

Para produção ou uso simultâneo por várias pessoas, o backend pode usar o
PostgreSQL do Supabase. Mantenha o acesso ao banco somente no FastAPI; não
coloque a URL nem credenciais do banco no frontend. Configure `DB_DRIVER` como
`postgresql` e `DATABASE_URL` com a connection string do Supabase, incluindo a
opção SSL recomendada pelo painel do projeto:

```powershell
$env:DB_DRIVER = "postgresql"
$env:DATABASE_URL = "<connection string PostgreSQL do Supabase>"
python -m alembic upgrade head
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
```

Armazene `DATABASE_URL` e os códigos/segredos da aplicação como variáveis
secretas no provedor de deploy, não em arquivos versionados. Use o pooler
recomendado pelo Supabase para o ambiente de hospedagem quando a rede do
provedor exigir conexão IPv4 ou pooling.

## Deploy independente na Vercel

Importe este repositório como um projeto Vercel separado, com **Root
Directory** na raiz. O entrypoint da função é `index.py`. Configure as
variáveis abaixo em **Project Settings → Environment Variables**:

- `DB_DRIVER=postgresql`
- `DATABASE_URL`: conexão PostgreSQL do Supabase com SSL.
- `ADMIN_CODIGO`: código aleatório com pelo menos 32 caracteres.
- `AVALIADOR_CODIGO`: código aleatório com pelo menos 32 caracteres.
- `ADMIN_TOKEN_SECRET`: segredo aleatório com pelo menos 32 caracteres.
- `CORS_ALLOWED_ORIGINS`: URL de produção exata do projeto Vercel do frontend,
  por exemplo `https://seu-frontend.vercel.app` (sem barra final).

Não use `*` em `CORS_ALLOWED_ORIGINS`. Para permitir mais de uma origem,
separe-as por vírgula. As URLs de Preview também precisam ser autorizadas
explicitamente se forem usadas para chamar esta API.

Antes do primeiro deploy, aplique as migrations no Supabase usando a mesma
`DATABASE_URL`. Não coloque credenciais no código nem no Git.

### Desenvolvimento local com SQLite

O backend continua usando MySQL por padrão. Para desenvolvimento local, é
possível selecionar SQLite sem instalar outro driver:

```powershell
$env:DB_DRIVER = "sqlite"
$env:DB_SQLITE_PATH = "$PWD\data\sistema_gp.sqlite3"
python -m alembic upgrade head
python -m uvicorn src.main:app --reload
```

As migrations criam o arquivo e as tabelas, além dos tipos básicos de usuário.
Os critérios e os usuários avaliadores são dados específicos do evento e não
são inventados pelas migrations; cadastre-os antes de testar avaliações.
A migration mais recente adiciona `curso`, `etapa`, `periodo` e `escola` à
tabela `escuderia`. As colunas ficam opcionais para equipes já cadastradas;
novos cadastros devem informar os quatro valores.

Em um banco vazio, `upgrade head` cria as tabelas e a coluna `avaliacao.comentario`.
Faça backup antes de migrar um banco com dados existentes.

Para um banco legado criado pelo script `src/db/sistema_gp.sql`, primeiro
confirme que as tabelas e constraints existentes correspondem à revisão
`20260930_01`. Em seguida, registre essa revisão sem recriar as tabelas e aplique
a migration aditiva:

```powershell
alembic stamp 20260930_01
alembic upgrade head
```

Se `avaliacao.comentario` já existir, confira o schema e registre a revisão
`20260930_02` para não tentar adicionar a coluna novamente; então aplique as
revisões seguintes normalmente:

```powershell
alembic stamp 20260930_02
alembic upgrade head
```

Nunca use `stamp` para contornar diferenças desconhecidas de schema. Compare o
banco com o script SQL e faça backup antes de registrar uma revisão.
Antes da revisão `20260930_03`, verifique se `resultado` não contém mais de uma
linha para a mesma combinação de `id_escuderia` e `id_divulgacao`; a migration
falhará explicitamente caso a constraint antiga não seja encontrada.

## Testes

Os testes unitários não precisam de banco:

```powershell
python -m unittest discover -s tests -v
```

Os testes de integração MySQL rodam somente com `APP_ENV=test` e configurações
separadas `DB_TEST_HOST`, `DB_TEST_PORT`, `DB_TEST_USER`, `DB_TEST_PASSWORD` e
`DB_TEST_NAME`. O nome do schema deve começar com `test_`; o código recusa outro
prefixo para evitar executar testes destrutivos contra um banco de produção.

Crie um schema descartável com nome como `test_sistema_gp`, configure as
variáveis acima apenas no terminal de teste e aplique as migrations nele:

```powershell
$env:APP_ENV = "test"
$env:DB_TEST_HOST = "127.0.0.1"
$env:DB_TEST_PORT = "3306"
$env:DB_TEST_USER = "<usuario-de-teste>"
$env:DB_TEST_PASSWORD = "<senha-de-teste>"
$env:DB_TEST_NAME = "test_sistema_gp"
alembic upgrade head
python -m unittest discover -s tests -v
```

Os testes de integração criam e removem apenas registros próprios nesse schema.
Eles nunca criam, limpam ou removem o banco inteiro.
