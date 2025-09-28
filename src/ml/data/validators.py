"""
Data validators for the SIH Timetable Optimization System.
Validates data integrity and constraints before optimization.
"""

from typing import List, Dict, Any, Optional
from src.utils.logger_config import get_logger

from .models import (
    Student, Course, Faculty, Room, TimeSlot, Assignment,
    Schedule, OptimizationConfig, CourseType, RoomType
)

logger = get_logger("data_validators")


def validate_student_data(students: List[Student]) -> Dict[str, Any]:
    """Validate student data for optimization."""
    try:
        errors = []
        warnings = []
        
        if not students:
            errors.append("No students found")
            return {"valid": False, "errors": errors, "warnings": warnings}
        
        for student in students:
            # Check required fields
            if not student.id:
                errors.append(f"Student missing ID: {student.name}")
            if not student.email:
                errors.append(f"Student missing email: {student.name}")
            if not student.department:
                warnings.append(f"Student missing department: {student.name}")
            if student.semester < 1 or student.semester > 8:
                errors.append(f"Invalid semester for student {student.name}: {student.semester}")
            
            # Check preferences
            if not student.preferences:
                warnings.append(f"Student {student.name} has no preferences")
            else:
                for pref in student.preferences:
                    if pref.priority < 1 or pref.priority > 5:
                        errors.append(f"Invalid preference priority for {student.name}: {pref.priority}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "student_count": len(students)
        }
        
    except Exception as e:
        logger.error(f"Error validating student data: {str(e)}")
        return {"valid": False, "errors": [str(e)], "warnings": []}


def validate_course_data(courses: List[Course]) -> Dict[str, Any]:
    """Validate course data for optimization."""
    try:
        errors = []
        warnings = []
        
        if not courses:
            errors.append("No courses found")
            return {"valid": False, "errors": errors, "warnings": warnings}
        
        for course in courses:
            # Check required fields
            if not course.id:
                errors.append(f"Course missing ID: {course.name}")
            if not course.name:
                errors.append(f"Course missing name: {course.id}")
            if not course.course_code:
                errors.append(f"Course missing code: {course.name}")
            if course.semester < 1 or course.semester > 8:
                errors.append(f"Invalid semester for course {course.name}: {course.semester}")
            if course.hours_per_week < 1 or course.hours_per_week > 12:
                errors.append(f"Invalid hours per week for course {course.name}: {course.hours_per_week}")
            
            # Check elective capacity
            if course.is_elective and course.elective_capacity <= 0:
                warnings.append(f"Elective course {course.name} has no capacity")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "course_count": len(courses),
            "elective_count": len([c for c in courses if c.is_elective])
        }
        
    except Exception as e:
        logger.error(f"Error validating course data: {str(e)}")
        return {"valid": False, "errors": [str(e)], "warnings": []}


def validate_faculty_data(faculty: List[Faculty]) -> Dict[str, Any]:
    """Validate faculty data for optimization."""
    try:
        errors = []
        warnings = []
        
        if not faculty:
            errors.append("No faculty found")
            return {"valid": False, "errors": errors, "warnings": warnings}
        
        for teacher in faculty:
            # Check required fields
            if not teacher.id:
                errors.append(f"Faculty missing ID: {teacher.name}")
            if not teacher.name:
                errors.append(f"Faculty missing name: {teacher.id}")
            if not teacher.email:
                errors.append(f"Faculty missing email: {teacher.name}")
            if not teacher.department:
                warnings.append(f"Faculty missing department: {teacher.name}")
            
            # Check subjects
            if not teacher.subjects:
                warnings.append(f"Faculty {teacher.name} has no subjects assigned")
            
            # Check availability
            if not teacher.is_available:
                warnings.append(f"Faculty {teacher.name} is not available")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "faculty_count": len(faculty),
            "available_faculty": len([f for f in faculty if f.is_available])
        }
        
    except Exception as e:
        logger.error(f"Error validating faculty data: {str(e)}")
        return {"valid": False, "errors": [str(e)], "warnings": []}


def validate_room_data(rooms: List[Room]) -> Dict[str, Any]:
    """Validate room data for optimization."""
    try:
        errors = []
        warnings = []
        
        if not rooms:
            errors.append("No rooms found")
            return {"valid": False, "errors": errors, "warnings": warnings}
        
        for room in rooms:
            # Check required fields
            if not room.id:
                errors.append(f"Room missing ID: {room.name}")
            if not room.name:
                errors.append(f"Room missing name: {room.id}")
            if room.capacity <= 0:
                errors.append(f"Invalid capacity for room {room.name}: {room.capacity}")
            
            # Check accessibility
            if not room.is_accessible:
                warnings.append(f"Room {room.name} is not accessible")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "room_count": len(rooms),
            "total_capacity": sum(r.capacity for r in rooms)
        }
        
    except Exception as e:
        logger.error(f"Error validating room data: {str(e)}")
        return {"valid": False, "errors": [str(e)], "warnings": []}


