import { useCallback, useRef, useState } from 'react';
import { vectorizeFile, downloadSvg, ApiError } from '../utils/api';
import { VectorizationParams, VectorizationResult, VectorizationStatus } from '../types/vectorization';

interface UseVectorizerReturn {
  status: VectorizationStatus;
  result: VectorizationResult | null;
  error: string | null;
  vectorize: (file: File, params: VectorizationParams) => Promise<void>;
  cancel: () => void;
  reset: () => void;
  download: () => void;
}

export function useVectorizer(): UseVectorizerReturn {
  const [status, setStatus] = useState<VectorizationStatus>('idle');
  const [result, setResult] = useState<VectorizationResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const vectorize = useCallback(async (file: File, params: VectorizationParams) => {
    // Cancel any in-flight request
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setStatus('uploading');
    setError(null);
    setResult(null);

    try {
      setStatus('processing');
      const res = await vectorizeFile(file, params, controller.signal);
      setResult(res);
      setStatus('done');
    } catch (err) {
      if ((err as Error).name === 'AbortError') {
        setStatus('idle');
        return;
      }
      const message = err instanceof ApiError ? err.message : 'Error inesperado. Inténtalo de nuevo.';
      setError(message);
      setStatus('error');
    }
  }, []);

  const cancel = useCallback(() => {
    abortRef.current?.abort();
    setStatus('idle');
  }, []);

  const reset = useCallback(() => {
    abortRef.current?.abort();
    setStatus('idle');
    setResult(null);
    setError(null);
  }, []);

  const download = useCallback(() => {
    if (result) downloadSvg(result.svgContent, result.filename);
  }, [result]);

  return { status, result, error, vectorize, cancel, reset, download };
}
