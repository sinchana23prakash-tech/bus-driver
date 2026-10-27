import React from 'react';

const StatCard = ({ title, value, subtitle, icon: Icon, color = 'blue' }) => {
  const colorMap = {
    blue: 'bg-blue-50 text-blue-700 border-blue-200',
    amber: 'bg-amber-50 text-amber-700 border-amber-200',
    emerald: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    rose: 'bg-rose-50 text-rose-700 border-rose-200',
    indigo: 'bg-indigo-50 text-indigo-700 border-indigo-200',
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm flex items-start justify-between">
      <div>
        <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{title}</p>
        <p className="text-2xl font-bold text-slate-900 mt-1">{value}</p>
        {subtitle && <p className="text-xs text-slate-500 mt-1">{subtitle}</p>}
      </div>
      {Icon && (
        <div className={`p-3 rounded-lg border ${colorMap[color] || colorMap.blue}`}>
          <Icon className="w-5 h-5" />
        </div>
      )}
    </div>
  );
};

export default StatCard;
