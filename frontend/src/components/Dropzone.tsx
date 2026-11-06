import React, { useCallback, useRef, useState } from 'react';
import { Upload } from 'lucide-react';

interface DropzoneProps {
  onFileSelected: (file: File) => void;
  disabled?: boolean;
}

const ACCEPTED = ['image/png', 'image/jpeg', 'image/webp', 'image/gif', 'image/bmp'].join(',');

export const Dropzone: React.FC<DropzoneProps> = ({ onFileSelected, disabled }) => {
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback(
    (file: File | undefined) => {
      if (!file || disabled) return;
      onFileSelected(file);
    },
    [onFileSelected, disabled],
  );

  const onDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      setDragging(false);
      handleFile(e.dataTransfer.files[0]);
    },
    [handleFile],
  );

  return (
    <div
      role="button"
      tabIndex={disabled ? -1 : 0}
      aria-label="Zona de carga de imagen"
      aria-disabled={disabled}
      onClick={() => !disabled && inputRef.current?.click()}
      onKeyDown={(e) => e.key === 'Enter' && !disabled && inputRef.current?.click()}
      onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={onDrop}
      style={{
        border: `2px dashed ${dragging ? '#6366f1' : '#4b5563'}`,
        borderRadius: '1rem',
        padding: '3rem 2rem',
        textAlign: 'center',
        cursor: disabled ? 'not-allowed' : 'pointer',
        transition: 'border-color 0.2s, background 0.2s',
        background: dragging ? 'rgba(99, 102, 241, 0.08)' : 'rgba(255,255,255,0.03)',
        opacity: disabled ? 0.5 : 1,
      }}
    >
      <Upload size={40} style={{ margin: '0 auto 1rem', color: '#6366f1' }} />
      <p style={{ margin: 0, fontWeight: 600, fontSize: '1.1rem' }}>
        Arrastra tu imagen aquí
      </p>
      <p style={{ margin: '0.4rem 0 0', color: '#9ca3af', fontSize: '0.9rem' }}>
        PNG, JPEG, WebP, GIF, BMP · máx. 10 MB
      </p>
      <input
        ref={inputRef}
        type="file"
        accept={ACCEPTED}
        style={{ display: 'none' }}
        onChange={(e) => handleFile(e.target.files?.[0])}
        disabled={disabled}
      />
    </div>
  );
};
