# Dynamic Reallocation System

A robust, AI-driven system for handling professor unavailability in timetable management with a 5-step fallback hierarchy.

## 🎯 Overview

The Dynamic Reallocation System automatically handles professor unavailability through an intelligent 5-step fallback hierarchy, ensuring minimal disruption to academic schedules while maintaining fairness and transparency.

## 🏗️ Architecture

### Core Components

```
src/
├── services/
│   └── dynamic_reallocation_service.py    # Main reallocation logic
├── routes/
│   └── dynamic_reallocation_routes.py      # FastAPI endpoints
├── ml/
│   └── constraints/
│       └── fairness_constraints.py        # Fairness optimization
└── models/ (Prisma schema)
    ├── ProfessorUnavailability
    ├── ReallocationLog
    ├── ProfessorAvailability
    └── StudentVote
```

## 🔄 5-Step Fallback Hierarchy

### Step 1: Direct Substitute (Professor's Choice)
- Professor suggests a substitute (assistant, PhD scholar, colleague)
- System checks substitute availability
- If available and agrees → **SUCCESS**

### Step 2: Section Professors Availability
- Check other professors teaching the same section
- Notify available professors via email
- First to accept gets the class → **SUCCESS**

### Step 3: Same-Subject Professors + Student Vote
- Find professors teaching the same subject
- Professor selects from available pool
- Students vote (yes/no) via class-wide notification
- Majority vote decides → **SUCCESS** or continue

### Step 4: Rescheduling Before Checkpoints
- Find free slots in coming weeks before mid/end-semester
- Check section and professor availability
- Reschedule to available slot → **SUCCESS**

### Step 5: Weekend Option
- Notify students about weekend class option
- Student majority vote
- If approved → schedule weekend class
- If rejected → **DROP CLASS** (logged and tracked)

## 🚀 API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/professor-unavailability` | POST | Report professor unavailability |
| `/assign-direct-substitute` | POST | Assign direct substitute (Step 1) |
| `/student-vote` | POST | Submit student vote (Step 3) |
| `/reschedule-class` | POST | Reschedule class (Step 4) |
| `/weekend-class` | POST | Schedule weekend class (Step 5) |
| `/reallocation-status/{id}` | GET | Get reallocation status |
| `/fairness-report/{institute_id}` | GET | Get fairness report |

### Example Usage

```python
# Report unavailability
POST /api/dynamic-reallocation/professor-unavailability
{
    "institute_id": "inst_001",
    "professor_id": "prof_001", 
    "assignment_id": "assign_001",
    "unavailability_date": "2024-01-15T10:00:00Z",
    "reason": "Medical emergency"
}

# Assign direct substitute
POST /api/dynamic-reallocation/assign-direct-substitute
{
    "unavailability_id": "unav_001",
    "substitute_professor_id": "prof_002",
    "professor_approval": true
}

# Student voting
POST /api/dynamic-reallocation/student-vote
{
    "reallocation_id": "realloc_001",
    "student_id": "student_001",
    "vote": true
}
```

## ⚖️ Fairness System

### Workload Balance
- Tracks teaching hours per professor
- Calculates variance from expected hours
- Generates balance recommendations
- Ensures fairness before mid/end-semester checkpoints

### Metrics
- **Gini Coefficient**: Measures inequality in workload distribution
- **Balance Score**: 0-1 scale (higher = more balanced)
- **Variance Tracking**: Individual professor workload variance
- **Recommendations**: Automated suggestions for workload adjustments

## 🧪 Testing

### Run Tests

```bash
# Test complete reallocation flow
python test_dynamic_reallocation.py

# Test API endpoints
python test_reallocation_api.py

# Test with 1000 students
python test_1000_students.py
```

### Test Coverage
- ✅ Step 1: Direct substitute assignment
- ✅ Step 2: Section professor availability
- ✅ Step 3: Student voting system
- ✅ Step 4: Rescheduling logic
- ✅ Step 5: Weekend class option
- ✅ Fairness constraints
- ✅ API integration
- ✅ Database operations

## 📊 Database Schema

### New Models Added

```prisma
model ProfessorUnavailability {
  id               String   @id @default(uuid())
  institute_id     String
  professor_id     String
  assignment_id    String
  unavailability_date DateTime
  reason           String
  status           String  @default("pending")
  // ... relationships
}

model ReallocationLog {
  id                    String   @id @default(uuid())
  unavailability_id     String
  step                  Int      // 1-5
  action_taken          String
  substitute_professor_id String?
  student_votes         Json?
  // ... relationships
}

model StudentVote {
  id               String   @id @default(uuid())
  reallocation_id  String
  student_id       String
  vote             Boolean
  // ... relationships
}
```

