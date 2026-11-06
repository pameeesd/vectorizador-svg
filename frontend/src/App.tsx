import React, { useEffect, useRef, useState } from 'react';
import { Dropzone } from './components/Dropzone';
import { ParamsPanel } from './components/ParamsPanel';
import { PreviewPanel } from './components/PreviewPanel';
import { useVectorizer } from './hooks/useVectorizer';
import { DEFAULT_PARAMS, VectorizationParams } from './types/vectorization';

const App: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [params, setParams] = useState<VectorizationParams>(DEFAULT_PARAMS);
  const { status, result, error, vectorize, cancel, reset, download } = useVectorizer();
  const prevUrlRef = useRef<string | null>(null);

  // Revoke old object URLs to avoid memory leaks
  useEffect(() => {
    if (prevUrlRef.current) URL.revokeObjectURL(prevUrlRef.current);
    if (file) {
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
      prevUrlRef.current = url;
    } else {
      setPreviewUrl(null);
    }
  }, [file]);

  const handleFile = (f: File) => {
    reset();
    setFile(f);
  };

  const handleVectorize = () => {
    if (file) vectorize(file, params);
  };

  const handleReset = () => {
    reset();
    setFile(null);
  };

  const isBusy = status === 'uploading' || status === 'processing';

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #0f0f1a 100%)',
      color: '#f3f4f6',
      fontFamily: "'Inter', system-ui, sans-serif",
      padding: '0 1rem 3rem',
    }}>
      {/* Header */}
      <header style={{ textAlign: 'center', padding: '2.5rem 0 1.5rem' }}>
        <h1 style={{ margin: 0, fontSize: 'clamp(1.8rem, 5vw, 2.8rem)', fontWeight: 800 }}>
          <span style={{ color: '#6366f1' }}>Vectorizador</span>SVG
        </h1>
        <p style={{ color: '#9ca3af', marginTop: '0.5rem', fontSize: '1rem' }}>
          Convierte imágenes rasterizadas a SVG vectorial de alta calidad · Open source
        </p>
        <a
          href="https://github.com/pameeesd/vectorizador-svg"
          target="_blank"
          rel="noopener noreferrer"
          style={{ color: '#6366f1', fontSize: '0.85rem', textDecoration: 'none' }}
        >
          ⭐ Ver en GitHub
        </a>
      </header>

      <main style={{ maxWidth: 1100, margin: '0 auto' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0,1fr) 300px', gap: '1.5rem' }}>
          {/* Left column */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            {!file && <Dropzone onFileSelected={handleFile} disabled={isBusy} />}

            {file && (
              <div style={{
                background: 'rgba(255,255,255,0.03)',
                borderRadius: '0.75rem',
                border: '1px solid rgba(255,255,255,0.08)',
                padding: '1rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
              }}>
                <span style={{ flex: 1, fontSize: '0.9rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  📄 {file.name} · {(file.size / 1024).toFixed(1)} KB
                </span>
                <button
                  onClick={handleVectorize}
                  disabled={isBusy || status === 'done'}
                  style={{
                    padding: '0.5rem 1.25rem',
                    borderRadius: '0.5rem',
                    border: 'none',
                    background: '#6366f1',
                    color: '#fff',
                    fontWeight: 700,
                    cursor: isBusy || status === 'done' ? 'not-allowed' : 'pointer',
                    opacity: isBusy || status === 'done' ? 0.6 : 1,
                  }}
                >
                  {isBusy ? '⏳ Procesando…' : '✨ Vectorizar'}
                </button>
                {isBusy && (
                  <button onClick={cancel} style={{
                    padding: '0.5rem 0.75rem', borderRadius: '0.5rem',
                    border: '1px solid #ef4444', background: 'transparent',
                    color: '#ef4444', cursor: 'pointer', fontWeight: 600,
                  }}>
                    Cancelar
                  </button>
                )}
              </div>
            )}

            {error && (
              <div style={{
                background: 'rgba(239, 68, 68, 0.1)',
                border: '1px solid rgba(239, 68, 68, 0.3)',
                borderRadius: '0.5rem',
                padding: '0.75rem 1rem',
                color: '#fca5a5',
                fontSize: '0.9rem',
              }}>
                ⚠️ {error}
              </div>
            )}

            {/* Status indicator */}
            {isBusy && (
              <div style={{ textAlign: 'center', color: '#9ca3af', fontSize: '0.9rem', animation: 'pulse 1.5s infinite' }}>
                🔄 Vectorizando imagen…
              </div>
            )}

            {(previewUrl || result) && (
              <PreviewPanel
                original={previewUrl}
                result={result}
                onDownload={download}
                onReset={handleReset}
              />
            )}
          </div>

          {/* Right column — parameters */}
          <ParamsPanel params={params} onChange={setParams} disabled={isBusy} />
        </div>
      </main>
    </div>
  );
};

export default App;
