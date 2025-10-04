import React from "react";
import Header from "@/app/(presentation-generator)/dashboard/components/Header";

export const APIKeyWarning: React.FC = () => {
  return (
    <div className="min-h-screen font-roboto bg-gradient-to-br from-slate-50 to-slate-100">
      <Header />
      <div className="flex items-center justify-center aspect-video mx-auto px-6">
        <div className="text-center space-y-6 my-6 bg-white p-10 rounded-lg shadow-lg max-w-2xl">
          <div className="space-y-4">
            <h1 className="text-2xl font-bold text-gray-900">
              ❌ API Key Missing
            </h1>
            <p className="text-lg text-gray-600">
              Please add your API keys to the <code className="bg-gray-100 px-2 py-1 rounded">.env</code> file to enable AI features.
            </p>
          </div>
          
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-left">
            <h2 className="text-lg font-semibold text-blue-900 mb-4">Required Environment Variables</h2>
            <div className="space-y-3 text-sm">
              <div className="flex items-center gap-2">
                <span className="font-mono bg-white px-2 py-1 rounded border">OPENAI_API_KEY</span>
                <span className="text-gray-600">- For OpenAI GPT models</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="font-mono bg-white px-2 py-1 rounded border">GOOGLE_API_KEY</span>
                <span className="text-gray-600">- For Google Gemini models</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="font-mono bg-white px-2 py-1 rounded border">ANTHROPIC_API_KEY</span>
                <span className="text-gray-600">- For Anthropic Claude models</span>
              </div>
            </div>
          </div>

          <div className="bg-green-50 border border-green-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-green-900 mb-2">Quick Setup</h3>
            <div className="text-sm text-green-800 space-y-2">
              <p>1. Copy <code className="bg-white px-1 py-0.5 rounded">.env.example</code> to <code className="bg-white px-1 py-0.5 rounded">.env</code></p>
              <p>2. Add your API keys to the <code className="bg-white px-1 py-0.5 rounded">.env</code> file</p>
              <p>3. Restart the application</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}; 