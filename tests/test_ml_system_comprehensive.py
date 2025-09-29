"""
Test script for the SIH Timetable Optimization System.
Validates the complete ML pipeline and generates sample timetables.
"""

import asyncio
import json
from datetime import datetime
from src.ml.core.optimizer import TimetableOptimizer
from src.ml.data.models import OptimizationConfig
from src.ml.data.loaders import load_institute_data
from src.utils.logger_config import get_logger

logger = get_logger("test_ml_system")


async def test_ml_system():
    """Test the complete ML system."""
    try:
        logger.info("Starting ML system test")
        
        # Test 1: Load sample data
        logger.info("Test 1: Loading sample data")
        institute_id = "test_institute_001"
        
        # Create sample data (you would normally load from database)
        sample_data = create_sample_data()
        
        # Test 2: Create optimizer
        logger.info("Test 2: Creating optimizer")
        config = OptimizationConfig()
        optimizer = TimetableOptimizer(config)
        
        # Test 3: Run optimization with sample data
        logger.info("Test 3: Running optimization with sample data")
        
        # Create sample data for testing
        from src.ml.data.models import Student, Course, Faculty, Room, TimeSlot, CourseType, RoomType, Section
        
        # Sample students
        students = [
            Student(
                id="s001",
                student_id="STU001",
                name="Alice Johnson",
                email="alice@example.com",
                department="Computer Science",
                semester=1,
                section="A",
                satisfaction_score=0.8,
                preferences=[]
            ),
            Student(
                id="s002", 
                student_id="STU002",
                name="Bob Smith",
                email="bob@example.com",
                department="Computer Science",
                semester=1,
                section="B",
                satisfaction_score=0.7,
                preferences=[]
            )
        ]
        
        # Sample courses
        courses = [
            Course(
                id="c001",
                course_code="CS101",
                name="Programming Fundamentals",
                department="Computer Science",
                semester=1,
                credits=3,
                hours_per_week=3,
                course_type=CourseType.THEORY,
                is_elective=False,
                max_students_per_section=50,
                prerequisites=[]
            ),
            Course(
                id="c002",
                course_code="CS102",
                name="Data Structures",
                department="Computer Science",
                semester=1,
                credits=4,
                hours_per_week=4,
                course_type=CourseType.THEORY,
                is_elective=False,
                max_students_per_section=40,
                prerequisites=[]
            )
        ]
        
        # Sample faculty
        faculty = [
            Faculty(
                id="f001",
                name="Dr. John Doe",
                email="john@example.com",
                department="Computer Science",
                designation="Professor",
                subjects=["c001", "c002"],
                max_hours_per_week=20,
                availability={}
            ),
            Faculty(
                id="f002",
                name="Dr. Jane Smith",
                email="jane@example.com",
                department="Computer Science",
                designation="Associate Professor",
                subjects=["c001", "c002"],
                max_hours_per_week=18,
                availability={}
            )
        ]
        
        # Sample rooms
        rooms = [
            Room(
                id="r001",
                name="Room 101",
                room_type=RoomType.LECTURE,
                capacity=50,
                building="Building A",
                floor=1,
                equipment=[]
            ),
            Room(
                id="r002",
                name="Room 102", 
                room_type=RoomType.LECTURE,
                capacity=40,
                building="Building A",
                floor=1,
                equipment=[]
            )
        ]
        
        # Sample time slots
        from datetime import time
        time_slots = [
            TimeSlot(
                id=1,
                day=1,  # Monday
                period=1,
                start_time=time(9, 0),
                end_time=time(10, 0)
            ),
            TimeSlot(
                id=2,
                day=1,  # Monday
                period=2,
                start_time=time(10, 0),
                end_time=time(11, 0)
            ),
            TimeSlot(
                id=3,
                day=2,  # Tuesday
                period=1,
                start_time=time(9, 0),
                end_time=time(10, 0)
            ),
            TimeSlot(
                id=4,
                day=2,  # Tuesday
                period=2,
                start_time=time(10, 0),
                end_time=time(11, 0)
            )
        ]
        
        # Create a mock data dictionary
        mock_data = {
            'students': students,
            'courses': courses,
            'faculty': faculty,
            'rooms': rooms,
            'time_slots': time_slots,
            'student_preferences': []
        }
        
        # Run optimization with mock data
        result = await optimizer.optimize_timetable_with_data(
            institute_id="test_institute_001",
            semester=1,
            config=config,
            data=mock_data
        )
        
        if result["success"]:
            logger.info("✅ Optimization completed successfully!")
            logger.info(f"Generated {len(result['assignments'])} assignments")
            logger.info(f"Student satisfaction: {result['student_satisfaction']:.3f}")
            logger.info(f"Faculty workload balance: {result['faculty_workload_balance']:.3f}")
            logger.info(f"Room utilization: {result['room_utilization']:.3f}")
            logger.info(f"Optimization time: {result['optimization_time']:.2f} seconds")
            
            # Test 4: Generate reports
            logger.info("Test 4: Generating reports")
            generate_test_reports(result)
            
        else:
            logger.error(f"❌ Optimization failed: {result['error']}")
        
        logger.info("ML system test completed")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise


