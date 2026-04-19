/** Remove cercas ```json de respostas Gemini. */
export function stripJsonFence(text: string): string {
  return text
    .replace(/```json/gi, "")
    .replace(/```/g, "")
    .trim();
}
