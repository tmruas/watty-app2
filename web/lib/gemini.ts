import { GoogleGenAI } from "@google/genai";

export const DEFAULT_MODEL =
  process.env.GEMINI_MODEL?.trim() || "gemini-2.5-flash";

let client: GoogleGenAI | null = null;

export function getGenAI(): GoogleGenAI {
  const key = process.env.GEMINI_API_KEY;
  if (!key) {
    throw new Error("GEMINI_API_KEY is not configured");
  }
  if (!client) {
    client = new GoogleGenAI({ apiKey: key });
  }
  return client;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export async function generateText(contents: any): Promise<string> {
  const ai = getGenAI();
  const res = await ai.models.generateContent({
    model: DEFAULT_MODEL,
    contents,
  });
  const text = res.text;
  if (!text) {
    throw new Error("Resposta vazia do modelo");
  }
  return text;
}

/** Remove cercas ```json do modelo. */
export function stripModelJson(text: string): string {
  return text.replace(/```json/gi, "").replace(/```/g, "").trim();
}
