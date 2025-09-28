"""
Default configuration settings for the SIH Timetable Optimization System.
"""

from typing import Dict, Any
from ..data.models import OptimizationConfig

# Default optimization configuration
DEFAULT_OPTIMIZATION_CONFIG = OptimizationConfig(
    max_optimization_time=300,  # 5 minutes
    max_iterations=1000,
    student_satisfaction_weight=1.0,
    faculty_workload_weight=0.8,
    room_utilization_weight=0.6,
    elective_preference_weight=1.2,
    nep_compliance_weight=1.0,
    interdisciplinary_weight=0.9,
    carry_forward_weight=0.7,
    section_balance_weight=0.5,
    max_electives_per_student=5,
    min_electives_per_student=1
)

# Time slot configuration
DEFAULT_TIME_SLOTS = {
    "start_hour": 9,
    "end_hour": 18,
    "periods_per_day": 8,
    "period_duration_minutes": 50,
    "break_duration_minutes": 10,
    "lunch_break_period": 4,
    "working_days": [1, 2, 3, 4, 5, 6]  # Monday to Saturday
}

# Room configuration
DEFAULT_ROOM_TYPES = {
    "lecture": {"min_capacity": 30, "max_capacity": 200},
    "lab": {"min_capacity": 20, "max_capacity": 60},
    "seminar": {"min_capacity": 10, "max_capacity": 30},
    "auditorium": {"min_capacity": 100, "max_capacity": 500}
}

# Course configuration
DEFAULT_COURSE_TYPES = {
    "theory": {"hours_per_week": 3, "max_sections": 3},
    "lab": {"hours_per_week": 2, "max_sections": 2},
    "project": {"hours_per_week": 4, "max_sections": 1},
    "elective": {"hours_per_week": 3, "max_sections": 2}
}

# Faculty configuration
DEFAULT_FACULTY_LIMITS = {
    "max_hours_per_day": 6,
    "max_hours_per_week": 30,
    "min_hours_per_week": 10,
    "max_courses_per_faculty": 4
}

# Student configuration
DEFAULT_STUDENT_LIMITS = {
    "max_courses_per_student": 8,
    "min_courses_per_student": 4,
    "max_electives_per_student": 5,
    "min_electives_per_student": 1
}

# NEP 2020 compliance settings
NEP2020_SETTINGS = {
    "multidisciplinary_weight": 0.9,
    "flexibility_weight": 0.8,
    "skill_development_weight": 0.7,
    "interdisciplinary_course_ratio": 0.3,
    "elective_course_ratio": 0.4
}

# Optimization algorithm settings
OPTIMIZATION_SETTINGS = {
    "solver_type": "CP-SAT",
    "time_limit_seconds": 300,
    "max_iterations": 1000,
    "solution_limit": 10,
    "log_search_progress": True,
    "enable_parallel_processing": True
}

# Logging configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "timetable_optimization.log",
    "max_file_size": 10485760,  # 10MB
    "backup_count": 5
}

# Database configuration
DATABASE_CONFIG = {
    "connection_pool_size": 10,
    "query_timeout": 30,
    "enable_query_logging": False
}

# Cache configuration
CACHE_CONFIG = {
    "enable_caching": True,
    "cache_ttl_seconds": 3600,  # 1 hour
    "max_cache_size": 1000
}

# Export configuration
EXPORT_CONFIG = {
    "supported_formats": ["json", "csv", "excel", "pdf"],
    "max_file_size": 52428800,  # 50MB
    "temp_file_cleanup_hours": 24
}

# API configuration
API_CONFIG = {
    "max_request_size": 10485760,  # 10MB
    "request_timeout": 300,  # 5 minutes
    "rate_limit_per_minute": 60,
    "enable_cors": True,
    "cors_origins": ["*"]
}

def get_default_config() -> OptimizationConfig:
    """Get default optimization configuration."""
    return DEFAULT_OPTIMIZATION_CONFIG

def get_config_dict() -> Dict[str, Any]:
    """Get all configuration as dictionary."""
    return {
        "optimization": DEFAULT_OPTIMIZATION_CONFIG.to_dict(),
        "time_slots": DEFAULT_TIME_SLOTS,
        "room_types": DEFAULT_ROOM_TYPES,
        "course_types": DEFAULT_COURSE_TYPES,
        "faculty_limits": DEFAULT_FACULTY_LIMITS,
        "student_limits": DEFAULT_STUDENT_LIMITS,
        "nep2020": NEP2020_SETTINGS,
        "optimization_settings": OPTIMIZATION_SETTINGS,
        "logging": LOGGING_CONFIG,
        "database": DATABASE_CONFIG,
        "cache": CACHE_CONFIG,
        "export": EXPORT_CONFIG,
        "api": API_CONFIG
    }

