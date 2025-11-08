"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  AreaChart,
  Area,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

interface ConfidenceChartProps {
  latestConfidence?: number;
}

export default function ConfidenceChartDialog({
  latestConfidence,
}: ConfidenceChartProps) {
  const [open, setOpen] = useState(false);
  const [confidences, setConfidences] = useState<number[]>([]);

  // 🎯 Mỗi khi backend gửi lên confidence mới => thêm vào danh sách
  useEffect(() => {
    if (latestConfidence !== undefined) {
      setConfidences((prev) => [...prev.slice(-49), latestConfidence]); // giữ 50 điểm gần nhất
    }
  }, [latestConfidence]);

  const data = confidences.map((c, i) => ({
    frame: i + 1,
    confidence: c * 100,
  }));

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button className="bg-white/10 border border-white/25 hover:bg-white/20 text-white backdrop-blur-xl rounded-xl transition-all duration-300 shadow-lg">
          📊 View Confidence Trend
        </Button>
      </DialogTrigger>

      <DialogContent className="max-w-5xl bg-slate-900/80 border border-white/15 backdrop-blur-3xl text-white rounded-3xl shadow-2xl p-8">
        <DialogHeader>
          <DialogTitle className="text-3xl font-bold bg-gradient-to-r from-cyan-300 to-blue-400 bg-clip-text text-transparent drop-shadow-lg">
            Confidence Analytics
          </DialogTitle>
          <p className="text-white/70 text-sm mt-1">
            Real-time trend of model confidence values from backend predictions
          </p>
        </DialogHeader>

        <div className="w-full h-[400px] mt-8 bg-white/5 backdrop-blur-xl rounded-2xl p-4 border border-white/10 shadow-inner">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data}>
              <defs>
                <linearGradient id="colorConf" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#38bdf8" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="rgba(255,255,255,0.08)"
              />
              <XAxis
                dataKey="frame"
                stroke="#94a3b8"
                tick={{ fill: "#94a3b8", fontSize: 12 }}
              />
              <YAxis
                domain={[0, 100]}
                stroke="#94a3b8"
                tick={{ fill: "#94a3b8", fontSize: 12 }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "rgba(15, 23, 42, 0.85)",
                  borderRadius: "1rem",
                  border: "1px solid rgba(255,255,255,0.1)",
                  color: "white",
                }}
                labelStyle={{ color: "#38bdf8" }}
              />
              <Area
                type="monotone"
                dataKey="confidence"
                stroke="#38bdf8"
                strokeWidth={3}
                fillOpacity={1}
                fill="url(#colorConf)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="text-right mt-6 text-white/70 text-sm italic">
          Showing last {data.length} frames — updated live
        </div>
      </DialogContent>
    </Dialog>
  );
}
