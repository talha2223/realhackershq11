import React from 'react';
import { Globe } from 'lucide-react';

interface DefaultTemplateProps {
  url: string;
  onGoHome?: () => void;
}

const DefaultTemplate: React.FC<DefaultTemplateProps> = ({ url, onGoHome }) => {
  return (
    <div className="min-h-full w-full bg-[#18181b] text-neutral-300 flex flex-col items-center justify-center p-8 text-center select-none animate-view">
      <div className="max-w-md w-full bg-[#27272a] border border-neutral-700 rounded-2xl p-8 flex flex-col items-center space-y-4">
        <Globe className="text-4xl text-neutral-500 animate-pulse" size={48} />
        <h2 className="text-xl font-bold text-white">Simulated Navigation Success</h2>
        <p className="text-xs text-neutral-400">
          You successfully browsed to <span className="text-neutral-200 font-mono underline block mt-1">{url}</span>
        </p>
        <div className="text-[11px] text-neutral-500">
          All buttons and tab components in this frame are responsive. Use the bookmarks to access login pages.
        </div>
        {onGoHome && (
          <button onClick={onGoHome} className="bg-neutral-800 hover:bg-neutral-700 text-white text-xs font-bold py-2 px-4 rounded-lg transition">
            Go Home
          </button>
        )}
      </div>
    </div>
  );
};

export default DefaultTemplate;
