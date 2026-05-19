import { Button } from "../../components/Button";
import { useState, useRef } from "react";
import { Icon } from "@iconify/react/dist/iconify.js";

export const Step1 = ({setStep, setOfferType, setIsFragile, setOfferImage, setOfferDescription}: { setStep: (step: number) => void; setOfferType: (type: string) => void; setIsFragile: (isFragile: boolean) => void; setOfferImage: (image: File | null) => void; setOfferDescription: (description: string) => void }) => {
    const [description, setDescription] = useState<string>('');
    const [imagePreview, setImagePreview] = useState<string | null>(null);
    const [selected, setSelected] = useState("");
    const [fragile, setFragile] = useState<boolean | null>(null);
    
    const fileInputRef = useRef<HTMLInputElement>(null);

    // Boolean check: all fields except image must be filled
    const isComplete = selected !== "" && fragile !== null && description.trim() !== "";

    const handleBrowseClick = () => {
        fileInputRef.current?.click();
    };

    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (file) {
            setOfferImage(file);
            const reader = new FileReader();
            reader.onloadend = () => {
                setImagePreview(reader.result as string);
            };
            reader.readAsDataURL(file);
        }
    };

    const removeImage = (e: React.MouseEvent) => {
        e.stopPropagation();
        setImagePreview(null);
        setOfferImage(null);
        if (fileInputRef.current) fileInputRef.current.value = "";
    };

    return (
        <div className="flex flex-col gap-8 !text-black">
            <div className="flex flex-col">
                <h2>What are you sending?</h2>
                <p className="!text-bodyText/50 !font-bold !text-sm">Choose your package type and tell us a bit about it.</p>
            </div>
            {/* Package Type */}
            <div className="flex flex-col gap-2">
                <p className="!font-black">Package Type</p>
                <div className="flex w-full overflow-x-scroll gap-2 p-2">
                    <div onClick={() => {setSelected('Small'); setOfferType('Small')}}>
                        <PackageTypeCard selected={selected === "Small"} title="Small" icon="mingcute:package-2-fill" details="Can fit inside a shoebox"/>
                    </div>
                    <div onClick={() => {setSelected('Medium'); setOfferType('Medium')}}>
                        <PackageTypeCard selected={selected === "Medium"} title="Medium" icon="icon-park-solid:backpack" details="Can fit inside a backpack"/>
                    </div>
                    <div onClick={() => {setSelected('Large'); setOfferType('Large')}}>
                        <PackageTypeCard selected={selected === "Large"} title="Large" icon="material-symbols:travel-luggage-and-bags-rounded" details="Can fit inside a travelling box"/>
                    </div>
                </div>
            </div>
            {/* Fragile? */}
            <div className="flex flex-col gap-2">
                <p className="!font-black">Is this item fragile?</p>
                <div className="flex w-full justify-between overflow-x-scroll gap-2 ">
                    <div onClick={() => {setFragile(true); setIsFragile(true)}} className="cursor-pointer flex justify-between rounded-lg p-4 w-[48%] bg-white border-1 border-gray-200">
                        <p className="!font-black">Yes</p>
                        {fragile === true ? <Icon icon="carbon:circle-filled" width={20} className='text-primary'/> : <div className='w-5 h-5 rounded-full border-1 border-gray-400'/>}
                    </div>
                    <div onClick={() => {setFragile(false); setIsFragile(false)}} className="cursor-pointer flex justify-between rounded-lg p-4  w-[48%] bg-white border-1 border-gray-200">
                        <p className="!font-black">No</p>
                        {fragile === false ? <Icon icon="carbon:circle-filled" width={20} className='text-primary'/> : <div className='w-5 h-5 rounded-full border-1 border-gray-400'/>}
                    </div>

                </div>
            </div>
            {/* Image Upload */}
            <div className="flex flex-col gap-2">
                <p className="!font-black">Upload Image (Optional)</p>
                
                <input 
                    type="file" 
                    ref={fileInputRef} 
                    onChange={handleFileChange} 
                    accept="image/*" 
                    className="hidden" 
                />

                <div 
                    onClick={handleBrowseClick}
                    className="bg-gray-100 rounded-2xl flex flex-col items-center justify-center p-8 border border-gray-200 min-h-[160px] cursor-pointer hover:bg-gray-200 transition-all"
                >
                    {imagePreview ? (
                        <div className="relative w-full flex justify-center">
                            <img src={imagePreview} alt="Preview" className="h-32 object-cover rounded-xl" />
                            <button 
                                onClick={removeImage}
                                className="absolute -top-2 right-[20%] bg-red-500 text-white p-1 rounded-full shadow-md hover:bg-red-600"
                            >
                                <Icon icon="material-symbols:close" width={16} />
                            </button>
                        </div>
                    ) : (
                        <>
                            <div className="mb-4">
                                <Icon icon="ion:image" width={48} className="text-gray-400" />
                            </div>
                            <p className="text-sm font-black mb-1">Upload Package Image</p>
                            <button className="text-sm text-blue-600 font-medium hover:text-blue-700 hover:underline">
                                Browse Images
                            </button>
                        </>
                    )}
                </div>
            </div>

            {/* Description Input */}
            <div className="flex flex-col gap-2">
                <p className="!font-black">Package Description</p>
                <textarea
                    value={description}
                    onChange={(e) => {
                        setDescription(e.target.value);
                        setOfferDescription(e.target.value);
                    }}
                    placeholder="e.g. Birthday gift, sealed documents, phone charger..."
                    className="w-full h-32 p-4 bg-white border border-gray-200 rounded-2xl resize-none text-sm  outline-none focus:ring-1 focus:ring-primary"
                />
            </div>
            {/* Continue Button */}
            <Button
                title="Continue"
                onClick={() => setStep(2)}
                disabled={!isComplete}
                className={!isComplete ? "opacity-50 cursor-not-allowed" : ""}
            />
        </div>
    );
};

const PackageTypeCard = ({ title, icon, details, selected }: { title: string, icon: string, details: string, selected: boolean }) => {
    return (
        <div className={`${selected && 'ring-2 ring-primary'} border-1 border-gray-100 rounded-xl p-4 hover:ring-2 hover:ring-primary shrink-0 w-[150px] shadow-xs cursor-pointer flex flex-col items-start bg-gray-50 text-black/80'`}>
            <Icon icon={icon} width={26} className='text-primary'/>
            <p className="!font-black mt-1">{title}</p>
            <p className="text-left !text-[12px]  !text-black/60">{details}</p>
        </div>
    )
}