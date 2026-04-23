import { google } from "googleapis";
import { PERFIS_SHEET, SPREADSHEET_NAME } from "./constants";

type ServiceAccount = {
  client_email: string;
  private_key: string;
};

function parseServiceAccount(): ServiceAccount {
  const raw = process.env.GCP_SERVICE_ACCOUNT_JSON;
  if (!raw) {
    throw new Error("GCP_SERVICE_ACCOUNT_JSON is not configured");
  }
  const parsed = JSON.parse(raw) as ServiceAccount;
  if (!parsed.client_email || !parsed.private_key) {
    throw new Error("Invalid GCP_SERVICE_ACCOUNT_JSON");
  }
  return parsed;
}

export function getJwtAuth() {
  const creds = parseServiceAccount();
  return new google.auth.JWT({
    email: creds.client_email,
    key: creds.private_key,
    scopes: [
      "https://www.googleapis.com/auth/spreadsheets",
      "https://www.googleapis.com/auth/drive.readonly",
    ],
  });
}

let cachedSpreadsheetId: string | null = null;

export async function getSpreadsheetId(): Promise<string> {
  if (process.env.WATTY_SPREADSHEET_ID?.trim()) {
    return process.env.WATTY_SPREADSHEET_ID.trim();
  }
  if (cachedSpreadsheetId) return cachedSpreadsheetId;
  const auth = getJwtAuth();
  await auth.authorize();
  const drive = google.drive({ version: "v3", auth });
  const res = await drive.files.list({
    q: `mimeType='application/vnd.google-apps.spreadsheet' and name='${SPREADSHEET_NAME}' and trashed=false`,
    fields: "files(id,name)",
    spaces: "drive",
    pageSize: 5,
  });
  const id = res.data.files?.[0]?.id;
  if (!id) {
    throw new Error(
      `Spreadsheet "${SPREADSHEET_NAME}" não encontrada no Drive (ou define WATTY_SPREADSHEET_ID)`,
    );
  }
  cachedSpreadsheetId = id;
  return id;
}

function norm(s: string) {
  return s.trim().toLowerCase();
}

export type ProfileRow = {
  rowIndex1Based: number;
  nome: string;
  xp: number;
  nivel: number;
  streak: number;
  ultimoLogin: string;
};

function parseProfileRow(
  row: string[],
  rowIndex1Based: number,
): ProfileRow | null {
  if (row.length < 5 || !row[0]?.trim()) return null;
  return {
    rowIndex1Based,
    nome: row[0],
    xp: parseInt(row[1] || "0", 10) || 0,
    nivel: parseInt(row[2] || "1", 10) || 1,
    streak: parseInt(row[3] || "1", 10) || 1,
    ultimoLogin: row[4] || "",
  };
}

/** Carrega ou cria perfil — lógica de streak espelhada do Streamlit. */
export async function loadOrCreateProfile(nomeAluno: string): Promise<{
  xp: number;
  nivel: number;
  streak: number;
  linha_bd: number;
}> {
  const auth = getJwtAuth();
  await auth.authorize();
  const sheets = google.sheets({ version: "v4", auth });
  const spreadsheetId = await getSpreadsheetId();

  const range = `${PERFIS_SHEET}!A2:E2000`;
  const res = await sheets.spreadsheets.values.get({
    spreadsheetId,
    range,
  });
  const rows = res.data.values ?? [];
  const hoje = new Date();
  const hojeStr = `${String(hoje.getDate()).padStart(2, "0")}/${String(hoje.getMonth() + 1).padStart(2, "0")}/${hoje.getFullYear()}`;

  const target = norm(nomeAluno);
  let found: ProfileRow | null = null;

  for (let i = 0; i < rows.length; i++) {
    const pr = parseProfileRow(rows[i], i + 2);
    if (pr && norm(pr.nome) === target) {
      found = pr;
      break;
    }
  }

  if (found) {
    let streak = found.streak;
    try {
      const [d, m, y] = found.ultimoLogin.split("/").map(Number);
      const ultimo = new Date(y, m - 1, d);
      const diffDays = Math.floor(
        (hoje.getTime() - ultimo.getTime()) / (1000 * 60 * 60 * 24),
      );
      if (diffDays === 1) streak += 1;
      else if (diffDays > 1) streak = 1;
    } catch {
      streak = 1;
    }

    await sheets.spreadsheets.values.batchUpdate({
      spreadsheetId,
      requestBody: {
        valueInputOption: "USER_ENTERED",
        data: [
          {
            range: `${PERFIS_SHEET}!D${found.rowIndex1Based}:E${found.rowIndex1Based}`,
            values: [[String(streak), hojeStr]],
          },
        ],
      },
    });

    return {
      xp: found.xp,
      nivel: found.nivel,
      streak,
      linha_bd: found.rowIndex1Based,
    };
  }

  await sheets.spreadsheets.values.append({
    spreadsheetId,
    range: `${PERFIS_SHEET}!A:E`,
    valueInputOption: "USER_ENTERED",
    insertDataOption: "INSERT_ROWS",
    requestBody: {
      values: [[nomeAluno, 0, 1, 1, hojeStr]],
    },
  });

  const after = await sheets.spreadsheets.values.get({
    spreadsheetId,
    range: `${PERFIS_SHEET}!A:A`,
  });
  const col = after.data.values ?? [];
  const linha_bd = Math.max(2, col.length);

  return { xp: 0, nivel: 1, streak: 1, linha_bd };
}

export async function updateProfileXpNivel(
  linha_bd: number,
  xp: number,
  nivel: number,
): Promise<void> {
  const auth = getJwtAuth();
  await auth.authorize();
  const sheets = google.sheets({ version: "v4", auth });
  const spreadsheetId = await getSpreadsheetId();
  await sheets.spreadsheets.values.update({
    spreadsheetId,
    range: `${PERFIS_SHEET}!B${linha_bd}:C${linha_bd}`,
    valueInputOption: "USER_ENTERED",
    requestBody: {
      values: [[String(xp), String(nivel)]],
    },
  });
}

export async function appendActivityLog(row: {
  nome: string;
  ano: string;
  disciplina: string;
  aba: string;
  tema: string;
  resposta: string;
}): Promise<void> {
  const auth = getJwtAuth();
  await auth.authorize();
  const sheets = google.sheets({ version: "v4", auth });
  const spreadsheetId = await getSpreadsheetId();

  const meta = await sheets.spreadsheets.get({
    spreadsheetId,
    fields: "sheets(properties(sheetId,title,index))",
  });
  const first = meta.data.sheets
    ?.slice()
    .sort(
      (a, b) =>
        (a.properties?.index ?? 0) - (b.properties?.index ?? 0),
    )[0];
  const title = first?.properties?.title ?? "Sheet1";

  const agora = new Date();
  const agoraStr = `${String(agora.getDate()).padStart(2, "0")}/${String(agora.getMonth() + 1).padStart(2, "0")}/${agora.getFullYear()} ${String(agora.getHours()).padStart(2, "0")}:${String(agora.getMinutes()).padStart(2, "0")}:${String(agora.getSeconds()).padStart(2, "0")}`;

  await sheets.spreadsheets.values.append({
    spreadsheetId,
    range: `'${title.replace(/'/g, "''")}'!A1`,
    valueInputOption: "USER_ENTERED",
    insertDataOption: "INSERT_ROWS",
    requestBody: {
      values: [
        [
          agoraStr,
          row.nome,
          row.ano,
          row.disciplina,
          row.aba,
          row.tema,
          row.resposta,
        ],
      ],
    },
  });
}
