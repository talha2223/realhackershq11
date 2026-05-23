import React, { useEffect } from 'react';
import { Monitor, Zap } from 'lucide-react';
import { motion } from 'framer-motion';

const HDexPage: React.FC = () => {
  useEffect(() => {
    document.title = "RealHackers HQ // H-Dex Desktop [Coming Soon]";
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
              STATUS: ARCHITECTING_MODULE
           </div>
        </div>
        
        <div className="card" style={{ maxWidth: '700px', margin: '4rem auto', padding: '3rem', borderStyle: 'dashed', borderColor: '#3498db' }}>
           <div style={{ display: 'flex', alignItems: 'center', gap: '10px', justifyContent: 'center', marginBottom: '1.5rem' }}>
              <Zap size={20} color="#f1c40f" />
              <h2 style={{ letterSpacing: '4px' }}>ACCESS_RESTRICTED</h2>
           </div>
           <p style={{ opacity: 0.5, lineHeight: '1.8', fontSize: '0.9rem' }}>
              The H-Dex PC persistence engine is currently undergoing a full core rewrite. 
              All mock telemetry and fake node data have been purged to prepare for the real deployment. 
              Visual process management and kernel-level keylogging will be enabled once the secure uplink is verified.
           </p>
           <div style={{ marginTop: '2rem', fontSize: '0.7rem', color: '#3498db', fontWeight: 'bold' }}>
              ESTIMATED_UPLINK: PHASE_2_INITIALIZATION
           </div>
        </div>
      </motion.div>
    </div>
  );
};

export default HDexPage;
