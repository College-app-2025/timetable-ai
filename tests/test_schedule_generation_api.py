"""
Simple test to generate a schedule with your data
"""

import requests
import json

# Your sample data - replace with your actual data
sample_data = {
    "institute_id": "inst_001",
    "semester": 3,
    "students": [
        {
            "id": "s001",
            "student_id": "STU001",
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "department": "Computer Science",
            "semester": 3,
            "section": "A",
            "preferences": [
                {"course_id": "CS304", "priority": 1},
                {"course_id": "CS305", "priority": 2}
            ]
        },
        {
            "id": "s002",
            "student_id": "STU002", 
            "name": "Bob Smith",
            "email": "bob@example.com",
            "department": "Computer Science",
            "semester": 3,
            "section": "B",
            "preferences": [
                {"course_id": "CS305", "priority": 1},
                {"course_id": "CS304", "priority": 2}
            ]
        }
    ],
    "courses": [
        {
            "id": "CS304",
            "name": "Machine Learning",
            "course_code": "CS304",
            "department": "Computer Science",
            "semester": 3,
            "credits": 3,
            "hours_per_week": 3,
            "course_type": "elective",
            "is_elective": True,
            "max_students_per_section": 30
        },
        {
            "id": "CS305",
            "name": "Web Development",
            "course_code": "CS305", 
            "department": "Computer Science",
            "semester": 3,
            "credits": 3,
            "hours_per_week": 3,
            "course_type": "elective",
            "is_elective": True,
            "max_students_per_section": 30
        }
    ],
    "faculty": [
        {
            "id": "f001",
            "name": "Dr. John Doe",
            "email": "john@example.com",
            "department": "Computer Science",
            "subjects": ["CS304", "CS305"],
            "max_hours_per_week": 20
        }
    ],
    "rooms": [
        {
            "id": "r001",
            "name": "Room 101",
            "room_type": "lecture",
            "capacity": 50,
            "building": "CS Building",
            "floor": 1
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

def test_schedule_generation():
    """Test the schedule generation endpoint."""
    
    print("🚀 TESTING SCHEDULE GENERATION")
    print("=" * 40)
    
    # Save sample data to file
    with open("test_data.json", "w") as f:
        json.dump(sample_data, f, indent=2)
    
    print("📁 Sample data saved to: test_data.json")
    
    # Test endpoint
    url = "http://localhost:8000/api/ml/generate-timetable"
    
    try:
        print(f"\n🔄 Sending request to: {url}")
        response = requests.post(url, json=sample_data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Schedule generated successfully!")
            print(f"   Schedule ID: {result.get('schedule_id')}")
            print(f"   Total Assignments: {result.get('total_assignments')}")
            print(f"   Student Satisfaction: {result.get('student_satisfaction', 0):.3f}")
            print(f"   Faculty Workload Balance: {result.get('faculty_workload_balance', 0):.3f}")
            print(f"   Room Utilization: {result.get('room_utilization', 0):.3f}")
            print(f"   Optimization Time: {result.get('optimization_time', 0):.2f}s")
            
            # Save result
            with open("generated_schedule.json", "w") as f:
                json.dump(result, f, indent=2)
            print("📁 Schedule saved to: generated_schedule.json")
            
            # Show assignments
            assignments = result.get('assignments', [])
            if assignments:
                print(f"\n📅 GENERATED ASSIGNMENTS ({len(assignments)}):")
                for i, assignment in enumerate(assignments, 1):
                    print(f"   {i}. {assignment.get('course_id')} → {assignment.get('faculty_id') → {assignment.get('room_id')} @ {assignment.get('time_slot_id')}")
            
            return result
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the server is running!")
        print("   Run: uvicorn main:app --reload")
        return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

if __name__ == "__main__":
    test_schedule_generation()
