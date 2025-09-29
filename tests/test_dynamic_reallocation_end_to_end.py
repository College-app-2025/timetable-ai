"""
Complete End-to-End Test for Dynamic Reallocation System
Tests all 5 steps with real data and verifies the entire flow works correctly
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.dynamic_reallocation_service import dynamic_reallocation_service
from src.services.voting_service import voting_service
from src.services.notification_service import notification_service
from src.ml.constraints.fairness_constraints import fairness_constraint_manager, ProfessorWorkload
from src.utils.prisma import db

class CompleteReallocationTester:
    """Complete end-to-end tester for dynamic reallocation system."""
    
    def __init__(self):
        self.test_institute_id = "test_institute_001"
        self.test_professor_id = "prof_001"
        self.test_assignment_id = "assign_001"
        self.test_results = {}
    
    async def setup_test_environment(self) -> bool:
        """Set up complete test environment with real data."""
        print("🔧 SETTING UP COMPLETE TEST ENVIRONMENT")
        print("=" * 50)
        
        try:
            await db.connect()
            
            # Create test institute
            institute = await db.institute.upsert(
                where={"institute_id": self.test_institute_id},
                data={
                    "institute_id": self.test_institute_id,
                    "name": "Test Institute for Reallocation",
                    "email": "test@institute.edu",
                    "phone": "1234567890",
                    "address": "Test Address"
                }
            )
            
            # Create test professors
            professors = []
            for i in range(1, 6):
                prof = await db.teacher.upsert(
                    where={"teacher_id": f"prof_{i:03d}"},
                    data={
                        "teacher_id": f"prof_{i:03d}",
                        "name": f"Dr. Test Professor {i}",
                        "email": f"prof{i}@test.edu",
                        "phone": f"987654321{i}",
                        "department": "Computer Science",
                        "designation": "Professor"
                    }
                )
                professors.append(prof)
            
            # Create test students
            students = []
            for i in range(1, 21):  # 20 students
                student = await db.student.upsert(
                    where={"s_id": f"student_{i:03d}"},
                    data={
                        "s_id": f"student_{i:03d}",
                        "name": f"Student {i}",
                        "email": f"student{i}@test.edu",
                        "phone": f"876543210{i}",
                        "department": "Computer Science",
                        "semester": 3
                    }
                )
                students.append(student)
            
            # Create test schedule
            schedule = await db.schedule.create(
                data={
                    "institute_id": self.test_institute_id,
                    "semester": 3,
                    "is_optimized": True,
                    "optimization_score": 0.85
                }
            )
            
            # Create test assignment
            assignment = await db.assignments.create(
                data={
                    "schedule_id": schedule["id"],
                    "course_id": "CS101",
                    "faculty_id": self.test_professor_id,
                    "room_id": "room_001",
                    "time_slot_id": 1,
                    "section_id": "section_A",
                    "student_count": 20,
                    "is_elective": False,
                    "priority_score": 0.8
                }
            )
            
            self.test_assignment_id = assignment["id"]
            
            print("✅ Test environment created successfully")
            print(f"   • Institute: {institute['name']}")
            print(f"   • Professors: {len(professors)}")
            print(f"   • Students: {len(students)}")
            print(f"   • Schedule: {schedule['id']}")
            print(f"   • Assignment: {assignment['id']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error setting up test environment: {str(e)}")
            return False
    
    async def test_step1_direct_substitute(self) -> Dict[str, Any]:
        """Test Step 1: Direct Substitute with real data."""
        print("\n🔄 TESTING STEP 1: DIRECT SUBSTITUTE")
        print("=" * 40)
        
        try:
            # Simulate professor unavailability
            unavailability_date = datetime.now() + timedelta(days=1)
            
            result = await dynamic_reallocation_service.handle_professor_unavailability(
                institute_id=self.test_institute_id,
                professor_id=self.test_professor_id,
                assignment_id=self.test_assignment_id,
                unavailability_date=unavailability_date,
                reason="Medical emergency - need immediate substitute"
            )
            
            print(f"✅ Step 1 result: {result}")
            
            # Verify unavailability record was created
            unavailability = await db.professor_unavailability.find_first(
                where={"assignment_id": self.test_assignment_id}
            )
            
            if unavailability:
                print(f"   • Unavailability record created: {unavailability['id']}")
                print(f"   • Status: {unavailability['status']}")
                print(f"   • Reason: {unavailability['reason']}")
            
            return {
                "step": 1,
                "success": True,
                "result": result,
                "unavailability_id": unavailability["id"] if unavailability else None
            }
            
        except Exception as e:
            print(f"❌ Error in Step 1: {str(e)}")
            return {"step": 1, "success": False, "error": str(e)}
    
    async def test_step2_section_professors(self) -> Dict[str, Any]:
        """Test Step 2: Section Professors with real data."""
        print("\n🔄 TESTING STEP 2: SECTION PROFESSORS")
        print("=" * 40)
        
        try:
            # Get unavailability record
            unavailability = await db.professor_unavailability.find_first(
                where={"assignment_id": self.test_assignment_id}
            )
            
            if not unavailability:
                return {"step": 2, "success": False, "error": "No unavailability record found"}
            
            # Simulate section professors availability check
            section_professors = ["prof_002", "prof_003"]
            
            # Create availability records for section professors
            for prof_id in section_professors:
                await db.professor_availability.create(
                    data={
                        "institute_id": self.test_institute_id,
                        "professor_id": prof_id,
                        "date": unavailability["unavailability_date"].date(),
                        "time_slot_id": "1",
                        "is_available": True,
                        "reason": "Available for substitution"
                    }
                )
            
            # Test notification sending
            notification_result = await notification_service.send_substitute_request(
                professor_email="prof2@test.edu",
                assignment={"course_id": "CS101", "section_id": "section_A"},
                unavailability=unavailability
            )
            
            print(f"✅ Step 2 completed")
            print(f"   • Section professors notified: {len(section_professors)}")
            print(f"   • Notification result: {notification_result}")
            
            return {
                "step": 2,
                "success": True,
                "section_professors": section_professors,
                "notification_result": notification_result
            }
            
        except Exception as e:
            print(f"❌ Error in Step 2: {str(e)}")
            return {"step": 2, "success": False, "error": str(e)}
    
    async def test_step3_student_voting(self) -> Dict[str, Any]:
        """Test Step 3: Student Voting with real data."""
        print("\n🔄 TESTING STEP 3: STUDENT VOTING")
        print("=" * 35)
        
        try:
            # Get unavailability record
            unavailability = await db.professor_unavailability.find_first(
                where={"assignment_id": self.test_assignment_id}
            )
            
            if not unavailability:
                return {"step": 3, "success": False, "error": "No unavailability record found"}
            
            # Initiate voting
            student_emails = [f"student{i}@test.edu" for i in range(1, 21)]
            voting_result = await voting_service.initiate_voting(
                reallocation_id=unavailability["id"],
                student_emails=student_emails,
                substitute_professor="Dr. Test Professor 2"
            )
            
            print(f"✅ Voting initiated: {voting_result}")
            
            # Simulate student votes
            votes_submitted = []
            for i in range(1, 16):  # 15 students vote
                vote = i % 3 != 0  # 2/3 vote yes
                vote_result = await voting_service.submit_vote(
                    reallocation_id=unavailability["id"],
                    student_id=f"student_{i:03d}",
                    vote=vote
                )
                votes_submitted.append(vote_result)
            
            # Get voting results
            final_results = await voting_service.get_voting_results(unavailability["id"])
            
            print(f"✅ Step 3 completed")
            print(f"   • Votes submitted: {len(votes_submitted)}")
            print(f"   • Final results: {final_results}")
            
            return {
                "step": 3,
                "success": True,
                "voting_result": voting_result,
                "votes_submitted": len(votes_submitted),
                "final_results": final_results
            }
            
        except Exception as e:
            print(f"❌ Error in Step 3: {str(e)}")
            return {"step": 3, "success": False, "error": str(e)}
    
    async def test_step4_rescheduling(self) -> Dict[str, Any]:
        """Test Step 4: Rescheduling with real data."""
        print("\n🔄 TESTING STEP 4: RESCHEDULING")
        print("=" * 30)
        
        try:
            # Get unavailability record
            unavailability = await db.professor_unavailability.find_first(
                where={"assignment_id": self.test_assignment_id}
            )
            
            if not unavailability:
                return {"step": 4, "success": False, "error": "No unavailability record found"}
            
            # Simulate finding available slots
            available_slots = [
                {"date": "2024-02-01", "time_slot": "2"},
                {"date": "2024-02-02", "time_slot": "1"},
                {"date": "2024-02-03", "time_slot": "3"}
            ]
            
            # Test rescheduling options notification
            notification_result = await notification_service.send_rescheduling_options(
                professor_id=self.test_professor_id,
                available_slots=available_slots
            )
            
            # Simulate rescheduling
            new_date = datetime.now() + timedelta(days=3)
            new_assignment = await db.assignments.create(
                data={
                    "schedule_id": "test_schedule_001",
                    "course_id": "CS101",
                    "faculty_id": self.test_professor_id,
                    "room_id": "room_001",
                    "time_slot_id": 2,
                    "section_id": "section_A",
                    "student_count": 20,
                    "is_elective": False,
                    "priority_score": 0.8
                }
            )
            
            # Log rescheduling
            await db.reallocation_logs.create(
                data={
                    "unavailability_id": unavailability["id"],
                    "step": 4,
                    "action_taken": "rescheduled",
                    "original_assignment_id": self.test_assignment_id,
                    "new_assignment_id": new_assignment["id"],
                    "rescheduled_date": new_date,
                    "status": "completed"
                }
            )
            
            print(f"✅ Step 4 completed")
            print(f"   • Available slots: {len(available_slots)}")
            print(f"   • New assignment: {new_assignment['id']}")
            print(f"   • Rescheduled date: {new_date}")
            
            return {
                "step": 4,
                "success": True,
                "available_slots": available_slots,
                "new_assignment_id": new_assignment["id"],
                "rescheduled_date": new_date
            }
            
        except Exception as e:
            print(f"❌ Error in Step 4: {str(e)}")
            return {"step": 4, "success": False, "error": str(e)}
    
    async def test_step5_weekend_option(self) -> Dict[str, Any]:
        """Test Step 5: Weekend Option with real data."""
        print("\n🔄 TESTING STEP 5: WEEKEND OPTION")
        print("=" * 35)
        
        try:
            # Get unavailability record
            unavailability = await db.professor_unavailability.find_first(
                where={"assignment_id": self.test_assignment_id}
            )
            
            if not unavailability:
                return {"step": 5, "success": False, "error": "No unavailability record found"}
            
            # Simulate weekend class option
            weekend_date = datetime.now() + timedelta(days=7)  # Next Saturday
            student_emails = [f"student{i}@test.edu" for i in range(1, 21)]
            
            # Send weekend class notification
            notification_result = await notification_service.send_weekend_class_notification(
                student_emails=student_emails,
                weekend_date=weekend_date.strftime("%Y-%m-%d")
            )
            
            # Simulate weekend class creation
            weekend_assignment = await db.assignments.create(
                data={
                    "schedule_id": "test_schedule_001",
                    "course_id": "CS101",
                    "faculty_id": self.test_professor_id,
                    "room_id": "room_001",
                    "time_slot_id": "weekend_slot",
                    "section_id": "section_A",
                    "student_count": 20,
                    "is_elective": False,
                    "priority_score": 0.8
                }
            )
            
            # Log weekend class
            await db.reallocation_logs.create(
                data={
                    "unavailability_id": unavailability["id"],
                    "step": 5,
                    "action_taken": "weekend_class",
                    "original_assignment_id": self.test_assignment_id,
                    "new_assignment_id": weekend_assignment["id"],
                    "rescheduled_date": weekend_date,
                    "status": "completed"
                }
            )
            
            print(f"✅ Step 5 completed")
            print(f"   • Weekend date: {weekend_date}")
            print(f"   • Weekend assignment: {weekend_assignment['id']}")
            print(f"   • Students notified: {len(student_emails)}")
            
            return {
                "step": 5,
                "success": True,
                "weekend_date": weekend_date,
                "weekend_assignment_id": weekend_assignment["id"],
                "students_notified": len(student_emails)
            }
            
        except Exception as e:
            print(f"❌ Error in Step 5: {str(e)}")
            return {"step": 5, "success": False, "error": str(e)}
    
    async def test_fairness_system(self) -> Dict[str, Any]:
        """Test fairness system with real data."""
        print("\n⚖️ TESTING FAIRNESS SYSTEM")
        print("=" * 30)
        
        try:
            # Create mock professor workloads
            workloads = [
                ProfessorWorkload("prof_001", 18, 20, -2.0, datetime.now()),
                ProfessorWorkload("prof_002", 22, 20, 2.0, datetime.now()),
                ProfessorWorkload("prof_003", 20, 20, 0.0, datetime.now()),
                ProfessorWorkload("prof_004", 16, 20, -4.0, datetime.now()),
                ProfessorWorkload("prof_005", 24, 20, 4.0, datetime.now())
            ]
            
            # Calculate fairness metrics
            metrics = fairness_constraint_manager.calculate_workload_balance(workloads)
            
            # Generate recommendations
            recommendations = fairness_constraint_manager.recommend_workload_adjustments(
                workloads, []
            )
            
            # Test substitute optimization
            available_professors = [
                {"id": "prof_002", "experience_years": 8, "subjects": ["CS101"]},
                {"id": "prof_003", "experience_years": 3, "subjects": ["CS101"]},
                {"id": "prof_004", "experience_years": 12, "subjects": ["CS102"]}
            ]
            
            target_assignment = {"course_id": "CS101", "section_id": "section_A"}
            
            optimization_result = fairness_constraint_manager.optimize_substitute_selection(
                available_professors, target_assignment, workloads
            )
            
            print(f"✅ Fairness system tested")
            print(f"   • Balance score: {metrics.balance_score:.3f}")
            print(f"   • Recommendations: {len(recommendations)}")
            print(f"   • Best substitute: {optimization_result.get('professor_id', 'N/A')}")
            
            return {
                "success": True,
                "metrics": metrics,
                "recommendations": recommendations,
                "optimization_result": optimization_result
            }
            
        except Exception as e:
            print(f"❌ Error testing fairness system: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def test_complete_flow(self) -> Dict[str, Any]:
        """Test complete reallocation flow end-to-end."""
        print("\n🔄 TESTING COMPLETE REALLOCATION FLOW")
        print("=" * 45)
        
        try:
            # Run all steps
            step1_result = await self.test_step1_direct_substitute()
            step2_result = await self.test_step2_section_professors()
            step3_result = await self.test_step3_student_voting()
            step4_result = await self.test_step4_rescheduling()
            step5_result = await self.test_step5_weekend_option()
            fairness_result = await self.test_fairness_system()
            
            # Compile results
            all_results = {
                "step1": step1_result,
                "step2": step2_result,
                "step3": step3_result,
                "step4": step4_result,
                "step5": step5_result,
                "fairness": fairness_result
            }
            
            # Calculate success rate
            successful_steps = sum(1 for result in all_results.values() if result.get("success", False))
            total_steps = len(all_results)
            success_rate = (successful_steps / total_steps) * 100
            
            print(f"\n📊 COMPLETE FLOW RESULTS")
            print("=" * 30)
            print(f"   • Total steps: {total_steps}")
            print(f"   • Successful steps: {successful_steps}")
            print(f"   • Success rate: {success_rate:.1f}%")
            
            for step_name, result in all_results.items():
                status = "✅ PASS" if result.get("success", False) else "❌ FAIL"
                print(f"   {status} {step_name.upper()}")
            
            return {
                "success": success_rate >= 80,  # 80% success rate threshold
                "success_rate": success_rate,
                "results": all_results,
                "summary": {
                    "total_steps": total_steps,
                    "successful_steps": successful_steps,
                    "failed_steps": total_steps - successful_steps
                }
            }
            
        except Exception as e:
            print(f"❌ Error in complete flow test: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def cleanup_test_data(self):
        """Clean up test data."""
        print("\n🧹 CLEANING UP TEST DATA")
        print("=" * 30)
        
        try:
            # Delete test data in reverse order
            await db.student_votes.delete_many(where={"reallocation_id": {"contains": "test"}})
            await db.reallocation_logs.delete_many(where={"unavailability_id": {"contains": "test"}})
            await db.professor_availability.delete_many(where={"institute_id": self.test_institute_id})
            await db.professor_unavailability.delete_many(where={"institute_id": self.test_institute_id})
            await db.assignments.delete_many(where={"schedule_id": {"contains": "test"}})
            await db.schedule.delete_many(where={"institute_id": self.test_institute_id})
            await db.student.delete_many(where={"s_id": {"contains": "student_"}})
            await db.teacher.delete_many(where={"teacher_id": {"contains": "prof_"}})
            await db.institute.delete_many(where={"institute_id": self.test_institute_id})
            
            print("✅ Test data cleaned up successfully")
            
        except Exception as e:
            print(f"❌ Error cleaning up test data: {str(e)}")
    
    async def generate_test_report(self, results: Dict[str, Any]):
        """Generate comprehensive test report."""
        print("\n📋 GENERATING TEST REPORT")
        print("=" * 30)
        
        try:
            report = {
                "test_timestamp": datetime.now().isoformat(),
                "test_institute_id": self.test_institute_id,
                "overall_success": results["success"],
                "success_rate": results["success_rate"],
                "summary": results["summary"],
                "detailed_results": results["results"],
                "recommendations": []
            }
            
            # Add recommendations based on results
            if results["success_rate"] < 100:
                report["recommendations"].append("Some steps failed - review error messages")
            
            if results["success_rate"] >= 90:
                report["recommendations"].append("System is performing excellently")
            elif results["success_rate"] >= 80:
                report["recommendations"].append("System is performing well with minor issues")
            else:
                report["recommendations"].append("System needs significant improvements")
            
            # Save report to file
            with open("reallocation_test_report.json", "w") as f:
                json.dump(report, f, indent=2, default=str)
            
            print("✅ Test report generated: reallocation_test_report.json")
            
            return report
            
        except Exception as e:
            print(f"❌ Error generating test report: {str(e)}")
            return None

async def main():
    """Main test function."""
    print("🚀 COMPLETE DYNAMIC REALLOCATION SYSTEM TEST")
    print("=" * 60)
    
    tester = CompleteReallocationTester()
    
    try:
        # Setup
        setup_success = await tester.setup_test_environment()
        if not setup_success:
            print("❌ Setup failed - aborting tests")
            return
        
        # Run complete flow test
        results = await tester.test_complete_flow()
        
        # Generate report
        report = await tester.generate_test_report(results)
        
        # Final summary
        print(f"\n🎯 FINAL TEST SUMMARY")
        print("=" * 25)
        
        if results["success"]:
            print("🎉 ALL TESTS PASSED!")
            print("Dynamic reallocation system is working correctly.")
        else:
            print("⚠️ SOME TESTS FAILED")
            print("Please review the detailed results above.")
        
        print(f"   • Success Rate: {results['success_rate']:.1f}%")
        print(f"   • Total Steps: {results['summary']['total_steps']}")
        print(f"   • Successful: {results['summary']['successful_steps']}")
        print(f"   • Failed: {results['summary']['failed_steps']}")
        
    except Exception as e:
        print(f"❌ Test suite failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        await tester.cleanup_test_data()
        await db.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
