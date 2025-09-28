"""
Data transformers for the SIH Timetable Optimization System.
Preprocesses and normalizes data for optimization.
"""

from typing import List, Dict, Any, Optional
from src.utils.logger_config import get_logger

from .models import (
    Student, Course, Faculty, Room, TimeSlot, Assignment,
    Schedule, OptimizationConfig, CourseType, RoomType
)

logger = get_logger("data_transformers")


def preprocess_student_data(students: List[Student]) -> List[Student]:
    """Preprocess student data for optimization."""
    try:
        logger.info(f"Preprocessing {len(students)} students")
        
        processed_students = []
        for student in students:
            # Clean and normalize data
            student.name = student.name.strip() if student.name else "Unknown"
            student.email = student.email.strip().lower() if student.email else ""
            student.department = student.department.strip() if student.department else "Unknown"
            
            # Ensure semester is valid
            if student.semester < 1:
                student.semester = 1
            elif student.semester > 8:
                student.semester = 8
            
            # Sort preferences by priority
            student.preferences.sort(key=lambda x: x.priority)
            
            # Calculate satisfaction score if not set
            if student.satisfaction_score == 0.0:
                student.satisfaction_score = student.calculate_satisfaction()
            
            processed_students.append(student)
        
        logger.info(f"Preprocessed {len(processed_students)} students")
        return processed_students
        
    except Exception as e:
        logger.error(f"Error preprocessing student data: {str(e)}")
        return students


def preprocess_course_data(courses: List[Course]) -> List[Course]:
    """Preprocess course data for optimization."""
    try:
        logger.info(f"Preprocessing {len(courses)} courses")
        
        processed_courses = []
        for course in courses:
            # Clean and normalize data
            course.name = course.name.strip() if course.name else "Unknown"
            course.course_code = course.course_code.strip().upper() if course.course_code else ""
            course.department = course.department.strip() if course.department else "Unknown"
            
            # Ensure valid values
            if course.semester < 1:
                course.semester = 1
            elif course.semester > 8:
                course.semester = 8
            
            if course.hours_per_week < 1:
                course.hours_per_week = 1
            elif course.hours_per_week > 12:
                course.hours_per_week = 12
            
            if course.max_students_per_section < 1:
                course.max_students_per_section = 30
            elif course.max_students_per_section > 200:
                course.max_students_per_section = 200
            
            # Set elective capacity if not set
            if course.is_elective and course.elective_capacity == 0:
                course.elective_capacity = course.max_students_per_section
            
            processed_courses.append(course)
        
        logger.info(f"Preprocessed {len(processed_courses)} courses")
        return processed_courses
        
    except Exception as e:
        logger.error(f"Error preprocessing course data: {str(e)}")
        return courses


def preprocess_faculty_data(faculty: List[Faculty]) -> List[Faculty]:
    """Preprocess faculty data for optimization."""
    try:
        logger.info(f"Preprocessing {len(faculty)} faculty members")
        
        processed_faculty = []
        for teacher in faculty:
            # Clean and normalize data
            teacher.name = teacher.name.strip() if teacher.name else "Unknown"
            teacher.email = teacher.email.strip().lower() if teacher.email else ""
            teacher.department = teacher.department.strip() if teacher.department else "Unknown"
            teacher.designation = teacher.designation.strip() if teacher.designation else "Professor"
            
            # Ensure valid limits
            if teacher.max_hours_per_day < 1:
                teacher.max_hours_per_day = 6
            elif teacher.max_hours_per_day > 12:
                teacher.max_hours_per_day = 12
            
            if teacher.max_hours_per_week < 1:
                teacher.max_hours_per_week = 30
            elif teacher.max_hours_per_week > 60:
                teacher.max_hours_per_week = 60
            
            # Clean subjects list
            teacher.subjects = [s.strip() for s in teacher.subjects if s.strip()]
            
            processed_faculty.append(teacher)
        
        logger.info(f"Preprocessed {len(processed_faculty)} faculty members")
        return processed_faculty
        
    except Exception as e:
        logger.error(f"Error preprocessing faculty data: {str(e)}")
        return faculty


