import React, { useEffect, useRef } from 'react';
import { 
  Terminal as TerminalIcon, 
  List, Code
} from 'lucide-react';

const DangerPage: React.FC = () => {
  const [history, setLogs] = useState<string[]>([
    'Initializing DANGER_AGENT v4.0.2...',
    'Loading exploitation modules... OK',
    'Establishing C2 secure bridge... OK',
    'Type "help" for available commands.'
  ]);
  const [input, setInput] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    document.title = "RealHackers HQ // Danger Agent Coming Soon";
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [history]);

  const handleCommand = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const cmd = input.trim().toLowerCase();
    const newHistory = [...history, `op@hq:~$ ${input}`];

    let response = '';
    if (cmd === 'help') {
       response = 'Available commands: scan, exploit, payloads, listeners, clear, sysinfo';
    } else if (cmd === 'scan') {
       response = 'Scanning global grid... Found 142 vulnerable nodes.';
    } else if (cmd === 'payloads') {
       response = 'Payloads: [1] win_x64_exe, [2] lin_x64_elf, [3] and_v8_apk';
    } else if (cmd === 'sysinfo') {
       response = 'OS: Kali GNU/Linux, KERNEL: 6.1.0-hq, ARCH: x86_64';
    } else if (cmd === 'clear') {
       setLogs([]);
       setInput('');
       return;
    } else {
       response = `Command not found: ${cmd}`;
    }

    setLogs([...newHistory, response]);
    setInput('');
  };

  return (
    <div className="container" style={{ maxWidth: '1600px', padding: '1rem' }}>
       
       <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem', background: 'rgba(231, 76, 60, 0.05)', padding: '1.2rem', border: '1px solid #333' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
            <TerminalIcon size={28} color="var(--accent-color)" />
            <h1 style={{ fontSize: '1.4rem', fontWeight: '900', letterSpacing: '4px' }}>DANGER // EXPLOIT</h1>
          </div>
          <div style={{ display: 'flex', gap: '20px', fontSize: '0.7rem', color: '#666', fontFamily: 'monospace' }}>
             <div>C2_LINK: <span style={{ color: '#2ecc71' }}>ACTIVE</span></div>
             <div>NODES: <span style={{ color: '#fff' }}>142</span></div>
          </div>
       </header>

       <div style={{ display: 'grid', gridTemplateColumns: '1fr 350px', gap: '1.5rem', height: '600px' }}>
          
          {/* Terminal UI */}
          <div className="card" style={{ background: '#050505', display: 'flex', flexDirection: 'column', padding: '1rem', border: '1px solid #222' }}>
             <div ref={scrollRef} style={{ flex: 1, overflowY: 'auto', fontFamily: 'JetBrains Mono, monospace', fontSize: '0.85rem', color: '#0f0', textShadow: '0 0 5px rgba(0,255,0,0.3)' }}>
                {history.map((line, i) => (
                  <div key={i} style={{ marginBottom: '5px' }}>{line}</div>
                ))}
             </div>
             <form onSubmit={handleCommand} style={{ display: 'flex', marginTop: '1rem', borderTop: '1px solid #111', paddingTop: '1rem' }}>
                <span style={{ color: '#0f0', marginRight: '10px' }}>op@hq:~$</span>
                <input 
                   autoFocus type="text" value={input} onChange={e => setInput(e.target.value)}
                   style={{ flex: 1, background: 'transparent', border: 'none', color: '#fff', outline: 'none', fontFamily: 'inherit' }}
                />
             </form>
          </div>

          {/* Sidebar Tools */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
             <div className="card" style={{ padding: '1.2rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1.5rem', borderBottom: '1px solid #222', paddingBottom: '0.6rem' }}>
                  <Code size={16} /> <span style={{ fontWeight: 'bold', fontSize: '0.7rem' }}>PAYLOAD_GEN</span>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                   <select style={{ background: '#000', border: '1px solid #333', color: '#fff', padding: '0.8rem', fontSize: '0.75rem' }}>
                      <option>Windows (.exe)</option>
                      <option>Linux (.elf)</option>
                      <option>Android (.apk)</option>
                   </select>
                   <button className="btn" style={{ width: '100%' }}>GENERATE_BUILD</button>
                </div>
             </div>

             <div className="card" style={{ flex: 1, padding: '1.2rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1.5rem', borderBottom: '1px solid #222', paddingBottom: '0.6rem' }}>
                  <List size={16} /> <span style={{ fontWeight: 'bold', fontSize: '0.7rem' }}>ACTIVE_LISTENERS</span>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
                   {[
                     { port: 4444, type: 'TCP_REVERSE', status: 'ON' },
                     { port: 8080, type: 'HTTP_SSL', status: 'ON' },
                   ].map(l => (
                     <div key={l.port} style={{ padding: '1rem', border: '1px solid #111', borderRadius: '4px', position: 'relative' }}>
                        <div style={{ fontSize: '0.8rem', fontWeight: 'bold' }}>PORT: {l.port}</div>
                        <div style={{ fontSize: '0.6rem', color: '#555' }}>TYPE: {l.type}</div>
                        <div style={{ position: 'absolute', top: '1rem', right: '1rem', width: '6px', height: '6px', background: '#0f0', borderRadius: '50%' }} />
                     </div>
                   ))}
                   <button className="btn" style={{ marginTop: 'auto', borderStyle: 'dashed' }}>+ CREATE_NEW</button>
                </div>
             </div>
          </div>

       </div>
    </div>
  );
};

export default DangerPage;
