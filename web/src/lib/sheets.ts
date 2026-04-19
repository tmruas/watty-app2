import { google } from "googleapis";
import { SCOPES, SPREADSHEET_NAME, WORKSHEET_PERFIS } from "./watty-config";

export function getServiceAccountJson(): Record<string, unknown> {
  const raw = process.env.GCP_SERVICE_ACCOUNT_JSON?.trim();
  if (!raw) {
    throw new Error(
      "GCP_SERVICE_ACCOUNT_JSON em falta (JSON da conta de serviço Google)."
    );
  }
  return JSON.parse(raw) as Record<string, unknown>;
}

function getGoogleAuth() {
  return new google.auth.GoogleAuth({
    credentials: getServiceAccountJson(),
    scopes: SCOPES,
  });
}

let cachedSpreadsheetId: string | null = null;

export async function resolveSpreadsheetId(): Promise<string> {
  if (cachedSpreadsheetId) return cachedSpreadsheetId;
  const fromEnv = process.env.GOOGLE_SHEETS_SPREADSHEET_ID?.trim();
  if (fromEnv) {
    cachedSpreadsheetId = fromEnv;
    return fromEnv;
  }
  const auth = getGoogleAuth();
  const drive = google.drive({ version: "v3", auth });
  const q = `mimeType='application/vnd.google-apps.spreadsheet' and name='${SPREADSHEET_NAME.replace(/'/g, "\\'")}' and trashed=false`;
  const res = await drive.files.list({
    q,
    fields: "files(id, name)",
    pageSize: 2,
  });
  const id = res.data.files?.[0]?.id;
  if (!id) {
    throw new Error(
      `Não foi encontrada folha Google com o nome "${SPREADSHEET_NAME}". ` +
        "Define GOOGLE_SHEETS_SPREADSHEET_ID com o ID do URL da folha."
    );
  }
  cachedSpreadsheetId = id;
  return id;
}

export type PerfilCarregado = {
  xp: number;
  nivel: number;
  streak: number;
  linha_bd: number;
};

function parsePtDate(s: string): Date | null {
  const t = s.trim();
  const m = /^(\d{1,2})\/(\d{1,2})\/(\d{4})$/.exec(t);
  if (!m) return null;
  const d = parseInt(m[1], 10);
  const mo = parseInt(m[2], 10) - 1;
  const y = parseInt(m[3], 10);
  const dt = new Date(y, mo, d);
  return Number.isNaN(dt.getTime()) ? null : dt;
}

/** Espelho de carregar_perfil (watty/services/sheets.py). */
export async function carregarPerfil(nomeAluno: string): Promise<PerfilCarregado> {
  const spreadsheetId = await resolveSpreadsheetId();
  const auth = getGoogleAuth();
  const sheets = google.sheets({ version: "v4", auth });

  const range = `${WORKSHEET_PERFIS}!A2:E2000`;
  const res = await sheets.spreadsheets.values.get({
    spreadsheetId,
    range,
  });
  const rows = res.data.values ?? [];
  const hoje = new Date();
  const hojeStr = `${String(hoje.getDate()).padStart(2, "0")}/${String(hoje.getMonth() + 1).padStart(2, "0")}/${hoje.getFullYear()}`;

  const target = nomeAluno.trim().toLowerCase();

  for (let i = 0; i < rows.length; i++) {
    const row = rows[i];
    if (!row || row.length < 1) continue;
    const nome = String(row[0] ?? "").trim().toLowerCase();
    if (nome !== target) continue;

    const xp = parseInt(String(row[1] ?? "0"), 10) || 0;
    const nivel = parseInt(String(row[2] ?? "1"), 10) || 1;
    let streakAtual = parseInt(String(row[3] ?? "1"), 10) || 1;
    const ultimoLoginStr = String(row[4] ?? "");

    const ultimo = parsePtDate(ultimoLoginStr);
    if (ultimo) {
      const diffDays = Math.floor(
        (hoje.getTime() - ultimo.getTime()) / (1000 * 60 * 60 * 24)
      );
      if (diffDays === 1) streakAtual += 1;
      else if (diffDays > 1) streakAtual = 1;
    } else {
      streakAtual = 1;
    }

    const sheetRow = i + 2;
    await sheets.spreadsheets.values.batchUpdate({
      spreadsheetId,
      requestBody: {
        valueInputOption: "USER_ENTERED",
        data: [
          {
            range: `${WORKSHEET_PERFIS}!D${sheetRow}:E${sheetRow}`,
            values: [[streakAtual, hojeStr]],
          },
        ],
      },
    });

    return { xp, nivel, streak: streakAtual, linha_bd: sheetRow };
  }

  await sheets.spreadsheets.values.append({
    spreadsheetId,
    range: `${WORKSHEET_PERFIS}!A:E`,
    valueInputOption: "USER_ENTERED",
    requestBody: {
      values: [[nomeAluno.trim(), 0, 1, 1, hojeStr]],
    },
  });

  const after = await sheets.spreadsheets.values.get({
    spreadsheetId,
    range: `${WORKSHEET_PERFIS}!A:A`,
  });
  const numLinhas = (after.data.values ?? []).length;
  return { xp: 0, nivel: 1, streak: 1, linha_bd: numLinhas };
}

