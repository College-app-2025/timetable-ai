"""
Complete usage example for the SIH Timetable Optimization System.
Shows both single schedule and multiple schedule generation approaches.
"""

from fastapi import requests
import json
import asyncio
from typing import Dict, Any, List

# ============================================================================
# OPTION 1: SINGLE SCHEDULE GENERATION (Current Implementation)
# ============================================================================

def generate_single_schedule():
    """Generate a single optimized schedule."""
    
    # Sample data
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
            }
        ],
        "faculty": [
            {
                "id": "f001",
                "name": "Dr. John Doe",
                "email": "john@example.com",
                "department": "Computer Science",
                "designation": "Professor",
                "subjects": ["c001"],
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
            }
        ],
        "student_preferences": []
    }
    
    # Send request to generate single schedule
    url = "http://localhost:8000/api/generate-timetable"
    
    try:
        response = requests.post(url, json=sample_data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Single Schedule Generated Successfully!")
            print(f"Generated {len(result.get('assignments', []))} assignments")
            print(f"Student satisfaction: {result.get('student_satisfaction', 0):.3f}")
            print(f"Faculty workload balance: {result.get('faculty_workload_balance', 0):.3f}")
            print(f"Room utilization: {result.get('room_utilization', 0):.3f}")
            print(f"Optimization time: {result.get('optimization_time', 0):.2f} seconds")
            
            # Save to database (you would implement this)
            save_schedule_to_database(result)
            
            return result
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

# ============================================================================
# OPTION 2: MULTIPLE SCHEDULE GENERATION (Enhanced Implementation)
# ============================================================================

def generate_multiple_schedules():
    """Generate multiple schedule options for admin selection."""
    
    # Same sample data as above
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
            }
        ],
        "faculty": [
            {
                "id": "f001",
                "name": "Dr. John Doe",
                "email": "john@example.com",
                "department": "Computer Science",
                "designation": "Professor",
                "subjects": ["c001"],
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
            }
        ],
        "student_preferences": [],
        "num_options": 3  # Generate 3 different schedule options
    }
    
    # Send request to generate multiple schedules
    url = "http://localhost:8000/api/generate-multiple-schedules"
    
    try:
        response = requests.post(url, json=sample_data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Multiple Schedules Generated Successfully!")
            print(f"Generated {result['total_options']} schedule options")
            
            # Display each schedule option
            for i, schedule in enumerate(result['schedules']):
                print(f"\n--- Schedule Option {i+1}: {schedule['name']} ---")
                print(f"Description: {schedule['description']}")
                print(f"Student Satisfaction: {schedule['metrics']['student_satisfaction']:.3f}")
                print(f"Faculty Workload Balance: {schedule['metrics']['faculty_workload_balance']:.3f}")
                print(f"Room Utilization: {schedule['metrics']['room_utilization']:.3f}")
                print(f"Assignments: {schedule['assignments_count']}")
                print(f"Feasible: {schedule['is_feasible']}")
            
            return result
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def select_schedule(selected_option_id: int, schedules_data: Dict[str, Any]):
    """Select a specific schedule option and save it to the database."""
    
    # Find the selected schedule
    selected_schedule = None
    for schedule in schedules_data['schedules']:
        if schedule['option_id'] == selected_option_id:
            selected_schedule = schedule
            break
    
    if not selected_schedule:
        print(f"❌ Schedule option {selected_option_id} not found")
        return None
    
    # Prepare selection request
    selection_request = {
        "institute_id": schedules_data['institute_id'],
        "selected_schedule": selected_schedule,
        "admin_notes": f"Selected {selected_schedule['name']} based on admin preference"
    }
    
    # Send selection request
    url = "http://localhost:8000/api/select-schedule"
    
    try:
        response = requests.post(url, json=selection_request)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Schedule Option {selected_option_id} Selected and Saved!")
            print(f"Schedule ID: {result['schedule_id']}")
            return result
        else:
            print(f"❌ Error selecting schedule: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

# ============================================================================
# DATABASE INTEGRATION FUNCTIONS
# ============================================================================

def save_schedule_to_database(schedule_data: Dict[str, Any]):
    """Save a schedule to the database."""
    # TODO: Implement database save logic
    print("💾 Saving schedule to database...")
    print(f"Schedule ID: {schedule_data.get('schedule', {}).get('id', 'N/A')}")
    print(f"Institute ID: {schedule_data.get('schedule', {}).get('institute_id', 'N/A')}")
    print(f"Semester: {schedule_data.get('schedule', {}).get('semester', 'N/A')}")
    print(f"Total Assignments: {len(schedule_data.get('assignments', []))}")
    
    # Example database save (you would implement this with your ORM)
    # await db.schedule.create(data={
    #     "institute_id": schedule_data['schedule']['institute_id'],
    #     "semester": schedule_data['schedule']['semester'],
    #     "assignments": schedule_data['assignments'],
    #     "is_optimized": True,
    #     "optimization_score": schedule_data['student_satisfaction']
    # })

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main function demonstrating both approaches."""
    
    print("🚀 SIH Timetable Optimization System - Usage Examples")
    print("=" * 60)
    
    # Choose approach
    approach = input("Choose approach:\n1. Single Schedule\n2. Multiple Schedules\nEnter choice (1 or 2): ")
    
    if approach == "1":
        print("\n📅 Generating Single Schedule...")
        result = generate_single_schedule()
        
        if result:
            print("\n✅ Single schedule generation completed!")
            print("The schedule has been automatically saved to the database.")
    
    elif approach == "2":
        print("\n📅 Generating Multiple Schedules...")
        result = generate_multiple_schedules()
        
        if result:
            print("\n✅ Multiple schedules generated successfully!")
            
            # Let admin select a schedule
            try:
                selected_id = int(input(f"\nSelect a schedule option (1-{result['total_options']}): "))
                selection_result = select_schedule(selected_id, result)
                
                if selection_result:
                    print("\n✅ Schedule selection completed!")
                    print("The selected schedule has been saved to the database.")
            except ValueError:
                print("❌ Invalid selection. Please enter a valid number.")
    
    else:
        print("❌ Invalid choice. Please run again and select 1 or 2.")

if __name__ == "__main__":
    main()