def normalize_time_slots(time_slots: List[TimeSlot]) -> List[TimeSlot]:
    """Normalize time slots for optimization."""
    try:
        logger.info(f"Normalizing {len(time_slots)} time slots")
        
        # Sort by day and period
        time_slots.sort(key=lambda x: (x.day, x.period))
        
        # Ensure unique IDs
        for i, slot in enumerate(time_slots):
            slot.id = i + 1
        
        logger.info(f"Normalized {len(time_slots)} time slots")
        return time_slots
        
    except Exception as e:
        logger.error(f"Error normalizing time slots: {str(e)}")
        return time_slots


def create_department_sections(students: List[Student]) -> Dict[str, List[str]]:
    """Create department sections from student data."""
    try:
        logger.info("Creating department sections")
        
        sections = {}
        for student in students:
            dept = student.department
            semester = student.semester
            section_key = f"{dept}_{semester}"
            
            if section_key not in sections:
                sections[section_key] = []
            sections[section_key].append(student.id)
        
        logger.info(f"Created {len(sections)} department sections")
        return sections
        
    except Exception as e:
        logger.error(f"Error creating department sections: {str(e)}")
        return {}


def normalize_room_capacities(rooms: List[Room]) -> List[Room]:
    """Normalize room capacities for optimization."""
    try:
        logger.info(f"Normalizing {len(rooms)} room capacities")
        
        for room in rooms:
            # Ensure minimum capacity
            if room.capacity < 10:
                room.capacity = 10
            elif room.capacity > 500:
                room.capacity = 500
        
        logger.info(f"Normalized {len(rooms)} room capacities")
        return rooms
        
    except Exception as e:
        logger.error(f"Error normalizing room capacities: {str(e)}")
        return rooms


def create_optimization_variables(students: List[Student],
                                courses: List[Course],
                                faculty: List[Faculty],
                                rooms: List[Room],
                                time_slots: List[TimeSlot]) -> Dict[str, Any]:
    """Create optimization variables for the solver."""
    try:
        logger.info("Creating optimization variables")
        
        variables = {
            "students": students,
            "courses": courses,
            "faculty": faculty,
            "rooms": rooms,
            "time_slots": time_slots,
            "variable_count": 0
        }
        
        # This would be implemented with the actual OR-Tools variable creation
        # For now, return the basic structure
        logger.info("Optimization variables created")
        return variables
        
    except Exception as e:
        logger.error(f"Error creating optimization variables: {str(e)}")
        return {}


def apply_data_filters(students: List[Student],
                      courses: List[Course],
                      faculty: List[Faculty],
                      rooms: List[Room],
                      filters: Dict[str, Any]) -> Dict[str, List]:
    """Apply filters to the dataset."""
    try:
        logger.info("Applying data filters")
        
        filtered_data = {
            "students": students,
            "courses": courses,
            "faculty": faculty,
            "rooms": rooms
        }
        
        # Apply student filters
        if "department" in filters:
            filtered_data["students"] = [
                s for s in students if s.department == filters["department"]
            ]
        
        if "semester" in filters:
            filtered_data["students"] = [
                s for s in filtered_data["students"] if s.semester == filters["semester"]
            ]
        
        # Apply course filters
        if "course_type" in filters:
            filtered_data["courses"] = [
                c for c in courses if c.course_type.value == filters["course_type"]
            ]
        
        # Apply faculty filters
        if "department" in filters:
            filtered_data["faculty"] = [
                f for f in faculty if f.department == filters["department"]
            ]
        
        logger.info("Data filters applied")
        return filtered_data
        
    except Exception as e:
        logger.error(f"Error applying data filters: {str(e)}")
        return {"students": students, "courses": courses, "faculty": faculty, "rooms": rooms}

