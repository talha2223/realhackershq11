import React, { useEffect } from 'react';
import { Globe, Search, User } from 'lucide-react';
import { motion } from 'framer-motion';

const OSINTPage: React.FC = () => {
  useEffect(() => {
    document.title = "RealHackers HQ // OSINT Coming Soon";
  }, []);

  return (
    <div className="container" style={{ textAlign: 'center', paddingTop: '10vh' }}>
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <Globe size={80} color="var(--accent-color)" style={{ marginBottom: '2rem' }} />
        <h1 style={{ fontSize: '3rem', fontWeight: '900', letterSpacing: '8px' }}>OSINT // INTELLIGENCE</h1>
        
        <div className="card" style={{ maxWidth: '600px', margin: '4rem auto', padding: '3rem', borderStyle: 'dashed' }}>
           <h2 style={{ letterSpacing: '4px', marginBottom: '1rem' }}>COMING_SOON</h2>
           <p style={{ opacity: 0.5, lineHeight: '1.8' }}>
              Our Open Source Intelligence suite is under development. 
              Email finder, username search, and social media mapping tools will be enabled shortly.
           </p>
        </div>
      </motion.div>
    </div>
  );
};

export default OSINTPage;
