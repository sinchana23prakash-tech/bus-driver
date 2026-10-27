import React, { useState, useEffect } from 'react';
import api from '../api/client';
import { MapPin, Plus, Edit2, Trash2, CheckCircle, AlertCircle, Info, RefreshCw } from 'lucide-react';

const ApprovedBunks = () => {
  const [bunks, setBunks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingBunk, setEditingBunk] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  const [formData, setFormData] = useState({
    name: '',
    address: '',
    latitude: '',
    longitude: '',
    geofence_radius_meters: 500,
    is_active: true
  });

  const fetchBunks = async () => {
    setLoading(true);
    try {
      const res = await api.get('/bunks');
      setBunks(res.data.bunks || []);
    } catch (err) {
      setErrorMsg('Failed to load approved petrol stations.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBunks();
  }, []);

  const openAddModal = () => {
    setEditingBunk(null);
    setFormData({
      name: '',
      address: '',
      latitude: '',
      longitude: '',
      geofence_radius_meters: 500,
      is_active: true
    });
    setModalOpen(true);
  };

  const openEditModal = (bunk) => {
    setEditingBunk(bunk);
    setFormData({
      name: bunk.name,
      address: bunk.address || '',
      latitude: bunk.latitude,
      longitude: bunk.longitude,
      geofence_radius_meters: bunk.geofence_radius_meters,
      is_active: bunk.is_active
    });
    setModalOpen(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    try {
      const payload = {
        name: formData.name.trim(),
        address: formData.address.trim(),
        latitude: parseFloat(formData.latitude),
        longitude: parseFloat(formData.longitude),
        geofence_radius_meters: parseInt(formData.geofence_radius_meters),
        is_active: formData.is_active
      };

      if (editingBunk) {
        await api.put(`/bunks/${editingBunk.id}`, payload);
        setSuccessMsg(`Fuel station "${formData.name}" updated successfully.`);
      } else {
        await api.post('/bunks', payload);
        setSuccessMsg(`Fuel station "${formData.name}" authorized.`);
      }

      setModalOpen(false);
      fetchBunks();
    } catch (err) {
      setErrorMsg(err.response?.data?.error || 'Operation failed.');
    }
  };

  const handleDeactivate = async (bunkId, bunkName) => {
    if (!window.confirm(`Deactivate authorized fuel station "${bunkName}"?`)) return;
    try {
      await api.delete(`/bunks/${bunkId}`);
      setSuccessMsg(`Station "${bunkName}" deactivated.`);
      fetchBunks();
    } catch (err) {
      setErrorMsg(err.response?.data?.error || 'Failed to deactivate station.');
    }
  };

  return (
    <div className="space-y-5">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h2 className="text-xl font-bold text-slate-900">Approved Fuel Stations (Geofencing)</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Configure authoritative petrol bunks, coordinates, and geofence radii for GPS verification
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={fetchBunks}
            className="p-2 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 text-xs font-semibold"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <button
            onClick={openAddModal}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-sm transition"
          >
            <Plus className="w-4 h-4" />
            <span>Add Fuel Station</span>
          </button>
        </div>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 text-xs text-blue-900 flex items-start gap-3">
        <Info className="w-4 h-4 text-blue-700 shrink-0 mt-0.5" />
        <div className="leading-relaxed">
          <strong>Institutional Governance Note:</strong> Only enter authentic petrol stations authorized by the college administration. These locations serve strictly as geofenced coordinates for automated distance checks against driver submissions. Petrol bunk attendants have no logins or access accounts.
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

      {/* Stations Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 uppercase text-[11px] font-bold">
                <th className="py-3 px-4">Station Name</th>
                <th className="py-3 px-4">Physical Address</th>
                <th className="py-3 px-4">GPS Coordinates (Lat, Lon)</th>
                <th className="py-3 px-4">Geofence Radius</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan="6" className="text-center py-10 text-slate-500">
                    Loading approved stations...
                  </td>
                </tr>
              ) : bunks.length === 0 ? (
                <tr>
                  <td colSpan="6" className="text-center py-10 text-slate-400">
                    No approved petrol stations configured yet. Click "Add Fuel Station" above to configure your college's authorized bunks.
                  </td>
                </tr>
              ) : (
                bunks.map((b) => (
                  <tr key={b.id} className="hover:bg-slate-50/70 transition">
                    <td className="py-3 px-4 font-bold text-slate-900 flex items-center gap-2">
                      <MapPin className="w-3.5 h-3.5 text-blue-600 shrink-0" />
                      <span>{b.name}</span>
                    </td>
                    <td className="py-3 px-4 text-slate-600 max-w-xs truncate">
                      {b.address || '—'}
                    </td>
                    <td className="py-3 px-4 font-mono text-slate-700">
                      {b.latitude.toFixed(6)}, {b.longitude.toFixed(6)}
                    </td>
                    <td className="py-3 px-4 font-mono font-semibold text-slate-800">
                      {b.geofence_radius_meters} meters
                    </td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                        b.is_active
                          ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                          : 'bg-slate-100 text-slate-500'
                      }`}>
                        {b.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right space-x-1">
                      <button
                        onClick={() => openEditModal(b)}
                        className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-100 text-slate-600 transition"
                        title="Edit Station"
                      >
                        <Edit2 className="w-3.5 h-3.5" />
                      </button>
                      {b.is_active && (
                        <button
                          onClick={() => handleDeactivate(b.id, b.name)}
                          className="p-1.5 rounded-lg border border-rose-200 hover:bg-rose-50 text-rose-600 transition"
                          title="Deactivate Station"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal: Add/Edit Bunk */}
      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 p-4">
          <div className="bg-white rounded-xl max-w-md w-full p-6 space-y-4 shadow-xl">
            <h4 className="font-bold text-slate-900 text-base">
              {editingBunk ? `Edit Station: ${editingBunk.name}` : 'Configure Approved Petrol Station'}
            </h4>

            <form onSubmit={handleSubmit} className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Fuel Station Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g., HPCL Campus Highway Fuel Point"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:outline-none"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Address / Landmark</label>
                <textarea
                  rows={2}
                  placeholder="e.g., National Highway 44, opposite College East Gate"
                  value={formData.address}
                  onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Latitude (-90 to +90)</label>
                  <input
                    type="number"
                    step="0.000001"
                    required
                    placeholder="12.971598"
                    value={formData.latitude}
                    onChange={(e) => setFormData({ ...formData, latitude: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg font-mono focus:ring-2 focus:ring-blue-600 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Longitude (-180 to +180)</label>
                  <input
                    type="number"
                    step="0.000001"
                    required
                    placeholder="77.594562"
                    value={formData.longitude}
                    onChange={(e) => setFormData({ ...formData, longitude: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg font-mono focus:ring-2 focus:ring-blue-600 focus:outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Geofence Radius (Meters)</label>
                <input
                  type="number"
                  min="50"
                  max="5000"
                  required
                  value={formData.geofence_radius_meters}
                  onChange={(e) => setFormData({ ...formData, geofence_radius_meters: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:outline-none"
                />
                <span className="text-[10px] text-slate-500 mt-0.5 block">
                  Recommended: 300 - 800 meters around the fuel pump forecourt.
                </span>
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
                  {editingBunk ? 'Save Changes' : 'Authorize Station'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default ApprovedBunks;
