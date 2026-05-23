import React, { useEffect } from 'react';
import { useLoading } from './LoadingContext';

const LoadingScreen: React.FC = () => {
  const { progress, isLoaded } = useLoading();
  const hasLoadedBefore = sessionStorage.getItem('hq_initialized');

  useEffect(() => {
    if (isLoaded) {
      sessionStorage.setItem('hq_initialized', 'true');
    }
  }, [isLoaded]);

  if (hasLoadedBefore) return null;

  return (
    <div className={`loading-screen ${isLoaded ? 'fade-out' : ''}`}>
      <div className="loading-logo">RH</div>
      <div className="loading-bar-container">
        <div 
          className="loading-bar-progress" 
          style={{ width: `${progress}%` }}
        ></div>
      </div>
      <div className="loading-status">
        {progress < 100 ? `INITIALIZING SYSTEM... ${Math.round(progress)}%` : 'SYSTEM READY'}
      </div>
    </div>
  );
};

export default LoadingScreen;
