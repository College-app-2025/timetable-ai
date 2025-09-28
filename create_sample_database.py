"""
Script to create sample database with realistic data for testing the ML system.
This creates students, courses, faculty, rooms, and time slots with proper relationships.
"""

import asyncio
from src.utils.prisma import db
from datetime import datetime, time
import random

async def create_sample_institute():
    """Create a sample institute."""
    try:
        # Create institute
        institute = await db.institute.create(data={
            "institute_id": "inst_sample_001",
            "name": "Sample Engineering College",
            "type": "engineering",
            "address": "123 College Street, Sample City",
            "phone": "9876543210",
            "email": "admin@samplecollege.edu",
            "password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J.8Qz8K2"  # password: "admin123"
        })
        print(f"✅ Created institute: {institute.name}")
        return institute.institute_id
    except Exception as e:
        print(f"❌ Error creating institute: {e}")
        return None

async def create_sample_students(institute_id: str, num_students: int = 50):
    """Create sample students."""
    students = []
    departments = ["Computer Science", "Electronics", "Mechanical", "Civil", "Electrical"]
    sections = ["A", "B", "C"]
    
    for i in range(1, num_students + 1):
        student = await db.student.create(data={
            "s_id": f"STU{i:03d}",
            "institute_id": institute_id,
            "name": f"Student {i}",
            "email": f"student{i}@samplecollege.edu",
            "password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J.8Qz8K2",  # password: "student123"
            "department": random.choice(departments),
            "semester": random.randint(1, 8),
            "section": random.choice(sections),
            "satisfaction_score": round(random.uniform(0.6, 1.0), 2)
        })
        students.append(student)
    
    print(f"✅ Created {len(students)} students")
    return students

async def create_sample_courses(institute_id: str):
    """Create sample courses with electives."""
    courses = []
    
    # Core courses (non-elective)
    core_courses = [
        {"code": "CS101", "name": "Programming Fundamentals", "credits": 3, "hours": 3, "type": "theory"},
        {"code": "CS102", "name": "Data Structures", "credits": 4, "hours": 4, "type": "theory"},
        {"code": "CS103", "name": "Algorithms", "credits": 4, "hours": 4, "type": "theory"},
        {"code": "CS104", "name": "Database Systems", "credits": 3, "hours": 3, "type": "theory"},
        {"code": "CS105", "name": "Computer Networks", "credits": 3, "hours": 3, "type": "theory"},
        {"code": "CS201", "name": "Software Engineering", "credits": 3, "hours": 3, "type": "theory"},
        {"code": "CS202", "name": "Operating Systems", "credits": 4, "hours": 4, "type": "theory"},
        {"code": "CS203", "name": "Computer Architecture", "credits": 3, "hours": 3, "type": "theory"},
    ]
    
    # Elective courses
    elective_courses = [
        {"code": "CS301", "name": "Machine Learning", "credits": 3, "hours": 3, "type": "theory", "is_elective": True},
        {"code": "CS302", "name": "Artificial Intelligence", "credits": 3, "hours": 3, "type": "theory", "is_elective": True},
        {"code": "CS303", "name": "Web Development", "credits": 3, "hours": 3, "type": "theory", "is_elective": True},
        {"code": "CS304", "name": "Mobile App Development", "credits": 3, "hours": 3, "type": "theory", "is_elective": True},
        {"code": "CS305", "name": "Cybersecurity", "credits": 3, "hours": 3, "type": "theory", "is_elective": True},
        {"code": "CS306", "name": "Cloud Computing", "credits": 3, "hours": 3, "type": "theory", "is_elective": True},
        {"code": "CS307", "name": "Data Science", "credits": 3, "hours": 3, "type": "theory", "is_elective": True},
        {"code": "CS308", "name": "Blockchain Technology", "credits": 3, "hours": 3, "type": "theory", "is_elective": True},
        {"code": "CS309", "name": "IoT Development", "credits": 3, "hours": 3, "type": "theory", "is_elective": True},
        {"code": "CS310", "name": "Game Development", "credits": 3, "hours": 3, "type": "theory", "is_elective": True},
    ]
    
    all_courses = core_courses + elective_courses
    
    for i, course_data in enumerate(all_courses, 1):
        course = await db.subject.create(data={
            "id": f"course_{i:03d}",
            "institute_id": institute_id,
            "course_code": course_data["code"],
            "name": course_data["name"],
            "department": "Computer Science",
            "semester": random.randint(1, 8),
            "credits": course_data["credits"],
            "hours_per_week": course_data["hours"],
            "type": course_data["type"],
            "is_elective": course_data.get("is_elective", False),
            "max_students_per_section": 50 if not course_data.get("is_elective", False) else 30
        })
        courses.append(course)
    
    print(f"✅ Created {len(courses)} courses ({len(elective_courses)} electives)")
    return courses

