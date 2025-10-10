import React from 'react';
import { z } from 'zod';

const TitleLayoutSchema = z.object({
  title: z.string().describe('Main title of the slide'),
  subtitle: z.string().optional().describe('Subtitle or tagline'),
  background: z.string().optional().describe('Background color or image URL')
});

const TitleLayout: React.FC<{ data: any }> = ({ data }) => {
  const { title, subtitle, background } = data;

  return (
    <div 
      className="w-full h-full flex flex-col items-center justify-center p-8"
      style={{ backgroundColor: background || '#ffffff' }}
    >
      <h1 className="text-6xl font-bold text-gray-900 text-center mb-4">
        {title}
      </h1>
      {subtitle && (
        <p className="text-2xl text-gray-600 text-center">
          {subtitle}
        </p>
      )}
    </div>
  );
};

export const Schema = TitleLayoutSchema;
export const layoutId = 'title';
export default TitleLayout;
