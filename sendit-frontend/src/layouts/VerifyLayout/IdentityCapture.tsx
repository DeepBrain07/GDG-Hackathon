import React, { useRef, useEffect, useState } from 'react';
import { Icon } from '@iconify/react';

interface IdentityCaptureProps {
  setStep: (step: number) => void;
  documentType?: string;
  setIdentificationData: (data: any) => void;
}

export const IdentityCapture: React.FC<IdentityCaptureProps> = ({ setStep, documentType = "NIN", setIdentificationData }) => {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null); // Ref for the hidden canvas
  const [stream, setStream] = useState<MediaStream | null>(null);

  // Initialize camera
  useEffect(() => {
    async function startCamera() {
      try {
        const mediaStream = await navigator.mediaDevices.getUserMedia({
          video: { 
            facingMode: 'environment', 
            width: { ideal: 1920 }, // Higher resolution for better OCR later
            height: { ideal: 1080 } 
          }
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
      // Improved cleanup: stop all tracks when component unmounts
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
      context.drawImage(video, 0, 0, canvas.width, canvas.height);

      const capturedImage = canvas.toDataURL('image/jpeg', 0.8);

      // --- ADD THIS SECTION TO STOP CAMERA ---
      if (stream) {
        stream.getTracks().forEach(track => {
          track.stop(); // This kills the camera light/process
        });
        setStream(null); // Clear state
      }
      // ---------------------------------------

      setIdentificationData({
        documentType,
        image: capturedImage,
        capturedAt: new Date(),
        dimensions: { width: canvas.width, height: canvas.height }
      });

      setStep(4);
    }
  }
};

  return (
    <div className="fixed inset-0 bg-black z-50 flex flex-col">
      {/* Hidden canvas used for capturing the frame */}
      <canvas ref={canvasRef} className="hidden" />

      {/* Header */}
      <div className="absolute top-0 left-0 right-0 p-6 flex items-center z-20">
        <button 
          onClick={() => setStep(3)}
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
        className="h-full w-full object-cover"
      />

      {/* Viewfinder Overlay */}
      <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
        <div className="absolute inset-0 bg-black/40" style={{ 
          clipPath: 'polygon(0% 0%, 0% 100%, 10% 100%, 10% 30%, 90% 30%, 90% 60%, 10% 60%, 10% 100%, 100% 100%, 100% 0%)' 
        }} />
        
        <div className="relative w-[85%] aspect-[1.6/1] border-2 border-white/50 rounded-xl">
          <div className="absolute -top-1 -left-1 w-6 h-6 border-t-4 border-l-4 border-white rounded-tl-lg" />
          <div className="absolute -top-1 -right-1 w-6 h-6 border-t-4 border-r-4 border-white rounded-tr-lg" />
          <div className="absolute -bottom-1 -left-1 w-6 h-6 border-b-4 border-l-4 border-white rounded-bl-lg" />
          <div className="absolute -bottom-1 -right-1 w-6 h-6 border-b-4 border-r-4 border-white rounded-br-lg" />
        </div>

        <div className="mt-8 text-center px-6">
          <div className="mb-2">
            <Icon icon="eos-icons:loading" className="text-primary text-2xl animate-spin inline-block" />
          </div>
          <h3 className="text-white font-semibold text-lg">Capture card</h3>
          <p className="text-white/80 text-sm">Position {documentType} in frame</p>
        </div>
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