"""
Comprehensive domain models for the SIH Timetable Optimization System.
Defines all data structures used by the constraint solver and optimization engine.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Set, Tuple
from enum import Enum
import json
from datetime import datetime, time


class CourseType(Enum):
    """Course type enumeration."""
    THEORY = "theory"
    LAB = "lab"
    PROJECT = "project"
    ELECTIVE = "elective"
    INTERDISCIPLINARY = "interdisciplinary"


class RoomType(Enum):
    """Room type enumeration."""
    LECTURE = "lecture"
    LAB = "lab"
    SEMINAR = "seminar"
    AUDITORIUM = "auditorium"


class DifficultyLevel(Enum):
    """Course difficulty level."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


@dataclass
class TimeSlot:
    """Represents a time slot in the timetable."""
    id: int
    day: int  # 1-6 (Monday-Saturday)
    period: int  # 1-N periods per day
    start_time: time
    end_time: time
    is_break: bool = False
    is_lunch: bool = False
    
    def __str__(self) -> str:
        return f"Day {self.day}, Period {self.period} ({self.start_time}-{self.end_time})"
    
    def overlaps_with(self, other: TimeSlot) -> bool:
        """Check if this time slot overlaps with another."""
        if self.day != other.day:
            return False
        return not (self.end_time <= other.start_time or other.end_time <= self.start_time)


@dataclass
class Room:
    """Represents a classroom or laboratory."""
    id: str
    name: str
    room_type: RoomType
    capacity: int
    building: str
    floor: int
    department: Optional[str] = None
    available_slots: List[int] = field(default_factory=list)
    equipment: List[str] = field(default_factory=list)
    is_accessible: bool = True
    
    def can_accommodate(self, student_count: int) -> bool:
        """Check if room can accommodate given number of students."""
        return student_count <= self.capacity
    
    def is_suitable_for_course(self, course: Course) -> bool:
        """Check if room is suitable for a specific course type."""
        if course.course_type == CourseType.LAB and self.room_type != RoomType.LAB:
            return False
        if course.course_type == CourseType.THEORY and self.room_type == RoomType.LAB:
            return False
        return True


@dataclass
class Course:
    """Represents a course/subject."""
    id: str
    name: str
    course_code: str
    course_type: CourseType
    department: str
    semester: int
    credits: int
    hours_per_week: int
    max_sections: int = 2
    max_students_per_section: int = 60
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    prerequisites: List[str] = field(default_factory=list)
    allowed_slots: List[int] = field(default_factory=list)
    preferred_rooms: List[str] = field(default_factory=list)
    is_elective: bool = False
    elective_capacity: int = 0
    is_nep_compliant: bool = True
    
    def get_weekly_slots_needed(self) -> int:
        """Calculate number of time slots needed per week."""
        return self.hours_per_week


@dataclass
class Faculty:
    """Represents a faculty member."""
    id: str
    name: str
    email: str
    department: str
    designation: str
    subjects: List[str] = field(default_factory=list)  # Course IDs they can teach
    availability: Dict[int, List[int]] = field(default_factory=dict)  # day -> list of period IDs
    max_hours_per_day: int = 6
    max_hours_per_week: int = 30
    preferred_slots: List[int] = field(default_factory=list)
    workload_balance_weight: float = 1.0
    is_available: bool = True
    
    def can_teach_course(self, course_id: str) -> bool:
        """Check if faculty can teach a specific course."""
        return course_id in self.subjects
    
    def is_available_at_slot(self, slot_id: int) -> bool:
        """Check if faculty is available at a specific time slot."""
        if not self.is_available:
            return False
        
        # Check if slot is in their availability
        for day_slots in self.availability.values():
            if slot_id in day_slots:
                return True
        return False


@dataclass
class StudentPreference:
    """Represents a student's elective preference."""
    student_id: str
    course_id: str
    priority: int  # 1-5, where 1 is highest priority
    preference_score: float = 0.0  # Calculated based on priority
    
    def __post_init__(self):
        """Calculate preference score based on priority."""
        self.preference_score = max(0, 6 - self.priority) / 5.0  # 1.0 for priority 1, 0.2 for priority 5


@dataclass
class Student:
    """Represents a student."""
    id: str
    student_id: str
    name: str
    email: str
    department: str
    semester: int
    section: str
    preferences: List[StudentPreference] = field(default_factory=list)
    assigned_courses: List[str] = field(default_factory=list)
    satisfaction_score: float = 0.0
    max_courses: int = 8  # Core + electives
    is_active: bool = True
    
    def add_preference(self, course_id: str, priority: int):
        """Add an elective preference."""
        preference = StudentPreference(self.id, course_id, priority)
        self.preferences.append(preference)
        self.preferences.sort(key=lambda x: x.priority)
    
    def get_preference_for_course(self, course_id: str) -> Optional[StudentPreference]:
        """Get preference for a specific course."""
        for pref in self.preferences:
            if pref.course_id == course_id:
                return pref
        return None
    
    def calculate_satisfaction(self) -> float:
        """Calculate student satisfaction based on assigned courses."""
        if not self.preferences:
            return 0.0
        
        total_score = 0.0
        assigned_count = 0
        
        for course_id in self.assigned_courses:
            pref = self.get_preference_for_course(course_id)
            if pref:
                total_score += pref.preference_score
                assigned_count += 1
        
        if assigned_count == 0:
            return 0.0
        
        return total_score / len(self.preferences)


