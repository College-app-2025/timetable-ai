"""
API integration module for the SIH Timetable Optimization System.
Provides FastAPI routes and schemas for ML functionality.
"""

from .routes import router as ml_router
from .schemas import (
    TimetableRequest,
    TimetableResponse,
    OptimizationMetricsResponse,
    StudentTimetableResponse,
    FacultyTimetableResponse,
    RoomTimetableResponse
)

__all__ = [
    'ml_router',
    'TimetableRequest',
    'TimetableResponse', 
    'OptimizationMetricsResponse',
    'StudentTimetableResponse',
    'FacultyTimetableResponse',
    'RoomTimetableResponse'
]

