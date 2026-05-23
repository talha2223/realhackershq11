import React from 'react';
import { 
  Mail, MessageSquare 
} from 'lucide-react';
import { motion } from 'framer-motion';

const CreditsPage: React.FC = () => {
  const team = [
    {
      name: 'Mr Real',
      role: 'Founder & Head of Operations',
      image: '/assets/mrreal.png',
      status: 'ADMIN',
    },
    {
      name: 'Talhaxd',
      role: 'Co-owner & System Architect',
      image: '/assets/talhaxd.png',
      status: 'ADMIN',
    },
    {
      name: 'Helter Ustad',
      role: 'Lead Developer & Exploitation Expert',
      image: '/assets/helterustad.png',
      status: 'DEVELOPER',
    },
  ];

  const accentColor = 'var(--accent-color)';

  return (
    <div className="container" style={{ maxWidth: '1600px', padding: '1rem' }}>
       
       <header style={{ textAlign: 'center', marginBottom: '5rem' }}>
          <h1 style={{ fontSize: '4rem', fontWeight: '900', letterSpacing: '8px', color: 'var(--accent-color)' }}>THE_TEAM</h1>
          <p style={{ opacity: 0.5 }}>THE_CORE_OPERATORS_BEHIND_REALHACKERS_HQ</p>
       </header>

       {/* Team Section */}
       <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '2rem', marginBottom: '5rem' }}>
          {team.map((member, i) => (
            <motion.div 
              key={member.name} 
              initial={{ y: 20, opacity: 0 }} 
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: i * 0.1 }}
              className="card" 
              style={{ padding: '2rem', textAlign: 'center' }}
            >
              <div style={{ width: '150px', height: '150px', margin: '0 auto 2rem', borderRadius: '50%', overflow: 'hidden', border: `2px solid ${accentColor}`, padding: '5px' }}>
                 <img 
                    src={member.image} 
                    alt={member.name} 
                    style={{ width: '100%', height: '100%', objectFit: 'cover', borderRadius: '50%', filter: 'grayscale(100%)' }} 
                 />
              </div>
              <div style={{ fontSize: '0.5rem', background: accentColor, color: '#fff', display: 'inline-block', padding: '2px 10px', borderRadius: '10px', marginBottom: '1rem', fontWeight: 'bold' }}>{member.status}</div>
              <h2 style={{ fontSize: '1.5rem', fontWeight: '900', letterSpacing: '2px' }}>{member.name.toUpperCase()}</h2>
              <p style={{ opacity: 0.5, fontSize: '0.8rem', margin: '1rem 0 2rem' }}>{member.role}</p>
              
              <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem' }}>
                 <button className="btn" style={{ padding: '0.5rem' }}><Mail size={14} /></button>
                 <button className="btn" style={{ padding: '0.5rem' }}><MessageSquare size={14} /></button>
              </div>
            </motion.div>
          ))}
       </div>

       <div style={{ textAlign: 'center', opacity: 0.1, fontSize: '0.7rem', letterSpacing: '10px', marginTop: '5rem' }}>
          REALHACKERS_HQ // MISSION_CRITICAL
       </div>

    </div>
  );
};

export default CreditsPage;