export async function guardarNoExcel(
  aba: string,
  tema: string,
  respostaIa: string,
  ano: string,
  disciplina: string,
  nomeAluno: string
): Promise<void> {
  try {
    const spreadsheetId = await resolveSpreadsheetId();
    const auth = getGoogleAuth();
    const sheets = google.sheets({ version: "v4", auth });
    const meta = await sheets.spreadsheets.get({ spreadsheetId });
    const firstTitle = meta.data.sheets?.[0]?.properties?.title ?? "Sheet1";
    const agora = new Date();
    const dataStr = `${String(agora.getDate()).padStart(2, "0")}/${String(agora.getMonth() + 1).padStart(2, "0")}/${agora.getFullYear()} ${String(agora.getHours()).padStart(2, "0")}:${String(agora.getMinutes()).padStart(2, "0")}:${String(agora.getSeconds()).padStart(2, "0")}`;

    await sheets.spreadsheets.values.append({
      spreadsheetId,
      range: `${firstTitle}!A:G`,
      valueInputOption: "USER_ENTERED",
      requestBody: {
        values: [
          [dataStr, nomeAluno, ano, disciplina, aba, tema, respostaIa],
        ],
      },
    });
  } catch (e) {
    console.error("Erro ao gravar no Google Sheets:", e);
  }
}

export async function verifyPerfilLinha(
  email: string,
  linhaBd: number
): Promise<boolean> {
  const spreadsheetId = await resolveSpreadsheetId();
  const auth = getGoogleAuth();
  const sheets = google.sheets({ version: "v4", auth });
  const res = await sheets.spreadsheets.values.get({
    spreadsheetId,
    range: `${WORKSHEET_PERFIS}!A${linhaBd}`,
  });
  const cell = String((res.data.values?.[0]?.[0] ?? "").trim()).toLowerCase();
  return cell === email.trim().toLowerCase();
}

export async function atualizarXpNivel(
  linhaBd: number,
  xp: number,
  nivel: number
): Promise<void> {
  try {
    const spreadsheetId = await resolveSpreadsheetId();
    const auth = getGoogleAuth();
    const sheets = google.sheets({ version: "v4", auth });
    await sheets.spreadsheets.values.batchUpdate({
      spreadsheetId,
      requestBody: {
        valueInputOption: "USER_ENTERED",
        data: [
          {
            range: `${WORKSHEET_PERFIS}!B${linhaBd}:C${linhaBd}`,
            values: [[xp, nivel]],
          },
        ],
      },
    });
  } catch {
    /* ignore */
  }
}
