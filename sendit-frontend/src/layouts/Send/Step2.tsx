import { Button } from "../../components/Button";
import { useState,  useMemo } from "react";
import { Icon } from "@iconify/react/dist/iconify.js";
import Select from "react-select";
// Correct library import
import { states, lgas } from "nigerian-states-and-lgas";

export const Step2 = ({setStep, setCity, setStreet, setTime, setDestinationCity, setDestinationStreet, setReceiverName, setReceiverContact}: { setStep: (step: number) => void; setCity: (city: string) => void; setStreet: (street: string) => void; setTime: (time: string) => void; setDestinationCity: (city: string) => void; setDestinationStreet: (street: string) => void; setReceiverName: (name: string) => void; setReceiverContact: (contact: string) => void }) => {    
    // Sender States
    const [city, setLocalCity] = useState<any>(null);
    const [street, setLocalStreet] = useState<string>('');
    const [time, setLocalTime] = useState<string>('');

    // Receiver/Delivery States
    const [destinationCity, setLocalDestinationCity] = useState<any>(null);
    const [destinationStreet, setLocalDestinationStreet] = useState<string>('');
    const [receiverName, setLocalReceiverName] = useState<string>('');
    const [receiverContact, setLocalReceiverContact] = useState<string>('');

    const [pickUpLocationOpen, setPickUpLocationOpen] = useState<boolean>(true);
    const [dropOffLocationOpen, setDropOffLocationOpen] = useState<boolean>(true);

    // Generate the list of all Nigerian Cities/Areas
    const nigerianOptions = useMemo(() => {
        return states().flatMap(state => {
            const stateLgas = lgas(state);
            return stateLgas?.map(lga => ({
                value: `${lga}, ${state}`,
                label: `${lga}, ${state}`
            }));
        });
    }, []);

    // Reusable phone handler
    const handlePhoneChange = (val: string, setterLocal: (v: string) => void, setterProp?: (v: string) => void) => {
        const onlyNums = val.replace(/\D/g, "");
        if (onlyNums.length <= 11) {
            setterLocal(onlyNums);
            if (setterProp) setterProp(onlyNums);
        }
    };

    // Validation Check: Now includes time and both contacts
    const isFormValid = 
        city && street && time && 
        destinationCity && destinationStreet && receiverContact.length === 11 && receiverName;

    const customSelectStyles = {
        control: (provided: any) => ({
            ...provided,
            borderRadius: '0.5rem',
            padding: '4px',
            border: '1px solid #D1D5DB',
            backgroundColor: 'white',
            boxShadow: 'none',
            '&:hover': { border: '1px solid #D1D5DB' }
        }),
        menu: (provided: any) => ({ ...provided, zIndex: 50 }),
        option: (provided: any, state: any) => ({
            ...provided,
            backgroundColor: state.isSelected ? '#001F72' : state.isFocused ? '#F3F4F6' : 'white',
            color: state.isSelected ? 'white' : 'black',
            fontSize: '14px'
        })
    };

    return (
        <div className="flex flex-col gap-8 !text-black">
            <div className="flex flex-col">
                <h2>Pickup & delivery</h2>
                <p className="!text-bodyText/50 !font-bold !text-sm">Where should the traveler collect and drop off your package?</p>
            </div>
            
            <div className="flex flex-col gap-4">
                {/* Pickup Location */}
                <div className="flex flex-col w-full bg-gray-100 border-1 border-gray-200 rounded-xl gap-2 p-4">
                    <div onClick={() => setPickUpLocationOpen(!pickUpLocationOpen)} className="flex gap-4 justify-between items-center cursor-pointer">
                        <div className="flex gap-2 justify-center items-center">
                            <Icon icon="boxicons:location-pin-filled" width={26} className='text-black'/>
                            <h2 className="!font-black !text-xl">Pickup Location</h2>
                        </div>
                        {pickUpLocationOpen ? <Icon icon="ri:arrow-up-s-line" width={28} className='text-black'/> : <Icon icon="ri:arrow-down-s-line" width={28} className='text-black'/>}
                    </div>
                    
                    {pickUpLocationOpen && <div className="flex flex-col gap-2 mt-2">
                        <p className="!font-black mt-4">City/Area</p>
                        <Select
                            options={nigerianOptions}
                            styles={customSelectStyles}
                            placeholder="Search pickup area..."
                            value={city}
                            onChange={(option) => { setLocalCity(option); setCity(option?.value || ""); }}
                        />

                        <p className="!font-black mt-4">Street/Landmark</p>
                        <input 
                            type="text" 
                            placeholder="e.g. Near GTBank, Opebi Road" 
                            value={street} 
                            onChange={(e) => {setLocalStreet(e.target.value); setStreet(e.target.value)}} 
                            className="w-full border-1 border-gray-300 bg-white rounded-lg p-4 outline-none focus:ring-1 focus:ring-primary"
                        />
                        
                        <p className="!font-black mt-4">Pickup Time</p>
                        <input 
                            type="time" 
                            value={time} 
                            onChange={(e) => {setLocalTime(e.target.value); setTime(e.target.value)}} 
                            className="w-full border-1 border-gray-300 bg-white rounded-lg p-4 outline-none focus:ring-1 focus:ring-primary"
                        />
                    </div>}
                </div>

                {/* Delivery Location */}
                <div className="flex flex-col w-full bg-gray-100 border-1 border-gray-200 rounded-xl gap-2 p-4">
                    <div onClick={() => setDropOffLocationOpen(!dropOffLocationOpen)} className="flex gap-4 justify-between items-center cursor-pointer">
                        <div className="flex gap-2 justify-center items-center">
                            <Icon icon="material-symbols:local-shipping" width={26} className='text-black'/>
                            <h2 className="!font-black !text-xl">Delivery Location</h2>
                        </div>
                        {dropOffLocationOpen ? <Icon icon="ri:arrow-up-s-line" width={28} className='text-black'/> : <Icon icon="ri:arrow-down-s-line" width={28} className='text-black'/>}
                    </div>
                    
                    {dropOffLocationOpen && <div className="flex flex-col gap-2 mt-2">
                        <p className="!font-black mt-4">City/Area</p>
                        <Select
                            options={nigerianOptions}
                            styles={customSelectStyles}
                            placeholder="Search delivery area..."
                            value={destinationCity}
                            onChange={(option) => {
                                setLocalDestinationCity(option);
                                setDestinationCity(option?.value || "");
                            }}
                        />

                        <p className="!font-black mt-4">Street/Landmark</p>
                        <input 
                            type="text" 
                            placeholder="Receiver's address or landmark" 
                            value={destinationStreet} 
                            onChange={(e) => {setLocalDestinationStreet(e.target.value); setDestinationStreet(e.target.value)}} 
                            className="w-full border-1 border-gray-300 bg-white rounded-lg p-4 outline-none focus:ring-1 focus:ring-primary"
                        />
                        
                        <p className="!font-black mt-4">Receiver's Name</p>
                        <input 
                            type="text" 
                            placeholder="Enter full name" 
                            value={receiverName} 
                            onChange={(e) => {setLocalReceiverName(e.target.value); setReceiverName(e.target.value)}} 
                            className="w-full border-1 border-gray-300 bg-white rounded-lg p-4 outline-none focus:ring-1 focus:ring-primary"
                        />
                        
                        <p className="!font-black mt-4">Receiver’s Contact</p>
                        <div className="relative">
                            <input 
                                type="tel" 
                                placeholder="08012345678" 
                                value={receiverContact} 
                                onChange={(e) => handlePhoneChange(e.target.value, setLocalReceiverContact, setReceiverContact)} 
                                className="w-full border-1 border-gray-300 bg-white rounded-lg p-4 outline-none focus:ring-1 focus:ring-primary"
                            />
                            <p className={`absolute right-4 top-4 text-[10px] font-bold ${receiverContact.length === 11 ? 'text-green-500' : 'text-gray-400'}`}>
                                {receiverContact.length}/11
                            </p>
                        </div>
                    </div>}
                </div>
            </div>
            
            <Button 
                title="Continue" 
                onClick={() => setStep(3)} 
                disabled={!isFormValid}
                className={!isFormValid ? "opacity-50" : ""}
            />
        </div>
    );
};