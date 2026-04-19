import { GoogleGenAI } from "@google/genai";
import { GEMINI_MODEL } from "./watty-config";

export function getGenAi(): GoogleGenAI {
  const key = process.env.GEMINI_API_KEY?.trim();
  if (!key) {
    throw new Error("GEMINI_API_KEY em falta nas variáveis de ambiente.");
  }
  return new GoogleGenAI({ apiKey: key });
}

/** Conteúdo aceite pelo SDK Gemini (texto ou estrutura multimodal). */
export async function generateContentText(contents: unknown): Promise<string> {
  const ai = getGenAi();
  const res = await ai.models.generateContent({
    model: GEMINI_MODEL,
    contents: contents as never,
  });
  return (res.text ?? "").trim();
}
