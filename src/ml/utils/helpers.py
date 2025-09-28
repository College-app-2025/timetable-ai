"""
Helper utilities for the SIH Timetable Optimization System.
"""

import random
import math
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

from src.utils.logger_config import get_logger

logger = get_logger("ml_helpers")


@dataclass
class TimeSlot:
    """Represents a time slot for scheduling."""
    id: str
    day: int  # 0-6 (Monday-Sunday)
    hour: int  # 0-23
    minute: int  # 0-59
    duration: int  # Duration in minutes
    
    def __str__(self):
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return f"{days[self.day]} {self.hour:02d}:{self.minute:02d} ({self.duration}min)"


class DataHelper:
    """Helper functions for data manipulation and validation."""
    
    @staticmethod
    def validate_student_data(students: List[Any]) -> Tuple[bool, List[str]]:
        """Validate student data for optimization."""
        errors = []
        
        if not students:
            errors.append("No students provided")
            return False, errors
        
        for i, student in enumerate(students):
            if not hasattr(student, 'id') or not student.id:
                errors.append(f"Student {i} missing id")
            
            if not hasattr(student, 'department') or not student.department:
                errors.append(f"Student {i} missing department")
            
            if hasattr(student, 'satisfaction_score') and student.satisfaction_score is not None:
                if not (0 <= student.satisfaction_score <= 1):
                    errors.append(f"Student {i} satisfaction_score out of range [0,1]")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_course_data(courses: List[Any]) -> Tuple[bool, List[str]]:
        """Validate course data for optimization."""
        errors = []
        
        if not courses:
            errors.append("No courses provided")
            return False, errors
        
        for i, course in enumerate(courses):
            if not hasattr(course, 'id') or not course.id:
                errors.append(f"Course {i} missing id")
            
            if not hasattr(course, 'hours_per_week') or course.hours_per_week <= 0:
                errors.append(f"Course {i} invalid hours_per_week")
            
            if hasattr(course, 'is_elective') and course.is_elective:
                if not hasattr(course, 'max_students') or course.max_students <= 0:
                    errors.append(f"Elective course {i} missing or invalid max_students")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_faculty_data(faculty: List[Any]) -> Tuple[bool, List[str]]:
        """Validate faculty data for optimization."""
        errors = []
        
        if not faculty:
            errors.append("No faculty provided")
            return False, errors
        
        for i, teacher in enumerate(faculty):
            if not hasattr(teacher, 'id') or not teacher.id:
                errors.append(f"Faculty {i} missing id")
            
            if not hasattr(teacher, 'department') or not teacher.department:
                errors.append(f"Faculty {i} missing department")
            
            if hasattr(teacher, 'max_hours_per_week') and teacher.max_hours_per_week <= 0:
                errors.append(f"Faculty {i} invalid max_hours_per_week")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_room_data(rooms: List[Any]) -> Tuple[bool, List[str]]:
        """Validate room data for optimization."""
        errors = []
        
        if not rooms:
            errors.append("No rooms provided")
            return False, errors
        
        for i, room in enumerate(rooms):
            if not hasattr(room, 'id') or not room.id:
                errors.append(f"Room {i} missing id")
            
            if not hasattr(room, 'capacity') or room.capacity <= 0:
                errors.append(f"Room {i} invalid capacity")
            
            if hasattr(room, 'room_type') and not room.room_type:
                errors.append(f"Room {i} missing room_type")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def calculate_data_quality_score(students: List[Any], 
                                   courses: List[Any], 
                                   faculty: List[Any], 
                                   rooms: List[Any]) -> float:
        """Calculate overall data quality score (0-1)."""
        try:
            scores = []
            
            # Student data quality
            student_valid, _ = DataHelper.validate_student_data(students)
            scores.append(1.0 if student_valid else 0.0)
            
            # Course data quality
            course_valid, _ = DataHelper.validate_course_data(courses)
            scores.append(1.0 if course_valid else 0.0)
            
            # Faculty data quality
            faculty_valid, _ = DataHelper.validate_faculty_data(faculty)
            scores.append(1.0 if faculty_valid else 0.0)
            
            # Room data quality
            room_valid, _ = DataHelper.validate_room_data(rooms)
            scores.append(1.0 if room_valid else 0.0)
            
            # Data completeness
            completeness = 1.0 if all([students, courses, faculty, rooms]) else 0.0
            scores.append(completeness)
            
            return sum(scores) / len(scores)
            
        except Exception as e:
            logger.error(f"Error calculating data quality score: {str(e)}")
            return 0.0


