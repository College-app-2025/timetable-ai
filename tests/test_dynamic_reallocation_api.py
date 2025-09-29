"""
Test script for dynamic reallocation API endpoints
Demonstrates how to use the reallocation system via API
"""

import requests
import json
from datetime import datetime, timedelta

# API Configuration
BASE_URL = "http://localhost:8000"
REALLOCATION_URL = f"{BASE_URL}/api/dynamic-reallocation"

# Test data
TEST_INSTITUTE_ID = "test_institute_001"
TEST_PROFESSOR_ID = "prof_001"
TEST_ASSIGNMENT_ID = "assign_001"

def test_professor_unavailability_report():
    """Test reporting professor unavailability."""
    print("🔄 TESTING PROFESSOR UNAVAILABILITY REPORT")
    print("=" * 50)
    
    url = f"{REALLOCATION_URL}/professor-unavailability"
    
    data = {
        "institute_id": TEST_INSTITUTE_ID,
        "professor_id": TEST_PROFESSOR_ID,
        "assignment_id": TEST_ASSIGNMENT_ID,
        "unavailability_date": (datetime.now() + timedelta(days=1)).isoformat(),
        "reason": "Medical emergency - need substitute"
    }
    
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        
        result = response.json()
        print("✅ Unavailability reported successfully!")
        print(f"   • Status: {result['status']}")
        print(f"   • Message: {result['message']}")
        
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error reporting unavailability: {e}")
        return None

def test_direct_substitute_assignment():
    """Test assigning direct substitute."""
    print("\n🎯 TESTING DIRECT SUBSTITUTE ASSIGNMENT")
    print("=" * 45)
    
    url = f"{REALLOCATION_URL}/assign-direct-substitute"
    
    data = {
        "unavailability_id": "test_unavailability_001",
        "substitute_professor_id": "prof_002",
        "professor_approval": True
    }
    
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        
        result = response.json()
        print("✅ Direct substitute assigned successfully!")
        print(f"   • Assignment ID: {result['assignment_id']}")
        print(f"   • Substitute: {result['substitute_professor_id']}")
        
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error assigning direct substitute: {e}")
        return None

def test_student_voting():
    """Test student voting system."""
    print("\n🗳️ TESTING STUDENT VOTING SYSTEM")
    print("=" * 35)
    
    url = f"{REALLOCATION_URL}/student-vote"
    
    # Simulate multiple student votes
    students = ["student_001", "student_002", "student_003", "student_004", "student_005"]
    votes = [True, True, False, True, True]  # 4 yes, 1 no
    
    results = []
    
    for student_id, vote in zip(students, votes):
        data = {
            "reallocation_id": "test_reallocation_001",
            "student_id": student_id,
            "vote": vote
        }
        
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            
            result = response.json()
            results.append(result)
            
            print(f"   • Student {student_id}: {'✅ YES' if vote else '❌ NO'}")
            
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Error with student {student_id}: {e}")
    
    # Check final voting result
    if results:
        final_result = results[-1]
        if "vote_result" in final_result:
            vote_result = final_result["vote_result"]
            print(f"\n📊 Final Vote Result:")
            print(f"   • Yes: {vote_result['yes']}")
            print(f"   • No: {vote_result['no']}")
            print(f"   • Total: {vote_result['total']}")
            print(f"   • Majority: {'✅ YES' if vote_result['yes'] > vote_result['no'] else '❌ NO'}")
    
    return results

def test_class_rescheduling():
    """Test class rescheduling."""
    print("\n📅 TESTING CLASS RESCHEDULING")
    print("=" * 30)
    
    url = f"{REALLOCATION_URL}/reschedule-class"
    
    data = {
        "unavailability_id": "test_unavailability_001",
        "new_time_slot_id": "slot_002",
        "new_date": (datetime.now() + timedelta(days=3)).isoformat(),
        "professor_approval": True
    }
    
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        
        result = response.json()
        print("✅ Class rescheduled successfully!")
        print(f"   • New Assignment ID: {result['new_assignment_id']}")
        print(f"   • Rescheduled Date: {result['rescheduled_date']}")
        
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error rescheduling class: {e}")
        return None

