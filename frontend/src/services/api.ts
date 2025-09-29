import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { 
  ApiResponse, 
  LoginForm, 
  User, 
  Timetable, 
  VoteProposal, 
  Vote, 
  LeaveApplication, 
  Analytics, 
  Notification,
  PaginatedResponse 
} from '../types';
import { API_ENDPOINTS, STORAGE_KEYS } from '../utils/constants';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor to handle errors
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
          localStorage.removeItem(STORAGE_KEYS.USER_DATA);
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Authentication
  async login(credentials: LoginForm): Promise<ApiResponse<{ user: User; token: string }>> {
    const response = await this.api.post(API_ENDPOINTS.login, credentials);
    return response.data;
  }

  async logout(): Promise<ApiResponse<null>> {
    const response = await this.api.post(API_ENDPOINTS.logout);
    return response.data;
  }

  async refreshToken(): Promise<ApiResponse<{ token: string }>> {
    const response = await this.api.post(API_ENDPOINTS.refresh);
    return response.data;
  }

  // Timetable
  async generateTimetable(instituteId: string, semester?: number): Promise<ApiResponse<Timetable>> {
    const response = await this.api.post(API_ENDPOINTS.generateTimetable, {
      institute_id: instituteId,
      semester,
      force_regenerate: false
    });
    return response.data;
  }

  async getTimetable(instituteId: string, semester?: number): Promise<ApiResponse<Timetable>> {
    const response = await this.api.get(API_ENDPOINTS.getTimetable, {
      params: { institute_id: instituteId, semester }
    });
    return response.data;
  }

  async getStudentTimetable(studentId: string): Promise<ApiResponse<Timetable>> {
    const response = await this.api.get(`${API_ENDPOINTS.getStudentTimetable}/${studentId}`);
    return response.data;
  }

  async getTeacherTimetable(teacherId: string): Promise<ApiResponse<Timetable>> {
    const response = await this.api.get(`${API_ENDPOINTS.getTeacherTimetable}/${teacherId}`);
    return response.data;
  }

  // Dynamic Reallocation
  async reportUnavailability(data: {
    professor_id: string;
    assignment_id: string;
    unavailability_date: string;
    reason: string;
  }): Promise<ApiResponse<any>> {
    const response = await this.api.post(API_ENDPOINTS.reportUnavailability, data);
    return response.data;
  }

  async getReallocationStatus(assignmentId: string): Promise<ApiResponse<any>> {
    const response = await this.api.get(`${API_ENDPOINTS.getReallocationStatus}/${assignmentId}`);
    return response.data;
  }

  async getVotingProposals(studentId: string): Promise<ApiResponse<VoteProposal[]>> {
    const response = await this.api.get(API_ENDPOINTS.getVotingProposals, {
      params: { student_id: studentId }
    });
    return response.data;
  }

  async submitVote(proposalId: string, vote: boolean): Promise<ApiResponse<Vote>> {
    const response = await this.api.post(API_ENDPOINTS.submitVote, {
      proposal_id: proposalId,
      vote
    });
    return response.data;
  }

  // Leave Management
  async applyLeave(data: {
    start_date: string;
    end_date: string;
    reason: string;
  }): Promise<ApiResponse<LeaveApplication>> {
    const response = await this.api.post(API_ENDPOINTS.applyLeave, data);
    return response.data;
  }

  async getLeaveHistory(teacherId: string): Promise<ApiResponse<LeaveApplication[]>> {
    const response = await this.api.get(`${API_ENDPOINTS.getLeaveHistory}/${teacherId}`);
    return response.data;
  }

  async approveLeave(leaveId: string, approved: boolean): Promise<ApiResponse<LeaveApplication>> {
    const response = await this.api.post(`${API_ENDPOINTS.approveLeave}/${leaveId}`, {
      approved
    });
    return response.data;
  }

  // Analytics
  async getAnalytics(instituteId: string): Promise<ApiResponse<Analytics>> {
    const response = await this.api.get(API_ENDPOINTS.getAnalytics, {
      params: { institute_id: instituteId }
    });
    return response.data;
  }

  async getTeacherLoad(instituteId: string): Promise<ApiResponse<any[]>> {
    const response = await this.api.get(API_ENDPOINTS.getTeacherLoad, {
      params: { institute_id: instituteId }
    });
    return response.data;
  }

  async getClassroomUtilization(instituteId: string): Promise<ApiResponse<any[]>> {
    const response = await this.api.get(API_ENDPOINTS.getClassroomUtilization, {
      params: { institute_id: instituteId }
    });
    return response.data;
  }

  // Notifications
  async getNotifications(userId: string): Promise<ApiResponse<Notification[]>> {
    const response = await this.api.get(API_ENDPOINTS.getNotifications, {
      params: { user_id: userId }
    });
    return response.data;
  }

  async markNotificationRead(notificationId: string): Promise<ApiResponse<null>> {
    const response = await this.api.post(`${API_ENDPOINTS.markNotificationRead}/${notificationId}`);
    return response.data;
  }

  // Institute Management
  async uploadData(file: File, dataType: 'students' | 'teachers' | 'classrooms'): Promise<ApiResponse<any>> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('data_type', dataType);

    const response = await this.api.post(API_ENDPOINTS.uploadData, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async getInstituteData(instituteId: string): Promise<ApiResponse<any>> {
    const response = await this.api.get(`${API_ENDPOINTS.getInstituteData}/${instituteId}`);
    return response.data;
  }

  async updateInstituteData(instituteId: string, data: any): Promise<ApiResponse<any>> {
    const response = await this.api.put(`${API_ENDPOINTS.updateInstituteData}/${instituteId}`, data);
    return response.data;
  }

  // Utility methods
  setAuthToken(token: string): void {
    localStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, token);
  }

  removeAuthToken(): void {
    localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
    localStorage.removeItem(STORAGE_KEYS.USER_DATA);
  }

  getAuthToken(): string | null {
    return localStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);
  }
}

// Create and export a singleton instance
export const apiService = new ApiService();
export default apiService;
