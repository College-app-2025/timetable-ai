import React, { useState } from 'react';
import { CheckCircle, XCircle, Clock, User, BookOpen, Calendar, MapPin } from 'lucide-react';
import { Timetable } from '../types';

interface ApprovalCardProps {
  timetable: Timetable;
  onApprove: (timetableId: string) => void;
  onReject: (timetableId: string, reason: string) => void;
  loading?: boolean;
}

const ApprovalCard: React.FC<ApprovalCardProps> = ({
  timetable,
  onApprove,
  onReject,
  loading = false
}) => {
  const [showRejectForm, setShowRejectForm] = useState(false);
  const [rejectReason, setRejectReason] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleApprove = async () => {
    if (loading || isSubmitting) return;
    setIsSubmitting(true);
    try {
      await onApprove(timetable.id);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReject = async () => {
    if (loading || isSubmitting || !rejectReason.trim()) return;
    setIsSubmitting(true);
    try {
      await onReject(timetable.id, rejectReason);
      setShowRejectForm(false);
      setRejectReason('');
    } finally {
      setIsSubmitting(false);
    }
  };

  const getOptimizationScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getOptimizationScoreBg = (score: number) => {
    if (score >= 80) return 'bg-green-100';
    if (score >= 60) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  return (
    <div className="card">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center space-x-3 mb-2">
              <div className="flex items-center space-x-2">
                <Clock className="w-5 h-5 text-gray-500" />
                <span className="text-sm text-gray-600">
                  Generated {new Date(timetable.created_at).toLocaleDateString()}
                </span>
              </div>
              <div className={`px-2 py-1 rounded-full text-xs font-medium ${getOptimizationScoreBg(timetable.optimization_score)} ${getOptimizationScoreColor(timetable.optimization_score)}`}>
                Score: {timetable.optimization_score}%
              </div>
            </div>
            <h3 className="text-xl font-semibold text-gray-900">
              Timetable for Semester {timetable.semester}
            </h3>
            <p className="text-gray-600 mt-1">
              Institute ID: {timetable.institute_id}
            </p>
          </div>
        </div>

        {/* Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-blue-50 rounded-lg p-4">
            <div className="flex items-center">
              <BookOpen className="w-8 h-8 text-blue-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-blue-900">Total Classes</p>
                <p className="text-2xl font-bold text-blue-600">{timetable.schedules.length}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-green-50 rounded-lg p-4">
            <div className="flex items-center">
              <User className="w-8 h-8 text-green-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-green-900">Unique Teachers</p>
                <p className="text-2xl font-bold text-green-600">
                  {new Set(timetable.schedules.map(s => s.teacher_name)).size}
                </p>
              </div>
            </div>
          </div>
          
          <div className="bg-purple-50 rounded-lg p-4">
            <div className="flex items-center">
              <MapPin className="w-8 h-8 text-purple-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-purple-900">Unique Rooms</p>
                <p className="text-2xl font-bold text-purple-600">
                  {new Set(timetable.schedules.map(s => s.room)).size}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Schedule Preview */}
        <div className="space-y-4">
          <h4 className="font-medium text-gray-900">Schedule Preview</h4>
          <div className="bg-gray-50 rounded-lg p-4 max-h-64 overflow-y-auto">
            <div className="space-y-2">
              {timetable.schedules.slice(0, 10).map((schedule, index) => (
                <div key={index} className="flex items-center justify-between text-sm">
                  <div className="flex items-center space-x-3">
                    <span className="font-medium text-gray-900">{schedule.course_name}</span>
                    <span className="text-gray-500">•</span>
                    <span className="text-gray-600">{schedule.teacher_name}</span>
                  </div>
                  <div className="flex items-center space-x-2 text-gray-500">
                    <Calendar className="w-4 h-4" />
                    <span>{schedule.time_slot.day}</span>
                    <span>{schedule.time_slot.start_time}-{schedule.time_slot.end_time}</span>
                    <MapPin className="w-4 h-4" />
                    <span>{schedule.room}</span>
                  </div>
                </div>
              ))}
              {timetable.schedules.length > 10 && (
                <div className="text-center text-gray-500 text-sm pt-2">
                  ... and {timetable.schedules.length - 10} more classes
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Optimization Details */}
        <div className="bg-gray-50 rounded-lg p-4">
          <h4 className="font-medium text-gray-900 mb-3">Optimization Details</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-600">Status:</span>
              <span className={`ml-2 font-medium ${timetable.is_optimized ? 'text-green-600' : 'text-yellow-600'}`}>
                {timetable.is_optimized ? 'Optimized' : 'Pending Optimization'}
              </span>
            </div>
            <div>
              <span className="text-gray-600">Score:</span>
              <span className={`ml-2 font-medium ${getOptimizationScoreColor(timetable.optimization_score)}`}>
                {timetable.optimization_score}%
              </span>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex space-x-3">
          <button
            onClick={handleApprove}
            disabled={loading || isSubmitting}
            className="flex-1 btn-primary bg-green-600 hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
          >
            {isSubmitting ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Processing...</span>
              </>
            ) : (
              <>
                <CheckCircle className="w-4 h-4" />
                <span>Approve Timetable</span>
              </>
            )}
          </button>
          
          <button
            onClick={() => setShowRejectForm(!showRejectForm)}
            disabled={loading || isSubmitting}
            className="btn-secondary border-red-300 text-red-600 hover:bg-red-50 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            <XCircle className="w-4 h-4" />
            <span>Reject</span>
          </button>
        </div>

        {/* Reject Form */}
        {showRejectForm && (
          <div className="border border-red-200 rounded-lg p-4 bg-red-50">
            <h4 className="font-medium text-red-900 mb-3">Reason for Rejection</h4>
            <textarea
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
              placeholder="Please provide a detailed reason for rejecting this timetable..."
              rows={3}
              className="w-full px-3 py-2 border border-red-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
              disabled={isSubmitting}
            />
            <div className="flex justify-end space-x-3 mt-3">
              <button
                onClick={() => {
                  setShowRejectForm(false);
                  setRejectReason('');
                }}
                className="btn-secondary"
                disabled={isSubmitting}
              >
                Cancel
              </button>
              <button
                onClick={handleReject}
                disabled={isSubmitting || !rejectReason.trim()}
                className="btn-primary bg-red-600 hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSubmitting ? 'Submitting...' : 'Submit Rejection'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

interface ApprovalGridProps {
  timetables: Timetable[];
  onApprove: (timetableId: string) => void;
  onReject: (timetableId: string, reason: string) => void;
  loading?: boolean;
}

const ApprovalGrid: React.FC<ApprovalGridProps> = ({
  timetables,
  onApprove,
  onReject,
  loading = false
}) => {
  if (loading) {
    return (
      <div className="space-y-6">
        {[...Array(3)].map((_, index) => (
          <div key={index} className="card animate-pulse">
            <div className="space-y-4">
              <div className="h-4 bg-gray-200 rounded w-3/4"></div>
              <div className="h-3 bg-gray-200 rounded w-1/2"></div>
              <div className="grid grid-cols-3 gap-4">
                <div className="h-20 bg-gray-200 rounded"></div>
                <div className="h-20 bg-gray-200 rounded"></div>
                <div className="h-20 bg-gray-200 rounded"></div>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (timetables.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-400 mb-4">
          <CheckCircle size={48} className="mx-auto" />
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">No pending approvals</h3>
        <p className="text-gray-600">All timetables have been reviewed and approved.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {timetables.map((timetable) => (
        <ApprovalCard
          key={timetable.id}
          timetable={timetable}
          onApprove={onApprove}
          onReject={onReject}
          loading={loading}
        />
      ))}
    </div>
  );
};

export { ApprovalCard, ApprovalGrid };
export default ApprovalCard;
