"""
Dynamic Reallocation Service
Handles the 5-step fallback hierarchy for professor unavailability
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
from src.utils.prisma import db
from src.services.notification_service import notification_service
from src.utils.logger_config import get_logger

logger = get_logger("dynamic_reallocation")

class DynamicReallocationService:
    """Service for handling dynamic reallocation of classes when professors are unavailable."""
    
    def __init__(self):
        self.logger = logger
    
    async def handle_professor_unavailability(self, 
                                             institute_id: str,
                                             professor_id: str,
                                             assignment_id: str,
                                             unavailability_date: datetime,
                                             reason: str) -> Dict[str, Any]:
        """
        Main entry point for handling professor unavailability.
        Implements the 5-step fallback hierarchy.
        """
        try:
            self.logger.info(f"Handling unavailability for professor {professor_id}, assignment {assignment_id}")
            
            # Step 0: Create unavailability record
            unavailability = await self._create_unavailability_record(
                institute_id, professor_id, assignment_id, unavailability_date, reason
            )
            
            # Step 1: Direct Substitute
            result = await self._step1_direct_substitute(unavailability)
            if result["success"]:
                return result
            
            # Step 2: Section Professors Availability
            result = await self._step2_section_professors(unavailability)
            if result["success"]:
                return result
            
            # Step 3: Same-Subject Professors with Student Vote
            result = await self._step3_same_subject_professors(unavailability)
            if result["success"]:
                return result
            
            # Step 4: Rescheduling Before Checkpoints
            result = await self._step4_rescheduling(unavailability)
            if result["success"]:
                return result
            
            # Step 5: Weekend Option
            result = await self._step5_weekend_option(unavailability)
            return result
            
        except Exception as e:
            self.logger.error(f"Error in dynamic reallocation: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _create_unavailability_record(self, 
                                          institute_id: str,
                                          professor_id: str,
                                          assignment_id: str,
                                          unavailability_date: datetime,
                                          reason: str) -> Dict[str, Any]:
        """Create unavailability record in database."""
        await db.connect()
        
        unavailability = await db.professor_unavailability.create(
            data={
                "institute_id": institute_id,
                "professor_id": professor_id,
                "assignment_id": assignment_id,
                "unavailability_date": unavailability_date,
                "reason": reason,
                "status": "pending"
            }
        )
        
        return unavailability
    
    async def _step1_direct_substitute(self, unavailability: Dict[str, Any]) -> Dict[str, Any]:
        """Step 1: Direct Substitute (Professor's choice)."""
        try:
            self.logger.info("Step 1: Checking for direct substitute")
            
            # Get assignment details
            assignment = await db.assignments.find_unique(
                where={"id": unavailability["assignment_id"]}
            )
            
            if not assignment:
                return {"success": False, "error": "Assignment not found"}
            
            # For now, return pending - in real implementation, this would:
            # 1. Notify the professor to suggest a substitute
            # 2. Check if suggested substitute is available
            # 3. If available and agrees, assign them
            
            await self._log_reallocation_step(
                unavailability["id"], 1, "direct_substitute_pending", 
                "Waiting for professor to suggest substitute"
            )
            
            return {
                "success": False,  # Continue to next step
                "step": 1,
                "message": "Direct substitute pending - professor needs to suggest substitute"
            }
            
        except Exception as e:
            self.logger.error(f"Error in Step 1: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _step2_section_professors(self, unavailability: Dict[str, Any]) -> Dict[str, Any]:
        """Step 2: Section Professors Availability."""
        try:
            self.logger.info("Step 2: Checking section professors availability")
            
            # Get assignment details
            assignment = await db.assignments.find_unique(
                where={"id": unavailability["assignment_id"]}
            )
            
            if not assignment:
                return {"success": False, "error": "Assignment not found"}
            
            # Find other professors who teach the same section
            section_professors = await self._find_section_professors(
                assignment["section_id"], assignment["course_id"]
            )
            
            # Check availability for each professor
            available_professors = []
            for prof in section_professors:
                if prof["id"] != unavailability["professor_id"]:
                    is_available = await self._check_professor_availability(
                        prof["id"], assignment["time_slot_id"], unavailability["unavailability_date"]
                    )
                    if is_available:
                        available_professors.append(prof)
            
            if available_professors:
                # Notify available professors
                for prof in available_professors:
                    await notification_service.send_substitute_request(
                        prof["email"], assignment, unavailability
                    )
                
                await self._log_reallocation_step(
                    unavailability["id"], 2, "section_professors_notified",
                    f"Notified {len(available_professors)} section professors"
                )
                
                return {
                    "success": False,  # Continue to next step
                    "step": 2,
                    "message": f"Notified {len(available_professors)} section professors"
                }
            else:
                return {"success": False, "message": "No section professors available"}
                
        except Exception as e:
            self.logger.error(f"Error in Step 2: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _step3_same_subject_professors(self, unavailability: Dict[str, Any]) -> Dict[str, Any]:
        """Step 3: Same-Subject Professors with Student Vote."""
        try:
            self.logger.info("Step 3: Checking same-subject professors with student vote")
            
            # Get assignment details
            assignment = await db.assignments.find_unique(
                where={"id": unavailability["assignment_id"]}
            )
            
            if not assignment:
                return {"success": False, "error": "Assignment not found"}
            
            # Find professors who teach the same subject
            same_subject_professors = await self._find_same_subject_professors(
                assignment["course_id"], unavailability["professor_id"]
            )
            
            # Check availability
            available_professors = []
            for prof in same_subject_professors:
                is_available = await self._check_professor_availability(
                    prof["id"], assignment["time_slot_id"], unavailability["unavailability_date"]
                )
                if is_available:
                    available_professors.append(prof)
            
            if available_professors:
                # Notify students for voting
                await self._initiate_student_voting(
                    unavailability["id"], available_professors, assignment
                )
                
                await self._log_reallocation_step(
                    unavailability["id"], 3, "student_voting_initiated",
                    f"Student voting initiated for {len(available_professors)} professors"
                )
                
                return {
                    "success": False,  # Continue to next step
                    "step": 3,
                    "message": "Student voting initiated"
                }
            else:
                return {"success": False, "message": "No same-subject professors available"}
                
        except Exception as e:
            self.logger.error(f"Error in Step 3: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _step4_rescheduling(self, unavailability: Dict[str, Any]) -> Dict[str, Any]:
        """Step 4: Rescheduling Before Checkpoints."""
        try:
            self.logger.info("Step 4: Attempting rescheduling before checkpoints")
            
            # Get assignment details
            assignment = await db.assignments.find_unique(
                where={"id": unavailability["assignment_id"]}
            )
            
            if not assignment:
                return {"success": False, "error": "Assignment not found"}
            
            # Find available slots in coming weeks
            available_slots = await self._find_available_slots(
                assignment["section_id"], assignment["course_id"], 
                unavailability["professor_id"], unavailability["unavailability_date"]
            )
            
            if available_slots:
                # Notify professor about rescheduling options
                await notification_service.send_rescheduling_options(
                    unavailability["professor_id"], available_slots
                )
                
                await self._log_reallocation_step(
                    unavailability["id"], 4, "rescheduling_options_sent",
                    f"Found {len(available_slots)} available slots for rescheduling"
                )
                
                return {
                    "success": False,  # Continue to next step
                    "step": 4,
                    "message": f"Rescheduling options sent - {len(available_slots)} slots available"
                }
            else:
                return {"success": False, "message": "No available slots for rescheduling"}
                
        except Exception as e:
            self.logger.error(f"Error in Step 4: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _step5_weekend_option(self, unavailability: Dict[str, Any]) -> Dict[str, Any]:
        """Step 5: Weekend Option for Students."""
        try:
            self.logger.info("Step 5: Offering weekend option to students")
            
            # Get assignment details
            assignment = await db.assignments.find_unique(
                where={"id": unavailability["assignment_id"]}
            )
            
            if not assignment:
                return {"success": False, "error": "Assignment not found"}
            
            # Notify students about weekend option
            await self._initiate_weekend_voting(unavailability["id"], assignment)
            
            await self._log_reallocation_step(
                unavailability["id"], 5, "weekend_option_sent",
                "Weekend class option sent to students"
            )
            
            return {
                "success": False,  # This is the last step
                "step": 5,
                "message": "Weekend option sent to students"
            }
            
        except Exception as e:
            self.logger.error(f"Error in Step 5: {str(e)}")
            return {"success": False, "error": str(e)}
    
    # Helper methods
    async def _find_section_professors(self, section_id: str, course_id: str) -> List[Dict]:
        """Find professors who teach the same section."""
        # This would query the database for professors teaching the same section
        # For now, return empty list
        return []
    
    async def _find_same_subject_professors(self, course_id: str, exclude_professor_id: str) -> List[Dict]:
        """Find professors who teach the same subject."""
        # This would query the database for professors teaching the same course
        # For now, return empty list
        return []
    
    async def _check_professor_availability(self, professor_id: str, time_slot_id: str, date: datetime) -> bool:
        """Check if professor is available at given time slot."""
        # This would check professor availability
        # For now, return True
        return True
    
    async def _initiate_student_voting(self, unavailability_id: str, professors: List[Dict], assignment: Dict) -> None:
        """Initiate student voting for substitute professor."""
        # This would send notifications to students and set up voting
        pass
    
    async def _find_available_slots(self, section_id: str, course_id: str, professor_id: str, after_date: datetime) -> List[Dict]:
        """Find available slots for rescheduling."""
        # This would find available time slots in the coming weeks
        return []
    
    async def _initiate_weekend_voting(self, unavailability_id: str, assignment: Dict) -> None:
        """Initiate weekend class voting."""
        # This would send weekend class option to students
        pass
    
    async def _log_reallocation_step(self, unavailability_id: str, step: int, action: str, details: str) -> None:
        """Log reallocation step."""
        await db.reallocation_logs.create(
            data={
                "unavailability_id": unavailability_id,
                "step": step,
                "action_taken": action,
                "status": "pending"
            }
        )

# Service instance
dynamic_reallocation_service = DynamicReallocationService()
