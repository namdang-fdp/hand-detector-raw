"use client";

import { Button } from "@/components/ui/button";
import type { RefObject } from "react";

interface CameraCardProps {
  videoRef: RefObject<HTMLVideoElement | null>;
  isCameraActive: boolean;
  isRecording: boolean;
  onStartCamera: () => void;
  onStopCamera: () => void;
  onToggleRecording: () => void;
}

export default function CameraCard({
  videoRef,
  isCameraActive,
  isRecording,
  onStartCamera,
  onStopCamera,
  onToggleRecording,
}: CameraCardProps) {
  return (
    <div className="rounded-3xl bg-black/60 backdrop-blur-3xl border border-white/10 shadow-2xl overflow-hidden flex flex-col h-full hover:bg-black/70 transition-all duration-500">
      <div className="px-8 py-6 border-b border-white/10 backdrop-blur-md bg-black/50">
        <h2 className="text-2xl font-bold text-white drop-shadow-lg">
          Camera Feed
        </h2>
        <p className="text-white/60 text-sm mt-1">Live hand sign detection</p>
      </div>

      <div className="flex-1 flex flex-col p-8 gap-6">
        <div className="relative bg-linear-to-br from-zinc-900/80 via-neutral-900/70 to-black/90 aspect-video rounded-2xl overflow-hidden flex items-center justify-center border border-white/10 shadow-inner backdrop-blur-sm">
          {isCameraActive ? (
            <>
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className="w-full h-full object-cover z-10"
              />
              {isRecording && (
                <div className="absolute top-6 right-6 flex items-center gap-2 bg-red-600/90 backdrop-blur-md px-5 py-3 rounded-full shadow-lg border border-white/20">
                  <span className="w-2.5 h-2.5 bg-white rounded-full animate-pulse"></span>
                  <span className="text-xs font-bold text-white tracking-wider">
                    RECORDING
                  </span>
                </div>
              )}
            </>
          ) : (
            <div className="text-center">
              <div className="w-20 h-20 rounded-full bg-white/5 flex items-center justify-center mx-auto mb-4 border border-white/20 backdrop-blur-sm">
                <svg
                  className="w-10 h-10 text-white/40"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.5}
                    d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
                  />
                </svg>
              </div>
              <p className="text-white/40 text-sm font-medium">Camera is off</p>
            </div>
          )}
        </div>

        <div className="flex gap-3">
          {!isCameraActive ? (
            <Button
              onClick={onStartCamera}
              className="flex-1 bg-linear-to-r from-gray-700 to-gray-900 hover:from-gray-600 hover:to-gray-800 text-white font-semibold py-6 rounded-xl shadow-lg transition-all duration-300 backdrop-blur-sm"
              size="lg"
            >
              Start Camera
            </Button>
          ) : (
            <>
              <Button
                onClick={onToggleRecording}
                className={`flex-1 font-semibold py-6 rounded-xl shadow-lg transition-all duration-300 backdrop-blur-sm ${
                  isRecording
                    ? "bg-red-600/90 hover:bg-red-700/90 text-white border border-white/20"
                    : "bg-linear-to-r from-gray-700 to-gray-900 hover:from-gray-600 hover:to-gray-800 text-white border border-white/20"
                }`}
                size="lg"
              >
                {isRecording ? "Stop Recording" : "Start Recording"}
              </Button>
              <Button
                onClick={onStopCamera}
                className="flex-1 bg-white/5 hover:bg-white/10 border border-white/20 text-white font-semibold py-6 rounded-xl backdrop-blur-md transition-all duration-300"
                size="lg"
              >
                Stop Camera
              </Button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