async def create_sample_faculty(institute_id: str):
    """Create sample faculty."""
    faculty = []
    designations = ["Professor", "Associate Professor", "Assistant Professor", "Lecturer"]
    subjects = [
        ["course_001", "course_002"],  # Prof 1 teaches CS101, CS102
        ["course_002", "course_003"],  # Prof 2 teaches CS102, CS103
        ["course_003", "course_004"],  # Prof 3 teaches CS103, CS104
        ["course_004", "course_005"],  # Prof 4 teaches CS104, CS105
        ["course_005", "course_006"],  # Prof 5 teaches CS105, CS201
        ["course_006", "course_007"],  # Prof 6 teaches CS201, CS202
        ["course_007", "course_008"],  # Prof 7 teaches CS202, CS203
        ["course_008", "course_009"],  # Prof 8 teaches CS203, CS301 (elective)
        ["course_009", "course_010"],  # Prof 9 teaches CS301, CS302 (electives)
        ["course_010", "course_011"],  # Prof 10 teaches CS302, CS303 (electives)
        ["course_011", "course_012"],  # Prof 11 teaches CS303, CS304 (electives)
        ["course_012", "course_013"],  # Prof 12 teaches CS304, CS305 (electives)
        ["course_013", "course_014"],  # Prof 13 teaches CS305, CS306 (electives)
        ["course_014", "course_015"],  # Prof 14 teaches CS306, CS307 (electives)
        ["course_015", "course_016"],  # Prof 15 teaches CS307, CS308 (electives)
    ]
    
    for i in range(1, 16):
        teacher = await db.teacher.create(data={
            "p_id": f"PROF{i:03d}",
            "institute_id": institute_id,
            "name": f"Dr. Professor {i}",
            "email": f"prof{i}@samplecollege.edu",
            "password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J.8Qz8K2",  # password: "prof123"
            "department": "Computer Science",
            "designation": random.choice(designations),
            "subjects": subjects[i-1] if i <= len(subjects) else ["course_001"],
            "max_hours_per_week": random.randint(15, 25)
        })
        faculty.append(teacher)
    
    print(f"✅ Created {len(faculty)} faculty members")
    return faculty

async def create_sample_rooms(institute_id: str):
    """Create sample rooms."""
    rooms = []
    room_types = ["lecture", "lab", "seminar"]
    buildings = ["Building A", "Building B", "Building C"]
    
    for i in range(1, 21):
        room = await db.classroom.create(data={
            "id": f"room_{i:03d}",
            "institute_id": institute_id,
            "name": f"Room {i:03d}",
            "room_type": random.choice(room_types),
            "capacity": random.choice([30, 40, 50, 60, 80, 100]),
            "building": random.choice(buildings),
            "floor": random.randint(1, 4),
            "equipment": ["Projector", "Whiteboard"] if random.choice([True, False]) else ["Projector", "Whiteboard", "Computer"]
        })
        rooms.append(room)
    
    print(f"✅ Created {len(rooms)} rooms")
    return rooms

async def create_sample_time_slots():
    """Create sample time slots."""
    time_slots = []
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    periods = [
        (time(9, 0), time(10, 0)),   # 9:00-10:00
        (time(10, 0), time(11, 0)),  # 10:00-11:00
        (time(11, 0), time(12, 0)),  # 11:00-12:00
        (time(12, 0), time(13, 0)),  # 12:00-13:00 (Lunch break)
        (time(14, 0), time(15, 0)),  # 14:00-15:00
        (time(15, 0), time(16, 0)),  # 15:00-16:00
        (time(16, 0), time(17, 0)),  # 16:00-17:00
    ]
    
    slot_id = 1
    for day_num, day_name in enumerate(days, 1):
        for period_num, (start_time, end_time) in enumerate(periods, 1):
            time_slot = await db.time_slot.create(data={
                "id": slot_id,
                "day": day_num,
                "period": period_num,
                "start_time": start_time,
                "end_time": end_time,
                "is_available": True
            })
            time_slots.append(time_slot)
            slot_id += 1
    
    print(f"✅ Created {len(time_slots)} time slots")
    return time_slots

async def create_sample_data():
    """Create complete sample database."""
    print("🚀 Creating Sample Database...")
    print("=" * 40)
    
    # Create institute
    institute_id = await create_sample_institute()
    if not institute_id:
        return
    
    # Create students
    students = await create_sample_students(institute_id, 50)
    
    # Create courses
    courses = await create_sample_courses(institute_id)
    
    # Create faculty
    faculty = await create_sample_faculty(institute_id)
    
    # Create rooms
    rooms = await create_sample_rooms(institute_id)
    
    # Create time slots
    time_slots = await create_sample_time_slots()
    
    print("\n🎉 Sample Database Created Successfully!")
    print("=" * 40)
    print(f"Institute ID: {institute_id}")
    print(f"Students: {len(students)}")
    print(f"Courses: {len(courses)} ({len([c for c in courses if c.is_elective])} electives)")
    print(f"Faculty: {len(faculty)}")
    print(f"Rooms: {len(rooms)}")
    print(f"Time Slots: {len(time_slots)}")
    
    return {
        "institute_id": institute_id,
        "students": students,
        "courses": courses,
        "faculty": faculty,
        "rooms": rooms,
        "time_slots": time_slots
    }

async def main():
    """Main function to create sample database."""
    try:
        await db.connect()
        sample_data = await create_sample_data()
        return sample_data
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await db.disconnect()

if __name__ == "__main__":
    asyncio.run(main())

