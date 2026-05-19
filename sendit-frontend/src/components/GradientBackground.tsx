import React from 'react';
import { bgGradient } from "../assets/images";

const GradientBackground = ({ children }: { children: React.ReactNode }) => {
  const containerStyle: React.CSSProperties = {
    position: 'relative',
    width: '100%',
    minHeight: '150px',
    borderRadius: '12px',
    overflow: 'hidden',
    backgroundColor: '#001F72', // Fallback color while SVG loads
    margin: '0 auto',
  };

  const imageStyle: React.CSSProperties = {
    position: 'absolute',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    // Fix: changed 'objectCover' to 'objectFit'
    objectFit: 'cover', 
    zIndex: 0, 
    display: 'block', // Ensures SVGs are treated as block elements
  };

  const contentStyle: React.CSSProperties = {
    position: 'relative',
    zIndex: 10, // Higher than the image
    width: '100%',
    height: '100%',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    padding: '16px',
  };

  return (
    <div style={containerStyle}>
      {/* Background SVG */}
      <img 
        src={bgGradient} 
        alt="" 
        style={imageStyle}
        // Force rendering if the SVG is missing dimensions
        onLoad={(e) => (e.currentTarget.style.opacity = "1")}
      />
      
      {/* Content */}
      <div style={contentStyle}>
        {children}
      </div>
    </div>
  );
};

export default GradientBackground;