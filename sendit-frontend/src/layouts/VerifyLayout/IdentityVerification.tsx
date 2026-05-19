import { Button } from "../../components/Button";
import { useState } from "react";
import { IdentityCapture } from "./IdentityCapture";
import { Icon } from "@iconify/react";

export const IdentityVerification = ({ setStep, setIdentificationData }: { setStep: (step: number) => void; setIdentificationData: (data: any) => void }) => {
    const documents = {
        "NIN Slip": "mdi:id-card-outline",
        "Passport": "mdi:file-document-outline",
        "Driver's License": "mdi:id-card-outline",
        "Voter's Card": "mdi:id-card-outline",
    };

    const [selectedDoc, setSelectedDoc] = useState<string>("");
    const [isCapturing, setIsCapturing] = useState<boolean>(false);

    // If the user clicked continue, show the Camera Screen
    if (isCapturing) {
        return (
            <IdentityCapture 
                setStep={(step) => {
                    setStep(step);
                    // If IdentityCapture calls setStep(3), it means they clicked "back"
                    // We just close the camera instead of changing the global step
                    setIsCapturing(false); 
                }} 
                setIdentificationData={setIdentificationData}
                documentType={selectedDoc} 
            />
        );
    }

    return (
        <div>
            <div className="w-full flex flex-col gap-8 px-4">
                <div className="flex flex-col justify-start">
                    <h2 className="text-left text-xl font-bold mb-2">Verify your identity</h2>
                    <p className="text-gray-500 text-sm mb-8">Choose a document type to proceed</p>
                </div>
                
                <div className="flex flex-col w-full gap-4 pr-4">
                    {Object.entries(documents).map(([name, icon]) => (
                        <div 
                            key={name}
                            onClick={() => setSelectedDoc(name)} 
                            className={`flex p-4 items-center bg-white rounded-lg gap-2 cursor-pointer transition-all border-2 ${
                                selectedDoc === name ? 'border-primary ring-1 ring-primary' : 'border-transparent'
                            }`}
                        >
                            <div className="flex gap-2 items-center">
                                <Icon icon={icon} width={20} className={selectedDoc === name ? "text-primary" : "text-black"} />
                                <p className={`text-sm font-medium ${selectedDoc === name ? "text-primary" : "text-gray-800"}`}>
                                    {name}
                                </p>
                            </div>
                            {selectedDoc === name ? (
                                <Icon icon="ix:circle-dot-filled" width={24} className="ml-auto text-primary" />
                            ) : (
                                <Icon icon="ph:circle-light" width={24} className="ml-auto text-gray-300" />
                            )}
                        </div>
                    ))}
                </div>

                <Button 
                    title="Continue" 
                    disabled={!selectedDoc} 
                    onClick={() =>{ setIsCapturing(true)}}
                />

                <div className="flex justify-center items-center gap-1">
                    <Icon icon="mdi:lock" width={16} className="text-black/30" />
                    <p className="text-center text-black/50 font-bold">
                        Your info will be encrypted and stored securely.
                    </p>
                </div>
            </div>
        </div>
    );
};