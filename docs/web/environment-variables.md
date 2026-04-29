# Variáveis de ambiente (Watty Web)

Não commitar ficheiros `.env*`. Copia estes nomes para `.env.local` (local) ou para **Environment Variables** na Vercel.

| Variável | Obrigatório | Notas |
|----------|-------------|--------|
| `NEXT_PUBLIC_SUPABASE_URL` | Sim (auth) | URL do projeto Supabase |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Sim (auth) | Chave anon |
| `NEXT_PUBLIC_SUPABASE_EMAIL_REDIRECT_URL` | Opcional | URL de redirect de email (domínio da app) |
| `GEMINI_API_KEY` | Para IA | |
| `GEMINI_MODEL` | Opcional | Ex.: `gemini-2.5-flash` |
| `SESSION_SECRET` | Recomendado (prod) | String longa aleatória |
| `PYTHON_BACKEND_URL` | Opcional | Se definido: proxy de perfil/xp/logs para backend Python |
| `GCP_SERVICE_ACCOUNT_JSON` | Condicional | Só se Sheets forem usados no Next (sem proxy Python) |
| `GOOGLE_SHEETS_SPREADSHEET_ID` | Condicional | ID da folha no Google |

Ver também [web/README.md](../../web/README.md).

## Se alguma chave chegou ao Git por engano

Revoga essa chave nos respetivos dashboards (Google Cloud, Supabase, Gemini) e cria novas. Considera [remover dados sensíveis do histórico Git](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository).
