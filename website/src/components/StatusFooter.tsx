import React, { useState, useEffect } from 'react';
import { useAuth } from './AuthContext';
import { Shield, Activity, Clock } from 'lucide-react';

const StatusFooter: React.FC = () => {
  const { user } = useAuth();
  const [uptime, setUptime] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setUptime(prev => prev + 1);
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const formatTime = (seconds: number) => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  return (
    <div className="status-bar">
      <div className="status-item">
        <div className="status-dot"></div>
        <span>SYSTEM: ENCRYPTED</span>
      </div>
      
      <div className="status-item">
        <Activity size={10} />
        <span>OPS_SEC: 100%</span>
      </div>

      <div className="status-item">
        <Shield size={10} />
        <span>OP: {user?.email?.split('@')[0].toUpperCase()}</span>
      </div>

      <div className="status-item">
        <Clock size={10} />
        <span>UPTIME: {formatTime(uptime)}</span>
      </div>

      <div style={{ marginLeft: 'auto', display: 'flex', gap: '20px' }}>
        <span>NODE_HF: RUNNING</span>
        <span>DB_SQL: READY</span>
      </div>
    </div>
  );
};

export default StatusFooter;
