import Modal from "../../components/Modal";
import { useState } from "react";
import { Icon } from "@iconify/react/dist/iconify.js";
import { escrowImage } from "../../assets/images";
import GradientBackground from "../../components/GradientBackground";
import { Button } from "../../components/Button";

interface FundEscrowModalProps {
    escrowId: number | null;
    amount: number | null;
    isModalOpen: boolean;
    setIsModalOpen: (open: boolean) => void;

}

const FundEscrowModal = ({  escrowId, amountToFund, isModalOpen, setIsModalOpen }: FundEscrowModalProps & { escrowId: number | null; amountToFund: number | null }) => {
    const [selectedPaymentMethod, setSelectedPaymentMethod] = useState<string | null>(null);
    const handleClose = () => {
        setIsModalOpen(false);
    };

    return (
        <Modal isOpen={isModalOpen} onClose={handleClose}>

            <div className="flex text-bodyText flex-col justify-center items-center gap-4 w-full py-2 mt-4">
                <img src={escrowImage} alt="Escrow Funding" className="w-24 h-24 mb-2" />
                <h2>Fund Escrow</h2>
                <p className="!text-sm text-center">A carrier accepted your offer! Pay into escrow - fund are held safely by Sendit × Interswitch</p>
                <GradientBackground>
                    <div className=' flex flex-col items-center  rounded-lg !text-white'>
                        <p>Total to lock in escrow</p>
                        <h1 >₦{amountToFund?.toLocaleString()}</h1>
                        <p className="!text-sm">₦{amountToFund?.toLocaleString()} offer + ₦350 platform fee (10%)</p>

                    </div>
                </GradientBackground>
                <div className="w-full  flex justify-between gap-4">
                    <div className="w-full" onClick={() => setSelectedPaymentMethod("Wallet")}>
                        <PaymentOption selected={selectedPaymentMethod === "Wallet"} name="Wallet" icon="iconoir:wallet-solid" onSelect={() => {}} />
                    </div>
                    <div className="w-full" onClick={() => setSelectedPaymentMethod("Transfer")}>
                        <PaymentOption selected={selectedPaymentMethod === "Transfer"} name="Transfer" icon="mdi:bank-transfer" onSelect={() => {}} />
                    </div>
                </div>

                <div className="w-full flex flex-col gap-4 items-center rounded-lg p-4 px-3 border border-[#CFD8FC] bg-[#F5F7FE]">
                    <p className="!text-sm">Debit ₦{amountToFund?.toLocaleString()} from your Sendit Wallet and lock in escrow</p>
                    <Button title={`Fund escrow - $${amountToFund?.toLocaleString()}`} />
                </div>
            </div>
        </Modal>
    );
};

const PaymentOption = ({ name, icon, onSelect, selected }: { name: string; icon: string; onSelect: (price: number) => void; selected: boolean }) => (
    <button onClick={() => onSelect(2500)} className={`w-full  rounded-lg bg-gray-200 flex flex-col justify-center items-center gap-2 rounded-lg p-2 px-4 transition-colors ${selected ? 'bg-[#F0F3FE] text-primary border-2 border-primary' : ''}`}>
        <Icon icon={icon} width={28} className="text-primary" />
        <span className="!text-sm font-bold">{name}</span>
    </button>
);

export default FundEscrowModal;