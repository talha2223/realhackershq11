import React, { useEffect } from 'react';
import { Monitor, Cpu, ShieldAlert } from 'lucide-react';
import { motion } from 'framer-motion';

const HDexPage: React.FC = () => {
  useEffect(() => {
    document.title = "RealHackers HQ // H-Dex Coming Soon";
  }, []);

  return (
    <div className="container" style={{ textAlign: 'center', paddingTop: '10vh' }}>
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
      >
        <Monitor size={80} color="#3498db" style={{ marginBottom: '2rem' }} />
        <h1 style={{ fontSize: '3rem', fontWeight: '900', letterSpacing: '8px' }}>H-DEX // DESKTOP</h1>
        <div style={{ display: 'flex', justifyContent: 'center', gap: '20px', marginTop: '1rem', color: '#3498db' }}>
           <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.8rem', fontWeight: 'bold' }}>
              <div style={{ width: '8px', height: '8px', background: '#f1c40f', borderRadius: '50%' }} />
              STATUS: IN_DEVELOPMENT
           </div>
        </div>
        
        <div className="card" style={{ maxWidth: '600px', margin: '4rem auto', padding: '3rem', borderStyle: 'dashed', borderColor: '#3498db' }}>
           <h2 style={{ letterSpacing: '4px', marginBottom: '1rem' }}>COMING_SOON</h2>
           <p style={{ opacity: 0.5, lineHeight: '1.8' }}>
              The H-Dex desktop persistence module is currently being calibrated for Windows, macOS, and Linux kernels. 
              Visual file management and remote shell capabilities will be available in Phase 2.
           </p>
        </div>
      </motion.div>
    </div>
  );
};

export default HDexPage;
