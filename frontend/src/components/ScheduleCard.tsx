import React from 'react';
import { Clock, MapPin, User, BookOpen } from 'lucide-react';
import { Schedule } from '../types';

interface ScheduleCardProps {
  schedule: Schedule;
  view: 'daily' | 'weekly';
  onClick?: () => void;
}

const ScheduleCard: React.FC<ScheduleCardProps> = ({ schedule, view, onClick }) => {
  const getTypeColor = (type: string) => {
    switch (type) {
      case 'theory':
        return 'bg-blue-100 text-blue-800';
      case 'lab':
        return 'bg-green-100 text-green-800';
      case 'project':
        return 'bg-purple-100 text-purple-800';
      case 'elective':
        return 'bg-orange-100 text-orange-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'theory':
        return <BookOpen size={16} />;
      case 'lab':
        return <BookOpen size={16} />;
      case 'project':
        return <BookOpen size={16} />;
      case 'elective':
        return <BookOpen size={16} />;
      default:
        return <BookOpen size={16} />;
    }
  };

  const formatTime = (time: string) => {
    return time.replace(':', ':'); // Keep as is for now
  };

  return (
    <div
      className={`card hover:shadow-lg transition-all duration-200 ${
        onClick ? 'cursor-pointer hover:scale-105' : ''
      }`}
      onClick={onClick}
    >
      <div className="space-y-3">
        {/* Header with course name and type */}
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3 className="font-semibold text-gray-900 text-lg leading-tight">
              {schedule.course_name}
            </h3>
            <div className="flex items-center mt-1">
              <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getTypeColor(schedule.type)}`}>
                {getTypeIcon(schedule.type)}
                <span className="ml-1 capitalize">{schedule.type}</span>
              </span>
            </div>
          </div>
        </div>

        {/* Time and location info */}
        <div className="space-y-2">
          <div className="flex items-center text-gray-600">
            <Clock size={16} className="mr-2" />
            <span className="text-sm">
              {formatTime(schedule.time_slot.start_time)} - {formatTime(schedule.time_slot.end_time)}
            </span>
          </div>
          
          <div className="flex items-center text-gray-600">
            <MapPin size={16} className="mr-2" />
            <span className="text-sm">{schedule.room}</span>
          </div>
          
          <div className="flex items-center text-gray-600">
            <User size={16} className="mr-2" />
            <span className="text-sm">{schedule.teacher_name}</span>
          </div>
        </div>

        {/* Day indicator for weekly view */}
        {view === 'weekly' && (
          <div className="pt-2 border-t border-gray-200">
            <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
              {schedule.time_slot.day}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

interface ScheduleGridProps {
  schedules: Schedule[];
  view: 'daily' | 'weekly';
  selectedDate?: Date;
  onScheduleClick?: (schedule: Schedule) => void;
}

const ScheduleGrid: React.FC<ScheduleGridProps> = ({
  schedules,
  view,
  selectedDate,
  onScheduleClick
}) => {
  if (view === 'daily') {
    // Group schedules by time slot for daily view
    const timeSlots = [
      '9:00-10:00', '10:00-11:00', '11:00-12:00', '12:00-13:00',
      '13:00-14:00', '14:00-15:00', '15:00-16:00', '16:00-17:00'
    ];

    return (
      <div className="space-y-4">
        <div className="text-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">
            {selectedDate?.toLocaleDateString('en-US', { 
              weekday: 'long', 
              year: 'numeric', 
              month: 'long', 
              day: 'numeric' 
            })}
          </h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {timeSlots.map((timeSlot) => {
            const scheduleForSlot = schedules.find(
              s => `${s.time_slot.start_time}-${s.time_slot.end_time}` === timeSlot
            );
            
            return (
              <div key={timeSlot} className="relative">
                <div className="text-sm font-medium text-gray-500 mb-2">
                  {timeSlot}
                </div>
                {scheduleForSlot ? (
                  <ScheduleCard
                    schedule={scheduleForSlot}
                    view="daily"
                    onClick={() => onScheduleClick?.(scheduleForSlot)}
                  />
                ) : (
                  <div className="card bg-gray-50 border-2 border-dashed border-gray-300">
                    <div className="text-center py-8">
                      <div className="text-gray-400 text-sm">No class scheduled</div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  // Weekly view - group by day
  const daysOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
  
  return (
    <div className="space-y-6">
      <div className="text-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Weekly Schedule</h2>
        <p className="text-gray-600 mt-2">Your classes for this week</p>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-4">
        {daysOfWeek.map((day) => {
          const daySchedules = schedules.filter(s => s.time_slot.day === day);
          
          return (
            <div key={day} className="space-y-3">
              <div className="text-center">
                <h3 className="font-semibold text-gray-900">{day}</h3>
                <div className="text-sm text-gray-500">
                  {daySchedules.length} class{daySchedules.length !== 1 ? 'es' : ''}
                </div>
              </div>
              
              <div className="space-y-3">
                {daySchedules.length > 0 ? (
                  daySchedules.map((schedule) => (
                    <ScheduleCard
                      key={schedule.id}
                      schedule={schedule}
                      view="weekly"
                      onClick={() => onScheduleClick?.(schedule)}
                    />
                  ))
                ) : (
                  <div className="card bg-gray-50 border-2 border-dashed border-gray-300">
                    <div className="text-center py-4">
                      <div className="text-gray-400 text-sm">No classes</div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export { ScheduleCard, ScheduleGrid };
export default ScheduleCard;
