import React from 'react';

interface CursorTemplateProps {
  onSuccess: (data: any) => void;
}

const CursorTemplate: React.FC<CursorTemplateProps> = () => {
  return (
    <div className="min-h-full w-full bg-[#050505] text-[#b0b0b0] flex flex-col justify-between items-center py-20 px-6 select-none animate-view">
      <div className="max-w-[800px] w-full flex flex-col items-center justify-center space-y-8 text-center">
        <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight text-white font-jakarta">
          The AI-first <br />Code Editor
        </h1>
        <p className="text-neutral-400 max-w-[500px] text-sm leading-relaxed">
          Built around Copilot, Cursor is the editor of choice for writing code cleanly and efficiently.
        </p>
        <div className="flex items-center space-x-4">
          <button className="bg-white hover:bg-neutral-200 text-black text-xs font-bold px-6 py-3 rounded-lg transition scale-on-click">
            Download for Windows
          </button>
          <button className="bg-neutral-900 border border-neutral-800 text-xs text-white px-6 py-3 rounded-lg hover:bg-neutral-800">
            Read Docs
          </button>
        </div>
      </div>
    </div>
  );
};

export default CursorTemplate;
