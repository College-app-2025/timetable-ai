"""
Complete timetable system integration.
Shows how to input data from database and get formatted schedule output.
"""

import asyncio
import pandas as pd
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ml.core.optimizer import TimetableOptimizer
from src.ml.data.models import OptimizationConfig
from src.ml.data.loaders import load_institute_data
from examples.schedule_output_formatter import ScheduleOutputFormatter
from src.utils.prisma import db

class CompleteTimetableSystem:
    """Complete integration of the timetable optimization system."""
    
    def __init__(self):
        self.optimizer = TimetableOptimizer()
        self.formatter = ScheduleOutputFormatter()
    
    async def generate_timetable_from_database(self, institute_id: str, semester: int) -> Dict[str, Any]:
        """Generate timetable using data from database."""
        
        print(f"🚀 Generating Timetable for Institute: {institute_id}, Semester: {semester}")
        print("=" * 60)
        
        try:
            # Step 1: Load data from database
            print("📊 Step 1: Loading data from database...")
            data = await load_institute_data(institute_id, semester)
            
            if not data:
                return {"success": False, "error": "No data found for the given institute and semester"}
            
            print(f"   ✅ Loaded {len(data['students'])} students")
            print(f"   ✅ Loaded {len(data['courses'])} courses")
            print(f"   ✅ Loaded {len(data['faculty'])} faculty")
            print(f"   ✅ Loaded {len(data['rooms'])} rooms")
            print(f"   ✅ Loaded {len(data['time_slots'])} time slots")
            
            # Step 2: Run optimization
            print("\n🎯 Step 2: Running optimization...")
            result = await self.optimizer.optimize_timetable_with_data(
                institute_id=institute_id,
                semester=semester,
                config=OptimizationConfig(),
                data=data
            )
            
            if not result["success"]:
                return result
            
            print(f"   ✅ Optimization completed in {result['optimization_time']:.2f}s")
            print(f"   ✅ Generated {len(result['assignments'])} assignments")
            
            # Step 3: Format output
            print("\n📋 Step 3: Formatting output...")
            
            # Create schedule table
            schedule_df = self.formatter.format_schedule_table(
                result['assignments'],
                data['students'],
                data['courses'],
                data['faculty'],
                data['rooms']
            )
            
            # Create elective allocation tables
            elective_tables = self.formatter.create_elective_allocation_tables(
                result['assignments'],
                data['students'],
                data['courses']
            )
            
            # Create summary report
            summary = self.formatter.create_summary_report(
                result['assignments'],
                data['students'],
                data['courses'],
                data['faculty'],
                data['rooms'],
                {
                    'student_satisfaction': result['student_satisfaction'],
                    'faculty_workload_balance': result['faculty_workload_balance'],
                    'room_utilization': result['room_utilization'],
                    'elective_allocation_rate': result['elective_allocation_rate']
                }
            )
            
            # Step 4: Save to Excel
            print("\n💾 Step 4: Saving to Excel...")
            filename = f"timetable_{institute_id}_semester_{semester}.xlsx"
            self.formatter.save_schedules_to_excel(
                schedule_df, elective_tables, summary, filename
            )
            
            return {
                "success": True,
                "assignments": result['assignments'],
                "schedule_table": schedule_df,
                "elective_tables": elective_tables,
                "summary": summary,
                "filename": filename
            }
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    def display_schedule_tables(self, result: Dict[str, Any]):
        """Display the generated schedule tables."""
        
        if not result["success"]:
            print(f"❌ Error: {result['error']}")
            return
        
        print("\n" + "="*80)
        print("📅 MAIN SCHEDULE TABLE")
        print("="*80)
        print(result['schedule_table'].to_string(index=False))
        
        print("\n" + "="*80)
        print("🎯 ELECTIVE ALLOCATION TABLES")
        print("="*80)
        
        for priority, table in result['elective_tables'].items():
            priority_num = priority.split('_')[1]
            print(f"\n📊 PRIORITY {priority_num} ELECTIVES:")
            print("-" * 60)
            if not table.empty:
                print(table.to_string(index=False))
            else:
                print("No students allocated to this priority level")
        
        print("\n" + "="*80)
        print("📊 SUMMARY REPORT")
        print("="*80)
        summary = result['summary']
        print(f"Total Assignments: {summary['total_assignments']}")
        print(f"Core Assignments: {summary['core_assignments']}")
        print(f"Elective Assignments: {summary['elective_assignments']}")
        print(f"Student Satisfaction: {summary['metrics']['student_satisfaction']:.3f}")
        print(f"Faculty Workload Balance: {summary['metrics']['faculty_workload_balance']:.3f}")
        print(f"Room Utilization: {summary['metrics']['room_utilization']:.3f}")
        print(f"Elective Allocation Rate: {summary['metrics']['elective_allocation_rate']:.3f}")
        
        print(f"\nElective Allocation by Priority:")
        for priority, count in summary['elective_by_priority'].items():
            print(f"  Priority {priority}: {count} assignments")
        
        print(f"\n💾 Full report saved to: {result['filename']}")

async def test_with_sample_database():
    """Test the complete system with sample database."""
    
    print("🧪 Testing Complete Timetable System")
    print("=" * 50)
    
    # First, create sample database
    print("📊 Creating sample database...")
    from create_sample_database import create_sample_data
    sample_data = await create_sample_data()
    
    if not sample_data:
        print("❌ Failed to create sample database")
        return
    
    institute_id = sample_data['institute_id']
    
    # Test the complete system
    system = CompleteTimetableSystem()
    result = await system.generate_timetable_from_database(institute_id, 1)
    
    # Display results
    system.display_schedule_tables(result)

async def test_with_api_format():
    """Test with API-style input format."""
    
    print("\n🌐 Testing with API Input Format")
    print("=" * 50)
    
    # Sample API input format
    api_input = {
        "institute_id": "inst_api_test_001",
        "semester": 1,
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
                "day": 1,
                "period": 1,
                "start_time": "09:00:00",
                "end_time": "10:00:00"
            },
            {
                "id": 2,
                "day": 1,
                "period": 2,
                "start_time": "10:00:00",
                "end_time": "11:00:00"
            }
        ]
    }
    
    # Test optimization
    system = CompleteTimetableSystem()
    result = await system.optimizer.optimize_timetable_with_data(
        institute_id=api_input["institute_id"],
        semester=api_input["semester"],
        config=OptimizationConfig(),
        data=api_input
    )
    
    if result["success"]:
        print("✅ API format test successful!")
        print(f"   Assignments: {len(result['assignments'])}")
        print(f"   Student Satisfaction: {result['student_satisfaction']:.3f}")
        print(f"   Faculty Workload Balance: {result['faculty_workload_balance']:.3f}")
        print(f"   Room Utilization: {result['room_utilization']:.3f}")
    else:
        print(f"❌ API format test failed: {result['error']}")

async def main():
    """Main function to test the complete system."""
    
    print("🚀 COMPLETE TIMETABLE SYSTEM TEST")
    print("=" * 60)
    
    try:
        await db.connect()
        
        # Test 1: With sample database
        await test_with_sample_database()
        
        # Test 2: With API format
        await test_with_api_format()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await db.disconnect()

if __name__ == "__main__":
    asyncio.run(main())

