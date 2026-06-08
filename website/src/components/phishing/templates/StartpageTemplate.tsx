import React from 'react';
import { Search, Keyboard } from 'lucide-react';

interface StartpageTemplateProps {
  onSuccess: (data: any) => void;
}

const StartpageTemplate: React.FC<StartpageTemplateProps> = () => {
  return (
    <div className="min-h-full w-full bg-[#111625] text-white flex flex-col justify-between items-center py-20 px-6 select-none animate-view">
      <div className="flex-1 flex flex-col items-center justify-center w-full max-w-[550px] space-y-8">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center text-xl font-bold">S</div>
          <span className="text-2xl font-bold tracking-tight">startpage</span>
        </div>

        <div className="w-full relative">
          <input 
            type="text" 
            placeholder="Search privately..." 
            className="w-full bg-[#1e2538] border border-neutral-700/60 rounded-full py-3.5 pl-12 pr-12 text-sm outline-none focus:ring-1 focus:ring-blue-500 transition shadow-lg text-white" 
          />
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
          <Keyboard className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 cursor-pointer hover:text-white" size={18} />
        </div>
      </div>
    </div>
  );
};

export default StartpageTemplate;
