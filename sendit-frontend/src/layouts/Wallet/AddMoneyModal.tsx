import Modal from "../../components/Modal"
import { Button } from "../../components/Button"
import { useEffect, useState, useCallback } from "react";
import { Icon } from "@iconify/react/dist/iconify.js";

interface AddMoneyModalProps {
    isAddMoneyModalOpen: boolean;
    setIsAddMoneyModalOpen: (open: boolean) => void;
    accountDetails: {
        bank: string;
        account_number: string;
        account_name: string;
    };
}

const AddMoneyModal = ({ accountDetails, isAddMoneyModalOpen, setIsAddMoneyModalOpen }: AddMoneyModalProps) => {
    const [showCopyToast, setShowCopyToast] = useState(false);
    const [isSuccess, setIsSuccess] = useState(false);
    const [isSdkReady, setIsSdkReady] = useState(false);
    const [offer, setOffer] = useState<number>(2500);

    const accountNumber = accountDetails.account_number || "null";
    const accountName = accountDetails.account_name || "null";
    const bankName = accountDetails.bank || "null";

    // ✅ Bulletproof SDK Check: Looks for either known Interswitch global variable
    const checkSDK = useCallback(() => {
        const isReady = !!((window as any).InterswitchPay || (window as any).webpayCheckout);
        if (isReady) {
            setIsSdkReady(true);
        }
        return isReady;
    }, []);

    useEffect(() => {
        if (!isAddMoneyModalOpen) return;

        let intervalId: ReturnType<typeof setInterval>;

        // 1. Immediate check in case it's already in the DOM
        if (checkSDK()) return;

        // 2. Inject the script securely
        const scriptId = "isw-inline-checkout";
        if (!document.getElementById(scriptId)) {
            const script = document.createElement("script");
            script.id = scriptId;
            script.src = "https://qa.interswitchng.com/collections/w/pay";
            script.async = true;
            
            script.onload = () => {
                console.log("Interswitch Script Loaded to DOM");
                checkSDK();
            };
            
            script.onerror = () => {
                console.error("Failed to fetch Interswitch script. Check network or adblocker.");
            };
            
            document.body.appendChild(script);
        }

        // 3. Poll aggressively every 500ms just in case the onload fires late
        intervalId = setInterval(() => {
            if (checkSDK()) {
                clearInterval(intervalId);
            }
        }, 500);

        return () => {
            if (intervalId) clearInterval(intervalId);
        };
    }, [isAddMoneyModalOpen, checkSDK]);

    const handleQuicktellerPayment = () => {
        // Grab whichever global object successfully loaded
        const ISWPay = (window as any).InterswitchPay || (window as any).webpayCheckout;

        if (!ISWPay) {
            alert("Payment gateway is still connecting. Please check your internet.");
            return;
        }

        const paymentParameters = {
            merchant_code: "MX276479", // Sometimes expects merchantCode
            pay_item_id: "Default_Payable_MX276479", // Sometimes expects payItemID
            txn_ref: `TX-${Date.now()}`,
            amount: offer * 100, // Kobo
            currency: "566",
            site_redirect_url: window.location.href,
            cust_email: "deepbrain@gmail.com", // Replace with real user email
            onComplete: (response: any) => {
                console.log("Payment Response:", response);
                if (response?.resp === "00" || response?.resp === "7001") {
                    setIsSuccess(true);
                }
            },
            onClose: () => {
                console.log("Payment window closed by user");
            },
            mode: "TEST"
        };

        try {
            // Support both trigger methods depending on the script version
            if (typeof ISWPay.open === 'function') {
                ISWPay.open(paymentParameters);
            } else if (typeof ISWPay === 'function') {
                ISWPay(paymentParameters);
            } else {
                console.error("Unrecognized Interswitch method:", ISWPay);
                alert("Gateway error. Please refresh the page.");
            }
        } catch (error) {
            console.error("Quickteller Launch Error:", error);
            alert("Could not open payment window.");
        }
    };

    const handleCopy = () => {
        navigator.clipboard.writeText(accountNumber).then(() => {
            setShowCopyToast(true);
            setTimeout(() => setShowCopyToast(false), 2000);
        });
    };

    const handleCloseModal = () => {
        setIsAddMoneyModalOpen(false);
        setTimeout(() => setIsSuccess(false), 300);
    };

    return (
        <Modal isOpen={isAddMoneyModalOpen} onClose={handleCloseModal} >
            {showCopyToast && (
                <div className="fixed top-10 left-1/2 -translate-x-1/2 z-[9999] bg-black/80 text-white px-4 py-2 rounded-full text-sm font-bold flex items-center gap-2">
                    <Icon icon="solar:check-circle-bold" className="text-green-400" />
                    Account number copied!
                </div>
            )}

            {!isSuccess ? (
                <div className="flex flex-col items-center gap-4">
                    <h2 className="!font-black !text-lg text-black">Add Money to Wallet</h2>

                    <div className="flex flex-col items-center gap-4 w-full mt-4">
                        <p className="!font-black text-black">Enter Amount</p>
                        <div className="text-5xl font-black text-primary flex items-center justify-center">
                            <span className="!text-[25px] !font-extrabold mr-1">₦</span>
                            <input
                                type="number"
                                value={offer === 0 ? "" : offer}
                                onChange={(e) => setOffer(Number(e.target.value))}
                                className="!text-4xl !font-black bg-transparent border-none outline-none max-w-[150px] text-center text-primary"
                                placeholder="0"
                            />
                        </div>

                        <div className="flex border-b border-gray-200 pb-4 w-full overflow-x-auto no-scrollbar justify-between gap-2">
                            {[2000, 4000, 6000, 8000, 10000].map((price) => (
                                <button
                                    key={price}
                                    onClick={() => setOffer(price)}
                                    className={`px-3 py-2 shrink-0 text-xs rounded-xl font-bold transition-all ${offer === price ? "bg-primary text-white" : "bg-gray-50 text-gray-600 hover:bg-gray-100"}`}
                                >
                                    ₦{price.toLocaleString()}
                                </button>
                            ))}
                        </div>

                        <div className="flex items-center w-full flex-col gap-3">
                            <button
                                onClick={handleQuicktellerPayment}
                                className={`w-full flex items-center justify-between rounded-lg p-4 border border-primary/20 transition-colors ${!isSdkReady ? 'bg-gray-100 cursor-not-allowed opacity-70' : 'bg-primary/5 hover:bg-primary/10 cursor-pointer'}`}
                            >
                                <div className="flex items-center gap-3">
                                    <Icon icon="logos:quickteller-icon" width={24} className={!isSdkReady ? 'grayscale' : ''} />
                                    <p className="text-black font-bold">
                                        {!isSdkReady ? 'Initializing Secure Gateway...' : 'Pay with Quickteller'}
                                    </p>
                                </div>
                                {!isSdkReady ? (
                                    <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
                                ) : (
                                    <Icon icon="solar:alt-arrow-right-linear" />
                                )}
                            </button>

                            {/* Manual Transfer Details */}
                            <div className="w-full flex flex-col gap-1 rounded-lg p-4 px-3 border border-[#CFD8FC] bg-[#F5F7FE]">
                                <div className="flex gap-4 justify-between font-bold text-black">
                                    <p>{bankName}</p>
                                    <p>{accountNumber}</p>
                                </div>
                                <div className="flex gap-4 text-gray-500 justify-between items-center text-sm">
                                    <p>{accountName}</p>
                                    <p className="text-primary font-bold cursor-pointer hover:underline" onClick={handleCopy}>copy</p>
                                </div>
                            </div>

                            <Button title="I have sent the money" onClick={() => setIsSuccess(true)} />
                        </div>
                    </div>
                </div>
            ) : (
                <div className="flex flex-col items-center justify-center py-12 px-4 text-center">
                    <Icon icon="icon-park-solid:success" width={64} className="text-green-600 mb-6" />
                    <h2 className="text-2xl font-black text-black mb-2">Payment Received!</h2>
                    <p className="text-gray-500 mb-8">Verification in progress. Your balance will update shortly.</p>
                    <Button title="Back to Wallet" onClick={handleCloseModal} />
                </div>
            )}
        </Modal>
    );
}

export default AddMoneyModal;