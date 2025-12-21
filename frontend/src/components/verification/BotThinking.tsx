'use client';

import React from 'react';
import { Brain, Upload, Shield, Search, CheckCircle2 } from 'lucide-react';

interface BotThinkingProps {
  stage: 'uploading' | 'extracting' | 'verifying' | 'analyzing' | 'complete';
  message?: string;
}

const stageConfig = {
  uploading: {
    icon: Upload,
    text: 'Uploading your certificate...',
    subtext: 'Securely transmitting your file to our servers...',
    color: 'text-blue-600',
    bgColor: 'bg-blue-50',
    progress: 15,
  },
  extracting: {
    icon: Search,
    text: 'Extracting certificate data...',
    subtext: 'Using advanced OCR to read certificate details...',
    color: 'text-purple-600',
    bgColor: 'bg-purple-50',
    progress: 40,
  },
  verifying: {
    icon: Shield,
    text: 'Verifying with issuer...',
    subtext: 'Cross-checking with issuer database...',
    color: 'text-orange-600',
    bgColor: 'bg-orange-50',
    progress: 70,
  },
  analyzing: {
    icon: Brain,
    text: 'Analyzing authenticity...',
    subtext: 'Running forensic analysis and final checks...',
    color: 'text-indigo-600',
    bgColor: 'bg-indigo-50',
    progress: 90,
  },
  complete: {
    icon: CheckCircle2,
    text: 'Verification complete!',
    subtext: 'Preparing your results...',
    color: 'text-green-600',
    bgColor: 'bg-green-50',
    progress: 100,
  },
};

export default function BotThinking({ stage, message }: BotThinkingProps) {
  const config = stageConfig[stage];
  const Icon = config.icon;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full mx-4">
        {/* Animated Icon */}
        <div className={`${config.bgColor} rounded-full w-20 h-20 mx-auto flex items-center justify-center mb-6`}>
          <Icon 
            className={`w-10 h-10 ${config.color} ${stage !== 'complete' ? 'animate-pulse' : ''}`} 
          />
        </div>

        {/* Main Text */}
        <h3 className="text-xl font-semibold text-gray-800 text-center mb-2">
          {message || config.text}
        </h3>

        {/* Thinking Animation - 3 Dots */}
        {stage !== 'complete' && (
          <div className="flex justify-center items-center space-x-2 mt-4">
            <div className="w-3 h-3 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0s' }}></div>
            <div className="w-3 h-3 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
            <div className="w-3 h-3 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
          </div>
        )}

        {/* Progress Bar with Percentage */}
        <div className="mt-6">
          <div className="flex justify-between items-center mb-2">
            <span className="text-xs font-medium text-gray-600">Progress</span>
            <span className="text-xs font-bold text-gray-700">{config.progress}%</span>
          </div>
          {stage !== 'complete' ? (
            <div className="bg-gray-200 rounded-full h-2 overflow-hidden">
              <div 
                className={`h-full ${config.color.replace('text-', 'bg-')} transition-all duration-500 ease-out`}
                style={{
                  width: `${config.progress}%`,
                }}
              ></div>
            </div>
          ) : (
            <div className="bg-green-200 rounded-full h-2 overflow-hidden">
              <div 
                className="h-full bg-green-600 w-full transition-all duration-300"
              ></div>
            </div>
          )}
        </div>

        {/* Sub-text */}
        <p className="text-sm text-gray-500 text-center mt-4">
          {config.subtext}
        </p>
      </div>
    </div>
  );
}