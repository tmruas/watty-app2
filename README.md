# Watty

App Streamlit — tutor inteligente para alunos.

Instruções de execução local: **[GUIA_EXECUCAO.md](GUIA_EXECUCAO.md)**.

## Arranque rápido

```bash
pip install -r requirements.txt
```

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
