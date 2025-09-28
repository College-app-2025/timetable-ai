"""
Main optimization orchestrator for the SIH Timetable Optimization System.
Coordinates all optimization steps and manages the complete workflow.
"""

from typing import List, Dict, Any, Optional, Tuple
import time
from ortools.sat.python import cp_model
from src.utils.logger_config import get_logger

from ..data.models import (
    Student, Course, Faculty, Room, TimeSlot, Assignment,
    Schedule, OptimizationMetrics, OptimizationConfig
)
from ..data.loaders import load_institute_data
from ..data.converters import convert_data_to_ml_models
from .constraint_solver import ConstraintSolver
from .elective_allocator import ElectiveAllocator
from .timetable_builder import TimetableBuilder
from ..evaluation.metrics import MetricsCalculator
from ..evaluation.fairness import FairnessCalculator

logger = get_logger("timetable_optimizer")


class TimetableOptimizer:
    """Main orchestrator for timetable optimization."""
    
    def __init__(self, config: Optional[OptimizationConfig] = None):
        self.config = config or OptimizationConfig()
        self.logger = logger
        self.solver = ConstraintSolver(self.config)
        self.allocator = ElectiveAllocator(self.config)
        self.builder = TimetableBuilder()
        self.metrics_calculator = MetricsCalculator()
        self.fairness_calculator = FairnessCalculator()
        
        # Optimization state
        self.current_schedule: Optional[Schedule] = None
        self.optimization_metrics: Optional[OptimizationMetrics] = None
        self.is_optimized = False
    
    async def optimize_timetable(self, institute_id: str) -> Dict[str, Any]:
        """Main optimization method - generates optimized timetable for an institute."""
        try:
            self.logger.info(f"Starting timetable optimization for institute: {institute_id}")
            start_time = time.time()
            
            # Step 1: Load data from database
            self.logger.info("Step 1: Loading institute data from database")
            data = await load_institute_data(institute_id)
            
            if not data:
                return {"success": False, "error": "Failed to load institute data"}
            
            students = data['students']
            courses = data['courses']
            faculty = data['faculty']
            rooms = data['rooms']
            time_slots = data['time_slots']
            
            self.logger.info(f"Loaded data: {len(students)} students, {len(courses)} courses, "
                           f"{len(faculty)} faculty, {len(rooms)} rooms, {len(time_slots)} time slots")
            
            # Step 2: Preprocess and validate data
            self.logger.info("Step 2: Preprocessing and validating data")
            validation_result = self._validate_data(students, courses, faculty, rooms, time_slots)
            if not validation_result['valid']:
                return {"success": False, "error": f"Data validation failed: {validation_result['errors']}"}
            
            # Step 3: Run constraint-based optimization
            self.logger.info("Step 3: Running constraint-based optimization")
            optimization_result = await self._run_optimization(students, courses, faculty, rooms, time_slots)
            
            if not optimization_result['success']:
                return {"success": False, "error": f"Optimization failed: {optimization_result['error']}"}
            
            # Step 4: Build final timetable
            self.logger.info("Step 4: Building final timetable")
            schedule = self.builder.build_schedule(
                optimization_result['assignments'],
                institute_id,
                students[0].semester if students else 1
            )
            
            # Step 5: Calculate metrics and evaluate results
            self.logger.info("Step 5: Calculating optimization metrics")
            metrics = self.metrics_calculator.calculate_metrics(
                schedule, students, courses, faculty, rooms
            )
            
            # Step 6: Apply fairness adjustments
            self.logger.info("Step 6: Applying fairness adjustments")
            fairness_result = self.fairness_calculator.apply_fairness_adjustments(
                schedule, students, courses
            )
            
            # Update final metrics
            metrics.optimization_time = time.time() - start_time
            metrics.is_feasible = True
            
            # Store results
            self.current_schedule = schedule
            self.optimization_metrics = metrics
            self.is_optimized = True
            
            self.logger.info(f"Optimization completed successfully in {metrics.optimization_time:.2f} seconds")
            
            return {
                "success": True,
                "schedule": self._schedule_to_dict(schedule),
                "metrics": metrics.to_dict(),
                "assignments": [self._assignment_to_dict(a) for a in schedule.assignments],
                "optimization_time": metrics.optimization_time,
                "student_satisfaction": metrics.student_satisfaction,
                "faculty_workload_balance": metrics.faculty_workload_balance,
                "room_utilization": metrics.room_utilization
            }
            
        except Exception as e:
            self.logger.error(f"Optimization failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _validate_data(self, 
                      students: List[Student],
                      courses: List[Course],
                      faculty: List[Faculty],
                      rooms: List[Room],
                      time_slots: List[TimeSlot]) -> Dict[str, Any]:
        """Validate input data for optimization."""
        errors = []
        
        # Check minimum data requirements
        if len(students) == 0:
            errors.append("No students found")
        if len(courses) == 0:
            errors.append("No courses found")
        if len(faculty) == 0:
            errors.append("No faculty found")
        if len(rooms) == 0:
            errors.append("No rooms found")
        if len(time_slots) == 0:
            errors.append("No time slots found")
        
        # Check faculty-course compatibility
        for course in courses:
            if not any(f.can_teach_course(course.id) for f in faculty):
                errors.append(f"No faculty can teach course: {course.name}")
        
        # Check room-course compatibility
        for course in courses:
            if not any(r.is_suitable_for_course(course) for r in rooms):
                errors.append(f"No suitable room for course: {course.name}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    async def _run_optimization(self, 
                               students: List[Student],
                               courses: List[Course],
                               faculty: List[Faculty],
                               rooms: List[Room],
                               time_slots: List[TimeSlot]) -> Dict[str, Any]:
        """Run the constraint-based optimization."""
        try:
            # Create CP-SAT model
            model = cp_model.CpModel()
            
            # Create decision variables
            variables = self._create_decision_variables(students, courses, faculty, rooms, time_slots)
            
            # Add constraints
            self.solver.add_all_constraints(students, courses, faculty, rooms, time_slots, variables)
            
            # Set objective function
            self._set_objective_function(model, variables, students, courses, faculty, rooms)
            
            # Solve the model
            solver = cp_model.CpSolver()
            solver.parameters.max_time_in_seconds = self.config.max_optimization_time
            solver.parameters.max_iterations = self.config.max_iterations
            
            self.logger.info("Starting CP-SAT solver...")
            status = solver.Solve(model)
            
            if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
                self.logger.info("Optimization completed successfully")
                
                # Extract solution
                assignments = self._extract_solution(solver, variables, students, courses, faculty, rooms, time_slots)
                
                return {
                    "success": True,
                    "assignments": assignments,
                    "solver_status": "OPTIMAL" if status == cp_model.OPTIMAL else "FEASIBLE"
                }
            else:
                self.logger.warning(f"Optimization failed with status: {status}")
                return {
                    "success": False,
                    "error": f"Solver failed with status: {status}"
                }
                
        except Exception as e:
            self.logger.error(f"Optimization error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _create_decision_variables(self, 
                                 students: List[Student],
                                 courses: List[Course],
                                 faculty: List[Faculty],
                                 rooms: List[Room],
                                 time_slots: List[TimeSlot]) -> Dict[str, Any]:
        """Create decision variables for the optimization model."""
        variables = {}
        model = cp_model.CpModel()
        
        # Create assignment variables: assign_faculty_course_room_timeslot
        for teacher in faculty:
            for course in courses:
                if teacher.can_teach_course(course.id):
                    for room in rooms:
                        if room.is_suitable_for_course(course):
                            for slot in time_slots:
                                var_name = f"assign_{teacher.id}_{course.id}_{room.id}_{slot.id}"
                                variables[var_name] = model.NewBoolVar(var_name)
        
        # Create elective assignment variables: elective_assign_student_course
        for student in students:
            for course in courses:
                if course.is_elective:
                    var_name = f"elective_assign_{student.id}_{course.id}"
                    variables[var_name] = model.NewBoolVar(var_name)
        
        # Create course scheduling variables: course_scheduled_course
        for course in courses:
            var_name = f"course_scheduled_{course.id}"
            variables[var_name] = model.NewBoolVar(var_name)
        
        return {
            "variables": variables,
            "model": model,
            "students": students,
            "courses": courses,
            "faculty": faculty,
            "rooms": rooms,
            "time_slots": time_slots
        }
    
    def _set_objective_function(self, 
                               model: cp_model.CpModel,
                               variables: Dict[str, Any],
                               students: List[Student],
                               courses: List[Course],
                               faculty: List[Faculty],
                               rooms: List[Room]) -> None:
        """Set the objective function for optimization."""
        objective_terms = []
        
        # Student satisfaction (maximize)
        if 'total_satisfaction' in variables:
            objective_terms.append(variables['total_satisfaction'])
        
        # Faculty workload balance (minimize variance)
        if 'workload_vars' in variables:
            for workload_var in variables['workload_vars'].values():
                objective_terms.append(workload_var)
        
        # Room utilization (maximize)
        if 'utilization_vars' in variables:
            for utilization_var in variables['utilization_vars'].values():
                objective_terms.append(utilization_var)
        
        # Elective preferences (maximize)
        if 'elective_weights' in variables:
            for var_name, weight in variables['elective_weights'].items():
                if var_name in variables['variables']:
                    objective_terms.append(weight * variables['variables'][var_name])
        
        # NEP 2020 compliance (maximize)
        if 'nep_weights' in variables:
            for var_name, weight in variables['nep_weights'].items():
                if var_name in variables['variables']:
                    objective_terms.append(weight * variables['variables'][var_name])
        
        if objective_terms:
            model.Maximize(sum(objective_terms))
    
    def _extract_solution(self, 
                         solver: cp_model.CpSolver,
                         variables: Dict[str, Any],
                         students: List[Student],
                         courses: List[Course],
                         faculty: List[Faculty],
                         rooms: List[Room],
                         time_slots: List[TimeSlot]) -> List[Assignment]:
        """Extract solution from the solver."""
        assignments = []
        
        # Extract assignment variables
        for teacher in faculty:
            for course in courses:
                if teacher.can_teach_course(course.id):
                    for room in rooms:
                        if room.is_suitable_for_course(course):
                            for slot in time_slots:
                                var_name = f"assign_{teacher.id}_{course.id}_{room.id}_{slot.id}"
                                if var_name in variables['variables']:
                                    if solver.Value(variables['variables'][var_name]) == 1:
                                        assignment = Assignment(
                                            id=f"assign_{len(assignments)}",
                                            course_id=course.id,
                                            faculty_id=teacher.id,
                                            room_id=room.id,
                                            time_slot_id=slot.id,
                                            section_id=f"section_{course.department}",
                                            student_count=course.max_students_per_section,
                                            is_elective=course.is_elective
                                        )
                                        assignments.append(assignment)
        
        return assignments
    
    def _schedule_to_dict(self, schedule: Schedule) -> Dict[str, Any]:
        """Convert schedule to dictionary for API response."""
        return {
            "id": schedule.id,
            "institute_id": schedule.institute_id,
            "semester": schedule.semester,
            "created_at": schedule.created_at.isoformat(),
            "is_optimized": schedule.is_optimized,
            "optimization_score": schedule.optimization_score,
            "total_assignments": len(schedule.assignments)
        }
    
    def _assignment_to_dict(self, assignment: Assignment) -> Dict[str, Any]:
        """Convert assignment to dictionary for API response."""
        return {
            "id": assignment.id,
            "course_id": assignment.course_id,
            "faculty_id": assignment.faculty_id,
            "room_id": assignment.room_id,
            "time_slot_id": assignment.time_slot_id,
            "section_id": assignment.section_id,
            "student_count": assignment.student_count,
            "is_elective": assignment.is_elective,
            "priority_score": assignment.priority_score
        }
    
    def get_current_schedule(self) -> Optional[Schedule]:
        """Get the current optimized schedule."""
        return self.current_schedule
    
    def get_optimization_metrics(self) -> Optional[OptimizationMetrics]:
        """Get the current optimization metrics."""
        return self.optimization_metrics
    
    def is_schedule_optimized(self) -> bool:
        """Check if schedule is currently optimized."""
        return self.is_optimized
    
    async def optimize_timetable_with_data(self, 
                                         institute_id: str, 
                                         semester: int,
                                         config: OptimizationConfig,
                                         data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize timetable with provided data (for testing)."""
        try:
            self.logger.info(f"Starting timetable optimization with provided data for institute: {institute_id}")
            start_time = time.time()
            
            # Step 1: Convert data to ML models
            self.logger.info("Step 1: Converting data to ML models")
            ml_data = convert_data_to_ml_models(data)
            
            # Step 2: Validate data
            self.logger.info("Step 2: Validating provided data")
            validation_result = self._validate_data(
                ml_data["students"],
                ml_data["courses"], 
                ml_data["faculty"],
                ml_data["rooms"],
                ml_data["time_slots"]
            )
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": f"Data validation failed: {validation_result['errors']}",
                    "assignments": [],
                    "student_satisfaction": 0.0,
                    "faculty_workload_balance": 0.0,
                    "room_utilization": 0.0,
                    "elective_allocation_rate": 0.0,
                    "optimization_time": time.time() - start_time
                }
            
            # Step 3: Run optimization with provided data
            self.logger.info("Step 3: Running optimization with provided data")
            result = await self._run_optimization_with_data(
                institute_id=institute_id,
                semester=semester,
                config=config,
                data=ml_data
            )
            
            # Step 4: Calculate final metrics
            self.logger.info("Step 4: Calculating final metrics")
            if result["success"] and result["schedule"]:
                metrics = self.metrics_calculator.calculate_metrics(
                    result["schedule"],
                    ml_data["students"],
                    ml_data["courses"],
                    ml_data["faculty"],
                    ml_data["rooms"]
                )
                
                return {
                    "success": True,
                    "assignments": [assignment.to_dict() for assignment in result["schedule"].assignments],
                    "student_satisfaction": metrics.student_satisfaction,
                    "faculty_workload_balance": metrics.faculty_workload_balance,
                    "room_utilization": metrics.room_utilization,
                    "elective_allocation_rate": metrics.elective_allocation_rate,
                    "constraint_violations": metrics.constraint_violations,
                    "optimization_time": time.time() - start_time,
                    "schedule": result["schedule"].to_dict()
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Unknown optimization error"),
                    "assignments": [],
                    "student_satisfaction": 0.0,
                    "faculty_workload_balance": 0.0,
                    "room_utilization": 0.0,
                    "elective_allocation_rate": 0.0,
                    "optimization_time": time.time() - start_time
                }
                
        except Exception as e:
            self.logger.error(f"Optimization with data failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "assignments": [],
                "student_satisfaction": 0.0,
                "faculty_workload_balance": 0.0,
                "room_utilization": 0.0,
                "elective_allocation_rate": 0.0,
                "optimization_time": time.time() - start_time
            }
    
    async def _run_optimization_with_data(self,
                                        institute_id: str,
                                        semester: int,
                                        config: OptimizationConfig,
                                        data: Dict[str, Any]) -> Dict[str, Any]:
        """Run optimization with provided data."""
        try:
            # Extract data
            students = data["students"]
            courses = data["courses"]
            faculty = data["faculty"]
            rooms = data["rooms"]
            time_slots = data["time_slots"]
            student_preferences = data.get("student_preferences", [])
            
            # Step 1: Allocate electives
            self.logger.info("Step 1: Allocating electives")
            elective_result = self.allocator.allocate_electives(
                students, courses, faculty, rooms, time_slots
            )
            
            # Extract elective assignments (for now, we'll use empty list since no electives)
            elective_assignments = []
            if elective_result.get("success", False):
                # Convert elective allocations to assignments if needed
                elective_assignments = elective_result.get("assignments", [])
            
            # Step 2: Solve constraints for remaining courses
            self.logger.info("Step 2: Solving constraint optimization")
            
            # Create CP-SAT model
            model = cp_model.CpModel()
            
            # Create decision variables
            variables = self._create_decision_variables(students, courses, faculty, rooms, time_slots)
            variables['model'] = model  # Add model to variables for constraint solver
            
            # Add constraints
            self.solver.add_all_constraints(students, courses, faculty, rooms, time_slots, variables)
            
            # Set objective function
            self._set_objective_function(model, variables, students, courses, faculty, rooms)
            
            # Solve the model
            solver = cp_model.CpSolver()
            solver.parameters.max_time_in_seconds = config.max_optimization_time
            # Note: max_iterations is not a valid parameter for CP-SAT
            
            self.logger.info("Starting CP-SAT solver...")
            status = solver.Solve(model)
            
            if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
                self.logger.info("Optimization completed successfully")
                theory_assignments = self._extract_assignments_from_solution(
                    solver, variables, students, courses, faculty, rooms, time_slots
                )
            else:
                self.logger.warning("No feasible solution found")
                theory_assignments = []
            
            # Step 3: Combine assignments
            all_assignments = elective_assignments + theory_assignments
            
            # Step 4: Build final schedule
            self.logger.info("Step 4: Building final schedule")
            schedule = self.builder.build_schedule(
                assignments=all_assignments,
                institute_id=institute_id,
                semester=semester
            )
            
            return {
                "success": True,
                "schedule": schedule,
                "assignments": all_assignments
            }
            
        except Exception as e:
            self.logger.error(f"Optimization with data failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "schedule": None,
                "assignments": []
            }
