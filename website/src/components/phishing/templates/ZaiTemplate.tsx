import React from 'react';
import { Sparkles, ArrowRight } from 'lucide-react';

interface ZaiTemplateProps {
  onSuccess: (data: any) => void;
}

const ZaiTemplate: React.FC<ZaiTemplateProps> = ({ onSuccess }) => {
  return (
    <div className="min-h-full w-full bg-[#0d0a14] text-[#ecebf0] flex flex-col justify-between font-sans select-none animate-view">
      <header className="flex items-center justify-between border-b border-white/5 px-6 py-4 backdrop-blur-md bg-black/25">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 rounded bg-gradient-to-tr from-purple-600 to-pink-500 flex items-center justify-center text-xs font-bold">Z</div>
          <span className="font-bold tracking-tight text-white font-jakarta">Z.ai Platform</span>
        </div>
        <div className="flex items-center space-x-4 text-xs text-neutral-400">
          <a href="#" className="hover:text-white transition">Research</a>
          <a href="#" className="hover:text-white transition">API Keys</a>
          <a href="#" className="hover:text-white transition">Docs</a>
          <button className="bg-white/10 hover:bg-white/20 text-white rounded-lg px-3 py-1.5 transition">Dashboard</button>
        </div>
      </header>

      <main className="flex-1 max-w-[800px] mx-auto w-full flex flex-col justify-center items-center px-6 py-16 space-y-8">
        <div className="flex flex-col items-center text-center space-y-4">
          <span className="bg-purple-500/10 text-purple-400 border border-purple-500/20 text-[10px] font-bold tracking-widest uppercase px-3 py-1 rounded-full">AI Workspace</span>
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-white leading-tight font-jakarta">
            Create and run custom workflows.
          </h1>
          <p className="text-neutral-400 max-w-[500px] text-sm">
            The premium, open-source environment built with lightning-fast speeds for designers and engineers.
          </p>
        </div>

        <div className="w-full bg-[#161220] border border-white/10 rounded-2xl p-4 flex flex-col space-y-3">
          <div className="flex items-center space-x-2">
            <Sparkles size={12} className="text-purple-400" />
            <span className="text-xs text-neutral-400 font-medium">Prompt Assistant</span>
          </div>
          <textarea 
            placeholder="Ask Z.ai to build a workflow, generate responsive UI assets..." 
            className="w-full bg-transparent border-none outline-none resize-none text-sm text-white placeholder-neutral-500 h-24"
            onKeyDown={(e) => {
              if (e.key === 'Enter' && e.ctrlKey) {
                onSuccess({ platform: 'Zai', prompt: e.currentTarget.value });
              }
            }}
          ></textarea>
          <div className="flex justify-between items-center">
            <span className="text-[10px] text-neutral-500">Ctrl + Enter to prompt</span>
            <button 
              onClick={() => onSuccess({ platform: 'Zai', action: 'generate' })}
              className="bg-white hover:bg-neutral-200 text-black text-xs font-bold px-4 py-2 rounded-lg transition scale-on-click"
            >
              Generate <ArrowRight size={10} className="inline ml-1" />
            </button>
          </div>
        </div>
      </main>

      <footer className="text-center py-6 border-t border-white/5 text-[10px] text-neutral-600">
        Z.ai Global Inc © 2026
      </footer>
    </div>
  );
};

export default ZaiTemplate;
