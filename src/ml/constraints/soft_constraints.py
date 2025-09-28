"""
Soft constraints for the SIH Timetable Optimization System.
These constraints are optimization preferences - violations are penalized but don't make solutions invalid.
"""

from typing import List, Dict, Any, Set, Tuple
from ortools.sat.python import cp_model
from src.utils.logger_config import get_logger

from ..data.models import (
    Student, Course, Faculty, Room, TimeSlot, Assignment,
    Schedule, OptimizationConfig, CourseType
)

logger = get_logger("soft_constraints")


class SoftConstraintManager:
    """Manages all soft constraints for the optimization problem."""
    
    def __init__(self, model: cp_model.CpModel, config: OptimizationConfig):
        self.model = model
        self.config = config
        self.constraints = []
        self.logger = logger
    
    def add_all_constraints(self, 
                          students: List[Student],
                          courses: List[Course], 
                          faculty: List[Faculty],
                          rooms: List[Room],
                          time_slots: List[TimeSlot],
                          assignments: Dict[str, Any]) -> None:
        """Add all soft constraints to the model."""
        self.logger.info("Adding soft constraints to optimization model")
        
        # Add individual constraint types
        self.add_student_satisfaction_constraint(students, courses, assignments)
        self.add_faculty_workload_balance_constraint(faculty, assignments)
        self.add_room_utilization_constraint(rooms, assignments)
        self.add_elective_preference_constraint(students, courses, assignments)
        self.add_nep2020_compliance_constraint(courses, assignments)
        
        self.logger.info(f"Added {len(self.constraints)} soft constraints")
    
    def add_student_satisfaction_constraint(self, 
                                          students: List[Student],
                                          courses: List[Course],
                                          assignments: Dict[str, Any]) -> None:
        """Maximize student satisfaction based on elective preferences."""
        constraint = StudentSatisfactionConstraint(self.model, self.config)
        constraint.add_constraints(students, courses, assignments)
        self.constraints.append(constraint)
    
    def add_faculty_workload_balance_constraint(self, 
                                              faculty: List[Faculty],
                                              assignments: Dict[str, Any]) -> None:
        """Balance faculty workload across time slots and days."""
        constraint = FacultyWorkloadBalanceConstraint(self.model, self.config)
        constraint.add_constraints(faculty, assignments)
        self.constraints.append(constraint)
    
    def add_room_utilization_constraint(self, rooms: List[Room], assignments: Dict[str, Any]) -> None:
        """Maximize room utilization efficiency."""
        constraint = RoomUtilizationConstraint(self.model, self.config)
        constraint.add_constraints(rooms, assignments)
        self.constraints.append(constraint)
    
    def add_elective_preference_constraint(self, 
                                         students: List[Student],
                                         courses: List[Course],
                                         assignments: Dict[str, Any]) -> None:
        """Prioritize elective course preferences."""
        constraint = ElectivePreferenceConstraint(self.model, self.config)
        constraint.add_constraints(students, courses, assignments)
        self.constraints.append(constraint)
    
    def add_nep2020_compliance_constraint(self, courses: List[Course], assignments: Dict[str, Any]) -> None:
        """Ensure NEP 2020 compliance in course scheduling."""
        constraint = NEP2020ComplianceConstraint(self.model, self.config)
        constraint.add_constraints(courses, assignments)
        self.constraints.append(constraint)


