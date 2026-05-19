import Modal from "../../components/Modal"
import { Button } from "../../components/Button"
import {useState } from "react";
import { Icon } from "@iconify/react/dist/iconify.js";
import Select from "react-select";

const NIGERIAN_BANKS = [
    { value: "044", label: "Access Bank" },
    { value: "050", label: "Ecobank Nigeria" },
    { value: "070", label: "Fidelity Bank" },
    { value: "011", label: "First Bank of Nigeria" },
    { value: "058", label: "GTBank" },
    { value: "030", label: "Heritage Bank" },
    { value: "301", label: "Jaiz Bank" },
    { value: "082", label: "Keystone Bank" },
    { value: "014", label: "Kuda Bank" },
    { value: "50211", label: "Moniepoint MFB" },
    { value: "999", label: "OPay" },
    { value: "076", label: "Polaris Bank" },
    { value: "221", label: "Stanbic IBTC Bank" },
    { value: "068", label: "Standard Chartered Bank" },
    { value: "232", label: "Sterling Bank" },
    { value: "100", label: "Suntrust Bank" },
    { value: "032", label: "Union Bank of Nigeria" },
    { value: "033", label: "United Bank for Africa (UBA)" },
    { value: "215", label: "Unity Bank" },
    { value: "035", label: "Wema Bank" },
    { value: "057", label: "Zenith Bank" },
].sort((a, b) => a.label.localeCompare(b.label));

interface WithdrawMoneyModalProps {
    isWithdrawMoneyModalOpen: boolean;
    setIsWithdrawMoneyModalOpen: (open: boolean) => void;
    walletBalance: number;
}

const WithdrawMoneyModal = ({ walletBalance, isWithdrawMoneyModalOpen, setIsWithdrawMoneyModalOpen }: WithdrawMoneyModalProps) => {
    const [isSuccess, setIsSuccess] = useState(false);
    const [offer, setOffer] = useState<number>(2500);
    const presets = [2000, 4000, 6000, 8000, 10000];
    const [accountNumber, setAccountNumber] = useState<string>('');
    const [receiverName, setReceiverName] = useState<string>('');
    const [selectedBank, setSelectedBank] = useState<any>(null);

    const handleCloseModal = () => {
        setIsWithdrawMoneyModalOpen(false);
        setTimeout(() => setIsSuccess(false), 300);
    };

    const updateOffer = (val: number) => {
        // Prevents negative values and caps at the wallet balance
        const newVal = Math.min(walletBalance, Math.max(0, val));
        setOffer(newVal);
    };

    const customSelectStyles = {
        control: (base: any) => ({
            ...base,
            borderRadius: '0.5rem',
            padding: '2px',
            borderColor: '#D1D5DB',
            boxShadow: 'none',
            '&:hover': {
                borderColor: '#335CF4',
            }
        }),
    };

    return (
        <Modal isOpen={isWithdrawMoneyModalOpen} onClose={handleCloseModal} >
            {!isSuccess ? (
                <div className="flex flex-col items-center gap-4">
                    <h2 className="!font-black !text-lg text-center"> Withdraw Money from Wallet</h2>
                    <div className="flex flex-col items-center gap-4 w-full mt-4">
                        <p className="!font-black">Enter Amount</p>
                        <div className="flex flex-col gap-2 w-full ">
                            <div className="flex flex-col items-center w-full gap-8 bg-white rounded-xl">
                                <div className="flex items-center gap-4">
                                    <div className="text-center">
                                        <div className="text-5xl font-black text-primary flex items-center justify-center">
                                            <span className="!text-[25px] !font-extrabold mr-1">₦</span>
                                            <h1>
                                                <input
                                                    type="number"
                                                    value={offer === 0 ? "" : offer}
                                                    onChange={(e) => updateOffer(Number(e.target.value))}
                                                    className="!text-4xl !font-black bg-transparent border-none outline-none max-w-[200px] text-center "
                                                    placeholder="0"
                                                />
                                            </h1>
                                        </div>
                                        {offer > walletBalance && (
                                            <p className="text-red-500 text-xs font-bold mt-2">Insufficient balance (Max: ₦{walletBalance.toLocaleString()})</p>
                                        )}
                                    </div>
                                </div>

                                <div className="flex border-b-1 border-gray-200 pb-4 w-full overflow-x-scroll justify-between gap-2 !font-bold !text-bodyText/80">
                                    {presets.map((price) => (
                                        <button
                                            key={price}
                                            disabled={price > walletBalance}
                                            onClick={() => updateOffer(price)}
                                            className={`px-2 py-2 !text-xs rounded-xl font-bold transition-all ${offer === price ? "bg-primary text-white" : price > walletBalance ? "bg-gray-100 text-gray-300 cursor-not-allowed" : "bg-gray-50 hover:bg-gray-100"}`}
                                        >
                                            ₦{price.toLocaleString()}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </div>
                        <div className="flex items-start w-full flex-col gap-3 justify-between">
                            <p className="!font-black mt-4">Account Number</p>
                            <input 
                                type="text" 
                                placeholder="Enter account number" 
                                value={accountNumber} 
                                onChange={(e) => setAccountNumber(e.target.value)} 
                                className="w-full border-1 border-gray-300 bg-white rounded-lg p-2 px-4 outline-none focus:ring-1 focus:ring-primary"
                            />

                            <p className="!font-black mt-4">Bank Name</p>
                            <div className="w-full">
                                <Select
                                    options={NIGERIAN_BANKS}
                                    value={selectedBank}
                                    onChange={(option) => setSelectedBank(option)}
                                    placeholder="Select your bank"
                                    styles={customSelectStyles}
                                    className="react-select-container"
                                    classNamePrefix="react-select"
                                />
                            </div>

                            <p className="!font-black mt-2">Account Name</p>
                            <input 
                                type="text" 
                                placeholder="Enter account name" 
                                value={receiverName} 
                                onChange={(e) => setReceiverName(e.target.value)} 
                                className="w-full border-1 border-gray-300 bg-white rounded-lg p-2 px-4 outline-none focus:ring-1 focus:ring-primary"
                            />
                            
                            <Button 
                                className="mt-4" 
                                disabled={offer <= 0 || offer > walletBalance || accountNumber === "" || receiverName === "" || !selectedBank} 
                                title="Withdraw Money" 
                                onClick={() => setIsSuccess(true)} 
                            />
                        </div>
                    </div>
                </div>
            ) : (
                <div className="flex flex-col items-center justify-center py-12 px-4 text-center animate-in zoom-in duration-300">
                    <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mb-6">
                        <Icon icon="icon-park-solid:success" width={48} className="text-green-600" />
                    </div>
                    <h2 className="text-2xl font-black text-black mb-8">Withdrawal Received!</h2>
                    <Button title="Back to Wallet" onClick={handleCloseModal} />
                </div>
            )}
        </Modal>
    )
}

export default WithdrawMoneyModal;