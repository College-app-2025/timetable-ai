"""
Example of how to send sample data to the ML system via FastAPI
"""

import requests
import json

# Sample data for testing the ML system
sample_data = {
    "institute_id": "test_institute_001",
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
            "section": "B",
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
            "course_code": "CS102",
            "name": "Data Structures",
            "department": "Computer Science",
            "semester": 1,
            "credits": 4,
            "hours_per_week": 4,
            "course_type": "theory",
            "is_elective": False,
            "max_students_per_section": 40,
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
        },
        {
            "id": "f002",
            "name": "Dr. Jane Smith",
            "email": "jane@example.com",
            "department": "Computer Science", 
            "designation": "Associate Professor",
            "subjects": ["c001", "c002"],
            "max_hours_per_week": 18,
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
        },
        {
            "id": "r002",
            "name": "Room 102",
            "room_type": "lecture", 
            "capacity": 40,
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
        },
        {
            "id": 3,
            "day": 2,  # Tuesday
            "period": 1,
            "start_time": "09:00:00", 
            "end_time": "10:00:00"
        },
        {
            "id": 4,
            "day": 2,  # Tuesday
            "period": 2,
            "start_time": "10:00:00",
            "end_time": "11:00:00"
        }
    ],
    "student_preferences": []
}

# Send data to the ML system
def send_sample_data():
    url = "http://localhost:8000/api/generate-timetable"
    
    try:
        response = requests.post(url, json=sample_data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Timetable generated successfully!")
            print(f"Generated {len(result.get('assignments', []))} assignments")
            print(f"Student satisfaction: {result.get('student_satisfaction', 0):.3f}")
            print(f"Faculty workload balance: {result.get('faculty_workload_balance', 0):.3f}")
            print(f"Room utilization: {result.get('room_utilization', 0):.3f}")
            print(f"Optimization time: {result.get('optimization_time', 0):.2f} seconds")
            
            # Save the result
            with open("generated_timetable.json", "w") as f:
                json.dump(result, f, indent=2)
            print("📁 Timetable saved to generated_timetable.json")
            
            return result
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"❌ Error sending data: {str(e)}")
        return None

if __name__ == "__main__":
    send_sample_data()
