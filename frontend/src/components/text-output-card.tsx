"use client";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useState } from "react";

interface TextOutputCardProps {
  detectedText: string;
  setDetectedText: (text: string) => void;
  currentPrediction?: string | null;
  confidence?: number;
  history?: string[];
}

export default function TextOutputCard({
  detectedText,
  setDetectedText,
  currentPrediction,
  confidence,
  history = [],
}: TextOutputCardProps) {
  const [isCopied, setIsCopied] = useState(false);

  const handleCopyToClipboard = () => {
    navigator.clipboard.writeText(detectedText);
    setIsCopied(true);
    setTimeout(() => setIsCopied(false), 2000);
  };

  const handleClearText = () => {
    setDetectedText("");
  };

  return (
    <div className="rounded-3xl bg-slate-900/60 backdrop-blur-3xl border border-white/25 shadow-2xl overflow-hidden flex flex-col h-full hover:bg-slate-900/70 transition-all duration-500">
      {/* Header */}
      <div className="px-8 py-6 border-b border-white/15 backdrop-blur-md bg-slate-800/40">
        <h2 className="text-2xl font-bold text-white drop-shadow-lg">
          <span className="bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
            Detected
          </span>{" "}
          Text
        </h2>
        <p className="text-white/70 text-sm mt-1">
          Real-time output from hand signs
        </p>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col gap-6 p-8">
        {/* Output text area */}
        <div className="flex-1 flex flex-col">
          <label className="text-sm font-semibold text-white/90 mb-3 drop-shadow-lg">
            Output
          </label>
          <Textarea
            value={detectedText}
            onChange={(e) => setDetectedText(e.target.value)}
            placeholder="Detected text will appear here..."
            className="flex-1 resize-none font-mono text-sm bg-white/8 backdrop-blur-md border border-white/25 rounded-2xl text-white placeholder-white/40 focus:bg-white/12 focus:border-white/40 focus:outline-none transition-all duration-300"
          />
        </div>

        {/* Actions */}
        <div className="flex gap-3">
          <Button
            onClick={handleCopyToClipboard}
            className="flex-1 bg-white/12 hover:bg-white/18 border border-white/30 text-white font-semibold rounded-xl backdrop-blur-md transition-all duration-300"
            disabled={!detectedText}
          >
            {isCopied ? "✓ Copied" : "Copy"}
          </Button>
          <Button
            onClick={handleClearText}
            className="flex-1 bg-white/12 hover:bg-white/18 border border-white/30 text-white font-semibold rounded-xl backdrop-blur-md transition-all duration-300"
            disabled={!detectedText}
          >
            Clear
          </Button>
        </div>

        {/* Stats + Live info */}
        <div className="bg-white/8 backdrop-blur-md rounded-2xl p-5 border border-white/20">
          <p className="text-xs font-bold text-white/90 uppercase tracking-wider mb-4 drop-shadow-lg">
            Statistics
          </p>

          <div className="grid grid-cols-2 gap-4">
            <div className="bg-white/8 rounded-xl p-4 border border-white/20 backdrop-blur-sm">
              <p className="text-xs text-white/70 font-medium mb-2">
                Characters
              </p>
              <p className="text-3xl font-bold text-white drop-shadow-lg">
                {detectedText.length}
              </p>
            </div>
            <div className="bg-white/8 rounded-xl p-4 border border-white/20 backdrop-blur-sm">
              <p className="text-xs text-white/70 font-medium mb-2">Words</p>
              <p className="text-3xl font-bold text-white drop-shadow-lg">
                {
                  detectedText
                    .trim()
                    .split(/\s+/)
                    .filter((w) => w).length
                }
              </p>
            </div>
          </div>

          {/* Live prediction */}
          {currentPrediction && (
            <div className="mt-6 flex flex-col items-start">
              <p className="text-white/70 text-sm">
                Current sign:{" "}
                <span className="text-white font-bold text-lg">
                  {currentPrediction}
                </span>
              </p>
              <p className="text-white/50 text-xs mt-1">
                Confidence: {(confidence ?? 0 * 100).toFixed(1)}%
              </p>

              {history.length > 0 && (
                <div className="mt-3 text-xs text-white/60">
                  <span className="font-semibold text-white/70">Recent:</span>{" "}
                  {history.slice(-5).join(" • ")}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
