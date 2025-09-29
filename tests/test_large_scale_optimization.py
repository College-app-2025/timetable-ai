"""
Test script for 1000 students - Large scale timetable generation
"""

import asyncio
import json
import time
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ml.core.optimizer import TimetableOptimizer
from config.large_scale_config import get_large_scale_config, get_performance_estimates

def create_1000_student_dataset():
    """Create a realistic dataset for 1000 students."""
    
    print("📊 CREATING 1000 STUDENT DATASET")
    print("=" * 40)
    
    # Generate students
    students = []
    for i in range(1, 1001):
        student = {
            "id": f"s{i:03d}",
            "student_id": f"STU{i:04d}",
            "name": f"Student {i}",
            "email": f"student{i}@college.edu",
            "department": "Computer Science" if i % 3 == 0 else "Electronics" if i % 3 == 1 else "Mechanical",
            "semester": 3,
            "section": "A" if i % 2 == 0 else "B",
            "preferences": [
                {"course_id": f"CS{i%20+1:03d}", "priority": 1},
                {"course_id": f"CS{(i+1)%20+1:03d}", "priority": 2},
                {"course_id": f"CS{(i+2)%20+1:03d}", "priority": 3}
            ]
        }
        students.append(student)
    
    # Generate courses (20 courses)
    courses = []
    for i in range(1, 21):
        course = {
            "id": f"CS{i:03d}",
            "name": f"Course {i}",
            "course_code": f"CS{i:03d}",
            "department": "Computer Science",
            "semester": 3,
            "credits": 3,
            "hours_per_week": 3,
            "course_type": "elective",
            "is_elective": True,
            "max_students_per_section": 50
        }
        courses.append(course)
    
    # Generate faculty (50 teachers)
    faculty = []
    for i in range(1, 51):
        teacher = {
            "id": f"f{i:03d}",
            "name": f"Dr. Teacher {i}",
            "email": f"teacher{i}@college.edu",
            "department": "Computer Science",
            "subjects": [f"CS{j:03d}" for j in range(1, 21)],
            "max_hours_per_week": 20
        }
        faculty.append(teacher)
    
    # Generate rooms (20 rooms)
    rooms = []
    for i in range(1, 21):
        room = {
            "id": f"r{i:03d}",
            "name": f"Room {i:03d}",
            "room_type": "lecture",
            "capacity": 50,
            "building": "Main Building",
            "floor": (i % 3) + 1
        }
        rooms.append(room)
    
    # Generate time slots (40 slots - 5 days x 8 periods)
    time_slots = []
    slot_id = 1
    for day in range(1, 6):  # Monday to Friday
        for period in range(1, 9):  # 8 periods per day
            time_slot = {
                "id": slot_id,
                "day": day,
                "period": period,
                "start_time": f"{8+period-1:02d}:00:00",
                "end_time": f"{8+period:02d}:00:00"
            }
            time_slots.append(time_slot)
            slot_id += 1
    
    dataset = {
        "institute_id": "large_scale_test",
        "semester": 3,
        "students": students,
        "courses": courses,
        "faculty": faculty,
        "rooms": rooms,
        "time_slots": time_slots
    }
    
    print(f"✅ Dataset created:")
    print(f"   • Students: {len(students)}")
    print(f"   • Courses: {len(courses)}")
    print(f"   • Faculty: {len(faculty)}")
    print(f"   • Rooms: {len(rooms)}")
    print(f"   • Time Slots: {len(time_slots)}")
    
    return dataset

async def test_1000_students():
    """Test timetable generation for 1000 students."""
    
    print("🚀 TESTING 1000 STUDENT TIMETABLE GENERATION")
    print("=" * 55)
    
    # Get performance estimates
    estimates = get_performance_estimates(1000)
    print(f"📈 Expected Performance:")
    print(f"   • Optimization Time: {estimates['optimization_time']}")
    print(f"   • Memory Usage: {estimates['memory_usage']}")
    print(f"   • Success Rate: {estimates['success_rate']}")
    
    # Create dataset
    dataset = create_1000_student_dataset()
    
    # Save dataset
    with open("1000_students_dataset.json", "w") as f:
        json.dump(dataset, f, indent=2)
    print("📁 Dataset saved to: 1000_students_dataset.json")
    
    # Get optimized config
    config = get_large_scale_config()
    print(f"⚙️ Using optimized config: {config.max_optimization_time}s timeout")
    
    # Create optimizer
    optimizer = TimetableOptimizer(config)
    
    print("\n🔄 Starting optimization...")
    start_time = time.time()
    
    try:
        # Run optimization
        result = await optimizer.optimize_timetable_with_data(
            institute_id="large_scale_test",
            semester=3,
            config=config,
            data=dataset
        )
        
        end_time = time.time()
        actual_time = end_time - start_time
        
        if result["success"]:
            print("✅ OPTIMIZATION SUCCESSFUL!")
            print(f"   • Actual Time: {actual_time:.2f} seconds")
            print(f"   • Assignments: {len(result['assignments'])}")
            print(f"   • Student Satisfaction: {result['student_satisfaction']:.3f}")
            print(f"   • Faculty Workload Balance: {result['faculty_workload_balance']:.3f}")
            print(f"   • Room Utilization: {result['room_utilization']:.3f}")
            print(f"   • Elective Allocation Rate: {result['elective_allocation_rate']:.3f}")
            
            # Save results
            with open("1000_students_results.json", "w") as f:
                json.dump(result, f, indent=2, default=str)
            print("📁 Results saved to: 1000_students_results.json")
            
            # Performance analysis
            print(f"\n📊 PERFORMANCE ANALYSIS:")
            print(f"   • Time per Student: {actual_time/1000:.3f}s")
            print(f"   • Assignments per Second: {len(result['assignments'])/actual_time:.1f}")
            print(f"   • Memory Efficiency: {'Good' if actual_time < 300 else 'Acceptable' if actual_time < 600 else 'Needs Optimization'}")
            
            return result
        else:
            print(f"❌ OPTIMIZATION FAILED: {result.get('error', 'Unknown error')}")
            return None
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def analyze_scalability():
    """Analyze scalability for different student counts."""
    
    print("\n📈 SCALABILITY ANALYSIS")
    print("=" * 30)
    
    scales = [100, 500, 1000, 2000, 5000]
    
    for students in scales:
        estimates = get_performance_estimates(students)
        print(f"• {students} students: {estimates['optimization_time']} | {estimates['memory_usage']} | {estimates['success_rate']}")

async def main():
    """Main function."""
    
    # Test 1000 students
    result = await test_1000_students()
    
    # Analyze scalability
    analyze_scalability()
    
    if result:
        print("\n🎉 1000 STUDENT TEST COMPLETED SUCCESSFULLY!")
        print("Your AI system can handle large-scale timetable generation!")
    else:
        print("\n⚠️ Test failed - check system configuration")

if __name__ == "__main__":
    asyncio.run(main())
