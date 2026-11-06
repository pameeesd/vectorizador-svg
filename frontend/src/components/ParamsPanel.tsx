import React from 'react';
import { VectorizationParams, DEFAULT_PARAMS } from '../types/vectorization';

interface ParamsPanelProps {
  params: VectorizationParams;
  onChange: (params: VectorizationParams) => void;
  disabled?: boolean;
}

interface SliderFieldProps {
  label: string;
  hint: string;
  name: keyof VectorizationParams;
  min: number;
  max: number;
  step?: number;
  value: number;
  onChange: (name: keyof VectorizationParams, value: number) => void;
  disabled?: boolean;
}

const SliderField: React.FC<SliderFieldProps> = ({
  label, hint, name, min, max, step = 1, value, onChange, disabled,
}) => (
  <div style={{ marginBottom: '1rem' }}>
    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
      <label htmlFor={name} style={{ fontWeight: 500, fontSize: '0.85rem' }}>{label}</label>
      <span style={{ color: '#6366f1', fontWeight: 700, fontSize: '0.85rem' }}>{value}</span>
    </div>
    <input
      id={name}
      type="range"
      min={min}
      max={max}
      step={step}
      value={value}
      disabled={disabled}
      onChange={(e) => onChange(name, parseFloat(e.target.value))}
      style={{ width: '100%', accentColor: '#6366f1' }}
    />
    <p style={{ margin: '0.15rem 0 0', color: '#6b7280', fontSize: '0.75rem' }}>{hint}</p>
  </div>
);

export const ParamsPanel: React.FC<ParamsPanelProps> = ({ params, onChange, disabled }) => {
  const set = (name: keyof VectorizationParams, value: number | string) => {
    onChange({ ...params, [name]: value });
  };

  return (
    <aside style={{
      background: 'rgba(255,255,255,0.04)',
      border: '1px solid rgba(255,255,255,0.08)',
      borderRadius: '0.75rem',
      padding: '1.25rem',
    }}>
      <h2 style={{ margin: '0 0 1rem', fontSize: '1rem', fontWeight: 700 }}>Parámetros</h2>

      {/* Color mode toggle */}
      <div style={{ marginBottom: '1rem' }}>
        <label style={{ fontWeight: 500, fontSize: '0.85rem', display: 'block', marginBottom: '0.4rem' }}>
          Modo de color
        </label>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          {(['color', 'binary'] as const).map((mode) => (
            <button
              key={mode}
              disabled={disabled}
              onClick={() => set('color_mode', mode)}
              style={{
                flex: 1,
                padding: '0.4rem 0',
                borderRadius: '0.4rem',
                border: 'none',
                cursor: disabled ? 'not-allowed' : 'pointer',
                fontWeight: 600,
                fontSize: '0.85rem',
                background: params.color_mode === mode ? '#6366f1' : 'rgba(255,255,255,0.06)',
                color: params.color_mode === mode ? '#fff' : '#9ca3af',
                transition: 'background 0.15s',
              }}
            >
              {mode === 'color' ? '🎨 Color' : '◑ Binario'}
            </button>
          ))}
        </div>
      </div>

      <SliderField label="Eliminar manchas" hint="Área mínima de caminos a conservar (px²)" name="filter_speckle" min={0} max={100} value={params.filter_speckle} onChange={set} disabled={disabled} />
      {params.color_mode === 'color' && (
        <>
          <SliderField label="Precisión de color" hint="Bits significativos por canal para clustering" name="color_precision" min={1} max={8} value={params.color_precision} onChange={set} disabled={disabled} />
          <SliderField label="Diferencia de capas" hint="Diferencia mínima de luminancia entre capas" name="layer_difference" min={1} max={256} value={params.layer_difference} onChange={set} disabled={disabled} />
        </>
      )}
      <SliderField label="Umbral de esquinas" hint="Ángulo para detectar esquinas (grados)" name="corner_threshold" min={1} max={180} value={params.corner_threshold} onChange={set} disabled={disabled} />
      <SliderField label="Long. mínima de segmento" hint="Longitud mínima de segmento de trayectoria" name="length_threshold" min={0.1} max={10} step={0.1} value={params.length_threshold} onChange={set} disabled={disabled} />
      <SliderField label="Iteraciones máx." hint="Iteraciones de simplificación de trayectoria" name="max_iterations" min={1} max={50} value={params.max_iterations} onChange={set} disabled={disabled} />
      <SliderField label="Umbral de empalme" hint="Ángulo para fusionar segmentos consecutivos" name="splice_threshold" min={1} max={180} value={params.splice_threshold} onChange={set} disabled={disabled} />

      <button
        onClick={() => onChange(DEFAULT_PARAMS)}
        disabled={disabled}
        style={{
          marginTop: '0.5rem',
          width: '100%',
          padding: '0.4rem',
          borderRadius: '0.4rem',
          border: '1px solid rgba(255,255,255,0.1)',
          background: 'transparent',
          color: '#9ca3af',
          cursor: disabled ? 'not-allowed' : 'pointer',
          fontSize: '0.8rem',
        }}
      >
        Restaurar valores por defecto
      </button>
    </aside>
  );
};
