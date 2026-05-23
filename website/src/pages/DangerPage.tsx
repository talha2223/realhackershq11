import React, { useEffect } from 'react';
import { Terminal, Zap, AlertTriangle } from 'lucide-react';
import { motion } from 'framer-motion';

const DangerPage: React.FC = () => {
  useEffect(() => {
    document.title = "RealHackers HQ // Danger Agent Coming Soon";
  }, []);

  return (
    <div className="container" style={{ textAlign: 'center', paddingTop: '10vh' }}>
      <motion.div initial={{ scale: 0.8 }} animate={{ scale: 1 }}>
        <Terminal size={80} color="var(--accent-color)" style={{ marginBottom: '2rem' }} />
        <h1 style={{ fontSize: '3rem', fontWeight: '900', letterSpacing: '8px' }}>DANGER // EXPLOIT</h1>
        
        <div className="card" style={{ maxWidth: '600px', margin: '4rem auto', padding: '3rem', borderStyle: 'dashed' }}>
           <h2 style={{ letterSpacing: '4px', marginBottom: '1rem' }}>COMING_SOON</h2>
           <p style={{ opacity: 0.5, lineHeight: '1.8' }}>
              The exploitation framework and C2 secure bridge are being hardened. 
              Automated vulnerability scanning and payload generation will be live in the next release.
           </p>
        </div>
      </motion.div>
    </div>
  );
};

export default DangerPage;
