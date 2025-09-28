# 🧠 ML System Structure Documentation

## 📁 **Final Clean Structure**

```
src/ml/
├── __init__.py                 # Main ML module entry point
├── api/                        # FastAPI endpoints and schemas
│   ├── __init__.py
│   ├── routes.py              # Main timetable API routes
│   ├── multi_schedule_routes.py # Multiple schedule generation routes
│   └── schemas.py             # Pydantic models for API requests/responses
├── config/                     # Configuration and settings
│   ├── __init__.py
│   ├── settings.py            # ML system configuration
│   └── validators.py          # Configuration validation
├── constraints/                # Constraint definitions
│   ├── __init__.py
│   ├── hard_constraints.py    # Hard constraints (must satisfy)
│   ├── soft_constraints.py    # Soft constraints (optimization)
│   └── nep2020_constraints.py # NEP 2020 specific constraints
├── core/                       # Core optimization logic
│   ├── __init__.py
│   ├── optimizer.py           # Main optimization orchestrator
│   ├── constraint_solver.py   # Google OR-Tools CP-SAT solver
│   ├── elective_allocator.py  # Elective course allocation
│   ├── timetable_builder.py   # Schedule construction
│   ├── multi_schedule_optimizer.py # Multiple schedule generation
│   └── pareto_optimizer.py    # Multi-objective optimization
├── data/                       # Data handling and models
│   ├── __init__.py
│   ├── models.py              # ML domain models (dataclasses)
│   ├── loaders.py             # Database data loaders
│   ├── converters.py          # Data format converters
│   ├── validators.py          # Data validation
│   └── transformers.py        # Data preprocessing
├── evaluation/                 # Metrics and evaluation
│   ├── __init__.py
│   ├── metrics.py             # Performance metrics calculation
│   ├── fairness.py            # Fairness evaluation
│   └── reporters.py           # Report generation
└── utils/                      # Utility functions
    ├── __init__.py
    ├── logging.py             # ML-specific logging
    ├── caching.py             # Caching utilities
    └── helpers.py             # Helper functions
```

## 📋 **File Purposes and Responsibilities**

### **Core Module (`src/ml/core/`)**

#### `optimizer.py` - Main Optimization Orchestrator
- **Purpose**: Coordinates the entire optimization workflow
- **Key Functions**:
  - `optimize_timetable()` - Main optimization entry point
  - `optimize_timetable_with_data()` - Test optimization with provided data
  - `_run_optimization_with_data()` - Internal optimization execution
  - `_validate_data()` - Input data validation
- **Dependencies**: All other core modules, data models, evaluation modules

#### `constraint_solver.py` - Google OR-Tools CP-SAT Solver
- **Purpose**: Handles constraint satisfaction and optimization
- **Key Functions**:
  - `add_all_constraints()` - Adds hard and soft constraints to model
  - `solve()` - Executes the CP-SAT solver
  - `validate_solution()` - Validates solution for constraint violations
- **Dependencies**: OR-Tools, constraint modules

#### `elective_allocator.py` - Elective Course Allocation
- **Purpose**: Handles priority-based elective course allocation
- **Key Functions**:
  - `allocate_electives()` - Allocates elective courses to students
  - `compute_student_priorities()` - Calculates student priority scores
- **Dependencies**: Data models, metrics

#### `timetable_builder.py` - Schedule Construction
- **Purpose**: Builds final timetable from optimization results
- **Key Functions**:
  - `build_schedule()` - Constructs final schedule object
  - `_create_assignments()` - Creates assignment objects
- **Dependencies**: Data models

#### `multi_schedule_optimizer.py` - Multiple Schedule Generation
- **Purpose**: Generates multiple schedule options with different strategies
- **Key Functions**:
  - `generate_multiple_schedules()` - Creates multiple schedule options
  - `_create_optimization_strategies()` - Defines different optimization strategies
- **Dependencies**: Main optimizer, evaluation modules

#### `pareto_optimizer.py` - Multi-Objective Optimization
- **Purpose**: True multi-objective optimization using Pareto frontier
- **Key Functions**:
  - `optimize_pareto()` - Finds Pareto-optimal solutions
  - `_calculate_pareto_frontier()` - Calculates Pareto frontier
- **Dependencies**: Main optimizer, evaluation modules

### **Data Module (`src/ml/data/`)**

