/**
 * API Service - Certificate Verification
 * Connects to FastAPI backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Type definitions matching your backend response
export interface OCRData {
  engines_used: string[];
  best_engine: string;
  easy_confidence: number | null;
  paddle_confidence: number | null;
}

export interface ExtractedData {
  student_name: string | null;
  issuer: string | null;
  course_name: string | null;
  completion_date: string | null;
  certificate_ids: any;
  urls: any;
}

export interface VerificationData {
  is_verified: boolean;
  trusted_domain: boolean;
  confidence_score: number;
  method: string;
  message: string;
  verification_url: string | null;
}

export interface BackendResponse {
  success: boolean;
  filename: string;
  data: {
    ocr: OCRData;
    extracted_data: ExtractedData;
    verification: VerificationData;
  };
}

// Your existing frontend types (keep these for compatibility)
export interface CertificateAnalysisResponse {
  filename: string;
  final_verdict: 'VERIFIED' | 'UNVERIFIED' | 'ERROR';
  extraction: {
    candidate_name: string | null;
    issuer_name: string | null;
    issuer_org: string | null;
    issuer_url: string | null;
    certificate_id: string | null;
  };
  verification: {
    is_verified: boolean;
    trusted_domain: boolean;
    message: string;
    confidence_score?: number;
    method?: string;
    verification_url?: string | null;
  };
  forensics: {
    is_high_risk: boolean;
    status: string;
    manipulation_score: number;
  };
}

/**
 * Convert backend response to frontend format
 */
function convertToFrontendFormat(backendResponse: BackendResponse): CertificateAnalysisResponse {
  const { data, filename } = backendResponse;
  
  return {
    filename,
    final_verdict: data.verification.is_verified ? 'VERIFIED' : 'UNVERIFIED',
    extraction: {
      candidate_name: data.extracted_data.student_name,
      issuer_name: data.extracted_data.issuer,
      issuer_org: data.extracted_data.issuer,
      issuer_url: Array.isArray(data.extracted_data.urls) 
        ? data.extracted_data.urls[0] 
        : (typeof data.extracted_data.urls === 'object' && data.extracted_data.urls !== null)
          ? Object.values(data.extracted_data.urls)[0] as string
          : null,
      certificate_id: Array.isArray(data.extracted_data.certificate_ids)
        ? data.extracted_data.certificate_ids[0]
        : (typeof data.extracted_data.certificate_ids === 'object' && data.extracted_data.certificate_ids !== null)
          ? Object.values(data.extracted_data.certificate_ids)[0] as string
          : null,
    },
    verification: {
      is_verified: data.verification.is_verified,
      trusted_domain: data.verification.trusted_domain,
      message: data.verification.message,
      confidence_score: data.verification.confidence_score,
      method: data.verification.method,
      verification_url: data.verification.verification_url,
    },
    forensics: {
      is_high_risk: !data.verification.is_verified,
      status: data.verification.is_verified ? 'No Issues Detected' : 'Verification Failed',
      manipulation_score: data.verification.is_verified ? 0 : 0.5,
    },
  };
}

/**
 * Upload certificate for verification
 */
async function uploadCertificate(file: File): Promise<CertificateAnalysisResponse> {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/verify`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Verification failed');
    }

    const backendResponse: BackendResponse = await response.json();
    
    // Convert to frontend format
    return convertToFrontendFormat(backendResponse);
    
  } catch (error) {
    console.error('Upload error:', error);
    throw error;
  }
}

/**
 * Manual verification (not implemented in backend yet)
 * For now, return a mock response
 */
async function manualVerify(data: { certificate_id: string; issuer_url: string }): Promise<CertificateAnalysisResponse> {
  // TODO: Implement manual verification endpoint in backend
  console.warn('Manual verification not yet implemented in backend');
  
  return {
    filename: 'manual-verification',
    final_verdict: 'UNVERIFIED',
    extraction: {
      candidate_name: null,
      issuer_name: null,
      issuer_org: null,
      issuer_url: data.issuer_url,
      certificate_id: data.certificate_id,
    },
    verification: {
      is_verified: false,
      trusted_domain: false,
      message: 'Manual verification is not yet implemented',
    },
    forensics: {
      is_high_risk: false,
      status: 'Pending',
      manipulation_score: 0,
    },
  };
}

/**
 * Health check
 */
async function checkHealth(): Promise<{ status: string }> {
  const response = await fetch(`${API_BASE_URL}/health`);
  return await response.json();
}

export const verificationService = {
  uploadCertificate,
  manualVerify,
  checkHealth,
};
