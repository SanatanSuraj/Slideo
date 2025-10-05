"use client";

import React, { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { PresentationConfig, ToneType, VerbosityType } from "../type";

interface AdvancedSettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (settings: Partial<PresentationConfig>) => void;
  initialConfig: PresentationConfig;
}

const AdvancedSettingsModal: React.FC<AdvancedSettingsModalProps> = ({
  isOpen,
  onClose,
  onSave,
  initialConfig,
}) => {
  const [settings, setSettings] = useState<Partial<PresentationConfig>>({
    tone: initialConfig.tone,
    verbosity: initialConfig.verbosity,
    includeTableOfContents: initialConfig.includeTableOfContents,
    includeTitleSlide: initialConfig.includeTitleSlide,
    webSearch: initialConfig.webSearch,
    instructions: initialConfig.instructions,
  });

  const handleSave = () => {
    onSave(settings);
    onClose();
  };

  const handleSettingChange = (key: keyof PresentationConfig, value: any) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Advanced settings</DialogTitle>
        </DialogHeader>
        
        <div className="space-y-6">
          {/* Tone */}
          <div className="space-y-2">
            <Label htmlFor="tone" className="text-sm font-medium">
              Tone
            </Label>
            <p className="text-sm text-gray-500">
              Controls the writing style (e.g., casual, professional, funny).
            </p>
            <Select
              value={settings.tone || ToneType.Default}
              onValueChange={(value) => handleSettingChange("tone", value)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value={ToneType.Default}>Default</SelectItem>
                <SelectItem value={ToneType.Casual}>Casual</SelectItem>
                <SelectItem value={ToneType.Professional}>Professional</SelectItem>
                <SelectItem value={ToneType.Funny}>Funny</SelectItem>
                <SelectItem value={ToneType.Educational}>Educational</SelectItem>
                <SelectItem value={ToneType.Sales_Pitch}>Sales Pitch</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Verbosity */}
          <div className="space-y-2">
            <Label htmlFor="verbosity" className="text-sm font-medium">
              Verbosity
            </Label>
            <p className="text-sm text-gray-500">
              Controls how detailed slide descriptions are: concise, standard, or text-heavy.
            </p>
            <Select
              value={settings.verbosity || VerbosityType.Standard}
              onValueChange={(value) => handleSettingChange("verbosity", value)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value={VerbosityType.Concise}>Concise</SelectItem>
                <SelectItem value={VerbosityType.Standard}>Standard</SelectItem>
                <SelectItem value={VerbosityType.Text_Heavy}>Text Heavy</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Image Type */}
          <div className="space-y-2">
            <Label htmlFor="imageType" className="text-sm font-medium">
              Image type
            </Label>
            <p className="text-sm text-gray-500">
              Choose whether images should be stock photos or AI-generated.
            </p>
            <Select defaultValue="stock">
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="stock">Stock</SelectItem>
                <SelectItem value="ai-generated">AI Generated</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Include Table of Contents */}
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <Label htmlFor="tableOfContents" className="text-sm font-medium">
                Include table of contents
              </Label>
              <p className="text-sm text-gray-500">
                Add an index slide summarizing sections (requires 3+ slides).
              </p>
            </div>
            <Switch
              id="tableOfContents"
              checked={settings.includeTableOfContents || false}
              onCheckedChange={(checked) => handleSettingChange("includeTableOfContents", checked)}
            />
          </div>

          {/* Title Slide */}
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <Label htmlFor="titleSlide" className="text-sm font-medium">
                Title slide
              </Label>
              <p className="text-sm text-gray-500">
                Include a title slide as the first slide.
              </p>
            </div>
            <Switch
              id="titleSlide"
              checked={settings.includeTitleSlide || false}
              onCheckedChange={(checked) => handleSettingChange("includeTitleSlide", checked)}
            />
          </div>

          {/* Web Search */}
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <Label htmlFor="webSearch" className="text-sm font-medium">
                Web search
              </Label>
              <p className="text-sm text-gray-500">
                Allow the model to consult the web for fresher facts.
              </p>
            </div>
            <Switch
              id="webSearch"
              checked={settings.webSearch || false}
              onCheckedChange={(checked) => handleSettingChange("webSearch", checked)}
            />
          </div>

          {/* Instructions */}
          <div className="space-y-2">
            <Label htmlFor="instructions" className="text-sm font-medium">
              Instructions
            </Label>
            <p className="text-sm text-gray-500">
              Optional guidance for the AI. These override defaults except format constraints.
            </p>
            <Textarea
              id="instructions"
              placeholder="Example: Focus on enterprise buyers, emphasize ROI and security compliance. Keep slides data-driven, avoid jargon, and include a short call-to-action on the final slide."
              value={settings.instructions || ""}
              onChange={(e) => handleSettingChange("instructions", e.target.value)}
              className="min-h-[100px]"
            />
          </div>

          {/* Don't show this again */}
          <div className="flex items-center justify-between">
            <Label htmlFor="dontShowAgain" className="text-sm font-medium">
              Don't show this again
            </Label>
            <Switch id="dontShowAgain" />
          </div>
        </div>

        <DialogFooter className="flex gap-2">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={handleSave} className="bg-indigo-600 hover:bg-indigo-700">
            Save
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default AdvancedSettingsModal;
