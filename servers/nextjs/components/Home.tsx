"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to upload page since this is now the marketing homepage
    router.push("/upload");
  }, [router]);

  return null;
}
