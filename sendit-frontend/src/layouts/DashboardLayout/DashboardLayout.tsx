import { Icon } from "@iconify/react";
import { useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import toast, { Toaster } from 'react-hot-toast';
import { useWebSocket } from "../../hooks/useWebSocket"; // Adjust path as needed

function DashboardLayout({ children }: { children: React.ReactNode }) {
  const navigate = useNavigate();
  const location = useLocation();
  const currentPath = location.pathname;

  // 1. Get auth data (adjust based on your auth logic)
  const token = localStorage.getItem('accessToken'); 
  
  // 2. Initialize the WebSocket connection
  const { messages } = useWebSocket('ws://localhost:8000/ws/notifications/', token);

  // 3. Listen for incoming notification messages
  useEffect(() => {
    if (messages.length > 0) {
      const lastMessage = messages[messages.length - 1];
      
      if (lastMessage.type === 'notification') {
        toast.success(
          <div className="flex flex-col">
            <p className="font-bold text-sm">{lastMessage.title || "Update"}</p>
            <p className="text-xs">{lastMessage.message}</p>
          </div>,
          {
            duration: 5000,
            position: 'top-right',
            style: {
              borderRadius: '12px',
              background: '#333',
              color: '#fff',
            },
          }
        );
      }
    }
  }, [messages]);

  const menu = {
    "Home": ["iconamoon:profile", "/home"],
    "Offers": ["mdi:package-outline", "/offers"],
    "Chat": ["humbleicons:chat", "/chats"],
    "Wallet": ["streamline-plump:wallet", "/wallet"],
    "Profile": ["iconamoon:profile", "/profile"],
  };

  return (
    <div className="w-full overflow-hidden min-h-screen bg-white">
      {/* 4. Global Toaster component */}
      <Toaster />

      <div className="mb-[100px]">
        {children}
      </div>

      <div className="bg-white border-t border-gray-100 shadow-[0_-4px_10px_rgba(0,0,0,0.05)] z-50 flex justify-between fixed bottom-0 w-full">
        {Object.entries(menu).map(([name, [icon, path]]) => (
          <div 
            key={name} 
            onClick={() => navigate(path)} 
            className={`cursor-pointer flex-1 p-4 flex ${path === currentPath ? "text-primary" : "text-black/80" } flex-col items-center justify-center`}
          >
            <Icon icon={icon} width={24} />
            <p className="text-[10px] font-bold mt-1">{name}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default DashboardLayout;