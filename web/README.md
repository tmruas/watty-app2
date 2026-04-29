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
cp .env.example .env.local
npm run dev
```

Abrir `http://localhost:3000`.

## Variáveis de ambiente

Ver `.env.example`.

Modos de execução suportados:

- **Next + fallback local**: Next fala diretamente com Google Sheets (`GCP_SERVICE_ACCOUNT_JSON` e `GOOGLE_SHEETS_SPREADSHEET_ID`).
- **Híbrido (recomendado para migração)**: definir `PYTHON_BACKEND_URL` para encaminhar `/api/profile`, `/api/profile/xp` e `/api/logs` para backend Python externo.

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
