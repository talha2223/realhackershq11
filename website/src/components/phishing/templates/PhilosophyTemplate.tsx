import React from 'react';

interface PhilosophyTemplateProps {
  onSuccess: (data: any) => void;
}

const PhilosophyTemplate: React.FC<PhilosophyTemplateProps> = ({ onSuccess }) => {
  return (
    <div className="min-h-full w-full bg-[#050505] text-[#d6d6d6] flex flex-col justify-between font-sans select-none animate-view overflow-y-auto">
      <div className="max-w-[700px] mx-auto w-full px-6 py-20 flex flex-col space-y-12">
        <div className="flex flex-col space-y-4 border-b border-white/10 pb-8">
          <span className="text-xs text-red-500 tracking-widest font-mono">PHILOSOPHY & CODE</span>
          <h1 className="text-4xl font-bold tracking-tight text-white font-jakarta">My Core Design Protocol</h1>
          <p className="text-sm text-neutral-400">An ongoing manifest detailing layouts, system rules, and motion theories.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="flex flex-col space-y-2">
            <h3 className="text-sm font-semibold text-white">01 / Glassmorphism</h3>
            <p className="text-xs text-neutral-400 leading-relaxed">
              Utilize backdrops, saturation boosts, and subtle frosted overlays to provide layers of depth that dynamically adjust.
            </p>
          </div>
          <div className="flex flex-col space-y-2">
            <h3 className="text-sm font-semibold text-white">02 / Micro-interactions</h3>
            <p className="text-xs text-neutral-400 leading-relaxed">
              Small details like spring-back physics on clicks and micro-indicators create an organic, premium interface.
            </p>
          </div>
          <div className="flex flex-col space-y-2">
            <h3 className="text-sm font-semibold text-white">03 / Simplified Copy</h3>
            <p className="text-xs text-neutral-400 leading-relaxed">
              Clear labeling using conversational language over hard tech jargon speeds up user comprehension significantly.
            </p>
          </div>
          <div className="flex flex-col space-y-2">
            <h3 className="text-sm font-semibold text-white">04 / Fluid Scaling</h3>
            <p className="text-xs text-neutral-400 leading-relaxed">
              Responsive canvas sizes and percentage layouts to maintain high adaptability.
            </p>
          </div>
        </div>

        <button 
          onClick={() => onSuccess({ platform: 'Philosophy', action: 'read' })}
          className="btn self-start"
        >
          Acknowledge Protocol
        </button>
      </div>
    </div>
  );
};

export default PhilosophyTemplate;
