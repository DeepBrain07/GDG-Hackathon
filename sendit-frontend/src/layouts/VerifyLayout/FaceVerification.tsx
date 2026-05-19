import { Button } from "../../components/Button";
import { useState } from "react";
import { Icon } from "@iconify/react";
import { FaceCapture } from "./FaceCapture";
import { selfie } from "../../assets/images";

export const FaceVerification = ({ loading, setStep, setFaceData, setIsLoading }: { loading: boolean; setStep: (step: number) => void; setFaceData: (data: any) => void; setIsLoading: (loading: boolean) => void }) => {

    const [isCapturing, setIsCapturing] = useState<boolean>(false);

    // If the user clicked continue, show the Camera Screen
    if (isCapturing) {
        return (
            <FaceCapture 
                setStep={setStep}
                setFaceData={setFaceData}
                setIsLoading={setIsLoading}
                onClose={() => setIsCapturing(false)} // This "closes" the camera
            />
        );
    }

    return (
        <div className="relative min-h-full">
            {/* --- Beautiful Loading Overlay --- */}
            {loading && (
                <div className="fixed inset-0 z-[100] flex flex-col items-center justify-center bg-white/60 backdrop-blur-md animate-in fade-in duration-300">
                    <div className="relative flex items-center justify-center">
                        {/* Outer rotating gradient ring */}
                        <div className="absolute w-20 h-20 rounded-full border-4 border-transparent border-t-primary border-r-primary/30 animate-spin"></div>
                        
                        {/* Inner pulsating icon or logo */}
                        <div className="bg-white p-4 rounded-full shadow-xl animate-pulse">
                            <Icon icon="solar:shield-user-bold" className="text-primary size-8" />
                        </div>
                    </div>
                    
                    <div className="mt-6 text-center">
                        <h3 className="text-lg font-bold text-gray-900">Verifying Identity</h3>
                        <p className="text-sm text-gray-500 animate-pulse">Please wait a moment...</p>
                    </div>
                </div>
            )}

            <div className={`w-full flex flex-col gap-8 px-4 transition-all duration-300 ${loading ? 'blur-sm scale-95 pointer-events-none' : ''}`}>
                <div className="flex flex-col justify-start">
                    <h2 className="text-left text-xl font-bold mb-2">Take a selfie</h2>
                    <p className="text-gray-500 text-sm mb-8">We'll match it with your document photo for safety.</p>
                </div>
                
                <div className="flex flex-col justify-center items-center w-full gap-4 pr-4">
                    <img src={selfie} alt="Selfie Illustration" className="w-[150px] max-w-xs mx-auto" />
                    <div className="w-[80%]">
                        <div className="flex gap-1 justify-start items-start">
                            <Icon icon="material-symbols:check-circle-rounded" className="text-primary size-5 shrink-0 inline-block" /> 
                            <p className="text-sm">Make sure you are in a well-lit area.</p>
                        </div>
                        <div className="flex gap-1 justify-start items-start mt-2">
                            <Icon icon="material-symbols:check-circle-rounded" className="text-primary size-5 shrink-0 inline-block" /> 
                            <p className="text-sm">Hold your phone at eye level and look straight to the camera</p>
                        </div>
                    </div>
                </div>

                <Button 
                    title="Take Selfie" 
                    onClick={() =>{ setIsCapturing(true)}}
                />

                <div className="flex justify-center items-center gap-1">
                    <Icon icon="mdi:lock" width={16} className="text-black/30" />
                    <p className="text-center text-xs text-black/50 font-bold">
                        Your info will be encrypted and stored securely.
                    </p>
                </div>
            </div>
        </div>
    );
};