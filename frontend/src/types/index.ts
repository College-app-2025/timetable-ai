// User Types
export interface User {
  id: string;
  email: string;
  name: string;
  role: 'student' | 'teacher' | 'admin';
  institute_id: string;
  avatar?: string;
}

// Student Types
export interface Student extends User {
  student_id: string;
  department: string;
  semester: number;
  section: string;
}

// Teacher Types
export interface Teacher extends User {
  teacher_id: string;
  department: string;
  subjects: string[];
  qualifications: string;
}

// Admin Types
export interface Admin extends User {
  admin_id: string;
  permissions: string[];
}

// Schedule Types
export interface TimeSlot {
  id: string;
  day: string;
  start_time: string;
  end_time: string;
}

export interface Schedule {
  id: string;
  course_name: string;
  teacher_name: string;
  room: string;
  time_slot: TimeSlot;
  type: 'theory' | 'lab' | 'project';
}

export interface Timetable {
  id: string;
  institute_id: string;
  semester: number;
  schedules: Schedule[];
  is_optimized: boolean;
  optimization_score: number;
  created_at: string;
}

// Voting Types
export interface VoteProposal {
  id: string;
  title: string;
  description: string;
  substitute_teacher: string;
  original_teacher: string;
  class_details: string;
  deadline: string;
  status: 'active' | 'completed' | 'expired';
  votes: {
    yes: number;
    no: number;
    total: number;
  };
}

export interface Vote {
  id: string;
  proposal_id: string;
  student_id: string;
  vote: boolean;
  created_at: string;
}

// Leave Types
export interface LeaveApplication {
  id: string;
  teacher_id: string;
  start_date: string;
  end_date: string;
  reason: string;
  status: 'pending' | 'approved' | 'rejected';
  created_at: string;
  approved_by?: string;
  approved_at?: string;
}

// Analytics Types
export interface Analytics {
  teacher_load: {
    teacher_id: string;
    teacher_name: string;
    total_hours: number;
    subjects: string[];
  }[];
  classroom_utilization: {
    room_id: string;
    room_name: string;
    utilization_percentage: number;
    total_hours: number;
  }[];
  conflict_resolution: {
    date: string;
    conflicts_resolved: number;
    method_used: string;
  }[];
}

// Notification Types
export interface Notification {
  id: string;
  user_id: string;
  title: string;
  message: string;
  type: 'info' | 'warning' | 'success' | 'error';
  is_read: boolean;
  created_at: string;
  action_url?: string;
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

// Form Types
export interface LoginForm {
  email: string;
  password: string;
  role: 'student' | 'teacher' | 'admin';
}

export interface LeaveApplicationForm {
  start_date: string;
  end_date: string;
  reason: string;
}

// Chart Data Types
export interface ChartData {
  name: string;
  value: number;
  color?: string;
}

export interface TimeSeriesData {
  date: string;
  value: number;
}
