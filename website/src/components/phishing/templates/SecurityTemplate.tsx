import React from 'react';
import { Shield, UserCheck, Key, Smartphone } from 'lucide-react';

interface SecurityTemplateProps {
  onSuccess: (data: any) => void;
}

const SecurityTemplate: React.FC<SecurityTemplateProps> = () => {
  return (
    <div className="min-h-full w-full bg-[#0a0d13] text-[#e3e3e3] flex flex-col py-10 px-6 select-none font-sans animate-view">
      <div className="max-w-[800px] mx-auto w-full flex flex-col space-y-8">
        <div className="flex items-center space-x-3">
          <Shield className="text-2xl text-green-400 animate-pulse" size={32} />
          <h1 className="text-2xl font-bold">Google Account Security</h1>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-[#141822] border border-neutral-800 p-6 rounded-xl flex flex-col space-y-4">
            <UserCheck className="text-xl text-blue-400" size={24} />
            <h3 className="font-bold">2-Step Verification</h3>
            <p className="text-xs text-neutral-400">Keep hackers out with an extra layer of active authentication.</p>
            <span className="text-xs text-emerald-400 font-bold">Enabled</span>
          </div>
          <div className="bg-[#141822] border border-neutral-800 p-6 rounded-xl flex flex-col space-y-4">
            <Key className="text-xl text-yellow-400" size={24} />
            <h3 className="font-bold">Passkeys</h3>
            <p className="text-xs text-neutral-400">Fast and biometric security without typing passwords manually.</p>
            <button className="bg-[#242c3e] hover:bg-neutral-800 px-3 py-1.5 rounded text-xs">Manage</button>
          </div>
          <div className="bg-[#141822] border border-neutral-800 p-6 rounded-xl flex flex-col space-y-4">
            <Smartphone className="text-xl text-red-400" size={24} />
            <h3 className="font-bold">Logged Devices</h3>
            <p className="text-xs text-neutral-400">Verify devices with active tokens currently on your profile.</p>
            <span className="text-xs text-neutral-400">3 active devices</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SecurityTemplate;
