import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api/client';
import { Fuel, Lock, User, AlertCircle, ShieldCheck } from 'lucide-react';

const Login = () => {
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [needsSetup, setNeedsSetup] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const checkSetup = async () => {
      try {
        const res = await api.get('/auth/setup-status');
        if (res.data.needs_initial_setup) {
          setNeedsSetup(true);
        }
      } catch (err) {
        console.error('Error checking setup status:', err);
      }
    };
    checkSetup();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const res = await api.post('/auth/login', { identifier, password });
      login(res.data.access_token, res.data.user, res.data.policies);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.error || 'Authentication failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#380a10] via-[#4a0d16] to-[#25050a] flex flex-col justify-between py-8 px-4 sm:px-6 lg:px-8">
      {/* Top Gold Utility Banner */}
      <div className="max-w-4xl mx-auto w-full mb-6">
        <div className="bg-[#d8b15a] text-[#3d0910] text-[11px] font-semibold px-4 py-2 rounded-xl flex items-center justify-between shadow-md">
          <div className="flex items-center gap-3">
            <span>📞 +91 8192 223344</span>
            <span className="opacity-40">•</span>
            <span>✉ info@gmu.ac.in</span>
          </div>
          <span className="hidden sm:inline">
            KCET Codes: <strong>B.Tech - E303</strong> | <strong>MCA - C568</strong> | <strong>MBA - B086</strong>
          </span>
        </div>
      </div>

      <div className="my-auto">
        <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
          {/* Gold Crest */}
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-[#d8b15a] text-[#3d0910] shadow-xl mb-3 ring-4 ring-[#e5ad35]/30">
            <Fuel className="w-9 h-9 text-[#4a0d15]" />
          </div>
          <h2 className="text-3xl font-extrabold text-[#f6d782] font-serif uppercase tracking-wider drop-shadow">
            GM University
          </h2>
          <p className="mt-1 text-xs font-semibold text-rose-200/90 tracking-wide">
            Igniting Innovation, Inspiring Transformation • Campus Fuel Management
          </p>
        </div>

        <div className="mt-6 sm:mx-auto sm:w-full sm:max-w-md">
          {needsSetup && (
            <div className="mb-4 p-4 rounded-xl bg-[#541019] border-2 border-[#d8b15a] text-white shadow-lg">
              <div className="flex items-start gap-3">
                <ShieldCheck className="w-5 h-5 text-[#f6d782] shrink-0 mt-0.5" />
                <div>
                  <p className="font-bold text-[#f6d782]">First-Time System Deployment</p>
                  <p className="text-xs text-rose-200 mt-1">
                    No Administrator account has been configured yet.
                  </p>
                  <Link
                    to="/initial-setup"
                    className="inline-block mt-3 px-3 py-1.5 rounded-lg bg-[#d8b15a] hover:bg-[#e5ad35] text-[#3d0910] font-bold text-xs transition shadow"
                  >
                    Configure Primary Administrator →
                  </Link>
                </div>
              </div>
            </div>
          )}

          <div className="bg-white rounded-2xl shadow-2xl border border-[#d8b15a]/30 overflow-hidden">
            {/* Admissions-style Header Banner in Gold */}
            <div className="bg-[#d8b15a] px-6 py-3 border-b border-[#c49a42] flex items-center justify-between text-[#3d0910]">
              <h3 className="font-bold text-sm tracking-wide">
                Portal Authentication
              </h3>
              <span className="text-[10px] bg-[#3d0910] text-[#f6d782] px-2 py-0.5 rounded font-bold uppercase tracking-wider">
                Batch 2026-27
              </span>
            </div>

            <div className="py-6 px-6 sm:px-8">
              {error && (
                <div className="mb-4 p-3 rounded-lg bg-rose-50 border border-rose-300 flex items-center gap-2 text-xs text-rose-800 font-medium">
                  <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />
                  <span>{error}</span>
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-xs font-bold text-[#541019] uppercase tracking-wider mb-1.5">
                    Username or Official Email
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-stone-400">
                      <User className="w-4 h-4" />
                    </div>
                    <input
                      type="text"
                      required
                      value={identifier}
                      onChange={(e) => setIdentifier(e.target.value)}
                      className="w-full pl-9 pr-3 py-2.5 border border-stone-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#541019] focus:border-transparent bg-white shadow-inner"
                      placeholder="admin or vc_office"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-bold text-[#541019] uppercase tracking-wider mb-1.5">
                    Password
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-stone-400">
                      <Lock className="w-4 h-4" />
                    </div>
                    <input
                      type="password"
                      required
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="w-full pl-9 pr-3 py-2.5 border border-stone-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#541019] focus:border-transparent bg-white shadow-inner"
                      placeholder="••••••••"
                    />
                  </div>
                </div>

                {/* Burgundy Button matching Apply Now */}
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-3 px-4 rounded-xl bg-[#541019] hover:bg-[#68131f] text-white font-bold text-sm shadow-md transition-all duration-150 disabled:opacity-50"
                >
                  {loading ? 'Authenticating...' : 'Sign In to Dashboard'}
                </button>
              </form>

              {/* Exact contact buttons from the GM University screenshot */}
              <div className="mt-6 pt-5 border-t border-stone-100 text-center">
                <p className="text-xs text-stone-600 font-medium mb-2.5">
                  If you have any queries do contact:
                </p>
                <div className="flex justify-center gap-2.5">
                  <span className="px-3.5 py-1.5 rounded-lg bg-[#e2bd68] text-[#3d0910] font-bold text-xs shadow-sm border border-[#ca8a1b]">
                    9364099720
                  </span>
                  <span className="px-3.5 py-1.5 rounded-lg bg-[#e2bd68] text-[#3d0910] font-bold text-xs shadow-sm border border-[#ca8a1b]">
                    6364259993
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="text-center py-3 text-xs text-rose-200/60">
        GM University Transport & Fleet Operations © 2026. All rights reserved.
      </div>
    </div>
  );
};

export default Login;