class TimeHelper:
    """Helper functions for time-related operations."""
    
    @staticmethod
    def generate_time_slots(start_hour: int = 8, 
                           end_hour: int = 18, 
                           slot_duration: int = 60,
                           days: List[int] = None) -> List[TimeSlot]:
        """Generate time slots for scheduling."""
        if days is None:
            days = [0, 1, 2, 3, 4]  # Monday to Friday
        
        time_slots = []
        slot_id = 0
        
        for day in days:
            current_hour = start_hour
            while current_hour < end_hour:
                time_slot = TimeSlot(
                    id=f"slot_{slot_id}",
                    day=day,
                    hour=current_hour,
                    minute=0,
                    duration=slot_duration
                )
                time_slots.append(time_slot)
                slot_id += 1
                current_hour += 1
        
        return time_slots
    
    @staticmethod
    def is_time_slot_available(time_slot: TimeSlot, 
                              existing_assignments: List[Any],
                              room_id: str = None,
                              faculty_id: str = None) -> bool:
        """Check if a time slot is available for assignment."""
        for assignment in existing_assignments:
            if hasattr(assignment, 'time_slot_id') and assignment.time_slot_id == time_slot.id:
                # Check room conflict
                if room_id and hasattr(assignment, 'room_id') and assignment.room_id == room_id:
                    return False
                
                # Check faculty conflict
                if faculty_id and hasattr(assignment, 'faculty_id') and assignment.faculty_id == faculty_id:
                    return False
        
        return True
    
    @staticmethod
    def calculate_time_conflicts(assignments: List[Any]) -> int:
        """Calculate number of time conflicts in assignments."""
        conflicts = 0
        
        # Group assignments by time slot
        time_slot_assignments = {}
        for assignment in assignments:
            if hasattr(assignment, 'time_slot_id'):
                time_slot_id = assignment.time_slot_id
                if time_slot_id not in time_slot_assignments:
                    time_slot_assignments[time_slot_id] = []
                time_slot_assignments[time_slot_id].append(assignment)
        
        # Check for conflicts in each time slot
        for time_slot_id, slot_assignments in time_slot_assignments.items():
            if len(slot_assignments) > 1:
                # Check room conflicts
                room_assignments = {}
                for assignment in slot_assignments:
                    if hasattr(assignment, 'room_id'):
                        room_id = assignment.room_id
                        if room_id in room_assignments:
                            conflicts += 1
                        else:
                            room_assignments[room_id] = assignment
                
                # Check faculty conflicts
                faculty_assignments = {}
                for assignment in slot_assignments:
                    if hasattr(assignment, 'faculty_id'):
                        faculty_id = assignment.faculty_id
                        if faculty_id in faculty_assignments:
                            conflicts += 1
                        else:
                            faculty_assignments[faculty_id] = assignment
        
        return conflicts


