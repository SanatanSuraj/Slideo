"use client";
import React from 'react';
import { Button } from "@/components/ui/button";
import { Play } from "lucide-react";
import { useRouter } from "next/navigation";
import { trackEvent, MixpanelEvent } from "@/utils/mixpanel";
import { usePathname } from "next/navigation";

interface UniversalPresentButtonProps {
  presentationId: string;
  currentSlide?: number;
  variant?: "default" | "ghost" | "outline" | "secondary" | "destructive" | "link";
  size?: "default" | "sm" | "lg" | "icon";
  className?: string;
  disabled?: boolean;
  children?: React.ReactNode;
}

const UniversalPresentButton: React.FC<UniversalPresentButtonProps> = ({
  presentationId,
  currentSlide = 0,
  variant = "default",
  size = "default",
  className = "",
  disabled = false,
  children
}) => {
  const router = useRouter();
  const pathname = usePathname();

  const handlePresent = () => {
    if (!presentationId || disabled) return;
    
    const to = `/presentation?id=${presentationId}&mode=present&slide=${currentSlide}`;
    trackEvent(MixpanelEvent.Navigation, { from: pathname, to });
    router.push(to);
  };

  return (
    <Button
      onClick={handlePresent}
      disabled={disabled || !presentationId}
      variant={variant}
      size={size}
      className={`flex items-center gap-2 ${className}`}
    >
      <Play className="w-4 h-4" />
      {children || "Present"}
    </Button>
  );
};

export default UniversalPresentButton;
