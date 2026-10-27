import React, { useState, useEffect } from 'react';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';
import { Users as UsersIcon, Plus, Key, ToggleLeft, ToggleRight, CheckCircle, AlertCircle, RefreshCw } from 'lucide-react';

const UserManagement = () => {
  const { user: currentAdmin } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [resetModalUser, setResetModalUser] = useState(null);
  const [newPassword, setNewPassword] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  const [formData, setFormData] = useState({
    username: '',
    email: '',
    full_name: '',
    phone_number: '',
    role: 'DRIVER',
    password: ''
  });

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const res = await api.get('/users');
      setUsers(res.data.users || []);
    } catch (err) {
      setErrorMsg('Failed to load accounts.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleCreateUser = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    try {
      await api.post('/users', formData);
      setSuccessMsg(`User ${formData.username} created successfully.`);
      setModalOpen(false);
      setFormData({
        username: '',
        email: '',
        full_name: '',
        phone_number: '',
        role: 'DRIVER',
        password: ''
      });
      fetchUsers();
    } catch (err) {
      setErrorMsg(err.response?.data?.error || 'Failed to create user.');
    }
  };

  const handleToggleStatus = async (user) => {
    try {
      await api.put(`/users/${user.id}/status`, { is_active: !user.is_active });
      setSuccessMsg(`User ${user.username} status updated.`);
      fetchUsers();
    } catch (err) {
      setErrorMsg(err.response?.data?.error || 'Failed to update user status.');
    }
  };

  const handleResetPassword = async (e) => {
    e.preventDefault();
    if (!resetModalUser || newPassword.length < 8) {
      setErrorMsg('Password must be at least 8 characters long.');
      return;
    }
    try {
      await api.put(`/users/${resetModalUser.id}/reset-password`, { new_password: newPassword });
      setSuccessMsg(`Password for ${resetModalUser.username} successfully reset.`);
      setResetModalUser(null);
      setNewPassword('');
    } catch (err) {
      setErrorMsg(err.response?.data?.error || 'Failed to reset password.');
    }
  };

  return (
    <div className="space-y-5">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h2 className="text-xl font-bold text-slate-900">Personnel & Role Management</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Safely provision Drivers, Vice-Chancellor auditors, and Fleet Administrators
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={fetchUsers}
            className="p-2 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 text-xs font-semibold"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <button
            onClick={() => setModalOpen(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-sm transition"
          >
            <Plus className="w-4 h-4" />
            <span>Create Account</span>
          </button>
        </div>
      </div>

      {errorMsg && (
        <div className="p-3 rounded-lg bg-rose-50 border border-rose-200 text-xs text-rose-700 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}
      {successMsg && (
        <div className="p-3 rounded-lg bg-emerald-50 border border-emerald-200 text-xs text-emerald-700 flex items-center gap-2">
          <CheckCircle className="w-4 h-4 shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {/* Users Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 uppercase text-[11px] font-bold">
                <th className="py-3 px-4">Full Name</th>
                <th className="py-3 px-4">Username</th>
                <th className="py-3 px-4">Official Email</th>
                <th className="py-3 px-4">Role</th>
                <th className="py-3 px-4">Account Status</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan="6" className="text-center py-10 text-slate-500">
                    Loading accounts...
                  </td>
                </tr>
              ) : users.map((u) => (
                <tr key={u.id} className="hover:bg-slate-50/70 transition">
                  <td className="py-3 px-4 font-bold text-slate-900">{u.full_name}</td>
                  <td className="py-3 px-4 font-mono text-slate-700">{u.username}</td>
                  <td className="py-3 px-4 text-slate-600">{u.email}</td>
                  <td className="py-3 px-4">
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${
                      u.role === 'ADMIN'
                        ? 'bg-blue-100 text-blue-800'
                        : u.role === 'VC'
                        ? 'bg-purple-100 text-purple-800'
                        : 'bg-emerald-100 text-emerald-800'
                    }`}>
                      {u.role}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <span className={`inline-flex items-center gap-1 font-semibold ${
                      u.is_active ? 'text-emerald-700' : 'text-slate-400'
                    }`}>
                      <span className={`w-2 h-2 rounded-full ${u.is_active ? 'bg-emerald-500' : 'bg-slate-300'}`}></span>
                      {u.is_active ? 'Active' : 'Deactivated'}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right space-x-2">
                    <button
                      onClick={() => setResetModalUser(u)}
                      className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-100 text-slate-600 transition"
                      title="Reset Password"
                    >
                      <Key className="w-3.5 h-3.5" />
                    </button>
                    {u.id !== currentAdmin?.id && (
                      <button
                        onClick={() => handleToggleStatus(u)}
                        className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-100 text-slate-600 transition"
                        title={u.is_active ? 'Deactivate Account' : 'Activate Account'}
                      >
                        {u.is_active ? (
                          <ToggleRight className="w-4 h-4 text-emerald-600" />
                        ) : (
                          <ToggleLeft className="w-4 h-4 text-slate-400" />
                        )}
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal: Create User */}
      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 p-4">
          <div className="bg-white rounded-xl max-w-md w-full p-6 space-y-4 shadow-xl">
            <h4 className="font-bold text-slate-900 text-base">Provision New User Account</h4>

            <form onSubmit={handleCreateUser} className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Role</label>
                <select
                  value={formData.role}
                  onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg bg-white focus:ring-2 focus:ring-blue-600 focus:outline-none"
                >
                  <option value="DRIVER">Driver (Flutter Mobile App)</option>
                  <option value="VC">Vice-Chancellor (Executive Dashboard)</option>
                  <option value="ADMIN">Fleet Administrator (Full Management)</option>
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Full Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g., Ramesh Kumar"
                  value={formData.full_name}
                  onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:outline-none"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Username</label>
                <input
                  type="text"
                  required
                  placeholder="e.g., ramesh_driver"
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:outline-none"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Official Email</label>
                <input
                  type="email"
                  required
                  placeholder="e.g., ramesh@college.edu"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:outline-none"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Phone Number</label>
                <input
                  type="text"
                  placeholder="+91 98765 00000"
                  value={formData.phone_number}
                  onChange={(e) => setFormData({ ...formData, phone_number: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:outline-none"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Initial Password (Min 8 Chars)</label>
                <input
                  type="password"
                  required
                  placeholder="••••••••"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:outline-none"
                />
              </div>

              <div className="flex justify-end gap-2 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setModalOpen(false)}
                  className="px-3 py-1.5 rounded-lg border border-slate-200 text-slate-700 font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-bold"
                >
                  Create Account
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Reset Password */}
      {resetModalUser && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 p-4">
          <div className="bg-white rounded-xl max-w-sm w-full p-6 space-y-4 shadow-xl">
            <h4 className="font-bold text-slate-900 text-base">
              Reset Password: {resetModalUser.username}
            </h4>
            <form onSubmit={handleResetPassword} className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">New Password (Min 8 chars)</label>
                <input
                  type="password"
                  required
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:outline-none"
                />
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setResetModalUser(null)}
                  className="px-3 py-1.5 rounded-lg border border-slate-200 text-slate-700 font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-bold"
                >
                  Update Password
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserManagement;
