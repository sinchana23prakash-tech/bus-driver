import React, { useState, useEffect, useMemo } from 'react';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';
import { 
  ResponsiveContainer, 
  AreaChart, 
  Area, 
  BarChart, 
  Bar, 
  PieChart, 
  Pie, 
  Cell, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend 
} from 'recharts';
import { 
  BarChart3, 
  PieChart as PieIcon,
  Calendar, 
  ChevronLeft, 
  ChevronRight, 
  Download, 
  Search, 
  FileSpreadsheet, 
  FileText, 
  RefreshCw, 
  TrendingUp, 
  Fuel, 
  Bus, 
  Users, 
  IndianRupee, 
  Filter, 
  ArrowUpDown, 
  CheckCircle2, 
  Clock, 
  XCircle, 
  AlertTriangle,
  Layers,
  FileCheck
} from 'lucide-react';

const AnalyticsReports = () => {
  const { token } = useAuth();
  const [period, setPeriod] = useState('monthly'); // 'weekly', 'monthly', 'yearly', 'all'
  const [offset, setOffset] = useState(0);
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(true);

  // Table filters & sorting
  const [tableSearch, setTableSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [sortField, setSortField] = useState('bill_date');
  const [sortAsc, setSortAsc] = useState(false);
  const [activeTab, setActiveTab] = useState('buses'); // 'buses' or 'drivers'

  const fetchReport = async () => {
    setLoading(true);
    try {
      const res = await api.get('/analytics/periodic-report', {
        params: { period, offset }
      });
      setReportData(res.data);
    } catch (err) {
      console.error('Failed to load periodic analytics report:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReport();
  }, [period, offset]);

  // Handle period switch: reset offset to 0
  const handlePeriodChange = (newPeriod) => {
    setPeriod(newPeriod);
    setOffset(0);
  };

  // CSV Export for current period
  const handleExportCsv = () => {
    if (!reportData) return;
    const { start_date, end_date } = reportData;
    let url = `/api/reports/fuel-csv?token=${encodeURIComponent(token)}`;
    if (start_date && end_date && period !== 'all') {
      url += `&start_date=${start_date}&end_date=${end_date}`;
    }
    window.open(url, '_blank');
  };

  // PDF Export
  const handleExportPdf = () => {
    window.open(`/api/reports/fuel-pdf?token=${encodeURIComponent(token)}`, '_blank');
  };

  // Client-side export of currently filtered table
  const handleExportFilteredTableCsv = () => {
    if (!filteredRecords.length) return;
    const headers = ['Reference Code', 'Bill Date', 'Bus', 'Registration', 'Driver', 'Fuel Type', 'Litres', 'Rate (INR)', 'Total Cost (INR)', 'Odometer', 'Station', 'Status'];
    const rows = filteredRecords.map(r => [
      r.reference_code,
      r.formatted_date,
      r.bus_number,
      r.registration_number,
      r.driver_name,
      r.fuel_type,
      r.fuel_litres,
      r.rate_per_litre,
      r.total_cost,
      r.odometer_reading,
      `"${(r.fuel_station_name || '').replace(/"/g, '""')}"`,
      r.status
    ]);

    const csvContent = [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `GMU_Fuel_Report_${period}_${reportData?.range_label?.replace(/\s+/g, '_') || 'export'}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const summary = reportData?.summary || {};
  const timeSeries = reportData?.time_series || [];
  const statusDist = reportData?.status_distribution || [];
  const busWise = reportData?.bus_wise || [];
  const driverWise = reportData?.driver_wise || [];
  const rawRecords = reportData?.records || [];

  // Filtered and sorted records for table
  const filteredRecords = useMemo(() => {
    return rawRecords
      .filter(r => {
        if (statusFilter !== 'ALL' && r.status !== statusFilter) return false;
        if (!tableSearch.trim()) return true;
        const q = tableSearch.toLowerCase();
        return (
          r.reference_code?.toLowerCase().includes(q) ||
          r.bus_number?.toLowerCase().includes(q) ||
          r.registration_number?.toLowerCase().includes(q) ||
          r.driver_name?.toLowerCase().includes(q) ||
          r.fuel_station_name?.toLowerCase().includes(q)
        );
      })
      .sort((a, b) => {
        let valA = a[sortField];
        let valB = b[sortField];
        if (typeof valA === 'string') valA = valA.toLowerCase();
        if (typeof valB === 'string') valB = valB.toLowerCase();
        if (valA < valB) return sortAsc ? -1 : 1;
        if (valA > valB) return sortAsc ? 1 : -1;
        return 0;
      });
  }, [rawRecords, tableSearch, statusFilter, sortField, sortAsc]);

  const toggleSort = (field) => {
    if (sortField === field) {
      setSortAsc(!sortAsc);
    } else {
      setSortField(field);
      setSortAsc(false);
    }
  };

  const statusColors = {
    APPROVED: { bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200' },
    PENDING: { bg: 'bg-amber-50', text: 'text-amber-800', border: 'border-amber-200' },
    REJECTED: { bg: 'bg-rose-50', text: 'text-rose-700', border: 'border-rose-200' },
    CORRECTION_REQUIRED: { bg: 'bg-indigo-50', text: 'text-indigo-700', border: 'border-indigo-200' }
  };

  return (
    <div className="space-y-6">
      {/* Top Header & Export Controls */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl sm:text-2xl font-bold text-stone-900 font-serif">
              Fleet Analytics & Audit Reports
            </h2>
            <span className="text-[10px] bg-[#541019] text-white px-2 py-0.5 rounded font-bold uppercase tracking-wider">
              GM University
            </span>
          </div>
          <p className="text-xs text-stone-500 mt-1">
            Dynamic periodic analytics, fuel expenditure telemetry, bus economy, and regulatory audit summaries
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={fetchReport}
            disabled={loading}
            className="p-2 rounded-lg border border-stone-300 bg-white hover:bg-stone-50 text-stone-700 text-xs font-semibold shadow-sm transition disabled:opacity-50"
            title="Refresh Data"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
          <button
            onClick={handleExportCsv}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-stone-300 bg-white hover:bg-stone-50 text-stone-700 text-xs font-semibold shadow-sm transition"
          >
            <FileSpreadsheet className="w-4 h-4 text-emerald-700" />
            <span>Export Period CSV</span>
          </button>
          <button
            onClick={handleExportPdf}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#541019] hover:bg-[#68131f] text-white text-xs font-bold shadow-sm transition"
          >
            <FileText className="w-4 h-4 text-rose-100" />
            <span>Audit PDF</span>
          </button>
        </div>
      </div>

      {/* Period Selection & Navigator Bar */}
      <div className="bg-white rounded-xl border border-stone-200 p-4 shadow-sm flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Period Tabs: Weekly, Monthly, Yearly, All Time */}
        <div className="flex items-center bg-stone-100 p-1 rounded-lg w-full md:w-auto">
          {[
            { id: 'weekly', label: 'Weekly' },
            { id: 'monthly', label: 'Monthly' },
            { id: 'yearly', label: 'Yearly' },
            { id: 'all', label: 'All Time' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => handlePeriodChange(tab.id)}
              className={`flex-1 md:flex-none px-4 py-1.5 rounded-md text-xs font-bold transition-all ${
                period === tab.id
                  ? 'bg-[#541019] text-white shadow-sm'
                  : 'text-stone-600 hover:text-stone-900 hover:bg-stone-200/60'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Date Navigator Controls */}
        <div className="flex items-center gap-2 w-full md:w-auto justify-between md:justify-end">
          {period !== 'all' && (
            <div className="flex items-center gap-1">
              <button
                onClick={() => setOffset(prev => prev - 1)}
                className="p-1.5 rounded-lg border border-stone-300 hover:bg-stone-100 text-stone-700 text-xs font-semibold transition"
                title="Previous Period"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              {offset !== 0 && (
                <button
                  onClick={() => setOffset(0)}
                  className="px-2 py-1 rounded-md text-[11px] font-bold text-[#541019] hover:bg-rose-50 border border-rose-200 transition"
                >
                  Latest
                </button>
              )}
            </div>
          )}

          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#fdf2f4] border border-[#fad0d6] text-[#541019] text-xs font-bold">
            <Calendar className="w-3.5 h-3.5 text-[#68131f]" />
            <span>{reportData?.range_label || 'Loading date range...'}</span>
          </div>

          {period !== 'all' && (
            <button
              onClick={() => setOffset(prev => prev + 1)}
              className="p-1.5 rounded-lg border border-stone-300 hover:bg-stone-100 text-stone-700 text-xs font-semibold transition"
              title="Next Period"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* KPI Summary Cards Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Requests */}
        <div className="bg-white rounded-xl border border-stone-200 p-4 shadow-sm">
          <div className="flex items-center justify-between text-stone-500 mb-2">
            <span className="text-[11px] font-bold uppercase tracking-wider">Total Fuel Requests</span>
            <div className="p-2 rounded-lg bg-stone-100 text-[#541019]">
              <FileCheck className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-stone-900 font-mono">
            {summary.total_requests || 0}
          </div>
          <div className="mt-1 flex items-center gap-2 text-[11px] text-stone-500 font-medium">
            <span className="text-emerald-700 font-bold">{summary.approved_count || 0} approved</span>
            <span>•</span>
            <span className="text-amber-800 font-bold">{summary.pending_count || 0} pending</span>
          </div>
        </div>

        {/* Total Fuel Issued */}
        <div className="bg-white rounded-xl border border-stone-200 p-4 shadow-sm">
          <div className="flex items-center justify-between text-stone-500 mb-2">
            <span className="text-[11px] font-bold uppercase tracking-wider">Total Fuel Issued</span>
            <div className="p-2 rounded-lg bg-stone-100 text-blue-700">
              <Fuel className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-stone-900 font-mono">
            {(summary.total_fuel_issued || 0).toLocaleString('en-IN', { maximumFractionDigits: 2 })} <span className="text-sm font-sans font-normal text-stone-500">L</span>
          </div>
          <div className="mt-1 text-[11px] text-stone-500">
            Across all submitted claims
          </div>
        </div>

        {/* Total Fuel Consumption (Approved) */}
        <div className="bg-white rounded-xl border border-stone-200 p-4 shadow-sm">
          <div className="flex items-center justify-between text-stone-500 mb-2">
            <span className="text-[11px] font-bold uppercase tracking-wider">Approved Consumption</span>
            <div className="p-2 rounded-lg bg-emerald-50 text-emerald-700">
              <Fuel className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-emerald-800 font-mono">
            {(summary.total_fuel_consumption || 0).toLocaleString('en-IN', { maximumFractionDigits: 2 })} <span className="text-sm font-sans font-normal text-emerald-600">L</span>
          </div>
          <div className="mt-1 text-[11px] text-emerald-700 font-medium">
            Operational verified fleet burn
          </div>
        </div>

        {/* Total Approved Expenditure */}
        <div className="bg-white rounded-xl border border-stone-200 p-4 shadow-sm">
          <div className="flex items-center justify-between text-stone-500 mb-2">
            <span className="text-[11px] font-bold uppercase tracking-wider">Approved Expenditure</span>
            <div className="p-2 rounded-lg bg-[#fdf2f4] text-[#541019]">
              <IndianRupee className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-[#541019] font-mono">
            ₹{(summary.total_expenditure || 0).toLocaleString('en-IN', { maximumFractionDigits: 2 })}
          </div>
          <div className="mt-1 text-[11px] text-stone-500 flex items-center justify-between">
            <span>Pending: ₹{(summary.pending_expenditure || 0).toLocaleString('en-IN')}</span>
            <span>Avg: ₹{summary.average_rate || 0}/L</span>
          </div>
        </div>
      </div>

      {/* Additional Secondary Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="bg-stone-50 rounded-lg p-3 border border-stone-200 text-center">
          <span className="text-[11px] text-stone-500 uppercase font-semibold">Buses Served</span>
          <p className="text-lg font-bold text-stone-900 mt-0.5">{summary.buses_served || 0} Vehicles</p>
        </div>
        <div className="bg-stone-50 rounded-lg p-3 border border-stone-200 text-center">
          <span className="text-[11px] text-stone-500 uppercase font-semibold">Active Drivers</span>
          <p className="text-lg font-bold text-stone-900 mt-0.5">{summary.drivers_active || 0} Personnel</p>
        </div>
        <div className="bg-stone-50 rounded-lg p-3 border border-stone-200 text-center">
          <span className="text-[11px] text-stone-500 uppercase font-semibold">Rejected Logs</span>
          <p className="text-lg font-bold text-rose-700 mt-0.5">{summary.rejected_count || 0} Logs</p>
        </div>
        <div className="bg-stone-50 rounded-lg p-3 border border-stone-200 text-center">
          <span className="text-[11px] text-stone-500 uppercase font-semibold">Correction Requests</span>
          <p className="text-lg font-bold text-indigo-700 mt-0.5">{summary.correction_count || 0} Logs</p>
        </div>
      </div>

      {/* Interactive Charts Row 1: Expenditure & Volume Trend + Status Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Trend Area/Bar Chart (Spans 2 columns) */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-stone-200 p-5 shadow-sm space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-b border-stone-100 pb-3">
            <div>
              <h3 className="text-sm font-bold text-stone-900 flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-[#541019]" />
                <span>Fuel Expenditure & Consumption Trends</span>
              </h3>
              <p className="text-xs text-stone-500">
                {period === 'weekly' && 'Day-by-day expenditure (₹) and fuel volume (L) for the selected week'}
                {period === 'monthly' && 'Weekly progression of approved spend (₹) and litres for the selected month'}
                {period === 'yearly' && 'Month-by-month annual fleet expenditure and fuel burn'}
                {period === 'all' && 'All-time monthly historical fleet expenditure'}
              </p>
            </div>
            <span className="text-xs font-semibold px-2.5 py-1 rounded bg-stone-100 text-stone-700">
              {reportData?.range_label}
            </span>
          </div>

          <div className="h-72 w-full">
            {timeSeries.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={timeSeries} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
                  <defs>
                    <linearGradient id="gmuSpendGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#541019" stopOpacity={0.4}/>
                      <stop offset="95%" stopColor="#541019" stopOpacity={0.0}/>
                    </linearGradient>
                    <linearGradient id="gmuVolumeGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#0284c7" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#0284c7" stopOpacity={0.0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f5f5f4" />
                  <XAxis 
                    dataKey="short_label" 
                    tick={{ fontSize: 11, fill: '#78716c' }} 
                  />
                  <YAxis 
                    yAxisId="left"
                    tickFormatter={(v) => `₹${v >= 1000 ? `${(v/1000).toFixed(0)}k` : v}`} 
                    tick={{ fontSize: 11, fill: '#78716c' }} 
                  />
                  <YAxis 
                    yAxisId="right"
                    orientation="right"
                    tickFormatter={(v) => `${v}L`} 
                    tick={{ fontSize: 11, fill: '#78716c' }} 
                  />
                  <Tooltip
                    formatter={(value, name) => [
                      name === 'approved_cost' ? `₹${Number(value).toLocaleString('en-IN')}` : `${value} Litres`,
                      name === 'approved_cost' ? 'Approved Spend' : 'Fuel Volume'
                    ]}
                    labelFormatter={(label, items) => {
                      const item = items?.[0]?.payload;
                      return item?.label || label;
                    }}
                    contentStyle={{ borderRadius: '8px', fontSize: '12px', border: '1px solid #e7e5e4' }}
                  />
                  <Legend 
                    formatter={(val) => val === 'approved_cost' ? 'Approved Spend (₹)' : 'Fuel Volume (Litres)'}
                    wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }}
                  />
                  <Area 
                    yAxisId="left" 
                    type="monotone" 
                    dataKey="approved_cost" 
                    stroke="#541019" 
                    strokeWidth={2}
                    fillOpacity={1} 
                    fill="url(#gmuSpendGradient)" 
                  />
                  <Area 
                    yAxisId="right" 
                    type="monotone" 
                    dataKey="approved_litres" 
                    stroke="#0284c7" 
                    strokeWidth={2}
                    fillOpacity={1} 
                    fill="url(#gmuVolumeGradient)" 
                  />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-stone-400">
                No telemetry data available for this date period.
              </div>
            )}
          </div>
        </div>

        {/* Status Distribution Pie / Doughnut Chart */}
        <div className="bg-white rounded-xl border border-stone-200 p-5 shadow-sm space-y-4">
          <div className="border-b border-stone-100 pb-3">
            <h3 className="text-sm font-bold text-stone-900 flex items-center gap-2">
              <PieIcon className="w-4 h-4 text-[#541019]" />
              <span>Request Review Statistics</span>
            </h3>
            <p className="text-xs text-stone-500">Distribution across review states</p>
          </div>

          <div className="h-52 w-full flex items-center justify-center">
            {summary.total_requests > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={statusDist}
                    dataKey="count"
                    nameKey="label"
                    cx="50%"
                    cy="50%"
                    innerRadius={45}
                    outerRadius={75}
                    paddingAngle={3}
                  >
                    {statusDist.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(val, name, item) => [
                      `${val} requests (₹${(item.payload.total_cost || 0).toLocaleString('en-IN')})`,
                      name
                    ]}
                    contentStyle={{ borderRadius: '8px', fontSize: '12px' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-xs text-stone-400">No requests in this period</div>
            )}
          </div>

          {/* Custom Status Legend */}
          <div className="space-y-1.5 pt-2 border-t border-stone-100 text-xs">
            {statusDist.map((st) => (
              <div key={st.status} className="flex items-center justify-between text-stone-600">
                <span className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full shrink-0" style={{ backgroundColor: st.color }}></span>
                  <span>{st.label}</span>
                </span>
                <span className="font-mono font-bold text-stone-900">
                  {st.count} ({summary.total_requests > 0 ? Math.round((st.count / summary.total_requests) * 100) : 0}%)
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Interactive Charts Row 2: Bus-Wise vs Driver-Wise Bar Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Bus-wise Fuel Consumption Chart */}
        <div className="bg-white rounded-xl border border-stone-200 p-5 shadow-sm space-y-4">
          <div>
            <h3 className="text-sm font-bold text-stone-900 flex items-center gap-2">
              <Bus className="w-4 h-4 text-[#541019]" />
              <span>Bus-Wise Fuel Consumption (Litres)</span>
            </h3>
            <p className="text-xs text-stone-500">Volume and expenditure allocation per college bus</p>
          </div>

          <div className="h-64 w-full">
            {busWise.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={busWise} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f5f5f4" />
                  <XAxis dataKey="bus_number" tick={{ fontSize: 11, fill: '#78716c' }} />
                  <YAxis tickFormatter={(v) => `${v}L`} tick={{ fontSize: 11, fill: '#78716c' }} />
                  <Tooltip
                    formatter={(val, name) => [
                      name === 'approved_litres' ? `${val} Litres` : `₹${Number(val).toLocaleString('en-IN')}`,
                      name === 'approved_litres' ? 'Approved Litres' : 'Approved Spend'
                    ]}
                    contentStyle={{ borderRadius: '8px', fontSize: '12px' }}
                  />
                  <Legend 
                    formatter={(v) => v === 'approved_litres' ? 'Approved Volume (L)' : 'Total Cost (₹)'}
                    wrapperStyle={{ fontSize: '11px', paddingTop: '6px' }}
                  />
                  <Bar dataKey="approved_litres" fill="#541019" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="approved_cost" fill="#0284c7" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-stone-400">
                No bus telemetry recorded for this period.
              </div>
            )}
          </div>
        </div>

        {/* Driver-wise Fuel Usage Chart */}
        <div className="bg-white rounded-xl border border-stone-200 p-5 shadow-sm space-y-4">
          <div>
            <h3 className="text-sm font-bold text-stone-900 flex items-center gap-2">
              <Users className="w-4 h-4 text-[#541019]" />
              <span>Driver-Wise Fuel Allocation</span>
            </h3>
            <p className="text-xs text-stone-500">Fuel volume dispensed per authorized campus driver</p>
          </div>

          <div className="h-64 w-full">
            {driverWise.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={driverWise} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f5f5f4" />
                  <XAxis dataKey="driver_name" tick={{ fontSize: 11, fill: '#78716c' }} />
                  <YAxis tickFormatter={(v) => `${v}L`} tick={{ fontSize: 11, fill: '#78716c' }} />
                  <Tooltip
                    formatter={(val, name) => [
                      name === 'approved_litres' ? `${val} Litres` : `₹${Number(val).toLocaleString('en-IN')}`,
                      name === 'approved_litres' ? 'Approved Fuel' : 'Approved Spend'
                    ]}
                    contentStyle={{ borderRadius: '8px', fontSize: '12px' }}
                  />
                  <Legend 
                    formatter={(v) => v === 'approved_litres' ? 'Approved Litres (L)' : 'Spend (₹)'}
                    wrapperStyle={{ fontSize: '11px', paddingTop: '6px' }}
                  />
                  <Bar dataKey="approved_litres" fill="#68131f" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="total_cost" fill="#78716c" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-stone-400">
                No driver submissions recorded for this period.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Breakdown Tab Switcher (Bus Efficiency vs Driver Performance) */}
      <div className="bg-white rounded-xl border border-stone-200 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-stone-200 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setActiveTab('buses')}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition ${
                activeTab === 'buses'
                  ? 'bg-[#541019] text-white shadow-sm'
                  : 'text-stone-600 hover:bg-stone-100'
              }`}
            >
              Bus Fleet Performance ({busWise.length})
            </button>
            <button
              onClick={() => setActiveTab('drivers')}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition ${
                activeTab === 'drivers'
                  ? 'bg-[#541019] text-white shadow-sm'
                  : 'text-stone-600 hover:bg-stone-100'
              }`}
            >
              Driver Usage Summary ({driverWise.length})
            </button>
          </div>
          <span className="text-xs text-stone-500 font-medium">
            Period: <strong className="text-stone-800">{reportData?.range_label}</strong>
          </span>
        </div>

        {activeTab === 'buses' ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-stone-50 border-b border-stone-200 text-stone-600 uppercase text-[11px] font-bold">
                  <th className="py-3 px-4">Bus Identifier</th>
                  <th className="py-3 px-4">Registration</th>
                  <th className="py-3 px-4">Model</th>
                  <th className="py-3 px-4">Fuel Type</th>
                  <th className="py-3 px-4">Approved Litres</th>
                  <th className="py-3 px-4">Approved Spend</th>
                  <th className="py-3 px-4">Distance (KM)</th>
                  <th className="py-3 px-4 text-right">Economy (KM/L)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-stone-100">
                {busWise.length === 0 ? (
                  <tr>
                    <td colSpan="8" className="py-8 text-center text-stone-400">
                      No bus records in this period.
                    </td>
                  </tr>
                ) : (
                  busWise.map((b) => (
                    <tr key={b.bus_id} className="hover:bg-stone-50/60 transition">
                      <td className="py-3 px-4 font-bold text-stone-900 flex items-center gap-2">
                        <Bus className="w-4 h-4 text-[#541019] shrink-0" />
                        <span>{b.bus_number}</span>
                      </td>
                      <td className="py-3 px-4 font-mono text-stone-700">{b.registration_number || 'N/A'}</td>
                      <td className="py-3 px-4 text-stone-600">{b.model_name || 'N/A'}</td>
                      <td className="py-3 px-4">
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#fdf2f4] text-[#541019] border border-[#fad0d6]">
                          {b.fuel_type}
                        </span>
                      </td>
                      <td className="py-3 px-4 font-semibold text-stone-900 font-mono">{b.approved_litres} L</td>
                      <td className="py-3 px-4 font-semibold text-[#541019] font-mono">₹{b.approved_cost.toLocaleString('en-IN')}</td>
                      <td className="py-3 px-4 font-mono text-stone-700">{b.distance_km > 0 ? `${b.distance_km} km` : '—'}</td>
                      <td className="py-3 px-4 text-right">
                        {b.average_kmpl ? (
                          <span className="font-bold text-emerald-800 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200">
                            {b.average_kmpl} km/L
                          </span>
                        ) : (
                          <span className="text-stone-400 italic">Baseline</span>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-stone-50 border-b border-stone-200 text-stone-600 uppercase text-[11px] font-bold">
                  <th className="py-3 px-4">Driver Name</th>
                  <th className="py-3 px-4">Username</th>
                  <th className="py-3 px-4">Allocated Buses</th>
                  <th className="py-3 px-4">Submissions</th>
                  <th className="py-3 px-4">Total Fuel</th>
                  <th className="py-3 px-4">Approved Fuel</th>
                  <th className="py-3 px-4 text-right">Total Expenditure</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-stone-100">
                {driverWise.length === 0 ? (
                  <tr>
                    <td colSpan="7" className="py-8 text-center text-stone-400">
                      No driver logs in this period.
                    </td>
                  </tr>
                ) : (
                  driverWise.map((d) => (
                    <tr key={d.driver_id} className="hover:bg-stone-50/60 transition">
                      <td className="py-3 px-4 font-bold text-stone-900 flex items-center gap-2">
                        <Users className="w-4 h-4 text-[#541019] shrink-0" />
                        <span>{d.driver_name}</span>
                      </td>
                      <td className="py-3 px-4 font-mono text-stone-600">{d.username}</td>
                      <td className="py-3 px-4">
                        <div className="flex flex-wrap gap-1">
                          {d.buses?.length > 0 ? (
                            d.buses.map(b => (
                              <span key={b} className="px-1.5 py-0.5 rounded text-[10px] bg-stone-100 text-stone-700 font-mono">
                                {b}
                              </span>
                            ))
                          ) : (
                            <span className="text-stone-400">—</span>
                          )}
                        </div>
                      </td>
                      <td className="py-3 px-4 font-mono">{d.requests_count} ({d.approved_count} approved)</td>
                      <td className="py-3 px-4 font-semibold text-stone-800 font-mono">{d.total_litres} L</td>
                      <td className="py-3 px-4 font-semibold text-emerald-800 font-mono">{d.approved_litres} L</td>
                      <td className="py-3 px-4 text-right font-bold text-[#541019] font-mono">
                        ₹{d.total_cost.toLocaleString('en-IN')}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Comprehensive Report Transactions Table with Search & Filter */}
      <div className="bg-white rounded-xl border border-stone-200 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-stone-200 space-y-3">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div>
              <h3 className="text-sm font-bold text-stone-900 flex items-center gap-2">
                <FileSpreadsheet className="w-4 h-4 text-[#541019]" />
                <span>Period Fuel Transactions Audit Register</span>
              </h3>
              <p className="text-xs text-stone-500">
                Detailed transaction records falling within <strong className="text-stone-700">{reportData?.range_label}</strong>
              </p>
            </div>
            <button
              onClick={handleExportFilteredTableCsv}
              disabled={filteredRecords.length === 0}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-stone-300 bg-stone-50 hover:bg-stone-100 text-stone-700 text-xs font-semibold shadow-sm transition disabled:opacity-50"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Download Filtered Table CSV ({filteredRecords.length})</span>
            </button>
          </div>

          {/* Table Search & Status Filters */}
          <div className="flex flex-col sm:flex-row items-center gap-3 pt-1">
            <div className="relative flex-1 w-full">
              <Search className="w-4 h-4 text-stone-400 absolute left-3 top-2.5" />
              <input
                type="text"
                placeholder="Search by reference, bus, driver, or station..."
                value={tableSearch}
                onChange={(e) => setTableSearch(e.target.value)}
                className="w-full pl-9 pr-3 py-1.5 text-xs border border-stone-300 rounded-lg focus:ring-2 focus:ring-[#541019] focus:outline-none"
              />
            </div>

            <div className="flex items-center gap-2 w-full sm:w-auto">
              <Filter className="w-3.5 h-3.5 text-stone-400 shrink-0" />
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full sm:w-auto px-2.5 py-1.5 text-xs border border-stone-300 rounded-lg focus:ring-2 focus:ring-[#541019] focus:outline-none font-medium"
              >
                <option value="ALL">All Statuses ({rawRecords.length})</option>
                <option value="APPROVED">Approved ({summary.approved_count || 0})</option>
                <option value="PENDING">Pending Review ({summary.pending_count || 0})</option>
                <option value="REJECTED">Rejected ({summary.rejected_count || 0})</option>
                <option value="CORRECTION_REQUIRED">Correction Needed ({summary.correction_count || 0})</option>
              </select>
            </div>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-stone-50 border-b border-stone-200 text-stone-600 uppercase text-[11px] font-bold select-none">
                <th onClick={() => toggleSort('bill_date')} className="py-3 px-4 cursor-pointer hover:bg-stone-100">
                  <div className="flex items-center gap-1.5">
                    <span>Date & Time</span>
                    <ArrowUpDown className="w-3 h-3 text-stone-400" />
                  </div>
                </th>
                <th onClick={() => toggleSort('reference_code')} className="py-3 px-4 cursor-pointer hover:bg-stone-100">
                  <div className="flex items-center gap-1.5">
                    <span>Ref Code</span>
                    <ArrowUpDown className="w-3 h-3 text-stone-400" />
                  </div>
                </th>
                <th onClick={() => toggleSort('bus_number')} className="py-3 px-4 cursor-pointer hover:bg-stone-100">
                  <div className="flex items-center gap-1.5">
                    <span>Bus</span>
                    <ArrowUpDown className="w-3 h-3 text-stone-400" />
                  </div>
                </th>
                <th onClick={() => toggleSort('driver_name')} className="py-3 px-4 cursor-pointer hover:bg-stone-100">
                  <div className="flex items-center gap-1.5">
                    <span>Driver</span>
                    <ArrowUpDown className="w-3 h-3 text-stone-400" />
                  </div>
                </th>
                <th onClick={() => toggleSort('fuel_litres')} className="py-3 px-4 cursor-pointer hover:bg-stone-100">
                  <div className="flex items-center gap-1.5">
                    <span>Litres</span>
                    <ArrowUpDown className="w-3 h-3 text-stone-400" />
                  </div>
                </th>
                <th className="py-3 px-4">Rate (₹/L)</th>
                <th onClick={() => toggleSort('total_cost')} className="py-3 px-4 cursor-pointer hover:bg-stone-100">
                  <div className="flex items-center gap-1.5">
                    <span>Total Cost (₹)</span>
                    <ArrowUpDown className="w-3 h-3 text-stone-400" />
                  </div>
                </th>
                <th className="py-3 px-4">Odometer</th>
                <th className="py-3 px-4">Station</th>
                <th className="py-3 px-4 text-center">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-stone-100">
              {filteredRecords.length === 0 ? (
                <tr>
                  <td colSpan="10" className="py-12 text-center text-stone-400">
                    <p className="font-semibold text-stone-600">No records found matching your filters.</p>
                    <p className="text-xs mt-1">Try switching the date period or clearing search filters.</p>
                  </td>
                </tr>
              ) : (
                filteredRecords.map((r) => {
                  const stStyle = statusColors[r.status] || statusColors.PENDING;
                  return (
                    <tr key={r.id} className="hover:bg-stone-50/70 transition">
                      <td className="py-3 px-4 font-mono text-stone-600 whitespace-nowrap">
                        {r.formatted_date}
                      </td>
                      <td className="py-3 px-4 font-mono font-bold text-stone-900 whitespace-nowrap">
                        {r.reference_code}
                      </td>
                      <td className="py-3 px-4">
                        <div className="font-bold text-stone-900">{r.bus_number}</div>
                        <div className="text-[10px] text-stone-500 font-mono">{r.registration_number}</div>
                      </td>
                      <td className="py-3 px-4 font-medium text-stone-800">
                        {r.driver_name}
                      </td>
                      <td className="py-3 px-4 font-mono font-semibold text-stone-900">
                        {r.fuel_litres} L
                      </td>
                      <td className="py-3 px-4 font-mono text-stone-600">
                        ₹{r.rate_per_litre.toFixed(2)}
                      </td>
                      <td className="py-3 px-4 font-mono font-bold text-[#541019]">
                        ₹{r.total_cost.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </td>
                      <td className="py-3 px-4 font-mono text-stone-600">
                        {r.odometer_reading?.toLocaleString()} km
                      </td>
                      <td className="py-3 px-4 text-stone-600 max-w-xs truncate">
                        {r.fuel_station_name}
                      </td>
                      <td className="py-3 px-4 text-center whitespace-nowrap">
                        <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-bold border ${stStyle.bg} ${stStyle.text} ${stStyle.border}`}>
                          {r.status === 'APPROVED' && <CheckCircle2 className="w-3 h-3" />}
                          {r.status === 'PENDING' && <Clock className="w-3 h-3" />}
                          {r.status === 'REJECTED' && <XCircle className="w-3 h-3" />}
                          {r.status === 'CORRECTION_REQUIRED' && <AlertTriangle className="w-3 h-3" />}
                          <span>{r.status}</span>
                        </span>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Table Footer Summary */}
        <div className="p-3 bg-stone-50 border-t border-stone-200 text-xs text-stone-600 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
          <span>
            Showing <strong className="text-stone-900">{filteredRecords.length}</strong> of <strong className="text-stone-900">{rawRecords.length}</strong> records in this period
          </span>
          <div className="flex items-center gap-4 font-mono font-semibold">
            <span>
              Filtered Fuel: <strong className="text-stone-900">{filteredRecords.reduce((acc, r) => acc + r.fuel_litres, 0).toFixed(1)} L</strong>
            </span>
            <span>
              Filtered Total: <strong className="text-[#541019]">₹{filteredRecords.reduce((acc, r) => acc + r.total_cost, 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</strong>
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsReports;
