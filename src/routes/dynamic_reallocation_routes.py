"""
FastAPI routes for dynamic reallocation system
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime
from pydantic import BaseModel, Field

from src.utils.logger_config import get_logger
from src.services.dynamic_reallocation_service import dynamic_reallocation_service
from src.services.notification_service import notification_service
from src.utils.prisma import db

logger = get_logger("dynamic_reallocation_routes")
router = APIRouter()
security = HTTPBearer()

# Pydantic models for request/response
class ProfessorUnavailabilityRequest(BaseModel):
    """Request model for professor unavailability."""
    institute_id: str
    professor_id: str
    assignment_id: str
    unavailability_date: datetime
    reason: str

class SubstituteAssignmentRequest(BaseModel):
    """Request model for assigning substitute."""
    unavailability_id: str
    substitute_professor_id: str
    professor_approval: bool

class StudentVoteRequest(BaseModel):
    """Request model for student voting."""
    reallocation_id: str
    student_id: str
    vote: bool

class ReschedulingRequest(BaseModel):
    """Request model for rescheduling."""
    unavailability_id: str
    new_time_slot_id: str
    new_date: datetime
    professor_approval: bool

class WeekendClassRequest(BaseModel):
    """Request model for weekend class."""
    unavailability_id: str
    weekend_date: datetime
    student_approval: bool

# Authentication dependency
async def get_current_institute(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current institute from JWT token."""
    # This would validate JWT and return institute info
    # For now, return mock data
    return {"institute_id": "test_institute", "name": "Test Institute"}

