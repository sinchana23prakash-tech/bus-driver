import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  LayoutDashboard, 
  Fuel, 
  Bus, 
  MapPin, 
  Users, 
  UserCheck,
  BarChart3, 
  ClipboardList 
} from 'lucide-react';

const Sidebar = () => {
  const { user } = useAuth();
  const isAdmin = user?.role === 'ADMIN';
  const isVC = user?.role === 'VC';

  const navItems = [
    { to: '/', label: 'Dashboard', icon: LayoutDashboard, show: true },
    { to: '/requests', label: 'Fuel Requests', icon: Fuel, show: true },
    { to: '/drivers', label: 'Driver Bills', icon: Users, show: isAdmin || isVC },
    { to: '/fleet', label: 'Fleet Management', icon: Bus, show: isAdmin },
    { to: '/users', label: 'User Accounts', icon: UserCheck, show: isAdmin },
    { to: '/analytics', label: 'Analytics & Reports', icon: BarChart3, show: isAdmin || isVC },
    { to: '/audit', label: 'Audit Trail', icon: ClipboardList, show: isAdmin }, // Hidden from VC
  ];

  return (
    <aside className="w-64 bg-slate-900 text-slate-300 min-h-[calc(100vh-4rem)] p-4 flex flex-col justify-between shrink-0">
      <div className="space-y-6">
        <div>
          <p className="px-3 text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2">
            Navigation Menu
          </p>
          <nav className="space-y-1">
            {navItems.filter(item => item.show).map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.to === '/'}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                      isActive
                        ? 'bg-blue-600 text-white shadow-sm'
                        : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                    }`
                  }
                >
                  <Icon className="w-4 h-4 shrink-0" />
                  <span>{item.label}</span>
                </NavLink>
              );
            })}
          </nav>
        </div>
      </div>

      <div className="pt-4 border-t border-slate-800 text-xs text-slate-400 space-y-1 px-3">
        <p className="font-semibold text-slate-300">College Transport Division</p>
        <p>Campus Bus Fuel System v1.0</p>
      </div>
    </aside>
  );
};

export default Sidebar;
