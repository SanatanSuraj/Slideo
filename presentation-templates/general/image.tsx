import React from 'react';
import { z } from 'zod';

const ImageLayoutSchema = z.object({
  title: z.string().describe('Slide title'),
  imageUrl: z.string().describe('URL of the image to display'),
  caption: z.string().optional().describe('Image caption'),
  content: z.string().optional().describe('Additional content text')
});

const ImageLayout: React.FC<{ data: any }> = ({ data }) => {
  const { title, imageUrl, caption, content } = data;

  return (
    <div className="w-full h-full flex flex-col p-8 bg-white">
      <h2 className="text-4xl font-bold text-gray-900 mb-6">
        {title}
      </h2>
      
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <img 
            src={imageUrl} 
            alt={caption || title}
            className="max-w-full max-h-96 object-contain rounded-lg shadow-lg mb-4"
          />
          {caption && (
            <p className="text-lg text-gray-600 italic">
              {caption}
            </p>
          )}
          {content && (
            <p className="text-lg text-gray-700 mt-4">
              {content}
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export const Schema = ImageLayoutSchema;
export const layoutId = 'image';
export default ImageLayout;
