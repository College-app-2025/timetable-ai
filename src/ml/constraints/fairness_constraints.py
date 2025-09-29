"""
Fairness constraints for dynamic reallocation
Ensures teaching hours balance across professors
"""

from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import numpy as np
from src.utils.logger_config import get_logger

logger = get_logger("fairness_constraints")

@dataclass
class ProfessorWorkload:
    """Professor workload tracking."""
    professor_id: str
    current_hours: int
    expected_hours: int
    variance: float
    last_updated: datetime

@dataclass
class FairnessMetrics:
    """Fairness metrics for workload balance."""
    gini_coefficient: float
    max_variance: float
    min_variance: float
    average_variance: float
    balance_score: float

class FairnessConstraintManager:
    """Manages fairness constraints for dynamic reallocation."""
    
    def __init__(self):
        self.logger = logger
    
    def calculate_workload_balance(self, professor_workloads: List[ProfessorWorkload]) -> FairnessMetrics:
        """Calculate workload balance metrics."""
        try:
            if not professor_workloads:
                return FairnessMetrics(0.0, 0.0, 0.0, 0.0, 1.0)
            
            # Calculate variances
            variances = [abs(w.variance) for w in professor_workloads]
            
            # Calculate Gini coefficient for workload distribution
            gini_coeff = self._calculate_gini_coefficient([w.current_hours for w in professor_workloads])
            
            # Calculate balance score (0-1, higher is better)
            max_variance = max(variances) if variances else 0.0
            min_variance = min(variances) if variances else 0.0
            avg_variance = np.mean(variances) if variances else 0.0
            
            # Balance score: 1 - (max_variance / expected_hours)
            expected_hours = np.mean([w.expected_hours for w in professor_workloads])
            balance_score = max(0.0, 1.0 - (max_variance / expected_hours)) if expected_hours > 0 else 1.0
            
            return FairnessMetrics(
                gini_coefficient=gini_coeff,
                max_variance=max_variance,
                min_variance=min_variance,
                average_variance=avg_variance,
                balance_score=balance_score
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating workload balance: {str(e)}")
            return FairnessMetrics(0.0, 0.0, 0.0, 0.0, 0.0)
    
    def _calculate_gini_coefficient(self, values: List[float]) -> float:
        """Calculate Gini coefficient for inequality measurement."""
        if not values or len(values) < 2:
            return 0.0
        
        # Sort values
        sorted_values = sorted(values)
        n = len(sorted_values)
        
        # Calculate Gini coefficient
        cumsum = np.cumsum(sorted_values)
        gini = (n + 1 - 2 * np.sum(cumsum) / cumsum[-1]) / n if cumsum[-1] > 0 else 0.0
        
        return gini
    
    def recommend_workload_adjustments(self, 
                                      professor_workloads: List[ProfessorWorkload],
                                      current_assignments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Recommend workload adjustments for fairness."""
        try:
            recommendations = []
            
            # Find professors with high variance
            high_variance_professors = [p for p in professor_workloads if abs(p.variance) > 2.0]
            low_variance_professors = [p for p in professor_workloads if abs(p.variance) < 1.0]
            
            for high_var_prof in high_variance_professors:
                if high_var_prof.variance > 0:  # Overloaded
                    # Find underloaded professors
                    underloaded = [p for p in low_variance_professors if p.variance < 0]
                    
                    if underloaded:
                        # Recommend swapping assignments
                        recommendation = {
                            "type": "swap_assignment",
                            "overloaded_professor": high_var_prof.professor_id,
                            "underloaded_professor": underloaded[0].professor_id,
                            "priority": "high",
                            "reason": f"Balance workload: {high_var_prof.professor_id} has {high_var_prof.variance:.1f} extra hours"
                        }
                        recommendations.append(recommendation)
                
                elif high_var_prof.variance < 0:  # Underloaded
                    # Find overloaded professors
                    overloaded = [p for p in professor_workloads if p.variance > 0]
                    
                    if overloaded:
                        recommendation = {
                            "type": "assign_more_classes",
                            "underloaded_professor": high_var_prof.professor_id,
                            "source_professors": [p.professor_id for p in overloaded],
                            "priority": "medium",
                            "reason": f"Assign more classes to {high_var_prof.professor_id} (currently {high_var_prof.variance:.1f} hours short)"
                        }
                        recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {str(e)}")
            return []
    
    def check_mid_semester_balance(self, 
                                  professor_workloads: List[ProfessorWorkload],
                                  current_date: datetime) -> Dict[str, Any]:
        """Check if mid-semester balance is needed."""
        try:
            # Calculate if we're approaching mid-semester
            semester_start = current_date.replace(month=1, day=1)  # Assuming January start
            mid_semester = semester_start + timedelta(days=60)  # Approximate mid-semester
            
            days_to_mid_semester = (mid_semester - current_date).days
            
            # Check if balance is needed
            metrics = self.calculate_workload_balance(professor_workloads)
            needs_balance = metrics.balance_score < 0.7 or days_to_mid_semester < 30
            
            return {
                "needs_balance": needs_balance,
                "days_to_mid_semester": days_to_mid_semester,
                "current_balance_score": metrics.balance_score,
                "recommendations": self.recommend_workload_adjustments(professor_workloads, [])
            }
            
        except Exception as e:
            self.logger.error(f"Error checking mid-semester balance: {str(e)}")
            return {"needs_balance": False, "error": str(e)}
    
    def optimize_substitute_selection(self, 
                                    available_professors: List[Dict[str, Any]],
                                    target_assignment: Dict[str, Any],
                                    professor_workloads: List[ProfessorWorkload]) -> Dict[str, Any]:
        """Optimize substitute selection based on fairness."""
        try:
            if not available_professors:
                return {"professor_id": None, "reason": "No available professors"}
            
            # Calculate fairness scores for each professor
            fairness_scores = []
            
            for prof in available_professors:
                # Find professor's current workload
                prof_workload = next((w for w in professor_workloads if w.professor_id == prof["id"]), None)
                
                if prof_workload:
                    # Calculate fairness score (higher is better for underloaded professors)
                    fairness_score = -prof_workload.variance  # Negative variance = underloaded = better
                    
                    # Add other factors
                    experience_bonus = 0.1 if prof.get("experience_years", 0) > 5 else 0.0
                    subject_match_bonus = 0.2 if prof.get("subjects", []) and target_assignment.get("course_id") in prof.get("subjects", []) else 0.0
                    
                    total_score = fairness_score + experience_bonus + subject_match_bonus
                    
                    fairness_scores.append({
                        "professor_id": prof["id"],
                        "fairness_score": total_score,
                        "workload_variance": prof_workload.variance,
                        "experience": prof.get("experience_years", 0),
                        "subject_match": subject_match_bonus > 0
                    })
            
            # Sort by fairness score (descending)
            fairness_scores.sort(key=lambda x: x["fairness_score"], reverse=True)
            
            if fairness_scores:
                best_professor = fairness_scores[0]
                return {
                    "professor_id": best_professor["professor_id"],
                    "fairness_score": best_professor["fairness_score"],
                    "reason": f"Best fairness score: {best_professor['fairness_score']:.2f}",
                    "workload_variance": best_professor["workload_variance"]
                }
            else:
                return {"professor_id": None, "reason": "No valid professors found"}
                
        except Exception as e:
            self.logger.error(f"Error optimizing substitute selection: {str(e)}")
            return {"professor_id": None, "reason": f"Error: {str(e)}"}
    
    def calculate_rescheduling_impact(self, 
                                   original_assignment: Dict[str, Any],
                                   new_time_slot: Dict[str, Any],
                                   professor_workloads: List[ProfessorWorkload]) -> Dict[str, Any]:
        """Calculate impact of rescheduling on fairness."""
        try:
            # Find professor's current workload
            prof_workload = next((w for w in professor_workloads if w.professor_id == original_assignment["faculty_id"]), None)
            
            if not prof_workload:
                return {"impact_score": 0.0, "reason": "Professor workload not found"}
            
            # Calculate impact on workload balance
            current_variance = prof_workload.variance
            
            # Simulate new workload after rescheduling
            # This would need actual calculation based on new time slot
            new_variance = current_variance  # Placeholder
            
            impact_score = abs(new_variance) - abs(current_variance)
            
            return {
                "impact_score": impact_score,
                "current_variance": current_variance,
                "new_variance": new_variance,
                "improvement": impact_score < 0,  # Negative impact_score means improvement
                "reason": f"Rescheduling would {'improve' if impact_score < 0 else 'worsen'} workload balance by {abs(impact_score):.1f} hours"
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating rescheduling impact: {str(e)}")
            return {"impact_score": 0.0, "reason": f"Error: {str(e)}"}

# Service instance
fairness_constraint_manager = FairnessConstraintManager()
