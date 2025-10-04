import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function GET() {
  // Check for any available API key from environment variables
  const openaiKey = process.env.OPENAI_API_KEY || "";
  const googleKey = process.env.GOOGLE_API_KEY || "";
  const anthropicKey = process.env.ANTHROPIC_API_KEY || "";
  
  const hasKey = Boolean(
    openaiKey.trim() || 
    googleKey.trim() || 
    anthropicKey.trim()
  );

  return NextResponse.json({ 
    hasKey,
    providers: {
      openai: Boolean(openaiKey.trim()),
      google: Boolean(googleKey.trim()),
      anthropic: Boolean(anthropicKey.trim())
    }
  });
} 