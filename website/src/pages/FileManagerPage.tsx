import React, { useState, useCallback, useEffect } from 'react';
import {
  HardDrive, Search, ArrowLeft, Download,
  RefreshCw, Home, ChevronRight
} from 'lucide-react';
import { motion } from 'framer-motion';
import { toast } from 'sonner';

interface FileItem {
  name: string; path: string; is_dir: boolean;
  size?: number; modified?: number;
}

interface DriveInfo {
  device: string; mount: string; fstype: string;
  total?: number; used?: number; free?: number; percent?: number;
}

const API_BASE = localStorage.getItem('hdex_url') || 'https://talhasss-hdex-ultra-server.hf.space';
const BOT_TOKEN = localStorage.getItem('hdex_token') || 'hdex_admin_2026';

const formatSize = (bytes?: number): string => {
  if (!bytes) return '';
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  let i = 0; let b = bytes;
  while (b >= 1024 && i < units.length - 1) { b /= 1024; i++; }
  return `${b.toFixed(1)} ${units[i]}`;
};

const formatDate = (ts?: number): string => {
  if (!ts) return '';
  return new Date(ts * 1000).toLocaleString();
};

const FolderIcon = (props: any) => <svg {...props} viewBox="0 0 48 48" fill="none"><path d="M6 12a2 2 0 0 1 2-2h12l4 4h16a2 2 0 0 1 2 2v22a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2V12z" fill="#f1c40f"/><path d="M6 14a2 2 0 0 1 2-2h16l4 4h12a2 2 0 0 1 2 2v6H6v-10z" fill="#f7dc6f" opacity="0.6"/></svg>;
const FileIcon = (props: any) => <svg {...props} viewBox="0 0 48 48" fill="none"><path d="M10 4a2 2 0 0 0-2 2v36a2 2 0 0 0 2 2h28a2 2 0 0 0 2-2V16L30 4H10z" fill="#e0e0e0"/><path d="M30 4v10a2 2 0 0 0 2 2h10L30 4z" fill="#c0c0c0"/></svg>;
const ImgIcon = (props: any) => <svg {...props} viewBox="0 0 48 48" fill="none"><path d="M10 4a2 2 0 0 0-2 2v36a2 2 0 0 0 2 2h28a2 2 0 0 0 2-2V16L30 4H10z" fill="#3498db"/><path d="M30 4v10a2 2 0 0 0 2 2h10L30 4z" fill="#2980b9"/><circle cx="18" cy="22" r="4" fill="#fff" opacity="0.8"/><path d="M10 38l8-10 6 8 4-6 8 10v2H10v-4z" fill="#fff" opacity="0.6"/></svg>;
const VdIcon = (props: any) => <svg {...props} viewBox="0 0 48 48" fill="none"><path d="M10 4a2 2 0 0 0-2 2v36a2 2 0 0 0 2 2h28a2 2 0 0 0 2-2V16L30 4H10z" fill="#9b59b6"/><path d="M30 4v10a2 2 0 0 0 2 2h10L30 4z" fill="#8e44ad"/><polygon points="20,20 20,32 32,26" fill="#fff" opacity="0.8"/></svg>;
const MusIcon = (props: any) => <svg {...props} viewBox="0 0 48 48" fill="none"><path d="M10 4a2 2 0 0 0-2 2v36a2 2 0 0 0 2 2h28a2 2 0 0 0 2-2V16L30 4H10z" fill="#2ecc71"/><path d="M30 4v10a2 2 0 0 0 2 2h10L30 4z" fill="#27ae60"/><circle cx="20" cy="32" r="4" fill="#fff" opacity="0.8"/><path d="M24 28l8-2v8" stroke="#fff" strokeWidth="2" fill="none" opacity="0.8"/></svg>;
const ArcIcon = (props: any) => <svg {...props} viewBox="0 0 48 48" fill="none"><path d="M10 4a2 2 0 0 0-2 2v36a2 2 0 0 0 2 2h28a2 2 0 0 0 2-2V16L30 4H10z" fill="#e67e22"/><path d="M30 4v10a2 2 0 0 0 2 2h10L30 4z" fill="#d35400"/><rect x="18" y="22" width="12" height="14" rx="2" fill="#fff" opacity="0.3"/><line x1="20" y1="26" x2="28" y2="26" stroke="#fff" strokeWidth="1.5" opacity="0.6"/><line x1="20" y1="30" x2="28" y2="30" stroke="#fff" strokeWidth="1.5" opacity="0.6"/></svg>;
const ExIcon = (props: any) => <svg {...props} viewBox="0 0 48 48" fill="none"><path d="M10 4a2 2 0 0 0-2 2v36a2 2 0 0 0 2 2h28a2 2 0 0 0 2-2V16L30 4H10z" fill="#e74c3c"/><path d="M30 4v10a2 2 0 0 0 2 2h10L30 4z" fill="#c0392b"/><text x="24" y="32" textAnchor="middle" fill="#fff" fontSize="10" fontWeight="bold" fontFamily="monospace">EXE</text></svg>;
const CdIcon = (props: any) => <svg {...props} viewBox="0 0 48 48" fill="none"><path d="M10 4a2 2 0 0 0-2 2v36a2 2 0 0 0 2 2h28a2 2 0 0 0 2-2V16L30 4H10z" fill="#1abc9c"/><path d="M30 4v10a2 2 0 0 0 2 2h10L30 4z" fill="#16a085"/><text x="24" y="32" textAnchor="middle" fill="#fff" fontSize="8" fontWeight="bold" fontFamily="monospace">&lt;/&gt;</text></svg>;
const TxtIcon = (props: any) => <svg {...props} viewBox="0 0 48 48" fill="none"><path d="M10 4a2 2 0 0 0-2 2v36a2 2 0 0 0 2 2h28a2 2 0 0 0 2-2V16L30 4H10z" fill="#95a5a6"/><path d="M30 4v10a2 2 0 0 0 2 2h10L30 4z" fill="#7f8c8d"/><line x1="16" y1="22" x2="32" y2="22" stroke="#fff" strokeWidth="1.5" opacity="0.6"/><line x1="16" y1="28" x2="28" y2="28" stroke="#fff" strokeWidth="1.5" opacity="0.6"/><line x1="16" y1="34" x2="30" y2="34" stroke="#fff" strokeWidth="1.5" opacity="0.6"/></svg>;

