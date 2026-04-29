import { headers } from "next/headers";

function getPythonBackendBaseUrl(): string | null {
  const raw = process.env.PYTHON_BACKEND_URL?.trim();
  if (!raw) return null;
  return raw.endsWith("/") ? raw.slice(0, -1) : raw;
}

export function hasPythonBackendConfigured(): boolean {
  return Boolean(getPythonBackendBaseUrl());
}

export async function forwardToPythonBackend(
  path: string,
  init?: RequestInit
): Promise<Response> {
  const baseUrl = getPythonBackendBaseUrl();
  if (!baseUrl) {
    throw new Error("PYTHON_BACKEND_URL não configurado.");
  }

  const requestHeaders = await headers();
  const cookie = requestHeaders.get("cookie");
  const auth = requestHeaders.get("authorization");

  const upstreamHeaders = new Headers(init?.headers);
  if (cookie) upstreamHeaders.set("cookie", cookie);
  if (auth) upstreamHeaders.set("authorization", auth);

  return fetch(`${baseUrl}${path}`, {
    ...init,
    headers: upstreamHeaders,
    cache: "no-store",
  });
}
