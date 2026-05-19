import React, { useState, useEffect } from "react";

interface MobileGuardProps {
  children: React.ReactNode;
}

export const MobileGuard: React.FC<MobileGuardProps> = ({ children }) => {
  const [isMobile, setIsMobile] = useState<boolean>(window.innerWidth <= 768);

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth <= 768);
    };

    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  if (!isMobile) {
    return (
      <div style={styles.container}>
        <div style={styles.card}>
          <h1>Mobile Only Access</h1>
          <p>This application is optimized for mobile devices. Please view this page on a mobile phone or shrink your browser window to continue.</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
};

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    display: "flex",
    height: "100vh",
    width: "100vw",
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "#1a1a1a",
    color: "white",
    textAlign: "center",
    fontFamily: "sans-serif",
    padding: "20px",
  },
  card: {
    maxWidth: "400px",
    padding: "40px",
    borderRadius: "12px",
    background: "#2a2a2a",
    boxShadow: "0 10px 30px rgba(0,0,0,0.5)",
  }
};