import React, { useState, useEffect } from 'react';
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom';
import BackgroundVideo from '../components/BackgroundVideo';
import LoadingScreen from '../components/LoadingScreen';
import { LoadingProvider } from '../components/LoadingContext';
import DataParticles from '../components/DataParticles';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../components/AuthContext';
import { LogOut, Menu, X, Terminal, Sun, Moon, Volume2, VolumeX, ShieldAlert } from 'lucide-react';
import StatusFooter from '../components/StatusFooter';
import { Toaster, toast } from 'sonner';

const MainLayout: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [isTerminating, setIsTerminating] = useState(false);
  const [oledMode, setOledMode] = useState(false);
  const [soundEnabled, setSoundEnabled] = useState(localStorage.getItem('hq_sound') === 'true');

  useEffect(() => {
    localStorage.setItem('hq_sound', soundEnabled.toString());
  }, [soundEnabled]);

  const playSound = (type: 'click' | 'alert' | 'success') => {
    if (!soundEnabled) return;
    console.log(`BEEP: ${type}`);
  };

  const handleLogout = async () => {
    playSound('alert');
    setIsTerminating(true);
    setTimeout(async () => {
      await logout();
      setIsTerminating(false);
      navigate('/');
    }, 2500);
  };

  const closeMenu = () => setMobileMenuOpen(false);

  useEffect(() => {
    if (user) {
      toast.success(`OPERATOR_AUTHORIZED: ${user.email?.split('@')[0].toUpperCase()}`, {
        description: 'Session initialized with RSA-4096 encryption.',
        style: { background: '#000', color: '#fff', border: '1px solid #222' }
      });
    }
  }, [user]);

  return (
    <LoadingProvider>
      <Toaster position="bottom-right" theme="dark" />
      <div style={{ backgroundColor: oledMode ? '#000000' : 'transparent', minHeight: '100vh', transition: 'background-color 0.3s' }}>
        <AnimatePresence>
          {isTerminating && (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="terminal-exit"
            >
              <Terminal size={48} className="spin" color="#f55" />
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: "200px" }}
                transition={{ duration: 2 }}
                style={{ height: '2px', background: '#f55' }}
              />
              <h2 style={{ letterSpacing: '8px', color: '#f55' }}>SESSION_TERMINATED</h2>
              <p style={{ fontSize: '0.6rem', opacity: 0.5, fontFamily: 'monospace' }}>WIPING_ENCRYPTION_KEYS... DISCONNECTING_UPLINK...</p>
            </motion.div>
          )}
        </AnimatePresence>

        <div className="crt-overlay" />
        <div className="crt-flicker" />
        <LoadingScreen />
        <BackgroundVideo />
        <DataParticles />
        
        <div className="app-container">
          <nav>
            <div className="logo" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
               <ShieldAlert size={20} color="var(--accent-color)" />
               <span>RealHackers HQ</span>
            </div>
            
            <button className="hamburger" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
              {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>

            <div className={`nav-links ${mobileMenuOpen ? 'mobile-open' : ''}`}>
              {[
                { path: '/', label: 'Home' },
                { path: '/a-dex', label: 'A-Dex' },
                { path: '/h-dex', label: 'H-Dex' },
                { path: '/phishing', label: 'Phishing' },
                { path: '/osint', label: 'OSINT' },
                { path: '/danger', label: 'Danger' },
                { path: '/credits', label: 'Credits' },
                { path: '/docs', label: 'Docs' },
                { path: '/admin', label: 'Admin' },
                { path: '/about', label: 'About' },
                { path: '/contact', label: 'Contact' },
              ].map(link => (
                <Link 
                  key={link.path} 
                  to={link.path} 
                  className={location.pathname === link.path ? 'active' : ''}
                  onClick={() => { closeMenu(); playSound('click'); }}
                >
                  {link.label}
                </Link>
              ))}
              
              <div style={{ display: 'flex', gap: '12px', alignItems: 'center', marginLeft: '10px', padding: '10px' }}>
                <button 
                  onClick={() => { setSoundEnabled(!soundEnabled); playSound('click'); }}
                  style={{ background: 'none', border: '1px solid #222', color: soundEnabled ? '#0f0' : '#444', cursor: 'pointer', padding: '6px', borderRadius: '4px' }}
                  title="Toggle Audio"
                >
                  {soundEnabled ? <Volume2 size={12} /> : <VolumeX size={12} />}
                </button>

                <button 
                  onClick={() => { setOledMode(!oledMode); playSound('click'); }}
                  title={oledMode ? "Disable OLED" : "Enable OLED"}
                  style={{ background: 'none', border: '1px solid #222', color: oledMode ? '#fff' : '#444', cursor: 'pointer', padding: '6px', borderRadius: '4px' }}
                >
                  {oledMode ? <Sun size={12} /> : <Moon size={12} />}
                </button>

                <button 
                  onClick={handleLogout} 
                  style={{ background: 'rgba(231, 76, 60, 0.1)', border: '1px solid #e74c3c', color: '#e74c3c', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '5px', fontSize: '0.65rem', fontWeight: 'bold', padding: '6px 12px', borderRadius: '4px' }}
                >
                  <LogOut size={12} /> EXIT
                </button>
              </div>
            </div>
          </nav>
          
          <main style={{ paddingBottom: '80px' }}>
            <AnimatePresence mode="wait">
              <motion.div
                key={location.pathname}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 10 }}
                transition={{ duration: 0.2 }}
                className="page-container"
              >
                <Outlet />
              </motion.div>
            </AnimatePresence>
          </main>

          <StatusFooter />
        </div>
      </div>
    </LoadingProvider>
  );
};

export default MainLayout;
