import React from 'react';
import { Shield, Target } from 'lucide-react';

const AboutPage: React.FC = () => {
  return (
    <div className="container" style={{ maxWidth: '900px', padding: '1rem' }}>
       
       <header style={{ textAlign: 'center', marginBottom: '5rem' }}>
          <h1 style={{ fontSize: '3.5rem', fontWeight: '900', letterSpacing: '8px', color: 'var(--accent-color)' }}>MISSION_LOG</h1>
          <p style={{ opacity: 0.5 }}>UNDERSTANDING_THE_CORE_OF_REALHACKERS_HQ</p>
       </header>

       <div className="card" style={{ padding: '3rem', marginBottom: '3rem', fontSize: '1.1rem', lineHeight: '1.8' }}>
          <p>
             <span style={{ color: 'var(--accent-color)', fontWeight: 'bold' }}>RealHackers HQ</span> is an elite digital operations ecosystem designed for advanced surveillance, penetration testing, and social engineering research.
          </p>
          <p style={{ marginTop: '2rem' }}>
             Born from the need for centralized control over distributed digital assets, our platform provides operators with the tools necessary to maintain persistence, extract intelligence, and execute precision strikes across multiple platforms.
          </p>
       </div>

       <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', marginBottom: '5rem' }}>
          <div className="card">
             <Target color="var(--accent-color)" size={32} style={{ marginBottom: '1.5rem' }} />
             <h3>OUR_OBJECTIVE</h3>
             <p style={{ opacity: 0.6, fontSize: '0.9rem' }}>To provide a unified command and control interface for mobile and desktop surveillance modules.</p>
          </div>
          <div className="card">
             <Shield color="var(--accent-color)" size={32} style={{ marginBottom: '1.5rem' }} />
             <h3>SECURE_OPERATIONS</h3>
             <p style={{ opacity: 0.6, fontSize: '0.9rem' }}>Maintaining absolute operator anonymity through advanced encryption and stealth deployment methods.</p>
          </div>
       </div>

       <div style={{ textAlign: 'center', opacity: 0.2, fontSize: '0.7rem', letterSpacing: '4px' }}>
          ESTABLISHED // 2024 - REALHACKERS_ELITE
       </div>

    </div>
  );
};

export default AboutPage;
