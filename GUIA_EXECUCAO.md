# Execução local da Watty

Aplicação **Streamlit** (`app.py`). O ecrã de login depende de um **custom component** em React; o bundle tem de existir antes do primeiro arranque.

---

## Requisitos

- **Python 3** com `pip`
- **Node.js** com `npm` (apenas para compilar o frontend do login)

---

## 1. Dependências Python

Na **raiz do repositório**:

```bash
pip install -r requirements.txt
```

Recomenda-se um ambiente virtual (`python -m venv .venv`, ativar conforme o sistema operativo, depois o comando acima).

---

## 2. Build do componente de login (uma vez por checkout)

Na raiz do repositório:

```bash
cd watty_login_wizard/frontend
npm ci
npm run build
cd ../..
```

### Deploy no Streamlit Community Cloud

O Streamlit Cloud **não** executa automaticamente o `npm run build` do componente.
Por isso, a pasta `watty_login_wizard/frontend/build` tem de existir no repositório
Git enviado ao GitHub (faz build local e commit, ou confia no workflow CI que falha
se o bundle estiver desatualizado).

Se essa pasta não existir no repositório, o deploy falha com:
`No such component directory`.

**Checklist rápido**

1. Faz push do repositório para o GitHub (com `frontend/build` incluído).
2. Em [Streamlit Community Cloud](https://share.streamlit.io/), cria uma app nova
   (ou atualiza uma existente): escolhe o **repositório**, **branch** (ex. `main`)
   e ficheiro principal **`app.py`**.
3. Em **Advanced settings** (no ecrã de deploy), escolhe a **versão de Python**
   igual ou próxima da que usas em local (ex. 3.11 ou 3.12).
4. Em **Settings → Secrets** da app na cloud, cola o mesmo conteúdo TOML que
   terias em `.streamlit/secrets.toml` (não commits o ficheiro local; só o
   painel da cloud). Inclui `gcp_service_account` como bloco TOML equivalente ao JSON da Google.
5. No **Supabase → Authentication → URL Configuration → Redirect URLs**, adiciona
   o URL público da app (ex. `https://<subdominio>.streamlit.app`) além do URL local.

---

## 3. Segredos Streamlit

Criar `.streamlit/secrets.toml` na **raiz do repositório**. O código lê:

| Chave | Uso |
|--------|-----|
| `GEMINI_API_KEY` | API Gemini (`watty/services/gemini.py`) |
| `gcp_service_account` | Credenciais de conta de serviço Google para `gspread` (`watty/services/sheets.py`) |
| `SUPABASE_URL` | URL do projeto (Auth), ex. `https://xxxx.supabase.co` |
| `SUPABASE_ANON_KEY` | Chave **anon** (pública); o componente de login recebe-a via Streamlit |
| `SUPABASE_SERVICE_ROLE_KEY` | Chave **service_role** (só servidor): validar o JWT no Python — **não** expor no frontend nem em repositórios |
| `SUPABASE_EMAIL_REDIRECT_URL` | (Opcional) URL exata para o link de confirmação do email, ex. `http://localhost:8501`. Se omitires, o login usa a origem da página. Esta URL tem de estar em **Authentication → URL Configuration → Redirect URLs** no painel Supabase. |

No [Supabase](https://supabase.com/dashboard), ativa o provider **Email**. O envio do email de confirmação é feito pelo **Auth** do Supabase (não depende de tabelas `public` na base de dados).

**Se não recebes o email de confirmação:** verifica spam; confirma que **Redirect URLs** inclui o URL onde corres o Streamlit (ex. `http://localhost:8501`); em produção considera **SMTP personalizado** (Project Settings → Auth).

**Desenvolvimento local (recomendado):** em **Authentication → Providers → Email**, desativa **Confirm email**. Assim, após «Criar conta», entras logo sem esperar pelo correio (a sessão devolve-se imediatamente). Em produção volta a ativar confirmação se precisares.

O perfil na Google Sheet usa o **email em minúsculas** como valor da coluna **Nome** para utilizadores autenticados.

O formato TOML segue as regras do Streamlit para segredos; a estrutura de `gcp_service_account` corresponde ao JSON da conta de serviço Google.

---

## 4. Arranque

Na **raiz do repositório**:

```bash
streamlit run app.py
```

Entrada alternativa equivalente: `streamlit run watty_app.py` (reexporta `app.py`).

---

Documentação oficial útil: [Streamlit — Run](https://docs.streamlit.io/get-started/installation/command-line), [Secrets](https://docs.streamlit.io/develop/concepts/connections/secrets-management).
