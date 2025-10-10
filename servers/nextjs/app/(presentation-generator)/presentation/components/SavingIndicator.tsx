'use client'
import React from 'react';
import { CheckCircle, Loader2 } from 'lucide-react';

interface SavingIndicatorProps {
  isSaving: boolean;
  isSaved: boolean;
  className?: string;
}

export const SavingIndicator: React.FC<SavingIndicatorProps> = ({
  isSaving,
  isSaved,
  className = ""
}) => {
  if (!isSaving && !isSaved) {
    return null;
  }

  return (
    <div className={`fixed top-4 left-1/2 transform -translate-x-1/2 z-50 ${className}`}>
      <div className="bg-white border border-gray-200 rounded-lg shadow-lg px-4 py-2 flex items-center gap-2 text-sm">
        {isSaving ? (
          <>
            <Loader2 className="h-4 w-4 animate-spin text-blue-500" />
            <span className="text-gray-700">Saving to Cloud...</span>
          </>
        ) : isSaved ? (
          <>
            <CheckCircle className="h-4 w-4 text-green-500" />
            <span className="text-gray-700">✅ Saved to Cloud</span>
          </>
        ) : null}
      </div>
    </div>
  );
};
