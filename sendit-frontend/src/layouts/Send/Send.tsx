import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import '../SignInLayout/style.css'
import { Icon } from '@iconify/react/dist/iconify.js';
import { Step1 } from './Step1';
import { Step2 } from './Step2';
import { Step3 } from './Step3';
import { Step4 } from './Step4';
import api from '../../api/axios'; // Assuming your axios instance is here

const Send = () => {
  const navigate = useNavigate();
  const [offerId, setOfferId] = useState<string>('');
  const [step, setStep] = useState<number>(1);
//   step 1
  const [isFragile, setIsFragile] = useState<boolean | null>(null);
  const [offerType, setOfferType] = useState<string>("");
  const [offerImage, setOfferImage] = useState<File | null>(null);
  const [_offerDescription, setOfferDescription] = useState<string>('');
//   step 2
  const [city, setCity] = useState<string>('');
  const [_street, setStreet] = useState<string>('');
    const [_time, setTime] = useState<string>('');
    const [destinationCity, setDestinationCity] = useState<string>('');
    const [_destinationStreet, setDestinationStreet] = useState<string>('');
    const [receiverName, setReceiverName] = useState<string>('');
    const [receiverContact, setReceiverContact] = useState<string>('');
    // step 3
    const [amount, setAmount] = useState<string>('2500');
    const [isUrgent, setIsUrgent] = useState<boolean>(false);
  const steps = ['Details', 'Location', 'Pricing', 'Review']

  useEffect(() => {
    let isMounted = true;

    const fetchOfferId = async () => {
      while (isMounted && !offerId) {
        try {
          const response = await api.post('/offers/');
          if (response.data) {
            setOfferId(response.data.data.id);
            console.log("Received Offer ID:", response.data.data.id);
            break; 
          }
        } catch (error) {
          console.error("Polling for Offer ID failed:", error);
        }
        // Wait for 2 seconds before the next poll to avoid overloading
        await new Promise(resolve => setTimeout(resolve, 2000));
      }
    };

    fetchOfferId();

    return () => {
      isMounted = false;
    };
  }, [offerId]);

  return (
    <div >
        
        <div className='bg-[#FBFBFBB2] p-4 flex flex-col gap-8'>
            <div className={` w-full flex items-center justify-between gap-4  `}>
                <div className='flex items-center '>
                    <button onClick={() => navigate('/home')} className="p-2 bg-white rounded-[50%] hover:bg-gray-100 transition-colors">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M15 18L9 12L15 6" stroke="black" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
                    </button>
                    <h2 className="!text-xl">Send Package</h2>
                </div>
                <div className=' flex justify-end w-fit '><p className='bg-gray-300 rounded-full p-1 px-2 !text-xs'>{step} / 4</p></div>
            </div>
            <div className="flex justify-between w-full overflow-x-scroll !text-white">
                {steps.map((name, index) => (
                    <div key={index} className={`flex flex-col w-full justify-between ${index === 0 ? 'items-start' : index === 3 ? 'items-end' : 'items-center'} `}>
                        <div className={`flex w-full items-center  ${index === 0 ? 'justify-start' : index === 3 ? 'justify-end' : 'justify-center'}`}>
                            {(index !== 0) && <div className={`${index + 1 <= step ? 'border-primary' : 'border-gray-400'} w-full h-fit border-1 relative`}/>}
                            <div className='shrink-0 '>
                                <Icon
                                    icon="tabler:circle-dot-filled"
                                    className={ `${index + 1 <= step ? ' text-primary' : 'text-gray-400 shrink-0 size-fit'}`}
                                />
                            </div>
                            {index !== 3 && <div className={`${index + 2 <= step ? 'border-primary' : 'border-gray-400'} w-full h-fit border-1 relative`}/>}
                            
                        </div>
                        <p className={`${index + 1 <= step ? 'text-black' : 'text-bodyText/50'} !font-bold`}>{name}</p>
                    </div>
                ))}
            </div>
        </div>
        
        {/* Content */}
        <div className='flex flex-col gap-8 p-4'>
            {step === 1 ? <Step1 setStep={setStep} setIsFragile={setIsFragile} setOfferType={setOfferType} setOfferImage={setOfferImage} setOfferDescription={setOfferDescription}/> : 
            step === 2 ? <Step2 setStep={setStep} setCity={setCity} setStreet={setStreet} setTime={setTime} setDestinationCity={setDestinationCity} setDestinationStreet={setDestinationStreet} setReceiverName={setReceiverName} setReceiverContact={setReceiverContact}/> : 
            step === 3 ? <Step3 setStep={setStep} amount={amount} setAmount={setAmount} setIsUrgent={setIsUrgent}/> : 
            <Step4 offerId={offerId} amount={amount} isFragile={isFragile} offerType={offerType} offerImage={offerImage} isUrgent={isUrgent} from={city}  to={destinationCity} receiverName={receiverName} receiverContact={receiverContact}/>}
        </div>

        
    </div>
  );
};

export default Send;