class StudentSatisfactionConstraint:
    """Maximizes student satisfaction based on elective preferences."""
    
    def __init__(self, model: cp_model.CpModel, config: OptimizationConfig):
        self.model = model
        self.config = config
        self.logger = logger
    
    def add_constraints(self, 
                       students: List[Student],
                       courses: List[Course],
                       assignments: Dict[str, Any]) -> None:
        """Add student satisfaction constraints."""
        self.logger.info("Adding student satisfaction constraints")
        
        # Create satisfaction variables for each student
        satisfaction_vars = {}
        for student in students:
            satisfaction_vars[student.id] = self.model.NewIntVar(
                0, 100, f"satisfaction_{student.id}"
            )
        
        # Add constraints linking satisfaction to elective assignments
        for student in students:
            satisfaction_terms = []
            
            for preference in student.preferences:
                course_id = preference.course_id
                priority = preference.priority
                preference_score = preference.preference_score
                
                # Find course
                course = next((c for c in courses if c.id == course_id), None)
                if course and course.is_elective:
                    # Create assignment variable for this student-course combination
                    assign_var = f"elective_assign_{student.id}_{course_id}"
                    if assign_var in assignments.get('variables', {}):
                        # Satisfaction increases with higher priority electives
                        satisfaction_terms.append(
                            assignments['variables'][assign_var] * int(preference_score * 100)
                        )
            
            # Student satisfaction is sum of assigned elective scores
            if satisfaction_terms:
                self.model.Add(
                    satisfaction_vars[student.id] == sum(satisfaction_terms)
                )
            else:
                self.model.Add(satisfaction_vars[student.id] == 0)
        
        # Add to objective function
        total_satisfaction = sum(satisfaction_vars.values())
        assignments['satisfaction_vars'] = satisfaction_vars
        assignments['total_satisfaction'] = total_satisfaction


class FacultyWorkloadBalanceConstraint:
    """Balances faculty workload across time slots and days."""
    
    def __init__(self, model: cp_model.CpModel, config: OptimizationConfig):
        self.model = model
        self.config = config
        self.logger = logger
    
    def add_constraints(self, faculty: List[Faculty], assignments: Dict[str, Any]) -> None:
        """Add faculty workload balance constraints."""
        self.logger.info("Adding faculty workload balance constraints")
        
        # Create workload variables for each faculty
        workload_vars = {}
        for teacher in faculty:
            workload_vars[teacher.id] = self.model.NewIntVar(
                0, teacher.max_hours_per_week, f"workload_{teacher.id}"
            )
        
        # Calculate workload for each faculty
        for teacher in faculty:
            workload_terms = []
            
            for course in assignments.get('courses', []):
                if teacher.can_teach_course(course.id):
                    # Count assignments for this faculty-course combination
                    course_assignments = []
                    for slot in assignments.get('time_slots', []):
                        var_name = f"assign_{teacher.id}_{course.id}_{slot.id}"
                        if var_name in assignments.get('variables', {}):
                            course_assignments.append(assignments['variables'][var_name])
                    
                    if course_assignments:
                        # Each assignment counts as 1 hour
                        workload_terms.append(sum(course_assignments))
            
            # Faculty workload is sum of all assignments
            if workload_terms:
                self.model.Add(
                    workload_vars[teacher.id] == sum(workload_terms)
                )
            else:
                self.model.Add(workload_vars[teacher.id] == 0)
        
        # Add workload balance penalty (minimize variance)
        self._add_workload_balance_penalty(faculty, workload_vars)
        
        assignments['workload_vars'] = workload_vars
    
    def _add_workload_balance_penalty(self, 
                                    faculty: List[Faculty], 
                                    workload_vars: Dict[str, Any]) -> None:
        """Add penalty for imbalanced faculty workload."""
        if len(faculty) < 2:
            return
        
        # Calculate average workload
        total_workload = sum(workload_vars.values())
        avg_workload = self.model.NewIntVar(0, 100, "avg_workload")
        self.model.Add(avg_workload * len(faculty) == total_workload)
        
        # Add penalty for deviation from average
        for teacher in faculty:
            deviation = self.model.NewIntVar(0, 100, f"deviation_{teacher.id}")
            self.model.Add(deviation >= workload_vars[teacher.id] - avg_workload)
            self.model.Add(deviation >= avg_workload - workload_vars[teacher.id])


