"use client";

import { useState, useRef, useEffect } from "react";
import io from "socket.io-client";
import CameraCard from "@/components/camera-card";
import TextOutputCard from "@/components/text-output-card";
import ConfidenceChartDialog from "@/components/confidence-chart";
import ModeSwitcher from "@/components/mode-switcher";
import ImageUploadCard from "@/components/image-upload";
import BenchmarkDashboard from "@/components/benchmark";

// ⚙️ Backend Socket URL (Flask-SocketIO server)
const SOCKET_URL = "http://localhost:8080";

export default function Home() {
  const [mode, setMode] = useState<"camera" | "image" | "charts">("camera");

  // 🔌 Socket
  const [socket, setSocket] = useState<any>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);

  // 🎥 Camera states
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [isRecording, setIsRecording] = useState(false);

  // 🔠 Prediction states
  const [detectedText, setDetectedText] = useState("");
  const [currentPrediction, setCurrentPrediction] = useState<string | null>(
    null,
  );
  const [confidence, setConfidence] = useState<number>(0);

  // ==========================
  // 🚀 INIT SOCKET CONNECTION
  // ==========================
  useEffect(() => {
    const sock = io(SOCKET_URL, {
      transports: ["websocket"],
      reconnection: true,
      reconnectionAttempts: 10,
      reconnectionDelay: 2000,
    });
    setSocket(sock);

    sock.on("connect", () => console.log("✅ Connected to backend"));
    sock.on("disconnect", () => console.log("❌ Disconnected from backend"));

    sock.on("prediction", (data: any) => {
      setCurrentPrediction(data.prediction);
      setConfidence(data.confidence);

      // Nếu độ tin cậy đủ cao => thêm vào text
      if (data.confidence > 0.5 && data.prediction.length === 1) {
        setDetectedText((prev) => prev + data.prediction);
      }
    });

    return () => {
      sock.disconnect();
    };
  }, []);

  // ==========================
  // 🎥 CAMERA CONTROL
  // ==========================
  const startCamera = async () => {
    try {
      const newStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "user" },
        audio: false,
      });
      setStream(newStream);
      setIsCameraActive(true);
      console.log("🎥 Camera permission granted");
    } catch (err) {
      console.error("❌ Error accessing camera:", err);
    }
  };

  useEffect(() => {
    if (isCameraActive && videoRef.current && stream) {
      const video = videoRef.current;
      video.srcObject = stream;
      video.muted = true;
      video.onloadedmetadata = () => {
        video
          .play()
          .catch((err) => console.error("❌ video.play() failed:", err));
        console.log("✅ Video stream started");
      };
    }
  }, [isCameraActive, stream]);

  const stopCamera = () => {
    if (videoRef.current?.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach((track) => track.stop());
      videoRef.current.srcObject = null;
      setIsCameraActive(false);
      setIsRecording(false);
    }
  };

  const toggleRecording = () => {
    if (!isCameraActive) return;
    setIsRecording((prev) => !prev);
  };

  // ==========================
  // 📸 CAPTURE & SEND FRAMES
  // ==========================
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isRecording && socket && videoRef.current) {
      interval = setInterval(() => captureAndSendFrame(), 300);
    }
    return () => clearInterval(interval);
  }, [isRecording, socket]);

  const captureAndSendFrame = () => {
    const video = videoRef.current;
    if (!video || !socket) return;

    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.drawImage(video, 0, 0);
    const frame = canvas.toDataURL("image/jpeg", 0.5);
    socket.emit("frame", frame);
  };

  // ==========================
  // 🎨 RENDER
  // ==========================
  return (
    <main className="min-h-screen w-full flex flex-col relative overflow-hidden">
      {/* Background */}
      <div
        className="absolute inset-0 bg-cover bg-center bg-no-repeat"
        style={{
          backgroundImage: 'url("/room-bg-3.jpg")',
        }}
      >
        <div className="absolute inset-0 bg-linear-to-b from-cyan-500/20 via-blue-500/10 to-slate-900/40" />
      </div>
      {/* Header */}
      <header className="relative z-20 backdrop-blur-xl bg-white/8 border-b border-white/15">
        <div className="container mx-auto px-6 py-6 flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-white drop-shadow-lg">
              Hand Sign Detector
            </h1>
            <p className="text-white/70 text-sm mt-1">
              Real-time hand sign recognition powered by Mediapipe +
              RandomForest
            </p>
          </div>

          {/* 📊 Chart Button */}
          <ConfidenceChartDialog latestConfidence={confidence} />
        </div>
      </header>
      {/* Main */}
      <div className="relative z-10 flex-1 flex items-center justify-center px-4 py-12">
        {mode === "camera" && (
          <div className="w-full max-w-7xl grid grid-cols-1 lg:grid-cols-2 gap-8">
            <CameraCard
              videoRef={videoRef}
              isCameraActive={isCameraActive}
              isRecording={isRecording}
              onStartCamera={startCamera}
              onStopCamera={stopCamera}
              onToggleRecording={toggleRecording}
            />
            <TextOutputCard
              detectedText={detectedText}
              setDetectedText={setDetectedText}
              currentPrediction={currentPrediction}
              confidence={confidence}
              history={[
                currentPrediction ?? "",
                ...detectedText.split(""),
              ].slice(-5)}
            />
          </div>
        )}

        {mode === "image" && <ImageUploadCard />}

        {mode === "charts" && <BenchmarkDashboard />}
      </div>
      {/* Switcher */}
      <ModeSwitcher mode={mode} onChange={setMode} />{" "}
    </main>
  );
}
