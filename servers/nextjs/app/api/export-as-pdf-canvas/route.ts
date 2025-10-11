import path from "path";
import fs from "fs";
import puppeteer from "puppeteer";

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
    page.setDefaultNavigationTimeout(120000); // Reduced to 2 minutes
    page.setDefaultTimeout(120000); // Reduced to 2 minutes

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

    // Inject html2canvas into the page
    console.log(`🔧 PDF Canvas Export: Injecting html2canvas into page...`);
    await page.addScriptTag({
      url: 'https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js'
    });

    // Wait for html2canvas to load
    await page.waitForFunction(() => typeof window.html2canvas !== 'undefined', { timeout: 10000 });

    // Use html2canvas to capture each slide individually with progress tracking
    console.log(`🔧 PDF Canvas Export: Capturing slides with html2canvas...`);
    
    const slideImages = await page.evaluate(async () => {
      const slides = Array.from(document.querySelectorAll('[data-speaker-note]'));
      const slideImages = [];
      
      for (let i = 0; i < slides.length; i++) {
        const slide = slides[i];
        console.log(`🔧 PDF Canvas Export: Capturing slide ${i + 1}/${slides.length}`);
        
        // Scroll the slide into view
        slide.scrollIntoView({ behavior: 'smooth', block: 'center' });
        await new Promise(resolve => setTimeout(resolve, 300)); // Reduced wait time
        
        try {
          // Capture the slide using html2canvas with optimized settings
          const canvas = await window.html2canvas(slide as HTMLElement, {
            backgroundColor: '#ffffff',
            scale: 1, // Reduced scale for better performance
            useCORS: true,
            allowTaint: true,
            logging: false,
            width: 1280,
            height: 720,
            scrollX: 0,
            scrollY: 0,
            removeContainer: true, // Clean up after capture
            timeout: 10000, // 10 second timeout per slide
          });
          
          slideImages.push(canvas.toDataURL('image/png', 0.8)); // Reduced quality for smaller size
          console.log(`🔧 PDF Canvas Export: Slide ${i + 1} captured successfully`);
        } catch (error) {
          console.error(`🔧 PDF Canvas Export: Failed to capture slide ${i + 1}:`, error);
          // Continue with other slides even if one fails
        }
      }
      
      return slideImages;
    });

    console.log(`🔧 PDF Canvas Export: Captured ${slideImages.length} slides`);

    // Inject jsPDF into the page
    console.log(`🔧 PDF Canvas Export: Injecting jsPDF into page...`);
    await page.addScriptTag({
      url: 'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js'
    });

    // Wait for jsPDF to load
    await page.waitForFunction(() => typeof window.jspdf !== 'undefined', { timeout: 10000 });

    // Create a PDF from the captured images with timeout
    console.log(`🔧 PDF Canvas Export: Starting PDF generation...`);
    const pdfArrayBuffer = await Promise.race([
      page.evaluate(async (images) => {
        console.log(`🔧 PDF Canvas Export: Creating PDF with ${images.length} images`);
        const { jsPDF } = window.jspdf;
        
        const pdf = new jsPDF({
          orientation: 'landscape',
          unit: 'in',
          format: 'a4'
        });
        
        for (let i = 0; i < images.length; i++) {
          console.log(`🔧 PDF Canvas Export: Adding slide ${i + 1}/${images.length}`);
          if (i > 0) {
            pdf.addPage();
          }
          // A4 landscape dimensions: 11.69 x 8.27 inches
          pdf.addImage(images[i], 'PNG', 0, 0, 11.69, 8.27);
        }
        
        console.log(`🔧 PDF Canvas Export: Converting PDF to arraybuffer...`);
        // Get arraybuffer and convert to regular array for serialization
        const arrayBuffer = pdf.output('arraybuffer');
        console.log(`🔧 PDF Canvas Export: PDF conversion complete, size: ${arrayBuffer.byteLength} bytes`);
        return Array.from(new Uint8Array(arrayBuffer));
      }, slideImages),
      new Promise((_, reject) => 
        setTimeout(() => reject(new Error('PDF generation timeout after 60 seconds')), 60000)
      )
    ]);

    browser.close();

    // Convert array back to buffer
    const pdfBufferData = Buffer.from(pdfArrayBuffer);
    
    console.log(`🔧 PDF Canvas Export: PDF buffer size: ${pdfBufferData.length} bytes`);
    console.log(`🔧 PDF Canvas Export: PDF buffer starts with: ${pdfBufferData.slice(0, 10).toString('hex')}`);

    const sanitizedTitle = sanitizeFilename(title ?? "presentation");
    const projectRoot = path.resolve(process.cwd(), "../../");
    const appDataDir = path.join(projectRoot, "app_data");
    const destinationPath = path.resolve(
      appDataDir,
      "exports",
      `${sanitizedTitle}-canvas.pdf`
    );
    await fs.promises.mkdir(path.dirname(destinationPath), { recursive: true });
    await fs.promises.writeFile(destinationPath, pdfBufferData);
    
    console.log(`🔧 PDF Canvas Export: PDF written to: ${destinationPath}`);

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
