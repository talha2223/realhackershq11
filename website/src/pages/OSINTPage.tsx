import React, { useState, useEffect } from 'react';
import { Globe, Search, Activity, User, Mail, MapPin } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'sonner';

const OSINTPage: React.FC = () => {
  const [target, setTarget] = useState('');
  const [isScanning, setIsScanning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [results, setResults] = useState<any[] | null>(null);

  useEffect(() => {
    document.title = "RealHackers HQ // OSINT Suite";
  }, []);

  const runScan = () => {
    if (!target) return;
    setIsScanning(true);
    setProgress(0);
    setResults(null);

    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setIsScanning(false);
          setResults([
            { category: 'Social Media', findings: ['Twitter: @target_found', 'LinkedIn: Professional Profile (Match 89%)'], icon: User },
            { category: 'Breach Data', findings: ['Found in 2021 Canva Leak', 'Found in 2019 Adobe Leak'], icon: Mail },
            { category: 'Geolocation', findings: ['Estimated IP: 182.22.XX.XX', 'Region: Punjab, Pakistan'], icon: MapPin },
          ]);
          toast.success("SCAN_COMPLETE: Intel records updated.");
          return 100;
        }
        return prev + 5;
      });
    }, 150);
  };

  return (
    <div className="container" style={{ maxWidth: '1000px' }}>
      <header style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '3rem' }}>
        <Globe size={32} color="var(--accent-color)" />
        <h1 style={{ letterSpacing: '4px' }}>OSINT_RECON_SUITE</h1>
      </header>

      <div className="card" style={{ padding: '2.5rem' }}>
        <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem' }}>
          <div style={{ flex: 1, position: 'relative' }}>
            <Search size={18} style={{ position: 'absolute', left: '15px', top: '50%', transform: 'translateY(-50%)', opacity: 0.3 }} />
            <input 
              type="text" value={target} onChange={e => setTarget(e.target.value)}
              placeholder="ENTER_EMAIL_USERNAME_OR_IP..."
              style={{ width: '100%', padding: '1.2rem 1.2rem 1.2rem 3rem', background: '#000', border: '1px solid #222', color: '#fff', fontSize: '1rem', outline: 'none' }}
            />
          </div>
          <button onClick={runScan} disabled={isScanning} className="btn" style={{ padding: '0 2rem', borderColor: 'var(--accent-color)' }}>
            {isScanning ? 'SCANNING...' : 'EXECUTE_RECON'}
          </button>
        </div>

        <AnimatePresence>
          {isScanning && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} style={{ marginTop: '2rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', marginBottom: '0.5rem', opacity: 0.5 }}>
                <span>QUERYING_GLOBAL_DATABASES...</span>
                <span>{progress}%</span>
              </div>
              <div style={{ height: '2px', background: '#111', width: '100%' }}>
                <motion.div style={{ height: '100%', background: 'var(--accent-color)', width: `${progress}%` }} />
              </div>
            </motion.div>
          )}

          {results && (
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} style={{ marginTop: '3rem', display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1.5rem' }}>
               {results.map((res, i) => (
                 <div key={i} className="card" style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid #111' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '1rem', opacity: 0.4 }}>
                       <res.icon size={14} />
                       <span style={{ fontSize: '0.6rem', fontWeight: 'bold' }}>{res.category.toUpperCase()}</span>
                    </div>
                    {res.findings.map((f: string, j: number) => (
                      <div key={j} style={{ fontSize: '0.8rem', marginBottom: '0.5rem', color: '#fff' }}>{f}</div>
                    ))}
                 </div>
               ))}
            </motion.div>
          )}
        </AnimatePresence>

        {!isScanning && !results && (
          <div style={{ textAlign: 'center', marginTop: '4rem', opacity: 0.1 }}>
             <Activity size={64} style={{ margin: '0 auto 1rem' }} />
             <p style={{ letterSpacing: '2px' }}>WAITING_FOR_TARGET_INPUT</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default OSINTPage;
