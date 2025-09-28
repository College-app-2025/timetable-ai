"""
NEP 2020 compliance constraints for the SIH Timetable Optimization System.
Implements specific constraints for National Education Policy 2020 compliance.
"""

from typing import List, Dict, Any, Set, Tuple
from ortools.sat.python import cp_model
from src.utils.logger_config import get_logger

from ..data.models import (
    Student, Course, Faculty, Room, TimeSlot, Assignment,
    Schedule, CourseType, OptimizationConfig
)

logger = get_logger("nep2020_constraints")


class NEP2020ConstraintManager:
    """Manages NEP 2020 compliance constraints."""
    
    def __init__(self, model: cp_model.CpModel, config: OptimizationConfig):
        self.model = model
        self.config = config
        self.logger = logger
    
    def add_all_constraints(self, 
                          students: List[Student],
                          courses: List[Course], 
                          faculty: List[Faculty],
                          rooms: List[Room],
                          time_slots: List[TimeSlot],
                          assignments: Dict[str, Any]) -> None:
        """Add all NEP 2020 compliance constraints."""
        self.logger.info("Adding NEP 2020 compliance constraints")
        
        # Add individual constraint types
        self.add_multidisciplinary_constraint(courses, assignments)
        self.add_flexibility_constraint(students, courses, assignments)
        self.add_skill_development_constraint(courses, assignments)
        self.add_interdisciplinary_constraint(courses, assignments)
        
        self.logger.info("NEP 2020 constraints added successfully")
    
    def add_multidisciplinary_constraint(self, courses: List[Course], assignments: Dict[str, Any]) -> None:
        """Ensure multidisciplinary course availability."""
        try:
            # Count multidisciplinary courses
            multidisciplinary_courses = [
                c for c in courses if c.course_type == CourseType.INTERDISCIPLINARY
            ]
            
            if not multidisciplinary_courses:
                self.logger.warning("No multidisciplinary courses found")
                return
            
            # Ensure at least 30% of courses are multidisciplinary
            total_courses = len(courses)
            min_multidisciplinary = int(total_courses * 0.3)
            
            multidisciplinary_vars = []
            for course in multidisciplinary_courses:
                course_var = f"course_scheduled_{course.id}"
                if course_var in assignments.get('variables', {}):
                    multidisciplinary_vars.append(assignments['variables'][course_var])
            
            if multidisciplinary_vars:
                self.model.Add(sum(multidisciplinary_vars) >= min_multidisciplinary)
                self.logger.info(f"Added multidisciplinary constraint: min {min_multidisciplinary} courses")
            
        except Exception as e:
            self.logger.error(f"Error adding multidisciplinary constraint: {str(e)}")
    
    def add_flexibility_constraint(self, students: List[Student], courses: List[Course], assignments: Dict[str, Any]) -> None:
        """Ensure flexible course scheduling for student choice."""
        try:
            # Ensure elective courses are available across different time slots
            elective_courses = [c for c in courses if c.is_elective]
            
            if not elective_courses:
                self.logger.warning("No elective courses found")
                return
            
            # For each elective course, ensure it's scheduled in multiple time slots
            for course in elective_courses:
                course_assignments = []
                for slot in assignments.get('time_slots', []):
                    var_name = f"elective_schedule_{course.id}_{slot['id']}"
                    if var_name in assignments.get('variables', {}):
                        course_assignments.append(assignments['variables'][var_name])
                
                # At least one time slot per elective course
                if course_assignments:
                    self.model.Add(sum(course_assignments) >= 1)
            
            self.logger.info(f"Added flexibility constraint for {len(elective_courses)} elective courses")
            
        except Exception as e:
            self.logger.error(f"Error adding flexibility constraint: {str(e)}")
    
    def add_skill_development_constraint(self, courses: List[Course], assignments: Dict[str, Any]) -> None:
        """Ensure skill development courses are prioritized."""
        try:
            # Identify skill development courses (lab, project courses)
            skill_courses = [
                c for c in courses 
                if c.course_type in [CourseType.LAB, CourseType.PROJECT]
            ]
            
            if not skill_courses:
                self.logger.warning("No skill development courses found")
                return
            
            # Prioritize skill development courses in scheduling
            for course in skill_courses:
                course_var = f"course_scheduled_{course.id}"
                if course_var in assignments.get('variables', {}):
                    # Add weight to objective function
                    weight = self.config.interdisciplinary_weight * 1.2  # Higher weight for skill courses
                    assignments['skill_weights'] = assignments.get('skill_weights', {})
                    assignments['skill_weights'][course_var] = weight
            
            self.logger.info(f"Added skill development constraint for {len(skill_courses)} courses")
            
        except Exception as e:
            self.logger.error(f"Error adding skill development constraint: {str(e)}")
    
    def add_interdisciplinary_constraint(self, courses: List[Course], assignments: Dict[str, Any]) -> None:
        """Ensure interdisciplinary course scheduling."""
        try:
            # Group courses by department
            dept_courses = {}
            for course in courses:
                dept = course.department
                if dept not in dept_courses:
                    dept_courses[dept] = []
                dept_courses[dept].append(course)
            
            # Ensure cross-departmental course availability
            departments = list(dept_courses.keys())
            if len(departments) < 2:
                self.logger.warning("Need at least 2 departments for interdisciplinary constraint")
                return
            
            # For each department, ensure some courses are available to other departments
            for dept in departments:
                dept_course_vars = []
                for course in dept_courses[dept]:
                    course_var = f"course_scheduled_{course.id}"
                    if course_var in assignments.get('variables', {}):
                        dept_course_vars.append(assignments['variables'][course_var])
                
                # At least 20% of department courses should be available
                min_courses = max(1, len(dept_course_vars) // 5)
                if dept_course_vars:
                    self.model.Add(sum(dept_course_vars) >= min_courses)
            
            self.logger.info(f"Added interdisciplinary constraint for {len(departments)} departments")
            
        except Exception as e:
            self.logger.error(f"Error adding interdisciplinary constraint: {str(e)}")


class MultidisciplinaryConstraint:
    """Ensures multidisciplinary course availability."""
    
    def __init__(self, model: cp_model.CpModel, config: OptimizationConfig):
        self.model = model
        self.config = config
        self.logger = logger
    
    def add_constraints(self, courses: List[Course], assignments: Dict[str, Any]) -> None:
        """Add multidisciplinary constraints."""
        try:
            # Ensure minimum ratio of multidisciplinary courses
            total_courses = len(courses)
            multidisciplinary_courses = [
                c for c in courses if c.course_type == CourseType.INTERDISCIPLINARY
            ]
            
            if total_courses > 0:
                min_ratio = 0.3  # 30% minimum
                min_count = int(total_courses * min_ratio)
                
                multidisciplinary_vars = []
                for course in multidisciplinary_courses:
                    course_var = f"course_scheduled_{course.id}"
                    if course_var in assignments.get('variables', {}):
                        multidisciplinary_vars.append(assignments['variables'][course_var])
                
                if multidisciplinary_vars and len(multidisciplinary_vars) >= min_count:
                    self.model.Add(sum(multidisciplinary_vars) >= min_count)
                    self.logger.info(f"Added multidisciplinary constraint: min {min_count} courses")
            
        except Exception as e:
            self.logger.error(f"Error adding multidisciplinary constraints: {str(e)}")


class FlexibilityConstraint:
    """Ensures flexible course scheduling."""
    
    def __init__(self, model: cp_model.CpModel, config: OptimizationConfig):
        self.model = model
        self.config = config
        self.logger = logger
    
    def add_constraints(self, students: List[Student], courses: List[Course], assignments: Dict[str, Any]) -> None:
        """Add flexibility constraints."""
        try:
            # Ensure elective courses have multiple time slot options
            elective_courses = [c for c in courses if c.is_elective]
            
            for course in elective_courses:
                # Ensure course is scheduled in at least one time slot
                course_scheduled_var = f"course_scheduled_{course.id}"
                if course_scheduled_var in assignments.get('variables', {}):
                    # Course must be scheduled
                    self.model.Add(assignments['variables'][course_scheduled_var] == 1)
            
            self.logger.info(f"Added flexibility constraints for {len(elective_courses)} elective courses")
            
        except Exception as e:
            self.logger.error(f"Error adding flexibility constraints: {str(e)}")


class SkillDevelopmentConstraint:
    """Ensures skill development course prioritization."""
    
    def __init__(self, model: cp_model.CpModel, config: OptimizationConfig):
        self.model = model
        self.config = config
        self.logger = logger
    
    def add_constraints(self, courses: List[Course], assignments: Dict[str, Any]) -> None:
        """Add skill development constraints."""
        try:
            # Prioritize lab and project courses
            skill_courses = [
                c for c in courses 
                if c.course_type in [CourseType.LAB, CourseType.PROJECT]
            ]
            
            for course in skill_courses:
                course_var = f"course_scheduled_{course.id}"
                if course_var in assignments.get('variables', {}):
                    # Add higher weight to objective
                    weight = self.config.skill_development_weight if hasattr(self.config, 'skill_development_weight') else 1.2
                    assignments['skill_weights'] = assignments.get('skill_weights', {})
                    assignments['skill_weights'][course_var] = weight
            
            self.logger.info(f"Added skill development constraints for {len(skill_courses)} courses")
            
        except Exception as e:
            self.logger.error(f"Error adding skill development constraints: {str(e)}")

