/** Vectorization parameters sent to the API. */
export interface VectorizationParams {
  color_mode: 'color' | 'binary';
  filter_speckle: number;
  color_precision: number;
  layer_difference: number;
  corner_threshold: number;
  length_threshold: number;
  max_iterations: number;
  splice_threshold: number;
  path_precision: number;
}

export const DEFAULT_PARAMS: VectorizationParams = {
  color_mode: 'color',
  filter_speckle: 4,
  color_precision: 6,
  layer_difference: 16,
  corner_threshold: 60,
  length_threshold: 4.0,
  max_iterations: 10,
  splice_threshold: 45,
  path_precision: 8,
};

export type VectorizationStatus = 'idle' | 'uploading' | 'processing' | 'done' | 'error';

export interface VectorizationResult {
  svgContent: string;
  filename: string;
  fileHash: string;
}
