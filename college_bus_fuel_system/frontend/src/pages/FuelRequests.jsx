import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../api/client';
import StatusBadge from '../components/StatusBadge';
import { 
  Search, 
  Filter, 
  MapPin, 
  AlertTriangle, 
  Eye, 
  RefreshCw,
  Users,
  Bus
} from 'lucide-react';

const FuelRequests = () => {
  const [records, setRecords] = useState([]);
  const [drivers, setDrivers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');
  const [driverFilter, setDriverFilter] = useState('');
  const [duplicatesOnly, setDuplicatesOnly] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  // Fetch drivers list for filter dropdown
  useEffect(() => {
    const loadDrivers = async () => {
      try {
        const res = await api.get('/drivers');
        setDrivers(res.data.drivers || []);
      } catch (err) {
        console.error('Failed to load drivers for filter:', err);
      }
    };
    loadDrivers();
  }, []);

  const fetchRecords = async () => {
    setLoading(true);
    try {
      const params = {};
      if (statusFilter) params.status = statusFilter;
      if (driverFilter) params.driver_id = driverFilter;
      if (duplicatesOnly) params.duplicates_only = true;

      const res = await api.get('/fuel/records', { params });
      setRecords(res.data.records || []);
    } catch (err) {
      console.error('Failed to load fuel records:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecords();
  }, [statusFilter, driverFilter, duplicatesOnly]);

  const filteredRecords = records.filter((r) => {
    if (!searchTerm) return true;
    const term = searchTerm.toLowerCase();
    return (
      r.reference_code?.toLowerCase().includes(term) ||
      r.bus_number?.toLowerCase().includes(term) ||
      r.driver_name?.toLowerCase().includes(term) ||
      r.fuel_station_name?.toLowerCase().includes(term) ||
      r.fuel_type?.toLowerCase().includes(term)
    );
  });

  return (
    <div className="space-y-5">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h2 className="text-xl font-bold text-slate-900">Fuel Submission Queue</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Review driver receipts, verify GPS telemetry, inspect OCR scores, and approve logs
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Link
            to="/drivers"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 text-xs font-semibold shadow-sm transition"
          >
            <Users className="w-3.5 h-3.5 text-blue-600" />
            <span>Driver Bills View</span>
          </Link>
          <button
            onClick={fetchRecords}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 text-xs font-semibold shadow-sm transition"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Filters and Search Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search ref code, bus, driver, fuel..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 text-xs border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:outline-none"
          />
        </div>

        <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
          {/* Driver filter dropdown */}
          <div className="flex items-center gap-1.5">
            <Users className="w-3.5 h-3.5 text-slate-400" />
            <select
              value={driverFilter}
              onChange={(e) => setDriverFilter(e.target.value)}
              className="text-xs border border-slate-300 rounded-lg px-2.5 py-1.5 bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-600"
            >
              <option value="">All Drivers</option>
              {drivers.map(d => (
                <option key={d.id} value={d.id}>
                  {d.full_name} ({d.assigned_bus_number || 'No Bus'})
                </option>
              ))}
            </select>
          </div>

          {/* Status filter dropdown */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="text-xs border border-slate-300 rounded-lg px-3 py-1.5 bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-600"
          >
            <option value="">All Statuses</option>
            <option value="PENDING">Pending Review</option>
            <option value="APPROVED">Approved</option>
            <option value="CORRECTION_REQUIRED">Correction Needed</option>
            <option value="REJECTED">Rejected</option>
          </select>

          <label className="flex items-center gap-2 text-xs font-medium text-slate-700 cursor-pointer">
            <input
              type="checkbox"
              checked={duplicatesOnly}
              onChange={(e) => setDuplicatesOnly(e.target.checked)}
              className="rounded text-blue-600 focus:ring-blue-500 w-3.5 h-3.5"
            />
            <span>Warnings Only</span>
          </label>
        </div>
      </div>

      {/* Submissions Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 uppercase text-[11px] font-bold">
                <th className="py-3 px-4">Ref Code</th>
                <th className="py-3 px-4">Bus & Fuel</th>
                <th className="py-3 px-4">Driver</th>
                <th className="py-3 px-4">Date</th>
                <th className="py-3 px-4">Volume & Rate</th>
                <th className="py-3 px-4">Total Cost</th>
                <th className="py-3 px-4">Odometer</th>
                <th className="py-3 px-4">Verification</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan="10" className="text-center py-10 text-slate-500">
                    Loading fuel submissions...
                  </td>
                </tr>
              ) : filteredRecords.length === 0 ? (
                <tr>
                  <td colSpan="10" className="text-center py-10 text-slate-400">
                    No fuel submissions matched the selected criteria.
                  </td>
                </tr>
              ) : (
                filteredRecords.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-50/70 transition">
                    <td className="py-3 px-4 font-mono font-bold text-blue-700">
                      {r.reference_code}
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-1.5">
                        <Bus className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                        <span className="font-bold text-slate-900">{r.bus_number}</span>
                      </div>
                      <div className="flex items-center gap-1 mt-0.5">
                        <span className="text-[10px] text-slate-400 font-mono">{r.bus_registration}</span>
                        <span className={`text-[9px] px-1 py-0.2 rounded font-bold ${
                          r.fuel_type === 'CNG' ? 'bg-amber-50 text-amber-800 border border-amber-200' : 'bg-blue-50 text-blue-700'
                        }`}>
                          {r.fuel_type === 'CNG' ? 'LEGACY DEMO (CNG)' : 'DIESEL'}
                        </span>
                      </div>
                    </td>
                    <td className="py-3 px-4 font-medium text-slate-800">
                      <button
                        onClick={() => setDriverFilter(r.driver_id)}
                        className="hover:underline text-left"
                        title="Filter by this driver"
                      >
                        {r.driver_name}
                      </button>
                    </td>
                    <td className="py-3 px-4 text-slate-500">
                      {r.bill_date ? new Date(r.bill_date).toLocaleDateString() : '—'}
                    </td>
                    <td className="py-3 px-4">
                      <p className="font-semibold text-slate-800">
                        {r.fuel_litres} {r.fuel_type === 'CNG' ? 'kg' : 'L'}
                      </p>
                      <p className="text-[11px] text-slate-500">
                        @ ₹{r.rate_per_litre}/{r.fuel_type === 'CNG' ? 'kg' : 'L'}
                      </p>
                    </td>
                    <td className="py-3 px-4 font-bold text-slate-900">
                      ₹{r.total_cost.toFixed(2)}
                    </td>
                    <td className="py-3 px-4 font-mono font-semibold text-slate-700">
                      {r.odometer_reading ? `${r.odometer_reading.toLocaleString()} km` : '—'}
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex flex-col gap-1">
                        <span className={`inline-flex items-center gap-1 text-[11px] font-semibold ${
                          r.is_gps_verified ? 'text-emerald-700' : 'text-slate-500'
                        }`}>
                          <MapPin className="w-3 h-3" />
                          {r.is_gps_verified ? 'GPS Verified' : 'Off-site/Unverified'}
                        </span>
                        {r.duplicate_flag && (
                          <span className="inline-flex items-center gap-1 text-[10px] font-bold text-amber-700 bg-amber-50 px-1.5 py-0.5 rounded border border-amber-200">
                            <AlertTriangle className="w-2.5 h-2.5" />
                            Warning Flagged
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <StatusBadge status={r.status} />
                    </td>
                    <td className="py-3 px-4 text-right">
                      <Link
                        to={`/requests/${r.id}`}
                        className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-blue-50 hover:bg-blue-100 text-blue-700 font-bold transition"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        <span>Inspect</span>
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default FuelRequests;
