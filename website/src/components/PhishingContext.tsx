import React, { createContext, useContext, useState, useEffect } from 'react';

interface CapturedIntel {
  id: string;
  timestamp: string;
  platform: string;
  data: any;
  ip?: string;
  userAgent?: string;
}

interface PhishingContextType {
  intel: CapturedIntel[];
  captureIntel: (platform: string, data: any) => void;
  clearIntel: () => void;
}

const PhishingContext = createContext<PhishingContextType | undefined>(undefined);

export const PhishingProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [intel, setIntel] = useState<CapturedIntel[]>([]);

  useEffect(() => {
    const savedIntel = localStorage.getItem('hq_captured_intel');
    if (savedIntel) {
      setIntel(JSON.parse(savedIntel));
    }
  }, []);

  const captureIntel = (platform: string, data: any) => {
    const newEntry: CapturedIntel = {
      id: Math.random().toString(36).substr(2, 9),
      timestamp: new Date().toISOString(),
      platform,
      data,
      ip: '192.168.' + Math.floor(Math.random() * 255) + '.' + Math.floor(Math.random() * 255), // Simulated IP
      userAgent: navigator.userAgent
    };

    const updatedIntel = [newEntry, ...intel];
    setIntel(updatedIntel);
    localStorage.setItem('hq_captured_intel', JSON.stringify(updatedIntel));
  };

  const clearIntel = () => {
    setIntel([]);
    localStorage.removeItem('hq_captured_intel');
  };

  return (
    <PhishingContext.Provider value={{ intel, captureIntel, clearIntel }}>
      {children}
    </PhishingContext.Provider>
  );
};

export const usePhishing = () => {
  const context = useContext(PhishingContext);
  if (context === undefined) {
    throw new Error('usePhishing must be used within a PhishingProvider');
  }
  return context;
};
