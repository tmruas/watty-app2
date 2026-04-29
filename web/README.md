# Watty Web (sem Streamlit)

Frontend e APIs em Next.js para deploy na Vercel.

## Estrutura

- App Router em `src/app`
- Componentes em `src/components`
- Lógica de domínio em `src/lib`
- Middleware em `src/middleware.ts`

## Desenvolvimento local

```bash
npm install
# Cria .env.local na mão (ver docs/web/environment-variables.md) — não há ficheiro de exemplo no Git
npm run dev
```

Abrir `http://localhost:3000`.

## Variáveis de ambiente

Lista de nomes e notas: [`docs/web/environment-variables.md`](../docs/web/environment-variables.md). Não há ficheiro `.env*` no repositório.

Modos de execução suportados:

- **Next + Google Sheets na Vercel**: define `GCP_SERVICE_ACCOUNT_JSON` + `GOOGLE_SHEETS_SPREADSHEET_ID` (e deixa `PYTHON_BACKEND_URL` vazio).
- **Híbrido**: define só `PYTHON_BACKEND_URL` para encaminhar `/api/profile`, `/api/profile/xp` e `/api/logs` ao teu backend Python; o Next não precisa de `GCP_SERVICE_ACCOUNT_JSON` para essas rotas.

### `GCP_SERVICE_ACCOUNT_JSON` (copiar para a Vercel)

1. Na [Google Cloud Console](https://console.cloud.google.com/), cria uma **conta de serviço**, ativa a API **Google Sheets** (e **Google Drive** se usares resolução por nome da folha).
2. Cria uma **chave JSON** e descarrega o ficheiro.
3. No projeto Vercel → **Settings → Environment Variables**, adiciona `GCP_SERVICE_ACCOUNT_JSON` com o **conteúdo completo do JSON** numa só linha (podes minificar com um formatador JSON) ou cola o JSON inteiro conforme o painel permitir multiline).
4. Partilha a folha Google Sheets com o **email** `client_email` do JSON (**Editor** ou leitura conforme precisares).
5. Define `GOOGLE_SHEETS_SPREADSHEET_ID` com o ID do URL da folha (entre `/d/` e `/edit`).

## Build e deploy

```bash
npm run build
```

Na Vercel:

- Root Directory: `web`
- Framework: Next.js
- Build Command: `npm run build`
- Install Command: `npm install`

## Notas de migração

- Não usar `.streamlit/secrets.toml`.
- Segredos devem ficar apenas em `.env.local` (local) e Environment Variables da Vercel (produção).
