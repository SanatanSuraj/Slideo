import path from "path";
import fs from "fs";
import puppeteer from "puppeteer";
import html2canvas from "html2canvas";

import { sanitizeFilename } from "@/app/(presentation-generator)/utils/others";
import { NextResponse, NextRequest } from "next/server";

export async function POST(req: NextRequest) {
  try {
    const { id, title, token } = await req.json();
    if (!id) {
      return NextResponse.json(
        { error: "Missing Presentation ID" },
        { status: 400 }
      );
    }

    console.log(`🔧 PDF Canvas Export: Starting export for presentation ${id}`);
    console.log(`🔧 PDF Canvas Export: Token provided: ${token ? 'Yes' : 'No'}`);

    const browser = await puppeteer.launch({
      executablePath: process.env.PUPPETEER_EXECUTABLE_PATH,
      headless: true,
      args: [
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--disable-web-security",
        "--disable-background-timer-throttling",
        "--disable-backgrounding-occluded-windows",
        "--disable-renderer-backgrounding",
        "--disable-features=TranslateUI",
        "--disable-ipc-flooding-protection",
      ],
    });
    
    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 720 });
    page.setDefaultNavigationTimeout(300000);
    page.setDefaultTimeout(300000);

    // If token is provided, set it in localStorage before navigating
    if (token) {
      console.log(`🔧 PDF Canvas Export: Setting authentication token in browser context`);
      await page.evaluateOnNewDocument((authToken) => {
        localStorage.setItem('authToken', authToken);
        console.log('🔧 PDF Canvas Export: Token set in localStorage');
      }, token);
    }

    // Navigate to the PDF maker page with token as URL parameter
    const pdfMakerUrl = token 
      ? `http://localhost:3000/pdf-maker?id=${id}&token=${encodeURIComponent(token)}`
      : `http://localhost:3000/pdf-maker?id=${id}`;
    console.log(`🔧 PDF Canvas Export: Navigating to ${pdfMakerUrl}`);
    
    await page.goto(pdfMakerUrl, {
      waitUntil: "networkidle0",
      timeout: 300000,
    });

    await page.waitForFunction('() => document.readyState === "complete"');

    // Wait for the presentation to load
    try {
      await page.waitForFunction(
        `
        () => {
          const slides = document.querySelectorAll('[data-speaker-note]');
          if (slides.length > 0) {
            const slideContent = document.querySelectorAll('[data-speaker-note] > div');
            if (slideContent.length > 0) {
              const hasRealContent = Array.from(slideContent).some(slide => {
                const text = slide.textContent || '';
                const hasText = text.trim().length > 0;
                const isNotSkeleton = !slide.classList.contains('bg-gray-400') && 
                                     !slide.querySelector('.bg-gray-400');
                return hasText && isNotSkeleton;
              });
              if (hasRealContent) {
                return true;
              }
            }
          }
          
          const errorElement = document.querySelector('.bg-red-500, .text-red-500, [role="alert"]');
          if (errorElement) {
            return 'error';
          }
          
          const skeletons = document.querySelectorAll('.bg-gray-400');
          if (skeletons.length > 0) {
            return false;
          }
          
          return false;
        }
        `,
        { timeout: 300000 }
      );
    } catch (error) {
      console.log("Warning: Content loading timeout, proceeding with PDF generation:", error);
    }

    // Wait for all images to load
    console.log(`🔧 PDF Canvas Export: Waiting for images to load...`);
    await page.evaluate(async () => {
      const images = Array.from(document.querySelectorAll('img'));
      const imagePromises = images.map(img => {
        if (img.complete) return Promise.resolve();
        return new Promise((resolve, reject) => {
          img.onload = resolve;
          img.onerror = resolve;
          setTimeout(resolve, 10000);
        });
      });
      await Promise.all(imagePromises);
    });

    // Additional wait for any dynamic content to render
    await new Promise((resolve) => setTimeout(resolve, 3000));

    // Check if we're in an error state
    const isErrorState = await page.evaluate(() => {
      const errorElement = document.querySelector('.bg-red-500, .text-red-500, [role="alert"]');
      return errorElement !== null;
    });

    if (isErrorState) {
      console.log("❌ PDF Canvas Export: Error state detected, generating error PDF");
      browser.close();
      return NextResponse.json(
        { error: "Failed to load presentation for PDF export" },
        { status: 500 }
      );
    }

    // Use html2canvas to capture each slide individually
    console.log(`🔧 PDF Canvas Export: Capturing slides with html2canvas...`);
    
    const slideImages = await page.evaluate(async () => {
      const slides = Array.from(document.querySelectorAll('[data-speaker-note]'));
      const slideImages = [];
      
      for (let i = 0; i < slides.length; i++) {
        const slide = slides[i];
        
        // Scroll the slide into view
        slide.scrollIntoView({ behavior: 'smooth', block: 'center' });
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Capture the slide using html2canvas
        const canvas = await html2canvas(slide as HTMLElement, {
          backgroundColor: '#ffffff',
          scale: 2, // Higher resolution
          useCORS: true,
          allowTaint: true,
          logging: false,
          width: 1280,
          height: 720,
          scrollX: 0,
          scrollY: 0,
        });
        
        slideImages.push(canvas.toDataURL('image/png'));
      }
      
      return slideImages;
    });

    console.log(`🔧 PDF Canvas Export: Captured ${slideImages.length} slides`);

    // Create a PDF from the captured images
    const pdfBuffer = await page.evaluate(async (images) => {
      // Import jsPDF dynamically
      const { jsPDF } = await import('jspdf');
      
      const pdf = new jsPDF({
        orientation: 'landscape',
        unit: 'px',
        format: [1280, 720]
      });
      
      images.forEach((imageData, index) => {
        if (index > 0) {
          pdf.addPage();
        }
        pdf.addImage(imageData, 'PNG', 0, 0, 1280, 720);
      });
      
      return pdf.output('arraybuffer');
    }, slideImages);

    browser.close();

    const sanitizedTitle = sanitizeFilename(title ?? "presentation");
    const projectRoot = path.resolve(process.cwd(), "../../");
    const appDataDir = path.join(projectRoot, "app_data");
    const destinationPath = path.resolve(
      appDataDir,
      "exports",
      `${sanitizedTitle}-canvas.pdf`
    );
    await fs.promises.mkdir(path.dirname(destinationPath), { recursive: true });
    await fs.promises.writeFile(destinationPath, Buffer.from(pdfBuffer));

    const relativePath = path.relative(path.resolve(appDataDir), destinationPath);
    const downloadUrl = `/app_data/${relativePath.replace(/\\/g, '/')}`;
    
    console.log(`✅ PDF Canvas Export: Successfully generated PDF at ${downloadUrl}`);
    return NextResponse.json({
      success: true,
      path: downloadUrl,
    });
  } catch (error: any) {
    console.error("PDF canvas export error:", error);
    return NextResponse.json(
      { error: "Failed to export PDF", details: error.message },
      { status: 500 }
    );
  }
}
