# Watty parity checklist (Streamlit -> Web)

Este documento congela a referência funcional para garantir equivalência da versão web sem Streamlit.

## Fluxos de autenticação

- [x] Login/registro com Supabase.
- [x] Sessão persistente em cookie SSR.
- [x] Gate de acesso para áreas autenticadas.
- [x] Páginas públicas institucionais (`/quem-somos`, `/termos`).

## Fluxos pedagógicos com IA

- [x] Chat principal com endpoint `/api/ai/chat`.
- [x] Quiz gerado por IA (`/api/ai/quiz/generate`).
- [x] Correção de quiz (`/api/ai/quiz/grade`).
- [x] Exame simulado (`/api/ai/exam`).
- [x] Resumos (`/api/ai/resumo`).

## Perfil e progressão

- [x] Carregar perfil do aluno (`/api/profile`).
- [x] Atualizar XP e nível (`/api/profile/xp`).
- [x] Registar atividade/logs (`/api/logs`).

## Conteúdo e media

- [x] Biblioteca de jogos HTML (`/jogos` + `/jogos/play`).
- [x] Watty TV com vídeos estáticos (`/watty-tv`).
- [x] Assets visuais em `web/public`.

## Critérios de aceitação para corte final Streamlit

- [ ] Build de produção (`npm run build`) sem erros.
- [ ] Fluxo completo login -> chat -> quiz -> perfil validado manualmente.
- [ ] Deploy na Vercel com `Root Directory=web`.
- [ ] Nenhum segredo via `.streamlit/secrets.toml` no runtime web.
