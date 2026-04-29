# Watty

App **Streamlit** (legado) e app **Next.js** para deploy no **Vercel** — tutor inteligente para alunos.

- **Web (Vercel):** pasta `web/` — ver [web/README.md](web/README.md) e [docs/web/environment-variables.md](docs/web/environment-variables.md) (sem ficheiros `.env` no Git).
- **Streamlit (local / Streamlit Cloud):** ver [GUIA_EXECUCAO.md](GUIA_EXECUCAO.md).

## Arranque rápido

```bash
pip install -r requirements.txt
```

Para correr testes Python: `pip install -r requirements-dev.txt` (inclui `pytest`).

O ecrã de login usa um **custom component** em React. Depois de clonar o repositório, gera o bundle uma vez:

```bash
cd watty_login_wizard/frontend
npm ci
npm run build
```

Na raiz do projeto:

```bash
streamlit run app.py
```

Configura `.streamlit/secrets.toml` com Gemini, Google Sheets e **Supabase** (login); lista completa em [GUIA_EXECUCAO.md](GUIA_EXECUCAO.md).
