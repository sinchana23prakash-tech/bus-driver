import React from 'react';
import { useAuth } from '../context/AuthContext';
import { LogOut, Shield, User, Fuel } from 'lucide-react';

const Navbar = () => {
  const { user, logout, policies } = useAuth();

  return (
    <header className="sticky top-0 z-30 shadow-md">
      {/* Top Gold Utility Strip - Exact match to GM University website */}
      <div className="bg-[#d8b15a] text-[#3d0910] text-[11px] font-semibold px-4 sm:px-6 lg:px-8 py-1.5 flex items-center justify-between border-b border-[#c49a42] shadow-sm">
        <div className="flex items-center gap-3 sm:gap-4">
          <span className="flex items-center gap-1.5">
            <span className="opacity-80">📞</span> +91 8192 223344
          </span>
          <span className="hidden sm:inline text-[#3d0910]/40">•</span>
          <span className="hidden sm:flex items-center gap-1.5">
            <span className="opacity-80">✉</span> info@gmu.ac.in
          </span>
        </div>
        <div className="flex items-center gap-3">
          <span className="tracking-wide">
            KCET Codes : <strong>B.Tech - E303</strong> | <strong>MCA - C568</strong> | <strong>MBA - B086</strong>
          </span>
        </div>
      </div>

      {/* Main GM University Deep Maroon Header */}
      <div className="bg-[#541019] text-white border-b border-[#3d0910]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3.5">
            {/* University Crest in Gold */}
            <div className="w-11 h-11 rounded-xl bg-[#d8b15a] text-[#3d0910] flex items-center justify-center shadow-md ring-2 ring-[#e5ad35]/40 shrink-0">
              <Fuel className="w-6 h-6 text-[#541019]" />
            </div>

            {/* University Title & Subtitle */}
            <div className="flex flex-col">
              <div className="flex items-center gap-2.5">
                <h1 className="font-extrabold text-[#f6d782] text-lg sm:text-xl tracking-wider font-serif uppercase leading-tight drop-shadow-sm">
                  GM University
                </h1>
                <span className="hidden sm:inline-block text-[10px] bg-[#d8b15a]/20 text-[#f6d782] px-2 py-0.5 rounded font-bold tracking-widest uppercase border border-[#d8b15a]/30">
                  Fleet Portal
                </span>
              </div>
              <p className="text-xs text-rose-200/90 font-medium tracking-tight">
                Igniting Innovation, Inspiring Transformation • Campus Fuel Management
              </p>
            </div>
          </div>

          {user && (
            <div className="flex items-center gap-3 sm:gap-4">
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/10 border border-white/20 text-xs">
                <Shield className="w-3.5 h-3.5 text-[#f6d782]" />
                <span className="font-bold text-white uppercase tracking-wider">{user.role}</span>
                {user.role === 'VC' && (
                  <span className="text-[10px] bg-[#d8b15a] text-[#3d0910] font-bold px-2 py-0.5 rounded-full shadow-sm">
                    {policies?.vc_can_approve ? 'Approver & Auditor' : 'Auditor (Read-Only)'}
                  </span>
                )}
              </div>

              <div className="hidden md:flex items-center gap-1.5 text-sm text-white font-medium">
                <User className="w-4 h-4 text-rose-200/80" />
                <span>{user.full_name}</span>
              </div>

              <button
                onClick={logout}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold text-white hover:bg-white/20 bg-white/10 border border-white/25 transition-all shadow-sm"
                title="Sign Out"
              >
                <LogOut className="w-3.5 h-3.5" />
                <span>Sign Out</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Navbar;
