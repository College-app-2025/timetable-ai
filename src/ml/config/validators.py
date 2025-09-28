"""
Configuration validators for the SIH Timetable Optimization System.
Validates optimization parameters and constraints.
"""

from typing import Dict, Any, List, Optional
from src.utils.logger_config import get_logger

logger = get_logger("config_validator")


class ConfigValidator:
    """Validates configuration parameters for optimization."""
    
    def __init__(self):
        self.logger = logger
    
    def validate_optimization_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate optimization configuration parameters."""
        try:
            self.logger.info("Validating optimization configuration")
            
            errors = []
            warnings = []
            
            # Validate required fields
            required_fields = [
                'max_iterations', 'timeout_seconds', 'satisfaction_weight',
                'workload_weight', 'utilization_weight', 'elective_weight'
            ]
            
            for field in required_fields:
                if field not in config:
                    errors.append(f"Missing required field: {field}")
                elif not isinstance(config[field], (int, float)):
                    errors.append(f"Field {field} must be a number")
            
            # Validate numeric ranges
            if 'max_iterations' in config:
                if not (1 <= config['max_iterations'] <= 10000):
                    errors.append("max_iterations must be between 1 and 10000")
            
            if 'timeout_seconds' in config:
                if not (1 <= config['timeout_seconds'] <= 3600):
                    errors.append("timeout_seconds must be between 1 and 3600")
            
            # Validate weight constraints
            weight_fields = [
                'satisfaction_weight', 'workload_weight', 
                'utilization_weight', 'elective_weight'
            ]
            
            total_weight = 0
            for field in weight_fields:
                if field in config:
                    weight = config[field]
                    if not (0 <= weight <= 1):
                        errors.append(f"{field} must be between 0 and 1")
                    total_weight += weight
            
            if total_weight > 1.1:  # Allow small floating point errors
                warnings.append("Sum of weights exceeds 1.0 - consider normalizing")
            
            # Validate elective parameters
            if 'elective_allocation_strategy' in config:
                valid_strategies = ['priority', 'random', 'balanced']
                if config['elective_allocation_strategy'] not in valid_strategies:
                    errors.append(f"elective_allocation_strategy must be one of {valid_strategies}")
            
            # Validate time constraints
            if 'max_classes_per_day' in config:
                if not (1 <= config['max_classes_per_day'] <= 12):
                    errors.append("max_classes_per_day must be between 1 and 12")
            
            if 'max_hours_per_day' in config:
                if not (1 <= config['max_hours_per_day'] <= 16):
                    errors.append("max_hours_per_day must be between 1 and 16")
            
            result = {
                'is_valid': len(errors) == 0,
                'errors': errors,
                'warnings': warnings,
                'validated_config': config
            }
            
            if errors:
                self.logger.error(f"Configuration validation failed: {errors}")
            else:
                self.logger.info("Configuration validation successful")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error validating configuration: {str(e)}")
            return {
                'is_valid': False,
                'errors': [str(e)],
                'warnings': [],
                'validated_config': config
            }
    
    def validate_constraint_parameters(self, constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Validate constraint parameters."""
        try:
            self.logger.info("Validating constraint parameters")
            
            errors = []
            warnings = []
            
            # Validate hard constraints
            hard_constraints = constraints.get('hard_constraints', {})
            
            if 'max_room_capacity' in hard_constraints:
                if not isinstance(hard_constraints['max_room_capacity'], int):
                    errors.append("max_room_capacity must be an integer")
                elif hard_constraints['max_room_capacity'] <= 0:
                    errors.append("max_room_capacity must be positive")
            
            if 'min_classes_per_subject' in hard_constraints:
                if not isinstance(hard_constraints['min_classes_per_subject'], int):
                    errors.append("min_classes_per_subject must be an integer")
                elif hard_constraints['min_classes_per_subject'] < 0:
                    errors.append("min_classes_per_subject must be non-negative")
            
            # Validate soft constraints
            soft_constraints = constraints.get('soft_constraints', {})
            
            if 'preferred_time_slots' in soft_constraints:
                if not isinstance(soft_constraints['preferred_time_slots'], list):
                    errors.append("preferred_time_slots must be a list")
                else:
                    for slot in soft_constraints['preferred_time_slots']:
                        if not isinstance(slot, (int, str)):
                            errors.append("preferred_time_slots must contain integers or strings")
            
            if 'max_gap_between_classes' in soft_constraints:
                if not isinstance(soft_constraints['max_gap_between_classes'], int):
                    errors.append("max_gap_between_classes must be an integer")
                elif soft_constraints['max_gap_between_classes'] < 0:
                    errors.append("max_gap_between_classes must be non-negative")
            
            result = {
                'is_valid': len(errors) == 0,
                'errors': errors,
                'warnings': warnings,
                'validated_constraints': constraints
            }
            
            if errors:
                self.logger.error(f"Constraint validation failed: {errors}")
            else:
                self.logger.info("Constraint validation successful")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error validating constraints: {str(e)}")
            return {
                'is_valid': False,
                'errors': [str(e)],
                'warnings': [],
                'validated_constraints': constraints
            }
    
    def validate_data_quality(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data quality for optimization."""
        try:
            self.logger.info("Validating data quality")
            
            errors = []
            warnings = []
            
            # Check for required data
            required_data = ['students', 'courses', 'faculty', 'rooms', 'time_slots']
            
            for data_type in required_data:
                if data_type not in data:
                    errors.append(f"Missing required data: {data_type}")
                elif not isinstance(data[data_type], list):
                    errors.append(f"{data_type} must be a list")
                elif len(data[data_type]) == 0:
                    warnings.append(f"No {data_type} found - optimization may not be possible")
            
            # Validate student data
            if 'students' in data and isinstance(data['students'], list):
                for i, student in enumerate(data['students']):
                    if not hasattr(student, 'id'):
                        errors.append(f"Student {i} missing id")
                    if not hasattr(student, 'department'):
                        errors.append(f"Student {i} missing department")
                    if hasattr(student, 'satisfaction_score') and student.satisfaction_score is not None:
                        if not (0 <= student.satisfaction_score <= 1):
                            warnings.append(f"Student {i} satisfaction_score out of range [0,1]")
            
            # Validate course data
            if 'courses' in data and isinstance(data['courses'], list):
                for i, course in enumerate(data['courses']):
                    if not hasattr(course, 'id'):
                        errors.append(f"Course {i} missing id")
                    if not hasattr(course, 'hours_per_week'):
                        errors.append(f"Course {i} missing hours_per_week")
                    elif course.hours_per_week <= 0:
                        errors.append(f"Course {i} hours_per_week must be positive")
            
            # Validate faculty data
            if 'faculty' in data and isinstance(data['faculty'], list):
                for i, teacher in enumerate(data['faculty']):
                    if not hasattr(teacher, 'id'):
                        errors.append(f"Faculty {i} missing id")
                    if not hasattr(teacher, 'department'):
                        errors.append(f"Faculty {i} missing department")
            
            # Validate room data
            if 'rooms' in data and isinstance(data['rooms'], list):
                for i, room in enumerate(data['rooms']):
                    if not hasattr(room, 'id'):
                        errors.append(f"Room {i} missing id")
                    if not hasattr(room, 'capacity'):
                        errors.append(f"Room {i} missing capacity")
                    elif room.capacity <= 0:
                        errors.append(f"Room {i} capacity must be positive")
            
            result = {
                'is_valid': len(errors) == 0,
                'errors': errors,
                'warnings': warnings,
                'data_quality_score': self._calculate_data_quality_score(data)
            }
            
            if errors:
                self.logger.error(f"Data quality validation failed: {errors}")
            else:
                self.logger.info("Data quality validation successful")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error validating data quality: {str(e)}")
            return {
                'is_valid': False,
                'errors': [str(e)],
                'warnings': [],
                'data_quality_score': 0.0
            }
    
    def _calculate_data_quality_score(self, data: Dict[str, Any]) -> float:
        """Calculate data quality score (0-1)."""
        try:
            score = 0.0
            total_checks = 0
            
            # Check data completeness
            required_data = ['students', 'courses', 'faculty', 'rooms', 'time_slots']
            for data_type in required_data:
                total_checks += 1
                if data_type in data and isinstance(data[data_type], list) and len(data[data_type]) > 0:
                    score += 1.0
            
            # Check data consistency
            if 'students' in data and 'courses' in data:
                total_checks += 1
                if len(data['students']) > 0 and len(data['courses']) > 0:
                    score += 1.0
            
            if 'faculty' in data and 'courses' in data:
                total_checks += 1
                if len(data['faculty']) > 0 and len(data['courses']) > 0:
                    score += 1.0
            
            return score / total_checks if total_checks > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating data quality score: {str(e)}")
            return 0.0

