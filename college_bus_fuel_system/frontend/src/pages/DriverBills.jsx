import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../api/client';
import StatusBadge from '../components/StatusBadge';
import SecureBillModal from '../components/SecureBillModal';
import { 
  Users, 
  Bus, 
  Fuel, 
  IndianRupee, 
  Clock, 
  Search, 
  FileText, 
  CheckCircle, 
  AlertCircle, 
  Eye, 
  RefreshCw,
  Gauge
} from 'lucide-react';

const DriverBills = () => {
  const [drivers, setDrivers] = useState([]);
  const [selectedDriverId, setSelectedDriverId] = useState(null);
  const [driverDetail, setDriverDetail] = useState(null);
  const [records, setRecords] = useState([]);
  const [loadingDrivers, setLoadingDrivers] = useState(true);
  const [loadingRecords, setLoadingRecords] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  
  // Modal for bill viewing
  const [selectedBillRecord, setSelectedBillRecord] = useState(null);

  const fetchDrivers = async () => {
    setLoadingDrivers(true);
    try {
      const res = await api.get('/drivers');
      const list = res.data.drivers || [];
      setDrivers(list);
      if (list.length > 0 && !selectedDriverId) {
        setSelectedDriverId(list[0].id);
      }
    } catch (err) {
      console.error('Failed to load drivers list:', err);
    } finally {
      setLoadingDrivers(false);
    }
  };

  useEffect(() => {
    fetchDrivers();
  }, []);

  const fetchDriverRecords = async (driverId, status = '') => {
    if (!driverId) return;
    setLoadingRecords(true);
    try {
      const params = {};
      if (status) params.status = status;
      const res = await api.get(`/drivers/${driverId}/records`, { params });
      setDriverDetail(res.data.driver);
      setRecords(res.data.records || []);
    } catch (err) {
      console.error(`Failed to load records for driver ${driverId}:`, err);
    } finally {
      setLoadingRecords(false);
    }
  };

  useEffect(() => {
    if (selectedDriverId) {
      fetchDriverRecords(selectedDriverId, statusFilter);
    }
  }, [selectedDriverId, statusFilter]);

  const filteredDrivers = drivers.filter(d => 
    d.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    d.username?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    d.assigned_bus_number?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const selectedDriver = drivers.find(d => d.id === selectedDriverId);

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <Users className="w-5 h-5 text-blue-600" />
            <span>Driver-Specific Fuel Records & Bills</span>
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Audit individual driver submissions, bill receipts, odometer progressions, and approval statuses
          </p>
        </div>
        <button
          onClick={() => {
            fetchDrivers();
            if (selectedDriverId) fetchDriverRecords(selectedDriverId, statusFilter);
          }}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 text-xs font-semibold shadow-sm transition"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Main Two-Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 items-start">
        {/* Left Column: Driver Selection List */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4 space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-slate-100">
            <h3 className="text-xs font-bold uppercase text-slate-700 tracking-wider">
              College Drivers ({drivers.length})
            </h3>
          </div>

          {/* Search drivers */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" />
            <input
              type="text"
              placeholder="Search driver or bus..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-8 pr-3 py-1.5 text-xs border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
            />
          </div>

          {/* Drivers List */}
          <div className="space-y-1.5 max-h-[600px] overflow-y-auto pr-1">
            {loadingDrivers ? (
              <div className="py-8 text-center text-xs text-slate-400">Loading drivers...</div>
            ) : filteredDrivers.length === 0 ? (
              <div className="py-8 text-center text-xs text-slate-400">No drivers found.</div>
            ) : (
              filteredDrivers.map(d => {
                const isSelected = d.id === selectedDriverId;
                return (
                  <button
                    key={d.id}
                    onClick={() => setSelectedDriverId(d.id)}
                    className={`w-full text-left p-3 rounded-lg border transition ${
                      isSelected
                        ? 'bg-blue-50/80 border-blue-300 shadow-sm'
                        : 'border-slate-100 hover:border-slate-200 hover:bg-slate-50'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className={`text-xs font-bold ${isSelected ? 'text-blue-900' : 'text-slate-900'}`}>
                        {d.full_name}
                      </span>
                      {d.pending_count > 0 && (
                        <span className="text-[10px] font-bold px-1.5 py-0.2 rounded-full bg-amber-100 text-amber-800 border border-amber-200">
                          {d.pending_count} pending
                        </span>
                      )}
                    </div>
                    <div className="flex items-center justify-between text-[11px] text-slate-500 mt-1">
                      <span className="flex items-center gap-1 font-mono">
                        <Bus className="w-3 h-3 text-slate-400" />
                        {d.assigned_bus_number || 'No Bus'}
                      </span>
                      <span className="font-semibold text-slate-700">
                        ₹{(d.approved_spend || 0).toLocaleString()}
                      </span>
                    </div>
                  </button>
                );
              })
            )}
          </div>
        </div>

        {/* Right 3 Columns: Selected Driver's Dashboard & Bills */}
        <div className="lg:col-span-3 space-y-5">
          {selectedDriver ? (
            <>
              {/* Driver Summary Banner */}
              <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-slate-100">
                  <div>
                    <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                      <span>{selectedDriver.full_name}</span>
                      <span className="text-xs px-2 py-0.5 rounded-full font-mono font-normal bg-slate-100 text-slate-600">
                        @{selectedDriver.username}
                      </span>
                    </h3>
                    <p className="text-xs text-slate-500 mt-0.5">
                      Assigned Vehicle: <strong className="text-slate-800">{selectedDriver.assigned_bus_number || 'Unassigned'}</strong> 
                      {selectedDriver.assigned_bus_registration && ` (${selectedDriver.assigned_bus_registration})`}
                      {selectedDriver.assigned_bus_fuel_type && (
                        <span className="ml-2 px-2 py-0.5 rounded text-[10px] font-bold bg-blue-50 text-blue-700 border border-blue-200">
                          {selectedDriver.assigned_bus_fuel_type}
                        </span>
                      )}
                    </p>
                  </div>

                  {/* Filter by status */}
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-slate-500">Status Filter:</span>
                    <select
                      value={statusFilter}
                      onChange={(e) => setStatusFilter(e.target.value)}
                      className="text-xs border border-slate-200 rounded-lg px-2.5 py-1.5 bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-600"
                    >
                      <option value="">All Statuses</option>
                      <option value="APPROVED">Approved Only</option>
                      <option value="PENDING">Pending Review</option>
                      <option value="CORRECTION_REQUIRED">Needs Correction</option>
                      <option value="REJECTED">Rejected</option>
                    </select>
                  </div>
                </div>

                {/* Driver Stats */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-4">
                  <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
                    <span className="text-[11px] text-slate-500 block">Total Records</span>
                    <span className="text-base font-bold text-slate-900 mt-0.5 block">
                      {selectedDriver.total_records}
                    </span>
                  </div>
                  <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
                    <span className="text-[11px] text-slate-500 block">Approved Spend</span>
                    <span className="text-base font-bold text-blue-700 mt-0.5 block">
                      ₹{selectedDriver.approved_spend.toLocaleString()}
                    </span>
                  </div>
                  <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
                    <span className="text-[11px] text-slate-500 block">Pending Queue</span>
                    <span className="text-base font-bold text-amber-600 mt-0.5 block">
                      {selectedDriver.pending_count}
                    </span>
                  </div>
                  <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
                    <span className="text-[11px] text-slate-500 block">Approved Entries</span>
                    <span className="text-base font-bold text-emerald-700 mt-0.5 block">
                      {selectedDriver.approved_count}
                    </span>
                  </div>
                </div>
              </div>

              {/* Driver's Fuel Records Table */}
              <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                <div className="p-4 border-b border-slate-100 flex items-center justify-between">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700">
                    Fuel Submissions ({records.length})
                  </h4>
                  <span className="text-[11px] text-slate-400">
                    Showing latest submissions first
                  </span>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left border-collapse text-xs">
                    <thead>
                      <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 uppercase text-[11px] font-bold">
                        <th className="py-3 px-4">Ref Code</th>
                        <th className="py-3 px-4">Date</th>
                        <th className="py-3 px-4">Bus & Fuel</th>
                        <th className="py-3 px-4">Volume & Rate</th>
                        <th className="py-3 px-4">Total Amount</th>
                        <th className="py-3 px-4">Odometer</th>
                        <th className="py-3 px-4">Status</th>
                        <th className="py-3 px-4 text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {loadingRecords ? (
                        <tr>
                          <td colSpan="8" className="text-center py-10 text-slate-400">
                            Loading driver fuel records...
                          </td>
                        </tr>
                      ) : records.length === 0 ? (
                        <tr>
                          <td colSpan="8" className="text-center py-10 text-slate-400">
                            No fuel records found for this driver matching the criteria.
                          </td>
                        </tr>
                      ) : (
                        records.map(r => (
                          <tr key={r.id} className="hover:bg-slate-50/70 transition">
                            <td className="py-3 px-4 font-mono font-bold text-blue-700">
                              {r.reference_code}
                            </td>
                            <td className="py-3 px-4 text-slate-600">
                              {r.bill_date ? new Date(r.bill_date).toLocaleDateString() : '—'}
                            </td>
                            <td className="py-3 px-4">
                              <span className="font-bold text-slate-900 block">{r.bus_number}</span>
                              <span className={`inline-block mt-0.5 text-[10px] font-semibold px-1.5 py-0.2 rounded ${
                                r.fuel_type === 'CNG' ? 'bg-amber-100 text-amber-900 border border-amber-200' : 'bg-slate-100 text-slate-700'
                              }`}>
                                {r.fuel_type === 'CNG' ? 'LEGACY DEMO (CNG)' : 'DIESEL'}
                              </span>
                            </td>
                            <td className="py-3 px-4">
                              <span className="font-semibold text-slate-800 block">
                                {r.fuel_litres} {r.fuel_type === 'CNG' ? 'kg' : 'L'}
                              </span>
                              <span className="text-[11px] text-slate-500">
                                @ ₹{r.rate_per_litre}/{r.fuel_type === 'CNG' ? 'kg' : 'L'}
                              </span>
                            </td>
                            <td className="py-3 px-4 font-bold text-slate-900">
                              ₹{r.total_cost.toFixed(2)}
                            </td>
                            <td className="py-3 px-4 font-mono text-slate-700">
                              {r.odometer_reading ? `${r.odometer_reading.toLocaleString()} km` : '—'}
                              {r.distance_travelled_km && (
                                <span className="block text-[10px] text-slate-400 font-sans">
                                  +{r.distance_travelled_km} km dist
                                </span>
                              )}
                            </td>
                            <td className="py-3 px-4">
                              <StatusBadge status={r.status} />
                            </td>
                            <td className="py-3 px-4 text-right space-x-1.5">
                              <button
                                onClick={() => setSelectedBillRecord(r)}
                                className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-100 text-slate-600 transition"
                                title="Quick View Bill Receipt"
                              >
                                <FileText className="w-3.5 h-3.5" />
                              </button>
                              <Link
                                to={`/requests/${r.id}`}
                                className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-blue-50 hover:bg-blue-100 text-blue-700 font-semibold transition"
                                title="Full Inspection"
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
            </>
          ) : (
            <div className="bg-white rounded-xl border border-slate-200 p-12 text-center text-slate-400 text-xs">
              Select a driver from the left list to view all their submitted bills and history.
            </div>
          )}
        </div>
      </div>

      {/* Bill Receipt Preview Modal */}
      {selectedBillRecord && (
        <SecureBillModal
          isOpen={Boolean(selectedBillRecord)}
          onClose={() => setSelectedBillRecord(null)}
          filename={selectedBillRecord.bill_image_filename}
          referenceCode={selectedBillRecord.reference_code}
          ocrData={selectedBillRecord.ocr_extracted_data}
          ocrConfidence={selectedBillRecord.ocr_confidence_score}
          ocrStatus={selectedBillRecord.ocr_status}
        />
      )}
    </div>
  );
};

export default DriverBills;
