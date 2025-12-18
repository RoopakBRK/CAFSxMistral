/**
 * API Service for certificate verification
 */

import { HistoryResponse, StatsResponse, SearchResponse } from '@/types/history';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface CertificateAnalysisResponse {
  filename: string;
  final_verdict: string;
  extraction: {
    candidate_name: string;
    issuer: string;
    course_name?: string;
    completion_date?: string;
    certificate_id?: string;
  };
  verification: {
    is_verified: boolean;
    confidence: number;
    method: string;
    details: string;
  };
  forensics: {
    is_manipulated: boolean;
    manipulation_score: number;
    anomalies: string[];
  };
}

/**
 * Upload and verify a certificate
 */
export async function uploadCertificate(file: File): Promise<CertificateAnalysisResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/api/v1/verify`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Verification failed: ${response.statusText}`);
  }

  const data = await response.json();
  
  // Convert backend format to frontend format
  return convertToFrontendFormat(data);
}

/**
 * Convert backend response to frontend format
 */
function convertToFrontendFormat(backendData: any): CertificateAnalysisResponse {
  const extractedData = backendData.data?.extracted_data || {};
  const verification = backendData.data?.verification || {};
  const forensics = backendData.data?.forensics || {};

  return {
    filename: backendData.filename || 'unknown',
    final_verdict: backendData.data?.final_verdict || (verification.is_verified ? 'VERIFIED' : 'UNVERIFIED'),
    extraction: {
      candidate_name: extractedData.student_name || 'Unknown',
      issuer: extractedData.issuer || 'Unknown',
      course_name: extractedData.course_name,
      completion_date: extractedData.completion_date,
      certificate_id: extractedData.certificate_ids?.[0],
    },
    verification: {
      is_verified: verification.is_verified || false,
      confidence: verification.confidence_score || 0,
      method: verification.method || 'unknown',
      details: verification.message || 'No details available',
    },
    forensics: {
      is_manipulated: forensics.is_high_risk || false,
      manipulation_score: forensics.manipulation_score || 0,
      anomalies: forensics.anomalies_detected || [],
    },
  };
}

// ===== HISTORY SERVICE =====

/**
 * Get recent verification activity
 */
async function getRecentActivity(limit: number = 10): Promise<HistoryResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/history?limit=${limit}`);
  
  if (!response.ok) {
    throw new Error('Failed to fetch recent activity');
  }
  
  return response.json();
}

/**
 * Get verification statistics
 */
async function getVerificationStats(): Promise<StatsResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/history/stats`);
  
  if (!response.ok) {
    throw new Error('Failed to fetch verification stats');
  }
  
  return response.json();
}

/**
 * Search verification history
 */
async function searchHistory(query: string, limit: number = 20): Promise<SearchResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/history/search?q=${encodeURIComponent(query)}&limit=${limit}`
  );
  
  if (!response.ok) {
    throw new Error('Failed to search history');
  }
  
  return response.json();
}

export const historyService = {
  getRecentActivity,
  getVerificationStats,
  searchHistory,
};

export const verificationService = {
  uploadCertificate,
};