def test_weekend_class_scheduling():
    """Test weekend class scheduling."""
    print("\n🏖️ TESTING WEEKEND CLASS SCHEDULING")
    print("=" * 40)
    
    url = f"{REALLOCATION_URL}/weekend-class"
    
    # Schedule for next Saturday
    next_saturday = datetime.now() + timedelta(days=(5 - datetime.now().weekday()) % 7)
    
    data = {
        "unavailability_id": "test_unavailability_001",
        "weekend_date": next_saturday.isoformat(),
        "student_approval": True
    }
    
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        
        result = response.json()
        print("✅ Weekend class scheduled successfully!")
        print(f"   • Weekend Assignment ID: {result['weekend_assignment_id']}")
        print(f"   • Weekend Date: {result['weekend_date']}")
        
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error scheduling weekend class: {e}")
        return None

def test_reallocation_status():
    """Test getting reallocation status."""
    print("\n📊 TESTING REALLOCATION STATUS")
    print("=" * 35)
    
    url = f"{REALLOCATION_URL}/reallocation-status/test_unavailability_001"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        result = response.json()
        print("✅ Reallocation status retrieved!")
        print(f"   • Status: {result['status']}")
        print(f"   • Current Step: {result['current_step']}")
        print(f"   • Last Updated: {result['last_updated']}")
        
        if result.get('logs'):
            print(f"   • Logs: {len(result['logs'])} entries")
        
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error getting reallocation status: {e}")
        return None

def test_fairness_report():
    """Test getting fairness report."""
    print("\n⚖️ TESTING FAIRNESS REPORT")
    print("=" * 30)
    
    url = f"{REALLOCATION_URL}/fairness-report/{TEST_INSTITUTE_ID}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        result = response.json()
        print("✅ Fairness report retrieved!")
        print(f"   • Institute ID: {result['institute_id']}")
        print(f"   • Fairness Score: {result['fairness_score']}")
        
        if result.get('professor_workloads'):
            print(f"   • Professor Workloads: {len(result['professor_workloads'])} professors")
            for workload in result['professor_workloads']:
                print(f"     - {workload['professor_id']}: {workload['hours']}/{workload['expected']} hours")
        
        if result.get('recommendations'):
            print(f"   • Recommendations: {len(result['recommendations'])} suggestions")
            for i, rec in enumerate(result['recommendations'], 1):
                print(f"     {i}. {rec}")
        
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error getting fairness report: {e}")
        return None

def test_complete_reallocation_flow():
    """Test complete reallocation flow."""
    print("\n🔄 TESTING COMPLETE REALLOCATION FLOW")
    print("=" * 45)
    
    # Step 1: Report unavailability
    step1 = test_professor_unavailability_report()
    
    # Step 2: Try direct substitute
    step2 = test_direct_substitute_assignment()
    
    # Step 3: Student voting
    step3 = test_student_voting()
    
    # Step 4: Rescheduling
    step4 = test_class_rescheduling()
    
    # Step 5: Weekend option
    step5 = test_weekend_class_scheduling()
    
    # Check status
    status = test_reallocation_status()
    
    # Get fairness report
    fairness = test_fairness_report()
    
    # Summary
    print(f"\n📋 COMPLETE FLOW SUMMARY")
    print("=" * 30)
    
    steps = [
        ("Step 1: Unavailability Report", step1),
        ("Step 2: Direct Substitute", step2),
        ("Step 3: Student Voting", step3),
        ("Step 4: Rescheduling", step4),
        ("Step 5: Weekend Class", step5),
        ("Status Check", status),
        ("Fairness Report", fairness)
    ]
    
    for step_name, result in steps:
        status_icon = "✅" if result else "❌"
        print(f"   {status_icon} {step_name}")
    
    return {
        "steps": steps,
        "overall_success": all(result for _, result in steps)
    }

def main():
    """Main test function."""
    print("🚀 DYNAMIC REALLOCATION API TEST")
    print("=" * 40)
    print("Make sure the FastAPI server is running on http://localhost:8000")
    print()
    
    try:
        # Test complete flow
        result = test_complete_reallocation_flow()
        
        if result["overall_success"]:
            print("\n🎉 ALL API TESTS PASSED!")
            print("Dynamic reallocation system is working correctly via API.")
        else:
            print("\n⚠️ Some tests failed - check the output above.")
        
    except Exception as e:
        print(f"❌ Test suite failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
