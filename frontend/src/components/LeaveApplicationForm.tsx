import React, { useState } from 'react';
import { Calendar, FileText, Send, AlertCircle } from 'lucide-react';
import { LeaveApplicationForm as LeaveFormData } from '../types';

interface LeaveApplicationFormProps {
  onSubmit: (data: LeaveFormData) => void;
  loading?: boolean;
  error?: string;
}

const LeaveApplicationForm: React.FC<LeaveApplicationFormProps> = ({
  onSubmit,
  loading = false,
  error
}) => {
  const [formData, setFormData] = useState<LeaveFormData>({
    start_date: '',
    end_date: '',
    reason: ''
  });

  const [errors, setErrors] = useState<Partial<LeaveFormData>>({});

  const validateForm = (): boolean => {
    const newErrors: Partial<LeaveFormData> = {};

    if (!formData.start_date) {
      newErrors.start_date = 'Start date is required';
    }

    if (!formData.end_date) {
      newErrors.end_date = 'End date is required';
    }

    if (formData.start_date && formData.end_date) {
      const startDate = new Date(formData.start_date);
      const endDate = new Date(formData.end_date);
      
      if (endDate < startDate) {
        newErrors.end_date = 'End date must be after start date';
      }
      
      if (startDate < new Date()) {
        newErrors.start_date = 'Start date cannot be in the past';
      }
    }

    if (!formData.reason.trim()) {
      newErrors.reason = 'Reason is required';
    } else if (formData.reason.trim().length < 10) {
      newErrors.reason = 'Reason must be at least 10 characters long';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (validateForm()) {
      onSubmit(formData);
    }
  };

  const handleInputChange = (field: keyof LeaveFormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  const getMinDate = () => {
    const today = new Date();
    return today.toISOString().split('T')[0];
  };

  const getMaxDate = () => {
    const maxDate = new Date();
    maxDate.setFullYear(maxDate.getFullYear() + 1);
    return maxDate.toISOString().split('T')[0];
  };

  return (
    <div className="card">
      <div className="space-y-6">
        {/* Header */}
        <div className="text-center">
          <div className="flex items-center justify-center w-12 h-12 bg-blue-100 rounded-full mx-auto mb-4">
            <FileText className="w-6 h-6 text-linkedin-blue" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900">Apply for Leave</h2>
          <p className="text-gray-600 mt-2">
            Submit your leave application for approval
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center">
              <AlertCircle className="w-5 h-5 text-red-600 mr-2" />
              <span className="text-red-800 text-sm">{error}</span>
            </div>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Date Range */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Start Date */}
            <div>
              <label htmlFor="start_date" className="block text-sm font-medium text-gray-700 mb-2">
                Start Date
              </label>
              <div className="relative">
                <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="date"
                  id="start_date"
                  value={formData.start_date}
                  onChange={(e) => handleInputChange('start_date', e.target.value)}
                  min={getMinDate()}
                  max={getMaxDate()}
                  className={`input-field pl-10 ${errors.start_date ? 'border-red-300 focus:ring-red-500' : ''}`}
                  disabled={loading}
                />
              </div>
              {errors.start_date && (
                <p className="mt-1 text-sm text-red-600">{errors.start_date}</p>
              )}
            </div>

            {/* End Date */}
            <div>
              <label htmlFor="end_date" className="block text-sm font-medium text-gray-700 mb-2">
                End Date
              </label>
              <div className="relative">
                <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="date"
                  id="end_date"
                  value={formData.end_date}
                  onChange={(e) => handleInputChange('end_date', e.target.value)}
                  min={formData.start_date || getMinDate()}
                  max={getMaxDate()}
                  className={`input-field pl-10 ${errors.end_date ? 'border-red-300 focus:ring-red-500' : ''}`}
                  disabled={loading}
                />
              </div>
              {errors.end_date && (
                <p className="mt-1 text-sm text-red-600">{errors.end_date}</p>
              )}
            </div>
          </div>

          {/* Reason */}
          <div>
            <label htmlFor="reason" className="block text-sm font-medium text-gray-700 mb-2">
              Reason for Leave
            </label>
            <textarea
              id="reason"
              value={formData.reason}
              onChange={(e) => handleInputChange('reason', e.target.value)}
              rows={4}
              placeholder="Please provide a detailed reason for your leave application..."
              className={`input-field resize-none ${errors.reason ? 'border-red-300 focus:ring-red-500' : ''}`}
              disabled={loading}
            />
            {errors.reason && (
              <p className="mt-1 text-sm text-red-600">{errors.reason}</p>
            )}
            <p className="mt-1 text-sm text-gray-500">
              {formData.reason.length}/500 characters
            </p>
          </div>

          {/* Duration Info */}
          {formData.start_date && formData.end_date && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-center">
                <Calendar className="w-5 h-5 text-blue-600 mr-2" />
                <span className="text-blue-800 text-sm">
                  Leave duration: {Math.ceil(
                    (new Date(formData.end_date).getTime() - new Date(formData.start_date).getTime()) / (1000 * 60 * 60 * 24)
                  ) + 1} day(s)
                </span>
              </div>
            </div>
          )}

          {/* Submit Button */}
          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={() => setFormData({ start_date: '', end_date: '', reason: '' })}
              className="btn-secondary"
              disabled={loading}
            >
              Clear
            </button>
            <button
              type="submit"
              className="btn-primary flex items-center space-x-2"
              disabled={loading}
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Submitting...</span>
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  <span>Submit Application</span>
                </>
              )}
            </button>
          </div>
        </form>

        {/* Guidelines */}
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <h4 className="font-medium text-gray-900 mb-2">Application Guidelines</h4>
          <ul className="text-sm text-gray-600 space-y-1">
            <li>• Submit applications at least 24 hours in advance</li>
            <li>• Provide detailed reasons for your leave request</li>
            <li>• Ensure your substitute teacher is available</li>
            <li>• Check with your department head for approval</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default LeaveApplicationForm;
