import React, { useState, useEffect } from 'react';
import { Calendar, Users, BarChart3, Bell, Upload, CheckCircle, XCircle, TrendingUp } from 'lucide-react';
import { Admin, Timetable, Analytics, Notification } from '../types';
import { ApprovalGrid } from '../components/ApprovalCard';
import { AnalyticsBarChart, AnalyticsPieChart, AnalyticsHeatmap } from '../components/AnalyticsChart';
import { apiService } from '../services/api';

interface AdminDashboardProps {
  user: Admin;
}

const AdminDashboard: React.FC<AdminDashboardProps> = ({ user }) => {
  const [timetables, setTimetables] = useState<Timetable[]>([]);
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [approvalLoading, setApprovalLoading] = useState(false);
  const [uploadLoading, setUploadLoading] = useState(false);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load pending timetables for approval
      const timetablesResponse = await apiService.getTimetable(user.institute_id);
      if (timetablesResponse.success) {
        setTimetables([timetablesResponse.data]);
      }

      // Load analytics
      const analyticsResponse = await apiService.getAnalytics(user.institute_id);
      if (analyticsResponse.success) {
        setAnalytics(analyticsResponse.data);
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

  const handleApprove = async (timetableId: string) => {
    try {
      setApprovalLoading(true);
      // Implement approval logic
      console.log('Approving timetable:', timetableId);
      // Reload data after approval
      await loadDashboardData();
    } catch (error) {
      console.error('Error approving timetable:', error);
    } finally {
      setApprovalLoading(false);
    }
  };

  const handleReject = async (timetableId: string, reason: string) => {
    try {
      setApprovalLoading(true);
      // Implement rejection logic
      console.log('Rejecting timetable:', timetableId, 'Reason:', reason);
      // Reload data after rejection
      await loadDashboardData();
    } catch (error) {
      console.error('Error rejecting timetable:', error);
    } finally {
      setApprovalLoading(false);
    }
  };

  const handleFileUpload = async (file: File, dataType: 'students' | 'teachers' | 'classrooms') => {
    try {
      setUploadLoading(true);
      const response = await apiService.uploadData(file, dataType);
      if (response.success) {
        // Show success message
        console.log('File uploaded successfully');
        // Reload data
        await loadDashboardData();
      }
    } catch (error) {
      console.error('Error uploading file:', error);
    } finally {
      setUploadLoading(false);
    }
  };

  const getTeacherLoadData = () => {
    if (!analytics) return [];
    return analytics.teacher_load.map(teacher => ({
      name: teacher.teacher_name,
      hours: teacher.total_hours
    }));
  };

  const getClassroomUtilizationData = () => {
    if (!analytics) return [];
    return analytics.classroom_utilization.map(room => ({
      name: room.room_name,
      utilization: room.utilization_percentage
    }));
  };

  const getHeatmapData = () => {
    // Generate sample heatmap data
    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
    const timeSlots = ['9:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00'];
    const data = [];
    
    for (const day of days) {
      for (const time of timeSlots) {
        data.push({
          day,
          time,
          value: Math.floor(Math.random() * 100)
        });
      }
    }
    
    return data;
  };

  const teacherLoadData = getTeacherLoadData();
  const classroomUtilizationData = getClassroomUtilizationData();
  const heatmapData = getHeatmapData();

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
      <div className="card bg-gradient-to-r from-purple-600 to-purple-700 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold mb-2">
              Welcome back, {user.name}!
            </h1>
            <p className="text-purple-100">
              Institute Administrator • Manage timetables and oversee operations
            </p>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold">{timetables.length}</div>
            <div className="text-purple-100">Pending Approvals</div>
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
              <p className="text-sm font-medium text-gray-600">Active Timetables</p>
              <p className="text-2xl font-bold text-gray-900">{timetables.length}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-3 bg-green-100 rounded-lg">
              <Users className="w-6 h-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Teachers</p>
              <p className="text-2xl font-bold text-gray-900">
                {analytics?.teacher_load.length || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-3 bg-purple-100 rounded-lg">
              <BarChart3 className="w-6 h-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Classroom Utilization</p>
              <p className="text-2xl font-bold text-gray-900">
                {analytics ? Math.round(analytics.classroom_utilization.reduce((acc, room) => acc + room.utilization_percentage, 0) / analytics.classroom_utilization.length) : 0}%
              </p>
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
        {/* Timetable Approval Section */}
        <div className="lg:col-span-2 space-y-6">
          {/* Timetable Approval */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900">Timetable Approval</h2>
              <span className="text-sm text-gray-500">
                {timetables.length} pending approval
              </span>
            </div>

            <ApprovalGrid
              timetables={timetables}
              onApprove={handleApprove}
              onReject={handleReject}
              loading={approvalLoading}
            />
          </div>

          {/* Data Management */}
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Institute Data Management</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center space-x-3 mb-3">
                  <Users className="w-8 h-8 text-blue-600" />
                  <div>
                    <h3 className="font-medium text-gray-900">Students</h3>
                    <p className="text-sm text-gray-600">Upload student data</p>
                  </div>
                </div>
                <input
                  type="file"
                  accept=".csv"
                  onChange={(e) => {
                    const file = e.target.files?.[0];
                    if (file) handleFileUpload(file, 'students');
                  }}
                  className="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                  disabled={uploadLoading}
                />
              </div>

              <div className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center space-x-3 mb-3">
                  <Users className="w-8 h-8 text-green-600" />
                  <div>
                    <h3 className="font-medium text-gray-900">Teachers</h3>
                    <p className="text-sm text-gray-600">Upload teacher data</p>
                  </div>
                </div>
                <input
                  type="file"
                  accept=".csv"
                  onChange={(e) => {
                    const file = e.target.files?.[0];
                    if (file) handleFileUpload(file, 'teachers');
                  }}
                  className="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-green-50 file:text-green-700 hover:file:bg-green-100"
                  disabled={uploadLoading}
                />
              </div>

              <div className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center space-x-3 mb-3">
                  <Calendar className="w-8 h-8 text-purple-600" />
                  <div>
                    <h3 className="font-medium text-gray-900">Classrooms</h3>
                    <p className="text-sm text-gray-600">Upload classroom data</p>
                  </div>
                </div>
                <input
                  type="file"
                  accept=".csv"
                  onChange={(e) => {
                    const file = e.target.files?.[0];
                    if (file) handleFileUpload(file, 'classrooms');
                  }}
                  className="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-purple-50 file:text-purple-700 hover:file:bg-purple-100"
                  disabled={uploadLoading}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Teacher Load Analysis */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Teacher Workload</h3>
            {teacherLoadData.length > 0 ? (
              <AnalyticsBarChart
                data={teacherLoadData}
                title="Teaching Hours by Teacher"
                xAxisKey="name"
                yAxisKey="hours"
                height={200}
              />
            ) : (
              <div className="text-center py-8">
                <TrendingUp className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                <p className="text-gray-500 text-sm">No data available</p>
              </div>
            )}
          </div>

          {/* Classroom Utilization */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Classroom Utilization</h3>
            {classroomUtilizationData.length > 0 ? (
              <AnalyticsPieChart
                data={classroomUtilizationData}
                title="Utilization by Room"
                height={200}
              />
            ) : (
              <div className="text-center py-8">
                <BarChart3 className="w-8 h-8 text-gray-400 mx-auto mb-2" />
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
                Generate New Timetable
              </button>
              <button className="w-full btn-secondary text-left">
                View All Timetables
              </button>
              <button className="w-full btn-secondary text-left">
                Export Reports
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
