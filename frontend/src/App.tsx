import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { User } from './types';
import { STORAGE_KEYS } from './utils/constants';

// Components
import RoleSelection from './components/RoleSelectionCard';
import Layout from './components/Layout';

// Pages
import LoginPage from './pages/LoginPage';
import StudentDashboard from './pages/StudentDashboard';
import TeacherDashboard from './pages/TeacherDashboard';
import AdminDashboard from './pages/AdminDashboard';

// Placeholder components for other routes
const AnalyticsPage = () => (
  <div className="card">
    <h1 className="text-2xl font-bold text-gray-900 mb-4">Analytics</h1>
    <p className="text-gray-600">Analytics page coming soon...</p>
  </div>
);

const NotificationsPage = () => (
  <div className="card">
    <h1 className="text-2xl font-bold text-gray-900 mb-4">Notifications</h1>
    <p className="text-gray-600">Notifications page coming soon...</p>
  </div>
);

const ProfilePage = () => (
  <div className="card">
    <h1 className="text-2xl font-bold text-gray-900 mb-4">Profile</h1>
    <p className="text-gray-600">Profile page coming soon...</p>
  </div>
);

const HelpPage = () => (
  <div className="card">
    <h1 className="text-2xl font-bold text-gray-900 mb-4">Help & Support</h1>
    <p className="text-gray-600">Help page coming soon...</p>
  </div>
);

function App() {
  const [user, setUser] = useState<User | null>(null);
  const [selectedRole, setSelectedRole] = useState<'student' | 'teacher' | 'admin' | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for existing user session
    const storedUser = localStorage.getItem(STORAGE_KEYS.USER_DATA);
    if (storedUser) {
      try {
        const userData = JSON.parse(storedUser);
        setUser(userData);
      } catch (error) {
        console.error('Error parsing stored user data:', error);
        localStorage.removeItem(STORAGE_KEYS.USER_DATA);
      }
    }
    setLoading(false);
  }, []);

  const handleRoleSelect = (role: 'student' | 'teacher' | 'admin') => {
    setSelectedRole(role);
  };

  const handleLogin = (userData: User) => {
    setUser(userData);
    setSelectedRole(null);
  };

  const handleLogout = () => {
    setUser(null);
    setSelectedRole(null);
    localStorage.removeItem(STORAGE_KEYS.USER_DATA);
    localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-linkedin-blue rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-white font-bold text-2xl">AI</span>
          </div>
          <div className="text-lg font-medium text-gray-900">Loading...</div>
        </div>
      </div>
    );
  }

  // If no user is logged in, show role selection or login
  if (!user) {
    if (selectedRole) {
      return (
        <LoginPage
          role={selectedRole}
          onLogin={handleLogin}
        />
      );
    }
    return <RoleSelection onRoleSelect={handleRoleSelect} />;
  }

  // Render appropriate dashboard based on user role
  const renderDashboard = () => {
    switch (user.role) {
      case 'student':
        return <StudentDashboard user={user} />;
      case 'teacher':
        return <TeacherDashboard user={user} />;
      case 'admin':
        return <AdminDashboard user={user} />;
      default:
        return <div>Invalid user role</div>;
    }
  };

  return (
    <Router>
      <Layout user={user} onLogout={handleLogout}>
        <Routes>
          <Route path="/dashboard" element={renderDashboard()} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/notifications" element={<NotificationsPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/help" element={<HelpPage />} />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
