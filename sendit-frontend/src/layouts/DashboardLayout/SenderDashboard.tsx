import { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Icon } from "@iconify/react/dist/iconify.js";
import api from "../../api/axios"; // Adjust path to your axios instance
import EscrowLifecycle from "../../components/EscrowLifecycle";
import { type LifecycleStep } from "../../components/EscrowLifecycle";
import GradientBackground from "../../components/GradientBackground";

const SenderDashboard = () => {
    const navigate = useNavigate();
    const otherUserId = useParams().senderId;
    const [offer, setOffer] = useState<any>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isChatLoading, setIsChatLoading] = useState(false); // New loading state

    const handleChat = async () => {
        try {
            setIsChatLoading(true); // Start loading
            const participantId = offer?.sender?.id;
            const offerId = offer?.id; 

            if (!participantId || !offerId) {
                console.error("Missing required data");
                return;
            }

            const response = await api.post('/chats/', {
                participant_id: participantId,
                offer_id: offerId 
            });

            const chatRoomId = response.data.id;
            navigate(`/chats/${chatRoomId}`);
        } catch (error) {
            console.error("Error initiating chat:", error);
        } finally {
            setIsChatLoading(false); // Stop loading
        }
    };

    useEffect(() => {
        const fetchOfferDetails = async () => {
            try {
                setIsLoading(true);
                const response = await api.get(`/offers/${otherUserId}/`);
                setOffer(response.data.data);
            } catch (error) {
                console.error("Error fetching offer:", error);
            } finally {
                setIsLoading(false);
            }
        };

        if (otherUserId) fetchOfferDetails();
    }, [otherUserId]);

    const lifecycleData: LifecycleStep[] = [
        {
          id: 1,
          title: "Carrier Accepted",
          description: "Awaiting sender to fund escrow",
          completed: offer?.status !== "posted",
          banner: "Sender must fund escrow before you do pickup. They've been notified",
        },
        {
          id: 2,
          title: "Escrow Activated",
          description: "Funds held by Sendit x Interswitch",
          completed: false
        },
        {
          id: 3,
          title: "Picked Up Package",
          description: "In carrier's hands - money still held",
          completed: false,
          action: {
            label: "Package picked Up",
            onClick: () => console.log("Picked up!")
          }
        },
        {
          id: 4,
          title: "On your way",
          description: "Carrier heading to destination",
          completed: false,
        },
        {
          id: 5,
          title: "Delivered",
          description: "Receiver, has received the package",
          completed: false,
        },
        {
          id: 6,
          title: "Dispute Window (12-24 hr)",
          description: "Final verification period",
          completed: false,
        },
      ];

    if (isLoading) {
        return (
            <div className="h-screen w-full flex flex-col items-center justify-center bg-white">
                <Icon icon="line-md:loading-twotone-loop" width={48} className="text-primary" />
                <p className="mt-4 text-sm text-gray-500 font-medium">Loading Dashboard...</p>
            </div>
        );
    }

    if (!offer) return <div className="p-10 text-center">Offer not found.</div>;

    const from = offer.location.pickup_location_detail.city;
    const to = offer.location.delivery_location_detail.city;
    const name = `${offer.sender.first_name} ${offer.sender.last_name}`;
    const amount = offer.pricing.total_price;
    const platformFee = offer.pricing.platform_fee;
    const earnings = offer.pricing.base_price;
    const size = offer.package_type;
    const properties = offer.is_fragile ? ["Fragile"] : [];
    const refCode = offer.code;
    const img = `https://ui-avatars.com/api/?name=${offer.sender.first_name}+${offer.sender.last_name}&background=random`;
    const userStr = localStorage.getItem('user');
    const userData = JSON.parse(userStr || '{}');
    const currentUserId = userData?.id || userData?.user?.id;
    const otherUser = offer.sender.id === currentUserId ? 'Carrier' : 'Sender';

    return (
        <div className='bg-[#FBFBFBB2] p-4 flex flex-col gap-8 min-h-screen'>
            <div className={` w-full flex items-center gap-4 `}>
                <button onClick={() => navigate(-1)} className="p-2 bg-white rounded-[50%] hover:bg-gray-100 transition-colors shadow-sm">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M15 18L9 12L15 6" stroke="black" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
                </button>
                <h2 className="!text-xl font-bold">{`${otherUser} Dashboard`}</h2>
            </div>

            <div className='flex flex-col gap-2'>
                <p className="text-xs font-bold text-gray-400 uppercase tracking-wider">{otherUser}</p>
                <div className='flex items-start gap-2 pt-2'>
                    <div className='border-1 border-primary size-12 rounded-lg bg-gray-300 shrink-0 flex items-center justify-center text-white overflow-hidden'>
                        <img src={img} alt={name} className='w-full h-full object-cover' />
                    </div>
                    <div className='flex flex-col flex-1'>
                        <p className='!text-sm !font-bold'>{name}</p>
                        <div className='flex items-center gap-1 mt-1'>
                            <div className='flex justify-center items-center gap-[1px] bg-gray-100 px-2 py-0.5 rounded-full border border-gray-200'>
                                <Icon icon="mdi:star" width={12} className="text-black"/>
                                <p className='!text-[10px] !text-black '>4.5</p>
                            </div>
                            {offer.sender.profile.is_verified && (
                                <div className='flex justify-center items-center gap-[1px] bg-gray-100 px-2 py-0.5 rounded-full border border-gray-200'>
                                    <Icon icon="codicon:verified-filled" width={12} className="text-primary"/>
                                    <p className='!text-[10px] !font-bold !text-gray-500'>Verified</p>
                                </div>
                            )}
                        </div>
                    </div>
                    <div className='flex gap-2 text-black'>
                        <button 
                            disabled={isChatLoading}
                            onClick={handleChat} 
                            className=' p-2 rounded-[50%] bg-white shadow-sm border border-gray-100 disabled:opacity-50'
                        >
                            {isChatLoading ? (
                                <Icon icon="line-md:loading-twotone-loop" width={20} />
                            ) : (
                                <Icon icon="ant-design:message-filled" width={20} className="cursor-pointer"/>
                            )}
                        </button>
                        <div className='p-2 rounded-[50%] bg-white shadow-sm border border-gray-100'>
                            <Icon icon="basil:phone-solid" width={20} className="cursor-pointer" />
                        </div>
                    </div>
                </div>    

                <div className="mt-4">
                    <GradientBackground>
                        <div className='flex flex-col gap-6 rounded-lg !text-white'>
                            <div className='flex justify-between items-center'>
                                <p className="font-medium">Escrow Status</p>
                                <p className='!text-xs !font-bold rounded-full py-1 px-3 bg-white/20 '>
                                    {offer.status === 'posted' ? 'Awaiting Funding' : offer.status}
                                </p>
                            </div>
                            <p className='!text-4xl !font-bold'>₦{offer.status === 'posted' ? '0' : amount.toLocaleString()}</p>
                            <p className='!text-sm opacity-90'>
                                {offer.status === 'posted' ? 'Sender has not funded escrow yet' : 'Funds secured in Escrow'}
                            </p>
                        </div>
                    </GradientBackground>
                </div>

                <div className='mt-4 rounded-lg flex bg-white border-1 border-gray-100 p-4 flex-col gap-4 shadow-sm'>
                    <p className='!font-black text-sm uppercase text-gray-400'>Package Details</p>
                    <div className='flex'>
                        <div className='p-2 rounded-lg bg-primary/10 flex justify-center items-center mr-3 h-fit shrink-0'>
                            <Icon icon="fluent:box-32-filled" width={24} className="text-primary inline-block shrink-0"/>
                        </div>
                        <div className='flex flex-col'>
                            <div className='flex items-center flex-wrap gap-1'>
                                <p className='!font-bold capitalize'>{size} Box </p>
                                {properties.map((property) => (
                                    <div key={property} className='flex items-center'>
                                        <Icon icon="lucide:dot" width={20} className="text-gray-400"/>
                                        <p className="!font-bold text-red-500">{property}</p>
                                    </div>
                                ))}
                            </div>
                            <p className='!text-xs text-bodyText/60 font-medium'>Ref #{refCode}</p>
                        </div>
                    </div>
                    <div className='flex justify-between pt-3 border-t border-gray-50'>
                        <p className='text-xs text-gray-400 font-bold uppercase'>Pick-up</p>
                        <p className='text-xs font-bold text-black'>📍 {from}</p>
                    </div>
                    <div className='flex justify-between pt-3 border-t border-gray-50'>
                        <p className='text-xs text-gray-400 font-bold uppercase'>Destination</p>
                        <p className='text-xs font-bold text-black'>📍 {to}</p>
                    </div>
                </div>

                <div className="mt-4">
                    <EscrowLifecycle steps={lifecycleData} />
                </div>

                <div className='mt-4 rounded-lg flex bg-white border-1 border-gray-100 p-4 flex-col gap-4 shadow-sm'>
                    <p className='!font-black text-sm uppercase text-gray-400'>Payout Breakdown</p>
                    <div className='flex justify-between items-center'>
                        <p className='text-sm text-gray-500'>Escrow (Sender Paid)</p>
                        <p className='text-sm font-bold text-black'>₦{amount.toLocaleString()}</p>
                    </div>
                    <div className='flex justify-between items-center'>
                        <p className='text-sm text-gray-500'>Platform fee</p>
                        <p className='text-sm font-bold text-red-500'>-₦{platformFee.toLocaleString()}</p>
                    </div>
                    <div className='flex justify-between items-center pt-3 border-t-2 border-gray-100 border-dotted'>
                        <p className='font-bold text-black'>You Earn</p>
                        <p className='font-black text-xl text-primary'>₦{earnings.toLocaleString()}</p>
                    </div>
                </div>

                {offer.status === 'posted' && (
                    <div className='mt-6 p-4 rounded-xl flex justify-center items-center bg-amber-50 border border-amber-200 text-amber-800 animate-pulse'>
                        <p className="font-bold text-center">Waiting for sender to fund escrow</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default SenderDashboard;