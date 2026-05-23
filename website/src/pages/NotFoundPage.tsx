import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldAlert, ChevronLeft } from 'lucide-react';
import { motion } from 'framer-motion';

const NotFoundPage: React.FC = () => {
  return (
    <div className="container" style={{ textAlign: 'center', paddingTop: '10vh' }}>
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5 }}
      >
        <ShieldAlert size={100} color="#f55" style={{ marginBottom: '2rem' }} />
        <h1 style={{ fontSize: '6rem', fontWeight: '900', color: '#f55', margin: 0 }}>404</h1>
        <h2 style={{ letterSpacing: '8px', marginBottom: '2rem' }}>ACCESS_DENIED</h2>
        <p style={{ opacity: 0.5, maxWidth: '500px', margin: '0 auto 3rem' }}>
          The sector you are trying to access does not exist or has been quarantined. 
          Unauthorized probing of HQ sectors is strictly logged.
        </p>
        
        <Link to="/" className="btn">
          <ChevronLeft size={16} /> RETURN_TO_SAFE_ZONE
        </Link>
      </motion.div>
    </div>
  );
};

export default NotFoundPage;
