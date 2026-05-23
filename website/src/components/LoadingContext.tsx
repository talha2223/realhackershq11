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
    // Faster, more realistic progress
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev < 95) return prev + Math.random() * 15;
        if (videoLoaded) return 100;
        return prev;
      });
    }, 100);

    return () => clearInterval(interval);
  }, [videoLoaded]);

  useEffect(() => {
    if (progress >= 100) {
      // Immediate load once ready
      setIsLoaded(true);
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
