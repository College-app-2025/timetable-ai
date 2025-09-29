import React, { useState, useEffect } from 'react';
import { Calendar, Clock, TrendingUp, Bell, Vote, BookOpen } from 'lucide-react';
import { Student, Timetable, VoteProposal, Notification } from '../types';
import { ScheduleGrid } from '../components/ScheduleCard';
import { VoteGrid } from '../components/VoteCard';
import { AnalyticsBarChart, AnalyticsPieChart } from '../components/AnalyticsChart';
import { apiService } from '../services/api';

interface StudentDashboardProps {
  user: Student;
}

const StudentDashboard: React.FC<StudentDashboardProps> = ({ user }) => {
  const [timetable, setTimetable] = useState<Timetable | null>(null);
  const [voteProposals, setVoteProposals] = useState<VoteProposal[]>([]);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [view, setView] = useState<'daily' | 'weekly'>('weekly');
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [loading, setLoading] = useState(true);
  const [voting, setVoting] = useState<Record<string, boolean>>({});

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load timetable
      const timetableResponse = await apiService.getStudentTimetable(user.id);
      if (timetableResponse.success) {
        setTimetable(timetableResponse.data);
      }

      // Load vote proposals
      const votesResponse = await apiService.getVotingProposals(user.id);
      if (votesResponse.success) {
        setVoteProposals(votesResponse.data);
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

  const handleVote = async (proposalId: string, vote: boolean) => {
    try {
      const response = await apiService.submitVote(proposalId, vote);
      if (response.success) {
        // Update local state
        setVoting(prev => ({ ...prev, [proposalId]: vote }));
        
        // Reload vote proposals to get updated results
        const votesResponse = await apiService.getVotingProposals(user.id);
        if (votesResponse.success) {
          setVoteProposals(votesResponse.data);
        }
      }
    } catch (error) {
      console.error('Error submitting vote:', error);
    }
  };

  const getAnalyticsData = () => {
    if (!timetable) return { subjects: [], hours: [] };

    // Group by subject
    const subjectHours: Record<string, number> = {};
    timetable.schedules.forEach(schedule => {
      subjectHours[schedule.course_name] = (subjectHours[schedule.course_name] || 0) + 1;
    });

    const subjects = Object.keys(subjectHours).map(subject => ({
      name: subject,
      value: subjectHours[subject]
    }));

    const hours = Object.keys(subjectHours).map(subject => ({
      name: subject,
      hours: subjectHours[subject]
    }));

    return { subjects, hours };
  };

  const { subjects, hours } = getAnalyticsData();

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
      <div className="card bg-gradient-to-r from-linkedin-blue to-linkedin-dark text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold mb-2">
              Welcome back, {user.name}!
            </h1>
            <p className="text-blue-100">
              {user.department} • Semester {user.semester} • Section {user.section}
            </p>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold">{timetable?.schedules.length || 0}</div>
            <div className="text-blue-100">Classes this week</div>
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
              <p className="text-sm font-medium text-gray-600">Free Slots</p>
              <p className="text-2xl font-bold text-gray-900">
                {40 - (timetable?.schedules.length || 0)}
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-3 bg-purple-100 rounded-lg">
              <Vote className="w-6 h-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Active Votes</p>
              <p className="text-2xl font-bold text-gray-900">
                {voteProposals.filter(p => p.status === 'active').length}
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
        {/* Timetable Section */}
        <div className="lg:col-span-2 space-y-6">
          {/* View Toggle */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900">Your Schedule</h2>
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
                <p className="text-gray-600">Your timetable will appear here once it's generated.</p>
              </div>
            )}
          </div>

          {/* Voting Section */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900">Class Change Proposals</h2>
              <span className="text-sm text-gray-500">
                {voteProposals.filter(p => p.status === 'active').length} active
              </span>
            </div>

            <VoteGrid
              proposals={voteProposals}
              onVote={handleVote}
              userVotes={voting}
            />
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Analytics */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Subject Analysis</h3>
            {subjects.length > 0 ? (
              <AnalyticsPieChart
                data={subjects}
                title="Classes by Subject"
                height={200}
              />
            ) : (
              <div className="text-center py-8">
                <TrendingUp className="w-8 h-8 text-gray-400 mx-auto mb-2" />
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
                View Full Timetable
              </button>
              <button className="w-full btn-secondary text-left">
                Download Schedule
              </button>
              <button className="w-full btn-secondary text-left">
                Contact Support
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StudentDashboard;
