import React, { useRef, useEffect, useState } from 'react';
import { Icon } from '@iconify/react';

interface FaceCaptureProps {
  setStep: (step: number) => void;
  setFaceData: (data: any) => void;
  setIsLoading: (loading: boolean) => void;
  onClose: () => void; 
}

export const FaceCapture: React.FC<FaceCaptureProps> = ({ setStep, setFaceData, setIsLoading, onClose }) => {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);

  // Helper to stop camera tracks
  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
  };

  // Initialize camera
  useEffect(() => {
    async function startCamera() {
      try {
        const mediaStream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: 'user', width: { ideal: 1280 }, height: { ideal: 720 } }
        });
        if (videoRef.current) {
          videoRef.current.srcObject = mediaStream;
          setStream(mediaStream);
        }
      } catch (err) {
        console.error("Error accessing camera: ", err);
      }
    }
    startCamera();

    return () => {
      // Standard cleanup on unmount
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const handleCapture = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;

    if (video && canvas) {
      const context = canvas.getContext('2d');
      if (context) {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        
        // Mirror the canvas draw because the video is mirrored for user experience
        context.translate(canvas.width, 0);
        context.scale(-1, 1);
        
        context.drawImage(video, 0, 0, canvas.width, canvas.height);

        const faceImage = canvas.toDataURL('image/jpeg', 0.8);

        // --- STOP CAMERA AFTER SUCCESSFUL CAPTURE ---
        stopCamera();

        setFaceData({
          image: faceImage,
          capturedAt: new Date(),
          type: 'selfie'
        });

        setIsLoading(true); 
        onClose(); 
      }
    }
  };

  const handleBack = () => {
    stopCamera();
    setStep(4);
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black z-50 flex flex-col">
      <canvas ref={canvasRef} className="hidden" />

      {/* Header */}
      <div className="absolute top-0 left-0 right-0 p-6 flex items-center z-20">
        <button 
          onClick={handleBack}
          className="w-10 h-10 bg-white rounded-full flex items-center justify-center shadow-lg"
        >
          <Icon icon="solar:arrow-left-linear" className="text-black text-xl" />
        </button>
      </div>

      {/* Video Feed */}
      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted
        style={{ transform: 'scaleX(-1)' }}
        className="h-full w-full object-cover"
      />

      {/* Face Guide Overlay */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
         <div className="w-64 h-80 border-2 border-white/30 rounded-[120px] shadow-[0_0_0_999px_rgba(0,0,0,0.5)]" />
      </div>

      {/* Bottom Controls */}
      <div className="absolute bottom-12 left-0 right-0 flex justify-center items-center z-20">
        <button 
          onClick={handleCapture}
          className="w-20 h-20 rounded-full border-4 border-white flex items-center justify-center transition-transform active:scale-95"
        >
          <div className="w-16 h-16 bg-white rounded-full shadow-inner" />
        </button>
      </div>

      <div className="absolute bottom-2 left-1/2 -translate-x-1/2 w-32 h-1 bg-white/40 rounded-full" />
    </div>
  );
};