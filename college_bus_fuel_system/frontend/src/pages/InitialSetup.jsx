import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api/client';
import { ShieldAlert, CheckCircle, AlertCircle } from 'lucide-react';

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
    <div className="min-h-screen bg-slate-900 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-amber-500 text-slate-950 shadow-lg mb-3">
          <ShieldAlert className="w-8 h-8" />
        </div>
        <h2 className="text-2xl font-extrabold text-white">
          Primary Administrator Setup
        </h2>
        <p className="mt-1 text-sm text-slate-400">
          Create the first administrative account to initialize the system securely.
        </p>
      </div>

      <div className="mt-6 sm:mx-auto sm:w-full sm:max-w-md px-4">
        <div className="bg-white py-8 px-6 shadow-xl rounded-2xl sm:px-10 border border-slate-200">
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
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-600 focus:outline-none"
                placeholder="Dr. K. Sharma (Transport Incharge)"
              />
            </div>

            <div>
              <label className="block font-semibold text-slate-700 uppercase mb-1">Username</label>
              <input
                type="text"
                required
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-600 focus:outline-none"
                placeholder="fleetadmin"
              />
            </div>

            <div>
              <label className="block font-semibold text-slate-700 uppercase mb-1">Official College Email</label>
              <input
                type="email"
                required
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-600 focus:outline-none"
                placeholder="transport.admin@college.edu"
              />
            </div>

            <div>
              <label className="block font-semibold text-slate-700 uppercase mb-1">Phone Number</label>
              <input
                type="text"
                value={formData.phone_number}
                onChange={(e) => setFormData({ ...formData, phone_number: e.target.value })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-600 focus:outline-none"
                placeholder="+91 98765 43210"
              />
            </div>

            <div>
              <label className="block font-semibold text-slate-700 uppercase mb-1">Password (Min 8 Characters)</label>
              <input
                type="password"
                required
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-600 focus:outline-none"
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
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-600 focus:outline-none"
                placeholder="••••••••"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-4 py-2.5 px-4 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm shadow-md transition disabled:opacity-50"
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
