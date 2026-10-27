import React, { useState, useEffect } from 'react';
import api from '../api/client';
import { Bus as BusIcon, Plus, Edit2, CheckCircle, AlertCircle, RefreshCw } from 'lucide-react';

const FleetManagement = () => {
  const [buses, setBuses] = useState([]);
  const [drivers, setDrivers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingBus, setEditingBus] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  const [formData, setFormData] = useState({
    bus_number: '',
    registration_number: '',
    model_name: '',
    fuel_tank_capacity: 150,
    fuel_type: 'DIESEL',
    current_odometer: 0,
    assigned_driver_id: '',
    status: 'ACTIVE'
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      const [busRes, driverRes] = await Promise.all([
        api.get('/buses'),
        api.get('/users?role=DRIVER')
      ]);
      setBuses(busRes.data.buses || []);
      setDrivers(driverRes.data.users || []);
    } catch (err) {
      setErrorMsg('Failed to load fleet and driver data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const openAddModal = () => {
    setEditingBus(null);
    setFormData({
      bus_number: '',
      registration_number: '',
      model_name: '',
      fuel_tank_capacity: 150,
      fuel_type: 'DIESEL',
      current_odometer: 0,
      assigned_driver_id: '',
      status: 'ACTIVE'
    });
    setModalOpen(true);
  };

  const openEditModal = (bus) => {
    setEditingBus(bus);
    setFormData({
      bus_number: bus.bus_number,
      registration_number: bus.registration_number,
      model_name: bus.model_name || '',
      fuel_tank_capacity: bus.fuel_tank_capacity,
      fuel_type: bus.fuel_type,
      current_odometer: bus.current_odometer,
      assigned_driver_id: bus.assigned_driver_id || '',
      status: bus.status
    });
    setModalOpen(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    try {
      const payload = {
        ...formData,
        fuel_tank_capacity: parseFloat(formData.fuel_tank_capacity),
        current_odometer: parseFloat(formData.current_odometer),
        assigned_driver_id: formData.assigned_driver_id ? parseInt(formData.assigned_driver_id) : null
      };

      if (editingBus) {
        await api.put(`/buses/${editingBus.id}`, payload);
        setSuccessMsg(`Bus ${formData.bus_number} updated successfully.`);
      } else {
        await api.post('/buses', payload);
        setSuccessMsg(`Bus ${formData.bus_number} registered successfully.`);
      }

      setModalOpen(false);
      fetchData();
    } catch (err) {
      setErrorMsg(err.response?.data?.error || 'Operation failed.');
    }
  };

  return (
    <div className="space-y-5">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h2 className="text-xl font-bold text-slate-900">College Bus Fleet Directory</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Manage transport buses, tank capacities, odometers, and driver assignments
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={fetchData}
            className="p-2 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 text-xs font-semibold"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <button
            onClick={openAddModal}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-sm transition"
          >
            <Plus className="w-4 h-4" />
            <span>Add Vehicle</span>
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

      {/* Fleet Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 uppercase text-[11px] font-bold">
                <th className="py-3 px-4">Bus #</th>
                <th className="py-3 px-4">Registration</th>
                <th className="py-3 px-4">Model & Fuel</th>
                <th className="py-3 px-4">Tank Capacity</th>
                <th className="py-3 px-4">Odometer</th>
                <th className="py-3 px-4">Assigned Driver</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan="8" className="text-center py-10 text-slate-500">
                    Loading bus fleet...
                  </td>
                </tr>
              ) : buses.length === 0 ? (
                <tr>
                  <td colSpan="8" className="text-center py-10 text-slate-400">
                    No buses configured in the college fleet yet. Click "Add Vehicle" above.
                  </td>
                </tr>
              ) : (
                buses.map((bus) => (
                  <tr key={bus.id} className="hover:bg-slate-50/70 transition">
                    <td className="py-3 px-4 font-bold text-slate-900">{bus.bus_number}</td>
                    <td className="py-3 px-4 font-mono font-semibold text-slate-700">
                      {bus.registration_number}
                    </td>
                    <td className="py-3 px-4">
                      <p className="font-medium text-slate-800">{bus.model_name || 'Standard Bus'}</p>
                      <p className="text-[10px] text-slate-500">{bus.fuel_type}</p>
                    </td>
                    <td className="py-3 px-4 text-slate-700">{bus.fuel_tank_capacity} L</td>
                    <td className="py-3 px-4 font-mono font-semibold text-slate-900">
                      {bus.current_odometer.toLocaleString()} km
                    </td>
                    <td className="py-3 px-4">
                      {bus.assigned_driver_name ? (
                        <span className="font-semibold text-slate-800">{bus.assigned_driver_name}</span>
                      ) : (
                        <span className="text-slate-400 italic">Unassigned</span>
                      )}
                    </td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                        bus.status === 'ACTIVE'
                          ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                          : 'bg-slate-100 text-slate-600'
                      }`}>
                        {bus.status}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={() => openEditModal(bus)}
                        className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-100 text-slate-600 transition"
                      >
                        <Edit2 className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal: Add/Edit Bus */}
      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 p-4">
          <div className="bg-white rounded-xl max-w-md w-full p-6 space-y-4 shadow-xl">
            <h4 className="font-bold text-slate-900 text-base">
              {editingBus ? `Edit Bus: ${editingBus.bus_number}` : 'Register New College Bus'}
            </h4>

            <form onSubmit={handleSubmit} className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Bus Number / Label</label>
                <input
                  type="text"
                  required
                  placeholder="e.g., Bus #04"
                  value={formData.bus_number}
                  onChange={(e) => setFormData({ ...formData, bus_number: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:outline-none"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Vehicle Registration Number</label>
                <input
                  type="text"
                  required
                  placeholder="e.g., KA-01-AB-1234"
                  value={formData.registration_number}
                  onChange={(e) => setFormData({ ...formData, registration_number: e.target.value.toUpperCase() })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:outline-none font-mono"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Model Name</label>
                  <input
                    type="text"
                    placeholder="e.g., Tata Starbus"
                    value={formData.model_name}
                    onChange={(e) => setFormData({ ...formData, model_name: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Fuel Type</label>
                  <select
                    value={formData.fuel_type}
                    onChange={(e) => setFormData({ ...formData, fuel_type: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg bg-slate-50 text-slate-700 focus:ring-2 focus:ring-blue-600 focus:outline-none"
                    disabled
                  >
                    <option value="DIESEL">Diesel (Institutional Standard)</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Tank Capacity (Litres)</label>
                  <input
                    type="number"
                    step="0.1"
                    required
                    value={formData.fuel_tank_capacity}
                    onChange={(e) => setFormData({ ...formData, fuel_tank_capacity: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Current Odometer (km)</label>
                  <input
                    type="number"
                    step="0.1"
                    required
                    value={formData.current_odometer}
                    onChange={(e) => setFormData({ ...formData, current_odometer: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Assigned Driver</label>
                <select
                  value={formData.assigned_driver_id}
                  onChange={(e) => setFormData({ ...formData, assigned_driver_id: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg bg-white focus:ring-2 focus:ring-blue-600 focus:outline-none"
                >
                  <option value="">-- No Driver Assigned --</option>
                  {drivers.map((d) => (
                    <option key={d.id} value={d.id}>
                      {d.full_name} ({d.username})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Status</label>
                <select
                  value={formData.status}
                  onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg bg-white focus:ring-2 focus:ring-blue-600 focus:outline-none"
                >
                  <option value="ACTIVE">Active (In Service)</option>
                  <option value="MAINTENANCE">Maintenance</option>
                  <option value="INACTIVE">Inactive (Decommissioned)</option>
                </select>
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
                  {editingBus ? 'Save Changes' : 'Register Vehicle'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default FleetManagement;
