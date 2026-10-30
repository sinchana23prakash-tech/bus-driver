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

  const sections = [
    {
      title: 'OVERVIEW',
      items: [
        { to: '/', label: 'Dashboard', icon: LayoutDashboard, show: true },
      ]
    },
    {
      title: 'FUEL MANAGEMENT',
      items: [
        { to: '/requests', label: 'Fuel Requests', icon: Fuel, show: true },
        { to: '/drivers', label: 'Driver Bills', icon: Users, show: isAdmin || isVC },
      ]
    },
    {
      title: 'FLEET & ACCOUNTS',
      items: [
        { to: '/fleet', label: 'Fleet Management', icon: Bus, show: isAdmin },
        { to: '/users', label: 'User Accounts', icon: UserCheck, show: isAdmin },
      ]
    },
    {
      title: 'ANALYTICS & COMPLIANCE',
      items: [
        { to: '/analytics', label: 'Analytics & Reports', icon: BarChart3, show: isAdmin || isVC },
        { to: '/audit', label: 'Audit Trail', icon: ClipboardList, show: isAdmin },
      ]
    }
  ];

  return (
    <aside className="w-64 bg-[#380a10] text-rose-100 min-h-[calc(100vh-5.5rem)] p-4 flex flex-col justify-between shrink-0 border-r border-[#26050a] shadow-inner">
      <div className="space-y-5">
        {sections.map((section) => {
          const visibleItems = section.items.filter(item => item.show);
          if (visibleItems.length === 0) return null;

          return (
            <div key={section.title}>
              <p className="px-3 text-[10px] font-bold text-[#d8b15a] uppercase tracking-widest mb-1.5 opacity-90">
                {section.title}
              </p>
              <nav className="space-y-1">
                {visibleItems.map((item) => {
                  const Icon = item.icon;
                  return (
                    <NavLink
                      key={item.to}
                      to={item.to}
                      end={item.to === '/'}
                      className={({ isActive }) =>
                        `flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-semibold transition-all ${
                          isActive
                            ? 'bg-[#541019] text-[#f6d782] shadow-sm border-l-4 border-[#d8b15a] ring-1 ring-[#d8b15a]/20 translate-x-0.5'
                            : 'text-rose-100/75 hover:bg-[#4a0d16] hover:text-white'
                        }`
                      }
                    >
                      <Icon className="w-4 h-4 shrink-0 text-[#d8b15a]" />
                      <span>{item.label}</span>
                    </NavLink>
                  );
                })}
              </nav>
            </div>
          );
        })}
      </div>

      <div className="pt-3 border-t border-[#4a0d16] text-[11px] text-rose-200/70 space-y-0.5 px-3 bg-[#26050a]/40 p-2.5 rounded-lg mt-4">
        <p className="font-bold text-[#f6d782]">GM University Transport</p>
        <p className="text-[10px] opacity-75">Fleet & Fuel Portal v2.0</p>
      </div>
    </aside>
  );
};

export default Sidebar;
