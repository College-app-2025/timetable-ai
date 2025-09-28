"""
Data handling and preprocessing module for the SIH Timetable Optimization System.
Provides domain models, data loaders, validators, and transformers.
"""

from .models import (
    Student,
    Course,
    Faculty,
    Room,
    TimeSlot,
    Assignment,
    Schedule,
    OptimizationMetrics,
    StudentPreference,
    Department,
    Section,
    OptimizationConfig
)

from .loaders import (
    load_students_from_db,
    load_courses_from_db,
    load_faculty_from_db,
    load_rooms_from_db,
    load_time_slots_from_config,
    load_student_preferences_from_db,
    load_institute_data
)

from .validators import (
    validate_student_data,
    validate_course_data,
    validate_faculty_data,
    validate_room_data,
    validate_time_slot_data,
    validate_optimization_config
)

from .transformers import (
    preprocess_student_data,
    preprocess_course_data,
    preprocess_faculty_data,
    normalize_time_slots,
    create_department_sections
)

__all__ = [
    # Models
    'Student', 'Course', 'Faculty', 'Room', 'TimeSlot',
    'Assignment', 'Schedule', 'OptimizationMetrics',
    'StudentPreference', 'Department', 'Section', 'OptimizationConfig',
    
    # Loaders
    'load_students_from_db', 'load_courses_from_db', 'load_faculty_from_db',
    'load_rooms_from_db', 'load_time_slots_from_config',
    'load_student_preferences_from_db', 'load_institute_data',
    
    # Validators
    'validate_student_data', 'validate_course_data', 'validate_faculty_data',
    'validate_room_data', 'validate_time_slot_data', 'validate_optimization_config',
    
    # Transformers
    'preprocess_student_data', 'preprocess_course_data', 'preprocess_faculty_data',
    'normalize_time_slots', 'create_department_sections'
]

