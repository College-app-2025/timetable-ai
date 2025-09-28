"""
Database loaders for the SIH Timetable Optimization System.
Fetches data from Prisma models and converts to domain models.
"""

from typing import List, Dict, Any, Optional
from datetime import time
import asyncio
from src.utils.prisma import db
from src.utils.logger_config import get_logger

from .models import (
    Student, Course, Faculty, Room, TimeSlot, StudentPreference,
    Department, Section, OptimizationConfig, CourseType, RoomType,
    DifficultyLevel
)

logger = get_logger("data_loaders")


async def load_students_from_db(institute_id: str) -> List[Student]:
    """Load students from database for a specific institute."""
    try:
        logger.info(f"Loading students for institute: {institute_id}")
        
        students_data = await db.student.find_many(
            where={"institute_id": institute_id},
            include={"institute": True}
        )
        
        students = []
        for student_data in students_data:
            student = Student(
                id=student_data.s_id,
                student_id=student_data.student_id,
                name=student_data.name if student_data.name != "__" else "Unknown",
                email=student_data.email,
                department=student_data.branch if student_data.branch != "__" else "Unknown",
                semester=student_data.semester,
                section=f"Section_{student_data.semester}_{student_data.branch}",
                is_active=True
            )
            students.append(student)
        
        logger.info(f"Loaded {len(students)} students")
        return students
        
    except Exception as e:
        logger.error(f"Error loading students: {str(e)}")
        return []


async def load_courses_from_db(institute_id: str) -> List[Course]:
    """Load courses from database for a specific institute."""
    try:
        logger.info(f"Loading courses for institute: {institute_id}")
        
        courses_data = await db.subject.find_many(
            where={"institute_id": institute_id}
        )
        
        courses = []
        for course_data in courses_data:
            # Determine course type based on subject type
            course_type = CourseType.THEORY
            if course_data.type == "lab":
                course_type = CourseType.LAB
            elif course_data.type == "project":
                course_type = CourseType.PROJECT
            elif course_data.type == "elective":
                course_type = CourseType.ELECTIVE
            
            course = Course(
                id=course_data.id,
                name=course_data.name,
                course_code=course_data.subject_code,
                course_type=course_type,
                department=course_data.branch or "Unknown",
                semester=course_data.semester or 1,
                credits=course_data.credits or 3,
                hours_per_week=course_data.credits or 3,  # Using credits as hours per week
                is_elective=course_data.type == "elective",
                elective_capacity=60 if course_data.type == "elective" else 0,
                is_nep_compliant=True
            )
            courses.append(course)
        
        logger.info(f"Loaded {len(courses)} courses")
        return courses
        
    except Exception as e:
        logger.error(f"Error loading courses: {str(e)}")
        return []


async def load_faculty_from_db(institute_id: str) -> List[Faculty]:
    """Load faculty from database for a specific institute."""
    try:
        logger.info(f"Loading faculty for institute: {institute_id}")
        
        faculty_data = await db.teacher.find_many(
            where={"institute_id": institute_id}
        )
        
        faculty = []
        for teacher_data in faculty_data:
            # Parse subjects from the subject field (assuming comma-separated)
            subjects = []
            if teacher_data.subject and teacher_data.subject != "__":
                subjects = [s.strip() for s in teacher_data.subject.split(",")]
            
            teacher = Faculty(
                id=teacher_data.p_id,
                name=teacher_data.name if teacher_data.name != "__" else "Unknown",
                email=teacher_data.email,
                department=teacher_data.department if teacher_data.department != "__" else "Unknown",
                designation="Professor",  # Default designation
                subjects=subjects,
                is_available=True
            )
            faculty.append(teacher)
        
        logger.info(f"Loaded {len(faculty)} faculty members")
        return faculty
        
    except Exception as e:
        logger.error(f"Error loading faculty: {str(e)}")
        return []


async def load_rooms_from_db(institute_id: str) -> List[Room]:
    """Load rooms from database for a specific institute."""
    try:
        logger.info(f"Loading rooms for institute: {institute_id}")
        
        rooms_data = await db.classroom.find_many(
            where={"institute_id": institute_id}
        )
        
        rooms = []
        for room_data in rooms_data:
            # Determine room type
            room_type = RoomType.LECTURE
            if room_data.type == "lab":
                room_type = RoomType.LAB
            elif room_data.type == "seminar":
                room_type = RoomType.SEMINAR
            elif room_data.type == "auditorium":
                room_type = RoomType.AUDITORIUM
            
            room = Room(
                id=room_data.id,
                name=room_data.room_id,
                room_type=room_type,
                capacity=room_data.capacity,
                building=room_data.building,
                floor=room_data.floor,
                is_accessible=True
            )
            rooms.append(room)
        
        logger.info(f"Loaded {len(rooms)} rooms")
        return rooms
        
    except Exception as e:
        logger.error(f"Error loading rooms: {str(e)}")
        return []


