import React, { useState, useEffect } from 'react';
import { 
  ArrowLeft, 
  ArrowRight, 
  RotateCw, 
  Home, 
  Lock, 
  Star, 
  Share2, 
  Puzzle, 
  MoreVertical, 
  Plus, 
  X,
  ShieldAlert,
  ChevronDown,
  Folder
} from 'lucide-react';

interface Tab {
  id: string;
  title: string;
  url: string;
  icon: React.ReactNode;
  active: boolean;
}

interface BraveBrowserWrapperProps {
  children: React.ReactNode;
  activeTabUrl?: string;
  onUrlChange?: (url: string) => void;
  onTabChange?: (tabId: string) => void;
  tabs?: Tab[];
}

const BraveBrowserWrapper: React.FC<BraveBrowserWrapperProps> = ({ 
  children, 
  activeTabUrl = 'https://accounts.google.com',
  onUrlChange,
  onTabChange,
  tabs: initialTabs
}) => {
  const [url, setUrl] = useState(activeTabUrl);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    setUrl(activeTabUrl);
  }, [activeTabUrl]);

  const handleRefresh = () => {
    setIsLoading(true);
    setTimeout(() => setIsLoading(false), 500);
  };

  const handleUrlKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && onUrlChange) {
      onUrlChange(url);
      handleRefresh();
    }
  };

  return (
    <div className="brave-browser-container w-full h-full flex flex-col bg-[#1c1822] text-sm select-none overflow-hidden rounded-lg border border-[#2a2233] shadow-2xl font-sans">
      <style>{`
        .brave-browser-container {
          --brave-bg: #1c1822;
          --brave-tab-active: #2d2736;
          --brave-tab-inactive: #211c29;
          --brave-input: #15111b;
          --brave-border: #2a2233;
        }
        .smooth-transition {
          transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        }
        .scale-on-click {
          transition: transform 0.15s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        .scale-on-click:active {
          transform: scale(0.95);
        }
        .no-scrollbar::-webkit-scrollbar {
          display: none;
        }
        .no-scrollbar {
          -ms-overflow-style: none;
          scrollbar-width: none;
        }
        @keyframes viewFadeIn {
          from { opacity: 0; transform: translateY(8px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-view {
          animation: viewFadeIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }
        @keyframes textGradient {
          0% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
          100% { background-position: 0% 50%; }
        }
        .ig-gradient-text {
          background: linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%);
          background-size: 200% auto;
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          animation: textGradient 6s ease infinite;
        }
      `}</style>
      
      {/* TOP SECTION: TABS & WINDOW CONTROLS */}
      <div className="flex items-center justify-between bg-[#191520] pt-2 px-3 pb-0 select-none border-b border-[#2a2233]">
        <div className="flex items-end space-x-[2px] overflow-x-auto max-w-[85%] pr-4 no-scrollbar">
          {initialTabs?.map((tab) => (
            <div 
              key={tab.id}
              onClick={() => onTabChange?.(tab.id)}
              className={`group relative flex items-center space-x-2 px-3 py-2 cursor-pointer rounded-t-lg select-none transition-all duration-200 shrink-0 text-xs ${
                tab.active 
                  ? 'bg-[#2d2736] text-white font-medium border-t-2 border-purple-500 z-10' 
                  : 'bg-[#211c29] text-gray-400 hover:bg-[#251f2f]/80 hover:text-gray-200'
              }`}
              style={{ width: '145px' }}
            >
              <div className="flex items-center space-x-1.5 w-full overflow-hidden">
                <span className="shrink-0 scale-75">{tab.icon}</span>
                <span className="truncate pr-4">{tab.title}</span>
              </div>
              <button className="absolute right-2 opacity-0 group-hover:opacity-100 hover:bg-[#3d324e] hover:text-white rounded px-1 py-0.2 text-[9px] transition-all duration-150 text-gray-400">
                <X size={10} />
              </button>
            </div>
          ))}
          <button className="mb-1 px-2.5 py-1.5 text-gray-400 hover:text-white hover:bg-[#2d2736] rounded-md transition duration-200 scale-on-click text-xs">
            <Plus size={14} />
          </button>
        </div>

        <div className="flex items-center space-x-3 mb-2 ml-auto shrink-0 text-gray-400">
          <button className="hover:text-white transition duration-200">
            <ShieldAlert size={16} className="text-[#ff763b]" />
          </button>
          <div className="flex items-center space-x-4 pl-3 border-l border-gray-700/60 text-xs">
            <ArrowLeft size={14} className="hover:text-white cursor-pointer transition rotate-[-45deg]" />
            <div className="w-3 h-3 border border-gray-400 hover:border-white cursor-pointer transition"></div>
            <X size={14} className="hover:text-white cursor-pointer transition" />
          </div>
        </div>
      </div>

      {/* MIDDLE SECTION: TOOLBAR & URL BAR */}
      <div className="flex items-center space-x-3 px-3 py-2 bg-[#2d2736] border-b border-[#3c3349]/50 select-none">
        <div className="flex items-center space-x-4 text-gray-300">
          <button className="hover:text-white transition scale-on-click">
            <ArrowLeft size={16} />
          </button>
          <button className="hover:text-white transition scale-on-click">
            <ArrowRight size={16} />
          </button>
          <button onClick={handleRefresh} className={`hover:text-white transition scale-on-click ${isLoading ? 'animate-spin' : ''}`}>
            <RotateCw size={14} />
          </button>
          <button className="hover:text-white transition scale-on-click">
            <Home size={14} />
          </button>
        </div>

        <div className="flex-1 relative flex items-center">
          <div className="absolute left-3 text-gray-400 flex items-center space-x-1">
            <Lock size={10} className="text-emerald-500" />
            <span className="text-[10px] text-emerald-500 opacity-90 hidden sm:inline">Secure</span>
          </div>
          
          <input 
            type="text" 
            value={url} 
            onChange={(e) => setUrl(e.target.value)}
            onKeyDown={handleUrlKeyDown}
            className="w-full bg-[#15111b] hover:bg-[#1a1522] focus:bg-[#130f1a] focus:ring-1 focus:ring-purple-500/50 outline-none text-xs rounded-lg py-[6px] pl-[74px] pr-28 text-gray-200 border border-[#3e344e] transition"
          />
          
          <div className="absolute right-3 flex items-center space-x-3 text-gray-400 text-xs">
            <Star size={12} className="hover:text-yellow-400 cursor-pointer transition" />
            <span className="bg-[#ff4e00]/20 text-[#ff763b] px-1.5 py-0.5 rounded text-[10px] font-bold">1 Shields</span>
            <Share2 size={12} className="hover:text-white cursor-pointer transition" />
          </div>
        </div>

        <div className="flex items-center space-x-3 text-gray-300 pl-1">
          <Puzzle size={14} className="hover:text-white cursor-pointer transition" />
          <div className="w-6 h-6 rounded-full bg-gradient-to-tr from-[#9c27b0] to-[#e91e63] flex items-center justify-center text-[10px] font-bold text-white cursor-pointer">
            Z
          </div>
          <MoreVertical size={16} className="hover:text-white cursor-pointer transition px-1" />
        </div>
      </div>

      {/* BOOKMARKS BAR */}
      <div className="flex items-center justify-between px-4 py-1.5 bg-[#2d2736]/90 border-b border-[#3c3349]/30 text-xs text-gray-300 select-none">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-1.5 hover:text-white cursor-pointer transition">
            <Lock size={10} className="text-red-400" />
            <span>Google Sign in</span>
          </div>
          <div className="flex items-center space-x-1.5 hover:text-white cursor-pointer transition">
            <Lock size={10} className="text-blue-500" />
            <span>Facebook Log in</span>
          </div>
          <div className="flex items-center space-x-1.5 hover:text-white cursor-pointer transition">
            <Lock size={10} className="text-pink-400" />
            <span>Instagram</span>
          </div>
        </div>
        
        <div className="flex items-center space-x-1 hover:text-white cursor-pointer transition">
          <Folder size={12} className="text-yellow-500" />
          <span>Other favorites</span>
          <ChevronDown size={10} className="pl-0.5" />
        </div>
      </div>

      {/* MAIN VIEWPORT: WHERE PAGES RENDER */}
      <div className="flex-1 bg-neutral-900 overflow-y-auto relative no-scrollbar">
        {isLoading && (
          <div className="absolute inset-0 bg-black/70 z-50 flex items-center justify-center backdrop-blur-md">
            <div className="flex flex-col items-center space-y-4">
              <div className="w-10 h-10 border-4 border-purple-500 border-t-transparent rounded-full animate-spin"></div>
              <p className="text-xs font-semibold tracking-wider text-gray-300">Resolving host...</p>
            </div>
          </div>
        )}
        {children}
      </div>
    </div>
  );
};

export default BraveBrowserWrapper;
