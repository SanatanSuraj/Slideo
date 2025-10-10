"use client";

import React, { useState, useEffect } from "react";

import Wrapper from "@/components/Wrapper";
import { DashboardApi } from "@/app/(presentation-generator)/services/api/dashboard";
import { PresentationGrid } from "@/app/(presentation-generator)/dashboard/components/PresentationGrid";


import Header from "@/app/(presentation-generator)/dashboard/components/Header";

const DashboardPage: React.FC = () => {
  const [presentations, setPresentations] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadData = async () => {
      await fetchPresentations();
    };
    loadData();
  }, []);

  const fetchPresentations = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await DashboardApi.getPresentations();
      data.sort(
        (a: any, b: any) =>
          new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
      );
      setPresentations(data);
    } catch (err) {
      setError(null);
      setPresentations([]);
    } finally {
      setIsLoading(false);
    }
  };

  const removePresentation = (presentationId: string) => {
    setPresentations((prev: any) =>
      prev ? prev.filter((p: any) => p.id !== presentationId) : []
    );
  };

  const refreshPresentations = async () => {
    console.log('🔄 Manually refreshing presentations...');
    await fetchPresentations();
  };

  return (
    <div className="min-h-screen bg-[#E9E8F8]">
      <Header />
      <Wrapper>
        <main className="container mx-auto px-4 py-8">
          <section>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-roboto font-medium">
                Slide Presentation
              </h2>
              <button
                onClick={refreshPresentations}
                disabled={isLoading}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? 'Loading...' : 'Refresh'}
              </button>
            </div>
            <PresentationGrid
              presentations={presentations}
              type="slide"
              isLoading={isLoading}
              error={error}
              onPresentationDeleted={removePresentation}
            />
          </section>
        </main>
      </Wrapper>
    </div>
  );
};

export default DashboardPage;
