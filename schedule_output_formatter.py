"""
Schedule output formatter for the ML timetable optimization system.
Creates tabular schedules and tracks elective allocations by priority.
"""

import pandas as pd
from typing import List, Dict, Any, Tuple
from datetime import datetime, time
import asyncio
from src.ml.core.optimizer import TimetableOptimizer
from src.ml.data.models import OptimizationConfig
from src.ml.data.loaders import load_institute_data

class ScheduleOutputFormatter:
    """Formats optimization results into readable tables and reports."""
    
    def __init__(self):
        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        self.time_slots = [
            "9:00-10:00", "10:00-11:00", "11:00-12:00", "12:00-13:00",
            "14:00-15:00", "15:00-16:00", "16:00-17:00"
        ]
    
    def format_schedule_table(self, assignments: List[Dict[str, Any]], 
                            students: List[Dict[str, Any]], 
                            courses: List[Dict[str, Any]], 
                            faculty: List[Dict[str, Any]], 
                            rooms: List[Dict[str, Any]]) -> pd.DataFrame:
        """Create a tabular schedule format."""
        
        # Create empty schedule matrix
        schedule_data = []
        
        for day_num, day_name in enumerate(self.days, 1):
            for period_num, time_slot in enumerate(self.time_slots, 1):
                # Find assignments for this day and period
                day_assignments = [
                    a for a in assignments 
                    if a.get('day') == day_num and a.get('period') == period_num
                ]
                
                if day_assignments:
                    for assignment in day_assignments:
                        # Get course, faculty, and room details
                        course = next((c for c in courses if c['id'] == assignment['course_id']), {})
                        faculty_member = next((f for f in faculty if f['id'] == assignment['faculty_id']), {})
                        room = next((r for r in rooms if r['id'] == assignment['room_id']), {})
                        
                        schedule_data.append({
                            'Day': day_name,
                            'Time': time_slot,
                            'Course Code': course.get('course_code', 'N/A'),
                            'Course Name': course.get('name', 'N/A'),
                            'Faculty': faculty_member.get('name', 'N/A'),
                            'Room': room.get('name', 'N/A'),
                            'Room Type': room.get('room_type', 'N/A'),
                            'Capacity': room.get('capacity', 0),
                            'Students Enrolled': assignment.get('students_enrolled', 0),
                            'Is Elective': course.get('is_elective', False)
                        })
                else:
                    # Empty slot
                    schedule_data.append({
                        'Day': day_name,
                        'Time': time_slot,
                        'Course Code': '-',
                        'Course Name': '-',
                        'Faculty': '-',
                        'Room': '-',
                        'Room Type': '-',
                        'Capacity': 0,
                        'Students Enrolled': 0,
                        'Is Elective': False
                    })
        
        return pd.DataFrame(schedule_data)
    
    def create_elective_allocation_tables(self, assignments: List[Dict[str, Any]], 
                                        students: List[Dict[str, Any]], 
                                        courses: List[Dict[str, Any]]) -> Dict[str, pd.DataFrame]:
        """Create separate tables for each elective priority level."""
        
        # Filter elective assignments
        elective_assignments = [a for a in assignments if a.get('is_elective', False)]
        
        # Group by priority level (1-5)
        priority_tables = {}
        
        for priority in range(1, 6):
            priority_assignments = [a for a in elective_assignments if a.get('priority', 1) == priority]
            
            if priority_assignments:
                table_data = []
                for assignment in priority_assignments:
                    # Get course details
                    course = next((c for c in courses if c['id'] == assignment['course_id']), {})
                    
                    # Get student details
                    student_ids = assignment.get('student_ids', [])
                    for student_id in student_ids:
                        student = next((s for s in students if s['id'] == student_id), {})
                        table_data.append({
                            'Student ID': student.get('student_id', 'N/A'),
                            'Student Name': student.get('name', 'N/A'),
                            'Institute ID': student.get('institute_id', 'N/A'),
                            'Course Code': course.get('course_code', 'N/A'),
                            'Course Name': course.get('name', 'N/A'),
                            'Priority': priority,
                            'Department': student.get('department', 'N/A'),
                            'Semester': student.get('semester', 'N/A'),
                            'Section': student.get('section', 'N/A')
                        })
                
                priority_tables[f'priority_{priority}'] = pd.DataFrame(table_data)
            else:
                priority_tables[f'priority_{priority}'] = pd.DataFrame(columns=[
                    'Student ID', 'Student Name', 'Institute ID', 'Course Code', 
                    'Course Name', 'Priority', 'Department', 'Semester', 'Section'
                ])
        
        return priority_tables
    
    def create_summary_report(self, assignments: List[Dict[str, Any]], 
                            students: List[Dict[str, Any]], 
                            courses: List[Dict[str, Any]], 
                            faculty: List[Dict[str, Any]], 
                            rooms: List[Dict[str, Any]],
                            metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Create a comprehensive summary report."""
        
        # Basic statistics
        total_assignments = len(assignments)
        elective_assignments = len([a for a in assignments if a.get('is_elective', False)])
        core_assignments = total_assignments - elective_assignments
        
        # Faculty workload
        faculty_workload = {}
        for assignment in assignments:
            faculty_id = assignment.get('faculty_id')
            if faculty_id:
                faculty_workload[faculty_id] = faculty_workload.get(faculty_id, 0) + 1
        
        # Room utilization
        room_utilization = {}
        for assignment in assignments:
            room_id = assignment.get('room_id')
            if room_id:
                room_utilization[room_id] = room_utilization.get(room_id, 0) + 1
        
        # Elective allocation by priority
        elective_by_priority = {}
        for assignment in assignments:
            if assignment.get('is_elective', False):
                priority = assignment.get('priority', 1)
                elective_by_priority[priority] = elective_by_priority.get(priority, 0) + 1
        
        return {
            'total_assignments': total_assignments,
            'core_assignments': core_assignments,
            'elective_assignments': elective_assignments,
            'faculty_workload': faculty_workload,
            'room_utilization': room_utilization,
            'elective_by_priority': elective_by_priority,
            'metrics': metrics
        }
    
    def save_schedules_to_excel(self, schedule_df: pd.DataFrame, 
                              elective_tables: Dict[str, pd.DataFrame], 
                              summary: Dict[str, Any], 
                              filename: str = "timetable_output.xlsx"):
        """Save all schedules to an Excel file with multiple sheets."""
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Main schedule
            schedule_df.to_excel(writer, sheet_name='Main Schedule', index=False)
            
            # Elective allocation tables
            for priority, table in elective_tables.items():
                sheet_name = f'Elective Priority {priority.split("_")[1]}'
                table.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Summary report
            summary_df = pd.DataFrame([
                {'Metric': 'Total Assignments', 'Value': summary['total_assignments']},
                {'Metric': 'Core Assignments', 'Value': summary['core_assignments']},
                {'Metric': 'Elective Assignments', 'Value': summary['elective_assignments']},
                {'Metric': 'Student Satisfaction', 'Value': f"{summary['metrics'].get('student_satisfaction', 0):.3f}"},
                {'Metric': 'Faculty Workload Balance', 'Value': f"{summary['metrics'].get('faculty_workload_balance', 0):.3f}"},
                {'Metric': 'Room Utilization', 'Value': f"{summary['metrics'].get('room_utilization', 0):.3f}"},
            ])
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        print(f"✅ Schedules saved to {filename}")

async def test_with_sample_data():
    """Test the formatter with sample data."""
    
    print("🧪 Testing Schedule Output Formatter")
    print("=" * 40)
    
    # Create sample data
    sample_data = {
        "students": [
            {
                "id": "s001",
                "student_id": "STU001",
                "name": "Alice Johnson",
                "email": "alice@example.com",
                "department": "Computer Science",
                "semester": 1,
                "section": "A",
                "satisfaction_score": 0.8,
                "preferences": []
            },
            {
                "id": "s002",
                "student_id": "STU002", 
                "name": "Bob Smith",
                "email": "bob@example.com",
                "department": "Computer Science",
                "semester": 1,
                "section": "A",
                "satisfaction_score": 0.7,
                "preferences": []
            }
        ],
        "courses": [
            {
                "id": "c001",
                "course_code": "CS101",
                "name": "Programming Fundamentals",
                "department": "Computer Science",
                "semester": 1,
                "credits": 3,
                "hours_per_week": 3,
                "course_type": "theory",
                "is_elective": False,
                "max_students_per_section": 50,
                "prerequisites": []
            },
            {
                "id": "c002",
                "course_code": "CS301",
                "name": "Machine Learning",
                "department": "Computer Science",
                "semester": 1,
                "credits": 3,
                "hours_per_week": 3,
                "course_type": "theory",
                "is_elective": True,
                "max_students_per_section": 30,
                "prerequisites": []
            }
        ],
        "faculty": [
            {
                "id": "f001",
                "name": "Dr. John Doe",
                "email": "john@example.com",
                "department": "Computer Science",
                "designation": "Professor",
                "subjects": ["c001", "c002"],
                "max_hours_per_week": 20,
                "availability": {}
            }
        ],
        "rooms": [
            {
                "id": "r001",
                "name": "Room 101",
                "room_type": "lecture",
                "capacity": 50,
                "building": "Building A",
                "floor": 1,
                "equipment": []
            }
        ],
        "time_slots": [
            {
                "id": 1,
                "day": 1,  # Monday
                "period": 1,
                "start_time": "09:00:00",
                "end_time": "10:00:00"
            },
            {
                "id": 2,
                "day": 1,  # Monday
                "period": 2,
                "start_time": "10:00:00",
                "end_time": "11:00:00"
            }
        ],
        "student_preferences": []
    }
    
    # Create formatter
    formatter = ScheduleOutputFormatter()
    
    # Sample assignments (simulated)
    sample_assignments = [
        {
            "course_id": "c001",
            "faculty_id": "f001",
            "room_id": "r001",
            "day": 1,
            "period": 1,
            "students_enrolled": 2,
            "is_elective": False,
            "priority": 1
        },
        {
            "course_id": "c002",
            "faculty_id": "f001", 
            "room_id": "r001",
            "day": 1,
            "period": 2,
            "students_enrolled": 2,
            "is_elective": True,
            "priority": 1,
            "student_ids": ["s001", "s002"]
        }
    ]
    
    # Create schedule table
    schedule_df = formatter.format_schedule_table(
        sample_assignments,
        sample_data["students"],
        sample_data["courses"],
        sample_data["faculty"],
        sample_data["rooms"]
    )
    
    print("\n📅 MAIN SCHEDULE TABLE:")
    print(schedule_df.to_string(index=False))
    
    # Create elective allocation tables
    elective_tables = formatter.create_elective_allocation_tables(
        sample_assignments,
        sample_data["students"],
        sample_data["courses"]
    )
    
    print("\n🎯 ELECTIVE ALLOCATION TABLES:")
    for priority, table in elective_tables.items():
        if not table.empty:
            print(f"\nPriority {priority.split('_')[1]}:")
            print(table.to_string(index=False))
    
    # Create summary
    summary = formatter.create_summary_report(
        sample_assignments,
        sample_data["students"],
        sample_data["courses"],
        sample_data["faculty"],
        sample_data["rooms"],
        {"student_satisfaction": 0.85, "faculty_workload_balance": 0.78, "room_utilization": 0.72}
    )
    
    print("\n📊 SUMMARY REPORT:")
    print(f"Total Assignments: {summary['total_assignments']}")
    print(f"Core Assignments: {summary['core_assignments']}")
    print(f"Elective Assignments: {summary['elective_assignments']}")
    print(f"Elective by Priority: {summary['elective_by_priority']}")

async def main():
    """Main function."""
    await test_with_sample_data()

if __name__ == "__main__":
    asyncio.run(main())

