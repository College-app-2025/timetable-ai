// Theme Colors
export const COLORS = {
  linkedin: {
    blue: '#0077B5',
    dark: '#004182',
    light: '#E1F5FE',
  },
  gray: {
    50: '#F5F5F5',
    100: '#EEEEEE',
    200: '#E0E0E0',
    300: '#BDBDBD',
    400: '#9E9E9E',
    500: '#757575',
    600: '#616161',
    700: '#424242',
    800: '#333333',
    900: '#212121',
  },
  status: {
    approved: '#10B981',
    pending: '#F59E0B',
    rejected: '#EF4444',
    normal: '#3B82F6',
  }
};

// Typography
export const TYPOGRAPHY = {
  fontFamily: {
    primary: 'Inter, sans-serif',
    secondary: 'Roboto, sans-serif',
  },
  fontSize: {
    xs: '0.75rem',
    sm: '0.875rem',
    base: '1rem',
    lg: '1.125rem',
    xl: '1.25rem',
    '2xl': '1.5rem',
    '3xl': '1.875rem',
    '4xl': '2.25rem',
  },
  fontWeight: {
    light: 300,
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  }
};

// Spacing
export const SPACING = {
  xs: '0.25rem',
  sm: '0.5rem',
  md: '1rem',
  lg: '1.5rem',
  xl: '2rem',
  '2xl': '3rem',
  '3xl': '4rem',
};

// Breakpoints
export const BREAKPOINTS = {
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
};

// API Endpoints
export const API_ENDPOINTS = {
  // Authentication
  login: '/api/auth/login',
  logout: '/api/auth/logout',
  refresh: '/api/auth/refresh',
  
  // Timetable
  generateTimetable: '/api/ml/generate-timetable',
  getTimetable: '/api/timetable',
  getStudentTimetable: '/api/timetable/student',
  getTeacherTimetable: '/api/timetable/teacher',
  
  // Dynamic Reallocation
  reportUnavailability: '/api/dynamic-reallocation/report-unavailability',
  getReallocationStatus: '/api/dynamic-reallocation/status',
  getVotingProposals: '/api/dynamic-reallocation/voting-proposals',
  submitVote: '/api/dynamic-reallocation/vote',
  
  // Leave Management
  applyLeave: '/api/leave/apply',
  getLeaveHistory: '/api/leave/history',
  approveLeave: '/api/leave/approve',
  
  // Analytics
  getAnalytics: '/api/analytics',
  getTeacherLoad: '/api/analytics/teacher-load',
  getClassroomUtilization: '/api/analytics/classroom-utilization',
  
  // Notifications
  getNotifications: '/api/notifications',
  markNotificationRead: '/api/notifications/read',
  
  // Institute Management
  uploadData: '/api/institute/upload',
  getInstituteData: '/api/institute/data',
  updateInstituteData: '/api/institute/update',
};

// Days of the Week
export const DAYS_OF_WEEK = [
  'Monday',
  'Tuesday', 
  'Wednesday',
  'Thursday',
  'Friday',
  'Saturday',
  'Sunday'
];

// Time Slots
export const TIME_SLOTS = [
  '9:00-10:00',
  '10:00-11:00',
  '11:00-12:00',
  '12:00-13:00',
  '13:00-14:00',
  '14:00-15:00',
  '15:00-16:00',
  '16:00-17:00',
];

// Course Types
export const COURSE_TYPES = [
  'theory',
  'lab',
  'project',
  'elective',
  'interdisciplinary'
];

// User Roles
export const USER_ROLES = {
  STUDENT: 'student',
  TEACHER: 'teacher',
  ADMIN: 'admin',
} as const;

// Notification Types
export const NOTIFICATION_TYPES = {
  INFO: 'info',
  WARNING: 'warning',
  SUCCESS: 'success',
  ERROR: 'error',
} as const;

// Status Types
export const STATUS_TYPES = {
  APPROVED: 'approved',
  PENDING: 'pending',
  REJECTED: 'rejected',
  NORMAL: 'normal',
} as const;

// Chart Colors
export const CHART_COLORS = [
  '#0077B5', // LinkedIn Blue
  '#10B981', // Green
  '#F59E0B', // Yellow
  '#EF4444', // Red
  '#8B5CF6', // Purple
  '#06B6D4', // Cyan
  '#84CC16', // Lime
  '#F97316', // Orange
];

// Local Storage Keys
export const STORAGE_KEYS = {
  AUTH_TOKEN: 'auth_token',
  USER_DATA: 'user_data',
  THEME: 'theme',
  LANGUAGE: 'language',
};

// Validation Rules
export const VALIDATION = {
  EMAIL_REGEX: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  PASSWORD_MIN_LENGTH: 6,
  NAME_MIN_LENGTH: 2,
  PHONE_REGEX: /^\+?1?\d{9,15}$/,
};

// Default Values
export const DEFAULTS = {
  PAGE_SIZE: 10,
  DEBOUNCE_DELAY: 300,
  TOAST_DURATION: 5000,
  VOTING_DEADLINE_HOURS: 24,
};

// Error Messages
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network error. Please check your connection.',
  UNAUTHORIZED: 'You are not authorized to perform this action.',
  FORBIDDEN: 'Access denied.',
  NOT_FOUND: 'Resource not found.',
  VALIDATION_ERROR: 'Please check your input and try again.',
  SERVER_ERROR: 'Server error. Please try again later.',
  INVALID_CREDENTIALS: 'Invalid email or password.',
  SESSION_EXPIRED: 'Your session has expired. Please login again.',
};

// Success Messages
export const SUCCESS_MESSAGES = {
  LOGIN_SUCCESS: 'Login successful!',
  LOGOUT_SUCCESS: 'Logout successful!',
  VOTE_SUBMITTED: 'Your vote has been submitted successfully!',
  LEAVE_APPLIED: 'Leave application submitted successfully!',
  LEAVE_APPROVED: 'Leave application approved!',
  LEAVE_REJECTED: 'Leave application rejected.',
  TIMETABLE_GENERATED: 'Timetable generated successfully!',
  DATA_UPLOADED: 'Data uploaded successfully!',
  PROFILE_UPDATED: 'Profile updated successfully!',
};
