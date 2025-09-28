"""
Hard constraints for the SIH Timetable Optimization System.
These constraints MUST be satisfied for a valid solution.
"""

from typing import List, Dict, Any, Set, Tuple
from ortools.sat.python import cp_model
from src.utils.logger_config import get_logger

from ..data.models import (
    Student, Course, Faculty, Room, TimeSlot, Assignment,
    Schedule, CourseType
)

logger = get_logger("hard_constraints")


class HardConstraintManager:
    """Manages all hard constraints for the optimization problem."""
    
    def __init__(self, model: cp_model.CpModel):
        self.model = model
        self.constraints = []
        self.logger = logger
    
    def add_all_constraints(self, 
                          students: List[Student],
                          courses: List[Course], 
                          faculty: List[Faculty],
                          rooms: List[Room],
                          time_slots: List[TimeSlot],
                          assignments: Dict[str, Any]) -> None:
        """Add all hard constraints to the model."""
        self.logger.info("Adding hard constraints to optimization model")
        
        # Add individual constraint types
        self.add_no_conflict_constraint(students, courses, faculty, rooms, time_slots, assignments)
        self.add_capacity_constraint(rooms, assignments)
        self.add_faculty_availability_constraint(faculty, time_slots, assignments)
        self.add_room_availability_constraint(rooms, time_slots, assignments)
        self.add_prerequisite_constraint(courses, assignments)
        
        self.logger.info(f"Added {len(self.constraints)} hard constraints")
    
    def add_no_conflict_constraint(self, 
                                 students: List[Student],
                                 courses: List[Course],
                                 faculty: List[Faculty], 
                                 rooms: List[Room],
                                 time_slots: List[TimeSlot],
                                 assignments: Dict[str, Any]) -> None:
        """Ensure no conflicts in assignments."""
        constraint = NoConflictConstraint(self.model)
        constraint.add_constraints(students, courses, faculty, rooms, time_slots, assignments)
        self.constraints.append(constraint)
    
    def add_capacity_constraint(self, rooms: List[Room], assignments: Dict[str, Any]) -> None:
        """Ensure room capacity is not exceeded."""
        constraint = CapacityConstraint(self.model)
        constraint.add_constraints(rooms, assignments)
        self.constraints.append(constraint)
    
    def add_faculty_availability_constraint(self, 
                                          faculty: List[Faculty],
                                          time_slots: List[TimeSlot],
                                          assignments: Dict[str, Any]) -> None:
        """Ensure faculty are only assigned during available time slots."""
        constraint = FacultyAvailabilityConstraint(self.model)
        constraint.add_constraints(faculty, time_slots, assignments)
        self.constraints.append(constraint)
    
    def add_room_availability_constraint(self, 
                                       rooms: List[Room],
                                       time_slots: List[TimeSlot],
                                       assignments: Dict[str, Any]) -> None:
        """Ensure rooms are only used during available time slots."""
        constraint = RoomAvailabilityConstraint(self.model)
        constraint.add_constraints(rooms, time_slots, assignments)
        self.constraints.append(constraint)
    
    def add_prerequisite_constraint(self, courses: List[Course], assignments: Dict[str, Any]) -> None:
        """Ensure prerequisite courses are scheduled before dependent courses."""
        constraint = PrerequisiteConstraint(self.model)
        constraint.add_constraints(courses, assignments)
        self.constraints.append(constraint)


class NoConflictConstraint:
    """Ensures no conflicts in timetable assignments."""
    
    def __init__(self, model: cp_model.CpModel):
        self.model = model
        self.logger = logger
    
    def add_constraints(self, 
                       students: List[Student],
                       courses: List[Course],
                       faculty: List[Faculty],
                       rooms: List[Room],
                       time_slots: List[TimeSlot],
                       assignments: Dict[str, Any]) -> None:
        """Add no-conflict constraints."""
        self.logger.info("Adding no-conflict constraints")
        
        # 1. No faculty can teach two classes at the same time
        self._add_faculty_no_conflict_constraint(faculty, time_slots, assignments)
        
        # 2. No student can attend two classes at the same time
        self._add_student_no_conflict_constraint(students, time_slots, assignments)
        
        # 3. No room can host two classes at the same time
        self._add_room_no_conflict_constraint(rooms, time_slots, assignments)
    
    def _add_faculty_no_conflict_constraint(self, 
                                          faculty: List[Faculty],
                                          time_slots: List[TimeSlot],
                                          assignments: Dict[str, Any]) -> None:
        """Ensure faculty don't have conflicting assignments."""
        for teacher in faculty:
            for slot in time_slots:
                # Get all possible assignments for this faculty at this time slot
                faculty_assignments = []
                for course in assignments.get('courses', []):
                    if teacher.can_teach_course(course.id):
                        var_name = f"assign_{teacher.id}_{course.id}_{slot.id}"
                        if var_name in assignments.get('variables', {}):
                            faculty_assignments.append(assignments['variables'][var_name])
                
                # At most one assignment per faculty per time slot
                if len(faculty_assignments) > 1:
                    self.model.Add(sum(faculty_assignments) <= 1)
    
    def _add_student_no_conflict_constraint(self, 
                                          students: List[Student],
                                          time_slots: List[TimeSlot],
                                          assignments: Dict[str, Any]) -> None:
        """Ensure students don't have conflicting assignments."""
        for student in students:
            for slot in time_slots:
                # Get all possible assignments for this student at this time slot
                student_assignments = []
                for course in assignments.get('courses', []):
                    if course.id in [pref.course_id for pref in student.preferences]:
                        var_name = f"assign_{student.id}_{course.id}_{slot.id}"
                        if var_name in assignments.get('variables', {}):
                            student_assignments.append(assignments['variables'][var_name])
                
                # At most one assignment per student per time slot
                if len(student_assignments) > 1:
                    self.model.Add(sum(student_assignments) <= 1)
    
    def _add_room_no_conflict_constraint(self, 
                                       rooms: List[Room],
                                       time_slots: List[TimeSlot],
                                       assignments: Dict[str, Any]) -> None:
        """Ensure rooms don't have conflicting assignments."""
        for room in rooms:
            for slot in time_slots:
                # Get all possible assignments for this room at this time slot
                room_assignments = []
                for course in assignments.get('courses', []):
                    if room.is_suitable_for_course(course):
                        var_name = f"assign_{room.id}_{course.id}_{slot.id}"
                        if var_name in assignments.get('variables', {}):
                            room_assignments.append(assignments['variables'][var_name])
                
                # At most one assignment per room per time slot
                if len(room_assignments) > 1:
                    self.model.Add(sum(room_assignments) <= 1)


