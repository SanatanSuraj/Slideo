import React from "react";

export type RemoteSvgOptions = {
  strokeColor?: string;
  fillColor?: string;
  className?: string;
  title?: string;
  color?: string;
 
};

function transformSvg(svgText: string, options: RemoteSvgOptions): string {
  try {
    const parser = new DOMParser();
    const doc = parser.parseFromString(svgText, "image/svg+xml");
    const svgEl = doc.querySelector("svg");
    if (!svgEl) return svgText;
    svgEl.style.outline = "none";
    svgEl.style.border = "none";
    svgEl.style.margin = "0";
    svgEl.style.padding = "0";
    svgEl.style.display = "inline-block";
    svgEl.style.verticalAlign = "middle";
    svgEl.style.overflow = "visible";
    svgEl.style.position = "relative";
    // Set only provided attributes to avoid clobbering inner shapes
    if (options.className) svgEl.setAttribute("class", options.className);
    if (options.strokeColor) svgEl.setAttribute("stroke", options.strokeColor);
    if (options.fillColor !== undefined) svgEl.setAttribute("fill", options.fillColor);

  
      const viewBox = svgEl.getAttribute("viewBox");
      let vbX = 0, vbY = 0, vbW = 0, vbH = 0;
      if (viewBox) {
        const parts = viewBox.split(/\s+/).map((n) => Number(n));
        if (parts.length === 4 && parts.every((n) => !Number.isNaN(n))) {
          vbX = parts[0];
          vbY = parts[1];
          vbW = parts[2];
          vbH = parts[3];
        }
      }
      // Only consider direct child rects; safer heuristic
      const rects = Array.from(svgEl.querySelectorAll("rect")).filter((r) => r.parentNode === svgEl);
      rects.forEach((r) => {
        const xAttr = r.getAttribute("x") || "0";
        const yAttr = r.getAttribute("y") || "0";
        const wAttr = r.getAttribute("width") || "";
        const hAttr = r.getAttribute("height") || "";
        const fill = r.getAttribute("fill");

        const x = Number(xAttr);
        const y = Number(yAttr);
        const w = Number(wAttr);
        const h = Number(hAttr);

        const isExactHundredPercent = wAttr === "100%" && hAttr === "100%" && (xAttr === "0" || xAttr === "0%") && (yAttr === "0" || yAttr === "0%");
        const approximatelyCoversViewBox = (
          vbW > 0 && vbH > 0 &&
          !Number.isNaN(w) && !Number.isNaN(h) &&
          Math.abs(w - vbW) <= Math.max(1, vbW * 0.02) &&
          Math.abs(h - vbH) <= Math.max(1, vbH * 0.02) &&
          Math.abs(x - vbX) <= Math.max(1, vbW * 0.02) &&
          Math.abs(y - vbY) <= Math.max(1, vbH * 0.02)
        );
        const noFill = (fill === null || fill === "none" || fill === "transparent");

        const looksLikeFrame = noFill && (isExactHundredPercent || approximatelyCoversViewBox);
        if (looksLikeFrame) {
          r.parentElement?.removeChild(r);
        }
      });
    

    return svgEl.outerHTML;
  } catch {
    return svgText;
  }
}

// Simple in-memory LRU cache for transformed SVG markup
const SVG_CACHE_LIMIT = 15;
const svgCache: Map<string, string> = new Map();

function makeCacheKey(url: string, options: RemoteSvgOptions): string {
  return [
    url,
    `sc=${options.strokeColor || ""}`,
    `fc=${options.fillColor || ""}`,
    `cls=${options.className || ""}`,
    
  ].join("|");
}

function cacheGet(key: string): string | undefined {
  const value = svgCache.get(key);
  if (value !== undefined) {
    // refresh LRU order
    svgCache.delete(key);
    svgCache.set(key, value);
  }
  return value;
}

function cacheSet(key: string, value: string) {
  if (svgCache.has(key)) svgCache.delete(key);
  svgCache.set(key, value);
  if (svgCache.size > SVG_CACHE_LIMIT) {
    const oldestKey = svgCache.keys().next().value as string | undefined;
    if (oldestKey !== undefined) svgCache.delete(oldestKey);
  }
}

