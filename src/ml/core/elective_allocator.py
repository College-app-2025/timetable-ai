"""
Elective allocation system for the SIH Timetable Optimization System.
Implements priority-based elective allocation with fairness algorithms.
"""

from typing import List, Dict, Any, Tuple, Optional
import random
from src.utils.logger_config import get_logger

from ..data.models import (
    Student, Course, Faculty, Room, TimeSlot, Assignment,
    StudentPreference, OptimizationConfig, CourseType
)

logger = get_logger("elective_allocator")


class ElectiveAllocator:
    """Handles priority-based elective allocation with fairness algorithms."""
    
    def __init__(self, config: OptimizationConfig):
        self.config = config
        self.logger = logger
        self.allocation_history: Dict[str, List[str]] = {}  # student_id -> list of allocated courses
    
    def allocate_electives(self, 
                          students: List[Student],
                          courses: List[Course],
                          faculty: List[Faculty],
                          rooms: List[Room],
                          time_slots: List[TimeSlot]) -> Dict[str, Any]:
        """Allocate electives to students based on preferences and fairness."""
        try:
            self.logger.info("Starting elective allocation process")
            
            # Filter elective courses
            elective_courses = [c for c in courses if c.is_elective]
            if not elective_courses:
                self.logger.warning("No elective courses found")
                return {"success": False, "error": "No elective courses available"}
            
            # Initialize allocation results
            allocation_results = {
                "allocations": {},  # student_id -> list of allocated courses
                "unallocated_students": [],
                "satisfaction_scores": {},
                "fairness_scores": {}
            }
            
            # Sort students by priority (fairness consideration)
            sorted_students = self._sort_students_by_priority(students)
            
            # Allocate electives in rounds
            for round_num in range(1, 6):  # 5 rounds for 5 preference levels
                self.logger.info(f"Starting allocation round {round_num}")
                
                round_allocations = self._allocate_round(
                    sorted_students, elective_courses, faculty, rooms, time_slots, round_num
                )
                
                # Update allocation results
                for student_id, allocated_courses in round_allocations.items():
                    if student_id not in allocation_results["allocations"]:
                        allocation_results["allocations"][student_id] = []
                    allocation_results["allocations"][student_id].extend(allocated_courses)
            
            # Calculate satisfaction and fairness scores
            self._calculate_satisfaction_scores(students, allocation_results["allocations"])
            self._calculate_fairness_scores(students, allocation_results["allocations"])
            
            # Identify unallocated students
            allocation_results["unallocated_students"] = [
                s.id for s in students 
                if len(allocation_results["allocations"].get(s.id, [])) < self.config.min_electives_per_student
            ]
            
            self.logger.info(f"Elective allocation completed. "
                           f"Allocated to {len(students) - len(allocation_results['unallocated_students'])} students")
            
            return {
                "success": True,
                "results": allocation_results
            }
            
        except Exception as e:
            self.logger.error(f"Error in elective allocation: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _sort_students_by_priority(self, students: List[Student]) -> List[Student]:
        """Sort students by priority for fair allocation."""
        def priority_score(student: Student) -> float:
            # Base priority on historical satisfaction
            historical_satisfaction = self._get_historical_satisfaction(student.id)
            
            # Add randomness for fairness
            random_factor = random.uniform(0.8, 1.2)
            
            return historical_satisfaction * random_factor
        
        return sorted(students, key=priority_score, reverse=True)
    
    def _get_historical_satisfaction(self, student_id: str) -> float:
        """Get historical satisfaction score for a student."""
        if student_id in self.allocation_history:
            # Calculate satisfaction based on previous allocations
            previous_allocations = self.allocation_history[student_id]
            return len(previous_allocations) / self.config.max_electives_per_student
        return 0.5  # Default neutral score
    
    def _allocate_round(self, 
                       students: List[Student],
                       elective_courses: List[Course],
                       faculty: List[Faculty],
                       rooms: List[Room],
                       time_slots: List[TimeSlot],
                       round_num: int) -> Dict[str, List[str]]:
        """Allocate electives for a specific round (preference level)."""
        round_allocations = {}
        
        for student in students:
            if len(round_allocations.get(student.id, [])) >= self.config.max_electives_per_student:
                continue
            
            # Get student's preference for this round
            preference = self._get_preference_for_round(student, round_num)
            if not preference:
                continue
            
            course = next((c for c in elective_courses if c.id == preference.course_id), None)
            if not course:
                continue
            
            # Check if course has available capacity
            if self._can_allocate_course(student, course, faculty, rooms, time_slots):
                if student.id not in round_allocations:
                    round_allocations[student.id] = []
                round_allocations[student.id].append(course.id)
                
                # Update course capacity
                course.elective_capacity -= 1
                
                # Update allocation history
                if student.id not in self.allocation_history:
                    self.allocation_history[student.id] = []
                self.allocation_history[student.id].append(course.id)
        
        return round_allocations
    
    def _get_preference_for_round(self, student: Student, round_num: int) -> Optional[StudentPreference]:
        """Get student's preference for a specific round."""
        for preference in student.preferences:
            if preference.priority == round_num:
                return preference
        return None
    
    def _can_allocate_course(self, 
                           student: Student,
                           course: Course,
                           faculty: List[Faculty],
                           rooms: List[Room],
                           time_slots: List[TimeSlot]) -> bool:
        """Check if a course can be allocated to a student."""
        # Check course capacity
        if course.elective_capacity <= 0:
            return False
        
        # Check if faculty can teach the course
        available_faculty = [f for f in faculty if f.can_teach_course(course.id)]
        if not available_faculty:
            return False
        
        # Check if suitable rooms are available
        suitable_rooms = [r for r in rooms if r.is_suitable_for_course(course)]
        if not suitable_rooms:
            return False
        
        # Check time slot availability
        available_slots = [s for s in time_slots if not s.is_break and not s.is_lunch]
        if not available_slots:
            return False
        
        return True
    
    def _calculate_satisfaction_scores(self, 
                                     students: List[Student],
                                     allocations: Dict[str, List[str]]) -> None:
        """Calculate satisfaction scores for all students."""
        for student in students:
            allocated_courses = allocations.get(student.id, [])
            satisfaction = 0.0
            
            for course_id in allocated_courses:
                preference = student.get_preference_for_course(course_id)
                if preference:
                    satisfaction += preference.preference_score
            
            # Normalize satisfaction score
            if student.preferences:
                satisfaction = satisfaction / len(student.preferences)
            
            student.satisfaction_score = satisfaction
    
    def _calculate_fairness_scores(self, 
                                 students: List[Student],
                                 allocations: Dict[str, List[str]]) -> None:
        """Calculate fairness scores for allocation."""
        total_allocations = sum(len(courses) for courses in allocations.values())
        total_students = len(students)
        
        if total_students == 0:
            return
        
        # Calculate average allocations per student
        avg_allocations = total_allocations / total_students
        
        # Calculate fairness score (lower variance = higher fairness)
        variance = 0.0
        for student in students:
            student_allocations = len(allocations.get(student.id, []))
            variance += (student_allocations - avg_allocations) ** 2
        
        variance = variance / total_students
        fairness_score = max(0, 1 - (variance / avg_allocations)) if avg_allocations > 0 else 0
        
        self.logger.info(f"Fairness score: {fairness_score:.3f}")
    
    def get_allocation_statistics(self, 
                                students: List[Student],
                                allocations: Dict[str, List[str]]) -> Dict[str, Any]:
        """Get statistics about the allocation process."""
        total_students = len(students)
        allocated_students = len([s for s in students if len(allocations.get(s.id, [])) > 0])
        
        total_allocations = sum(len(courses) for courses in allocations.values())
        avg_allocations = total_allocations / total_students if total_students > 0 else 0
        
        satisfaction_scores = [s.satisfaction_score for s in students]
        avg_satisfaction = sum(satisfaction_scores) / len(satisfaction_scores) if satisfaction_scores else 0
        
        return {
            "total_students": total_students,
            "allocated_students": allocated_students,
            "allocation_rate": allocated_students / total_students if total_students > 0 else 0,
            "total_allocations": total_allocations,
            "avg_allocations_per_student": avg_allocations,
            "avg_satisfaction_score": avg_satisfaction,
            "unallocated_students": total_students - allocated_students
        }
    
    def reset_allocation_history(self) -> None:
        """Reset allocation history for fresh start."""
        self.allocation_history.clear()
        self.logger.info("Allocation history reset")
    
    def update_allocation_history(self, student_id: str, allocated_courses: List[str]) -> None:
        """Update allocation history for a student."""
        self.allocation_history[student_id] = allocated_courses

