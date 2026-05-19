import { Button } from "../../components/Button";
import { useState } from "react";
import { logo2 } from "../../assets/images";
import { Icon } from "@iconify/react/dist/iconify.js";

export const PhoneInput = ({setStep, setPhone}: { setStep: (step: number) => void; setPhone: (number: string) => void }) => {
    const [phoneNumber, setPhoneNumber] = useState<string>("");

    const formatPhoneNumber = (value: string) => {
        // Remove all non-digits
        const digits = value.replace(/\D/g, "");
        // Limit to 10 digits
        const limited = digits.substring(0, 10);
        
        // Apply spacing: 00 000 0000
        const part1 = limited.substring(0, 2);
        const part2 = limited.substring(2, 5);
        const part3 = limited.substring(5, 10);

        if (limited.length > 5) return `${part1} ${part2} ${part3}`;
        if (limited.length > 2) return `${part1} ${part2}`;
        return part1;
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const formatted = formatPhoneNumber(e.target.value);
        setPhoneNumber(formatted);
    };

    // Calculate raw length (excluding spaces) for the button validation
    const rawLength = phoneNumber.replace(/\s/g, "").length;

    return (
        <div  >
            <div className="w-full flex flex-col gap-8 px-4">
                <div className="flex flex-col justify-start">
                    <img src={logo2} alt="Sendit Logo" className="size-32 my-[-20px] mt-[-40px]" />
                    <h2 className="text-left text-xl font-bold mb-2">Enter your phone</h2>
                    <p className="text-gray-500 text-sm mb-8">We'll send a verification code to confirm it's you.</p>
                </div>
                
                <div className="flex jusify-between gap-2">
                    <div className="flex rounded-xl p-4 max-w-[120px] items-center bg-white w-fit">
                        <Icon icon="twemoji:flag-nigeria" width={20} className="mr-2" />
                        <span className="text-black ">+234</span>
                    </div>
                    <div className="flex rounded-xl p-4 w-full items-center bg-white">
                        <input 
                            type="tel" 
                            inputMode="numeric"
                            value={phoneNumber}
                            onChange={handleInputChange} 
                            placeholder="00 000 0000" 
                            className="bg-transparent flex-1 outline-none" 
                        />
                    </div>
                </div>

                <Button disabled={rawLength < 10} title="Continue" onClick={() => {setStep(3); setPhone(phoneNumber);}}/>
                <div className="flex justify-center items-center gap-1 cursor-pointer">
                    <Icon icon="mdi:whatsapp" width={20} className="inline-block  text-green-500" />
                    <p className="text-center text-primary hover:text-primary/80 !font-bold">Verify with WhatsApp instead</p>
                </div>
            </div>
        </div>
    );
};