class RoomUtilizationConstraint:
    """Maximizes room utilization efficiency."""
    
    def __init__(self, model: cp_model.CpModel, config: OptimizationConfig):
        self.model = model
        self.config = config
        self.logger = logger
    
    def add_constraints(self, rooms: List[Room], assignments: Dict[str, Any]) -> None:
        """Add room utilization constraints."""
        self.logger.info("Adding room utilization constraints")
        
        # Create utilization variables for each room
        utilization_vars = {}
        for room in rooms:
            utilization_vars[room.id] = self.model.NewIntVar(
                0, 100, f"utilization_{room.id}"
            )
        
        # Calculate utilization for each room
        for room in rooms:
            utilization_terms = []
            
            for course in assignments.get('courses', []):
                if room.is_suitable_for_course(course):
                    # Count assignments for this room-course combination
                    room_assignments = []
                    for slot in assignments.get('time_slots', []):
                        var_name = f"assign_{room.id}_{course.id}_{slot.id}"
                        if var_name in assignments.get('variables', {}):
                            room_assignments.append(assignments['variables'][var_name])
                    
                    if room_assignments:
                        # Utilization increases with more assignments
                        utilization_terms.append(sum(room_assignments))
            
            # Room utilization is sum of all assignments
            if utilization_terms:
                self.model.Add(
                    utilization_vars[room.id] == sum(utilization_terms)
                )
            else:
                self.model.Add(utilization_vars[room.id] == 0)
        
        assignments['utilization_vars'] = utilization_vars


class ElectivePreferenceConstraint:
    """Prioritizes elective course preferences."""
    
    def __init__(self, model: cp_model.CpModel, config: OptimizationConfig):
        self.model = model
        self.config = config
        self.logger = logger
    
    def add_constraints(self, 
                       students: List[Student],
                       courses: List[Course],
                       assignments: Dict[str, Any]) -> None:
        """Add elective preference constraints."""
        self.logger.info("Adding elective preference constraints")
        
        # Prioritize higher preference electives
        for student in students:
            for preference in student.preferences:
                course_id = preference.course_id
                priority = preference.priority
                
                # Find course
                course = next((c for c in courses if c.id == course_id), None)
                if course and course.is_elective:
                    # Higher priority courses get higher weight in objective
                    assign_var = f"elective_assign_{student.id}_{course_id}"
                    if assign_var in assignments.get('variables', {}):
                        # Add to objective with priority weight
                        weight = (6 - priority) * self.config.elective_preference_weight
                        assignments['elective_weights'] = assignments.get('elective_weights', {})
                        assignments['elective_weights'][assign_var] = weight


class NEP2020ComplianceConstraint:
    """Ensures NEP 2020 compliance in course scheduling."""
    
    def __init__(self, model: cp_model.CpModel, config: OptimizationConfig):
        self.model = model
        self.config = config
        self.logger = logger
    
    def add_constraints(self, courses: List[Course], assignments: Dict[str, Any]) -> None:
        """Add NEP 2020 compliance constraints."""
        self.logger.info("Adding NEP 2020 compliance constraints")
        
        # Prioritize NEP-compliant courses
        nep_courses = [c for c in courses if c.is_nep_compliant]
        
        for course in nep_courses:
            # NEP-compliant courses get higher weight
            course_var = f"course_scheduled_{course.id}"
            if course_var in assignments.get('variables', {}):
                weight = self.config.nep_compliance_weight
                assignments['nep_weights'] = assignments.get('nep_weights', {})
                assignments['nep_weights'][course_var] = weight
        
        # Prioritize interdisciplinary courses
        interdisciplinary_courses = [c for c in courses if c.course_type == CourseType.INTERDISCIPLINARY]
        
        for course in interdisciplinary_courses:
            course_var = f"course_scheduled_{course.id}"
            if course_var in assignments.get('variables', {}):
                weight = self.config.interdisciplinary_weight
                assignments['interdisciplinary_weights'] = assignments.get('interdisciplinary_weights', {})
                assignments['interdisciplinary_weights'][course_var] = weight
