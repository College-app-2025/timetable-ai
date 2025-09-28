from typing import List, Dict, Any
from datetime import datetime

from src.utils.prisma import db


class TimetableService:
    """Service to persist schedules, assignments and elective allocations."""

    async def save_schedule(self, schedule: Dict[str, Any], assignments: List[Dict[str, Any]], allocations: List[Dict[str, Any]] | None = None) -> Dict[str, Any]:
        await db.connect()

        created_schedule = await db.schedules.create(
            data={
                "id": schedule["id"],
                "institute_id": schedule["institute_id"],
                "semester": schedule["semester"],
                "is_optimized": schedule.get("is_optimized", True),
                "optimization_score": schedule.get("optimization_score", 0),
            }
        )

        # Bulk create assignments
        if assignments:
            for a in assignments:
                await db.assignments.create(
                    data={
                        "schedule_id": created_schedule.id,
                        "course_id": a["course_id"],
                        "faculty_id": a["faculty_id"],
                        "room_id": a["room_id"],
                        "time_slot_id": str(a["time_slot_id"]),
                        "section_id": a.get("section_id", ""),
                        "student_count": int(a.get("student_count", 0)),
                        "is_elective": bool(a.get("is_elective", False)),
                        "priority_score": float(a.get("priority_score", 0)),
                    }
                )

        # Save elective allocations if provided
        if allocations:
            for e in allocations:
                await db.student_elective_allocations.create(
                    data={
                        "institute_id": e["institute_id"],
                        "schedule_id": created_schedule.id,
                        "student_id": e["student_id"],
                        "course_id": e["course_id"],
                        "preference_rank": int(e.get("preference_rank", 0)),
                        "satisfaction": float(e.get("satisfaction", 0)),
                    }
                )

        return {"schedule_id": created_schedule.id}


timetable_service = TimetableService()


