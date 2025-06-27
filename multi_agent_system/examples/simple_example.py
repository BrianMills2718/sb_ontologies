#!/usr/bin/env python3
"""
Simple example of using the multi-agent system in another project
"""
import sys
from pathlib import Path

# Add multi-agent system to path
sys.path.append(str(Path(__file__).parent.parent))

from auto_phase_manager import AutoPhaseManager

def create_example_phase():
    """Create a simple example phase for demonstration"""
    
    # Create phase directory
    phases_dir = Path("example_phases")
    phase_dir = phases_dir / "phase1_calculator_isolated"
    phase_dir.mkdir(parents=True, exist_ok=True)
    
    # Create implementation instructions
    instructions = """# Phase 1: Calculator Implementation

**Implementation Agent Instructions - Completely Isolated**

You are implementing a simple calculator with basic math operations.

## 🎯 **GOAL**
Create a calculator that can perform addition, subtraction, multiplication, and division.

## 📋 **IMPLEMENTATION REQUIREMENTS**

### **1. Create Calculator Component**
Location: `calculator.py`

```python
class Calculator:
    \"\"\"Simple calculator with basic operations\"\"\"
    
    def add(self, a: float, b: float) -> float:
        \"\"\"Add two numbers\"\"\"
        pass
    
    def subtract(self, a: float, b: float) -> float:
        \"\"\"Subtract b from a\"\"\"
        pass
    
    def multiply(self, a: float, b: float) -> float:
        \"\"\"Multiply two numbers\"\"\"
        pass
    
    def divide(self, a: float, b: float) -> float:
        \"\"\"Divide a by b\"\"\"
        pass
```

## 🧪 **TESTING REQUIREMENTS**
- Test addition: 2 + 3 = 5
- Test subtraction: 5 - 3 = 2  
- Test multiplication: 4 * 3 = 12
- Test division: 10 / 2 = 5
- Test division by zero handling

## 📦 **DELIVERABLES**
Create evidence package at: `evidence/phase1_calculator/`

### **Required Files**:
**CRITICAL**: You MUST create ALL of these files or evaluation will FAIL

1. **implementation_summary.md** - Technical overview
2. **test_results.txt** - All test outputs
3. **working_implementation.py** - Standalone implementation
4. **calculator.py** - Main calculator class

## ✅ **SUCCESS CRITERIA (100/100 REQUIRED)**
1. **Functional**: All operations work correctly
2. **Reliable**: Handles edge cases (division by zero)
3. **Performance**: Operations complete instantly
4. **Testable**: Complete test suite passes
"""
    
    with open(phase_dir / "CLAUDE.md", "w") as f:
        f.write(instructions)
    
    # Create evaluation criteria
    criteria = """# Evaluation Criteria: Calculator Implementation

**Success Threshold**: Must achieve exactly 100/100 points to PASS

## 📊 **EVALUATION CRITERIA**

### **1. Functional Correctness (40 points)**
**Test the calculator:**
```bash
cd evidence/phase1_calculator
python working_implementation.py
```

**Scoring**:
- 40 points: All operations work correctly
- 0 points: Any operation failures

### **2. Test Coverage (30 points)**
**Run tests:**
```bash
python -m pytest evidence/phase1_calculator/ -v
```

**Scoring**:
- 30 points: All tests pass
- 0 points: Any test failures

### **3. Error Handling (20 points)**
**Test edge cases:**
- Division by zero
- Invalid inputs

**Scoring**:
- 20 points: Graceful error handling
- 0 points: Crashes or poor handling

### **4. Code Quality (10 points)**
**Review implementation:**
- Clear documentation
- Proper error messages
- Clean code structure

**Scoring**:
- 10 points: Excellent quality
- 0 points: Poor quality

## ✅ **PASS CRITERIA**
**PASS (100 points ONLY)**: Perfect calculator implementation
**FAIL (<100 points)**: Any deficiencies

Write evaluation to: `evaluation_clean/phase1_evaluation_result.md`
"""
    
    with open(phase_dir / "evaluation_criteria.md", "w") as f:
        f.write(criteria)
    
    print(f"✅ Example phase created at: {phase_dir}")
    return phase_dir

def run_example():
    """Run the simple calculator example"""
    
    print("🚀 Multi-Agent System Example")
    print("="*50)
    
    # Step 1: Create example phase
    phase_dir = create_example_phase()
    
    # Step 2: Set up phase manager
    manager = AutoPhaseManager()
    manager.phases_dir = Path("example_phases")
    manager.evaluation_dir = Path("example_evaluation")
    manager.evaluation_dir.mkdir(exist_ok=True)
    
    # Step 3: Run the phase
    print("\n🎯 Running Phase 1: Calculator Implementation")
    success = manager.auto_run_phase(1, "calculator")
    
    if success:
        print("\n✅ SUCCESS! Calculator implemented with 100/100 quality")
        print("📁 Evidence available at: evidence/phase1_calculator/")
    else:
        print("\n❌ FAILED! Calculator implementation needs work")
    
    return success

if __name__ == "__main__":
    run_example()