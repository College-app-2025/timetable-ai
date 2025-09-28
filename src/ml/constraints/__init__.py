"""
Constraint definitions for the SIH Timetable Optimization System.
Implements hard constraints (must satisfy) and soft constraints (optimization preferences).
"""

from .hard_constraints import (
    HardConstraintManager,
    NoConflictConstraint,
    CapacityConstraint,
    FacultyAvailabilityConstraint,
    RoomAvailabilityConstraint,
    PrerequisiteConstraint
)

from .soft_constraints import (
    SoftConstraintManager,
    StudentSatisfactionConstraint,
    FacultyWorkloadBalanceConstraint,
    RoomUtilizationConstraint,
    ElectivePreferenceConstraint,
    NEP2020ComplianceConstraint
)

from .nep2020_constraints import (
    NEP2020ConstraintManager,
    MultidisciplinaryConstraint,
    FlexibilityConstraint,
    SkillDevelopmentConstraint
)

__all__ = [
    # Hard Constraints
    'HardConstraintManager', 'NoConflictConstraint', 'CapacityConstraint',
    'FacultyAvailabilityConstraint', 'RoomAvailabilityConstraint', 'PrerequisiteConstraint',
    
    # Soft Constraints
    'SoftConstraintManager', 'StudentSatisfactionConstraint', 'FacultyWorkloadBalanceConstraint',
    'RoomUtilizationConstraint', 'ElectivePreferenceConstraint', 'NEP2020ComplianceConstraint',
    
    # NEP 2020 Constraints
    'NEP2020ConstraintManager', 'MultidisciplinaryConstraint', 'FlexibilityConstraint',
    'SkillDevelopmentConstraint'
]

