import { Button } from "../../components/Button";
import { useState } from "react";
import { logo2 } from "../../assets/images";
import { useNavigate } from "react-router-dom";
import { Icon } from "@iconify/react/dist/iconify.js";
import confetti from "canvas-confetti";
import api from "../../api/axios";

// --- Loading Component ---
const LoadingOverlay = () => (
  <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-white/90 backdrop-blur-sm">
    <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
    <p className="mt-4 text-primary font-bold animate-pulse">Finalizing your offer...</p>
  </div>
);

export const Step4 = ({ 
  amount, 
  offerId, 
  isFragile, 
  offerType, 
  offerImage, 
  isUrgent, 
  from, 
  to, 
  receiverName, 
  receiverContact 
}: { 
  amount: string; 
  offerId: string; 
  isFragile: boolean | null; 
  offerType: string; 
  offerImage: File | null; 
  isUrgent: boolean; 
  from: string; 
  to: string; 
  receiverName: string; 
  receiverContact: string 
}) => {
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handlePostOffer = async () => {
    if (!offerId) {
      alert("System error: Missing Offer ID. Please restart the process.");
      return;
    }

    setIsLoading(true);

    try {
      const formData = new FormData();
      
      // Basic Details
      formData.append('package_type', offerType.toLowerCase() || 'small');
      formData.append('is_fragile', String(isFragile ?? false));
      formData.append('description', `Package from ${from} to ${to}`);
      formData.append('receiver_name', receiverName);
      formData.append('receiver_phone', receiverContact);
      formData.append('base_price', amount);
      formData.append('is_urgent', String(isUrgent));

      // Locations
      formData.append('pickup_location', JSON.stringify({ 
        city: from, 
        street: from 
      }));
      
      formData.append('delivery_location', JSON.stringify({ 
        city: to, 
        street: to 
      }));
      
      if (offerImage) {
        formData.append('image', offerImage);
      }

      await api.patch(`/offers/${offerId}/review/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      // Success effects
      confetti({
        particleCount: 150,
        spread: 70,
        origin: { y: 0.6 },
        colors: ['#1D4ED8', '#60A5FA', '#FFFFFF']
      });

      setIsSubmitted(true);
    } catch (error: any) {
      console.error("Finalization Error:", error.response?.data);
      const backendError = error.response?.data;
      
      let msg = "Failed to post offer.";
      if (backendError && typeof backendError === 'object') {
        msg = Object.entries(backendError)
          .map(([key, val]) => `${key}: ${Array.isArray(val) ? val.join(", ") : val}`)
          .join('\n');
      }
      alert(msg);
    } finally {
      setIsLoading(false);
    }
  };

  if (isSubmitted) {
    return (
      <div className="w-full flex mt-4 flex-col justify-center items-center gap-8 px-4">
        <img src={logo2} alt="Sendit Logo" className="size-32 my-[-20px] mt-[-60px]" />
        <div className="flex flex-col justify-center items-center gap-2">
          <div className="bg-primary/10 p-6 rounded-full mb-4">
            <Icon icon="icon-park-solid:check-one" className="text-primary text-6xl" />
          </div>
          <h2 className="text-center text-xl font-bold mb-2">Offer Posted!</h2>
          <p className="text-center text-gray-500 text-sm mb-8">
            Your delivery from <b>{from}</b> to <b>{to}</b> is now live.
          </p>
        </div>
        <Button title="Go to Dashboard" onClick={() => navigate('/home')} />
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-8 !text-black relative min-h-[400px]">
      {isLoading && <LoadingOverlay />}

      <div className="flex flex-col">
        <h2>Review & confirm</h2>
        <p className="!text-bodyText/50 !font-bold !text-sm">Double check your delivery details.</p>
      </div>

      <div className='rounded-lg flex bg-gray-100 border border-gray-200 p-4 flex-col gap-4'>
        <div className='flex justify-between items-center'>
          <p className='!text-bodyText/70'>Package</p>
          <p className='!text-sm text-black font-semibold'>{offerType} · {isFragile ? 'Fragile' : 'Standard'}</p>
        </div>
        
        <div className='flex border-t border-bodyText/20 gap-4 border-dotted justify-between pt-4'>
          <p className='!text-bodyText/70'>Route</p>
          <p className='!text-sm text-right font-medium'>{from} → {to}</p>
        </div>

        <div className='flex border-t border-bodyText/20 gap-4 border-dotted justify-between pt-4'>
          <p className='!text-bodyText/70'>Pricing</p>
          <p className='!text-sm text-right font-bold text-primary'>₦{Number(amount).toLocaleString()}</p>
        </div>

        <div className='flex border-t border-bodyText/20 gap-4 border-dotted justify-between pt-4'>
          <p className='!text-bodyText/70'>Urgent</p>
          <p className='!text-sm text-right'>{isUrgent ? 'Yes (+ Bonus)' : 'Standard'}</p>
        </div>

        <div className='flex border-t border-bodyText/20 gap-4 border-dotted justify-between pt-4'>
          <p className='!text-bodyText/70'>Receiver</p>
          <p className='!text-sm text-right'>{receiverName} ({receiverContact})</p>
        </div>
      </div>

      <Button
        title="Confirm & Post Offer"
        onClick={handlePostOffer}
        disabled={isLoading}
      />
    </div>
  );
};