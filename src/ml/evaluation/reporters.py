"""
Report generators for the SIH Timetable Optimization System.
Creates detailed reports and summaries of optimization results.
"""

from typing import List, Dict, Any, Optional
import json
import csv
from datetime import datetime
from src.utils.logger_config import get_logger

from ..data.models import (
    Student, Course, Faculty, Room, TimeSlot, Assignment,
    Schedule, OptimizationMetrics
)

logger = get_logger("report_generator")


class ReportGenerator:
    """Generates various reports for timetable optimization results."""
    
    def __init__(self):
        self.logger = logger
    
    def generate_optimization_report(self, 
                                   schedule: Schedule,
                                   metrics: OptimizationMetrics,
                                   students: List[Student],
                                   courses: List[Course],
                                   faculty: List[Faculty],
                                   rooms: List[Room]) -> Dict[str, Any]:
        """Generate comprehensive optimization report."""
        try:
            self.logger.info("Generating optimization report")
            
            report = {
                "report_metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "schedule_id": schedule.id,
                    "institute_id": schedule.institute_id,
                    "semester": schedule.semester
                },
                "optimization_metrics": metrics.to_dict(),
                "schedule_summary": self._generate_schedule_summary(schedule),
                "student_analysis": self._generate_student_analysis(schedule, students),
                "faculty_analysis": self._generate_faculty_analysis(schedule, faculty),
                "room_analysis": self._generate_room_analysis(schedule, rooms),
                "course_analysis": self._generate_course_analysis(schedule, courses),
                "recommendations": self._generate_recommendations(metrics)
            }
            
            self.logger.info("Optimization report generated successfully")
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating optimization report: {str(e)}")
            return {"error": str(e)}
    
    def _generate_schedule_summary(self, schedule: Schedule) -> Dict[str, Any]:
        """Generate schedule summary."""
        total_assignments = len(schedule.assignments)
        elective_assignments = sum(1 for a in schedule.assignments if a.is_elective)
        theory_assignments = total_assignments - elective_assignments
        
        unique_courses = len(set(a.course_id for a in schedule.assignments))
        unique_faculty = len(set(a.faculty_id for a in schedule.assignments))
        unique_rooms = len(set(a.room_id for a in schedule.assignments))
        time_slots_used = len(set(a.time_slot_id for a in schedule.assignments))
        
        return {
            "total_assignments": total_assignments,
            "elective_assignments": elective_assignments,
            "theory_assignments": theory_assignments,
            "unique_courses": unique_courses,
            "unique_faculty": unique_faculty,
            "unique_rooms": unique_rooms,
            "time_slots_used": time_slots_used,
            "optimization_score": schedule.optimization_score,
            "is_optimized": schedule.is_optimized
        }
    
    def _generate_student_analysis(self, schedule: Schedule, students: List[Student]) -> Dict[str, Any]:
        """Generate student analysis."""
        if not students:
            return {"message": "No students found"}
        
        # Calculate satisfaction statistics
        satisfaction_scores = [s.satisfaction_score for s in students]
        avg_satisfaction = sum(satisfaction_scores) / len(satisfaction_scores)
        max_satisfaction = max(satisfaction_scores)
        min_satisfaction = min(satisfaction_scores)
        
        # Count students by satisfaction level
        high_satisfaction = len([s for s in satisfaction_scores if s > 0.8])
        medium_satisfaction = len([s for s in satisfaction_scores if 0.4 <= s <= 0.8])
        low_satisfaction = len([s for s in satisfaction_scores if s < 0.4])
        
        # Department analysis
        dept_analysis = {}
        for student in students:
            dept = student.department
            if dept not in dept_analysis:
                dept_analysis[dept] = {"count": 0, "avg_satisfaction": 0.0, "scores": []}
            dept_analysis[dept]["count"] += 1
            dept_analysis[dept]["scores"].append(student.satisfaction_score)
        
        # Calculate department averages
        for dept in dept_analysis:
            scores = dept_analysis[dept]["scores"]
            dept_analysis[dept]["avg_satisfaction"] = sum(scores) / len(scores)
            del dept_analysis[dept]["scores"]  # Remove raw scores for cleaner output
        
        return {
            "total_students": len(students),
            "satisfaction_statistics": {
                "average": avg_satisfaction,
                "maximum": max_satisfaction,
                "minimum": min_satisfaction
            },
            "satisfaction_distribution": {
                "high": high_satisfaction,
                "medium": medium_satisfaction,
                "low": low_satisfaction
            },
            "department_analysis": dept_analysis
        }
    
    def _generate_faculty_analysis(self, schedule: Schedule, faculty: List[Faculty]) -> Dict[str, Any]:
        """Generate faculty analysis."""
        if not faculty:
            return {"message": "No faculty found"}
        
        # Calculate workload for each faculty member
        faculty_workloads = {}
        for teacher in faculty:
            assignments = schedule.get_assignments_for_faculty(teacher.id)
            faculty_workloads[teacher.id] = {
                "name": teacher.name,
                "department": teacher.department,
                "total_assignments": len(assignments),
                "hours_per_week": len(assignments),  # Assuming 1 hour per assignment
                "courses_taught": len(set(a.course_id for a in assignments))
            }
        
        # Calculate workload statistics
        workloads = [f["total_assignments"] for f in faculty_workloads.values()]
        avg_workload = sum(workloads) / len(workloads) if workloads else 0
        max_workload = max(workloads) if workloads else 0
        min_workload = min(workloads) if workloads else 0
        
        # Department workload analysis
        dept_workloads = {}
        for teacher_id, workload in faculty_workloads.items():
            dept = workload["department"]
            if dept not in dept_workloads:
                dept_workloads[dept] = {"faculty_count": 0, "total_assignments": 0, "avg_workload": 0.0}
            dept_workloads[dept]["faculty_count"] += 1
            dept_workloads[dept]["total_assignments"] += workload["total_assignments"]
        
        # Calculate department averages
        for dept in dept_workloads:
            dept_workloads[dept]["avg_workload"] = (
                dept_workloads[dept]["total_assignments"] / dept_workloads[dept]["faculty_count"]
            )
        
        return {
            "total_faculty": len(faculty),
            "workload_statistics": {
                "average": avg_workload,
                "maximum": max_workload,
                "minimum": min_workload
            },
            "faculty_workloads": faculty_workloads,
            "department_workloads": dept_workloads
        }
    
    def _generate_room_analysis(self, schedule: Schedule, rooms: List[Room]) -> Dict[str, Any]:
        """Generate room analysis."""
        if not rooms:
            return {"message": "No rooms found"}
        
        # Calculate utilization for each room
        room_utilizations = {}
        for room in rooms:
            assignments = schedule.get_assignments_for_room(room.id)
            utilization_rate = len(assignments) / 40  # Assuming 40 possible slots per week
            utilization_rate = min(1.0, utilization_rate)  # Cap at 100%
            
            room_utilizations[room.id] = {
                "name": room.name,
                "type": room.room_type.value,
                "capacity": room.capacity,
                "assignments": len(assignments),
                "utilization_rate": utilization_rate,
                "building": room.building,
                "floor": room.floor
            }
        
        # Calculate utilization statistics
        utilizations = [r["utilization_rate"] for r in room_utilizations.values()]
        avg_utilization = sum(utilizations) / len(utilizations) if utilizations else 0
        max_utilization = max(utilizations) if utilizations else 0
        min_utilization = min(utilizations) if utilizations else 0
        
        # Room type analysis
        type_analysis = {}
        for room in rooms:
            room_type = room.room_type.value
            if room_type not in type_analysis:
                type_analysis[room_type] = {"count": 0, "total_utilization": 0.0}
            type_analysis[room_type]["count"] += 1
            type_analysis[room_type]["total_utilization"] += room_utilizations[room.id]["utilization_rate"]
        
        # Calculate type averages
        for room_type in type_analysis:
            type_analysis[room_type]["avg_utilization"] = (
                type_analysis[room_type]["total_utilization"] / type_analysis[room_type]["count"]
            )
            del type_analysis[room_type]["total_utilization"]  # Remove for cleaner output
        
        return {
            "total_rooms": len(rooms),
            "utilization_statistics": {
                "average": avg_utilization,
                "maximum": max_utilization,
                "minimum": min_utilization
            },
            "room_utilizations": room_utilizations,
            "room_type_analysis": type_analysis
        }
    
    def _generate_course_analysis(self, schedule: Schedule, courses: List[Course]) -> Dict[str, Any]:
        """Generate course analysis."""
        if not courses:
            return {"message": "No courses found"}
        
        # Calculate assignments for each course
        course_assignments = {}
        for course in courses:
            assignments = schedule.get_assignments_for_course(course.id)
            course_assignments[course.id] = {
                "name": course.name,
                "code": course.course_code,
                "type": course.course_type.value,
                "department": course.department,
                "semester": course.semester,
                "assignments": len(assignments),
                "is_elective": course.is_elective,
                "hours_per_week": course.hours_per_week
            }
        
        # Course type analysis
        type_analysis = {}
        for course in courses:
            course_type = course.course_type.value
            if course_type not in type_analysis:
                type_analysis[course_type] = {"count": 0, "total_assignments": 0}
            type_analysis[course_type]["count"] += 1
            type_analysis[course_type]["total_assignments"] += course_assignments[course.id]["assignments"]
        
        # Calculate type averages
        for course_type in type_analysis:
            type_analysis[course_type]["avg_assignments"] = (
                type_analysis[course_type]["total_assignments"] / type_analysis[course_type]["count"]
            )
            del type_analysis[course_type]["total_assignments"]  # Remove for cleaner output
        
        # Elective vs Theory analysis
        elective_courses = [c for c in courses if c.is_elective]
        theory_courses = [c for c in courses if not c.is_elective]
        
        return {
            "total_courses": len(courses),
            "elective_courses": len(elective_courses),
            "theory_courses": len(theory_courses),
            "course_assignments": course_assignments,
            "course_type_analysis": type_analysis
        }
    
    def _generate_recommendations(self, metrics: OptimizationMetrics) -> List[str]:
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
        
        if not recommendations:
            recommendations.append("Schedule is well-optimized with no major issues identified")
        
        return recommendations
    
    def export_to_csv(self, report: Dict[str, Any], filename: str) -> bool:
        """Export report to CSV format."""
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write metadata
                writer.writerow(['Report Metadata'])
                for key, value in report.get('report_metadata', {}).items():
                    writer.writerow([key, value])
                
                writer.writerow([])  # Empty row
                
                # Write optimization metrics
                writer.writerow(['Optimization Metrics'])
                for key, value in report.get('optimization_metrics', {}).items():
                    writer.writerow([key, value])
                
                writer.writerow([])  # Empty row
                
                # Write schedule summary
                writer.writerow(['Schedule Summary'])
                for key, value in report.get('schedule_summary', {}).items():
                    writer.writerow([key, value])
            
            self.logger.info(f"Report exported to CSV: {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting to CSV: {str(e)}")
            return False
    
    def export_to_json(self, report: Dict[str, Any], filename: str) -> bool:
        """Export report to JSON format."""
        try:
            with open(filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(report, jsonfile, indent=2, default=str)
            
            self.logger.info(f"Report exported to JSON: {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting to JSON: {str(e)}")
            return False

