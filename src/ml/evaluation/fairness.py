"""
Fairness evaluation for the SIH Timetable Optimization System.
Implements carry-forward fairness algorithms across semesters.
"""

from typing import List, Dict, Any, Optional
from src.utils.logger_config import get_logger

from ..data.models import (
    Student, Course, Faculty, Room, TimeSlot, Assignment,
    Schedule, OptimizationConfig
)

logger = get_logger("fairness_calculator")


class FairnessCalculator:
    """Calculates and applies fairness adjustments for elective allocation."""
    
    def __init__(self):
        self.logger = logger
        self.fairness_history: Dict[str, List[float]] = {}  # student_id -> satisfaction scores
    
    def apply_fairness_adjustments(self, 
                                 schedule: Schedule,
                                 students: List[Student],
                                 courses: List[Course]) -> Dict[str, Any]:
        """Apply fairness adjustments to the schedule."""
        try:
            self.logger.info("Applying fairness adjustments")
            
            # Calculate current satisfaction scores
            current_satisfaction = self._calculate_current_satisfaction(students, schedule)
            
            # Update fairness history
            self._update_fairness_history(current_satisfaction)
            
            # Calculate fairness scores
            fairness_scores = self._calculate_fairness_scores(students)
            
            # Apply carry-forward adjustments
            adjustments = self._apply_carry_forward_adjustments(students, fairness_scores)
            
            result = {
                "success": True,
                "fairness_scores": fairness_scores,
                "adjustments_applied": adjustments,
                "current_satisfaction": current_satisfaction
            }
            
            self.logger.info("Fairness adjustments applied successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Error applying fairness adjustments: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _calculate_current_satisfaction(self, students: List[Student], schedule: Schedule) -> Dict[str, float]:
        """Calculate current satisfaction scores for all students."""
        satisfaction_scores = {}
        
        for student in students:
            # Get assigned courses for this student
            assigned_courses = self._get_student_assigned_courses(student, schedule)
            
            # Calculate satisfaction based on preferences
            satisfaction = self._calculate_individual_satisfaction(student, assigned_courses)
            satisfaction_scores[student.id] = satisfaction
            
            # Update student's satisfaction score
            student.satisfaction_score = satisfaction
        
        return satisfaction_scores
    
    def _get_student_assigned_courses(self, student: Student, schedule: Schedule) -> List[str]:
        """Get courses assigned to a specific student."""
        assigned_courses = []
        
        for assignment in schedule.assignments:
            # Check if this assignment is for a course the student prefers
            if assignment.course_id in [pref.course_id for pref in student.preferences]:
                assigned_courses.append(assignment.course_id)
        
        return assigned_courses
    
    def _calculate_individual_satisfaction(self, student: Student, assigned_courses: List[str]) -> float:
        """Calculate satisfaction score for an individual student."""
        if not student.preferences or not assigned_courses:
            return 0.0
        
        total_score = 0.0
        assigned_count = 0
        
        for course_id in assigned_courses:
            preference = student.get_preference_for_course(course_id)
            if preference:
                total_score += preference.preference_score
                assigned_count += 1
        
        # Normalize by number of preferences
        return total_score / len(student.preferences) if student.preferences else 0.0
    
    def _update_fairness_history(self, current_satisfaction: Dict[str, float]) -> None:
        """Update fairness history with current satisfaction scores."""
        for student_id, satisfaction in current_satisfaction.items():
            if student_id not in self.fairness_history:
                self.fairness_history[student_id] = []
            
            self.fairness_history[student_id].append(satisfaction)
            
            # Keep only last 5 semesters of history
            if len(self.fairness_history[student_id]) > 5:
                self.fairness_history[student_id] = self.fairness_history[student_id][-5:]
    
    def _calculate_fairness_scores(self, students: List[Student]) -> Dict[str, float]:
        """Calculate fairness scores for all students."""
        fairness_scores = {}
        
        for student in students:
            if student.id in self.fairness_history:
                # Calculate average historical satisfaction
                historical_satisfaction = self.fairness_history[student.id]
                avg_satisfaction = sum(historical_satisfaction) / len(historical_satisfaction)
                
                # Fairness score: higher for students with lower historical satisfaction
                fairness_score = max(0, 1 - avg_satisfaction)
                fairness_scores[student.id] = fairness_score
            else:
                # New student gets neutral fairness score
                fairness_scores[student.id] = 0.5
        
        return fairness_scores
    
    def _apply_carry_forward_adjustments(self, 
                                       students: List[Student],
                                       fairness_scores: Dict[str, float]) -> Dict[str, Any]:
        """Apply carry-forward adjustments based on fairness scores."""
        adjustments = {
            "students_prioritized": 0,
            "students_deprioritized": 0,
            "total_adjustments": 0
        }
        
        for student in students:
            fairness_score = fairness_scores.get(student.id, 0.5)
            
            # Students with lower historical satisfaction get priority
            if fairness_score > 0.7:  # High fairness score = low historical satisfaction
                student.priority_weight = 1.5  # Higher priority
                adjustments["students_prioritized"] += 1
            elif fairness_score < 0.3:  # Low fairness score = high historical satisfaction
                student.priority_weight = 0.8  # Lower priority
                adjustments["students_deprioritized"] += 1
            else:
                student.priority_weight = 1.0  # Normal priority
        
        adjustments["total_adjustments"] = adjustments["students_prioritized"] + adjustments["students_deprioritized"]
        
        return adjustments
    
    def get_fairness_statistics(self) -> Dict[str, Any]:
        """Get fairness statistics."""
        if not self.fairness_history:
            return {"message": "No fairness history available"}
        
        total_students = len(self.fairness_history)
        total_semesters = sum(len(scores) for scores in self.fairness_history.values())
        
        # Calculate average satisfaction across all students and semesters
        all_scores = []
        for scores in self.fairness_history.values():
            all_scores.extend(scores)
        
        avg_satisfaction = sum(all_scores) / len(all_scores) if all_scores else 0.0
        
        # Calculate satisfaction distribution
        high_satisfaction = len([s for s in all_scores if s > 0.8])
        medium_satisfaction = len([s for s in all_scores if 0.4 <= s <= 0.8])
        low_satisfaction = len([s for s in all_scores if s < 0.4])
        
        return {
            "total_students": total_students,
            "total_semesters": total_semesters,
            "average_satisfaction": avg_satisfaction,
            "satisfaction_distribution": {
                "high": high_satisfaction,
                "medium": medium_satisfaction,
                "low": low_satisfaction
            },
            "fairness_active": total_students > 0
        }
    
    def reset_fairness_history(self) -> None:
        """Reset fairness history."""
        self.fairness_history.clear()
        self.logger.info("Fairness history reset")
    
    def export_fairness_data(self) -> Dict[str, Any]:
        """Export fairness data for analysis."""
        return {
            "fairness_history": self.fairness_history,
            "statistics": self.get_fairness_statistics(),
            "export_timestamp": "2024-01-01T00:00:00Z"  # This would be actual timestamp
        }