class ValidationHelper:
    """Helper functions for validation operations."""
    
    @staticmethod
    def validate_optimization_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate optimization configuration."""
        errors = []
        
        required_fields = [
            'max_iterations', 'timeout_seconds', 'satisfaction_weight',
            'workload_weight', 'utilization_weight', 'elective_weight'
        ]
        
        for field in required_fields:
            if field not in config:
                errors.append(f"Missing required field: {field}")
            elif not isinstance(config[field], (int, float)):
                errors.append(f"Field {field} must be a number")
        
        # Validate weight constraints
        weight_fields = [
            'satisfaction_weight', 'workload_weight', 
            'utilization_weight', 'elective_weight'
        ]
        
        total_weight = sum(config.get(field, 0) for field in weight_fields)
        if total_weight > 1.1:  # Allow small floating point errors
            errors.append("Sum of weights exceeds 1.0")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_constraint_parameters(constraints: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate constraint parameters."""
        errors = []
        
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
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_schedule_feasibility(assignments: List[Any], 
                                    students: List[Any],
                                    courses: List[Any],
                                    faculty: List[Any],
                                    rooms: List[Any]) -> Tuple[bool, List[str]]:
        """Validate if a schedule is feasible."""
        errors = []
        
        # Check for time conflicts
        time_conflicts = TimeHelper.calculate_time_conflicts(assignments)
        if time_conflicts > 0:
            errors.append(f"Found {time_conflicts} time conflicts")
        
        # Check room capacity constraints
        for assignment in assignments:
            if hasattr(assignment, 'room_id') and hasattr(assignment, 'course_id'):
                room = next((r for r in rooms if r.id == assignment.room_id), None)
                course = next((c for c in courses if c.id == assignment.course_id), None)
                
                if room and course:
                    if hasattr(course, 'max_students') and course.max_students > room.capacity:
                        errors.append(f"Course {course.id} exceeds room {room.id} capacity")
        
        # Check faculty availability
        for assignment in assignments:
            if hasattr(assignment, 'faculty_id'):
                faculty_member = next((f for f in faculty if f.id == assignment.faculty_id), None)
                if not faculty_member:
                    errors.append(f"Faculty {assignment.faculty_id} not found")
        
        return len(errors) == 0, errors


class MathHelper:
    """Helper functions for mathematical operations."""
    
    @staticmethod
    def calculate_satisfaction_score(preferences: List[float], 
                                   assignments: List[Any]) -> float:
        """Calculate student satisfaction score."""
        if not preferences or not assignments:
            return 0.0
        
        try:
            # Simple satisfaction calculation based on preference fulfillment
            fulfilled_preferences = sum(1 for pref in preferences if pref > 0.5)
            total_preferences = len(preferences)
            
            return fulfilled_preferences / total_preferences if total_preferences > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating satisfaction score: {str(e)}")
            return 0.0
    
    @staticmethod
    def calculate_workload_balance(faculty_workloads: List[int]) -> float:
        """Calculate faculty workload balance score."""
        if not faculty_workloads:
            return 0.0
        
        try:
            if len(faculty_workloads) == 1:
                return 1.0
            
            # Calculate coefficient of variation (lower is better)
            mean_workload = sum(faculty_workloads) / len(faculty_workloads)
            if mean_workload == 0:
                return 1.0
            
            variance = sum((workload - mean_workload) ** 2 for workload in faculty_workloads) / len(faculty_workloads)
            std_dev = math.sqrt(variance)
            coefficient_of_variation = std_dev / mean_workload
            
            # Convert to balance score (0-1, higher is better)
            return max(0.0, 1.0 - coefficient_of_variation)
            
        except Exception as e:
            logger.error(f"Error calculating workload balance: {str(e)}")
            return 0.0
    
    @staticmethod
    def calculate_room_utilization(room_assignments: Dict[str, int], 
                                 total_slots: int) -> float:
        """Calculate room utilization rate."""
        if not room_assignments or total_slots <= 0:
            return 0.0
        
        try:
            total_assignments = sum(room_assignments.values())
            return min(1.0, total_assignments / (len(room_assignments) * total_slots))
            
        except Exception as e:
            logger.error(f"Error calculating room utilization: {str(e)}")
            return 0.0
    
    @staticmethod
    def normalize_score(score: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
        """Normalize score to 0-1 range."""
        try:
            if max_val == min_val:
                return 0.0
            
            normalized = (score - min_val) / (max_val - min_val)
            return max(0.0, min(1.0, normalized))
            
        except Exception as e:
            logger.error(f"Error normalizing score: {str(e)}")
            return 0.0

