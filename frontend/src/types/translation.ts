export interface TranslationRequest {
  text: string;
  beam_size: number;
  max_new_tokens: number;
}

export interface TranslationResponse {
  source_text: string;
  translated_text: string;
  source_language: string;
  target_language: string;
  model: string;
  beam_size: number;
  input_tokens: number;
  output_tokens: number;
  latency_ms: number;
  device: string;
}