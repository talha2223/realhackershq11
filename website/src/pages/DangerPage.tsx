import React, { useState, useEffect } from 'react';
import { Terminal } from 'lucide-react';

const DangerPage: React.FC = () => {
  const [history, setHistory] = useState<string[]>(['REALHACKERS_HQ // DANGER_TERMINAL v1.0', 'TYPE "HELP" FOR AVAILABLE COMMANDS.']);
  const [input, setInput] = useState('');
  const terminalEndRef = React.useRef<HTMLDivElement>(null);

  useEffect(() => {
    document.title = "RealHackers HQ // Danger Terminal";
    terminalEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [history]);

  const handleCommand = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const cmd = input.trim().toLowerCase();
    const newHistory = [...history, `> ${input}`];
    
    switch (cmd) {
      case 'help':
        newHistory.push('AVAILABLE COMMANDS:', ' - SCAN: INVENTORY NETWORK ASSETS', ' - EXPLOIT [TARGET]: ATTEMPT CVE INJECTION', ' - PAYLOAD: GENERATE STEALTH APK', ' - CLEAR: PURGE TERMINAL HISTORY', ' - EXIT: DISCONNECT UPLINK');
        break;
      case 'scan':
        newHistory.push('SCANNING_NETWORK...', 'FOUND 3 VULNERABLE ASSETS:', ' [!] 192.168.1.45 (Android 11) - CVE-2023-4012', ' [!] 192.168.1.102 (Windows 10) - MS17-010', ' [!] 192.168.1.156 (Ubuntu 20.04) - Log4Shell');
        break;
      case 'clear':
        setHistory([]);
        setInput('');
        return;
      case 'payload':
        newHistory.push('GENERATING_STEALTH_PAYLOAD...', 'ENCRYPTING_STAGERS...', 'APK_READY: /assets/adex_update_signed.apk');
        break;
      default:
        newHistory.push(`UNKNOWN_COMMAND: ${cmd}`);
    }

    setHistory(newHistory);
    setInput('');
  };

  return (
    <div className="container" style={{ maxWidth: '1000px', height: '80vh', display: 'flex', flexDirection: 'column' }}>
      <div className="card" style={{ flex: 1, display: 'flex', flexDirection: 'column', padding: '1.5rem', border: '1px solid #e74c3c', background: 'rgba(20, 0, 0, 0.9)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem', marginBottom: '1.5rem', borderBottom: '1px solid rgba(231, 76, 60, 0.3)', paddingBottom: '0.8rem' }}>
          <Terminal size={20} color="#e74c3c" />
          <span style={{ fontWeight: '900', letterSpacing: '2px', fontSize: '0.8rem' }}>DANGER_ZONE // TERMINAL_ACCESS</span>
        </div>

        <div style={{ flex: 1, overflowY: 'auto', fontFamily: 'JetBrains Mono, monospace', fontSize: '0.85rem', color: '#e74c3c' }}>
          {history.map((line, i) => (
            <div key={i} style={{ marginBottom: '4px' }}>{line}</div>
          ))}
          <div ref={terminalEndRef} />
        </div>

        <form onSubmit={handleCommand} style={{ marginTop: '1.5rem', display: 'flex', gap: '10px' }}>
          <span style={{ color: '#e74c3c', fontWeight: 'bold' }}>#</span>
          <input 
            autoFocus
            type="text" 
            value={input} 
            onChange={e => setInput(e.target.value)}
            style={{ flex: 1, background: 'transparent', border: 'none', color: '#e74c3c', outline: 'none', fontFamily: 'JetBrains Mono, monospace' }}
            placeholder="ENTER_COMMAND..."
          />
        </form>
      </div>
    </div>
  );
};

export default DangerPage;
