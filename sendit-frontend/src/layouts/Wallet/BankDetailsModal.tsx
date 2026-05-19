import Modal from "../../components/Modal";
import { useState } from "react";
import { Icon } from "@iconify/react/dist/iconify.js";

interface BankDetailsModalProps {
    isModalOpen: boolean;
    setIsModalOpen: (open: boolean) => void;
    accountDetails: {
        bank: string;
        account_number: string;
        account_name: string;
    };
}

const BankDetailsModal = ({ accountDetails, isModalOpen, setIsModalOpen }: BankDetailsModalProps) => {
    const [showCopyToast, setShowCopyToast] = useState(false);
    
    // Account Information
    const accountInfo = {
        bankName: accountDetails.bank || "null",
        accountNumber: accountDetails.account_number || "null",
        accountName: accountDetails.account_name || "null"
    };

    const handleCopy = (text: string) => {
        navigator.clipboard.writeText(text).then(() => {
            setShowCopyToast(true);
            setTimeout(() => setShowCopyToast(false), 2000);
        });
    };

    const handleClose = () => {
        setIsModalOpen(false);
    };

    return (
        <Modal isOpen={isModalOpen} onClose={handleClose}>
            {/* Copy Notification Toast */}
            {showCopyToast && (
                <div className="fixed top-10 left-1/2 -translate-x-1/2 z-[9999] bg-black/80 text-white px-4 py-2 rounded-full text-sm font-bold flex items-center gap-2 animate-in fade-in slide-in-from-top-4 duration-300">
                    <Icon icon="solar:check-circle-bold" className="text-green-400" />
                    Copied to clipboard!
                </div>
            )}

            <div className="flex flex-col items-center gap-6 w-full py-2">
                <div className="flex flex-col items-center gap-2">
                    <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mb-2">
                        <Icon icon="streamline:bank-remix" className="text-primary" width={32} />
                    </div>
                    <h2 className="!font-black !text-xl text-black">Bank Account Details</h2>
                    <p className="text-bodyText/60 text-sm text-center px-4">
                        Use the details below to transfer funds into your Sendit wallet.
                    </p>
                </div>

                <div className="w-full flex flex-col gap-4">
                    {/* Bank Name Display */}
                    <div className="flex flex-col gap-1 w-full bg-gray-50 p-4 rounded-xl border border-gray-100">
                        <p className="!text-[10px] uppercase tracking-wider font-bold text-bodyText/50">Bank Name</p>
                        <p className="text-black font-black">{accountInfo.bankName}</p>
                    </div>

                    {/* Account Number Card */}
                    <div className="flex flex-col gap-1 w-full bg-primary/5 p-4 rounded-xl border border-primary/10 relative">
                        <p className="!text-[10px] uppercase tracking-wider font-bold text-bodyText/50">Account Number</p>
                        <div className="flex justify-between items-center">
                            <p className="text-black font-black text-2xl tabular-nums">{accountInfo.accountNumber}</p>
                            <button 
                                onClick={() => handleCopy(accountInfo.accountNumber)}
                                className="flex items-center gap-1 bg-primary text-white px-3 py-1.5 rounded-lg text-xs font-bold hover:bg-primary/90 transition-colors"
                            >
                                <Icon icon="solar:copy-bold" />
                                Copy
                            </button>
                        </div>
                    </div>

                    {/* Account Name Display */}
                    <div className="flex flex-col gap-1 w-full bg-gray-50 p-4 rounded-xl border border-gray-100">
                        <p className="!text-[10px] uppercase tracking-wider font-bold text-bodyText/50">Account Name</p>
                        <p className="text-black font-black">{accountInfo.accountName}</p>
                    </div>
                </div>

                <div className="flex items-start w-full gap-3 p-4 bg-[#F5F7FE] border border-[#CFD8FC] rounded-xl mt-2">
                    <Icon icon="carbon:information" width={20} className="shrink-0 text-primary mt-0.5" />
                    <p className="!text-xs leading-relaxed text-bodyText/80">
                        Funds transferred to this account will be automatically credited to your wallet balance within minutes.
                    </p>
                </div>

                <button 
                    onClick={handleClose}
                    className="w-full py-4 bg-gray-100 text-black font-black rounded-xl hover:bg-gray-200 transition-colors mt-2"
                >
                    Close
                </button>
            </div>
        </Modal>
    );
};

export default BankDetailsModal;