def load_time_slots_from_config() -> List[TimeSlot]:
    """Load time slots from configuration (not stored in DB)."""
    try:
        logger.info("Loading time slots from configuration")
        
        # Default time slot configuration
        time_slots = []
        slot_id = 1
        
        # Monday to Saturday (1-6)
        for day in range(1, 7):
            # 8 periods per day
            for period in range(1, 9):
                if period == 1:
                    start_time = time(9, 0)  # 9:00 AM
                    end_time = time(9, 50)   # 9:50 AM
                elif period == 2:
                    start_time = time(10, 0)  # 10:00 AM
                    end_time = time(10, 50)   # 10:50 AM
                elif period == 3:
                    start_time = time(11, 0)  # 11:00 AM
                    end_time = time(11, 50)   # 11:50 AM
                elif period == 4:
                    start_time = time(12, 0)  # 12:00 PM
                    end_time = time(12, 50)   # 12:50 PM
                elif period == 5:
                    start_time = time(14, 0)  # 2:00 PM
                    end_time = time(14, 50)   # 2:50 PM
                elif period == 6:
                    start_time = time(15, 0)  # 3:00 PM
                    end_time = time(15, 50)   # 3:50 PM
                elif period == 7:
                    start_time = time(16, 0)  # 4:00 PM
                    end_time = time(16, 50)   # 4:50 PM
                elif period == 8:
                    start_time = time(17, 0)  # 5:00 PM
                    end_time = time(17, 50)   # 5:50 PM
                
                time_slot = TimeSlot(
                    id=slot_id,
                    day=day,
                    period=period,
                    start_time=start_time,
                    end_time=end_time,
                    is_break=(period == 4),  # Lunch break
                    is_lunch=(period == 4)
                )
                time_slots.append(time_slot)
                slot_id += 1
        
        logger.info(f"Loaded {len(time_slots)} time slots")
        return time_slots
        
    except Exception as e:
        logger.error(f"Error loading time slots: {str(e)}")
        return []


async def load_student_preferences_from_db(institute_id: str) -> List[StudentPreference]:
    """Load student preferences from database."""
    try:
        logger.info(f"Loading student preferences for institute: {institute_id}")
        
        # For now, return empty list as preferences are not stored in current schema
        # This would need to be implemented when student preference table is added
        preferences = []
        
        logger.info(f"Loaded {len(preferences)} student preferences")
        return preferences
        
    except Exception as e:
        logger.error(f"Error loading student preferences: {str(e)}")
        return []


async def load_institute_data(institute_id: str) -> Dict[str, Any]:
    """Load all data for an institute."""
    try:
        logger.info(f"Loading complete institute data for: {institute_id}")
        
        # Load all data in parallel
        students, courses, faculty, rooms, preferences = await asyncio.gather(
            load_students_from_db(institute_id),
            load_courses_from_db(institute_id),
            load_faculty_from_db(institute_id),
            load_rooms_from_db(institute_id),
            load_student_preferences_from_db(institute_id)
        )
        
        # Load time slots (synchronous)
        time_slots = load_time_slots_from_config()
        
        # Create departments from students
        departments = create_departments_from_students(students)
        
        data = {
            'students': students,
            'courses': courses,
            'faculty': faculty,
            'rooms': rooms,
            'time_slots': time_slots,
            'preferences': preferences,
            'departments': departments,
            'institute_id': institute_id
        }
        
        logger.info(f"Loaded complete institute data: {len(students)} students, "
                   f"{len(courses)} courses, {len(faculty)} faculty, {len(rooms)} rooms")
        
        return data
        
    except Exception as e:
        logger.error(f"Error loading institute data: {str(e)}")
        return {}


def create_departments_from_students(students: List[Student]) -> List[Department]:
    """Create departments from student data."""
    departments = {}
    
    for student in students:
        dept_name = student.department
        if dept_name not in departments:
            departments[dept_name] = Department(
                id=f"dept_{dept_name.lower()}",
                name=dept_name,
                code=dept_name.upper()[:3],
                max_sections=3
            )
    
    return list(departments.values())


def create_default_optimization_config() -> OptimizationConfig:
    """Create default optimization configuration."""
    return OptimizationConfig(
        max_optimization_time=300,
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