def validate_time_slot_data(time_slots: List[TimeSlot]) -> Dict[str, Any]:
    """Validate time slot data for optimization."""
    try:
        errors = []
        warnings = []
        
        if not time_slots:
            errors.append("No time slots found")
            return {"valid": False, "errors": errors, "warnings": warnings}
        
        for slot in time_slots:
            # Check required fields
            if not slot.id:
                errors.append(f"Time slot missing ID")
            if slot.day < 1 or slot.day > 6:
                errors.append(f"Invalid day for time slot {slot.id}: {slot.day}")
            if slot.period < 1:
                errors.append(f"Invalid period for time slot {slot.id}: {slot.period}")
            
            # Check time validity
            if slot.start_time >= slot.end_time:
                errors.append(f"Invalid time range for slot {slot.id}: {slot.start_time} >= {slot.end_time}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "time_slot_count": len(time_slots),
            "working_days": len(set(s.day for s in time_slots))
        }
        
    except Exception as e:
        logger.error(f"Error validating time slot data: {str(e)}")
        return {"valid": False, "errors": [str(e)], "warnings": []}


def validate_optimization_config(config: OptimizationConfig) -> Dict[str, Any]:
    """Validate optimization configuration."""
    try:
        errors = []
        warnings = []
        
        # Check time limits
        if config.max_optimization_time <= 0:
            errors.append("Invalid optimization time limit")
        if config.max_iterations <= 0:
            errors.append("Invalid iteration limit")
        
        # Check weights
        if config.student_satisfaction_weight < 0:
            errors.append("Student satisfaction weight cannot be negative")
        if config.faculty_workload_weight < 0:
            errors.append("Faculty workload weight cannot be negative")
        if config.room_utilization_weight < 0:
            errors.append("Room utilization weight cannot be negative")
        
        # Check elective limits
        if config.max_electives_per_student < config.min_electives_per_student:
            errors.append("Max electives cannot be less than min electives")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
        
    except Exception as e:
        logger.error(f"Error validating optimization config: {str(e)}")
        return {"valid": False, "errors": [str(e)], "warnings": []}


def validate_complete_dataset(students: List[Student],
                            courses: List[Course],
                            faculty: List[Faculty],
                            rooms: List[Room],
                            time_slots: List[TimeSlot]) -> Dict[str, Any]:
    """Validate complete dataset for optimization."""
    try:
        logger.info("Validating complete dataset")
        
        # Validate individual components
        student_validation = validate_student_data(students)
        course_validation = validate_course_data(courses)
        faculty_validation = validate_faculty_data(faculty)
        room_validation = validate_room_data(rooms)
        time_slot_validation = validate_time_slot_data(time_slots)
        
        # Combine results
        all_errors = []
        all_warnings = []
        
        all_errors.extend(student_validation.get("errors", []))
        all_errors.extend(course_validation.get("errors", []))
        all_errors.extend(faculty_validation.get("errors", []))
        all_errors.extend(room_validation.get("errors", []))
        all_errors.extend(time_slot_validation.get("errors", []))
        
        all_warnings.extend(student_validation.get("warnings", []))
        all_warnings.extend(course_validation.get("warnings", []))
        all_warnings.extend(faculty_validation.get("warnings", []))
        all_warnings.extend(room_validation.get("warnings", []))
        all_warnings.extend(time_slot_validation.get("warnings", []))
        
        # Check cross-component constraints
        cross_errors = validate_cross_component_constraints(students, courses, faculty, rooms)
        all_errors.extend(cross_errors)
        
        return {
            "valid": len(all_errors) == 0,
            "errors": all_errors,
            "warnings": all_warnings,
            "component_validation": {
                "students": student_validation,
                "courses": course_validation,
                "faculty": faculty_validation,
                "rooms": room_validation,
                "time_slots": time_slot_validation
            }
        }
        
    except Exception as e:
        logger.error(f"Error validating complete dataset: {str(e)}")
        return {"valid": False, "errors": [str(e)], "warnings": []}


def validate_cross_component_constraints(students: List[Student],
                                       courses: List[Course],
                                       faculty: List[Faculty],
                                       rooms: List[Room]) -> List[str]:
    """Validate constraints across different components."""
    errors = []
    
    try:
        # Check if faculty can teach courses
        for course in courses:
            if not any(f.can_teach_course(course.id) for f in faculty):
                errors.append(f"No faculty can teach course: {course.name}")
        
        # Check if rooms are suitable for courses
        for course in courses:
            if not any(r.is_suitable_for_course(course) for r in rooms):
                errors.append(f"No suitable room for course: {course.name}")
        
        # Check student preferences against available courses
        for student in students:
            for preference in student.preferences:
                if not any(c.id == preference.course_id for c in courses):
                    errors.append(f"Student {student.name} prefers non-existent course: {preference.course_id}")
        
        return errors
        
    except Exception as e:
        logger.error(f"Error validating cross-component constraints: {str(e)}")
        return [str(e)]

