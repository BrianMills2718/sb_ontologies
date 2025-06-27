# Multi-Agent System Usage Guide

## Overview

The multi-agent system provides a proven methodology for implementing complex development phases with 100/100 quality standards. It uses isolated implementation agents, objective external evaluation, and automatic remediation.

## Quick Start

### 1. Copy the Multi-Agent System

```bash
# Copy the entire multi-agent system to your project
cp -r /home/brian/autocoder3_cc/tools/multi_agent_system /path/to/your/project/
```

### 2. Basic Usage Pattern

```python
from multi_agent_system.auto_phase_manager import AutoPhaseManager
from claude_code import Task

# Initialize the phase manager
manager = AutoPhaseManager()

# Run a single phase
success = manager.auto_run_phase(
    phase_num=1, 
    phase_name="your_implementation_name"
)

if success:
    print("Phase completed with 100/100!")
else:
    print("Phase failed - needs remediation")
```

## Creating New Phases

### Step 1: Create Phase Directory Structure

```bash
mkdir -p your_project/phases/phase{N}_{name}_isolated/
```

### Step 2: Create Implementation Instructions

Create `phases/phase{N}_{name}_isolated/CLAUDE.md`:

```markdown
# Phase {N}: {Your Phase Name}

**Implementation Agent Instructions - Completely Isolated**

You are implementing {description of what to build}.

## 🎯 **GOAL**
{Clear goal statement}

## 📋 **IMPLEMENTATION REQUIREMENTS**

### **1. Create Main Component**
Location: `/path/to/your/component.py`

```python
class YourComponent:
    \"\"\"Your component description\"\"\"
    
    def main_method(self):
        \"\"\"Implementation requirements\"\"\"
        pass
```

## 🧪 **TESTING REQUIREMENTS**
- Test A: {specific test}
- Test B: {specific test}

## 📦 **DELIVERABLES**
Create evidence package at: `/path/to/evidence/phase{N}_{name}/`

### **Required Files**:
**CRITICAL**: You MUST create ALL of these files or evaluation will FAIL

1. **implementation_summary.md** - Technical overview
2. **test_results.txt** - All test outputs
3. **working_implementation.py** - Standalone implementation

## ✅ **SUCCESS CRITERIA (100/100 REQUIRED)**
1. **Functional**: {specific requirement}
2. **Reliable**: {specific requirement}
3. **Performance**: {specific requirement}
```

### Step 3: Create Evaluation Criteria

Create `phases/phase{N}_{name}_isolated/evaluation_criteria.md`:

```markdown
# Evaluation Criteria: {Your Phase Name}

**Success Threshold**: Must achieve exactly 100/100 points to PASS

## 📊 **EVALUATION CRITERIA**

### **1. Functional Correctness (40 points)**
**Test the implementation:**
```bash
cd /path/to/evidence
python working_implementation.py
```

**Scoring**:
- 40 points: Perfect functionality
- 0 points: Any functional failures

### **2. Test Coverage (30 points)**
**Run tests:**
```bash
python -m pytest evidence/ -v
```

**Scoring**:
- 30 points: All tests pass
- 0 points: Any test failures

### **3. Code Quality (20 points)**
- 20 points: Excellent code quality
- 0 points: Poor quality

### **4. Performance (10 points)**
- 10 points: Meets requirements
- 0 points: Doesn't meet requirements

## ✅ **PASS CRITERIA**
**PASS (100 points ONLY)**: Perfect implementation
**FAIL (<100 points)**: Any deficiencies

Write evaluation to: `/path/to/evaluation_clean/phase{N}_evaluation_result.md`
```

## Integration with Your Project

### Method 1: Direct Integration

```python
# your_project/development_workflow.py
import sys
sys.path.append('/path/to/multi_agent_system')

from auto_phase_manager import AutoPhaseManager

class YourProjectManager:
    def __init__(self):
        self.phase_manager = AutoPhaseManager()
        # Customize paths for your project
        self.phase_manager.phases_dir = Path("your_project/phases")
        self.phase_manager.evaluation_dir = Path("your_project/evaluation")
    
    def implement_feature(self, feature_name: str):
        """Implement a feature using multi-agent approach"""
        phase_num = self.get_next_phase_number()
        
        success = self.phase_manager.auto_run_phase(
            phase_num=phase_num,
            phase_name=feature_name
        )
        
        return success
```

### Method 2: Standalone Usage

