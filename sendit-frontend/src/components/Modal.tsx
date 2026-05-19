import React, { useEffect, useRef } from 'react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
}

const Modal: React.FC<ModalProps> = ({ isOpen, onClose, children }) => {
  const modalRef = useRef<HTMLDivElement>(null);

  // Close when clicking outside the modal content
  const handleBackdropClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (modalRef.current && !modalRef.current.contains(e.target as Node)) {
      onClose();
    }
  };

  // Close on Escape key press
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      // Prevent scrolling on the body when modal is open
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div 
      className="fixed inset-0 z-[100] flex items-end justify-center bg-black/50 transition-opacity"
      onClick={handleBackdropClick}
    >
      <div
        ref={modalRef}
        className="w-full bg-white rounded-t-[32px] overflow-hidden transition-transform duration-300 ease-out shadow-2xl"
        style={{ height: '70vh' }}
      >
        {/* Optional: Drag Handle/Indicator for mobile feel */}
        <div className="w-full flex justify-center pt-4 pb-2">
          <div className="w-12 h-1.5 bg-gray-200 rounded-full" />
        </div>

        <div className="h-full overflow-y-auto px-6 pb-20">
          {children}
        </div>
      </div>
    </div>
  );
};

export default Modal;