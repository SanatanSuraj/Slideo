import React from 'react';
import { z } from 'zod';

const ContentLayoutSchema = z.object({
  title: z.string().describe('Slide title'),
  content: z.string().describe('Main content text'),
  bulletPoints: z.array(z.string()).optional().describe('List of bullet points')
});

const ContentLayout: React.FC<{ data: any }> = ({ data }) => {
  const { title, content, bulletPoints } = data;

  return (
    <div className="w-full h-full flex flex-col p-8 bg-white">
      <h2 className="text-4xl font-bold text-gray-900 mb-6">
        {title}
      </h2>
      
      <div className="flex-1 flex flex-col justify-center">
        <p className="text-xl text-gray-700 mb-6 leading-relaxed">
          {content}
        </p>
        
        {bulletPoints && bulletPoints.length > 0 && (
          <ul className="space-y-3">
            {bulletPoints.map((point: string, index: number) => (
              <li key={index} className="flex items-start">
                <span className="text-blue-500 mr-3 mt-1">•</span>
                <span className="text-lg text-gray-700">{point}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export const Schema = ContentLayoutSchema;
export const layoutId = 'content';
export default ContentLayout;
