import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api/client';
import { ShieldAlert, AlertCircle } from 'lucide-react';

const InitialSetup = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    full_name: '',
    phone_number: '',
    password: '',
    confirm_password: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.confirm_password) {
      setError('Passwords do not match.');
      return;
    }

    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters long.');
      return;
    }

    setLoading(true);
    try {
      const res = await api.post('/auth/setup-initial-admin', {
        username: formData.username,
        email: formData.email,
        full_name: formData.full_name,
        phone_number: formData.phone_number,
        password: formData.password,
      });

      login(res.data.access_token, res.data.user, { vc_can_approve: false });
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to initialize administrator account.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#380a10] via-[#4a0d16] to-[#25050a] flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-[#d8b15a] text-[#3d0910] shadow-xl mb-3 ring-4 ring-[#e5ad35]/30">
          <ShieldAlert className="w-9 h-9 text-[#4a0d15]" />
        </div>
        <h2 className="text-3xl font-extrabold text-[#f6d782] font-serif uppercase tracking-wider">
          GM University
        </h2>
        <p className="mt-1 text-sm font-semibold text-rose-200/90">
          Primary Administrator Initial Setup
        </p>
      </div>

      <div className="mt-6 sm:mx-auto sm:w-full sm:max-w-md px-4">
        <div className="bg-white py-8 px-6 shadow-2xl rounded-2xl sm:px-10 border-2 border-[#d8b15a]/50">
          {error && (
            <div className="mb-4 p-3 rounded-lg bg-rose-50 border border-rose-200 flex items-center gap-2 text-xs text-rose-700">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4 text-xs">
            <div>
              <label className="block font-semibold text-slate-700 uppercase mb-1">Full Name</label>
              <input
                type="text"
                required
                value={formData.full_name}
                onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-[#541019] focus:outline-none"
                placeholder="Dr. Rajesh V"
              />
            </div>

            <div>
              <label className="block font-semibold text-slate-700 uppercase mb-1">Official Email</label>
              <input
                type="email"
                required
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-[#541019] focus:outline-none"
                placeholder="transport.admin@gmu.ac.in"
              />
            </div>

            <div>
              <label className="block font-semibold text-slate-700 uppercase mb-1">Admin Username</label>
              <input
                type="text"
                required
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-[#541019] focus:outline-none"
                placeholder="admin"
              />
            </div>

            <div>
              <label className="block font-semibold text-slate-700 uppercase mb-1">Phone Number</label>
              <input
                type="text"
                value={formData.phone_number}
                onChange={(e) => setFormData({ ...formData, phone_number: e.target.value })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-[#541019] focus:outline-none"
                placeholder="+91 8192 223344"
              />
            </div>

            <div>
              <label className="block font-semibold text-slate-700 uppercase mb-1">Password (Min 8 Characters)</label>
              <input
                type="password"
                required
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-[#541019] focus:outline-none"
                placeholder="••••••••"
              />
            </div>

            <div>
              <label className="block font-semibold text-slate-700 uppercase mb-1">Confirm Password</label>
              <input
                type="password"
                required
                value={formData.confirm_password}
                onChange={(e) => setFormData({ ...formData, confirm_password: e.target.value })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-[#541019] focus:outline-none"
                placeholder="••••••••"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-4 py-2.5 px-4 rounded-xl bg-[#541019] hover:bg-[#68131f] text-white font-bold text-sm shadow-md transition disabled:opacity-50"
            >
              {loading ? 'Initializing Administrator...' : 'Create Administrator & Enter Portal'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default InitialSetup;
