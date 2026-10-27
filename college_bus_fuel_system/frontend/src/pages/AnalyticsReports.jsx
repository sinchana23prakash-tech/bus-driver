import React, { useState, useEffect } from 'react';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer 
} from 'recharts';
import { 
  FileSpreadsheet, 
  FileText, 
  Gauge, 
  Bus, 
  RefreshCw, 
  TrendingUp, 
  Fuel, 
  Info,
  IndianRupee 
} from 'lucide-react';

const AnalyticsReports = () => {
  const { token } = useAuth();
  const [efficiency, setEfficiency] = useState([]);
  const [trends, setTrends] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [effRes, trendsRes] = await Promise.all([
        api.get('/analytics/bus-efficiency'),
        api.get('/analytics/monthly-trends')
      ]);
      setEfficiency(effRes.data.bus_efficiency || []);
      setTrends(trendsRes.data.monthly_trends || []);
    } catch (err) {
      console.error('Failed to load analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const downloadCsv = () => {
    window.open(`/api/reports/fuel-csv?token=${encodeURIComponent(token)}`, '_blank');
  };

  const downloadPdf = () => {
    window.open(`/api/reports/fuel-pdf?token=${encodeURIComponent(token)}`, '_blank');
  };

  // Helper to format month strings e.g. "2026-10" -> "Oct '26"
  const formatMonthTick = (val) => {
    if (!val) return '';
    try {
      const [y, m] = val.split('-');
      const d = new Date(parseInt(y, 10), parseInt(m, 10) - 1, 1);
      return d.toLocaleDateString('en-US', { month: 'short', year: '2-digit' });
    } catch {
      return val;
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h2 className="text-xl font-bold text-slate-900">Analytics & Institutional Compliance Reports</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Institutional expenditure trends, volume distribution, fuel economy evaluations, and regulatory exports
          </p>
        </div>

        {/* Export and Action Buttons */}
        <div className="flex items-center gap-2">
          <button
            onClick={fetchData}
            className="p-2 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 text-xs font-semibold shadow-sm transition"
            title="Refresh Data"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <button
            onClick={downloadCsv}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-300 bg-white hover:bg-slate-50 text-slate-700 text-xs font-semibold shadow-sm transition"
          >
            <FileSpreadsheet className="w-4 h-4 text-emerald-600" />
            <span>Export CSV</span>
          </button>
          <button
            onClick={downloadPdf}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-700 hover:bg-blue-800 text-white text-xs font-semibold shadow-sm transition"
          >
            <FileText className="w-4 h-4 text-blue-200" />
            <span>Download Audit PDF</span>
          </button>
        </div>
      </div>

      {/* Accounting and Data Precision Policy Banner */}
      <div className="bg-blue-50/70 border border-blue-200 rounded-xl p-3.5 text-xs text-blue-900 flex items-start gap-2.5">
        <Info className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
        <div className="leading-relaxed">
          <strong>Institutional Audit Accounting Standard:</strong> Historical expenditure and consumption charts calculate approved transactions strictly by verifiable receipt billing dates. Pending claims are displayed separately to provide transparency without double-counting. Rejected and correction-required entries are excluded from fleet mileage calculations.
        </div>
      </div>

      {/* Charts Grid: Expenditure Trend and Volume Consumption */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chart 1: Monthly Fuel Expenditure Trend (Moved from Dashboard) */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <IndianRupee className="w-4 h-4 text-blue-600" />
                <span>Monthly Fuel Expenditure Trend (₹)</span>
              </h3>
              <p className="text-xs text-slate-500">Approved financial spend vs. pending verification queue</p>
            </div>
            <TrendingUp className="w-4 h-4 text-slate-400" />
          </div>

          <div className="h-64 w-full">
            {trends.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={trends} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis 
                    dataKey="month" 
                    tickFormatter={formatMonthTick} 
                    tick={{ fontSize: 11, fill: '#64748b' }} 
                  />
                  <YAxis 
                    tickFormatter={(v) => `₹${v >= 1000 ? `${(v/1000).toFixed(0)}k` : v}`} 
                    tick={{ fontSize: 11, fill: '#64748b' }} 
                  />
                  <Tooltip
                    formatter={(value, name) => [
                      `₹${Number(value).toLocaleString('en-IN')}`, 
                      name === 'approved_cost' ? 'Approved Spend' : 'Pending Review'
                    ]}
                    labelFormatter={(label) => {
                      const item = trends.find(t => t.month === label);
                      return item?.month_label || label;
                    }}
                    contentStyle={{ borderRadius: '8px', fontSize: '12px' }}
                  />
                  <Legend 
                    formatter={(val) => val === 'approved_cost' ? 'Approved Spend (₹)' : 'Pending Review (₹)'}
                    wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }}
                  />
                  <Bar dataKey="approved_cost" fill="#2563eb" stackId="spend" radius={[0, 0, 0, 0]} />
                  <Bar dataKey="pending_cost" fill="#f59e0b" stackId="spend" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-slate-400">
                No recorded expenditure transactions yet.
              </div>
            )}
          </div>
        </div>

        {/* Chart 2: Monthly Fuel Volume Consumption */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <Fuel className="w-4 h-4 text-emerald-600" />
                <span>Monthly Fuel Volume Consumption</span>
              </h3>
              <p className="text-xs text-slate-500">Institutional Diesel Volume (Litres)</p>
            </div>
          </div>

          <div className="h-64 w-full">
            {trends.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={trends} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis 
                    dataKey="month" 
                    tickFormatter={formatMonthTick} 
                    tick={{ fontSize: 11, fill: '#64748b' }} 
                  />
                  <YAxis 
                    tickFormatter={(v) => `${v} L`}
                    tick={{ fontSize: 11, fill: '#64748b' }} 
                  />
                  <Tooltip
                    formatter={(value) => [
                      `${value} Litres`,
                      'Diesel Volume'
                    ]}
                    labelFormatter={(label) => {
                      const item = trends.find(t => t.month === label);
                      return item?.month_label || label;
                    }}
                    contentStyle={{ borderRadius: '8px', fontSize: '12px' }}
                  />
                  <Legend 
                    formatter={() => 'Diesel Volume (Litres)'}
                    wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }}
                  />
                  <Bar dataKey="diesel_litres" fill="#0284c7" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-slate-400">
                No historical fuel volume records available.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Per-Bus Mileage Efficiency & Reliability Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <Gauge className="w-4 h-4 text-blue-600" />
              <span>Bus-by-Bus Fuel Economy & Mileage Performance</span>
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Strictly calculated across verified consecutive odometer progressions per bus
            </p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 uppercase text-[11px] font-bold">
                <th className="py-3 px-4">Bus Identifier</th>
                <th className="py-3 px-4">Registration</th>
                <th className="py-3 px-4">Fuel Type</th>
                <th className="py-3 px-4">Current Odometer</th>
                <th className="py-3 px-4">Fuel Consumed</th>
                <th className="py-3 px-4">Approved Spend</th>
                <th className="py-3 px-4">Reliable Average Economy</th>
                <th className="py-3 px-4 text-right">Reliable Sequences</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan="8" className="text-center py-10 text-slate-500">
                    Loading efficiency statistics...
                  </td>
                </tr>
              ) : efficiency.length === 0 ? (
                <tr>
                  <td colSpan="8" className="text-center py-10 text-slate-400">
                    No bus efficiency logs found.
                  </td>
                </tr>
              ) : (
                efficiency.map((item) => (
                  <tr key={item.bus_id} className="hover:bg-slate-50/70 transition">
                    <td className="py-3 px-4 font-bold text-slate-900 flex items-center gap-2">
                      <Bus className="w-3.5 h-3.5 text-blue-600 shrink-0" />
                      <span>{item.bus_number}</span>
                    </td>
                    <td className="py-3 px-4 font-mono text-slate-700">
                      {item.registration_number}
                    </td>
                    <td className="py-3 px-4">
                      <span className="inline-block px-2 py-0.5 rounded text-[10px] font-bold bg-blue-50 text-blue-800 border border-blue-200">
                        DIESEL
                      </span>
                    </td>
                    <td className="py-3 px-4 font-mono font-semibold text-slate-800">
                      {item.current_odometer.toLocaleString()} km
                    </td>
                    <td className="py-3 px-4 font-semibold text-slate-700">
                      {item.total_litres} L
                    </td>
                    <td className="py-3 px-4 font-semibold text-blue-700">
                      ₹{item.total_spend.toLocaleString()}
                    </td>
                    <td className="py-3 px-4">
                      {item.reliable_avg_kmpl ? (
                        <span className="font-bold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200">
                          {item.reliable_avg_kmpl} km/L
                        </span>
                      ) : (
                        <span className="text-slate-400 italic">
                          Baseline / Insufficient Sequence
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-right font-mono font-semibold text-slate-600">
                      {item.reliable_samples_count} fill-up logs
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

export default AnalyticsReports;
