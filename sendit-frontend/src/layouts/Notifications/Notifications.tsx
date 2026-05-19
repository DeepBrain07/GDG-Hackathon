import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import '../SignInLayout/style.css'
import DashboardLayout from '../DashboardLayout/DashboardLayout';
import { Icon } from '@iconify/react/dist/iconify.js';
import { Button } from '../../components/Button';
import FundEscrowModal from '../Wallet/FundEscrowModal';
import api from '../../api/axios';
import toast, { Toaster } from 'react-hot-toast';

const Notifications = () => {
  const navigate = useNavigate();
  const [proposals, setProposals] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
    const userStr = localStorage.getItem('user');
    const userData = JSON.parse(userStr || '{}');
    
    const currentUserId = userData?.id || userData?.user?.id;

  useEffect(() => {
    const fetchNotifications = async () => {
      try {
        setLoading(true);
        const response = await api.get('/offers/proposals');
        const data = response.data.results || [];
        console.log(data)
        setProposals(data);
      } catch (error) {
        console.error("Error fetching notifications:", error);
        toast.error("Failed to load notifications");
      } finally {
        setLoading(false);
      }
    };

    fetchNotifications();
  }, []);

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <DashboardLayout>
      <Toaster position="top-center" reverseOrder={false} />
      
      <div className='bg-[#FBFBFBB2] p-4 flex flex-col gap-8'>
        <div className={` w-full flex items-center gap-4   `}>
          <button onClick={() => navigate('/home')} className="p-2 bg-white rounded-[50%] hover:bg-gray-100 transition-colors">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M15 18L9 12L15 6" stroke="black" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
          <h2 className="!text-xl">Notifications</h2>
        </div>
      </div>

      <div className='p-2 flex flex-col w-full'>
        {loading ? (
          <div className="flex justify-center py-10">
            <Icon icon="line-md:loading-twotone-loop" width={40} className="text-primary" />
          </div>
        ) : proposals.length > 0 ? (
          proposals.map((proposal) => {
            // FIX: Corrected the conditional logic and wrapping
            const shouldShow = (proposal.carrier === currentUserId && proposal.status === "accepted") || (proposal.carrier !== currentUserId);
            
            return shouldShow ? (
              <NotificationCard 
                key={proposal.id}
                proposal={proposal} 
                title="New Bid"
                time={formatTime(proposal.created_at)} 
                amount={proposal.price} 
                carrierName={proposal.carrier_name}
                to="Check details" 
                avatar={proposal.carrier_avatar?.file_url}
                status={proposal.status}
                carrierId={proposal.carrier}
                offerId={proposal.offer} 
              />
            ) : null;
          })
        ) : (
          <div className="text-center py-10 text-gray-500">No notifications yet</div>
        )}
      </div>
    </DashboardLayout>
  );
};

const NotificationCard = ({ proposal, offerId, carrierId, status, title, time, amount, carrierName, avatar }: { proposal: any; offerId: string; carrierId: number; status: string; title: string; time: string; amount: string; carrierName: string; to: string; avatar: string; }) => {
    const [isEscrowModalOpen, setIsEscrowModalOpen] = useState(false);
    const [escrowId, setEscrowId] = useState<number | null>(null);
    const [amountToFund, setAmountToFund] = useState<number | null>(null);
    const navigate = useNavigate();

    const userStr = localStorage.getItem('user');
    const userData = JSON.parse(userStr || '{}');
    
    const currentUserId = userData?.id || userData?.user?.id;

    const handleAction = async () => {
        try {
            const response = await api.post(`/offers/proposals/${proposal.id}/accept/`, {
                offer: proposal.offer,
                price: parseFloat(proposal.price),
                message: proposal?.message || "Accepted via notifications"
            });
            setEscrowId(response.data.escrow_id);
            toast.success(response.data.message || "Proposal Accepted successfully");
            setAmountToFund(parseFloat(proposal.price)); 
            setIsEscrowModalOpen(true);
        } catch (error: any) {
            console.error(`Error during acceptance:`, error);
            toast.error(error.response?.data?.message || "Failed to accept proposal");
        }
    }

    return (
        <div className={`flex flex-col border-b-2 border-gray-100 p-2 py-4 gap-2 `}>
            <FundEscrowModal 
                isModalOpen={isEscrowModalOpen} 
                setIsModalOpen={setIsEscrowModalOpen}
                escrowId={escrowId}
                amountToFund={amountToFund}
            />
            <div className='flex justify-between items-center'>
                <div className='flex items-center gap-2'>
                    <div className='p-2 rounded-[50%] bg-gray-100'>
                        <Icon icon="material-symbols:luggage-rounded" width={26} className="text-primary"/>
                    </div>
                    <p className='font-black !text-lg'>{title}</p>
                </div>
                <p className='!text-sm text-gray-400'>{time}</p>
            </div>
            
            <div className='flex flex-col gap-2'>
                <div className='flex gap-2 items-center'>
                    <h2 className="font-bold">₦{amount}</h2>
                    <div className='p-2 py-1 rounded-full w-fit flex justify-center items-center bg-primary'>
                        <Icon icon="codicon:thumbsup-filled" width={15} className="text-white"/>
                        <p className='!text-xs text-white ml-1 mt-1'>Bidding</p>
                    </div>
                </div>
                <div className='mt-3 flex gap-2'>
                    <div className='border-1 border-primary size-10 rounded-lg bg-gray-300 shrink-0 flex items-center justify-center text-white overflow-hidden'>
                        <img src={avatar} alt={carrierName} className='w-full h-full object-cover shrink-0' />
                    </div>
                    <div className='flex flex-col'>
                        <p className='!text-sm !font-bold'>{carrierName}</p>
                        <div className='flex items-center gap-1'>
                            <div className='flex justify-center items-center gap-[1px] bg-gray-100 px-2 py-0.5 rounded-full'>
                                <Icon icon="mdi:star" width={12} className="text-black" />
                                <p className='!text-[10px] !text-black '>4.2</p>
                            </div>
                            <Icon icon="codicon:verified-filled" width={14} className="text-primary" />
                        </div>
                    </div>
                </div>
            </div>

            {status === "accepted" && carrierId === currentUserId ? (
              <Button onClick={() => navigate(`/sender/${offerId}`)} title="View Sender's Dashboard" className='mt-2' />
            ) : (
              <div className='flex justify-between gap-4 mt-2'>
                  <Button 
                      title="Dismiss" 
                      onClick={() => toast.success("Proposal dismissed locally")} 
                      className='!bg-gray-100 !text-black !py-2 !text-xs'
                  />
                  <Button 
                      title="Accept Proposal" 
                      onClick={handleAction} 
                      className='!py-2 !text-xs' 
                  />
              </div>
            )}
        </div>
    );
}

export default Notifications;