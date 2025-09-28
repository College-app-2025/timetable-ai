"""
Timetable builder for the SIH Timetable Optimization System.
Constructs final timetables from optimization results.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from src.utils.logger_config import get_logger

from ..data.models import (
    Student, Course, Faculty, Room, TimeSlot, Assignment,
    Schedule, CourseType
)

logger = get_logger("timetable_builder")


class TimetableBuilder:
    """Builds final timetables from optimization results."""
    
    def __init__(self):
        self.logger = logger
    
    def build_schedule(self, 
                      assignments: List[Assignment],
                      institute_id: str,
                      semester: int) -> Schedule:
        """Build a complete schedule from assignments."""
        try:
            self.logger.info(f"Building schedule for institute {institute_id}, semester {semester}")
            
            # Create schedule
            schedule = Schedule(
                id=f"schedule_{institute_id}_{semester}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                institute_id=institute_id,
                semester=semester,
                is_optimized=True,
                optimization_score=0.0
            )
            
            # Add assignments to schedule
            for assignment in assignments:
                schedule.add_assignment(assignment)
            
            # Calculate optimization score
            schedule.optimization_score = self._calculate_optimization_score(schedule)
            
            self.logger.info(f"Schedule built with {len(schedule.assignments)} assignments")
            return schedule
            
        except Exception as e:
            self.logger.error(f"Error building schedule: {str(e)}")
            raise
    
    def _calculate_optimization_score(self, schedule: Schedule) -> float:
        """Calculate optimization score for the schedule."""
        try:
            if not schedule.assignments:
                return 0.0
            
            # Base score from number of assignments
            base_score = len(schedule.assignments) * 10
            
            # Bonus for elective assignments
            elective_count = sum(1 for a in schedule.assignments if a.is_elective)
            elective_bonus = elective_count * 5
            
            # Penalty for potential conflicts (simplified)
            conflict_penalty = self._calculate_conflict_penalty(schedule)
            
            total_score = base_score + elective_bonus - conflict_penalty
            return max(0, total_score)
            
        except Exception as e:
            self.logger.error(f"Error calculating optimization score: {str(e)}")
            return 0.0
    
    def _calculate_conflict_penalty(self, schedule: Schedule) -> float:
        """Calculate penalty for potential conflicts."""
        try:
            conflicts = 0
            
            # Check for faculty conflicts
            faculty_assignments = {}
            for assignment in schedule.assignments:
                key = f"{assignment.faculty_id}_{assignment.time_slot_id}"
                if key in faculty_assignments:
                    conflicts += 1
                else:
                    faculty_assignments[key] = assignment
            
            # Check for room conflicts
            room_assignments = {}
            for assignment in schedule.assignments:
                key = f"{assignment.room_id}_{assignment.time_slot_id}"
                if key in room_assignments:
                    conflicts += 1
                else:
                    room_assignments[key] = assignment
            
            return conflicts * 20  # 20 points penalty per conflict
            
        except Exception as e:
            self.logger.error(f"Error calculating conflict penalty: {str(e)}")
            return 0.0
    
    def build_student_timetable(self, 
                              schedule: Schedule,
                              student: Student) -> Dict[str, Any]:
        """Build timetable for a specific student."""
        try:
            student_assignments = []
            
            # Find assignments relevant to this student
            for assignment in schedule.assignments:
                # Check if this assignment is for a course the student is taking
                if assignment.course_id in [pref.course_id for pref in student.preferences]:
                    student_assignments.append(assignment)
            
            # Sort by time slot
            student_assignments.sort(key=lambda x: x.time_slot_id)
            
            # Build timetable structure
            timetable = {
                "student_id": student.id,
                "student_name": student.name,
                "department": student.department,
                "semester": student.semester,
                "assignments": []
            }
            
            for assignment in student_assignments:
                assignment_info = {
                    "course_id": assignment.course_id,
                    "faculty_id": assignment.faculty_id,
                    "room_id": assignment.room_id,
                    "time_slot_id": assignment.time_slot_id,
                    "section_id": assignment.section_id,
                    "is_elective": assignment.is_elective
                }
                timetable["assignments"].append(assignment_info)
            
            return timetable
            
        except Exception as e:
            self.logger.error(f"Error building student timetable: {str(e)}")
            return {}
    
    def build_faculty_timetable(self, 
                              schedule: Schedule,
                              faculty: Faculty) -> Dict[str, Any]:
        """Build timetable for a specific faculty member."""
        try:
            faculty_assignments = schedule.get_assignments_for_faculty(faculty.id)
            
            # Sort by time slot
            faculty_assignments.sort(key=lambda x: x.time_slot_id)
            
            # Build timetable structure
            timetable = {
                "faculty_id": faculty.id,
                "faculty_name": faculty.name,
                "department": faculty.department,
                "assignments": []
            }
            
            for assignment in faculty_assignments:
                assignment_info = {
                    "course_id": assignment.course_id,
                    "room_id": assignment.room_id,
                    "time_slot_id": assignment.time_slot_id,
                    "section_id": assignment.section_id,
                    "student_count": assignment.student_count,
                    "is_elective": assignment.is_elective
                }
                timetable["assignments"].append(assignment_info)
            
            return timetable
            
        except Exception as e:
            self.logger.error(f"Error building faculty timetable: {str(e)}")
            return {}
    
    def build_room_timetable(self, 
                           schedule: Schedule,
                           room: Room) -> Dict[str, Any]:
        """Build timetable for a specific room."""
        try:
            room_assignments = schedule.get_assignments_for_room(room.id)
            
            # Sort by time slot
            room_assignments.sort(key=lambda x: x.time_slot_id)
            
            # Build timetable structure
            timetable = {
                "room_id": room.id,
                "room_name": room.name,
                "room_type": room.room_type.value,
                "capacity": room.capacity,
                "building": room.building,
                "floor": room.floor,
                "assignments": []
            }
            
            for assignment in room_assignments:
                assignment_info = {
                    "course_id": assignment.course_id,
                    "faculty_id": assignment.faculty_id,
                    "time_slot_id": assignment.time_slot_id,
                    "section_id": assignment.section_id,
                    "student_count": assignment.student_count,
                    "is_elective": assignment.is_elective
                }
                timetable["assignments"].append(assignment_info)
            
            return timetable
            
        except Exception as e:
            self.logger.error(f"Error building room timetable: {str(e)}")
            return {}
    
    def build_department_timetable(self, 
                                 schedule: Schedule,
                                 department: str) -> Dict[str, Any]:
        """Build timetable for a specific department."""
        try:
            department_assignments = []
            
            # Find assignments for this department
            for assignment in schedule.assignments:
                # This would need to be enhanced based on how department info is stored
                if assignment.section_id and department.lower() in assignment.section_id.lower():
                    department_assignments.append(assignment)
            
            # Sort by time slot
            department_assignments.sort(key=lambda x: x.time_slot_id)
            
            # Build timetable structure
            timetable = {
                "department": department,
                "assignments": []
            }
            
            for assignment in department_assignments:
                assignment_info = {
                    "course_id": assignment.course_id,
                    "faculty_id": assignment.faculty_id,
                    "room_id": assignment.room_id,
                    "time_slot_id": assignment.time_slot_id,
                    "section_id": assignment.section_id,
                    "student_count": assignment.student_count,
                    "is_elective": assignment.is_elective
                }
                timetable["assignments"].append(assignment_info)
            
            return timetable
            
        except Exception as e:
            self.logger.error(f"Error building department timetable: {str(e)}")
            return {}
    
    def generate_timetable_summary(self, schedule: Schedule) -> Dict[str, Any]:
        """Generate a summary of the timetable."""
        try:
            total_assignments = len(schedule.assignments)
            elective_assignments = sum(1 for a in schedule.assignments if a.is_elective)
            theory_assignments = total_assignments - elective_assignments
            
            # Count unique courses, faculty, rooms
            unique_courses = len(set(a.course_id for a in schedule.assignments))
            unique_faculty = len(set(a.faculty_id for a in schedule.assignments))
            unique_rooms = len(set(a.room_id for a in schedule.assignments))
            
            # Count time slots used
            time_slots_used = len(set(a.time_slot_id for a in schedule.assignments))
            
            return {
                "total_assignments": total_assignments,
                "elective_assignments": elective_assignments,
                "theory_assignments": theory_assignments,
                "unique_courses": unique_courses,
                "unique_faculty": unique_faculty,
                "unique_rooms": unique_rooms,
                "time_slots_used": time_slots_used,
                "optimization_score": schedule.optimization_score,
                "is_optimized": schedule.is_optimized,
                "created_at": schedule.created_at.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating timetable summary: {str(e)}")
            return {}

