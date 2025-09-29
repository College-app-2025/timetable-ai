import React from 'react';
import { User, GraduationCap, Building2 } from 'lucide-react';

interface RoleSelectionCardProps {
  role: 'student' | 'teacher' | 'admin';
  title: string;
  description: string;
  icon: React.ReactNode;
  onClick: () => void;
}

const RoleSelectionCard: React.FC<RoleSelectionCardProps> = ({
  role,
  title,
  description,
  icon,
  onClick
}) => {
  const getRoleColor = (role: string) => {
    switch (role) {
      case 'student':
        return 'border-blue-200 hover:border-linkedin-blue bg-blue-50 hover:bg-blue-100';
      case 'teacher':
        return 'border-green-200 hover:border-green-600 bg-green-50 hover:bg-green-100';
      case 'admin':
        return 'border-purple-200 hover:border-purple-600 bg-purple-50 hover:bg-purple-100';
      default:
        return 'border-gray-200 hover:border-linkedin-blue bg-gray-50 hover:bg-gray-100';
    }
  };

  const getIconColor = (role: string) => {
    switch (role) {
      case 'student':
        return 'text-linkedin-blue';
      case 'teacher':
        return 'text-green-600';
      case 'admin':
        return 'text-purple-600';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <div
      className={`card cursor-pointer transition-all duration-300 transform hover:scale-105 hover:shadow-lg ${getRoleColor(role)}`}
      onClick={onClick}
    >
      <div className="flex flex-col items-center text-center space-y-4">
        <div className={`p-4 rounded-full bg-white shadow-md ${getIconColor(role)}`}>
          {icon}
        </div>
        
        <div className="space-y-2">
          <h3 className="text-xl font-semibold text-gray-900">{title}</h3>
          <p className="text-gray-600 text-sm leading-relaxed">{description}</p>
        </div>
        
        <div className="w-full">
          <button className="btn-primary w-full">
            Continue as {title}
          </button>
        </div>
      </div>
    </div>
  );
};

interface RoleSelectionProps {
  onRoleSelect: (role: 'student' | 'teacher' | 'admin') => void;
}

const RoleSelection: React.FC<RoleSelectionProps> = ({ onRoleSelect }) => {
  const roles = [
    {
      role: 'student' as const,
      title: 'Student',
      description: 'View your timetable, vote on class changes, and track your academic schedule.',
      icon: <User size={32} />
    },
    {
      role: 'teacher' as const,
      title: 'Teacher',
      description: 'Manage your schedule, apply for leave, and view your teaching assignments.',
      icon: <GraduationCap size={32} />
    },
    {
      role: 'admin' as const,
      title: 'Admin',
      description: 'Generate timetables, manage institute data, and oversee the entire system.',
      icon: <Building2 size={32} />
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="max-w-6xl w-full">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            AI Timetable Management System
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Choose your role to access the intelligent timetable optimization platform
          </p>
        </div>

        {/* Role Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {roles.map((roleData) => (
            <RoleSelectionCard
              key={roleData.role}
              role={roleData.role}
              title={roleData.title}
              description={roleData.description}
              icon={roleData.icon}
              onClick={() => onRoleSelect(roleData.role)}
            />
          ))}
        </div>

        {/* Footer */}
        <div className="text-center mt-12">
          <p className="text-gray-500 text-sm">
            Powered by AI-driven constraint optimization • NEP 2020 Compliant
          </p>
        </div>
      </div>
    </div>
  );
};

export default RoleSelection;
