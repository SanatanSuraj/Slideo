import React from 'react';
import { z } from 'zod';

const ModernTitleLayoutSchema = z.object({
  title: z.string().describe('Main title of the slide'),
  subtitle: z.string().optional().describe('Subtitle or tagline'),
  accent: z.string().optional().describe('Accent color')
});

const ModernTitleLayout: React.FC<{ data: any }> = ({ data }) => {
  const { title, subtitle, accent } = data;

  return (
    <div className="w-full h-full flex flex-col items-center justify-center p-8 bg-gradient-to-br from-gray-900 to-gray-700 text-white">
      <div className="text-center">
        <div 
          className="w-24 h-1 bg-blue-500 mx-auto mb-8"
          style={{ backgroundColor: accent || '#3b82f6' }}
        ></div>
        <h1 className="text-7xl font-light text-white mb-6 tracking-tight">
          {title}
        </h1>
        {subtitle && (
          <p className="text-2xl text-gray-300 font-light">
            {subtitle}
          </p>
        )}
      </div>
    </div>
  );
};

export const Schema = ModernTitleLayoutSchema;
export const layoutId = 'title';
export default ModernTitleLayout;
