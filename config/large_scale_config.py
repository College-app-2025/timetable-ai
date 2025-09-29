"""
Optimized configuration for large-scale timetable generation (1000+ students)
"""

from src.ml.data.models import OptimizationConfig

def get_large_scale_config():
    """Get optimized configuration for 1000+ students."""
    
    config = OptimizationConfig()
    
    # Optimize for large scale
    config.max_optimization_time = 600  # 10 minutes for 1000 students
    config.max_iterations = 2000       # More iterations for better solutions
    
    # Adjust weights for large scale
    config.student_satisfaction_weight = 1.2  # Prioritize satisfaction
    config.faculty_workload_weight = 0.9      # Balance workload
    config.room_utilization_weight = 0.7     # Optimize room usage
    config.elective_preference_weight = 1.5  # Strong preference weighting
    
    # NEP 2020 compliance
    config.nep_compliance_weight = 1.1
    config.interdisciplinary_weight = 1.0
    
    # Fairness for large groups
    config.carry_forward_weight = 0.8
    config.section_balance_weight = 0.6
    
    # Elective allocation for large scale
    config.max_electives_per_student = 3  # Reduce complexity
    config.min_electives_per_student = 1
    
    return config

def get_performance_estimates(students_count: int):
    """Get performance estimates for different scales."""
    
    if students_count < 500:
        return {
            "optimization_time": "30-60 seconds",
            "memory_usage": "< 1GB",
            "success_rate": "95%+",
            "recommended_config": "default"
        }
    elif students_count < 1000:
        return {
            "optimization_time": "2-5 minutes", 
            "memory_usage": "1-2GB",
            "success_rate": "90%+",
            "recommended_config": "large_scale"
        }
    elif students_count < 2000:
        return {
            "optimization_time": "5-10 minutes",
            "memory_usage": "2-4GB", 
            "success_rate": "85%+",
            "recommended_config": "large_scale"
        }
    else:
        return {
            "optimization_time": "10+ minutes",
            "memory_usage": "4GB+",
            "success_rate": "80%+",
            "recommended_config": "large_scale + chunking"
        }

# Performance benchmarks for 1000 students
PERFORMANCE_BENCHMARKS = {
    "students": 1000,
    "courses": 50,
    "faculty": 100,
    "rooms": 30,
    "time_slots": 40,
    "expected_assignments": 200,
    "optimization_time": "3-5 minutes",
    "memory_usage": "1.5-2GB",
    "success_rate": "90%+"
}
