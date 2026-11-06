import React from 'react';
import { Download, RotateCcw, ZoomIn, ZoomOut } from 'lucide-react';
import { VectorizationResult } from '../types/vectorization';

interface PreviewPanelProps {
  original: string | null;    // Object URL of original image
  result: VectorizationResult | null;
  onDownload: () => void;
  onReset: () => void;
}

export const PreviewPanel: React.FC<PreviewPanelProps> = ({
  original, result, onDownload, onReset,
}) => {
  const [zoom, setZoom] = React.useState(1);

  const panelStyle: React.CSSProperties = {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    background: 'rgba(255,255,255,0.03)',
    border: '1px solid rgba(255,255,255,0.08)',
    borderRadius: '0.75rem',
    padding: '1rem',
    minHeight: 300,
    overflow: 'hidden',
    position: 'relative',
  };

  const imgStyle: React.CSSProperties = {
    maxWidth: '100%',
    maxHeight: 400,
    transform: `scale(${zoom})`,
    transformOrigin: 'center',
    transition: 'transform 0.2s',
  };

  const ZoomControls = () => (
    <div style={{ position: 'absolute', bottom: '0.75rem', right: '0.75rem', display: 'flex', gap: '0.4rem' }}>
      <button onClick={() => setZoom(z => Math.min(z + 0.25, 4))} style={btnStyle} title="Acercar">
        <ZoomIn size={16} />
      </button>
      <button onClick={() => setZoom(1)} style={btnStyle} title="100%">1×</button>
      <button onClick={() => setZoom(z => Math.max(z - 0.25, 0.25))} style={btnStyle} title="Alejar">
        <ZoomOut size={16} />
      </button>
    </div>
  );

  const btnStyle: React.CSSProperties = {
    background: 'rgba(255,255,255,0.08)',
    border: '1px solid rgba(255,255,255,0.12)',
    borderRadius: '0.4rem',
    color: '#fff',
    cursor: 'pointer',
    padding: '0.3rem 0.5rem',
    display: 'flex',
    alignItems: 'center',
    fontSize: '0.75rem',
  };

  return (
    <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
      {/* Original */}
      <div style={{ ...panelStyle, flex: '1 1 240px' }}>
        <p style={{ margin: '0 0 0.75rem', fontWeight: 600, color: '#9ca3af', fontSize: '0.8rem', alignSelf: 'flex-start' }}>ORIGINAL</p>
        {original
          ? <img src={original} alt="Imagen original" style={imgStyle} />
          : <p style={{ color: '#4b5563' }}>Sin imagen</p>
        }
        {original && <ZoomControls />}
      </div>

      {/* SVG result */}
      <div style={{ ...panelStyle, flex: '1 1 240px' }}>
        <p style={{ margin: '0 0 0.75rem', fontWeight: 600, color: '#9ca3af', fontSize: '0.8rem', alignSelf: 'flex-start' }}>VECTOR SVG</p>
        {result
          ? (
            <>
              {/* Render SVG using dangerouslySetInnerHTML is intentional here:
                  the SVG comes from our own backend (never from arbitrary user input).
                  The backend only produces vtracer-generated SVG. */}
              <div
                style={imgStyle}
                dangerouslySetInnerHTML={{ __html: result.svgContent }}
              />
              <ZoomControls />
            </>
          )
          : <p style={{ color: '#4b5563' }}>El resultado aparecerá aquí</p>
        }
      </div>

      {/* Action buttons */}
      {result && (
        <div style={{ width: '100%', display: 'flex', gap: '0.75rem', justifyContent: 'flex-end' }}>
          <button onClick={onReset} style={{ ...btnStyle, padding: '0.5rem 1rem' }}>
            <RotateCcw size={16} style={{ marginRight: '0.4rem' }} /> Nueva imagen
          </button>
          <button
            onClick={onDownload}
            style={{ ...btnStyle, background: '#6366f1', border: 'none', padding: '0.5rem 1.25rem', fontWeight: 700 }}
          >
            <Download size={16} style={{ marginRight: '0.4rem' }} /> Descargar SVG
          </button>
        </div>
      )}
    </div>
  );
};