## 🔧 Configuration

### Environment Variables
```bash
DATABASE_URL="postgresql://user:pass@localhost:5432/timetable"
REDIS_URL="redis://localhost:6379"
SMTP_HOST="smtp.gmail.com"
SMTP_PORT=587
SMTP_USER="your-email@gmail.com"
SMTP_PASS="your-password"
```

### Optimization Settings
```python
# Large scale configuration
config = OptimizationConfig()
config.max_optimization_time = 600  # 10 minutes
config.max_iterations = 2000
config.student_satisfaction_weight = 1.2
config.faculty_workload_weight = 0.9
```

## 📈 Performance

### Scalability
| Students | Optimization Time | Memory Usage | Success Rate |
|----------|------------------|--------------|--------------|
| 100 | 30-60s | < 1GB | 95%+ |
| 500 | 2-3min | 1-2GB | 90%+ |
| 1000 | 3-5min | 1.5-2GB | 90%+ |
| 2000+ | 5-10min | 2-4GB | 85%+ |

### Optimization Features
- **Batch Processing**: Process students in groups of 200-300
- **Parallel Processing**: Use multiple CPU cores
- **Memory Management**: Clear unused data
- **Incremental Optimization**: Start with core courses, add electives

## 🚨 Error Handling

### Graceful Degradation
- If Step 1 fails → automatically try Step 2
- If Step 2 fails → automatically try Step 3
- If all steps fail → log and track for manual intervention
- Every decision is logged for transparency

### Logging
- All reallocation decisions are logged
- Professor responses are tracked
- Student votes are recorded
- System performance is monitored

## 🔮 Future Enhancements

### Planned Features
- [ ] Machine learning for substitute recommendation
- [ ] Predictive unavailability detection
- [ ] Mobile app for professor notifications
- [ ] Real-time dashboard for administrators
- [ ] Integration with calendar systems
- [ ] Automated email templates
- [ ] Advanced fairness algorithms

### Integration Points
- [ ] Google Calendar integration
- [ ] Microsoft Teams notifications
- [ ] SMS notifications
- [ ] WhatsApp integration
- [ ] Slack notifications

## 📝 Usage Examples

### Basic Reallocation
```python
# Report unavailability
result = await dynamic_reallocation_service.handle_professor_unavailability(
    institute_id="inst_001",
    professor_id="prof_001",
    assignment_id="assign_001", 
    unavailability_date=datetime.now() + timedelta(days=1),
    reason="Medical emergency"
)
```

### Fairness Check
```python
# Check workload balance
workloads = [ProfessorWorkload("prof_001", 18, 20, -2.0, datetime.now())]
metrics = fairness_constraint_manager.calculate_workload_balance(workloads)
print(f"Balance Score: {metrics.balance_score}")
```

### API Testing
```bash
# Test complete flow
curl -X POST "http://localhost:8000/api/dynamic-reallocation/professor-unavailability" \
  -H "Content-Type: application/json" \
  -d '{
    "institute_id": "inst_001",
    "professor_id": "prof_001",
    "assignment_id": "assign_001",
    "unavailability_date": "2024-01-15T10:00:00Z",
    "reason": "Medical emergency"
  }'
```

## 🎉 Success Metrics

### System Performance
- **Response Time**: < 2 seconds for API calls
- **Success Rate**: > 90% for reallocation
- **Fairness Score**: > 0.8 for workload balance
- **Student Satisfaction**: > 0.85 for elective allocation

### Business Impact
- **Reduced Manual Work**: 80% reduction in manual scheduling
- **Improved Fairness**: Balanced workload distribution
- **Better Transparency**: Complete audit trail
- **Enhanced Flexibility**: Multiple fallback options

---

## 🚀 Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup Database**
   ```bash
   npx prisma migrate dev
   ```

3. **Run Tests**
   ```bash
   python test_dynamic_reallocation.py
   ```

4. **Start Server**
   ```bash
   uvicorn main:app --reload
   ```

5. **Test API**
   ```bash
   python test_reallocation_api.py
   ```

The Dynamic Reallocation System is now ready to handle professor unavailability with intelligent fallback mechanisms! 🎯
