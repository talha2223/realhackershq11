import React from 'react';
import { Smartphone, Monitor, Shield, Terminal, Zap } from 'lucide-react';

const DocsPage: React.FC = () => {
  const sections = [
    { title: 'GETTING_STARTED', icon: Zap, content: 'Initialize your operator session by authenticating with the HQ master key.' },
    { title: 'A-DEX_MOBILE', icon: Smartphone, content: 'Deploy the System Update engine to target Android devices to begin data extraction.' },
    { title: 'H-DEX_DESKTOP', icon: Monitor, content: 'Install the X-Link bridge on Windows/macOS for advanced PC surveillance.' },
    { title: 'PHISHING_OPS', icon: Shield, content: 'Select a high-conversion template and deploy a secure capture link to targets.' },
    { title: 'EXPLOITATION', icon: Terminal, content: 'Use the Danger Framework to execute remote shell payloads on compromised nodes.' },
  ];

  return (
    <div className="container" style={{ maxWidth: '1000px', padding: '1rem' }}>
       <header style={{ textAlign: 'center', marginBottom: '4rem' }}>
          <h1 style={{ fontSize: '3rem', fontWeight: '900', letterSpacing: '4px' }}>OPERATOR_DOCS</h1>
          <p style={{ opacity: 0.5 }}>MISSION_CRITICAL_DOCUMENTATION_AND_GUIDES</p>
       </header>

       <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {sections.map(s => (
            <div key={s.title} className="card" style={{ padding: '2rem' }}>
               <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
                  <s.icon color="var(--accent-color)" size={20} />
                  <h2 style={{ fontSize: '1.2rem', letterSpacing: '2px' }}>{s.title}</h2>
               </div>
               <p style={{ opacity: 0.6, lineHeight: '1.6' }}>{s.content}</p>
               <button className="btn" style={{ marginTop: '1.5rem', padding: '0.4rem 1rem', fontSize: '0.6rem' }}>READ_FULL_MANUAL</button>
            </div>
          ))}
       </div>
    </div>
  );
};

export default DocsPage;
