"""
Elective Preference Tracking System
Creates tables to track which students got their 1st, 2nd, 3rd, 4th, and 5th choice electives.
"""

import json
import pandas as pd
from typing import Dict, List, Any
from datetime import datetime

class ElectivePreferenceTracker:
    """Tracks student elective preferences and allocations."""
    
    def __init__(self):
        self.preference_tables = {
            "primary_electives": [],      # Students getting 1st choice
            "secondary_electives": [],    # Students getting 2nd choice  
            "tertiary_electives": [],     # Students getting 3rd choice
            "quaternary_electives": [],   # Students getting 4th choice
            "quinary_electives": []       # Students getting 5th choice
        }
        
    def create_preference_tables(self, allocation_results: Dict[str, Any]) -> Dict[str, List[Dict]]:
        """
        Create preference tracking tables based on allocation results.
        
        Args:
            allocation_results: Dictionary with student allocations and preferences
            
        Returns:
            Dictionary with preference tables for each choice level
        """
        
        print("📋 CREATING ELECTIVE PREFERENCE TRACKING TABLES")
        print("=" * 55)
        
        # Process each student's allocation
        for student_data in allocation_results.get("students", []):
            student_id = student_data.get("s_id")
            institute_id = student_data.get("institute_id")
            student_name = student_data.get("name", "Unknown")
            preferences = student_data.get("preferences", [])
            allocated_course = student_data.get("allocated_course")
            
            if not student_id or not allocated_course:
                continue
                
            # Find the preference rank for the allocated course
            preference_rank = None
            for i, pref in enumerate(preferences, 1):
                if pref.get("course_id") == allocated_course:
                    preference_rank = i
                    break
            
            if preference_rank is None:
                continue
                
            # Create student record
            student_record = {
                "s_id": student_id,
                "institute_id": institute_id,
                "student_name": student_name,
                "allocated_course_id": allocated_course,
                "allocated_course_name": self._get_course_name(allocated_course, allocation_results),
                "preference_rank": preference_rank,
                "satisfaction_score": self._calculate_satisfaction_score(preference_rank),
                "allocation_timestamp": datetime.now().isoformat()
            }
            
            # Add to appropriate preference table
            if preference_rank == 1:
                self.preference_tables["primary_electives"].append(student_record)
            elif preference_rank == 2:
                self.preference_tables["secondary_electives"].append(student_record)
            elif preference_rank == 3:
                self.preference_tables["tertiary_electives"].append(student_record)
            elif preference_rank == 4:
                self.preference_tables["quaternary_electives"].append(student_record)
            elif preference_rank == 5:
                self.preference_tables["quinary_electives"].append(student_record)
        
        return self.preference_tables
    
    def _get_course_name(self, course_id: str, allocation_results: Dict) -> str:
        """Get course name from course ID."""
        for course in allocation_results.get("courses", []):
            if course.get("id") == course_id:
                return course.get("name", course_id)
        return course_id
    
    def _calculate_satisfaction_score(self, preference_rank: int) -> float:
        """Calculate satisfaction score based on preference rank."""
        return max(0, (6 - preference_rank) / 5.0)  # 1.0 for 1st choice, 0.2 for 5th choice
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """Generate summary report of preference allocations."""
        
        total_students = sum(len(table) for table in self.preference_tables.values())
        
        summary = {
            "total_students_allocated": total_students,
            "preference_distribution": {
                "primary_electives": len(self.preference_tables["primary_electives"]),
                "secondary_electives": len(self.preference_tables["secondary_electives"]),
                "tertiary_electives": len(self.preference_tables["tertiary_electives"]),
                "quaternary_electives": len(self.preference_tables["quaternary_electives"]),
                "quinary_electives": len(self.preference_tables["quinary_electives"])
            },
            "satisfaction_metrics": self._calculate_satisfaction_metrics(),
            "generated_at": datetime.now().isoformat()
        }
        
        return summary
    
    def _calculate_satisfaction_metrics(self) -> Dict[str, float]:
        """Calculate satisfaction metrics."""
        all_scores = []
        for table in self.preference_tables.values():
            for student in table:
                all_scores.append(student.get("satisfaction_score", 0))
        
        if not all_scores:
            return {"average_satisfaction": 0.0, "high_satisfaction_rate": 0.0}
        
        avg_satisfaction = sum(all_scores) / len(all_scores)
        high_satisfaction_rate = len([s for s in all_scores if s >= 0.8]) / len(all_scores)
        
        return {
            "average_satisfaction": avg_satisfaction,
            "high_satisfaction_rate": high_satisfaction_rate
        }
    
    def export_to_csv(self, output_dir: str = "preference_tables"):
        """Export preference tables to CSV files."""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        for table_name, table_data in self.preference_tables.items():
            if table_data:
                df = pd.DataFrame(table_data)
                csv_path = os.path.join(output_dir, f"{table_name}.csv")
                df.to_csv(csv_path, index=False)
                print(f"📁 Exported {table_name} to {csv_path}")
    
    def save_to_json(self, filename: str = "elective_preference_tables.json"):
        """Save preference tables to JSON file."""
        with open(filename, "w") as f:
            json.dump(self.preference_tables, f, indent=2)
        print(f"📁 Saved preference tables to {filename}")

