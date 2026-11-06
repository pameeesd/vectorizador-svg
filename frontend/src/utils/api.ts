import { VectorizationParams, VectorizationResult } from '../types/vectorization';

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? '/api/v1';

/** Allowed MIME types for client-side pre-validation. */
const ALLOWED_TYPES = new Set([
  'image/png',
  'image/jpeg',
  'image/jpg',
  'image/webp',
  'image/gif',
  'image/bmp',
]);

/** Maximum file size in bytes (10 MB — mirrors backend limit). */
const MAX_SIZE_BYTES = 10 * 1024 * 1024;

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

/** Client-side file validation before sending to the server. */
export function validateFile(file: File): void {
  if (!ALLOWED_TYPES.has(file.type)) {
    throw new ApiError(415, `Tipo de archivo no soportado: ${file.type}`);
  }
  if (file.size > MAX_SIZE_BYTES) {
    throw new ApiError(413, `El archivo supera el límite de 10 MB.`);
  }
  if (file.size === 0) {
    throw new ApiError(400, 'El archivo está vacío.');
  }
}

/** Upload and vectorize a file. Returns SVG content. */
export async function vectorizeFile(
  file: File,
  params: VectorizationParams,
  signal?: AbortSignal,
): Promise<VectorizationResult> {
  validateFile(file);

  const form = new FormData();
  form.append('file', file);
  Object.entries(params).forEach(([key, value]) => {
    form.append(key, String(value));
  });

  const response = await fetch(`${API_BASE}/vectorize`, {
    method: 'POST',
    body: form,
    signal,
    // No Authorization header needed — this is a public API
  });

  if (!response.ok) {
    let detail = `Error ${response.status}`;
    try {
      const json = await response.json();
      detail = json.detail ?? detail;
    } catch {
      /* ignore parse error */
    }
    throw new ApiError(response.status, detail);
  }

  const svgContent = await response.text();
  const disposition = response.headers.get('Content-Disposition') ?? '';
  const filenameMatch = disposition.match(/filename="([^"]+)"/);
  const filename = filenameMatch?.[1] ?? `${file.name.replace(/\.[^.]+$/, '')}.svg`;
  const fileHash = response.headers.get('X-File-Hash') ?? '';

  return { svgContent, filename, fileHash };
}

/** Trigger a browser download for the given SVG content. */
export function downloadSvg(svgContent: string, filename: string): void {
  const blob = new Blob([svgContent], { type: 'image/svg+xml' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  // Revoke the object URL after a short delay to free memory
  setTimeout(() => URL.revokeObjectURL(url), 5000);
}
