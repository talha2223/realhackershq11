import React from 'react';
import { Sparkles, MessageCircle, Repeat, Heart } from 'lucide-react';

interface TwitterTemplateProps {
  onSuccess: (data: any) => void;
}

const TwitterTemplate: React.FC<TwitterTemplateProps> = () => {
  return (
    <div className="min-h-full w-full bg-black text-white flex flex-col select-none animate-view">
      <div className="max-w-[600px] mx-auto w-full border-x border-neutral-800 flex-1 flex flex-col">
        <div className="sticky top-0 bg-black/80 backdrop-blur-md border-b border-neutral-800 px-4 py-3 flex justify-between items-center">
          <span className="font-bold text-lg">Home</span>
          <Sparkles size={16} className="text-white" />
        </div>

        <div className="p-4 border-b border-neutral-800 flex space-x-3 items-start hover:bg-white/5 cursor-pointer">
          <div className="w-10 h-10 rounded-full bg-blue-500 shrink-0"></div>
          <div className="flex-1 flex flex-col space-y-1">
            <div className="flex items-center space-x-1.5 text-xs text-neutral-400">
              <span className="font-bold text-white text-sm">Developer Pro</span>
              <span>@dev_pro</span>
              <span>• 2h</span>
            </div>
            <p className="text-sm leading-relaxed">
              Just completed the visual layout clones for the new system simulator. Everything feels incredibly quick and reliable. ✨
            </p>
            <div className="flex justify-between text-neutral-500 text-xs pt-2 pr-10">
              <span className="flex items-center gap-1"><MessageCircle size={14} /> 12</span>
              <span className="flex items-center gap-1"><Repeat size={14} /> 4</span>
              <span className="flex items-center gap-1"><Heart size={14} /> 45</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TwitterTemplate;
