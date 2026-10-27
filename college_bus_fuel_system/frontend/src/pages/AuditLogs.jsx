import React, { useState, useEffect } from 'react';
import api from '../api/client';
import { ClipboardList, Shield, Search, RefreshCw } from 'lucide-react';

const AuditLogs = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterAction, setFilterAction] = useState('');

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const params = {};
      if (filterAction) params.action = filterAction;
      const res = await api.get('/audit-logs', { params });
      setLogs(res.data.audit_logs || []);
    } catch (err) {
      console.error('Failed to load audit logs:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [filterAction]);

  return (
    <div className="space-y-5">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h2 className="text-xl font-bold text-slate-900">Regulatory Audit Trail</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Immutable log of all administrative actions, status transitions, and data submissions
          </p>
        </div>
        <button
          onClick={fetchLogs}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 text-xs font-semibold shadow-sm transition"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh Trail</span>
        </button>
      </div>

      {/* Filter Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <span className="text-xs font-semibold text-slate-600">Filter Event Action:</span>
          <select
            value={filterAction}
            onChange={(e) => setFilterAction(e.target.value)}
            className="text-xs border border-slate-300 rounded-lg px-3 py-1.5 bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-600"
          >
            <option value="">All Logged Actions</option>
            <option value="FUEL_ENTRY_SUBMITTED">Fuel Entry Submitted</option>
            <option value="RECORD_APPROVED">Record Approved</option>
            <option value="RECORD_REJECTED">Record Rejected</option>
            <option value="RECORD_CORRECTION_REQUESTED">Correction Requested</option>
            <option value="RECORD_RESUBMITTED_AFTER_CORRECTION">Record Resubmitted</option>
            <option value="USER_CREATED">User Created</option>
            <option value="BUS_CREATED">Bus Created</option>
            <option value="BUNK_CONFIGURED">Fuel Station Configured</option>
          </select>
        </div>

        <span className="text-xs text-slate-400 font-mono">
          Showing latest {logs.length} system events
        </span>
      </div>

      {/* Logs Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 uppercase text-[11px] font-bold">
                <th className="py-3 px-4">Timestamp (UTC)</th>
                <th className="py-3 px-4">Actor</th>
                <th className="py-3 px-4">Role</th>
                <th className="py-3 px-4">Action</th>
                <th className="py-3 px-4">Entity</th>
                <th className="py-3 px-4">Event Details</th>
                <th className="py-3 px-4 text-right">IP Address</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-mono">
              {loading ? (
                <tr>
                  <td colSpan="7" className="text-center py-10 text-slate-500 font-sans">
                    Loading audit events...
                  </td>
                </tr>
              ) : logs.length === 0 ? (
                <tr>
                  <td colSpan="7" className="text-center py-10 text-slate-400 font-sans">
                    No audit records match the criteria.
                  </td>
                </tr>
              ) : (
                logs.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-50/70 transition">
                    <td className="py-3 px-4 text-slate-500 whitespace-nowrap">
                      {new Date(log.created_at).toLocaleString()}
                    </td>
                    <td className="py-3 px-4 font-bold text-slate-900 font-sans">
                      {log.actor_name}
                    </td>
                    <td className="py-3 px-4">
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-700">
                        {log.actor_role}
                      </span>
                    </td>
                    <td className="py-3 px-4 font-bold text-blue-700">
                      {log.action}
                    </td>
                    <td className="py-3 px-4 text-slate-600 font-sans">
                      {log.entity_type} #{log.entity_id}
                    </td>
                    <td className="py-3 px-4 text-slate-700 font-sans max-w-md truncate">
                      {log.details || '—'}
                    </td>
                    <td className="py-3 px-4 text-right text-slate-400">
                      {log.ip_address || '127.0.0.1'}
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

export default AuditLogs;
