import React, { useState, useEffect, useRef } from 'react';
import { Button } from '../../components/Button';
import { Icon } from '@iconify/react/dist/iconify.js';

const PhoneVerification = ({ setStep, phone }: { setStep: (step: number) => void; phone: string }) => {
  const [otp, setOtp] = useState(['', '', '', '', '', '']);
  const [timer, setTimer] = useState(300); 
  
  // Initialize as an empty array but typed correctly
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  useEffect(() => {
    const interval = setInterval(() => {
      setTimer((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `[${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}]`;
  };

  const handleChange = (element: HTMLInputElement, index: number) => {
    if (isNaN(Number(element.value))) return false;

    const newOtp = [...otp];
    newOtp[index] = element.value;
    setOtp(newOtp);

    if (element.value !== '' && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>, index: number) => {
    if (e.key === 'Backspace' && !otp[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  return (
    <div>
      <div className="w-full flex flex-col gap-8 px-4">
        <div className="w-full max-w-md ">
          <h2 className="text-2xl font-bold text-black mb-2">Verify your number</h2>
          <p className="text-bodyText mb-8">
            We sent a 6-digit code to: <span className="font-semibold text-gray-800">{phone.slice(0, 4)} {phone.slice(4, 8)} *** ******</span>
          </p>

          <div className="flex gap-2 mb-8 justify-between">
            {otp.map((data, index) => (
              <input
                key={index}
                type="text"
                maxLength={1}
                // Refined ref callback to satisfy TS requirements
                ref={(el) => {
                  inputRefs.current[index] = el;
                }}
                value={data}
                onChange={(e) => handleChange(e.target as HTMLInputElement, index)}
                onKeyDown={(e) => handleKeyDown(e, index)}
                className="w-12 h-14 sm:w-14 sm:h-16 bg-white border border-transparent rounded-xl text-center text-xl font-semibold text-gray-800 shadow-sm focus:border-blue-400 focus:ring-2 focus:ring-blue-100 outline-none transition-all"
              />
            ))}
          </div>

          <div className="flex items-center justify-center gap-2 mb-10">
            <span className="text-black text-sm">Didn't receive the code?</span>
            <button 
              className="text-blue-600 font-medium text-sm hover:underline disabled:text-gray-400 disabled:no-underline"
              onClick={() => setTimer(300)}
              disabled={timer > 0}
            >
              Resend code
            </button>
            <div className="flex items-center bg-primary/15 gap-1 text-primary px-3 py-1 rounded-full text-sm">
              <Icon icon="lets-icons:clock" width={16} className="inline-block text-black" />
              <span className="!font-bold">{formatTime(timer)}</span>
            </div>
          </div>

          <Button
            className="w-full bg-[#C3D0FF] hover:bg-[#B3C0FF] text-white font-semibold py-4 rounded-3xl transition-colors text-lg disabled:opacity-50"
            onClick={() => setStep(3)}
            title="Verify Code"
            disabled={otp.some((digit) => digit === '')}
          />
        </div>
      </div>
    </div>
  );
};

export default PhoneVerification;