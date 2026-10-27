import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const ProtectedRoute = ({ children, allowedRoles }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return (
      <div className="min-h-screen bg-slate-900 flex flex-col items-center justify-center p-6 text-white text-center">
        <div className="max-w-md bg-slate-800 p-8 rounded-2xl border border-slate-700 shadow-xl space-y-4">
          <div className="w-12 h-12 bg-amber-500/20 text-amber-400 rounded-xl flex items-center justify-center mx-auto">
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h2 className="text-xl font-bold">Access Restricted</h2>
          <p className="text-xs text-slate-400 leading-relaxed">
            Your account ({user.username} &bull; {user.role}) is not authorized to access this administration section. Driver accounts should use the mobile application.
          </p>
          <button
            onClick={() => {
              localStorage.removeItem('college_fuel_token');
              localStorage.removeItem('college_fuel_user');
              window.location.href = '/login';
            }}
            className="w-full py-2.5 px-4 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs transition"
          >
            Switch Account / Sign In
          </button>
        </div>
      </div>
    );
  }

  return children;
};

export default ProtectedRoute;
