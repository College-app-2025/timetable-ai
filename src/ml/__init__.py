"""
Main ML module for the SIH Timetable Optimization System.
Provides the public API for timetable optimization.
"""

from .core.optimizer import TimetableOptimizer
from .data.models import OptimizationConfig
from .api.routes import router as ml_router

# Public API
__all__ = [
    'TimetableOptimizer',
    'OptimizationConfig',
    'ml_router'
]

# Version
__version__ = "1.0.0"