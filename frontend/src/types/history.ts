/**
 * Types for verification history
 */

export interface HistoryRecord {
  id: number;
  timestamp: string;
  filename: string | null;
  student_name: string | null;
  issuer: string | null;
  course_name: string | null;
  certificate_id: string | null;
  is_verified: boolean;
  verification_method: string | null;
  confidence_score: number | null;
  is_high_risk: boolean;
  manipulation_score: number | null;
  verification_url: string | null;
}

export interface VerificationStats {
  total_verifications: number;
  verified_count: number;
  unverified_count: number;
  high_risk_count: number;
  success_rate: number;
  average_confidence: number;
  last_24h: number;
}

export interface HistoryResponse {
  success: boolean;
  count: number;
  verifications: HistoryRecord[];
}

export interface StatsResponse {
  success: boolean;
  stats: VerificationStats;
}

export interface SearchResponse {
  success: boolean;
  query: string;
  count: number;
  results: HistoryRecord[];
}
