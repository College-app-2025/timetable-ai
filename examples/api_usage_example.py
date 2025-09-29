"""
API usage example showing exact input/output formats for the timetable system.
"""

import asyncio
import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ml.core.optimizer import TimetableOptimizer
from src.ml.data.models import OptimizationConfig
from examples.schedule_output_formatter import ScheduleOutputFormatter

async def demonstrate_api_usage():
    """Demonstrate the exact API input/output format."""
    
    print("🌐 API USAGE DEMONSTRATION")
    print("=" * 50)
    
    # ========================================
    # INPUT FORMAT (What you send to the API)
    # ========================================
    
    print("\n📥 INPUT FORMAT:")
    print("POST /api/timetable/generate")
    print("Content-Type: application/json")
    print()
    
    api_input = {
        "institute_id": "inst_001",
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
                "preferences": [
                    {
                        "course_id": "c002",
                        "priority": 1,
                        "preferred_time_slots": [1, 2],
                        "preferred_rooms": ["r001"]
                    }
                ]
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
                "preferences": [
                    {
                        "course_id": "c002",
                        "priority": 2,
                        "preferred_time_slots": [1, 3],
                        "preferred_rooms": ["r001", "r002"]
                    }
                ]
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
                "prerequisites": ["c001"]
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
                "availability": {
                    "1": [1, 2, 3],  # Monday: periods 1, 2, 3
                    "2": [1, 2, 3],  # Tuesday: periods 1, 2, 3
                    "3": [1, 2, 3]   # Wednesday: periods 1, 2, 3
                }
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
                "equipment": ["Projector", "Whiteboard", "Computer"]
            },
            {
                "id": "r002",
                "name": "Room 102",
                "room_type": "lecture",
                "capacity": 30,
                "building": "Building A",
                "floor": 1,
                "equipment": ["Projector", "Whiteboard"]
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
            },
            {
                "id": 3,
                "day": 1,  # Monday
                "period": 3,
                "start_time": "11:00:00",
                "end_time": "12:00:00"
            },
            {
                "id": 4,
                "day": 2,  # Tuesday
                "period": 1,
                "start_time": "09:00:00",
                "end_time": "10:00:00"
            },
            {
                "id": 5,
                "day": 2,  # Tuesday
                "period": 2,
                "start_time": "10:00:00",
                "end_time": "11:00:00"
            }
        ]
    }
    
    print(json.dumps(api_input, indent=2))
    
    # ========================================
    # PROCESSING (What happens in the backend)
    # ========================================
    
    print("\n🔄 PROCESSING:")
    print("1. Validate input data")
    print("2. Convert to ML models")
    print("3. Run constraint optimization")
    print("4. Generate schedule")
    print("5. Calculate metrics")
    print("6. Format output")
    
    # Run the actual optimization
    optimizer = TimetableOptimizer()
    result = await optimizer.optimize_timetable_with_data(
        institute_id=api_input["institute_id"],
        semester=api_input["semester"],
        config=OptimizationConfig(),
        data=api_input
    )
    
    # ========================================
    # OUTPUT FORMAT (What you get back)
    # ========================================
    
    print("\n📤 OUTPUT FORMAT:")
    print("HTTP 200 OK")
    print("Content-Type: application/json")
    print()
    
    if result["success"]:
        # Create formatter for tabular output
        formatter = ScheduleOutputFormatter()
        
        # Generate schedule table
        schedule_df = formatter.format_schedule_table(
            result['assignments'],
            api_input['students'],
            api_input['courses'],
            api_input['faculty'],
            api_input['rooms']
        )
        
        # Generate elective allocation tables
        elective_tables = formatter.create_elective_allocation_tables(
            result['assignments'],
            api_input['students'],
            api_input['courses']
        )
        
        # Create API response
        api_response = {
            "success": True,
            "message": "Timetable generated successfully",
            "institute_id": api_input["institute_id"],
            "semester": api_input["semester"],
            "optimization_time": result["optimization_time"],
            "metrics": {
                "student_satisfaction": result["student_satisfaction"],
                "faculty_workload_balance": result["faculty_workload_balance"],
                "room_utilization": result["room_utilization"],
                "elective_allocation_rate": result["elective_allocation_rate"]
            },
            "assignments": result["assignments"],
            "schedule_table": schedule_df.to_dict('records'),
            "elective_allocations": {
                f"priority_{i}": elective_tables[f"priority_{i}"].to_dict('records')
                for i in range(1, 6)
            },
            "summary": {
                "total_assignments": len(result["assignments"]),
                "core_assignments": len([a for a in result["assignments"] if not a.get("is_elective", False)]),
                "elective_assignments": len([a for a in result["assignments"] if a.get("is_elective", False)]),
                "faculty_workload": {},
                "room_utilization": {},
                "elective_by_priority": {}
            }
        }
        
        print(json.dumps(api_response, indent=2, default=str))
        
        # ========================================
        # TABULAR OUTPUT (Human-readable format)
        # ========================================
        
        print("\n📊 TABULAR SCHEDULE OUTPUT:")
        print("=" * 80)
        print(schedule_df.to_string(index=False))
        
        print("\n🎯 ELECTIVE ALLOCATION TABLES:")
        print("=" * 80)
        
        for priority, table in elective_tables.items():
            priority_num = priority.split('_')[1]
            print(f"\n📋 PRIORITY {priority_num} ELECTIVES:")
            print("-" * 60)
            if not table.empty:
                print(table.to_string(index=False))
            else:
                print("No students allocated to this priority level")
        
        # ========================================
        # DATABASE TABLES (What gets saved to DB)
        # ========================================
        
        print("\n💾 DATABASE TABLES TO CREATE:")
        print("=" * 50)
        
        print("\n1. MAIN_SCHEDULE table:")
        print("   - assignment_id (PK)")
        print("   - institute_id")
        print("   - semester")
        print("   - course_id")
        print("   - faculty_id")
        print("   - room_id")
        print("   - day")
        print("   - period")
        print("   - start_time")
        print("   - end_time")
        print("   - students_enrolled")
        print("   - is_elective")
        print("   - created_at")
        
        print("\n2. ELECTIVE_ALLOCATIONS table:")
        print("   - allocation_id (PK)")
        print("   - institute_id")
        print("   - student_id")
        print("   - course_id")
        print("   - priority")
        print("   - assignment_id (FK)")
        print("   - allocated_at")
        
        print("\n3. PRIORITY_1_ELECTIVES view:")
        print("   - student_id")
        print("   - institute_id")
        print("   - course_code")
        print("   - course_name")
        print("   - priority")
        print("   - department")
        print("   - semester")
        print("   - section")
        
        print("\n4. PRIORITY_2_ELECTIVES view:")
        print("   - (same structure as Priority 1)")
        
        print("\n5. PRIORITY_3_ELECTIVES view:")
        print("   - (same structure as Priority 1)")
        
        print("\n6. PRIORITY_4_ELECTIVES view:")
        print("   - (same structure as Priority 1)")
        
        print("\n7. PRIORITY_5_ELECTIVES view:")
        print("   - (same structure as Priority 1)")
        
    else:
        error_response = {
            "success": False,
            "error": result["error"],
            "message": "Timetable generation failed"
        }
        print(json.dumps(error_response, indent=2))

async def main():
    """Main function."""
    await demonstrate_api_usage()

if __name__ == "__main__":
    asyncio.run(main())

