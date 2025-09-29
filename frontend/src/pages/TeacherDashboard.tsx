import React, { useState, useEffect } from 'react';
import { Calendar, Clock, FileText, Bell, User, BookOpen, CheckCircle, XCircle } from 'lucide-react';
import { Teacher, Timetable, LeaveApplication, Notification } from '../types';
import { ScheduleGrid } from '../components/ScheduleCard';
import { LeaveApplicationForm } from '../components/LeaveApplicationForm';
import { AnalyticsBarChart } from '../components/AnalyticsChart';
import { apiService } from '../services/api';

interface TeacherDashboardProps {
  user: Teacher;
}

const TeacherDashboard: React.FC<TeacherDashboardProps> = ({ user }) => {
  const [timetable, setTimetable] = useState<Timetable | null>(null);
  const [leaveHistory, setLeaveHistory] = useState<LeaveApplication[]>([]);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [view, setView] = useState<'daily' | 'weekly'>('weekly');
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [showLeaveForm, setShowLeaveForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [leaveLoading, setLeaveLoading] = useState(false);
  const [leaveError, setLeaveError] = useState('');

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load timetable
      const timetableResponse = await apiService.getTeacherTimetable(user.id);
      if (timetableResponse.success) {
        setTimetable(timetableResponse.data);
      }

      // Load leave history
      const leaveResponse = await apiService.getLeaveHistory(user.id);
      if (leaveResponse.success) {
        setLeaveHistory(leaveResponse.data);
      }

      // Load notifications
      const notificationsResponse = await apiService.getNotifications(user.id);
      if (notificationsResponse.success) {
        setNotifications(notificationsResponse.data);
      }
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLeaveSubmit = async (data: any) => {
    try {
      setLeaveLoading(true);
      setLeaveError('');
      
      const response = await apiService.applyLeave(data);
      if (response.success) {
        setLeaveHistory(prev => [response.data, ...prev]);
        setShowLeaveForm(false);
        // Show success message
      } else {
        setLeaveError(response.error || 'Failed to submit leave application');
      }
    } catch (error: any) {
      setLeaveError(error.response?.data?.error || 'Network error. Please try again.');
    } finally {
      setLeaveLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'approved':
        return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'rejected':
        return <XCircle className="w-4 h-4 text-red-600" />;
      case 'pending':
        return <Clock className="w-4 h-4 text-yellow-600" />;
      default:
        return <Clock className="w-4 h-4 text-gray-600" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved':
        return 'status-approved';
      case 'rejected':
        return 'status-rejected';
      case 'pending':
        return 'status-pending';
      default:
        return 'status-normal';
    }
  };

  const getWorkloadData = () => {
    if (!timetable) return [];

    // Group by day
    const dayHours: Record<string, number> = {};
    timetable.schedules.forEach(schedule => {
      dayHours[schedule.time_slot.day] = (dayHours[schedule.time_slot.day] || 0) + 1;
    });

    return Object.keys(dayHours).map(day => ({
      name: day,
      hours: dayHours[day]
    }));
  };

  const workloadData = getWorkloadData();

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[...Array(4)].map((_, index) => (
            <div key={index} className="card animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-8 bg-gray-200 rounded w-1/2"></div>
            </div>
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card animate-pulse">
            <div className="h-64 bg-gray-200 rounded"></div>
          </div>
          <div className="card animate-pulse">
            <div className="h-64 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="card bg-gradient-to-r from-green-600 to-green-700 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold mb-2">
              Welcome back, {user.name}!
            </h1>
            <p className="text-green-100">
              {user.department} • {user.subjects.join(', ')}
            </p>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold">{timetable?.schedules.length || 0}</div>
            <div className="text-green-100">Classes this week</div>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center">
            <div className="p-3 bg-blue-100 rounded-lg">
              <Calendar className="w-6 h-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Classes</p>
              <p className="text-2xl font-bold text-gray-900">{timetable?.schedules.length || 0}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-3 bg-green-100 rounded-lg">
              <Clock className="w-6 h-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Teaching Hours</p>
              <p className="text-2xl font-bold text-gray-900">
                {timetable?.schedules.length || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-3 bg-purple-100 rounded-lg">
              <FileText className="w-6 h-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Leave Applications</p>
              <p className="text-2xl font-bold text-gray-900">{leaveHistory.length}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-3 bg-orange-100 rounded-lg">
              <Bell className="w-6 h-6 text-orange-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Notifications</p>
              <p className="text-2xl font-bold text-gray-900">
                {notifications.filter(n => !n.is_read).length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Timetable Section */}
        <div className="lg:col-span-2 space-y-6">
          {/* View Toggle */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900">Your Teaching Schedule</h2>
              <div className="flex space-x-2">
                <button
                  onClick={() => setView('weekly')}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    view === 'weekly'
                      ? 'bg-linkedin-blue text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  Weekly
                </button>
                <button
                  onClick={() => setView('daily')}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    view === 'daily'
                      ? 'bg-linkedin-blue text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  Daily
                </button>
              </div>
            </div>

            {timetable ? (
              <ScheduleGrid
                schedules={timetable.schedules}
                view={view}
                selectedDate={selectedDate}
                onScheduleClick={(schedule) => {
                  console.log('Schedule clicked:', schedule);
                }}
              />
            ) : (
              <div className="text-center py-12">
                <BookOpen className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No timetable available</h3>
                <p className="text-gray-600">Your teaching schedule will appear here once it's generated.</p>
              </div>
            )}
          </div>

          {/* Leave Management */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900">Leave Management</h2>
              <button
                onClick={() => setShowLeaveForm(!showLeaveForm)}
                className="btn-primary"
              >
                Apply for Leave
              </button>
            </div>

            {showLeaveForm && (
              <div className="mb-6">
                <LeaveApplicationForm
                  onSubmit={handleLeaveSubmit}
                  loading={leaveLoading}
                  error={leaveError}
                />
              </div>
            )}

            {/* Leave History */}
            <div className="space-y-4">
              <h3 className="font-medium text-gray-900">Recent Applications</h3>
              {leaveHistory.length > 0 ? (
                <div className="space-y-3">
                  {leaveHistory.slice(0, 5).map((leave) => (
                    <div key={leave.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          {getStatusIcon(leave.status)}
                          <div>
                            <p className="font-medium text-gray-900">
                              {new Date(leave.start_date).toLocaleDateString()} - {new Date(leave.end_date).toLocaleDateString()}
                            </p>
                            <p className="text-sm text-gray-600">{leave.reason}</p>
                          </div>
                        </div>
                        <span className={getStatusColor(leave.status)}>
                          {leave.status}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <FileText className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                  <p className="text-gray-500 text-sm">No leave applications yet</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Workload Analysis */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Weekly Workload</h3>
            {workloadData.length > 0 ? (
              <AnalyticsBarChart
                data={workloadData}
                title="Classes by Day"
                xAxisKey="name"
                yAxisKey="hours"
                height={200}
              />
            ) : (
              <div className="text-center py-8">
                <Clock className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                <p className="text-gray-500 text-sm">No data available</p>
              </div>
            )}
          </div>

          {/* Notifications */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Notifications</h3>
            <div className="space-y-3">
              {notifications.slice(0, 5).map((notification) => (
                <div
                  key={notification.id}
                  className={`p-3 rounded-lg border ${
                    notification.is_read
                      ? 'bg-gray-50 border-gray-200'
                      : 'bg-blue-50 border-blue-200'
                  }`}
                >
                  <div className="flex items-start space-x-3">
                    <div className={`w-2 h-2 rounded-full mt-2 ${
                      notification.is_read ? 'bg-gray-400' : 'bg-blue-600'
                    }`} />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900">
                        {notification.title}
                      </p>
                      <p className="text-xs text-gray-600 mt-1">
                        {notification.message}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        {new Date(notification.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
              {notifications.length === 0 && (
                <div className="text-center py-8">
                  <Bell className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                  <p className="text-gray-500 text-sm">No notifications</p>
                </div>
              )}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
            <div className="space-y-3">
              <button className="w-full btn-primary text-left">
                View Full Schedule
              </button>
              <button className="w-full btn-secondary text-left">
                Download Timetable
              </button>
              <button className="w-full btn-secondary text-left">
                Contact Admin
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TeacherDashboard;
