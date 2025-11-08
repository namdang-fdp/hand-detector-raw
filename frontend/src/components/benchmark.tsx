"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
} from "recharts";
import { Loader2 } from "lucide-react";

interface BenchmarkItem {
  model: string;
  accuracy: number;
  precision: number;
  recall: number;
  f1: number;
  train_time: number;
}

export default function BenchmarkDashboard() {
  const [data, setData] = useState<BenchmarkItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://localhost:8080/stats")
      .then(async (res) => {
        if (!res.ok) {
          const text = await res.text();
          throw new Error(`Response not OK: ${res.status} - ${text}`);
        }
        return res.json();
      })
      .then((json) => {
        setData(json.benchmark_results || []);
      })
      .catch((err) => console.error("Fetch error:", err))
      .finally(() => setLoading(false));
  }, []);

  const chartBaseProps = {
    margin: { top: 30, right: 30, bottom: 10, left: 0 },
  };

  return (
    <main className="min-h-screen w-full flex flex-col relative overflow-hidden">
      {/* Background */}

      {/* Content */}
      <div className="relative z-10 flex-1 flex flex-col items-center justify-center px-8 py-12">
        {loading ? (
          <div className="flex flex-col items-center text-white/70">
            <Loader2 className="animate-spin w-10 h-10 mb-3" />
            <p>Loading benchmark results...</p>
          </div>
        ) : (
          <div className="w-full max-w-7xl grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8">
            {/* Accuracy */}
            <MetricChart
              title="Accuracy"
              data={data}
              dataKey="accuracy"
              color="#22d3ee"
              {...chartBaseProps}
            />
            {/* Precision */}
            <MetricChart
              title="Precision"
              data={data}
              dataKey="precision"
              color="#a855f7"
              {...chartBaseProps}
            />
            {/* Recall */}
            <MetricChart
              title="Recall"
              data={data}
              dataKey="recall"
              color="#10b981"
              {...chartBaseProps}
            />
            {/* F1 */}
            <MetricChart
              title="F1 Score"
              data={data}
              dataKey="f1"
              color="#3b82f6"
              {...chartBaseProps}
            />
            {/* Train Time */}
            <MetricChart
              title="Training Time (s)"
              data={data}
              dataKey="train_time"
              color="#facc15"
              {...chartBaseProps}
            />
            {/* Radar Chart */}
            <RadarOverview data={data} />
          </div>
        )}
      </div>
    </main>
  );
}

/* ---------- Sub-components ---------- */

function MetricChart({
  title,
  data,
  dataKey,
  color,
  ...props
}: {
  title: string;
  data: BenchmarkItem[];
  dataKey: keyof BenchmarkItem;
  color: string;
}) {
  return (
    <Card className="bg-black/60 backdrop-blur-3xl border border-white/10 shadow-2xl text-white rounded-3xl">
      <CardHeader>
        <CardTitle className="text-xl flex items-center gap-2">
          <span
            className="inline-block w-3 h-3 rounded-full"
            style={{ backgroundColor: color }}
          />
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={data} {...props}>
            <XAxis dataKey="model" stroke="#ccc" tick={{ fill: "#ccc" }} />
            <YAxis
              stroke="#ccc"
              tick={{ fill: "#ccc" }}
              domain={dataKey === "train_time" ? [0, "auto"] : [0, 1]}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "rgba(20,20,30,0.9)",
                borderRadius: "10px",
                border: "1px solid rgba(255,255,255,0.15)",
                color: "#fff",
              }}
            />
            <Bar dataKey={dataKey} fill={color} radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}

function RadarOverview({ data }: { data: BenchmarkItem[] }) {
  const radarData = data.map((m) => ({
    model: m.model,
    accuracy: m.accuracy,
    precision: m.precision,
    recall: m.recall,
    f1: m.f1,
  }));

  return (
    <Card className="bg-black/60 backdrop-blur-3xl border border-white/10 shadow-2xl text-white rounded-3xl">
      <CardHeader>
        <CardTitle className="text-xl">📈 Performance Radar</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarData}>
            <PolarGrid stroke="rgba(255,255,255,0.15)" />
            <PolarAngleAxis
              dataKey="model"
              tick={{ fill: "#fff", fontSize: 12 }}
            />
            <PolarRadiusAxis
              angle={45}
              domain={[0, 1]}
              tick={{ fill: "#ccc" }}
            />
            <Radar
              name="accuracy"
              dataKey="accuracy"
              stroke="#22d3ee"
              fill="#22d3ee80"
            />
            <Radar name="f1" dataKey="f1" stroke="#3b82f6" fill="#3b82f680" />
          </RadarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
