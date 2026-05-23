import React, { createContext, useContext, useState, useEffect } from 'react';

interface LoadingContextType {
  progress: number;
  isLoaded: boolean;
  setVideoLoaded: () => void;
}

const LoadingContext = createContext<LoadingContextType | undefined>(undefined);

export const LoadingProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [progress, setProgress] = useState(0);
  const [videoLoaded, setVideoLoaded] = useState(false);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    // Ultra-fast transition
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev < 98) return prev + Math.random() * 25;
        if (videoLoaded) return 100;
        return prev;
      });
    }, 50);

    return () => clearInterval(interval);
  }, [videoLoaded]);

  useEffect(() => {
    if (progress >= 100) {
      // Near-instant load
      const timer = setTimeout(() => setIsLoaded(true), 100);
      return () => clearTimeout(timer);
    }
  }, [progress]);

  return (
    <LoadingContext.Provider value={{ progress, isLoaded, setVideoLoaded: () => setVideoLoaded(true) }}>
      {children}
    </LoadingContext.Provider>
  );
};

export const useLoading = () => {
  const context = useContext(LoadingContext);
  if (!context) throw new Error('useLoading must be used within LoadingProvider');
  return context;
};
