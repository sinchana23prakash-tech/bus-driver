import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../api/client';
import StatCard from '../components/StatCard';
import { 
  Fuel, 
  IndianRupee, 
  ArrowRight
} from 'lucide-react';

const Dashboard = () => {
  const [overview, setOverview] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const overviewRes = await api.get('/analytics/overview');
        setOverview(overviewRes.data);
      } catch (err) {
        console.error('Failed to load dashboard data:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  const statusDist = overview?.status_distribution || {};
  const currentMonthLabel = overview?.current_month_label || 'Current Month';

  return (
    <div className="space-y-6">
      {/* Top Banner / Welcome */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h2 className="text-xl font-bold text-slate-900">Institutional Diesel Fleet Overview</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Current month approved Diesel expenditure and consumption across all college buses
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Link
            to="/requests"
            className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-sm transition"
          >
            <span>Review Queue</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>

      {/* KPI Cards: Only Diesel Spend and Diesel Consumed for Current Month */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <StatCard
          title="Diesel Spend"
          value={`₹${(overview?.current_month_diesel_spend || 0).toLocaleString('en-IN', { maximumFractionDigits: 2 })}`}
          subtitle={`Approved Diesel • ${currentMonthLabel}`}
          icon={IndianRupee}
          color="blue"
        />
        <StatCard
          title="Diesel Consumed"
          value={`${(overview?.current_month_diesel_litres || 0).toLocaleString('en-IN', { maximumFractionDigits: 2 })} L`}
          subtitle={`Approved Volume • ${currentMonthLabel}`}
          icon={Fuel}
          color="emerald"
        />
      </div>

      {/* Bill Review Status Distribution Summary */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-b border-slate-100 pb-3">
          <div>
            <h3 className="font-bold text-slate-900 text-sm">Bill Review Status Distribution</h3>
            <p className="text-xs text-slate-500">Mutual status breakdown of all submitted institution fuel records</p>
          </div>
          <span className="text-xs font-medium text-slate-500">
            Authorized Station: <strong className="text-slate-800">IOC DEALERS, DSS FUEL SOUK</strong>
          </span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="p-3 rounded-lg border border-emerald-100 bg-emerald-50/50">
            <div className="text-[11px] font-bold text-emerald-800 uppercase tracking-wider">Approved</div>
            <div className="text-lg font-bold text-emerald-950 mt-1 font-mono">
              {statusDist['APPROVED']?.count || 0} bills
            </div>
            <div className="text-xs text-emerald-700 mt-0.5">
              ₹{(statusDist['APPROVED']?.total_cost || 0).toLocaleString('en-IN')}
            </div>
          </div>

          <div className="p-3 rounded-lg border border-amber-100 bg-amber-50/50">
            <div className="text-[11px] font-bold text-amber-800 uppercase tracking-wider">Pending Review</div>
            <div className="text-lg font-bold text-amber-950 mt-1 font-mono">
              {statusDist['PENDING']?.count || 0} bills
            </div>
            <div className="text-xs text-amber-700 mt-0.5">
              ₹{(statusDist['PENDING']?.total_cost || 0).toLocaleString('en-IN')}
            </div>
          </div>

          <div className="p-3 rounded-lg border border-rose-100 bg-rose-50/50">
            <div className="text-[11px] font-bold text-rose-800 uppercase tracking-wider">Rejected</div>
            <div className="text-lg font-bold text-rose-950 mt-1 font-mono">
              {statusDist['REJECTED']?.count || 0} bills
            </div>
            <div className="text-xs text-rose-700 mt-0.5">
              ₹{(statusDist['REJECTED']?.total_cost || 0).toLocaleString('en-IN')}
            </div>
          </div>

          <div className="p-3 rounded-lg border border-blue-100 bg-blue-50/50">
            <div className="text-[11px] font-bold text-blue-800 uppercase tracking-wider">Correction Needed</div>
            <div className="text-lg font-bold text-blue-950 mt-1 font-mono">
              {statusDist['CORRECTION_REQUIRED']?.count || 0} bills
            </div>
            <div className="text-xs text-blue-700 mt-0.5">
              ₹{(statusDist['CORRECTION_REQUIRED']?.total_cost || 0).toLocaleString('en-IN')}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
