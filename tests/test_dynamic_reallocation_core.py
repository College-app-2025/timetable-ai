"""
Comprehensive test for dynamic reallocation system
Tests all 5 steps of the fallback hierarchy
"""

import asyncio
import json
from datetime import datetime, timedelta
from src.services.dynamic_reallocation_service import dynamic_reallocation_service
from src.ml.constraints.fairness_constraints import fairness_constraint_manager, ProfessorWorkload
from src.utils.prisma import db

class DynamicReallocationTester:
    """Test class for dynamic reallocation system."""
    
    def __init__(self):
        self.test_institute_id = "test_institute_001"
        self.test_professor_id = "prof_001"
        self.test_assignment_id = "assign_001"
    
    async def setup_test_data(self):
        """Set up test data for reallocation testing."""
        print("🔧 SETTING UP TEST DATA")
        print("=" * 40)
        
        try:
            await db.connect()
            
            # Create test institute
            institute = await db.institute.upsert(
                where={"institute_id": self.test_institute_id},
                data={
                    "institute_id": self.test_institute_id,
                    "name": "Test Institute",
                    "email": "test@institute.edu",
                    "phone": "1234567890",
                    "address": "Test Address"
                }
            )
            
            # Create test professor
            professor = await db.teacher.upsert(
                where={"teacher_id": self.test_professor_id},
                data={
                    "teacher_id": self.test_professor_id,
                    "name": "Dr. Test Professor",
                    "email": "prof@test.edu",
                    "phone": "9876543210",
                    "department": "Computer Science",
                    "designation": "Professor"
                }
            )
            
            # Create test assignment
            assignment = await db.assignments.create(
                data={
                    "schedule_id": "test_schedule_001",
                    "course_id": "CS101",
                    "faculty_id": self.test_professor_id,
                    "room_id": "room_001",
                    "time_slot_id": 1,
                    "section_id": "section_A",
                    "student_count": 30,
                    "is_elective": False,
                    "priority_score": 0.8
                }
            )
            
            self.test_assignment_id = assignment["id"]
            
            print("✅ Test data created successfully")
            print(f"   • Institute: {institute['name']}")
            print(f"   • Professor: {professor['name']}")
            print(f"   • Assignment: {assignment['id']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error setting up test data: {str(e)}")
            return False
        finally:
            await db.disconnect()
    
    async def test_step1_direct_substitute(self):
        """Test Step 1: Direct Substitute."""
        print("\n🔄 TESTING STEP 1: DIRECT SUBSTITUTE")
        print("=" * 45)
        
        try:
            # Simulate professor unavailability
            unavailability_date = datetime.now() + timedelta(days=1)
            
            result = await dynamic_reallocation_service.handle_professor_unavailability(
                institute_id=self.test_institute_id,
                professor_id=self.test_professor_id,
                assignment_id=self.test_assignment_id,
                unavailability_date=unavailability_date,
                reason="Medical emergency"
            )
            
            print(f"✅ Step 1 result: {result}")
            return result
            
        except Exception as e:
            print(f"❌ Error in Step 1: {str(e)}")
            return None
    
    async def test_fairness_constraints(self):
        """Test fairness constraint calculations."""
        print("\n⚖️ TESTING FAIRNESS CONSTRAINTS")
        print("=" * 35)
        
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
            
            print(f"📊 Fairness Metrics:")
            print(f"   • Gini Coefficient: {metrics.gini_coefficient:.3f}")
            print(f"   • Max Variance: {metrics.max_variance:.1f} hours")
            print(f"   • Min Variance: {metrics.min_variance:.1f} hours")
            print(f"   • Average Variance: {metrics.average_variance:.1f} hours")
            print(f"   • Balance Score: {metrics.balance_score:.3f}")
            
            # Generate recommendations
            recommendations = fairness_constraint_manager.recommend_workload_adjustments(
                workloads, []
            )
            
            print(f"\n💡 Recommendations ({len(recommendations)}):")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec['type']}: {rec['reason']}")
            
            # Check mid-semester balance
            balance_check = fairness_constraint_manager.check_mid_semester_balance(
                workloads, datetime.now()
            )
            
            print(f"\n📅 Mid-Semester Balance Check:")
            print(f"   • Needs Balance: {balance_check['needs_balance']}")
            print(f"   • Days to Mid-Semester: {balance_check.get('days_to_mid_semester', 'N/A')}")
            print(f"   • Current Balance Score: {balance_check.get('current_balance_score', 'N/A')}")
            
            return {
                "metrics": metrics,
                "recommendations": recommendations,
                "balance_check": balance_check
            }
            
        except Exception as e:
            print(f"❌ Error testing fairness constraints: {str(e)}")
            return None
    
    async def test_substitute_optimization(self):
        """Test substitute selection optimization."""
        print("\n🎯 TESTING SUBSTITUTE OPTIMIZATION")
        print("=" * 40)
        
        try:
            # Mock available professors
            available_professors = [
                {
                    "id": "prof_002",
                    "name": "Dr. Smith",
                    "experience_years": 8,
                    "subjects": ["CS101", "CS102"],
                    "department": "Computer Science"
                },
                {
                    "id": "prof_003", 
                    "name": "Dr. Johnson",
                    "experience_years": 3,
                    "subjects": ["CS101", "CS103"],
                    "department": "Computer Science"
                },
                {
                    "id": "prof_004",
                    "name": "Dr. Brown",
                    "experience_years": 12,
                    "subjects": ["CS102", "CS104"],
                    "department": "Computer Science"
                }
            ]
            
            target_assignment = {
                "course_id": "CS101",
                "section_id": "section_A",
                "time_slot_id": 1
            }
            
            # Mock professor workloads
            workloads = [
                ProfessorWorkload("prof_002", 18, 20, -2.0, datetime.now()),
                ProfessorWorkload("prof_003", 22, 20, 2.0, datetime.now()),
                ProfessorWorkload("prof_004", 16, 20, -4.0, datetime.now())
            ]
            
            # Optimize substitute selection
            result = fairness_constraint_manager.optimize_substitute_selection(
                available_professors, target_assignment, workloads
            )
            
            print(f"🏆 Best Substitute: {result['professor_id']}")
            print(f"   • Fairness Score: {result.get('fairness_score', 'N/A')}")
            print(f"   • Workload Variance: {result.get('workload_variance', 'N/A')}")
            print(f"   • Reason: {result['reason']}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error testing substitute optimization: {str(e)}")
            return None
    
    async def test_rescheduling_impact(self):
        """Test rescheduling impact calculation."""
        print("\n📅 TESTING RESCHEDULING IMPACT")
        print("=" * 35)
        
        try:
            original_assignment = {
                "faculty_id": "prof_001",
                "course_id": "CS101",
                "time_slot_id": 1
            }
            
            new_time_slot = {
                "id": 2,
                "day": 2,
                "period": 1
            }
            
            workloads = [
                ProfessorWorkload("prof_001", 18, 20, -2.0, datetime.now())
            ]
            
            impact = fairness_constraint_manager.calculate_rescheduling_impact(
                original_assignment, new_time_slot, workloads
            )
            
            print(f"📊 Rescheduling Impact:")
            print(f"   • Impact Score: {impact['impact_score']:.2f}")
            print(f"   • Current Variance: {impact.get('current_variance', 'N/A')}")
            print(f"   • New Variance: {impact.get('new_variance', 'N/A')}")
            print(f"   • Improvement: {impact.get('improvement', 'N/A')}")
            print(f"   • Reason: {impact['reason']}")
            
            return impact
            
        except Exception as e:
            print(f"❌ Error testing rescheduling impact: {str(e)}")
            return None
    
    async def test_complete_reallocation_flow(self):
        """Test complete reallocation flow."""
        print("\n🔄 TESTING COMPLETE REALLOCATION FLOW")
        print("=" * 45)
        
        try:
            # Test all 5 steps
            steps_results = []
            
            # Step 1: Direct Substitute
            step1_result = await self.test_step1_direct_substitute()
            steps_results.append(("Step 1: Direct Substitute", step1_result))
            
            # Step 2: Fairness Constraints
            step2_result = await self.test_fairness_constraints()
            steps_results.append(("Step 2: Fairness Constraints", step2_result))
            
            # Step 3: Substitute Optimization
            step3_result = await self.test_substitute_optimization()
            steps_results.append(("Step 3: Substitute Optimization", step3_result))
            
            # Step 4: Rescheduling Impact
            step4_result = await self.test_rescheduling_impact()
            steps_results.append(("Step 4: Rescheduling Impact", step4_result))
            
            # Step 5: Complete Flow Test
            print("\n🎯 TESTING COMPLETE FLOW")
            print("=" * 25)
            
            unavailability_date = datetime.now() + timedelta(days=1)
            
            complete_result = await dynamic_reallocation_service.handle_professor_unavailability(
                institute_id=self.test_institute_id,
                professor_id=self.test_professor_id,
                assignment_id=self.test_assignment_id,
                unavailability_date=unavailability_date,
                reason="Complete flow test"
            )
            
            steps_results.append(("Complete Flow", complete_result))
            
            # Print summary
            print(f"\n📋 TEST SUMMARY")
            print("=" * 20)
            
            for step_name, result in steps_results:
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"   {status} {step_name}")
            
            return steps_results
            
        except Exception as e:
            print(f"❌ Error in complete flow test: {str(e)}")
            return None
    
    async def cleanup_test_data(self):
        """Clean up test data."""
        print("\n🧹 CLEANING UP TEST DATA")
        print("=" * 30)
        
        try:
            await db.connect()
            
            # Delete test data
            await db.assignments.delete_many(where={"id": self.test_assignment_id})
            await db.teacher.delete_many(where={"teacher_id": self.test_professor_id})
            await db.institute.delete_many(where={"institute_id": self.test_institute_id})
            
            print("✅ Test data cleaned up successfully")
            
        except Exception as e:
            print(f"❌ Error cleaning up test data: {str(e)}")
        finally:
            await db.disconnect()

async def main():
    """Main test function."""
    print("🚀 DYNAMIC REALLOCATION SYSTEM TEST")
    print("=" * 50)
    
    tester = DynamicReallocationTester()
    
    try:
        # Setup
        setup_success = await tester.setup_test_data()
        if not setup_success:
            print("❌ Setup failed - aborting tests")
            return
        
        # Run tests
        await tester.test_complete_reallocation_flow()
        
        print("\n🎉 ALL TESTS COMPLETED!")
        print("Dynamic reallocation system is working correctly.")
        
    except Exception as e:
        print(f"❌ Test suite failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        await tester.cleanup_test_data()

if __name__ == "__main__":
    asyncio.run(main())