#### `models.py` - ML Domain Models
- **Purpose**: Defines clean dataclasses for ML operations
- **Key Classes**:
  - `Student`, `Course`, `Faculty`, `Room`, `TimeSlot` - Core entities
  - `Assignment`, `Schedule` - Optimization results
  - `OptimizationConfig` - Configuration parameters
  - `OptimizationMetrics` - Performance metrics
- **Dependencies**: None (pure data structures)

#### `loaders.py` - Database Data Loaders
- **Purpose**: Loads data from PostgreSQL database via Prisma
- **Key Functions**:
  - `load_students_from_db()`, `load_courses_from_db()`, etc.
  - `load_institute_data()` - Loads all data for an institute
- **Dependencies**: Prisma client, data models

#### `converters.py` - Data Format Converters
- **Purpose**: Converts between different data formats
- **Key Functions**:
  - `convert_data_to_ml_models()` - Converts dict to ML models
  - `convert_ml_models_to_dict()` - Converts ML models to dict
- **Dependencies**: Data models

#### `validators.py` - Data Validation
- **Purpose**: Validates data integrity and constraints
- **Key Functions**:
  - `validate_student_data()`, `validate_course_data()`, etc.
- **Dependencies**: Data models

#### `transformers.py` - Data Preprocessing
- **Purpose**: Preprocesses and normalizes data
- **Key Functions**:
  - `normalize_data()`, `preprocess_preferences()`, etc.
- **Dependencies**: Data models

### **Constraints Module (`src/ml/constraints/`)**

#### `hard_constraints.py` - Hard Constraints
- **Purpose**: Defines constraints that MUST be satisfied
- **Key Constraints**:
  - Faculty no-conflict (one class at a time)
  - Room no-conflict (one class at a time)
  - Student no-conflict (one class at a time)
  - Capacity constraints (room capacity ≥ class size)
  - Teacher-subject allocation (qualified teachers only)
- **Dependencies**: OR-Tools, data models

#### `soft_constraints.py` - Soft Constraints
- **Purpose**: Defines optimization preferences (penalized if violated)
- **Key Constraints**:
  - Faculty workload balance
  - Student satisfaction (preferences, timing)
  - Room utilization optimization
  - NEP 2020 compliance
- **Dependencies**: OR-Tools, data models, config

#### `nep2020_constraints.py` - NEP 2020 Specific Constraints
- **Purpose**: Implements NEP 2020 specific requirements
- **Key Constraints**:
  - Multidisciplinary subject scheduling
  - Elective course flexibility
  - Skill development course scheduling
- **Dependencies**: Soft constraints, data models

### **Evaluation Module (`src/ml/evaluation/`)**

#### `metrics.py` - Performance Metrics
- **Purpose**: Calculates optimization performance metrics
- **Key Functions**:
  - `calculate_metrics()` - Calculates all metrics
  - `student_satisfaction_score()` - Student satisfaction
  - `faculty_workload_balance()` - Faculty workload balance
  - `room_utilization_score()` - Room utilization
- **Dependencies**: Data models

#### `fairness.py` - Fairness Evaluation
- **Purpose**: Evaluates fairness across different groups
- **Key Functions**:
  - `calculate_fairness_metrics()` - Fairness across departments
  - `gender_equity_score()` - Gender equity in scheduling
- **Dependencies**: Data models, metrics

#### `reporters.py` - Report Generation
- **Purpose**: Generates optimization reports
- **Key Functions**:
  - `generate_optimization_report()` - Detailed optimization report
  - `generate_summary_report()` - Executive summary
- **Dependencies**: Metrics, data models

### **API Module (`src/ml/api/`)**

#### `routes.py` - Main API Routes
- **Purpose**: FastAPI endpoints for timetable operations
- **Key Endpoints**:
  - `POST /generate` - Generate single schedule
  - `GET /status` - System status
- **Dependencies**: Core optimizer, schemas

#### `multi_schedule_routes.py` - Multiple Schedule Routes
- **Purpose**: FastAPI endpoints for multiple schedule generation
- **Key Endpoints**:
  - `POST /generate-multiple` - Generate multiple schedules
  - `POST /select-schedule` - Select and save schedule
- **Dependencies**: Multi-schedule optimizer, schemas

#### `schemas.py` - API Schemas
- **Purpose**: Pydantic models for API requests/responses
- **Key Models**:
  - `TimetableRequest`, `TimetableResponse`
  - `MultiScheduleRequest`, `MultiScheduleResponse`
  - `ScheduleSelectionRequest`
- **Dependencies**: Data models

