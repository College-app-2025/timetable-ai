"""
Pydantic schemas for the SIH Timetable Optimization System API.
Defines request and response models for ML endpoints.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class TimetableRequest(BaseModel):
    """Request schema for timetable generation."""
    institute_id: str = Field(..., description="Institute ID for timetable generation")
    semester: Optional[int] = Field(None, description="Specific semester (if not provided, uses current)")
    config: Optional[Dict[str, Any]] = Field(None, description="Custom optimization configuration")
    force_regenerate: bool = Field(False, description="Force regeneration even if existing timetable exists")


class AssignmentResponse(BaseModel):
    """Response schema for a single assignment."""
    id: str
    course_id: str
    faculty_id: str
    room_id: str
    time_slot_id: int
    section_id: str
    student_count: int
    is_elective: bool
    priority_score: float


class TimetableResponse(BaseModel):
    """Response schema for timetable generation."""
    success: bool
    message: str
    schedule_id: str
    institute_id: str
    semester: int
    total_assignments: int
    optimization_time: float
    student_satisfaction: float
    faculty_workload_balance: float
    room_utilization: float
    elective_allocation_rate: float
    constraint_violations: int
    is_feasible: bool
    assignments: List[AssignmentResponse]
    created_at: datetime


class OptimizationMetricsResponse(BaseModel):
    """Response schema for optimization metrics."""
    total_assignments: int
    student_satisfaction: float
    faculty_workload_balance: float
    room_utilization: float
    elective_allocation_rate: float
    constraint_violations: int
    optimization_time: float
    is_feasible: bool


class StudentTimetableResponse(BaseModel):
    """Response schema for student-specific timetable."""
    student_id: str
    student_name: str
    department: str
    semester: int
    assignments: List[AssignmentResponse]
    satisfaction_score: float


class FacultyTimetableResponse(BaseModel):
    """Response schema for faculty-specific timetable."""
    faculty_id: str
    faculty_name: str
    department: str
    assignments: List[AssignmentResponse]
    total_hours: int
    workload_balance_score: float


class RoomTimetableResponse(BaseModel):
    """Response schema for room-specific timetable."""
    room_id: str
    room_name: str
    room_type: str
    capacity: int
    building: str
    floor: int
    assignments: List[AssignmentResponse]
    utilization_rate: float


class DepartmentTimetableResponse(BaseModel):
    """Response schema for department-specific timetable."""
    department: str
    assignments: List[AssignmentResponse]
    student_count: int
    course_count: int
    satisfaction_score: float


class TimetableSummaryResponse(BaseModel):
    """Response schema for timetable summary."""
    total_assignments: int
    elective_assignments: int
    theory_assignments: int
    unique_courses: int
    unique_faculty: int
    unique_rooms: int
    time_slots_used: int
    optimization_score: float
    is_optimized: bool
    created_at: datetime


class ErrorResponse(BaseModel):
    """Response schema for errors."""
    success: bool = False
    error: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class OptimizationConfigRequest(BaseModel):
    """Request schema for optimization configuration."""
    max_optimization_time: Optional[int] = Field(300, description="Maximum optimization time in seconds")
    max_iterations: Optional[int] = Field(1000, description="Maximum solver iterations")
    student_satisfaction_weight: Optional[float] = Field(1.0, description="Weight for student satisfaction")
    faculty_workload_weight: Optional[float] = Field(0.8, description="Weight for faculty workload balance")
    room_utilization_weight: Optional[float] = Field(0.6, description="Weight for room utilization")
    elective_preference_weight: Optional[float] = Field(1.2, description="Weight for elective preferences")
    nep_compliance_weight: Optional[float] = Field(1.0, description="Weight for NEP 2020 compliance")
    interdisciplinary_weight: Optional[float] = Field(0.9, description="Weight for interdisciplinary courses")
    carry_forward_weight: Optional[float] = Field(0.7, description="Weight for carry-forward fairness")
    section_balance_weight: Optional[float] = Field(0.5, description="Weight for section balance")
    max_electives_per_student: Optional[int] = Field(5, description="Maximum electives per student")
    min_electives_per_student: Optional[int] = Field(1, description="Minimum electives per student")


class StudentPreferenceRequest(BaseModel):
    """Request schema for student preferences."""
    student_id: str
    preferences: List[Dict[str, Any]] = Field(..., description="List of course preferences with priority")


class BatchTimetableRequest(BaseModel):
    """Request schema for batch timetable generation."""
    institute_ids: List[str] = Field(..., description="List of institute IDs")
    semester: Optional[int] = Field(None, description="Specific semester")
    config: Optional[Dict[str, Any]] = Field(None, description="Custom optimization configuration")


class BatchTimetableResponse(BaseModel):
    """Response schema for batch timetable generation."""
    success: bool
    results: Dict[str, TimetableResponse] = Field(..., description="Results by institute ID")
    total_processed: int
    successful: int
    failed: int
    processing_time: float


class TimetableComparisonRequest(BaseModel):
    """Request schema for timetable comparison."""
    schedule_id_1: str
    schedule_id_2: str


class TimetableComparisonResponse(BaseModel):
    """Response schema for timetable comparison."""
    schedule_1_metrics: OptimizationMetricsResponse
    schedule_2_metrics: OptimizationMetricsResponse
    comparison: Dict[str, Any]
    recommendation: str


class ExportRequest(BaseModel):
    """Request schema for timetable export."""
    schedule_id: str
    format: str = Field("json", description="Export format: json, csv, excel")
    include_details: bool = Field(True, description="Include detailed assignment information")


class ExportResponse(BaseModel):
    """Response schema for timetable export."""
    success: bool
    file_url: Optional[str] = None
    file_content: Optional[str] = None
    format: str
    size: Optional[int] = None


class MultiScheduleRequest(BaseModel):
    """Request model for multiple schedule generation."""
    institute_id: str
    semester: int
    students: List[Dict[str, Any]]
    courses: List[Dict[str, Any]]
    faculty: List[Dict[str, Any]]
    rooms: List[Dict[str, Any]]
    time_slots: List[Dict[str, Any]]
    student_preferences: List[Dict[str, Any]] = []
    num_options: int = 3


class ScheduleSelectionRequest(BaseModel):
    """Request model for schedule selection."""
    institute_id: str
    selected_schedule: Dict[str, Any]
    admin_notes: Optional[str] = None


class ScheduleOption(BaseModel):
    """Model for a schedule option."""
    option_id: int
    name: str
    description: str
    metrics: Dict[str, Any]
    assignments_count: int
    is_feasible: bool
    quality_score: Optional[float] = None


class MultiScheduleResponse(BaseModel):
    """Response model for multiple schedule generation."""
    success: bool
    message: str
    institute_id: str
    semester: int
    total_options: int
    schedules: List[ScheduleOption]
