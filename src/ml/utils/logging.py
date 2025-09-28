"""
Enhanced logging utilities for the SIH Timetable Optimization System.
"""

import logging
import sys
from typing import Optional, Dict, Any
from datetime import datetime
import json

from src.utils.logger_config import get_logger

logger = get_logger("ml_logging")


class MLogger:
    """Enhanced logger for ML operations with structured logging."""
    
    def __init__(self, name: str = "ml_optimizer"):
        self.logger = get_logger(name)
        self.operation_id = None
        self.start_time = None
    
    def start_operation(self, operation_name: str, **kwargs) -> str:
        """Start a new operation with tracking."""
        self.operation_id = f"{operation_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.start_time = datetime.now()
        
        self.logger.info(f"Starting operation: {operation_name}", extra={
            'operation_id': self.operation_id,
            'operation_name': operation_name,
            'start_time': self.start_time.isoformat(),
            'metadata': kwargs
        })
        
        return self.operation_id
    
    def log_operation_step(self, step_name: str, status: str = "info", **kwargs):
        """Log a step within an operation."""
        if self.operation_id is None:
            self.logger.warning("Logging step without active operation")
            return
        
        log_data = {
            'operation_id': self.operation_id,
            'step_name': step_name,
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'metadata': kwargs
        }
        
        if status == "error":
            self.logger.error(f"Operation step failed: {step_name}", extra=log_data)
        elif status == "warning":
            self.logger.warning(f"Operation step warning: {step_name}", extra=log_data)
        else:
            self.logger.info(f"Operation step: {step_name}", extra=log_data)
    
    def end_operation(self, status: str = "success", **kwargs):
        """End the current operation."""
        if self.operation_id is None:
            self.logger.warning("Ending operation without active operation")
            return
        
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds() if self.start_time else 0
        
        self.logger.info(f"Operation completed: {self.operation_id}", extra={
            'operation_id': self.operation_id,
            'status': status,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': end_time.isoformat(),
            'duration_seconds': duration,
            'metadata': kwargs
        })
        
        self.operation_id = None
        self.start_time = None
    
    def log_optimization_metrics(self, metrics: Dict[str, Any]):
        """Log optimization metrics in structured format."""
        self.logger.info("Optimization metrics", extra={
            'operation_id': self.operation_id,
            'metrics': metrics,
            'timestamp': datetime.now().isoformat()
        })
    
    def log_constraint_violations(self, violations: list):
        """Log constraint violations."""
        if violations:
            self.logger.warning(f"Constraint violations detected: {len(violations)}", extra={
                'operation_id': self.operation_id,
                'violation_count': len(violations),
                'violations': violations,
                'timestamp': datetime.now().isoformat()
            })
        else:
            self.logger.info("No constraint violations detected", extra={
                'operation_id': self.operation_id,
                'timestamp': datetime.now().isoformat()
            })
    
    def log_data_quality(self, quality_report: Dict[str, Any]):
        """Log data quality report."""
        self.logger.info("Data quality report", extra={
            'operation_id': self.operation_id,
            'quality_report': quality_report,
            'timestamp': datetime.now().isoformat()
        })
    
    def log_performance(self, performance_data: Dict[str, Any]):
        """Log performance metrics."""
        self.logger.info("Performance metrics", extra={
            'operation_id': self.operation_id,
            'performance': performance_data,
            'timestamp': datetime.now().isoformat()
        })


class OptimizationLogger:
    """Specialized logger for optimization operations."""
    
    def __init__(self):
        self.logger = MLogger("optimization")
        self.iteration_count = 0
        self.best_score = float('-inf')
    
    def log_iteration(self, iteration: int, score: float, status: str = "info"):
        """Log optimization iteration."""
        self.iteration_count = iteration
        
        if score > self.best_score:
            self.best_score = score
            status = "best"
        
        self.logger.log_operation_step(
            f"iteration_{iteration}",
            status=status,
            iteration=iteration,
            score=score,
            best_score=self.best_score,
            improvement=score - self.best_score if score != self.best_score else 0
        )
    
    def log_convergence(self, final_iteration: int, final_score: float, reason: str):
        """Log optimization convergence."""
        self.logger.log_operation_step(
            "convergence",
            status="info",
            final_iteration=final_iteration,
            final_score=final_score,
            reason=reason,
            total_iterations=self.iteration_count
        )
    
    def log_constraint_analysis(self, constraint_data: Dict[str, Any]):
        """Log constraint analysis results."""
        self.logger.log_operation_step(
            "constraint_analysis",
            status="info",
            constraint_data=constraint_data
        )
    
    def log_elective_allocation(self, allocation_data: Dict[str, Any]):
        """Log elective allocation results."""
        self.logger.log_operation_step(
            "elective_allocation",
            status="info",
            allocation_data=allocation_data
        )

