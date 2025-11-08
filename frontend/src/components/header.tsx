"use client";

export default function Header() {
  return (
    <header className="backdrop-blur-md bg-white/70 dark:bg-slate-900/70 border-b border-white/20">
      <div className="container mx-auto px-4 py-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">
            Hand Sign Detector
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Real-time hand sign recognition powered by AI
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-2 px-3 py-1.5 bg-primary/20 rounded-full border border-white/20">
            <span className="w-2 h-2 bg-primary rounded-full animate-pulse"></span>
            <span className="text-xs font-medium text-primary">Live</span>
          </div>
        </div>
      </div>
    </header>
  );
}
