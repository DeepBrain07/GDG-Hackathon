import { useEffect, useRef, useState } from 'react';

export const useWebSocket = (url: string, token: string | null) => {
  
  console.log("Initializing WebSocket with URL:", url, "and token:", token);
  const [messages, setMessages] = useState<any[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const socketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!token) return;

    // We pass the token as a query parameter for the handshake
    const fullUrl = `${url}?token=${token}`;
    socketRef.current = new WebSocket(fullUrl);

    socketRef.current.onopen = () => {
      console.log('✅ Connected to Sendit WebSocket');
      setIsConnected(true);
    };

    socketRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setMessages((prev) => [...prev, data]);
    };

    socketRef.current.onclose = () => {
      console.log('❌ Disconnected');
      setIsConnected(false);
    };

    return () => {
      socketRef.current?.close();
    };
  }, [url, token]);

  const sendMessage = (data: any) => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify(data));
    }
  };

  return { messages, isConnected, sendMessage };
};