def create_sample_data():
    """Create sample data for testing."""
    # This would normally be loaded from the database
    # For testing, we'll create mock data
    return {
        "students": [
            {
                "id": "student_001",
                "student_id": "S001",
                "name": "John Doe",
                "email": "john@example.com",
                "department": "Computer Science",
                "semester": 3,
                "preferences": [
                    {"course_id": "CS301", "priority": 1},
                    {"course_id": "CS302", "priority": 2},
                    {"course_id": "CS303", "priority": 3}
                ]
            }
        ],
        "courses": [
            {
                "id": "CS301",
                "name": "Data Structures",
                "course_code": "CS301",
                "course_type": "theory",
                "department": "Computer Science",
                "semester": 3,
                "credits": 3,
                "hours_per_week": 3,
                "is_elective": False
            }
        ],
        "faculty": [
            {
                "id": "faculty_001",
                "name": "Dr. Smith",
                "email": "smith@example.com",
                "department": "Computer Science",
                "subjects": ["CS301", "CS302"]
            }
        ],
        "rooms": [
            {
                "id": "room_001",
                "name": "CS101",
                "room_type": "lecture",
                "capacity": 60,
                "building": "CS Building",
                "floor": 1
            }
        ]
    }


def generate_test_reports(result):
    """Generate test reports."""
    try:
        # Create results directory
        import os
        os.makedirs("test_results", exist_ok=True)
        
        # Save optimization result
        with open("test_results/optimization_result.json", "w") as f:
            json.dump(result, f, indent=2, default=str)
        
        # Generate assignment summary
        assignments_summary = {
            "total_assignments": len(result["assignments"]),
            "elective_assignments": sum(1 for a in result["assignments"] if a.get("is_elective", False)),
            "theory_assignments": sum(1 for a in result["assignments"] if not a.get("is_elective", False)),
            "unique_courses": len(set(a["course_id"] for a in result["assignments"])),
            "unique_faculty": len(set(a["faculty_id"] for a in result["assignments"])),
            "unique_rooms": len(set(a["room_id"] for a in result["assignments"]))
        }
        
        with open("test_results/assignments_summary.json", "w") as f:
            json.dump(assignments_summary, f, indent=2)
        
        # Generate CSV report
        import csv
        with open("test_results/assignments.csv", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "course_id", "faculty_id", "room_id", "time_slot_id", "is_elective"])
            writer.writeheader()
            for assignment in result["assignments"]:
                writer.writerow(assignment)
        
        logger.info("✅ Test reports generated successfully")
        
    except Exception as e:
        logger.error(f"Error generating reports: {str(e)}")


async def test_api_endpoints():
    """Test API endpoints."""
    try:
        logger.info("Testing API endpoints")
        
        # This would test the actual API endpoints
        # For now, just log that we would test them
        logger.info("API endpoint testing would be implemented here")
        
    except Exception as e:
        logger.error(f"API test failed: {str(e)}")


if __name__ == "__main__":
    # Run the test
    asyncio.run(test_ml_system())
