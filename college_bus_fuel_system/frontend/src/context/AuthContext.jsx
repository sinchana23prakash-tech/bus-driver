import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../api/client';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    try {
      const saved = localStorage.getItem('college_fuel_user');
      return saved && saved !== 'undefined' ? JSON.parse(saved) : null;
    } catch (_) {
      localStorage.removeItem('college_fuel_user');
      return null;
    }
  });
  const [token, setToken] = useState(() => localStorage.getItem('college_fuel_token') || null);
  const [policies, setPolicies] = useState(() => {
    try {
      const saved = localStorage.getItem('college_fuel_policies');
      return saved && saved !== 'undefined' ? JSON.parse(saved) : { vc_can_approve: false };
    } catch (_) {
      return { vc_can_approve: false };
    }
  });
  const [loading, setLoading] = useState(() => Boolean(localStorage.getItem('college_fuel_token')));

  useEffect(() => {
    const verifySession = async () => {
      if (token) {
        try {
          const res = await api.get('/auth/me');
          setUser(res.data.user);
          setPolicies(res.data.policies || { vc_can_approve: false });
          localStorage.setItem('college_fuel_user', JSON.stringify(res.data.user));
          localStorage.setItem('college_fuel_policies', JSON.stringify(res.data.policies || { vc_can_approve: false }));
        } catch (err) {
          logout();
        }
      }
      setLoading(false);
    };
    verifySession();
  }, [token]);

  const login = (authToken, authUser, authPolicies) => {
    setToken(authToken);
    setUser(authUser);
    setPolicies(authPolicies || { vc_can_approve: false });
    localStorage.setItem('college_fuel_token', authToken);
    localStorage.setItem('college_fuel_user', JSON.stringify(authUser));
    localStorage.setItem('college_fuel_policies', JSON.stringify(authPolicies || { vc_can_approve: false }));
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    setPolicies({ vc_can_approve: false });
    localStorage.removeItem('college_fuel_token');
    localStorage.removeItem('college_fuel_user');
    localStorage.removeItem('college_fuel_policies');
  };

  return (
    <AuthContext.Provider value={{ user, token, policies, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