export function useRemoteSvgIcon(url?: string, options: RemoteSvgOptions = {}) {
  const [svgMarkup, setSvgMarkup] = React.useState<string | null>(null);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    let cancelled = false;
    async function run() {
      if (!url) {
        // build simple fallback svg
        const stroke = options.strokeColor || "currentColor";
        const fill = options.fillColor ?? "none";
        const cls = options.className ? ` class=\"${options.className}\"` : "";
        setSvgMarkup(`<svg${cls} xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' stroke='${stroke}' fill='${fill}' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><circle cx='12' cy='12' r='10' fill='currentColor' opacity='0.12'></circle><path d='M8 12l3 3 5-6' fill='none'></path></svg>`);
        return;
      }
      // non-svg extensions fallback
      if (/\.(png|jpe?g|gif|webp)(\?.*)?$/i.test(url)) {
        const stroke = options.strokeColor || "currentColor";
        const fill = options.fillColor ?? "none";
        const cls = options.className ? ` class=\"${options.className}\"` : "";
        setSvgMarkup(`<svg${cls} xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' stroke='${stroke}' fill='${fill}' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><circle cx='12' cy='12' r='10' fill='currentColor' opacity='0.12'></circle><path d='M8 12l3 3 5-6' fill='none'></path></svg>`);
        return;
      }

      // Cache lookup
      const cacheKey = makeCacheKey(url, options);
      const cached = cacheGet(cacheKey);
      if (cached) {
        setSvgMarkup(cached);
        setError(null);
        return;
      }
      try {
        // Check if URL is a placeholder that should be avoided
        if (url.includes('example.com') || url.includes('placeholder')) {
          throw new Error('Placeholder URL detected - using fallback icon');
        }
        
        const res = await fetch(url);
        if (!res.ok) {
          throw new Error(`HTTP ${res.status}`);
        }
        const ct = res.headers.get("content-type") || "";
        if (ct && !ct.includes("svg")) {
          throw new Error(`Non-SVG content: ${ct}`);
        }
        const text = await res.text();
        if (cancelled) return;
        const transformed = transformSvg(text, options);
        cacheSet(cacheKey, transformed);
        setSvgMarkup(transformed);
        setError(null);
      } catch (e: any) {
        if (cancelled) return;
        
        // Enhanced error handling with CORS detection
        const isCorsError = e?.message?.includes('CORS') || 
                           e?.message?.includes('blocked') || 
                           e?.message?.includes('Access-Control-Allow-Origin') ||
                           e?.name === 'TypeError' && e?.message?.includes('Failed to fetch');
        
        const isPlaceholderError = e?.message?.includes('Placeholder URL detected');
        
        setError(e?.message || "Failed to load SVG");
        
        // Create appropriate fallback icon based on error type
        const stroke = options.strokeColor || "currentColor";
        const fill = options.fillColor ?? "none";
        const cls = options.className ? ` class=\"${options.className}\"` : "";
        
        let fallbackIcon;
        if (isCorsError || isPlaceholderError) {
          // Use a warning icon for CORS/placeholder errors
          fallbackIcon = `<svg${cls} xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' stroke='${stroke}' fill='${fill}' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><circle cx='12' cy='12' r='10' fill='currentColor' opacity='0.12'></circle><path d='M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z' fill='none'></path></svg>`;
        } else {
          // Use default checkmark icon for other errors
          fallbackIcon = `<svg${cls} xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' stroke='${stroke}' fill='${fill}' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><circle cx='12' cy='12' r='10' fill='currentColor' opacity='0.12'></circle><path d='M8 12l3 3 5-6' fill='none'></path></svg>`;
        }
        
        setSvgMarkup(fallbackIcon);
        
        if (process.env.NODE_ENV !== "production") {
          // Enhanced logging with error type detection
          if (isCorsError) {
            console.warn("RemoteSvgIcon CORS error - using fallback icon:", url, e);
          } else if (isPlaceholderError) {
            console.warn("RemoteSvgIcon placeholder URL detected - using fallback icon:", url);
          } else {
            console.warn("RemoteSvgIcon fetch error:", url, e);
          }
        }
      }
    }
    run();
    return () => {
      cancelled = true;
    };
  }, [url, options.strokeColor, options.fillColor, options.className]);

  return { svgMarkup, error };
}

export const RemoteSvgIcon: React.FC<{
  url?: string;
  strokeColor?: string;
  fillColor?: string;
  className?: string;
  title?: string;
  color?: string;
}> = ({ url, strokeColor, fillColor, className, title, color }) => {
  const { svgMarkup } = useRemoteSvgIcon(url, { strokeColor, fillColor, className, title, color });
  if (!svgMarkup) return null;
  return (
    <span
      data-path={url}
      role={title ? "img" : undefined}
      aria-label={title}
      dangerouslySetInnerHTML={{ __html: svgMarkup }}
      style={{ display: "inline-block", color: color }}
    />
  );
};