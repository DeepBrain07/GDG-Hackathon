import { Button } from "../../components/Button";
import { useState,} from "react";
import { Icon } from "@iconify/react/dist/iconify.js";

export const Step3 = ({amount, setAmount, setStep, setIsUrgent}: { amount: string; setAmount: (amount: string) => void; setStep: (step: number) => void; setIsUrgent: (urgent: boolean) => void }) => {
  const [offer, setOffer] = useState<number>(2500);
  const presets = [2000, 4000, 6000, 8000, 10000];
  const [urgent, setUrgent] = useState<boolean>(false);

  const updateOffer = (val: number) => {
    const newVal = Math.max(0, val); // Allow 0 while typing, but min is 500 for slider
    setOffer(newVal);
    setAmount(newVal.toString());
  };

  // Calculate percentage for the slider fill color
  const min = 500;
  const max = 20000;
  const percentage = ((offer - min) / (max - min)) * 100;

  return (
    <div className="flex flex-col gap-8 !text-black">
      <div className="flex flex-col">
        <h2>Set your price</h2>
        <p className="!text-bodyText/50 !font-bold !text-sm">Offer a fair amount to attract travelers quickly.</p>
      </div>
      {/* Amount */}
      <div className="flex flex-col gap-2">
        <div className="flex flex-col items-center w-full gap-8 bg-white rounded-xl">
          <div className="flex items-center gap-4">
            <button 
              onClick={() => updateOffer(offer - 100)}
              className="flex items-center justify-center p-[12px] border border-gray-100 rounded-full cursor-pointer hover:bg-gray-100 transition-colors"
            >
              <Icon icon="akar-icons:minus" className="text-sm"/>
            </button>
            <div className="text-center">
              <div className="text-5xl font-black text-primary flex items-center  justify-center">
                <span className="!text-[25px] !font-extrabold mr-1">₦</span>
                <h1>
                <input 
                  type="number"
                  value={offer === 0 ? "" : offer}
                  onChange={(e) => updateOffer(Number(e.target.value))}
                  className="!text-4xl !font-black bg-transparent border-none outline-none  max-w-[150px]  text-center "
                  placeholder="0"
                />
                </h1>
              </div>
              <p className="text-gray-500 mt-2 font-medium">Your offer to the traveler</p>
            </div>
            <button 
              onClick={() => updateOffer(offer + 100)}
              className="flex items-center justify-center p-[12px] border border-gray-100 rounded-full cursor-pointer hover:bg-gray-100 transition-colors"
            >
              <Icon icon="akar-icons:plus" className="text-sm"/>
            </button>
          </div>

          <div className="w-full px-4">
            <input 
              type="range" 
              min={min} 
              max={max} 
              step="500"
              value={offer < min ? min : offer}
              onChange={(e) => updateOffer(parseInt(e.target.value))}
              style={{
                background: `linear-gradient(to right, #335CF4 ${percentage}%, #F3F4F6 ${percentage}%)`
              }}
              className="w-full h-2 rounded-lg appearance-none cursor-pointer accent-primary"
            />
            <div className="flex justify-between mt-2 text-xs  !text-bodyText/80 !font-bold">
              <span>₦500 min</span>
              <span>Custom</span>
            </div>
          </div>

          <div className="flex flex-wrap justify-center gap-2 !font-bold !text-bodyText/80">
            {presets.map((price) => (
              <button
                key={price}
                onClick={() => updateOffer(price)}
                className={`px-2 py-2 !text-xs rounded-xl font-bold transition-all ${
                  offer === price ? "bg-primary text-white" : "bg-gray-50  hover:bg-gray-100"
                }`}
              >
                ₦{price.toLocaleString()}
              </button>
            ))}
          </div>
        </div>
      </div>
      {/* Urgent Delivery */}
      <div className="!font-black p-4 px-2 flex items-center justify-between border-1 rounded-xl border-gray-200">
            <div className="flex gap-2 items-start">
                <div className="p-2 w-fit rounded-lg h-fit bg-gray-100">
                    <Icon icon="fluent:flash-sparkle-24-filled" width={26} className='text-primary'/>
                </div>
                <p>Urgent delivery bonus <br/><span className="text-bodyText/80 font-medium !text-xs">Add +₦500 to attract travelers faster</span></p>
            </div>
            <div>
                {/* Urgent Delivery Checkbox */}
                <label className="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" checked={urgent} onChange={(e) => {setUrgent(e.target.checked); setIsUrgent(e.target.checked)}} className="sr-only peer" />
                    <div className="w-11 h-6 bg-gray-200 rounded-full peer  peer-focus:ring-primary/50 peer-checked:bg-primary after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:after:translate-x-full peer-checked:after:border-white" />
                </label>

            </div>
      </div>
      {/* payout breakdown */}
        <div className='mt-4 rounded-lg flex bg-gray-100 border-1 border-gray-200 p-4 flex-col gap-4'>
            <p className='!font-black'>Breakdown</p>
            <div className='flex justify-between pt-2  t-2'>
                <p className='!text-bodyText/70'>Your offer</p>
                <p className='!text-sm text-black'>₦{amount}</p>
            </div>
            <div className='flex justify-between   '>
                <p className='!text-bodyText/70'>Platform fee (10%)</p>
                <p className='!text-sm text-red-500'>-₦350</p>
            </div>
            {urgent && (
                <div className='flex justify-between   '>
                    <p className='!text-bodyText/70'>Urgent Bonus</p>
                    <p className='!text-sm '>+₦500</p>
                </div>
            )}
            <div className='flex justify-between !text-xl pt-2  mt-[-4px]  border-t-2 border-bodyText/30 border-dotted'>
                <p className='!text-black'>Traveler receives</p>
                <p className=' !text-black'>₦3,650</p>
            </div>
        </div>
      {/* Continue Button */}
      <Button
        title="Review & Post"
        onClick={() => setStep(4)}
      />
    </div>
  );
};