import React, { useEffect } from 'react';
import { Shield } from 'lucide-react';
import { motion } from 'framer-motion';

const PhishingPage: React.FC = () => {
  useEffect(() => {
    document.title = "RealHackers HQ // Phishing [Coming Soon]";
  }, []);

  return (
    <div className="container" style={{ textAlign: 'center', paddingTop: '10vh' }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <Shield size={80} color="var(--accent-color)" style={{ marginBottom: '2rem' }} />
        <h1 style={{ fontSize: '3rem', fontWeight: '900', letterSpacing: '8px' }}>PHISHING // OPS</h1>
        
        <div className="card" style={{ maxWidth: '600px', margin: '4rem auto', padding: '3rem', borderStyle: 'dashed' }}>
           <h2 style={{ letterSpacing: '4px', marginBottom: '1rem' }}>COMING_SOON</h2>
           <p style={{ opacity: 0.5, lineHeight: '1.8' }}>
              Advanced social engineering templates and credential harvesting vaults are being integrated. 
              The fake templates have been removed. This module will allow real link deployment in Phase 2.
           </p>
        </div>
      </motion.div>
    </div>
  );
};

export default PhishingPage;