class CapacityConstraint:
    """Ensures room capacity is not exceeded."""
    
    def __init__(self, model: cp_model.CpModel):
        self.model = model
        self.logger = logger
    
    def add_constraints(self, rooms: List[Room], assignments: Dict[str, Any]) -> None:
        """Add capacity constraints."""
        self.logger.info("Adding capacity constraints")
        
        for room in rooms:
            for course in assignments.get('courses', []):
                # Get student count for this course
                student_count = course.max_students_per_section
                
                # Create constraint: if room is used, it must have enough capacity
                var_name = f"assign_{room.id}_{course.id}"
                if var_name in assignments.get('variables', {}):
                    room_var = assignments['variables'][var_name]
                    # If room is assigned, capacity must be sufficient
                    self.model.Add(room_var * student_count <= room.capacity)


class FacultyAvailabilityConstraint:
    """Ensures faculty are only assigned during available time slots."""
    
    def __init__(self, model: cp_model.CpModel):
        self.model = model
        self.logger = logger
    
    def add_constraints(self, 
                       faculty: List[Faculty],
                       time_slots: List[TimeSlot],
                       assignments: Dict[str, Any]) -> None:
        """Add faculty availability constraints."""
        self.logger.info("Adding faculty availability constraints")
        
        for teacher in faculty:
            for slot in time_slots:
                # Check if faculty is available at this time slot
                if not teacher.is_available_at_slot(slot.id):
                    # If not available, set all assignments for this faculty at this slot to 0
                    for course in assignments.get('courses', []):
                        if teacher.can_teach_course(course.id):
                            var_name = f"assign_{teacher.id}_{course.id}_{slot.id}"
                            if var_name in assignments.get('variables', {}):
                                self.model.Add(assignments['variables'][var_name] == 0)


class RoomAvailabilityConstraint:
    """Ensures rooms are only used during available time slots."""
    
    def __init__(self, model: cp_model.CpModel):
        self.model = model
        self.logger = logger
    
    def add_constraints(self, 
                       rooms: List[Room],
                       time_slots: List[TimeSlot],
                       assignments: Dict[str, Any]) -> None:
        """Add room availability constraints."""
        self.logger.info("Adding room availability constraints")
        
        for room in rooms:
            for slot in time_slots:
                # Check if room is available at this time slot
                if slot.id not in room.available_slots and room.available_slots:
                    # If not available, set all assignments for this room at this slot to 0
                    for course in assignments.get('courses', []):
                        if room.is_suitable_for_course(course):
                            var_name = f"assign_{room.id}_{course.id}_{slot.id}"
                            if var_name in assignments.get('variables', {}):
                                self.model.Add(assignments['variables'][var_name] == 0)


class PrerequisiteConstraint:
    """Ensures prerequisite courses are scheduled before dependent courses."""
    
    def __init__(self, model: cp_model.CpModel):
        self.model = model
        self.logger = logger
    
    def add_constraints(self, courses: List[Course], assignments: Dict[str, Any]) -> None:
        """Add prerequisite constraints."""
        self.logger.info("Adding prerequisite constraints")
        
        for course in courses:
            if course.prerequisites:
                for prereq_id in course.prerequisites:
                    # Find prerequisite course
                    prereq_course = next((c for c in courses if c.id == prereq_id), None)
                    if prereq_course:
                        # Ensure prerequisite is scheduled before dependent course
                        self._add_prerequisite_timing_constraint(prereq_course, course, assignments)
    
    def _add_prerequisite_timing_constraint(self, 
                                          prereq_course: Course,
                                          dependent_course: Course,
                                          assignments: Dict[str, Any]) -> None:
        """Add timing constraint between prerequisite and dependent course."""
        # This is a simplified implementation
        # In practice, you'd need to ensure prerequisite is scheduled in an earlier time slot
        # For now, we'll just ensure both courses are scheduled
        prereq_var = f"course_scheduled_{prereq_course.id}"
        dependent_var = f"course_scheduled_{dependent_course.id}"
        
        if prereq_var in assignments.get('variables', {}) and dependent_var in assignments.get('variables', {}):
            # If dependent course is scheduled, prerequisite must also be scheduled
            self.model.Add(assignments['variables'][dependent_var] <= assignments['variables'][prereq_var])
