"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Camera, Image, BarChart3 } from "lucide-react";
import clsx from "clsx";

interface ModeSwitcherProps {
  mode: "camera" | "image" | "charts";
  onChange: (newMode: "camera" | "image" | "charts") => void;
}

export default function ModeSwitcher({ mode, onChange }: ModeSwitcherProps) {
  const items = [
    { id: "camera", icon: <Camera size={18} />, label: "Camera" },
    { id: "image", icon: <Image size={18} />, label: "Image" },
    { id: "charts", icon: <BarChart3 size={18} />, label: "Charts" },
  ];

  return (
    <div className="fixed bottom-6 right-6 flex gap-3 z-50">
      {items.map((item) => (
        <Button
          key={item.id}
          onClick={() => onChange(item.id as any)}
          className={clsx(
            "h-12 w-12 rounded-full backdrop-blur-xl border border-white/25 text-white flex items-center justify-center shadow-lg transition-all duration-300",
            mode === item.id
              ? "bg-cyan-400/30 hover:bg-cyan-400/40 scale-105"
              : "bg-white/10 hover:bg-white/20",
          )}
        >
          {item.icon}
        </Button>
      ))}
    </div>
  );
}
