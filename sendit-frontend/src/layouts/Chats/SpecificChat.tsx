import { useState, useEffect, useRef } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Icon } from '@iconify/react/dist/iconify.js';
import api from '../../api/axios';
import { useWebSocket } from '../../hooks/useWebSocket';
import { Button } from '../../components/Button';
import { bgGradient } from '../../assets/images';

interface Message {
  id?: number;
  type: 'sent' | 'received';
  text: string;
  time: string;
  sender_id?: string;
}

const SpecificChat = () => {
  const navigate = useNavigate();
  const { chatId } = useParams();
  const [roomData, setRoomData] = useState<any>(null);
  const [offerData, setOfferData] = useState<any>(null);
  const [chatHistory, setChatHistory] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const scrollRef = useRef<HTMLDivElement>(null);
  const userStr = localStorage.getItem('user');
  const userData = JSON.parse(userStr || '{}');
  // console.log("Parsed User Data:", userData);
  const token = userData?.token?.access_token || userData?.access_token; 
  
  const currentUserId = userData?.id || userData?.user?.id;

  const wsUrl = `${import.meta.env.VITE_WS_URL}/${chatId}/`;
  const { messages: wsMessages, sendMessage } = useWebSocket(wsUrl, token);

  useEffect(() => {
    const fetchAllData = async () => {
      setIsLoading(true);
      try {
        // 1. Fetch Room Metadata
        const roomRes = await api.get(`/chats/${chatId}/`);
        const room = roomRes.data;
        setRoomData(room);

        // 2. Fetch Offer Details and Message History concurrently
        const [offerRes, msgRes] = await Promise.all([
          api.get(`/offers/${room.offer_id}/`),
          api.get(`/chats/${chatId}/messages/`)
        ]);

        setOfferData(offerRes.data.data);

        const formattedHistory = msgRes.data.results.map((m: any) => ({
          id: m.id,
          text: m.text,
          type: m.sender === currentUserId ? 'sent' : 'received',
          time: new Date(m.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          sender_id: m.sender
        }));
        setChatHistory(formattedHistory.reverse());
      } catch (err) {
        console.error("Error loading chat data:", err);
      } finally {
        setIsLoading(false);
      }
    };

    if (chatId) fetchAllData();
  }, [chatId, currentUserId]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [chatHistory, wsMessages, isLoading]);

  const handleSend = () => {
    if (newMessage.trim()) {
      sendMessage({ message: newMessage, chat_id: chatId });
      setNewMessage("");
    }
  };

  if (isLoading) {
    return (
      <div className="h-screen w-full flex flex-col items-center justify-center bg-white">
        <Icon icon="line-md:loading-twotone-loop" width={48} className="text-primary" />
        <p className="mt-4 text-sm text-gray-500 font-medium animate-pulse">Loading conversation...</p>
      </div>
    );
  }

  const otherParticipant = roomData?.participants?.find((p: any) => p.id !== currentUserId);
  const displayName = otherParticipant ? `${otherParticipant.first_name} ${otherParticipant.last_name}` : "Chat";
  const displayAvatar = otherParticipant?.avatar || `https://ui-avatars.com/api/?name=${otherParticipant?.first_name}+${otherParticipant?.last_name}`;

  const liveMessages: Message[] = wsMessages.map((m: any) => ({
    text: m.message,
    type: m.sender_id === currentUserId ? 'sent' : 'received',
    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    sender_id: m.sender_id
  }));

  const allMessages = [...chatHistory, ...liveMessages];

  return (
    <div className='flex flex-col h-screen bg-gray-100 overflow-hidden'>
      {/* Chat header */}
      <div className="z-50 fixed shadow-sm bg-white w-full top-0 p-4 flex gap-4 justify-between items-center">
        <div className="w-full flex items-center gap-4 py-2">
          <button onClick={() => navigate('/chats')} className="border-1 border-gray-100 p-2 bg-white rounded-[50%] hover:bg-gray-100 transition-colors">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M15 18L9 12L15 6" stroke="black" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
          </button>
          
          <div className='flex gap-2 items-center'>
            <img src={displayAvatar} alt="Profile" className='border-1 border-primary w-10 h-10 rounded-full object-cover' />
            <div>
              <div className='flex items-center'>
                <h2 className='!text-sm font-bold'>{displayName}</h2>
                <Icon icon="fluent-mdl2:verified-brand-solid" width={16} className="text-primary inline-block ml-1" />
              </div>
              <div className='flex text-green-500 items-center'>
                <Icon icon="stash:circle-dot-duotone" width={16} className="shrink-0" />
                <p className='!text-xs mt-1'>Online</p>
              </div>
            </div>
          </div>
        </div>
        <div className='flex items-center gap-2'>
          <Icon icon="solar:phone-outline" width={28} className="cursor-pointer pt-1 text-bodyText/80" />
          <Icon icon="iwwa:option" height={30} className="text-bodyText/80 cursor-pointer" />
        </div>
      </div>

      <main ref={scrollRef} className="flex-1 mt-[90px] overflow-y-auto pb-28">
        <div className='flex w-full bg-blue-50 p-2 justify-center'>
          <p className='font-black !text-[10px] text-blue-600 uppercase'>Messages are end-to-end encrypted</p>
        </div>

        <div className='p-4 flex flex-col gap-4 items-center'>
          <p className='font-black !text-[11px]'>🎉 Offer ID: {offerData?.code || '...'}</p>
          <div className='w-full rounded-xl bg-white border-1 border-gray-100 overflow-hidden shadow-sm max-w-md'>
            <div className="relative h-24">
              <img src={ bgGradient} alt="Package" className="w-full h-full object-cover" />
              <div className="absolute inset-0 p-4 flex flex-col justify-end bg-black/10">
                <p className="text-white !text-lg !font-bold capitalize">{offerData?.package_type} Package</p>
                <div className="flex gap-2 mt-1">
                  <span className='bg-[#001F72] backdrop-blur-md px-2 py-1 rounded-full text-white !text-[13px] capitalize'>
                    📦 {offerData?.package_type}
                  </span>
                  {offerData?.is_fragile && (
                    <span className='bg-red-500 backdrop-blur-md px-2 py-1 rounded-full text-white text-[10px]'>Fragile</span>
                  )}
                </div>
              </div>
            </div>
            
            <div className='p-4 space-y-3'>
               <div className='flex justify-between items-center border-b border-gray-50 pb-2'>
                  <div>
                    <p className='text-[10px] text-gray-400 uppercase font-bold'>Pickup</p>
                    <p className='text-xs font-bold'>{offerData?.location.pickup_location_detail.city}</p>
                  </div>
                  <Icon icon="solar:arrow-right-linear" className="text-gray-300" />
                  <div className="text-right">
                    <p className='text-[10px] text-gray-400 uppercase font-bold'>Delivery</p>
                    <p className='text-xs font-bold'>{offerData?.location.delivery_location_detail.city}</p>
                  </div>
               </div>
               <div className='flex justify-between items-center'>
                  <p className='text-xs text-gray-500'>Total Price</p>
                  <p className='text-sm font-black text-primary'>₦{offerData?.pricing.total_price.toLocaleString()}</p>
               </div>
               <Button onClick={() => navigate(`/sender/${offerData?.id}`)} title={`${offerData?.sender.id === currentUserId ? 'View Carrier Dashboard' : 'View Sender Dashboard'}`} className="w-full !py-2.5 !text-xs" />
            </div>
          </div>
        </div>

        <div className='px-6 space-y-6 mt-4'>
          {allMessages.map((message, idx) => (
            <div key={idx} className={`flex items-start gap-3 w-full ${message.type === 'sent' ? 'justify-end' : 'justify-start'}`}>
              {message.type === 'received' && (
                <img src={displayAvatar} alt="Avatar" className="w-9 h-9 rounded-full shrink-0 mt-1 object-cover" />
              )}
              <div className={`flex flex-col gap-1.5 max-w-[80%] ${message.type === 'sent' ? 'items-end' : 'items-start'}`}>
                <div className={`p-4 ${message.type === 'sent' 
                  ? 'bg-blue-600 text-white rounded-[20px] rounded-tr-[0px]' 
                  : 'bg-white text-black border border-gray-200 rounded-[20px] rounded-tl-[0px]'}`}>
                  <p className="!text-sm leading-relaxed">{message.text}</p>
                </div>
                <span className="!text-[10px] text-gray-400 font-medium">{message.time}</span>
              </div>
            </div>
          ))}
        </div>
      </main>

      <footer className="w-full bg-white px-6 py-4 flex items-center gap-4 fixed bottom-0 left-0 border-t border-gray-100 z-10">
        <div className="flex-1 flex items-center gap-3 bg-gray-50 border border-gray-200 rounded-full px-5 py-3 focus-within:border-primary">
          <input 
            type="text" 
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder="Type a message..." 
            className="flex-1 bg-transparent text-sm text-black outline-none"
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          />
        </div>
        <button 
          onClick={handleSend}
          disabled={!newMessage.trim()}
          className={`p-3 rounded-full flex items-center justify-center shadow-sm transition-all ${newMessage.trim() ? 'bg-primary' : 'bg-gray-200'}`}
        >
          <Icon icon="mynaui:send-solid" className={newMessage.trim() ? "text-white" : "text-gray-400"} width={24} />
        </button>
      </footer>
    </div>
  );
}

export default SpecificChat;