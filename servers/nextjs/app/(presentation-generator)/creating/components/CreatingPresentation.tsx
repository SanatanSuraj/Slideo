"use client";

import React, { useEffect } from "react";
import { useRouter } from "next/navigation";

const CreatingPresentation: React.FC = () => {
  const router = useRouter();

  useEffect(() => {
    // Don't auto-redirect - let the user stay on the creating page
    // The presentation generation will handle the redirect when ready
    console.log('CreatingPresentation: Staying on creating page, waiting for generation to complete');
    
    // Optional: Add a manual "Cancel" button or "Go to Dashboard" button
    // instead of automatic redirect
  }, [router]);

  return (
    <div className="flex flex-col items-center justify-center h-screen text-center bg-gray-50">
      <div className="bg-white rounded-xl shadow-lg p-8 max-w-md w-full mx-4">
        <h2 className="text-xl font-semibold mb-2 text-gray-900">
          Creating Your Presentation
        </h2>
        <p className="text-gray-500 mb-4">
          We're crafting your presentation with AI magic ✨
        </p>
        <div className="w-64 h-2 bg-gray-200 rounded-full mx-auto">
          <div 
            className="h-2 bg-indigo-600 rounded-full animate-pulse" 
            style={{ width: "80%" }} 
          />
        </div>
      </div>
    </div>
  );
};

export default CreatingPresentation;
