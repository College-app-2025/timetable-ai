"""
Multi-schedule optimizer for generating multiple timetable options.
Allows admin to choose from different optimization strategies.
"""

from typing import List, Dict, Any, Optional
import time
from src.utils.logger_config import get_logger

from .optimizer import TimetableOptimizer
from ..data.models import OptimizationConfig, Schedule

logger = get_logger("multi_schedule_optimizer")


class MultiScheduleOptimizer:
    """Generates multiple timetable options with different optimization strategies."""
    
    def __init__(self, base_config: Optional[OptimizationConfig] = None):
        self.base_config = base_config or OptimizationConfig()
        self.logger = logger
    
    async def generate_multiple_schedules(self, 
                                        institute_id: str, 
                                        semester: int,
                                        data: Dict[str, Any],
                                        num_options: int = 3) -> Dict[str, Any]:
        """Generate multiple schedule options with different optimization strategies."""
        try:
            self.logger.info(f"Generating {num_options} schedule options for institute: {institute_id}")
            
            schedules = []
            optimization_strategies = [
                {
                    "name": "Student Satisfaction Focus",
                    "description": "Prioritizes student satisfaction and preferences",
                    "config": self._create_satisfaction_config()
                },
                {
                    "name": "Faculty Workload Balance",
                    "description": "Focuses on balanced faculty workload distribution", 
                    "config": self._create_workload_config()
                },
                {
                    "name": "Resource Utilization",
                    "description": "Maximizes room and resource utilization",
                    "config": self._create_utilization_config()
                },
                {
                    "name": "NEP 2020 Compliance",
                    "description": "Emphasizes NEP 2020 compliance and flexibility",
                    "config": self._create_nep_config()
                },
                {
                    "name": "Balanced Approach",
                    "description": "Balanced optimization across all metrics",
                    "config": self._create_balanced_config()
                }
            ]
            
            # Generate schedules with different strategies
            for i, strategy in enumerate(optimization_strategies[:num_options]):
                try:
                    self.logger.info(f"Generating schedule option {i+1}: {strategy['name']}")
                    
                    optimizer = TimetableOptimizer(strategy['config'])
                    result = await optimizer.optimize_timetable_with_data(
                        institute_id=institute_id,
                        semester=semester,
                        config=strategy['config'],
                        data=data
                    )
                    
                    if result["success"]:
                        schedule_info = {
                            "option_id": i + 1,
                            "name": strategy['name'],
                            "description": strategy['description'],
                            "schedule": result["schedule"],
                            "metrics": {
                                "student_satisfaction": result["student_satisfaction"],
                                "faculty_workload_balance": result["faculty_workload_balance"],
                                "room_utilization": result["room_utilization"],
                                "elective_allocation_rate": result["elective_allocation_rate"],
                                "constraint_violations": result["constraint_violations"],
                                "optimization_time": result["optimization_time"]
                            },
                            "assignments_count": len(result["assignments"]),
                            "is_feasible": result["constraint_violations"] == 0
                        }
                        schedules.append(schedule_info)
                        self.logger.info(f"✅ Generated schedule option {i+1} successfully")
                    else:
                        self.logger.warning(f"❌ Failed to generate schedule option {i+1}: {result['error']}")
                        
                except Exception as e:
                    self.logger.error(f"Error generating schedule option {i+1}: {str(e)}")
                    continue
            
            # Sort schedules by overall quality score
            schedules.sort(key=lambda x: self._calculate_quality_score(x["metrics"]), reverse=True)
            
            return {
                "success": True,
                "institute_id": institute_id,
                "semester": semester,
                "total_options": len(schedules),
                "schedules": schedules,
                "generation_time": time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating multiple schedules: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "schedules": []
            }
    
    def _create_satisfaction_config(self) -> OptimizationConfig:
        """Create config optimized for student satisfaction."""
        config = OptimizationConfig()
        config.satisfaction_weight = 0.6
        config.workload_weight = 0.2
        config.utilization_weight = 0.1
        config.elective_weight = 0.1
        return config
    
    def _create_workload_config(self) -> OptimizationConfig:
        """Create config optimized for faculty workload balance."""
        config = OptimizationConfig()
        config.satisfaction_weight = 0.2
        config.workload_weight = 0.6
        config.utilization_weight = 0.1
        config.elective_weight = 0.1
        return config
    
    def _create_utilization_config(self) -> OptimizationConfig:
        """Create config optimized for resource utilization."""
        config = OptimizationConfig()
        config.satisfaction_weight = 0.2
        config.workload_weight = 0.2
        config.utilization_weight = 0.5
        config.elective_weight = 0.1
        return config
    
    def _create_nep_config(self) -> OptimizationConfig:
        """Create config optimized for NEP 2020 compliance."""
        config = OptimizationConfig()
        config.satisfaction_weight = 0.3
        config.workload_weight = 0.2
        config.utilization_weight = 0.2
        config.elective_weight = 0.3
        return config
    
    def _create_balanced_config(self) -> OptimizationConfig:
        """Create balanced optimization config."""
        config = OptimizationConfig()
        config.satisfaction_weight = 0.25
        config.workload_weight = 0.25
        config.utilization_weight = 0.25
        config.elective_weight = 0.25
        return config
    
    def _calculate_quality_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall quality score for a schedule."""
        try:
            satisfaction = metrics.get("student_satisfaction", 0.0)
            workload_balance = metrics.get("faculty_workload_balance", 0.0)
            utilization = metrics.get("room_utilization", 0.0)
            elective_rate = metrics.get("elective_allocation_rate", 0.0)
            violations = metrics.get("constraint_violations", 0)
            
            # Penalize constraint violations heavily
            violation_penalty = max(0, 1.0 - (violations * 0.1))
            
            # Calculate weighted average
            quality_score = (
                satisfaction * 0.3 +
                workload_balance * 0.25 +
                utilization * 0.25 +
                elective_rate * 0.2
            ) * violation_penalty
            
            return quality_score
            
        except Exception as e:
            self.logger.error(f"Error calculating quality score: {str(e)}")
            return 0.0
    
    async def save_selected_schedule(self, 
                                   selected_schedule: Dict[str, Any],
                                   institute_id: str) -> Dict[str, Any]:
        """Save the admin-selected schedule to the database."""
        try:
            self.logger.info(f"Saving selected schedule for institute: {institute_id}")
            
            # Here you would implement the database save logic
            # For now, we'll just return success
            
            schedule_data = selected_schedule["schedule"]
            
            # TODO: Implement database save logic
            # Example:
            # await db.schedule.create(data={
            #     "institute_id": institute_id,
            #     "semester": schedule_data["semester"],
            #     "assignments": schedule_data["assignments"],
            #     "is_optimized": True,
            #     "optimization_score": selected_schedule["metrics"]["student_satisfaction"]
            # })
            
            return {
                "success": True,
                "message": "Schedule saved successfully",
                "schedule_id": schedule_data["id"]
            }
            
        except Exception as e:
            self.logger.error(f"Error saving schedule: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

