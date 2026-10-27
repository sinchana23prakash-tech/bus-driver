import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';

import Login from './pages/Login';
import InitialSetup from './pages/InitialSetup';
import Dashboard from './pages/Dashboard';
import FuelRequests from './pages/FuelRequests';
import FuelDetailReview from './pages/FuelDetailReview';
import DriverBills from './pages/DriverBills';
import FleetManagement from './pages/FleetManagement';
import ApprovedBunks from './pages/ApprovedBunks';
import UserManagement from './pages/UserManagement';
import AnalyticsReports from './pages/AnalyticsReports';
import AuditLogs from './pages/AuditLogs';

const AppLayout = () => {
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Navbar />
      <div className="flex-1 flex overflow-hidden">
        <Sidebar />
        <main className="flex-1 p-6 md:p-8 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public Auth Routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/initial-setup" element={<InitialSetup />} />

          {/* Protected Routes for Admin & VC */}
          <Route
            element={
              <ProtectedRoute allowedRoles={['ADMIN', 'VC']}>
                <AppLayout />
              </ProtectedRoute>
            }
          >
            <Route path="/" element={<Dashboard />} />
            <Route path="/requests" element={<FuelRequests />} />
            <Route path="/requests/:id" element={<FuelDetailReview />} />
            <Route path="/drivers" element={<DriverBills />} />
            
            {/* Admin-only Configuration Routes */}
            <Route
              path="/fleet"
              element={
                <ProtectedRoute allowedRoles={['ADMIN']}>
                  <FleetManagement />
                </ProtectedRoute>
              }
            />
            <Route
              path="/bunks"
              element={
                <ProtectedRoute allowedRoles={['ADMIN']}>
                  <ApprovedBunks />
                </ProtectedRoute>
              }
            />
            <Route
              path="/users"
              element={
                <ProtectedRoute allowedRoles={['ADMIN']}>
                  <UserManagement />
                </ProtectedRoute>
              }
            />

            {/* Admin-only Audit Trail (Removed for VC) */}
            <Route
              path="/audit"
              element={
                <ProtectedRoute allowedRoles={['ADMIN']}>
                  <AuditLogs />
                </ProtectedRoute>
              }
            />

            {/* Admin and VC shared Reports */}
            <Route path="/analytics" element={<AnalyticsReports />} />
          </Route>

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
