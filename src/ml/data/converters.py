"""
Data converters for converting between different data formats.
Converts between database models, API schemas, and ML domain models.
"""

from typing import List, Dict, Any
from datetime import datetime, time
from src.ml.data.models import (
    Student, Course, Faculty, Room, TimeSlot, StudentPreference,
    CourseType, RoomType, Section, Department
)

def convert_dict_to_student(data: Dict[str, Any]) -> Student:
    """Convert dictionary to Student dataclass."""
    return Student(
        id=data["id"],
        student_id=data["student_id"],
        name=data["name"],
        email=data["email"],
        department=data["department"],
        semester=data["semester"],
        section=data["section"],
        satisfaction_score=data.get("satisfaction_score", 0.8),
        preferences=[]  # Will be populated separately if needed
    )

def convert_dict_to_course(data: Dict[str, Any]) -> Course:
    """Convert dictionary to Course dataclass."""
    return Course(
        id=data["id"],
        course_code=data["course_code"],
        name=data["name"],
        department=data["department"],
        semester=data["semester"],
        credits=data["credits"],
        hours_per_week=data["hours_per_week"],
        course_type=CourseType(data["course_type"]) if isinstance(data["course_type"], str) else data["course_type"],
        is_elective=data.get("is_elective", False),
        max_students_per_section=data["max_students_per_section"],
        prerequisites=data.get("prerequisites", [])
    )

def convert_dict_to_faculty(data: Dict[str, Any]) -> Faculty:
    """Convert dictionary to Faculty dataclass."""
    return Faculty(
        id=data["id"],
        name=data["name"],
        email=data["email"],
        department=data["department"],
        designation=data.get("designation", "Professor"),
        subjects=data.get("subjects", []),
        max_hours_per_week=data.get("max_hours_per_week", 20),
        availability=data.get("availability", {})
    )

def convert_dict_to_room(data: Dict[str, Any]) -> Room:
    """Convert dictionary to Room dataclass."""
    return Room(
        id=data["id"],
        name=data["name"],
        room_type=RoomType(data["room_type"]) if isinstance(data["room_type"], str) else data["room_type"],
        capacity=data["capacity"],
        building=data.get("building", "Unknown"),
        floor=data.get("floor", 1),
        equipment=data.get("equipment", [])
    )

def convert_dict_to_time_slot(data: Dict[str, Any]) -> TimeSlot:
    """Convert dictionary to TimeSlot dataclass."""
    # Handle time string conversion
    start_time_str = data["start_time"]
    end_time_str = data["end_time"]
    
    if isinstance(start_time_str, str):
        start_time = datetime.strptime(start_time_str, "%H:%M:%S").time()
    else:
        start_time = start_time_str
        
    if isinstance(end_time_str, str):
        end_time = datetime.strptime(end_time_str, "%H:%M:%S").time()
    else:
        end_time = end_time_str
    
    return TimeSlot(
        id=data["id"],
        day=data["day"],
        period=data["period"],
        start_time=start_time,
        end_time=end_time
    )

def convert_dict_to_student_preference(data: Dict[str, Any]) -> StudentPreference:
    """Convert dictionary to StudentPreference dataclass."""
    return StudentPreference(
        student_id=data["student_id"],
        course_id=data["course_id"],
        priority=data.get("priority", 1),
        preferred_time_slots=data.get("preferred_time_slots", []),
        preferred_rooms=data.get("preferred_rooms", [])
    )

def convert_data_to_ml_models(data: Dict[str, Any]) -> Dict[str, List[Any]]:
    """Convert raw data dictionary to ML domain models."""
    try:
        # Convert students
        students = [convert_dict_to_student(student_data) for student_data in data.get("students", [])]
        
        # Convert courses
        courses = [convert_dict_to_course(course_data) for course_data in data.get("courses", [])]
        
        # Convert faculty
        faculty = [convert_dict_to_faculty(faculty_data) for faculty_data in data.get("faculty", [])]
        
        # Convert rooms
        rooms = [convert_dict_to_room(room_data) for room_data in data.get("rooms", [])]
        
        # Convert time slots
        time_slots = [convert_dict_to_time_slot(slot_data) for slot_data in data.get("time_slots", [])]
        
        # Convert student preferences
        student_preferences = [
            convert_dict_to_student_preference(pref_data) 
            for pref_data in data.get("student_preferences", [])
        ]
        
        return {
            "students": students,
            "courses": courses,
            "faculty": faculty,
            "rooms": rooms,
            "time_slots": time_slots,
            "student_preferences": student_preferences
        }
        
    except Exception as e:
        raise ValueError(f"Error converting data to ML models: {str(e)}")

def convert_ml_models_to_dict(ml_data: Dict[str, List[Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Convert ML domain models back to dictionary format."""
    try:
        result = {}
        
        # Convert students
        if "students" in ml_data:
            result["students"] = [student.to_dict() for student in ml_data["students"]]
        
        # Convert courses
        if "courses" in ml_data:
            result["courses"] = [course.to_dict() for course in ml_data["courses"]]
        
        # Convert faculty
        if "faculty" in ml_data:
            result["faculty"] = [faculty.to_dict() for faculty in ml_data["faculty"]]
        
        # Convert rooms
        if "rooms" in ml_data:
            result["rooms"] = [room.to_dict() for room in ml_data["rooms"]]
        
        # Convert time slots
        if "time_slots" in ml_data:
            result["time_slots"] = [slot.to_dict() for slot in ml_data["time_slots"]]
        
        # Convert student preferences
        if "student_preferences" in ml_data:
            result["student_preferences"] = [pref.to_dict() for pref in ml_data["student_preferences"]]
        
        return result
        
    except Exception as e:
        raise ValueError(f"Error converting ML models to dictionary: {str(e)}")

