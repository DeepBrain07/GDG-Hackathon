import { carrierLogo, senderLogo } from '../../assets/images';
import './style.css';
import { Button } from '../../components/Button';
import { useNavigate } from 'react-router-dom';
import { useState } from 'react';

function Onboarding() {
  const navigate = useNavigate();
  const [selectedRole, setSelectedRole] = useState<any>(null);
  return (
    <div className="background">
        {/* Background Layers */}
        <div className="gradient-layer-alt" />
        <div className='my-14 mx-243 w-full flex flex-col justify-start'>
            <div className='p-4 flex flex-col mb-10'>
                <h2 >How will you use Send<span className="!font-extrabold !text-2xl">it</span></h2>    
                <p className='text-bodyText/80 font-bold'>You can switch anytime from settings.</p>
            </div>
            <div className="flex flex-col gap-8 w-full px-4 pr-8">
                <SenderCard 
                isSelected={selectedRole === 'sender'} 
                onClick={() => setSelectedRole('sender')} 
                />
                <CarrierCard 
                    isSelected={selectedRole === 'carrier'} 
                    onClick={() => setSelectedRole('carrier')} 
                />
                <Button disabled={selectedRole === null} title='Continue' onClick={() => navigate("/verify")} className="!w-[100%] mt-6"/>
            </div>
        </div>      
    </div>
  );
}


const SenderCard = ({ isSelected, onClick }: { isSelected: boolean; onClick: () => void }) => {
    const features = [
        "💸 Save up to 60%",
        "⚡ Faster than couriers",
        "🛡️ Verified travelers only"
    ];

    return (
        <div 
            onClick={onClick}
            className={`
                w-full flex flex-col gap-2 justify-start bg-white rounded-xl p-4 py-6 border-1 transition-all cursor-pointer
                ${isSelected 
                    ? 'border-primary/80 border-3 ring-4 ring-primary/30' 
                    : 'border-secondary/20 hover:border-primary/40'
                }
            `}
        >       
            <img src={senderLogo} alt="Sender Logo" className='size-12 mb-4' />
            <h2 className='text-bodyText font-extrabold !text-[15px]'>I want to send something - Sender</h2>
            <p className='text-bodyText/80 !text-xs'>Find trusted travelers heading to your destination.</p>
            <div className='flex gap-2 mt-4'>
                {features.map((feature, index) => (
                    <div key={index} className='flex flex-start items-center rounded-full px-2 py-1 bg-secondary/40 gap-2'>
                        <span>{feature.split(" ")[0]}</span>
                        <p className='text-bodyText/80 !text-[10px] '>{feature.split(" ").slice(1).join(" ")}</p>
                    </div>
                ))}
            </div>
        </div>
    );
}

const CarrierCard = ({ isSelected, onClick }: { isSelected: boolean; onClick: () => void }) => {
    const features = [
        "💰 Earn ₦3k–₦15k",
        "🗺️ Match your route",
        "🛡️ Verified senders only"
    ];

    return (
        <div 
            onClick={onClick}
            className={`
                w-full flex flex-col gap-2 justify-start bg-white rounded-xl p-4 py-6 border-1 transition-all cursor-pointer
                ${isSelected 
                    ? 'border-primary/80 border-3 ring-4 ring-primary/30' 
                    : 'border-secondary/20 hover:border-primary/40'
                }
            `}
        >       
            <img src={carrierLogo} alt="Carrier Logo" className='size-12 mb-4' />
            <h2 className='text-bodyText font-extrabold !text-[15px]'>I'm traveling somewhere - Carrier</h2>
            <p className='text-bodyText/80 !text-xs'>Monetize your trips by carrying packages along your route.</p>
            <div className='flex gap-2 mt-4'>
                {features.map((feature, index) => (
                    <div key={index} className='flex flex-start items-center rounded-full px-2 py-1 bg-secondary/40 gap-2'>
                        <span>{feature.split(" ")[0]}</span>
                        <p className='text-bodyText/80 !text-[10px] '>{feature.split(" ").slice(1).join(" ")}</p>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default Onboarding;