@dataclass
class Department:
    """Represents a department."""
    id: str
    name: str
    code: str
    max_sections: int = 3
    sections: List[Section] = field(default_factory=list)
    core_courses: List[str] = field(default_factory=list)
    elective_courses: List[str] = field(default_factory=list)


@dataclass
class Section:
    """Represents a section within a department."""
    id: str
    name: str
    department_id: str
    semester: int
    student_ids: List[str] = field(default_factory=list)
    max_students: int = 60


@dataclass
class Assignment:
    """Represents a course assignment to a time slot and room."""
    id: str
    course_id: str
    faculty_id: str
    room_id: str
    time_slot_id: int
    section_id: str
    student_count: int
    is_elective: bool = False
    priority_score: float = 0.0
    
    def __str__(self) -> str:
        return f"{self.course_id} -> {self.room_id} @ {self.time_slot_id}"


@dataclass
class Schedule:
    """Represents a complete timetable schedule."""
    id: str
    institute_id: str
    semester: int
    assignments: List[Assignment] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    is_optimized: bool = False
    optimization_score: float = 0.0
    
    def add_assignment(self, assignment: Assignment):
        """Add an assignment to the schedule."""
        self.assignments.append(assignment)
    
    def get_assignments_for_course(self, course_id: str) -> List[Assignment]:
        """Get all assignments for a specific course."""
        return [a for a in self.assignments if a.course_id == course_id]
    
    def get_assignments_for_faculty(self, faculty_id: str) -> List[Assignment]:
        """Get all assignments for a specific faculty."""
        return [a for a in self.assignments if a.faculty_id == faculty_id]
    
    def get_assignments_for_room(self, room_id: str) -> List[Assignment]:
        """Get all assignments for a specific room."""
        return [a for a in self.assignments if a.room_id == room_id]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert schedule to dictionary."""
        return {
            "id": self.id,
            "institute_id": self.institute_id,
            "semester": self.semester,
            "assignments": [assignment.to_dict() for assignment in self.assignments],
            "created_at": self.created_at.isoformat(),
            "is_optimized": self.is_optimized,
            "optimization_score": self.optimization_score
        }


@dataclass
class OptimizationMetrics:
    """Represents optimization performance metrics."""
    total_assignments: int = 0
    student_satisfaction: float = 0.0
    faculty_workload_balance: float = 0.0
    room_utilization: float = 0.0
    elective_allocation_rate: float = 0.0
    constraint_violations: int = 0
    optimization_time: float = 0.0
    is_feasible: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            'total_assignments': self.total_assignments,
            'student_satisfaction': self.student_satisfaction,
            'faculty_workload_balance': self.faculty_workload_balance,
            'room_utilization': self.room_utilization,
            'elective_allocation_rate': self.elective_allocation_rate,
            'constraint_violations': self.constraint_violations,
            'optimization_time': self.optimization_time,
            'is_feasible': self.is_feasible
        }


@dataclass
class OptimizationConfig:
    """Configuration for optimization parameters."""
    # Time limits
    max_optimization_time: int = 300  # 5 minutes
    max_iterations: int = 1000
    
    # Weights for soft constraints
    student_satisfaction_weight: float = 1.0
    faculty_workload_weight: float = 0.8
    room_utilization_weight: float = 0.6
    elective_preference_weight: float = 1.2
    
    # NEP 2020 compliance
    nep_compliance_weight: float = 1.0
    interdisciplinary_weight: float = 0.9
    
    # Fairness parameters
    carry_forward_weight: float = 0.7
    section_balance_weight: float = 0.5
    
    # Elective allocation
    max_electives_per_student: int = 5
    min_electives_per_student: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            'max_optimization_time': self.max_optimization_time,
            'max_iterations': self.max_iterations,
            'student_satisfaction_weight': self.student_satisfaction_weight,
            'faculty_workload_weight': self.faculty_workload_weight,
            'room_utilization_weight': self.room_utilization_weight,
            'elective_preference_weight': self.elective_preference_weight,
            'nep_compliance_weight': self.nep_compliance_weight,
            'interdisciplinary_weight': self.interdisciplinary_weight,
            'carry_forward_weight': self.carry_forward_weight,
            'section_balance_weight': self.section_balance_weight,
            'max_electives_per_student': self.max_electives_per_student,
            'min_electives_per_student': self.min_electives_per_student
        }