### **Config Module (`src/ml/config/`)**

#### `settings.py` - Configuration Settings
- **Purpose**: ML system configuration
- **Key Settings**:
  - Optimization parameters
  - Constraint weights
  - Time limits
- **Dependencies**: None

#### `validators.py` - Configuration Validation
- **Purpose**: Validates configuration parameters
- **Key Functions**:
  - `validate_config()` - Validates configuration
- **Dependencies**: Settings

### **Utils Module (`src/ml/utils/`)**

#### `logging.py` - ML Logging
- **Purpose**: ML-specific logging configuration
- **Key Functions**:
  - `setup_ml_logging()` - Sets up ML logging
- **Dependencies**: Logger config

#### `caching.py` - Caching Utilities
- **Purpose**: Caching for optimization results
- **Key Functions**:
  - `cache_optimization_result()` - Caches results
  - `get_cached_result()` - Retrieves cached results
- **Dependencies**: Redis (optional)

#### `helpers.py` - Helper Functions
- **Purpose**: Common utility functions
- **Key Functions**:
  - `format_time_slot()`, `calculate_duration()`, etc.
- **Dependencies**: Data models

## 🔄 **Data Flow**

1. **Input**: Raw data (dict) from API or database
2. **Conversion**: `converters.py` converts to ML models
3. **Validation**: `validators.py` validates data integrity
4. **Preprocessing**: `transformers.py` preprocesses data
5. **Optimization**: `optimizer.py` coordinates optimization
6. **Constraint Solving**: `constraint_solver.py` solves constraints
7. **Schedule Building**: `timetable_builder.py` builds final schedule
8. **Evaluation**: `metrics.py` calculates performance metrics
9. **Output**: Formatted results for API response

## 🎯 **Key Benefits of This Structure**

1. **Modularity**: Each module has a single responsibility
2. **Clean Separation**: Data, logic, and API are separated
3. **Testability**: Each module can be tested independently
4. **Maintainability**: Easy to modify and extend
5. **Reusability**: Components can be reused across different contexts
6. **Scalability**: Easy to add new features and constraints

## 🚀 **Usage Examples**

### **Single Schedule Generation**
```python
from src.ml.core.optimizer import TimetableOptimizer
from src.ml.data.models import OptimizationConfig

optimizer = TimetableOptimizer()
result = await optimizer.optimize_timetable_with_data(
    institute_id="inst_001",
    semester=1,
    config=OptimizationConfig(),
    data=your_data
)
```

### **Multiple Schedule Generation**
```python
from src.ml.core.multi_schedule_optimizer import MultiScheduleOptimizer

multi_optimizer = MultiScheduleOptimizer()
result = await multi_optimizer.generate_multiple_schedules(
    institute_id="inst_001",
    semester=1,
    data=your_data,
    num_options=3
)
```

### **API Usage**
```bash
# Generate single schedule
POST /api/timetable/generate
{
    "institute_id": "inst_001",
    "semester": 1,
    "students": [...],
    "courses": [...],
    "faculty": [...],
    "rooms": [...],
    "time_slots": [...]
}

# Generate multiple schedules
POST /api/timetable/generate-multiple
{
    "institute_id": "inst_001",
    "semester": 1,
    "students": [...],
    "courses": [...],
    "faculty": [...],
    "rooms": [...],
    "time_slots": [...],
    "num_options": 3
}
```

## 📊 **External Files (Outside src/ml/)**

### **`test_ml_clean.py`** - Clean Test Script
- **Purpose**: Demonstrates proper usage of the ML system
- **Key Functions**:
  - `test_ml_system()` - Tests optimization with sample data
  - `show_api_usage()` - Shows API usage examples
- **Dependencies**: ML modules

### **`sample_data_example.py`** - Sample Data Example
- **Purpose**: Shows how to format data for the ML system
- **Key Functions**:
  - `create_sample_data()` - Creates properly formatted sample data
  - `test_api_endpoints()` - Tests API endpoints
- **Dependencies**: ML modules, FastAPI

### **`complete_usage_example.py`** - Complete Usage Example
- **Purpose**: Comprehensive example of all ML system features
- **Key Functions**:
  - `test_single_schedule()` - Tests single schedule generation
  - `test_multiple_schedules()` - Tests multiple schedule generation
  - `test_api_integration()` - Tests API integration
- **Dependencies**: ML modules, FastAPI

This structure provides a clean, modular, and maintainable ML system that can be easily extended and tested! 🎉

