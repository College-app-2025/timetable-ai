"""
Student Voting Service for Dynamic Reallocation
Handles real-time vote counting and majority detection
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
from src.utils.prisma import db
from src.utils.logger_config import get_logger
from src.services.notification_service import notification_service

logger = get_logger("voting_service")

class StudentVotingService:
    """Service for managing student voting in dynamic reallocation."""
    
    def __init__(self):
        self.logger = logger
        self.voting_timeout = 24 * 60 * 60  # 24 hours in seconds
        self.minimum_votes_required = 5  # Minimum votes for valid result
        self.majority_threshold = 0.5  # 50% + 1 for majority
    
    async def initiate_voting(self, 
                            reallocation_id: str,
                            student_emails: List[str],
                            substitute_professor: str,
                            voting_deadline: Optional[datetime] = None) -> Dict[str, Any]:
        """Initiate voting process for substitute professor."""
        try:
            self.logger.info(f"Initiating voting for reallocation {reallocation_id}")
            
            # Set voting deadline
            if not voting_deadline:
                voting_deadline = datetime.now() + timedelta(hours=24)
            
            # Create voting session
            voting_session = await self._create_voting_session(
                reallocation_id, substitute_professor, voting_deadline
            )
            
            # Send voting notifications to students
            notification_result = await notification_service.send_student_voting_notification(
                student_emails, reallocation_id, substitute_professor
            )
            
            # Start background task to monitor voting
            asyncio.create_task(self._monitor_voting_progress(reallocation_id, voting_deadline))
            
            return {
                "success": True,
                "voting_session_id": voting_session["id"],
                "voting_deadline": voting_deadline.isoformat(),
                "total_students": len(student_emails),
                "notification_result": notification_result
            }
            
        except Exception as e:
            self.logger.error(f"Error initiating voting: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def submit_vote(self, 
                         reallocation_id: str,
                         student_id: str,
                         vote: bool) -> Dict[str, Any]:
        """Submit a student vote."""
        try:
            self.logger.info(f"Student {student_id} voting: {vote}")
            
            # Check if voting is still open
            voting_status = await self._get_voting_status(reallocation_id)
            if not voting_status["is_open"]:
                return {
                    "success": False,
                    "error": "Voting is closed",
                    "deadline": voting_status.get("deadline")
                }
            
            # Check if student already voted
            existing_vote = await db.student_votes.find_unique(
                where={
                    "reallocation_id_student_id": {
                        "reallocation_id": reallocation_id,
                        "student_id": student_id
                    }
                }
            )
            
            if existing_vote:
                return {
                    "success": False,
                    "error": "Student has already voted",
                    "previous_vote": existing_vote["vote"]
                }
            
            # Submit vote
            vote_record = await db.student_votes.create(
                data={
                    "reallocation_id": reallocation_id,
                    "student_id": student_id,
                    "vote": vote
                }
            )
            
            # Check if we have enough votes for a result
            vote_summary = await self._get_vote_summary(reallocation_id)
            
            result = {
                "success": True,
                "vote_id": vote_record["id"],
                "vote_summary": vote_summary,
                "message": "Vote submitted successfully"
            }
            
            # Check for majority
            if vote_summary["total_votes"] >= self.minimum_votes_required:
                majority_result = await self._check_majority(reallocation_id)
                result["majority_result"] = majority_result
                
                if majority_result["has_majority"]:
                    result["message"] = f"Majority reached: {majority_result['majority_side']} wins"
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error submitting vote: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_voting_results(self, reallocation_id: str) -> Dict[str, Any]:
        """Get current voting results."""
        try:
            vote_summary = await self._get_vote_summary(reallocation_id)
            voting_status = await self._get_voting_status(reallocation_id)
            majority_result = await self._check_majority(reallocation_id)
            
            return {
                "success": True,
                "reallocation_id": reallocation_id,
                "vote_summary": vote_summary,
                "voting_status": voting_status,
                "majority_result": majority_result
            }
            
        except Exception as e:
            self.logger.error(f"Error getting voting results: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _create_voting_session(self, 
                                   reallocation_id: str,
                                   substitute_professor: str,
                                   voting_deadline: datetime) -> Dict[str, Any]:
        """Create a voting session record."""
        # For now, we'll use the reallocation_logs table to track voting
        # In a real implementation, you might want a separate VotingSession table
        
        voting_session = {
            "id": f"vote_session_{reallocation_id}",
            "reallocation_id": reallocation_id,
            "substitute_professor": substitute_professor,
            "deadline": voting_deadline,
            "created_at": datetime.now()
        }
        
        return voting_session
    
    async def _get_vote_summary(self, reallocation_id: str) -> Dict[str, Any]:
        """Get summary of votes."""
        try:
            votes = await db.student_votes.find_many(
                where={"reallocation_id": reallocation_id}
            )
            
            yes_votes = sum(1 for vote in votes if vote["vote"])
            no_votes = len(votes) - yes_votes
            total_votes = len(votes)
            
            return {
                "yes_votes": yes_votes,
                "no_votes": no_votes,
                "total_votes": total_votes,
                "yes_percentage": (yes_votes / total_votes * 100) if total_votes > 0 else 0,
                "no_percentage": (no_votes / total_votes * 100) if total_votes > 0 else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error getting vote summary: {str(e)}")
            return {"yes_votes": 0, "no_votes": 0, "total_votes": 0, "yes_percentage": 0, "no_percentage": 0}
    
    async def _get_voting_status(self, reallocation_id: str) -> Dict[str, Any]:
        """Get current voting status."""
        try:
            # Get reallocation log to check deadline
            reallocation_log = await db.reallocation_logs.find_first(
                where={"unavailability_id": reallocation_id}
            )
            
            if not reallocation_log:
                return {"is_open": False, "error": "Reallocation not found"}
            
            # For now, assume voting is open for 24 hours
            # In a real implementation, you'd store the deadline in the database
            is_open = True  # This would be calculated based on stored deadline
            
            return {
                "is_open": is_open,
                "deadline": (datetime.now() + timedelta(hours=24)).isoformat(),
                "time_remaining": "24 hours"  # This would be calculated
            }
            
        except Exception as e:
            self.logger.error(f"Error getting voting status: {str(e)}")
            return {"is_open": False, "error": str(e)}
    
    async def _check_majority(self, reallocation_id: str) -> Dict[str, Any]:
        """Check if majority has been reached."""
        try:
            vote_summary = await self._get_vote_summary(reallocation_id)
            
            if vote_summary["total_votes"] < self.minimum_votes_required:
                return {
                    "has_majority": False,
                    "reason": f"Not enough votes (need {self.minimum_votes_required}, have {vote_summary['total_votes']})"
                }
            
            yes_votes = vote_summary["yes_votes"]
            no_votes = vote_summary["no_votes"]
            total_votes = vote_summary["total_votes"]
            
            # Check for majority
            if yes_votes > no_votes:
                majority_percentage = (yes_votes / total_votes) * 100
                if majority_percentage > (self.majority_threshold * 100):
                    return {
                        "has_majority": True,
                        "majority_side": "yes",
                        "majority_percentage": majority_percentage,
                        "winning_votes": yes_votes,
                        "losing_votes": no_votes
                    }
            elif no_votes > yes_votes:
                majority_percentage = (no_votes / total_votes) * 100
                if majority_percentage > (self.majority_threshold * 100):
                    return {
                        "has_majority": True,
                        "majority_side": "no",
                        "majority_percentage": majority_percentage,
                        "winning_votes": no_votes,
                        "losing_votes": yes_votes
                    }
            
            return {
                "has_majority": False,
                "reason": "No clear majority yet",
                "yes_votes": yes_votes,
                "no_votes": no_votes,
                "total_votes": total_votes
            }
            
        except Exception as e:
            self.logger.error(f"Error checking majority: {str(e)}")
            return {"has_majority": False, "error": str(e)}
    
    async def _monitor_voting_progress(self, reallocation_id: str, voting_deadline: datetime):
        """Monitor voting progress and handle timeout."""
        try:
            self.logger.info(f"Starting voting monitor for {reallocation_id}")
            
            # Wait until deadline
            time_remaining = (voting_deadline - datetime.now()).total_seconds()
            if time_remaining > 0:
                await asyncio.sleep(time_remaining)
            
            # Check final results
            final_results = await self.get_voting_results(reallocation_id)
            
            if final_results["success"]:
                majority_result = final_results["majority_result"]
                
                if majority_result["has_majority"]:
                    # Update reallocation log with final result
                    await db.reallocation_logs.update_many(
                        where={"unavailability_id": reallocation_id},
                        data={
                            "student_votes": {
                                "yes": final_results["vote_summary"]["yes_votes"],
                                "no": final_results["vote_summary"]["no_votes"],
                                "total": final_results["vote_summary"]["total_votes"],
                                "majority": majority_result["majority_side"]
                            },
                            "status": "completed"
                        }
                    )
                    
                    self.logger.info(f"Voting completed for {reallocation_id}: {majority_result['majority_side']} wins")
                else:
                    # No majority - proceed to next step
                    await db.reallocation_logs.update_many(
                        where={"unavailability_id": reallocation_id},
                        data={
                            "student_votes": {
                                "yes": final_results["vote_summary"]["yes_votes"],
                                "no": final_results["vote_summary"]["no_votes"],
                                "total": final_results["vote_summary"]["total_votes"],
                                "majority": "none"
                            },
                            "status": "no_majority"
                        }
                    )
                    
                    self.logger.info(f"Voting completed for {reallocation_id}: No majority reached")
            
        except Exception as e:
            self.logger.error(f"Error monitoring voting progress: {str(e)}")
    
    async def get_voting_statistics(self, institute_id: str) -> Dict[str, Any]:
        """Get voting statistics for an institute."""
        try:
            # Get all reallocation logs for the institute
            reallocations = await db.reallocation_logs.find_many(
                where={"unavailability": {"institute_id": institute_id}}
            )
            
            total_votes = 0
            successful_votes = 0
            failed_votes = 0
            
            for reallocation in reallocations:
                if reallocation.get("student_votes"):
                    votes_data = reallocation["student_votes"]
                    total_votes += votes_data.get("total", 0)
                    
                    if votes_data.get("majority") != "none":
                        successful_votes += 1
                    else:
                        failed_votes += 1
            
            return {
                "success": True,
                "institute_id": institute_id,
                "total_reallocations": len(reallocations),
                "total_votes_cast": total_votes,
                "successful_votes": successful_votes,
                "failed_votes": failed_votes,
                "success_rate": (successful_votes / len(reallocations) * 100) if reallocations else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error getting voting statistics: {str(e)}")
            return {"success": False, "error": str(e)}

# Service instance
voting_service = StudentVotingService()
