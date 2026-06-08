import React, { useState, useEffect } from 'react';
import { 
  Shield, Save, Layout, Database
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'sonner';
import { usePhishing } from '../components/PhishingContext';

const AdminPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'OPERATIONS' | 'INTEL' | 'USERS' | 'ANALYTICS' | 'API' | 'SETTINGS'>('OPERATIONS');
  const { intel } = usePhishing();

  useEffect(() => {
    document.title = "RealHackers HQ // Admin Panel";
  }, []);

  const tabs = ['OPERATIONS', 'INTEL', 'USERS', 'ANALYTICS', 'API', 'SETTINGS'];

  return (
    <div className="container" style={{ maxWidth: '1400px', padding: '1rem' }}>
       
       <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '3rem', borderBottom: '1px solid #222', paddingBottom: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
             <Shield size={32} color="var(--accent-color)" />
             <h1 style={{ fontSize: '1.8rem', fontWeight: '900', letterSpacing: '4px' }}>ADMIN_CONTROL_PANEL</h1>
          </div>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
             {tabs.map(tab => (
               <button 
                  key={tab} onClick={() => setActiveTab(tab as any)}
                  className={`tab-btn ${activeTab === tab ? 'active' : ''}`}
                  style={{ fontSize: '0.6rem', padding: '0.5rem 1rem' }}
               >
                  {tab}
               </button>
             ))}
          </div>
       </header>

       <div className="grid-responsive" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))' }}>
          
          <div style={{ gridColumn: 'span 2' }}>
             <AnimatePresence mode="wait">
                {activeTab === 'OPERATIONS' && (
                  <motion.div key="ops" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}>
                     <div className="card">
                        <SectionTitle icon={Layout} label="ACTIVE_OPERATIONS_METRICS" />
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem', marginTop: '1rem' }}>
                           <StatBox label="TOTAL_UPLINKS" value={String(intel.length + 24)} color="#3498db" />
                           <StatBox label="DATA_FLOW" value="1.2 GB/s" color="#2ecc71" />
                           <StatBox label="THREAT_LEVEL" value="LOW" color="#f1c40f" />
                        </div>
                        <div style={{ marginTop: '2rem' }}>
                           <p style={{ fontSize: '0.8rem', opacity: 0.5 }}>System load is stable. {intel.length} new intel entries captured today.</p>
                        </div>
                     </div>
                  </motion.div>
                )}

                {activeTab === 'INTEL' && (
                  <motion.div key="intel" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}>
                     <div className="card">
                        <SectionTitle icon={Database} label="HARVESTED_INTEL_VAULT" />
                        <div style={{ maxHeight: '600px', overflowY: 'auto' }}>
                           <table style={{ width: '100%', fontSize: '0.7rem', borderCollapse: 'collapse', marginTop: '1rem' }}>
                              <thead style={{ opacity: 0.3, textAlign: 'left', position: 'sticky', top: 0, background: 'var(--card-bg)' }}>
                                 <tr>
                                    <th style={{ padding: '10px' }}>TIMESTAMP</th>
                                    <th>SOURCE/PLATFORM</th>
                                    <th>DATA_EXTRACTED</th>
                                    <th>STATUS</th>
                                 </tr>
                              </thead>
                              <tbody>
                                 {intel.length === 0 ? (
                                    <tr>
                                       <td colSpan={4} style={{ textAlign: 'center', padding: '3rem', opacity: 0.3 }}>VAULT_EMPTY_AWAITING_UPLINK...</td>
                                    </tr>
                                 ) : (
                                    intel.map((entry) => (
                                       <tr key={entry.id} style={{ borderBottom: '1px solid #111' }}>
                                          <td style={{ padding: '10px', opacity: 0.5 }}>{new Date(entry.timestamp).toLocaleString()}</td>
                                          <td style={{ fontWeight: 'bold' }}>{entry.platform.toUpperCase()}</td>
                                          <td>
                                             <pre style={{ fontSize: '0.6rem', color: 'var(--accent-color)', margin: 0 }}>
                                                {JSON.stringify(entry.data, null, 1)}
                                             </pre>
                                          </td>
                                          <td style={{ color: '#2ecc71' }}>VERIFIED</td>
                                       </tr>
                                    ))
                                 )}
                                 {/* Mock entries for aesthetic */}
                                 {[
                                    { ts: '2026-06-05 10:12:03', src: 'DEV_8821', type: 'KEYLOG_DUMP', data: '{ "keys": "admin123" }' },
                                    { ts: '2026-06-05 09:45:12', src: 'DEV_1102', type: 'WEBCAM_SNAP', data: '[BLOB_DATA]' },
                                 ].map((row, i) => (
                                    <tr key={'mock'+i} style={{ borderBottom: '1px solid #111', opacity: 0.4 }}>
                                       <td style={{ padding: '10px' }}>{row.ts}</td>
                                       <td style={{ fontWeight: 'bold' }}>{row.src}</td>
                                       <td style={{ color: 'var(--accent-color)' }}>{row.data}</td>
                                       <td>ARCHIVED</td>
                                    </tr>
                                 ))}
                              </tbody>
                           </table>
                        </div>
                     </div>
                  </motion.div>
                )}

                {activeTab === 'USERS' && (
                   <motion.div key="users" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}>
                      <div className="card">
                         <SectionTitle icon={Shield} label="OPERATOR_MANAGEMENT" />
                         <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem', background: '#050505', border: '1px solid #111' }}>
                               <div>
                                  <div style={{ fontWeight: 'bold' }}>talha@realhackers.hq</div>
                                  <div style={{ fontSize: '0.6rem', color: '#2ecc71' }}>ROLE: ROOT_ADMIN</div>
                               </div>
                               <button className="btn" style={{ fontSize: '0.6rem' }}>REVOKE</button>
                            </div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem', background: '#050505', border: '1px solid #111' }}>
                               <div>
                                  <div style={{ fontWeight: 'bold' }}>guest@realhackers.hq</div>
                                  <div style={{ fontSize: '0.6rem', color: '#f1c40f' }}>ROLE: OPERATOR</div>
                               </div>
                               <button className="btn" style={{ fontSize: '0.6rem' }}>REVOKE</button>
                            </div>
                         </div>
                      </div>
                   </motion.div>
                )}

                {activeTab === 'SETTINGS' && (
                  <motion.div key="settings" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} className="card">
                     <SectionTitle icon={Layout} label="SYSTEM_PREFERENCES" />
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

                        <button className="btn" style={{ width: 'fit-content' }} onClick={() => toast.success("Settings Saved")}>
                           <Save size={16} /> COMMIT_CHANGES
                        </button>
                     </div>
                  </motion.div>
                )}
             </AnimatePresence>
          </div>

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
                   <span>INTEL_VAULT_SYNC</span>
                   <span style={{ color: '#2ecc71' }}>{intel.length > 0 ? 'ACTIVE' : 'IDLE'}</span>
                </div>
             </div>
          </div>

       </div>

    </div>
  );
};

const SectionTitle: React.FC<{ icon: any, label: string }> = ({ icon: Icon, label }) => (
   <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '2rem' }}>
      <Icon size={20} color="var(--accent-color)" />
      <h3>{label}</h3>
   </div>
);

const StatBox: React.FC<{ label: string, value: string, color: string }> = ({ label, value, color }) => (
   <div style={{ background: '#050505', border: '1px solid #111', padding: '1rem', borderRadius: '4px', borderLeft: `4px solid ${color}` }}>
      <div style={{ fontSize: '0.5rem', opacity: 0.4, fontWeight: '900', marginBottom: '5px' }}>{label}</div>
      <div style={{ fontSize: '1.2rem', fontWeight: '900', fontFamily: 'monospace' }}>{value}</div>
   </div>
);

export default AdminPage;