def create_sample_allocation_data():
    """Create sample allocation data for testing."""
    
    sample_data = {
        "students": [
            {
                "s_id": "stu_001",
                "institute_id": "inst_001",
                "name": "Alice Johnson",
                "preferences": [
                    {"course_id": "CS304", "priority": 1, "course_name": "Machine Learning"},
                    {"course_id": "CS305", "priority": 2, "course_name": "Web Development"},
                    {"course_id": "CS306", "priority": 3, "course_name": "Data Science"},
                    {"course_id": "CS307", "priority": 4, "course_name": "Cybersecurity"},
                    {"course_id": "CS308", "priority": 5, "course_name": "Mobile Development"}
                ],
                "allocated_course": "CS304"  # Alice gets her 1st choice
            },
            {
                "s_id": "stu_002",
                "institute_id": "inst_001", 
                "name": "Bob Smith",
                "preferences": [
                    {"course_id": "CS304", "priority": 1, "course_name": "Machine Learning"},
                    {"course_id": "CS305", "priority": 2, "course_name": "Web Development"},
                    {"course_id": "CS306", "priority": 3, "course_name": "Data Science"},
                    {"course_id": "CS307", "priority": 4, "course_name": "Cybersecurity"},
                    {"course_id": "CS308", "priority": 5, "course_name": "Mobile Development"}
                ],
                "allocated_course": "CS305"  # Bob gets his 2nd choice
            },
            {
                "s_id": "stu_003",
                "institute_id": "inst_001",
                "name": "Charlie Brown", 
                "preferences": [
                    {"course_id": "CS304", "priority": 1, "course_name": "Machine Learning"},
                    {"course_id": "CS305", "priority": 2, "course_name": "Web Development"},
                    {"course_id": "CS306", "priority": 3, "course_name": "Data Science"},
                    {"course_id": "CS307", "priority": 4, "course_name": "Cybersecurity"},
                    {"course_id": "CS308", "priority": 5, "course_name": "Mobile Development"}
                ],
                "allocated_course": "CS306"  # Charlie gets his 3rd choice
            },
            {
                "s_id": "stu_004",
                "institute_id": "inst_001",
                "name": "Diana Prince",
                "preferences": [
                    {"course_id": "CS304", "priority": 1, "course_name": "Machine Learning"},
                    {"course_id": "CS305", "priority": 2, "course_name": "Web Development"},
                    {"course_id": "CS306", "priority": 3, "course_name": "Data Science"},
                    {"course_id": "CS307", "priority": 4, "course_name": "Cybersecurity"},
                    {"course_id": "CS308", "priority": 5, "course_name": "Mobile Development"}
                ],
                "allocated_course": "CS307"  # Diana gets her 4th choice
            },
            {
                "s_id": "stu_005",
                "institute_id": "inst_001",
                "name": "Eve Wilson",
                "preferences": [
                    {"course_id": "CS304", "priority": 1, "course_name": "Machine Learning"},
                    {"course_id": "CS305", "priority": 2, "course_name": "Web Development"},
                    {"course_id": "CS306", "priority": 3, "course_name": "Data Science"},
                    {"course_id": "CS307", "priority": 4, "course_name": "Cybersecurity"},
                    {"course_id": "CS308", "priority": 5, "course_name": "Mobile Development"}
                ],
                "allocated_course": "CS308"  # Eve gets her 5th choice
            }
        ],
        "courses": [
            {"id": "CS304", "name": "Machine Learning"},
            {"id": "CS305", "name": "Web Development"},
            {"id": "CS306", "name": "Data Science"},
            {"id": "CS307", "name": "Cybersecurity"},
            {"id": "CS308", "name": "Mobile Development"}
        ]
    }
    
    return sample_data

def main():
    """Main function to demonstrate the preference tracking system."""
    
    print("🎯 ELECTIVE PREFERENCE TRACKING SYSTEM")
    print("=" * 45)
    
    # Create sample data
    sample_data = create_sample_allocation_data()
    
    # Initialize tracker
    tracker = ElectivePreferenceTracker()
    
    # Create preference tables
    preference_tables = tracker.create_preference_tables(sample_data)
    
    # Generate summary report
    summary = tracker.generate_summary_report()
    
    # Display results
    print("\n📊 PREFERENCE ALLOCATION RESULTS:")
    print("-" * 40)
    
    for table_name, table_data in preference_tables.items():
        choice_level = table_name.replace("_electives", "").title()
        print(f"• {choice_level}: {len(table_data)} students")
        
        for student in table_data:
            print(f"  - {student['student_name']} ({student['s_id']}) → {student['allocated_course_name']} (Score: {student['satisfaction_score']:.2f})")
    
    print(f"\n📈 SATISFACTION METRICS:")
    print(f"• Average Satisfaction: {summary['satisfaction_metrics']['average_satisfaction']:.3f}")
    print(f"• High Satisfaction Rate: {summary['satisfaction_metrics']['high_satisfaction_rate']:.3f}")
    
    # Save results
    tracker.save_to_json()
    tracker.export_to_csv()
    
    # Save summary
    with open("preference_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n✅ PREFERENCE TRACKING COMPLETE!")
    print("📁 Files created:")
    print("   • elective_preference_tables.json - Detailed tables")
    print("   • preference_tables/ - CSV exports")
    print("   • preference_summary.json - Summary report")

if __name__ == "__main__":
    main()
