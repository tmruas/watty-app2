# Contratos Next.js <-> Python backend

Quando `PYTHON_BACKEND_URL` está definido, as rotas Next.js encaminham pedidos para o backend Python externo.
Sem essa variável, o fallback local permanece ativo (Google Sheets direto no Next).

## Base URL

- `PYTHON_BACKEND_URL=https://api.watty.example`

## Endpoints de contrato

### `GET /api/profile`

- **Auth**: cookie/sessão Supabase ou header `Authorization`.
- **Resposta 200**:

```json
{
  "email": "aluno@escola.pt",
  "nome_display": "Aluno",
  "xp": 120,
  "nivel": 2,
  "streak": 4,
  "linha_bd": 12,
  "user_created_at": "2026-04-29T20:00:00.000Z"
}
```

### `POST /api/profile/xp`

- **Body**:

```json
{
  "xp": 150,
  "nivel": 3,
  "linha_bd": 12
}
```

- **Resposta 200**:

```json
{ "ok": true }
```

### `POST /api/logs`

- **Body**:

```json
{
  "aba": "quiz",
  "tema": "Frações",
  "resposta_ia": "conteúdo...",
  "ano": "6º Ano",
  "disciplina": "Matemática"
}
```

- **Resposta 200**:

```json
{ "ok": true }
```

## Regras operacionais

- Next.js propaga `cookie` e `authorization` para o backend Python.
- Em erro upstream, Next.js devolve o status e payload recebidos.
- O backend Python deve garantir validação de ownership (`linha_bd` pertence ao email autenticado).
