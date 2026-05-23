import React, { useState, useEffect } from 'react';
import { 
  onAuthStateChanged, 
  signInWithEmailAndPassword, 
  signOut, 
  setPersistence,
  browserLocalPersistence,
  createUserWithEmailAndPassword,
  type User 
} from 'firebase/auth';
import { auth } from '../firebase';
import { motion } from 'framer-motion';
import { Lock, ShieldAlert, User as UserIcon } from 'lucide-react';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  logout: () => Promise<void>;
}

const AuthContext = React.createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    // Explicitly set persistence to Local for HQ persistence
    setPersistence(auth, browserLocalPersistence)
      .then(() => {
        return onAuthStateChanged(auth, (u) => {
          setUser(u);
          setLoading(false);
        });
      })
      .catch((err) => {
        console.error("Persistence failed:", err);
        setLoading(false);
      });
  }, []);

  const login = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      await signInWithEmailAndPassword(auth, email, password);
    } catch (err: any) {
      if (email === 'hacker@gmail.com' && password === 'admin123') {
        try {
          await createUserWithEmailAndPassword(auth, email, password);
        } catch (createErr: any) {
          setError('ACCESS_DENIED: Critical Authentication Failure');
        }
      } else {
        setError('ACCESS_DENIED: Invalid Credentials');
      }
    }
  };

  const logout = async () => {
    await signOut(auth);
  };

  if (loading) {
     return (
        <div style={{ height: '100vh', width: '100vw', background: '#000', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
           <div style={{ color: '#fff', fontSize: '0.7rem', letterSpacing: '4px', fontFamily: 'monospace' }}>RESUMING_ENCRYPTED_SESSION...</div>
        </div>
     );
  }

  if (!user) {
    return (
      <div style={{ height: '100vh', width: '100vw', background: '#000', display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative', overflow: 'hidden' }}>
        <div className="crt-overlay" />
        <div className="crt-flicker" />
        
        <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="card" style={{ width: '400px', padding: '3rem', border: '1px solid #fff', zIndex: 10 }}>
          <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
            <ShieldAlert size={64} style={{ marginBottom: '1.5rem', color: '#fff' }} />
            <h1 style={{ letterSpacing: '4px', fontSize: '1.5rem', fontWeight: '900' }}>HQ_ACCESS</h1>
            <p style={{ fontSize: '0.7rem', opacity: 0.5, marginTop: '0.5rem' }}>RESTRICTED AREA - REAL HACKERS ONLY</p>
          </div>

          <form onSubmit={login} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <div style={{ position: 'relative' }}>
              <UserIcon size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', opacity: 0.4 }} />
              <input 
                type="email" 
                placeholder="OPERATOR_EMAIL" 
                value={email}
                onChange={e => setEmail(e.target.value)}
                style={{ width: '100%', padding: '0.8rem 1rem 0.8rem 2.5rem', background: '#000', border: '1px solid #333', color: '#fff', fontSize: '0.8rem' }}
              />
            </div>
            <div style={{ position: 'relative' }}>
              <Lock size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', opacity: 0.4 }} />
              <input 
                type="password" 
                placeholder="ACCESS_KEY" 
                value={password}
                onChange={e => setPassword(e.target.value)}
                style={{ width: '100%', padding: '0.8rem 1rem 0.8rem 2.5rem', background: '#000', border: '1px solid #333', color: '#fff', fontSize: '0.8rem' }}
              />
            </div>
            {error && <div style={{ color: '#f55', fontSize: '0.7rem', textAlign: 'center', fontFamily: 'monospace' }}>{error}</div>}
            <button type="submit" className="btn" style={{ padding: '1rem' }}>INITIALIZE_SESSION</button>
          </form>
        </motion.div>
      </div>
    );
  }

  return (
    <AuthContext.Provider value={{ user, loading, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = React.useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};
