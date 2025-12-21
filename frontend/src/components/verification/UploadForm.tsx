'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { UploadCloud, File as FileIcon, XCircle } from 'lucide-react';
import { verificationService } from '@/services/api';
import BotThinking from './BotThinking';

type ThinkingStage = 'uploading' | 'extracting' | 'verifying' | 'analyzing' | 'complete' | null;

export default function UploadForm() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Bot thinking state
  const [thinkingStage, setThinkingStage] = useState<ThinkingStage>(null);

  // Handle Drag Events
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  // Handle File Input
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const validateAndSetFile = (selectedFile: File) => {
    const validTypes = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg'];
    if (!validTypes.includes(selectedFile.type)) {
      setError('Invalid file type. Please upload a PDF or Image.');
      return;
    }
    
    const maxSize = 5 * 1024 * 1024; // 5MB
    if (selectedFile.size > maxSize) {
      setError('File size exceeds 5MB. Please upload a smaller file.');
      return;
    }

    setFile(selectedFile);
    setError(null);
  };

  const handleVerification = async () => {
    if (!file) return;

    try {
      setError(null);
      
      // Stage 1: Uploading (when API call starts)
      setThinkingStage('uploading');
      
      // Small delay to show uploading state
      await new Promise(resolve => setTimeout(resolve, 800));
      
      // Stage 2: Extracting (OCR is happening on backend)
      setThinkingStage('extracting');
      
      // Make the actual API call
      const response = await verificationService.uploadCertificate(file);
      
      // Stage 3: Verifying (after we get response, show verifying)
      setThinkingStage('verifying');
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Stage 4: Analyzing (final check)
      setThinkingStage('analyzing');
      await new Promise(resolve => setTimeout(resolve, 800));
      
      // Stage 5: Complete
      setThinkingStage('complete');
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Store result and redirect
      localStorage.setItem('verificationResult', JSON.stringify(response));
      router.push('/verify-result');
      
    } catch (err: any) {
      setThinkingStage(null);
      setError(err.message || 'Verification failed. Please try again.');
      console.error('Verification error:', err);
    }
  };

  return (
    <>
      <div className="bg-white rounded-lg shadow-md p-6 w-full max-w-md">
        <h2 className="text-xl font-bold text-slate-800 mb-4">Upload Certificate</h2>
        
        {/* Drag & Drop Area */}
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`
            relative border-2 border-dashed rounded-lg p-8 transition-all cursor-pointer
            ${isDragging ? 'border-orange-500 bg-orange-50' : 'border-slate-300 hover:border-slate-400'}
            ${file ? 'bg-slate-50' : ''}
          `}
        >
          <input
            type="file"
            id="certificate-upload"
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            onChange={handleFileChange}
            accept=".pdf,.png,.jpg,.jpeg"
            disabled={thinkingStage !== null}
          />

          <div className="flex flex-col items-center justify-center space-y-3 pointer-events-none">
            {file ? (
              <>
                <FileIcon className="w-10 h-10 text-orange-600" />
                <div className="text-sm text-slate-700 font-medium truncate max-w-[200px]">
                  {file.name}
                </div>
                <p className="text-xs text-slate-500">
                  {(file.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </>
            ) : (
              <>
                <UploadCloud className="w-10 h-10 text-slate-400" />
                <div className="text-slate-600">
                  <span className="font-semibold text-orange-600">Click to upload</span> or drag and drop
                </div>
                <p className="text-xs text-slate-500">PDF, PNG, JPG (Max 5MB)</p>
              </>
            )}
          </div>
        </div>

        {error && (
          <div className="mt-4 p-3 bg-red-50 text-red-600 text-sm rounded-md flex items-center gap-2 border border-red-200">
            <XCircle className="w-4 h-4" />
            {error}
          </div>
        )}

        <button
          onClick={handleVerification}
          disabled={!file || thinkingStage !== null}
          className={`
            w-full mt-6 flex items-center justify-center py-3 px-4 rounded-lg font-semibold text-white transition-all
            ${!file || thinkingStage !== null
              ? 'bg-slate-300 cursor-not-allowed' 
              : 'bg-orange-600 hover:bg-orange-700 shadow-md hover:shadow-lg active:scale-95'
            }
          `}
        >
          Verify Certificate
        </button>
      </div>

      {/* Bot Thinking Overlay - Shows for ALL stages */}
      {thinkingStage && (
        <BotThinking stage={thinkingStage} />
      )}
    </>
  );
}