@router.post('/professor-unavailability')
async def report_professor_unavailability(
    request: ProfessorUnavailabilityRequest,
    background_tasks: BackgroundTasks,
    current_institute: Dict[str, Any] = Depends(get_current_institute)
):
    """
    Report professor unavailability and trigger dynamic reallocation.
    """
    try:
        logger.info(f"Professor {request.professor_id} reporting unavailability")
        
        # Trigger dynamic reallocation in background
        background_tasks.add_task(
            dynamic_reallocation_service.handle_professor_unavailability,
            request.institute_id,
            request.professor_id,
            request.assignment_id,
            request.unavailability_date,
            request.reason
        )
        
        return {
            "success": True,
            "message": "Unavailability reported. Dynamic reallocation process initiated.",
            "status": "processing"
        }
        
    except Exception as e:
        logger.error(f"Error reporting unavailability: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/assign-direct-substitute')
async def assign_direct_substitute(
    request: SubstituteAssignmentRequest,
    current_institute: Dict[str, Any] = Depends(get_current_institute)
):
    """
    Assign direct substitute (Step 1).
    """
    try:
        logger.info(f"Assigning direct substitute for unavailability {request.unavailability_id}")
        
        # Check if substitute is available
        unavailability = await db.professor_unavailability.find_unique(
            where={"id": request.unavailability_id}
        )
        
        if not unavailability:
            raise HTTPException(status_code=404, detail="Unavailability record not found")
        
        assignment = await db.assignments.find_unique(
            where={"id": unavailability["assignment_id"]}
        )
        
        if not assignment:
            raise HTTPException(status_code=404, detail="Assignment not found")
        
        # Update assignment with substitute
        updated_assignment = await db.assignments.update(
            where={"id": assignment["id"]},
            data={"faculty_id": request.substitute_professor_id}
        )
        
        # Log the reallocation
        await db.reallocation_logs.create(
            data={
                "unavailability_id": request.unavailability_id,
                "step": 1,
                "action_taken": "substitute_assigned",
                "substitute_professor_id": request.substitute_professor_id,
                "original_assignment_id": assignment["id"],
                "status": "completed"
            }
        )
        
        # Update unavailability status
        await db.professor_unavailability.update(
            where={"id": request.unavailability_id},
            data={"status": "resolved"}
        )
        
        return {
            "success": True,
            "message": "Direct substitute assigned successfully",
            "assignment_id": updated_assignment["id"],
            "substitute_professor_id": request.substitute_professor_id
        }
        
    except Exception as e:
        logger.error(f"Error assigning direct substitute: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/student-vote')
async def submit_student_vote(
    request: StudentVoteRequest,
    current_institute: Dict[str, Any] = Depends(get_current_institute)
):
    """
    Submit student vote for substitute professor (Step 3).
    """
    try:
        logger.info(f"Student {request.student_id} voting: {request.vote}")
        
        # Create or update student vote
        vote = await db.student_votes.upsert(
            where={
                "reallocation_id_student_id": {
                    "reallocation_id": request.reallocation_id,
                    "student_id": request.student_id
                }
            },
            data={
                "reallocation_id": request.reallocation_id,
                "student_id": request.student_id,
                "vote": request.vote
            }
        )
        
        # Check if majority has voted
        votes = await db.student_votes.find_many(
            where={"reallocation_id": request.reallocation_id}
        )
        
        if len(votes) >= 10:  # Assuming minimum 10 students for majority
            yes_votes = sum(1 for v in votes if v["vote"])
            no_votes = len(votes) - yes_votes
            
            if yes_votes > no_votes:
                # Majority says yes - assign substitute
                await db.reallocation_logs.update(
                    where={"id": request.reallocation_id},
                    data={
                        "student_votes": {"yes": yes_votes, "no": no_votes, "total": len(votes)},
                        "status": "completed"
                    }
                )
                
                return {
                    "success": True,
                    "message": "Majority vote completed - substitute will be assigned",
                    "vote_result": {"yes": yes_votes, "no": no_votes, "total": len(votes)}
            else:
                return {
                    "success": True,
                    "message": "Majority vote completed - proceeding to next step",
                    "vote_result": {"yes": yes_votes, "no": no_votes, "total": len(votes)}
                }
        
        return {
            "success": True,
            "message": "Vote recorded. Waiting for more votes.",
            "current_votes": len(votes)
        }
        
    except Exception as e:
        logger.error(f"Error submitting student vote: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/reschedule-class')
async def reschedule_class(
    request: ReschedulingRequest,
    current_institute: Dict[str, Any] = Depends(get_current_institute)
):
    """
    Reschedule class to new time slot (Step 4).
    """
    try:
        logger.info(f"Rescheduling class for unavailability {request.unavailability_id}")
        
        # Get unavailability record
        unavailability = await db.professor_unavailability.find_unique(
            where={"id": request.unavailability_id}
        )
        
        if not unavailability:
            raise HTTPException(status_code=404, detail="Unavailability record not found")
        
        # Update assignment with new time slot
        assignment = await db.assignments.find_unique(
            where={"id": unavailability["assignment_id"]}
        )
        
        if not assignment:
            raise HTTPException(status_code=404, detail="Assignment not found")
        
        # Create new assignment for rescheduled class
        new_assignment = await db.assignments.create(
            data={
                "schedule_id": assignment["schedule_id"],
                "course_id": assignment["course_id"],
                "faculty_id": assignment["faculty_id"],
                "room_id": assignment["room_id"],
                "time_slot_id": request.new_time_slot_id,
                "section_id": assignment["section_id"],
                "student_count": assignment["student_count"],
                "is_elective": assignment["is_elective"],
                "priority_score": assignment["priority_score"]
            }
        )
        
        # Log the rescheduling
        await db.reallocation_logs.create(
            data={
                "unavailability_id": request.unavailability_id,
                "step": 4,
                "action_taken": "rescheduled",
                "original_assignment_id": assignment["id"],
                "new_assignment_id": new_assignment["id"],
                "rescheduled_date": request.new_date,
                "status": "completed"
            }
        )
        
        # Update unavailability status
        await db.professor_unavailability.update(
            where={"id": request.unavailability_id},
            data={"status": "resolved"}
        )
        
        return {
            "success": True,
            "message": "Class rescheduled successfully",
            "new_assignment_id": new_assignment["id"],
            "rescheduled_date": request.new_date
        }
        
    except Exception as e:
        logger.error(f"Error rescheduling class: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/weekend-class')
async def schedule_weekend_class(
    request: WeekendClassRequest,
    current_institute: Dict[str, Any] = Depends(get_current_institute)
):
    """
    Schedule weekend class (Step 5).
    """
    try:
        logger.info(f"Scheduling weekend class for unavailability {request.unavailability_id}")
        
        # Get unavailability record
        unavailability = await db.professor_unavailability.find_unique(
            where={"id": request.unavailability_id}
        )
        
        if not unavailability:
            raise HTTPException(status_code=404, detail="Unavailability record not found")
        
        # Create weekend assignment
        assignment = await db.assignments.find_unique(
            where={"id": unavailability["assignment_id"]}
        )
        
        if not assignment:
            raise HTTPException(status_code=404, detail="Assignment not found")
        
        # Create weekend assignment
        weekend_assignment = await db.assignments.create(
            data={
                "schedule_id": assignment["schedule_id"],
                "course_id": assignment["course_id"],
                "faculty_id": assignment["faculty_id"],
                "room_id": assignment["room_id"],
                "time_slot_id": "weekend_slot",  # Special weekend slot
                "section_id": assignment["section_id"],
                "student_count": assignment["student_count"],
                "is_elective": assignment["is_elective"],
                "priority_score": assignment["priority_score"]
            }
        )
        
        # Log the weekend class
        await db.reallocation_logs.create(
            data={
                "unavailability_id": request.unavailability_id,
                "step": 5,
                "action_taken": "weekend_class",
                "original_assignment_id": assignment["id"],
                "new_assignment_id": weekend_assignment["id"],
                "rescheduled_date": request.weekend_date,
                "status": "completed"
            }
        )
        
        # Update unavailability status
        await db.professor_unavailability.update(
            where={"id": request.unavailability_id},
            data={"status": "resolved"}
        )
        
        return {
            "success": True,
            "message": "Weekend class scheduled successfully",
            "weekend_assignment_id": weekend_assignment["id"],
            "weekend_date": request.weekend_date
        }
        
    except Exception as e:
        logger.error(f"Error scheduling weekend class: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/reallocation-status/{unavailability_id}')
async def get_reallocation_status(
    unavailability_id: str,
    current_institute: Dict[str, Any] = Depends(get_current_institute)
):
    """
    Get current status of reallocation process.
    """
    try:
        # Get unavailability record
        unavailability = await db.professor_unavailability.find_unique(
            where={"id": unavailability_id}
        )
        
        if not unavailability:
            raise HTTPException(status_code=404, detail="Unavailability record not found")
        
        # Get reallocation logs
        logs = await db.reallocation_logs.find_many(
            where={"unavailability_id": unavailability_id},
            order_by={"created_at": "asc"}
        )
        
        return {
            "unavailability_id": unavailability_id,
            "status": unavailability["status"],
            "current_step": len(logs),
            "logs": logs,
            "last_updated": unavailability["updated_at"]
        }
        
    except Exception as e:
        logger.error(f"Error getting reallocation status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/fairness-report/{institute_id}')
async def get_fairness_report(
    institute_id: str,
    current_institute: Dict[str, Any] = Depends(get_current_institute)
):
    """
    Get fairness report for teaching hours balance.
    """
    try:
        # This would implement fairness logic
        # For now, return mock data
        return {
            "institute_id": institute_id,
            "fairness_score": 0.85,
            "professor_workloads": [
                {"professor_id": "prof1", "hours": 18, "expected": 20},
                {"professor_id": "prof2", "hours": 22, "expected": 20}
            ],
            "recommendations": [
                "Professor 1 needs 2 more hours",
                "Professor 2 has 2 extra hours - consider swapping"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting fairness report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
