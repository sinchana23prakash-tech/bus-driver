import React from 'react';
import { useAuth } from '../context/AuthContext';
import { LogOut, Shield, User, Fuel } from 'lucide-react';

const Navbar = () => {
  const { user, logout, policies } = useAuth();

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-blue-700 flex items-center justify-center text-white shadow-sm">
            <Fuel className="w-6 h-6" />
          </div>
          <div>
            <h1 className="font-bold text-slate-900 text-lg leading-tight">
              College Bus Fuel Management
            </h1>
            <p className="text-xs text-slate-500 font-medium">
              Transport Fleet & Audit Portal
            </p>
          </div>
        </div>

        {user && (
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-100 border border-slate-200 text-xs">
              <Shield className="w-3.5 h-3.5 text-blue-700" />
              <span className="font-semibold text-slate-700 uppercase">{user.role}</span>
              {user.role === 'VC' && (
                <span className="text-[10px] bg-amber-100 text-amber-800 font-semibold px-2 py-0.5 rounded-full">
                  {policies?.vc_can_approve ? 'Approver & Auditor' : 'Auditor (Read-Only)'}
                </span>
              )}
            </div>

            <div className="flex items-center gap-2 text-sm text-slate-700 font-medium">
              <User className="w-4 h-4 text-slate-400" />
              <span>{user.full_name}</span>
            </div>

            <button
              onClick={logout}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-semibold text-rose-700 hover:bg-rose-50 border border-transparent hover:border-rose-200 transition-colors"
              title="Sign Out"
            >
              <LogOut className="w-3.5 h-3.5" />
              <span>Sign Out</span>
            </button>
          </div>
        )}
      </div>
    </header>
  );
};

export default Navbar;
