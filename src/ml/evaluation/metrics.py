"""
Metrics calculation for the SIH Timetable Optimization System.
Calculates satisfaction scores, utilization metrics, and performance indicators.
"""

from typing import List, Dict, Any, Optional
from src.utils.logger_config import get_logger

from ..data.models import (
    Student, Course, Faculty, Room, TimeSlot, Assignment,
    Schedule, OptimizationMetrics
)

logger = get_logger("metrics_calculator")


class MetricsCalculator:
    """Calculates various metrics for timetable optimization."""
    
    def __init__(self):
        self.logger = logger
    
    def calculate_metrics(self, 
                         schedule: Schedule,
                         students: List[Student],
                         courses: List[Course],
                         faculty: List[Faculty],
                         rooms: List[Room]) -> OptimizationMetrics:
        """Calculate comprehensive optimization metrics."""
        try:
            self.logger.info("Calculating optimization metrics")
            
            metrics = OptimizationMetrics()
            
            # Basic metrics
            metrics.total_assignments = len(schedule.assignments)
            metrics.is_feasible = True  # Assuming schedule is feasible if it exists
            
            # Student satisfaction
            metrics.student_satisfaction = self._calculate_student_satisfaction(students, schedule)
            
            # Faculty workload balance
            metrics.faculty_workload_balance = self._calculate_faculty_workload_balance(faculty, schedule)
            
            # Room utilization
            metrics.room_utilization = self._calculate_room_utilization(rooms, schedule)
            
            # Elective allocation rate
            metrics.elective_allocation_rate = self._calculate_elective_allocation_rate(students, schedule)
            
            # Constraint violations
            metrics.constraint_violations = self._count_constraint_violations(schedule)
            
            self.logger.info(f"Metrics calculated: satisfaction={metrics.student_satisfaction:.3f}, "
                           f"workload_balance={metrics.faculty_workload_balance:.3f}, "
                           f"room_utilization={metrics.room_utilization:.3f}")
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating metrics: {str(e)}")
            return OptimizationMetrics()
    
    def _calculate_student_satisfaction(self, students: List[Student], schedule: Schedule) -> float:
        """Calculate average student satisfaction score."""
        try:
            if not students:
                return 0.0
            
            total_satisfaction = 0.0
            valid_students = 0
            
            for student in students:
                # Calculate satisfaction based on assigned courses
                assigned_courses = self._get_student_assigned_courses(student, schedule)
                satisfaction = self._calculate_individual_satisfaction(student, assigned_courses)
                
                total_satisfaction += satisfaction
                valid_students += 1
            
            return total_satisfaction / valid_students if valid_students > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating student satisfaction: {str(e)}")
            return 0.0
    
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
    
    def _calculate_faculty_workload_balance(self, faculty: List[Faculty], schedule: Schedule) -> float:
        """Calculate faculty workload balance score."""
        try:
            if not faculty:
                return 0.0
            
            # Calculate workload for each faculty member
            faculty_workloads = {}
            for teacher in faculty:
                workload = len(schedule.get_assignments_for_faculty(teacher.id))
                faculty_workloads[teacher.id] = workload
            
            if not faculty_workloads:
                return 0.0
            
            # Calculate variance in workload
            workloads = list(faculty_workloads.values())
            avg_workload = sum(workloads) / len(workloads)
            
            if avg_workload == 0:
                return 1.0  # Perfect balance if no workload
            
            variance = sum((w - avg_workload) ** 2 for w in workloads) / len(workloads)
            std_dev = variance ** 0.5
            
            # Balance score (higher is better, max 1.0)
            balance_score = max(0, 1 - (std_dev / avg_workload))
            return balance_score
            
        except Exception as e:
            self.logger.error(f"Error calculating faculty workload balance: {str(e)}")
            return 0.0
    
    def _calculate_room_utilization(self, rooms: List[Room], schedule: Schedule) -> float:
        """Calculate room utilization efficiency."""
        try:
            if not rooms:
                return 0.0
            
            total_utilization = 0.0
            valid_rooms = 0
            
            for room in rooms:
                room_assignments = schedule.get_assignments_for_room(room.id)
                utilization = len(room_assignments) / 40  # Assuming 40 possible time slots per week
                utilization = min(1.0, utilization)  # Cap at 100%
                
                total_utilization += utilization
                valid_rooms += 1
            
            return total_utilization / valid_rooms if valid_rooms > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating room utilization: {str(e)}")
            return 0.0
    
    def _calculate_elective_allocation_rate(self, students: List[Student], schedule: Schedule) -> float:
        """Calculate rate of successful elective allocations."""
        try:
            if not students:
                return 0.0
            
            total_elective_requests = 0
            successful_allocations = 0
            
            for student in students:
                elective_preferences = [p for p in student.preferences if p.course_id in [c.id for c in student.preferences]]
                total_elective_requests += len(elective_preferences)
                
                # Count successful allocations
                assigned_electives = 0
                for assignment in schedule.assignments:
                    if assignment.is_elective and assignment.course_id in [p.course_id for p in student.preferences]:
                        assigned_electives += 1
                
                successful_allocations += min(assigned_electives, len(elective_preferences))
            
            return successful_allocations / total_elective_requests if total_elective_requests > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating elective allocation rate: {str(e)}")
            return 0.0
    
    def _count_constraint_violations(self, schedule: Schedule) -> int:
        """Count constraint violations in the schedule."""
        try:
            violations = 0
            
            # Check for faculty conflicts
            faculty_slots = {}
            for assignment in schedule.assignments:
                key = f"{assignment.faculty_id}_{assignment.time_slot_id}"
                if key in faculty_slots:
                    violations += 1
                else:
                    faculty_slots[key] = assignment
            
            # Check for room conflicts
            room_slots = {}
            for assignment in schedule.assignments:
                key = f"{assignment.room_id}_{assignment.time_slot_id}"
                if key in room_slots:
                    violations += 1
                else:
                    room_slots[key] = assignment
            
            return violations
            
        except Exception as e:
            self.logger.error(f"Error counting constraint violations: {str(e)}")
            return 0
    
    def calculate_department_metrics(self, 
                                   schedule: Schedule,
                                   students: List[Student],
                                   courses: List[Course]) -> Dict[str, Any]:
        """Calculate metrics by department."""
        try:
            department_metrics = {}
            
            # Group students by department
            dept_students = {}
            for student in students:
                dept = student.department
                if dept not in dept_students:
                    dept_students[dept] = []
                dept_students[dept].append(student)
            
            # Calculate metrics for each department
            for dept, dept_students_list in dept_students.items():
                dept_courses = [c for c in courses if c.department == dept]
                dept_assignments = [a for a in schedule.assignments if a.section_id and dept.lower() in a.section_id.lower()]
                
                dept_satisfaction = self._calculate_student_satisfaction(dept_students_list, schedule)
                
                department_metrics[dept] = {
                    "student_count": len(dept_students_list),
                    "course_count": len(dept_courses),
                    "assignment_count": len(dept_assignments),
                    "satisfaction_score": dept_satisfaction,
                    "elective_assignments": sum(1 for a in dept_assignments if a.is_elective)
                }
            
            return department_metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating department metrics: {str(e)}")
            return {}
    
    def calculate_time_slot_utilization(self, 
                                      schedule: Schedule,
                                      time_slots: List[TimeSlot]) -> Dict[int, int]:
        """Calculate utilization for each time slot."""
        try:
            slot_utilization = {}
            
            for slot in time_slots:
                slot_utilization[slot.id] = 0
            
            for assignment in schedule.assignments:
                slot_id = assignment.time_slot_id
                if slot_id in slot_utilization:
                    slot_utilization[slot_id] += 1
            
            return slot_utilization
            
        except Exception as e:
            self.logger.error(f"Error calculating time slot utilization: {str(e)}")
            return {}
    
    def generate_optimization_report(self, 
                                   metrics: OptimizationMetrics,
                                   department_metrics: Dict[str, Any],
                                   slot_utilization: Dict[int, int]) -> Dict[str, Any]:
        """Generate a comprehensive optimization report."""
        try:
            report = {
                "overall_metrics": metrics.to_dict(),
                "department_breakdown": department_metrics,
                "time_slot_utilization": slot_utilization,
                "recommendations": self._generate_recommendations(metrics, department_metrics)
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating optimization report: {str(e)}")
            return {}
    
    def _generate_recommendations(self, 
                                metrics: OptimizationMetrics,
                                department_metrics: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on metrics."""
        recommendations = []
        
        if metrics.student_satisfaction < 0.7:
            recommendations.append("Consider increasing elective course capacity to improve student satisfaction")
        
        if metrics.faculty_workload_balance < 0.6:
            recommendations.append("Faculty workload is imbalanced - consider redistributing assignments")
        
        if metrics.room_utilization < 0.5:
            recommendations.append("Room utilization is low - consider consolidating classes or adding more courses")
        
        if metrics.elective_allocation_rate < 0.8:
            recommendations.append("Elective allocation rate is low - consider adding more elective options")
        
        if metrics.constraint_violations > 0:
            recommendations.append(f"Found {metrics.constraint_violations} constraint violations - review schedule")
        
        return recommendations

