import React from 'react';
import { Icon } from '@iconify/react/dist/iconify.js';
import { Button } from './Button';

export interface LifecycleStep {
  id: number;
  title: string;
  description: string;
  completed: boolean;
  banner?: string;
  action?: {
    label: string;
    onClick: () => void;
  };
}

interface EscrowLifecycleProps {
  steps: LifecycleStep[];
}

const EscrowLifecycle: React.FC<EscrowLifecycleProps> = ({ steps }) => {
  return (
    <div className="w-full flex flex-col gap-4 mt-4 rounded-lg bg-gray-100 border border-gray-200 p-4 font-sans">
        <p className='!font-black'>Escrow Lifecycle</p>
        {/* Lifecycle Steps */}
        <div className=''>
          {steps.map((step, index) => (
              <div key={step.id} className="flex items-start gap-4">
                <div className={`relative self-stretch flex flex-col items-center justify-start shrink-0`}>
                  <div className='shrink-0'>
                    <Icon
                      icon="tabler:circle-dot-filled"
                      className={ `${step.completed ? ' text-primary' : 'text-gray-400 shrink-0 size-fit'}`}
                    />
                  </div>
                  {step.id < steps.length && <div className={`${steps[index + 1].completed ? 'border-primary' : 'border-gray-400'} border-1 relative h-full`}/>}
                </div>
                {/* content */}
                <div className='mt-[-2.5px] flex flex-col pb-8'>
                    <p className={`${step.completed ? 'text-black' : 'text-bodyText/50'}`} >{step.id}. {step.title}</p>
                    <p className={`${step.completed ? 'text-bodyText/50' : 'text-bodyText/30'}`} >{step.description}</p>
                    {step.banner && <div className='mt-2 p-2 rounded-lg bg-[#FFF9EB] border border-[#92400E] text-[#92400E] text-sm'><p>{step.banner}</p></div>}
                    {step.action && <Button disabled={!step.completed} onClick={step.action.onClick} className='py-2 !w-fit' title={step.action.label}/>}

                </div>
              </div>
          ))}  
        </div>     
    </div>
  );
};

export default EscrowLifecycle;