const getFileIcon = (name: string, isDir: boolean) => {
  if (isDir) return <FolderIcon size={36} />;
  const ext = name.split('.').pop()?.toLowerCase();
  if (['jpg','jpeg','png','gif','bmp','webp','ico'].includes(ext!)) return <ImgIcon size={36} />;
  if (['mp4','avi','mkv','mov','wmv'].includes(ext!)) return <VdIcon size={36} />;
  if (['mp3','wav','flac','aac','ogg'].includes(ext!)) return <MusIcon size={36} />;
  if (['zip','rar','7z','tar','gz'].includes(ext!)) return <ArcIcon size={36} />;
  if (['exe','msi','bat','cmd','ps1'].includes(ext!)) return <ExIcon size={36} />;
  if (['html','css','js','ts','py','java','cpp','c','go','rs'].includes(ext!)) return <CdIcon size={36} />;
  if (['txt','md','json','xml','csv','log'].includes(ext!)) return <TxtIcon size={36} />;
  return <FileIcon size={36} />;
};

const FileManagerPage: React.FC = () => {
  const [currentPath, setCurrentPath] = useState('C:\\');
  const [items, setItems] = useState<FileItem[]>([]);
  const [drives, setDrives] = useState<DriveInfo[]>([]);
  const [showDrives, setShowDrives] = useState(true);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<FileItem[]>([]);
  const [searching, setSearching] = useState(false);
  const [selectedItem, setSelectedItem] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'icons' | 'list'>('icons');

  const fetchDrives = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/fm/drive`, {
        headers: { 'x-adex-bot-token': BOT_TOKEN }
      });
      const data = await res.json();
      if (data.drives) setDrives(data.drives);
    } catch { }
  }, []);

  const fetchPath = useCallback(async (path: string) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/fm/list?path=${encodeURIComponent(path)}`, {
        headers: { 'x-adex-bot-token': BOT_TOKEN }
      });
      const data = await res.json();
      if (data.items) {
        setItems(data.items);
        setCurrentPath(data.path);
        setShowDrives(false);
      }
    } catch { toast.error('Failed to load directory'); }
    setLoading(false);
  }, []);

  useEffect(() => { fetchDrives(); }, [fetchDrives]);

  const navigateTo = (path: string) => {
    setSearchResults([]);
    setSearchQuery('');
    fetchPath(path);
  };

  const goUp = () => {
    if (showDrives) return;
    const parent = currentPath.endsWith('\\') && currentPath.length > 3
      ? currentPath.slice(0, -1)
      : currentPath;
    const up = parent.substring(0, parent.lastIndexOf('\\'));
    if (up.length >= 2) {
      navigateTo(up + '\\');
    } else {
      setShowDrives(true);
    }
  };

  const goHome = () => setShowDrives(true);

  const doSearch = async () => {
    if (!searchQuery.trim()) return;
    setSearching(true);
    try {
      const root = currentPath || 'C:\\';
      const res = await fetch(`${API_BASE}/fm/search?root=${encodeURIComponent(root)}&pattern=${encodeURIComponent(searchQuery)}`, {
        headers: { 'x-adex-bot-token': BOT_TOKEN }
      });
      const data = await res.json();
      setSearchResults(data.results || []);
    } catch { toast.error('Search failed'); }
    setSearching(false);
  };

  const downloadFile = async (path: string) => {
    try {
      const res = await fetch(`${API_BASE}/fm/download?path=${encodeURIComponent(path)}`, {
        headers: { 'x-adex-bot-token': BOT_TOKEN }
      });
      const data = await res.json();
      if (data.content) {
        const blob = new Blob([Uint8Array.from(atob(data.content), c => c.charCodeAt(0))]);
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url; a.download = data.name; a.click();
        URL.revokeObjectURL(url);
        toast.success(`Downloaded ${data.name}`);
      }
    } catch { toast.error('Download failed'); }
  };

  const pathParts = showDrives
    ? [{ label: 'Drives', path: '' }]
    : currentPath.split('\\').filter(Boolean).reduce((acc: {label:string,path:string}[], part, i, arr) => {
        const p = arr.slice(0, i + 1).join('\\') + '\\';
        acc.push({ label: part, path: p });
        return acc;
      }, [{ label: 'Drives', path: '' }]);

  const displayItems = searchResults.length > 0 ? searchResults : items;

  return (
    <div className="container" style={{ paddingTop: '1rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
        <HardDrive size={28} color="#2ecc71" />
        <div>
          <h1 style={{ fontSize: '1.3rem', fontWeight: 900, letterSpacing: '3px' }}>FILE_MANAGER</h1>
          <div style={{ fontSize: '0.6rem', color: '#666', letterSpacing: '2px' }}>REMOTE_FILE_EXPLORER</div>
        </div>
      </div>

      <div className="card" style={{ padding: '0.8rem 1rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
        <button onClick={goHome} className="btn" style={{ padding: '0.4rem 0.8rem', fontSize: '0.65rem' }}><Home size={12} /></button>
        <button onClick={goUp} className="btn" style={{ padding: '0.4rem 0.8rem', fontSize: '0.65rem' }}><ArrowLeft size={12} /></button>
        <button onClick={() => fetchPath(currentPath)} className="btn" style={{ padding: '0.4rem 0.8rem', fontSize: '0.65rem' }}><RefreshCw size={12} /></button>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', flex: 1, fontSize: '0.75rem', fontFamily: 'monospace', color: '#888', overflow: 'hidden' }}>
          {pathParts.map((p, i) => (
            <React.Fragment key={p.path}>
              {i > 0 && <ChevronRight size={10} style={{ flexShrink: 0 }} />}
              <span onClick={() => p.path ? navigateTo(p.path) : goHome()} style={{ cursor: 'pointer', whiteSpace: 'nowrap', color: i === pathParts.length - 1 ? '#8b5cf6' : '#888' }}>{p.label}</span>
            </React.Fragment>
          ))}
        </div>
        <div style={{ display: 'flex', gap: '0.3rem' }}>
          <button onClick={() => setViewMode('icons')} className="btn" style={{ padding: '0.3rem 0.6rem', fontSize: '0.6rem', background: viewMode === 'icons' ? 'rgba(139,92,246,0.3)' : '' }}>ICONS</button>
          <button onClick={() => setViewMode('list')} className="btn" style={{ padding: '0.3rem 0.6rem', fontSize: '0.6rem', background: viewMode === 'list' ? 'rgba(139,92,246,0.3)' : '' }}>LIST</button>
        </div>
        <div style={{ display: 'flex', gap: '0.3rem', flexBasis: '100%', marginTop: '0.3rem' }}>
          <input value={searchQuery} onChange={e => setSearchQuery(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && doSearch()}
            placeholder="Search files..." style={{ flex: 1, background: '#0a0a0a', border: '1px solid #222', padding: '0.5rem 0.8rem', borderRadius: '6px', color: '#fff', fontSize: '0.75rem' }} />
          <button onClick={doSearch} disabled={searching} className="btn" style={{ padding: '0.4rem 1rem', fontSize: '0.65rem' }}>
            <Search size={12} /> {searching ? '...' : 'SEARCH'}
          </button>
        </div>
      </div>

      {showDrives ? (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: '0.8rem' }}>
          {drives.map(d => (
            <motion.div key={d.device} whileHover={{ scale: 1.02 }} className="card" style={{ padding: '1.2rem', cursor: 'pointer' }}
              onClick={() => navigateTo(d.mount)}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <HardDrive size={32} color={d.percent !== undefined && d.percent > 90 ? '#e74c3c' : '#2ecc71'} />
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 800, fontSize: '0.9rem' }}>{d.device.replace('\\', '')}</div>
                  <div style={{ fontSize: '0.6rem', color: '#666' }}>{d.mount} ({d.fstype})</div>
                  {d.total !== undefined && (
                    <div style={{ marginTop: '0.5rem' }}>
                      <div style={{ height: '4px', background: '#1a1a1a', borderRadius: '2px', overflow: 'hidden' }}>
                        <div style={{ height: '100%', width: `${d.percent || 0}%`, background: d.percent && d.percent > 90 ? '#e74c3c' : d.percent && d.percent > 70 ? '#f1c40f' : '#2ecc71', borderRadius: '2px' }} />
                      </div>
                      <div style={{ fontSize: '0.6rem', color: '#666', marginTop: '0.3rem', display: 'flex', justifyContent: 'space-between' }}>
                        <span>{formatSize(d.free)} free</span>
                        <span>{formatSize(d.total)} total</span>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      ) : (
        <>
          {loading ? (
            <div style={{ textAlign: 'center', padding: '3rem', color: '#555', fontFamily: 'monospace' }}>LOADING...</div>
          ) : displayItems.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '3rem', color: '#555', fontFamily: 'monospace' }}>EMPTY_DIRECTORY</div>
          ) : viewMode === 'icons' ? (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(120px, 1fr))', gap: '0.5rem' }}>
              {displayItems.map((item, i) => (
                <motion.div key={item.path} initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: i * 0.01 }}
                  onDoubleClick={() => item.is_dir && navigateTo(item.path)}
                  onClick={() => setSelectedItem(selectedItem === item.path ? null : item.path)}
                  className="card" style={{
                    padding: '0.8rem', cursor: 'pointer', textAlign: 'center',
                    border: selectedItem === item.path ? '1px solid #8b5cf6' : '1px solid #1a1a1a',
                    background: selectedItem === item.path ? 'rgba(139,92,246,0.1)' : ''
                  }}>
                  <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '0.3rem' }}>
                    {getFileIcon(item.name, item.is_dir)}
                  </div>
                  <div style={{ fontSize: '0.6rem', fontWeight: 600, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{item.name}</div>
                  <div style={{ fontSize: '0.5rem', color: '#555' }}>{item.is_dir ? 'Folder' : formatSize(item.size)}</div>
                  {selectedItem === item.path && (
                    <div style={{ display: 'flex', gap: '0.3rem', justifyContent: 'center', marginTop: '0.3rem' }}>
                      {!item.is_dir && <button onClick={() => downloadFile(item.path)} className="btn" style={{ padding: '0.2rem 0.5rem', fontSize: '0.5rem' }}><Download size={10} /></button>}
                    </div>
                  )}
                </motion.div>
              ))}
            </div>
          ) : (
            <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
              {displayItems.map((item, i) => (
                <div key={item.path} onDoubleClick={() => item.is_dir && navigateTo(item.path)}
                  onClick={() => setSelectedItem(selectedItem === item.path ? null : item.path)}
                  style={{
                    display: 'flex', alignItems: 'center', gap: '0.8rem', padding: '0.6rem 1rem',
                    borderBottom: '1px solid #111', cursor: 'pointer',
                    background: selectedItem === item.path ? 'rgba(139,92,246,0.1)' : i % 2 === 0 ? 'rgba(255,255,255,0.02)' : ''
                  }}>
                  {getFileIcon(item.name, item.is_dir)}
                  <div style={{ flex: 1, fontSize: '0.75rem', fontWeight: 600 }}>{item.name}</div>
                  <div style={{ fontSize: '0.6rem', color: '#666', width: '70px', textAlign: 'right' }}>{item.is_dir ? '<DIR>' : formatSize(item.size)}</div>
                  <div style={{ fontSize: '0.55rem', color: '#555', width: '140px', textAlign: 'right' }}>{formatDate(item.modified)}</div>
                  {!item.is_dir && <button onClick={() => downloadFile(item.path)} className="btn" style={{ padding: '0.2rem 0.5rem', fontSize: '0.5rem' }}><Download size={10} /></button>}
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default FileManagerPage;
