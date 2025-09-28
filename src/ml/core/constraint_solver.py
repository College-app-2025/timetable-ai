"""
Constraint solver for the SIH Timetable Optimization System.
Integrates hard and soft constraints using Google OR-Tools CP-SAT.
"""

from typing import List, Dict, Any
from ortools.sat.python import cp_model
from src.utils.logger_config import get_logger

from ..data.models import (
    Student, Course, Faculty, Room, TimeSlot, Assignment,
    OptimizationConfig
)
from ..constraints.hard_constraints import HardConstraintManager
from ..constraints.soft_constraints import SoftConstraintManager

logger = get_logger("constraint_solver")


class ConstraintSolver:
    """Main constraint solver using Google OR-Tools CP-SAT."""
    
    def __init__(self, config: OptimizationConfig):
        self.config = config
        self.logger = logger
        self.model = None
        self.hard_constraint_manager = None
        self.soft_constraint_manager = None
    
    def add_all_constraints(self, 
                          students: List[Student],
                          courses: List[Course], 
                          faculty: List[Faculty],
                          rooms: List[Room],
                          time_slots: List[TimeSlot],
                          variables: Dict[str, Any]) -> None:
        """Add all constraints to the optimization model."""
        try:
            self.logger.info("Adding all constraints to optimization model")
            
            # Get the model from variables
            self.model = variables.get('model')
            if not self.model:
                raise ValueError("Model not found in variables")
            
            # Initialize constraint managers
            self.hard_constraint_manager = HardConstraintManager(self.model)
            self.soft_constraint_manager = SoftConstraintManager(self.model, self.config)
            
            # Add hard constraints (must satisfy)
            self.logger.info("Adding hard constraints")
            self.hard_constraint_manager.add_all_constraints(
                students, courses, faculty, rooms, time_slots, variables
            )
            
            # Add soft constraints (optimization preferences)
            self.logger.info("Adding soft constraints")
            self.soft_constraint_manager.add_all_constraints(
                students, courses, faculty, rooms, time_slots, variables
            )
            
            self.logger.info("All constraints added successfully")
            
        except Exception as e:
            self.logger.error(f"Error adding constraints: {str(e)}")
            raise
    
    def solve(self, time_limit: int = 300) -> Dict[str, Any]:
        """Solve the constraint satisfaction problem."""
        try:
            if not self.model:
                raise ValueError("Model not initialized")
            
            self.logger.info(f"Starting constraint solver with time limit: {time_limit}s")
            
            # Create solver
            solver = cp_model.CpSolver()
            solver.parameters.max_time_in_seconds = time_limit
            
            # Solve
            status = solver.Solve(self.model)
            
            result = {
                "status": status,
                "is_optimal": status == cp_model.OPTIMAL,
                "is_feasible": status == cp_model.FEASIBLE or status == cp_model.OPTIMAL,
                "solver": solver
            }
            
            if status == cp_model.OPTIMAL:
                self.logger.info("Optimal solution found")
                result["message"] = "Optimal solution found"
            elif status == cp_model.FEASIBLE:
                self.logger.info("Feasible solution found")
                result["message"] = "Feasible solution found"
            else:
                self.logger.warning(f"No solution found. Status: {status}")
                result["message"] = f"No solution found. Status: {status}"
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error solving constraints: {str(e)}")
            return {
                "status": cp_model.UNKNOWN,
                "is_optimal": False,
                "is_feasible": False,
                "error": str(e)
            }
    
    def get_solution_value(self, solver: cp_model.CpSolver, variable) -> int:
        """Get solution value for a variable."""
        try:
            return solver.Value(variable)
        except Exception as e:
            self.logger.error(f"Error getting solution value: {str(e)}")
            return 0
    
    def get_solution_statistics(self, solver: cp_model.CpSolver) -> Dict[str, Any]:
        """Get solution statistics."""
        try:
            return {
                "wall_time": solver.WallTime(),
                "branches": solver.NumBranches(),
                "conflicts": solver.NumConflicts(),
                "objective_value": solver.ObjectiveValue() if solver.ObjectiveValue() else 0
            }
        except Exception as e:
            self.logger.error(f"Error getting solution statistics: {str(e)}")
            return {}
    
    def validate_solution(self, 
                         solver: cp_model.CpSolver,
                         variables: Dict[str, Any],
                         students: List[Student],
                         courses: List[Course],
                         faculty: List[Faculty],
                         rooms: List[Room],
                         time_slots: List[TimeSlot]) -> Dict[str, Any]:
        """Validate the solution for constraint violations."""
        try:
            self.logger.info("Validating solution for constraint violations")
            
            violations = []
            
            # Check hard constraint violations
            hard_violations = self._check_hard_constraint_violations(
                solver, variables, students, courses, faculty, rooms, time_slots
            )
            violations.extend(hard_violations)
            
            # Check soft constraint violations
            soft_violations = self._check_soft_constraint_violations(
                solver, variables, students, courses, faculty, rooms, time_slots
            )
            violations.extend(soft_violations)
            
            return {
                "valid": len(violations) == 0,
                "violations": violations,
                "violation_count": len(violations)
            }
            
        except Exception as e:
            self.logger.error(f"Error validating solution: {str(e)}")
            return {"valid": False, "violations": [str(e)], "violation_count": 1}
    
    def _check_hard_constraint_violations(self, 
                                        solver: cp_model.CpSolver,
                                        variables: Dict[str, Any],
                                        students: List[Student],
                                        courses: List[Course],
                                        faculty: List[Faculty],
                                        rooms: List[Room],
                                        time_slots: List[TimeSlot]) -> List[str]:
        """Check for hard constraint violations."""
        violations = []
        
        # Check faculty conflicts
        for teacher in faculty:
            for slot in time_slots:
                active_assignments = []
                for course in courses:
                    if course.id in teacher.subjects:  # Check if teacher can teach this course
                        for room in rooms:
                            if room.capacity >= course.max_students_per_section:  # Check room suitability
                                var_name = f"assign_{teacher.id}_{course.id}_{room.id}_{slot.id}"
                                if var_name in variables.get('variables', {}):
                                    if solver.Value(variables['variables'][var_name]) == 1:
                                        active_assignments.append(course.id)
                
                if len(active_assignments) > 1:
                    violations.append(f"Faculty {teacher.name} has multiple assignments at slot {slot.id}")
        
        # Check student conflicts
        for student in students:
            for slot in time_slots:
                active_assignments = []
                for course in courses:
                    if course.id in [pref.course_id for pref in student.preferences]:
                        var_name = f"elective_assign_{student.id}_{course.id}"
                        if var_name in variables.get('variables', {}):
                            if solver.Value(variables['variables'][var_name]) == 1:
                                active_assignments.append(course.id)
                
                if len(active_assignments) > 1:
                    violations.append(f"Student {student.name} has multiple assignments at slot {slot.id}")
        
        # Check room conflicts
        for room in rooms:
            for slot in time_slots:
                active_assignments = []
                for course in courses:
                    if room.capacity >= course.max_students_per_section:  # Check room suitability
                        for teacher in faculty:
                            if course.id in teacher.subjects:  # Check if teacher can teach this course
                                var_name = f"assign_{teacher.id}_{course.id}_{room.id}_{slot.id}"
                                if var_name in variables.get('variables', {}):
                                    if solver.Value(variables['variables'][var_name]) == 1:
                                        active_assignments.append(course.id)
                
                if len(active_assignments) > 1:
                    violations.append(f"Room {room.name} has multiple assignments at slot {slot.id}")
        
        return violations
    
    def _check_soft_constraint_violations(self, 
                                        solver: cp_model.CpSolver,
                                        variables: Dict[str, Any],
                                        students: List[Student],
                                        courses: List[Course],
                                        faculty: List[Faculty],
                                        rooms: List[Room],
                                        time_slots: List[TimeSlot]) -> List[str]:
        """Check for soft constraint violations."""
        violations = []
        
        # Check faculty workload balance
        faculty_workloads = {}
        for teacher in faculty:
            workload = 0
            for course in courses:
                if course.id in teacher.subjects:  # Check if teacher can teach this course
                    for room in rooms:
                        if room.capacity >= course.max_students_per_section:  # Check room suitability
                            for slot in time_slots:
                                var_name = f"assign_{teacher.id}_{course.id}_{room.id}_{slot.id}"
                                if var_name in variables.get('variables', {}):
                                    if solver.Value(variables['variables'][var_name]) == 1:
                                        workload += 1
            
            faculty_workloads[teacher.id] = workload
            
            if workload > teacher.max_hours_per_week:
                violations.append(f"Faculty {teacher.name} exceeds max weekly hours: {workload}/{teacher.max_hours_per_week}")
        
        # Check room utilization
        room_utilization = {}
        for room in rooms:
            utilization = 0
            for course in courses:
                if room.capacity >= course.max_students_per_section:  # Check room suitability
                    for teacher in faculty:
                        if course.id in teacher.subjects:  # Check if teacher can teach this course
                            for slot in time_slots:
                                var_name = f"assign_{teacher.id}_{course.id}_{room.id}_{slot.id}"
                                if var_name in variables.get('variables', {}):
                                    if solver.Value(variables['variables'][var_name]) == 1:
                                        utilization += 1
            
            room_utilization[room.id] = utilization
        
        return violations
