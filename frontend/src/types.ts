export interface EntropyRequest {
  systemA: number[];
  systemB: number[];
}

export interface SystemMetrics {
  probabilities: number[];
  entropy: number;
  maxEntropy: number;
  redundancy: number;
  perplexity: number;
  statesCount: number;
}

export interface JointSystemMetrics {
  entropy: number;
  maxEntropy: number;
  redundancy: number;
  perplexity: number;
  statesCount: number;
}

export interface EntropyResponse {
  systemA: SystemMetrics;
  systemB: SystemMetrics;
  jointSystem: JointSystemMetrics;
  jointMatrix: number[][];
  explanation: string;
}

export interface ExampleCase {
  id: string;
  title: string;
  description: string;
  systemA: number[];
  systemB: number[];
  expected: EntropyResponse;
}

export interface ApiErrorResponse {
  detail?: string | Array<{ msg?: string; loc?: string[]; type?: string }>;
}