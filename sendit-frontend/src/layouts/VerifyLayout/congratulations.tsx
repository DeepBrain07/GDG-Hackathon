import { useEffect, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import confetti from "canvas-confetti";
import { Button } from "../../components/Button";
import { logo2, selfie2 } from "../../assets/images";

export const Congratulations = () => {
    const navigate = useNavigate(); 

    const userData = useMemo(() => {
        try {
            const user = localStorage.getItem('user');
            console.log("RAW STORAGE USER:", user); // DEBUG 1
            const parsed = JSON.parse(user || '{}');
            console.log("PARSED USER DATA:", parsed); // DEBUG 2
            return parsed;
        } catch (e) {
            console.error("FAILED TO PARSE USER:", e);
            return {};
        }
    }, []);

    // Let's check the exact path to the file URL
    // Depending on your MediaSerializer, it might be .file or .file_url
    const avatarUrl = userData?.profile?.avatar?.file_url || userData?.profile?.avatar?.file || userData?.profile?.data?.avatar?.file_url || selfie2;

    console.log(userData?.profile?.data?.avatar?.file_url); // DEBUG 3
    console.log("FINAL AVATAR URL:", avatarUrl); // DEBUG 3

    useEffect(() => {
        confetti({
            particleCount: 150,
            spread: 70,
            origin: { y: 0.6 },
            colors: ['#1D4ED8', '#60A5FA', '#FFFFFF'] 
        });
    }, []);

    return (
        <div className="w-full flex flex-col justify-center items-center gap-8 px-4"> 
            <img 
                src={logo2} 
                alt="Sendit Logo" 
                className="w-32 h-32 mt-[-60px] object-contain" 
            />
            
            <div className="flex flex-col justify-center items-center gap-2">
                <div className="relative w-[120px] h-[120px] mb-4">
                    <img 
                        src={avatarUrl} 
                        alt="User Avatar" 
                        className="w-full h-full object-cover rounded-2xl border-4 border-blue-50 shadow-lg" 
                        onError={(e) => {
                            console.log("IMAGE FAILED TO LOAD, USING FALLBACK");
                            (e.target as HTMLImageElement).src = selfie2;
                        }}
                    />
                    <div className="absolute -bottom-2 -right-2 bg-blue-600 rounded-full p-1 border-2 border-white">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M20 6L9 17L4 12" stroke="white" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
                        </svg>
                    </div>
                </div>

                <h2 className="text-center text-xl font-bold mb-2">
                    Your account is verified!
                </h2>
                
                <p className="text-center text-gray-500 text-sm mb-8 leading-relaxed">
                    Your ID and selfie are verified. <br />
                    You can now send packages and earn on trips.
                </p>
            </div>

            <Button 
                title="Proceed to Homepage" 
                onClick={() => navigate('/home')}
                className="w-full max-w-xs"
            />
        </div>
    );
};