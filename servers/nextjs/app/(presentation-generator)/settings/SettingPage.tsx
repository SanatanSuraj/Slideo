"use client";
import React, { useEffect } from "react";
import { useRouter } from "next/navigation";
import { RootState } from "@/store/store";
import { useSelector } from "react-redux";
import Header from "../dashboard/components/Header";

const SettingsPage = () => {
  const router = useRouter();
  const userConfigState = useSelector((state: RootState) => state.userConfig);
  const canChangeKeys = userConfigState.can_change_keys;

  useEffect(() => {
    if (!canChangeKeys) {
      router.push("/dashboard");
    }
  }, [canChangeKeys, router]);

  return (
    <div className="h-screen bg-gradient-to-b font-instrument_sans from-gray-50 to-white flex flex-col overflow-hidden">
      <Header />
      <main className="flex-1 container mx-auto px-4 max-w-3xl overflow-hidden flex flex-col">
        {/* Environment Configuration Notice */}
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center space-y-6 max-w-2xl">
            <div className="space-y-4">
              <h1 className="text-3xl font-bold text-gray-900">
                Configuration via Environment Variables
              </h1>
              <p className="text-lg text-gray-600">
                API keys are configured through environment variables in your <code className="bg-gray-100 px-2 py-1 rounded">.env</code> file.
              </p>
            </div>
            
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-left">
              <h2 className="text-lg font-semibold text-blue-900 mb-4">Required Environment Variables</h2>
              <div className="space-y-3 text-sm">
                <div className="flex items-center gap-2">
                  <span className="font-mono bg-white px-2 py-1 rounded border">OPENAI_API_KEY</span>
                  <span className="text-gray-600">- Your OpenAI API key</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="font-mono bg-white px-2 py-1 rounded border">GOOGLE_API_KEY</span>
                  <span className="text-gray-600">- Your Google Gemini API key</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="font-mono bg-white px-2 py-1 rounded border">ANTHROPIC_API_KEY</span>
                  <span className="text-gray-600">- Your Anthropic Claude API key (optional)</span>
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

            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-yellow-900 mb-2">Current Configuration Status</h3>
              <div className="text-sm text-yellow-800 space-y-2">
                <p>✅ Configuration loaded from environment variables</p>
                <p>🔒 API keys are secure and not stored in the browser</p>
                <p>🚀 Ready to generate presentations</p>
              </div>
            </div>

            <div className="pt-4">
              <button
                onClick={() => router.push("/dashboard")}
                className="w-full font-semibold py-3 px-4 rounded-lg transition-all duration-500 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 focus:ring-4 focus:ring-blue-200 text-white"
              >
                Back to Dashboard
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default SettingsPage;