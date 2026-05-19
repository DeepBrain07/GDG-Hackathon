import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../api/axios';
import DashboardLayout from '../DashboardLayout/DashboardLayout';
import { ProviderRoutePaths } from '../../routers/provider.router';
import { Icon } from '@iconify/react/dist/iconify.js';
import './style.css';

const Chats = () => {
  const navigate = useNavigate();
  const [chatRooms, setChatRooms] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentUserId, setCurrentUserId] = useState<string | null>(null);

  useEffect(() => {
    // 1. Get current user ID from your existing storage structure
    const userStr = localStorage.getItem('user');
    if (userStr) {
      const userData = JSON.parse(userStr);
      // Adjust this if your user ID is nested differently (e.g., userData.user.id)
      setCurrentUserId(userData?.id || userData?.user?.id);
    }

    // 2. Fetch Chat Rooms using your custom axios instance
    const fetchChats = async () => {
      try {
        const response = await api.get('/chats/');
        setChatRooms(response.data.results);
      } catch (error) {
        console.error("Error fetching chats:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchChats();
  }, []);

  return (
    <DashboardLayout>
      <div className='bg-[#FBFBFBB2] p-4 flex flex-col pb-8 gap-8'>
        <div className={` w-full flex items-center gap-4 `}>
          <button onClick={() => navigate('/home')} className="p-2 bg-white rounded-[50%] hover:bg-gray-100 transition-colors">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M15 18L9 12L15 6" stroke="black" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
          <h2 className="!text-xl">Chats</h2>
        </div>
      </div>

      <div className='py-4 flex flex-col '>
        {loading ? (
          <div className="p-8 text-center text-gray-500">Loading conversations...</div>
        ) : chatRooms.length > 0 ? (
          chatRooms.map((room) => {
            // Find the participant that IS NOT the current user
            const otherParticipant = room.participants.find((p: any) => p.id !== currentUserId);
            
            const displayName = otherParticipant 
              ? `${otherParticipant.first_name} ${otherParticipant.last_name}` 
              : "Direct Message";
            
            const time = room.last_message 
              ? new Date(room.last_message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) 
              : "";

            return (
              <ChatCard
                key={room.id}
                chatId={room.id.toString()}
                name={displayName}
                lastMessage={room.last_message?.text || "No messages yet"}
                // Fallback to a default avatar if no profile image exists in participant data
                profileImage={otherParticipant?.avatar || "https://ui-avatars.com/api/?name=" + displayName}
                lastMessageTime={time}
              />
            );
          })
        ) : (
          <div className="p-8 text-center text-gray-500">No chats found.</div>
        )}
      </div>
    </DashboardLayout>
  );
};

const ChatCard = ({name, chatId, lastMessage, profileImage, lastMessageTime}: {name: string, chatId: string,  lastMessage: string, profileImage: string, lastMessageTime: string}) => {
    
  const navigate = useNavigate();
    return (
        <div 
          onClick={() => navigate(ProviderRoutePaths.specificChat.replace(':chatId', chatId))} 
          className='cursor-pointer hover:bg-gray-50 flex items-center gap-4 bg-white p-4 border-b border-gray-100 transition-colors'
        >
            <div className='relative'>
                <img src={profileImage} alt={name} className='w-12 h-12 rounded-full object-cover border border-gray-200' />
            </div>
            <div className='flex-1 min-w-0'>
                <div className='flex justify-start items-center gap-1'>
                    <h3 className='font-semibold truncate text-gray-900'>{name}</h3>
                    <Icon icon="fluent-mdl2:verified-brand-solid" width={14} className="text-primary flex-shrink-0" />
                </div>
                <p className='text-sm text-gray-500 truncate'>{lastMessage}</p>
            </div>
            <div className='flex flex-col items-end gap-1'>
                <p className='text-[10px] text-gray-400 whitespace-nowrap'>{lastMessageTime}</p>
                {/* {notifications > 0 && (
                    <div className='bg-primary text-white text-[10px] font-bold w-5 h-5 rounded-full flex items-center justify-center shadow-sm'>
                        !
                    </div>
                )} */}
            </div>
        </div>
    );
};

export default Chats;