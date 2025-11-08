"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Upload, Image as ImageIcon, Loader2 } from "lucide-react";

export default function ImageUploadPanel() {
  const [image, setImage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [prediction, setPrediction] = useState<string | null>(null);
  const [confidence, setConfidence] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = () => setImage(reader.result as string);
    reader.readAsDataURL(file);

    setLoading(true);
    setError(null);
    setPrediction(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch("http://localhost:8080/predict_image", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error("Server error");
      const data = await res.json();
      setPrediction(data.prediction);
      setConfidence(data.confidence);
    } catch (err) {
      console.error(err);
      setError("❌ Failed to analyze image. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-7xl grid grid-cols-1 lg:grid-cols-2 gap-8">
      {/* --- Left: Upload Card --- */}
      <div className="rounded-3xl bg-black/60 backdrop-blur-3xl border border-white/10 shadow-2xl overflow-hidden flex flex-col hover:bg-black/70 transition-all duration-500">
        <div className="px-8 py-6 border-b border-white/10 backdrop-blur-md bg-black/50">
          <h2 className="text-2xl font-bold text-white drop-shadow-lg">
            Image Upload
          </h2>
          <p className="text-white/60 text-sm mt-1">
            Upload an image for hand sign detection
          </p>
        </div>

        <div className="flex-1 flex flex-col p-8 gap-6">
          <div className="relative bg-linear-to-br from-zinc-900/80 via-neutral-900/70 to-black/90 aspect-video rounded-2xl overflow-hidden flex items-center justify-center border border-white/10 shadow-inner backdrop-blur-sm">
            {image ? (
              <img
                src={image}
                alt="Preview"
                className="object-contain w-full h-full bg-black/30 backdrop-blur-sm"
              />
            ) : (
              <div className="flex flex-col items-center justify-center text-white/40">
                <div className="w-20 h-20 rounded-full bg-white/5 flex items-center justify-center border border-white/20 mb-3">
                  <ImageIcon className="w-10 h-10" />
                </div>
                <p className="text-sm font-medium">No image uploaded</p>
              </div>
            )}
          </div>

          <div className="flex gap-3">
            <label
              htmlFor="file-upload"
              className="flex-1 flex items-center justify-center cursor-pointer bg-linear-to-r from-gray-700 to-gray-900 hover:from-gray-600 hover:to-gray-800 text-white font-semibold py-6 rounded-xl shadow-lg transition-all duration-300 backdrop-blur-sm border border-white/20"
            >
              <Upload className="w-5 h-5 mr-2" />
              Upload Image
            </label>
            <input
              id="file-upload"
              type="file"
              accept="image/*"
              className="hidden"
              onChange={handleFileChange}
            />
          </div>
        </div>
      </div>

      {/* --- Right: Result Card --- */}
      <div className="rounded-3xl bg-black/60 backdrop-blur-3xl border border-white/10 shadow-2xl overflow-hidden flex flex-col hover:bg-black/70 transition-all duration-500">
        <div className="px-8 py-6 border-b border-white/10 backdrop-blur-md bg-black/50">
          <h2 className="text-2xl font-bold text-white drop-shadow-lg">
            Prediction Result
          </h2>
          <p className="text-white/60 text-sm mt-1">
            Model output and confidence level
          </p>
        </div>

        <div className="flex-1 flex flex-col items-center justify-center p-8 text-center">
          {loading ? (
            <div className="flex flex-col items-center gap-3">
              <Loader2 className="animate-spin text-white/80" size={40} />
              <p className="text-white/60 text-sm">Analyzing image...</p>
            </div>
          ) : error ? (
            <p className="text-red-400 font-medium text-sm">{error}</p>
          ) : prediction ? (
            <div className="flex flex-col items-center gap-6">
              <h2 className="text-[130px] font-extrabold text-transparent bg-gradient-to-br from-cyan-300 to-blue-500 bg-clip-text drop-shadow-[0_0_25px_rgba(0,255,255,0.3)]">
                {prediction}
              </h2>
              <div className="w-80 bg-white/10 rounded-full h-4 overflow-hidden border border-white/20 shadow-inner">
                <div
                  className="bg-gradient-to-r from-cyan-400 via-blue-500 to-indigo-500 h-full transition-all duration-700"
                  style={{
                    width: `${Math.min(confidence! * 100, 100)}%`,
                  }}
                ></div>
              </div>
              <p className="text-white/70 text-base">
                Confidence: {(confidence! * 100).toFixed(2)}%
              </p>
            </div>
          ) : (
            <p className="text-white/40 text-sm">
              Upload an image to view prediction results here.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