```python
# your_project/use_multi_agent.py
from claude_code import Task

def run_implementation_phase(instructions_file: str, evidence_dir: str):
    """Run a single implementation phase"""
    
    # Step 1: Implementation
    impl_task = Task(
        description="Implement phase",
        prompt=f"""You are an implementation agent. Read the implementation 
        instructions in {instructions_file} and implement the complete system 
        according to those specifications. Create all required evidence files 
        in {evidence_dir}."""
    )
    
    # Step 2: Evaluation  
    eval_task = Task(
        description="Evaluate implementation", 
        prompt=f"""You are an external evaluator. Read the evaluation criteria 
        and evaluate the evidence in {evidence_dir}. Score must be exactly 
        100/100 to PASS."""
    )
    
    return impl_task, eval_task

# Usage
impl_result, eval_result = run_implementation_phase(
    "phases/phase1_feature_isolated/CLAUDE.md",
    "evidence/phase1_feature/"
)
```

## Configuration for Your Project

### Update Paths

```python
# Customize AutoPhaseManager for your project structure
class CustomPhaseManager(AutoPhaseManager):
    def __init__(self, project_root: str):
        super().__init__()
        self.project_root = Path(project_root)
        self.phases_dir = self.project_root / "development" / "phases"
        self.evaluation_dir = self.project_root / "development" / "evaluation"
        self.evidence_dir = self.project_root / "evidence"
```

### Project Structure

```
your_project/
├── development/
│   ├── phases/
│   │   ├── phase1_feature_isolated/
│   │   │   ├── CLAUDE.md
│   │   │   └── evaluation_criteria.md
│   │   └── phase2_integration_isolated/
│   └── evaluation/
│       └── phase1_evaluation_result.md
├── evidence/
│   ├── phase1_feature/
│   └── phase2_integration/
└── src/
    └── your_code.py
```

## Advanced Usage

### Custom Evaluation Logic

```python
def custom_evaluation_check(phase_num: int, evidence_dir: str) -> bool:
    """Add custom evaluation logic"""
    
    # Run your specific tests
    test_results = run_your_tests(evidence_dir)
    
    # Custom validation
    if not validate_your_requirements(evidence_dir):
        return False
    
    # Standard multi-agent evaluation
    manager = AutoPhaseManager()
    passed, score = manager.check_evaluation_result(phase_num)
    
    return passed and score == 100
```

### Batch Phase Execution

```python
def run_multiple_phases(phase_list: List[Tuple[int, str]]):
    """Run multiple phases in sequence"""
    manager = AutoPhaseManager()
    
    for phase_num, phase_name in phase_list:
        print(f"Starting Phase {phase_num}: {phase_name}")
        
        success = manager.auto_run_phase(phase_num, phase_name)
        
        if not success:
            print(f"Phase {phase_num} failed - stopping")
            return False
    
    return True

# Usage
phases = [
    (1, "data_processor"),
    (2, "api_interface"), 
    (3, "integration_tests")
]

success = run_multiple_phases(phases)
```

## Key Benefits

1. **100/100 Quality Standard**: No partial success allowed
2. **Objective Evaluation**: External agents verify all claims
3. **Automatic Remediation**: Failed phases get automatically fixed
4. **Zero Context Contamination**: Each phase implemented independently
5. **Evidence-Based**: All results verifiable by running actual code

## Best Practices

1. **Clear Instructions**: Make phase instructions completely self-contained
2. **Specific Requirements**: Define exact success criteria upfront
3. **Comprehensive Testing**: Include all necessary test cases
4. **Evidence Structure**: Specify exactly what files must be created
5. **Isolated Design**: Each phase should work independently

## Example Phase Sequence

```python
# Example: Building a web application
WEBAPP_PHASES = [
    (1, "data_models"),      # Database schema and models
    (2, "api_endpoints"),    # REST API implementation  
    (3, "frontend_ui"),      # User interface
    (4, "authentication"),   # User auth system
    (5, "integration"),      # End-to-end integration
    (6, "deployment")        # Production deployment
]

def build_webapp():
    manager = AutoPhaseManager()
    
    for phase_num, phase_name in WEBAPP_PHASES:
        success = manager.auto_run_phase(phase_num, phase_name)
        if not success:
            return False
    
    print("🎉 Complete webapp built with 100/100 quality!")
    return True
```

This multi-agent approach ensures every component is implemented to perfection before moving to the next phase.