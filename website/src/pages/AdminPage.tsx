import React, { useState, useEffect } from 'react';
import { 
  Shield, Save, Layout
} from 'lucide-react';
import { motion } from 'framer-motion';
import { toast } from 'sonner';

const AdminPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'GENERAL' | 'SECURITY' | 'USERS' | 'API'>('GENERAL');

  useEffect(() => {
    document.title = "RealHackers HQ // Admin Panel";
  }, []);

  return (
    <div className="container" style={{ maxWidth: '1400px', padding: '1rem' }}>
       
       <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '3rem', borderBottom: '1px solid #222', paddingBottom: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
             <Shield size={32} color="var(--accent-color)" />
             <h1 style={{ fontSize: '1.8rem', fontWeight: '900', letterSpacing: '4px' }}>ADMIN_CONTROL_PANEL</h1>
          </div>
          <div style={{ display: 'flex', gap: '1rem' }}>
             {['GENERAL', 'SECURITY', 'USERS', 'API'].map(tab => (
               <button 
                  key={tab} onClick={() => setActiveTab(tab as any)}
                  className={`tab-btn ${activeTab === tab ? 'active' : ''}`}
               >
                  {tab}
               </button>
             ))}
          </div>
       </header>

       <div className="grid-responsive">
          
          {activeTab === 'GENERAL' && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="card" style={{ gridColumn: 'span 2' }}>
               <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '2rem' }}>
                  <Layout size={20} color="var(--accent-color)" />
                  <h3>SYSTEM_PREFERENCES</h3>
               </div>
               
               <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                     <div>
                        <div style={{ fontWeight: 'bold' }}>HQ_MAINTENANCE_MODE</div>
                        <div style={{ fontSize: '0.7rem', opacity: 0.5 }}>Disable public access to all modules.</div>
                     </div>
                     <input type="checkbox" style={{ width: '40px', height: '20px' }} />
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                     <div>
                        <div style={{ fontWeight: 'bold' }}>REALTIME_LOGGING</div>
                        <div style={{ fontSize: '0.7rem', opacity: 0.5 }}>Enable verbose debug logs in console.</div>
                     </div>
                     <input type="checkbox" defaultChecked style={{ width: '40px', height: '20px' }} />
                  </div>

                  <div>
                     <div style={{ fontWeight: 'bold', marginBottom: '10px' }}>GLOBAL_THEME_ACCENT</div>
                     <div style={{ display: 'flex', gap: '10px' }}>
                        {['#e74c3c', '#3498db', '#f1c40f', '#2ecc71'].map(color => (
                          <div key={color} style={{ width: '30px', height: '30px', background: color, borderRadius: '4px', cursor: 'pointer', border: '2px solid transparent' }} />
                        ))}
                     </div>
                  </div>

                  <button className="btn" style={{ width: 'fit-content' }} onClick={() => toast.success("Settings Saved")}>
                     <Save size={16} /> COMMIT_CHANGES
                  </button>
               </div>
            </motion.div>
          )}

          <div className="card" style={{ height: 'fit-content' }}>
             <h3>SERVER_HEALTH</h3>
             <div style={{ marginTop: '2rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem' }}>
                   <span>NODE_JS_UPLINK</span>
                   <span style={{ color: '#2ecc71' }}>OPTIMAL</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem' }}>
                   <span>DB_LATENCY</span>
                   <span style={{ color: '#2ecc71' }}>12ms</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem' }}>
                   <span>FIREBASE_SYNC</span>
                   <span style={{ color: '#2ecc71' }}>ACTIVE</span>
                </div>
             </div>
          </div>

       </div>

    </div>
  );
};

export default AdminPage;
