# Watty (Next.js)

Interface web migrada do Streamlit: autenticação Supabase, chat/quiz/resumos com Gemini, perfis em Google Sheets, jogos HTML e Watty TV.

## Requisitos

- Node 20+
- Conta Supabase (URL + anon key)
- Chave **Gemini** (`GEMINI_API_KEY`)
- Conta de serviço Google com acesso à folha **Watty_Logs** (mesmo JSON que no Streamlit: `GCP_SERVICE_ACCOUNT_JSON`)

## Configuração

1. Copia `web/.env.example` para `web/.env.local`.
2. Preenche as variáveis (Gemini e JSON da conta de serviço **só no servidor** — não uses `NEXT_PUBLIC_` para segredos).
3. Opcional: `GOOGLE_SHEETS_SPREADSHEET_ID` com o ID do URL da folha; se vazio, tenta localizar uma folha com o nome `Watty_Logs` no Drive da conta de serviço.

## Desenvolvimento

```bash
cd web
npm ci
npm run dev
```

Abre [http://localhost:3000](http://localhost:3000) — redireciona para `/login` se não houver sessão.

## Deploy (Vercel)

1. Importa o repositório e define **Root Directory** como `web`.
2. Adiciona as mesmas variáveis de ambiente do `.env.example` no painel Vercel (incluindo `GCP_SERVICE_ACCOUNT_JSON` como texto JSON numa única variável).
3. No Supabase Auth, adiciona o domínio Vercel aos **Redirect URLs** e define `NEXT_PUBLIC_SUPABASE_EMAIL_REDIRECT_URL` para `https://<teu-projeto>.vercel.app/login` se usares confirmação por email.

## Vídeos Watty TV

Coloca `wattyvid1.mp4` (e opcionalmente `wattyvid2.mp4`) em `web/public/media/` — o ficheiro grande pode ficar fora do Git e ser enviado manualmente ou via armazenamento externo.
