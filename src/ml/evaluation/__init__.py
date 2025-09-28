"""
Evaluation and metrics module for the SIH Timetable Optimization System.
Provides satisfaction scoring, fairness evaluation, and performance metrics.
"""

from .metrics import MetricsCalculator
from .fairness import FairnessCalculator
from .reporters import ReportGenerator

__all__ = [
    'MetricsCalculator',
    'FairnessCalculator', 
    'ReportGenerator'
]

