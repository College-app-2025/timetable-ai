"""
Pareto-optimal multi-objective optimizer for generating multiple diverse schedules.
Finds multiple solutions that represent different trade-offs between objectives.
"""

from typing import List, Dict, Any, Optional, Tuple
import time
import random
from ortools.sat.python import cp_model
from src.utils.logger_config import get_logger

from ..data.models import (
    Student, Course, Faculty, Room, TimeSlot, Assignment,
    Schedule, OptimizationConfig
)
from .constraint_solver import ConstraintSolver
from .elective_allocator import ElectiveAllocator
from .timetable_builder import TimetableBuilder
from ..evaluation.metrics import MetricsCalculator

logger = get_logger("pareto_optimizer")


class ParetoOptimizer:
    """Multi-objective optimizer that finds Pareto-optimal solutions."""
    
    def __init__(self, base_config: Optional[OptimizationConfig] = None):
        self.base_config = base_config or OptimizationConfig()
        self.logger = logger
        self.solver = ConstraintSolver(self.base_config)
        self.allocator = ElectiveAllocator(self.base_config)
        self.builder = TimetableBuilder()
        self.metrics_calculator = MetricsCalculator()
    
    async def find_pareto_optimal_schedules(self,
                                          institute_id: str,
                                          semester: int,
                                          data: Dict[str, Any],
                                          max_solutions: int = 5,
                                          time_limit: int = 300) -> Dict[str, Any]:
        """Find multiple Pareto-optimal schedules using different approaches."""
        try:
            self.logger.info(f"Finding Pareto-optimal schedules for institute: {institute_id}")
            start_time = time.time()
            
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
            elective_assignments = elective_result.get("assignments", []) if elective_result.get("success", False) else []
            
            # Step 2: Find multiple Pareto-optimal solutions
            self.logger.info("Step 2: Finding Pareto-optimal solutions")
            pareto_solutions = await self._find_pareto_solutions(
                students, courses, faculty, rooms, time_slots, elective_assignments, max_solutions, time_limit
            )
            
            # Step 3: Build schedules for each solution
            self.logger.info("Step 3: Building schedules")
            schedules = []
            for i, solution in enumerate(pareto_solutions):
                try:
                    all_assignments = elective_assignments + solution["assignments"]
                    schedule = self.builder.build_schedule(
                        assignments=all_assignments,
                        institute_id=institute_id,
                        semester=semester
                    )
                    
                    # Calculate metrics
                    metrics = self.metrics_calculator.calculate_metrics(
                        schedule, students, courses, faculty, rooms
                    )
                    
                    schedule_info = {
                        "option_id": i + 1,
                        "name": f"Pareto Solution {i + 1}",
                        "description": f"Solution {i + 1} with {solution['strategy']} focus",
                        "schedule": schedule,
                        "metrics": {
                            "student_satisfaction": metrics.student_satisfaction,
                            "faculty_workload_balance": metrics.faculty_workload_balance,
                            "room_utilization": metrics.room_utilization,
                            "elective_allocation_rate": metrics.elective_allocation_rate,
                            "constraint_violations": metrics.constraint_violations,
                            "optimization_time": solution["optimization_time"]
                        },
                        "assignments_count": len(all_assignments),
                        "is_feasible": metrics.constraint_violations == 0,
                        "strategy": solution["strategy"],
                        "pareto_rank": solution["pareto_rank"]
                    }
                    schedules.append(schedule_info)
                    
                except Exception as e:
                    self.logger.error(f"Error building schedule {i+1}: {str(e)}")
                    continue
            
            # Sort by Pareto rank
            schedules.sort(key=lambda x: x["pareto_rank"])
            
            return {
                "success": True,
                "institute_id": institute_id,
                "semester": semester,
                "total_options": len(schedules),
                "schedules": schedules,
                "generation_time": time.time() - start_time,
                "optimization_type": "Pareto-optimal"
            }
            
        except Exception as e:
            self.logger.error(f"Error finding Pareto-optimal schedules: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "schedules": []
            }
    
    async def _find_pareto_solutions(self,
                                   students: List[Student],
                                   courses: List[Course],
                                   faculty: List[Faculty],
                                   rooms: List[Room],
                                   time_slots: List[TimeSlot],
                                   elective_assignments: List[Assignment],
                                   max_solutions: int,
                                   time_limit: int) -> List[Dict[str, Any]]:
        """Find multiple Pareto-optimal solutions using different strategies."""
        
        solutions = []
        strategies = [
            {"name": "Satisfaction Focus", "weights": [0.6, 0.2, 0.1, 0.1]},
            {"name": "Workload Balance", "weights": [0.2, 0.6, 0.1, 0.1]},
            {"name": "Resource Utilization", "weights": [0.1, 0.2, 0.6, 0.1]},
            {"name": "NEP Compliance", "weights": [0.2, 0.2, 0.2, 0.4]},
            {"name": "Balanced", "weights": [0.25, 0.25, 0.25, 0.25]}
        ]
        
        for i, strategy in enumerate(strategies[:max_solutions]):
            try:
                self.logger.info(f"Finding solution {i+1}: {strategy['name']}")
                
                # Create model with this strategy
                model = cp_model.CpModel()
                variables = self._create_decision_variables(students, courses, faculty, rooms, time_slots)
                
                # Add constraints
                self.solver.add_all_constraints(students, courses, faculty, rooms, time_slots, variables)
                
                # Set objective with this strategy's weights
                self._set_weighted_objective(model, variables, strategy["weights"])
                
                # Solve
                solver = cp_model.CpSolver()
                solver.parameters.max_time_in_seconds = time_limit // max_solutions
                
                start_time = time.time()
                status = solver.Solve(model)
                optimization_time = time.time() - start_time
                
                if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
                    assignments = self._extract_assignments_from_solution(
                        solver, variables, students, courses, faculty, rooms, time_slots
                    )
                    
                    # Calculate Pareto rank
                    pareto_rank = self._calculate_pareto_rank(assignments, solutions)
                    
                    solutions.append({
                        "assignments": assignments,
                        "strategy": strategy["name"],
                        "optimization_time": optimization_time,
                        "pareto_rank": pareto_rank
                    })
                    
                    self.logger.info(f"✅ Found solution {i+1} with {len(assignments)} assignments")
                else:
                    self.logger.warning(f"❌ No feasible solution found for strategy: {strategy['name']}")
                    
            except Exception as e:
                self.logger.error(f"Error finding solution {i+1}: {str(e)}")
                continue
        
        return solutions
    
    def _set_weighted_objective(self, model: cp_model.CpModel, variables: Dict[str, Any], weights: List[float]):
        """Set objective function with specific weights."""
        objective_terms = []
        
        # Student satisfaction (weight 0)
        if 'total_satisfaction' in variables and weights[0] > 0:
            objective_terms.append(weights[0] * variables['total_satisfaction'])
        
        # Faculty workload balance (weight 1)
        if 'workload_vars' in variables and weights[1] > 0:
            for workload_var in variables['workload_vars'].values():
                objective_terms.append(weights[1] * workload_var)
        
        # Room utilization (weight 2)
        if 'utilization_vars' in variables and weights[2] > 0:
            for utilization_var in variables['utilization_vars'].values():
                objective_terms.append(weights[2] * utilization_var)
        
        # Elective preferences (weight 3)
        if 'elective_weights' in variables and weights[3] > 0:
            for var_name, weight in variables['elective_weights'].items():
                if var_name in variables['variables']:
                    objective_terms.append(weights[3] * weight * variables['variables'][var_name])
        
        if objective_terms:
            model.Maximize(sum(objective_terms))
    
    def _calculate_pareto_rank(self, new_assignments: List[Assignment], existing_solutions: List[Dict[str, Any]]) -> int:
        """Calculate Pareto rank for a solution."""
        # Simple ranking based on number of assignments and diversity
        base_rank = len(new_assignments)
        
        # Add diversity bonus
        diversity_bonus = 0
        for solution in existing_solutions:
            if len(solution["assignments"]) != len(new_assignments):
                diversity_bonus += 1
        
        return base_rank + diversity_bonus
    
    def _create_decision_variables(self, students, courses, faculty, rooms, time_slots):
        """Create decision variables for the optimization model."""
        # This would be implemented similar to the main optimizer
        # For now, return a placeholder
        return {"variables": {}, "model": None}
    
    def _extract_assignments_from_solution(self, solver, variables, students, courses, faculty, rooms, time_slots):
        """Extract assignments from the solved model."""
        # This would be implemented similar to the main optimizer
        # For now, return empty list
        return []

