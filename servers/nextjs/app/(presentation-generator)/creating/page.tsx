import React from 'react';
import { Metadata } from 'next';
import CreatingPresentation from './components/CreatingPresentation';
import Header from '@/app/(presentation-generator)/dashboard/components/Header';

export const metadata: Metadata = {
  title: "Creating Presentation | Presenton",
  description: "We're crafting your presentation with AI magic ✨",
  alternates: {
    canonical: "https://presenton.ai/creating",
  },
};

const page = () => {
  return (
    <div className="relative min-h-screen">
      <Header />
      <CreatingPresentation />
    </div>
  );
};

export default page;
