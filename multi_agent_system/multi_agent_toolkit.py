#!/usr/bin/env python3
"""
Multi-Agent Toolkit - Standalone package for using the multi-agent system
"""
from pathlib import Path
from typing import List, Tuple, Optional
import json
import re

class MultiAgentToolkit:
    """
    Standalone toolkit for using the multi-agent development system
    in any Python project.
    """
    
    def __init__(self, project_root: str):
        """
        Initialize the toolkit for your project
        
        Args:
            project_root: Path to your project root directory
        """
        self.project_root = Path(project_root)
        self.phases_dir = self.project_root / "multi_agent" / "phases"
        self.evaluation_dir = self.project_root / "multi_agent" / "evaluation"
        self.evidence_dir = self.project_root / "evidence"
        
        # Create directories
        self.phases_dir.mkdir(parents=True, exist_ok=True)
        self.evaluation_dir.mkdir(parents=True, exist_ok=True)
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
    
    def create_phase(self, 
                     phase_num: int, 
                     phase_name: str,
                     goal: str,
                     requirements: str,
                     success_criteria: str,
                     evidence_files: List[str]) -> Path:
        """
        Create a new development phase
        
        Args:
            phase_num: Phase number (e.g., 1, 2, 3)
            phase_name: Short name for the phase (e.g., "api_implementation")
            goal: Clear goal statement
            requirements: Implementation requirements
            success_criteria: Success criteria for 100/100 score
            evidence_files: List of required evidence files
            
        Returns:
            Path to created phase directory
        """
        
        phase_dir = self.phases_dir / f"phase{phase_num}_{phase_name}_isolated"
        phase_dir.mkdir(exist_ok=True)
        
        # Create implementation instructions
        instructions = f"""# Phase {phase_num}: {phase_name.replace('_', ' ').title()}

**Implementation Agent Instructions - Completely Isolated**

{goal}

## 🎯 **GOAL**
{goal}

## 📋 **IMPLEMENTATION REQUIREMENTS**

{requirements}

## 🧪 **TESTING REQUIREMENTS**
- Comprehensive test suite required
- All functionality must be tested
- Edge cases must be covered

## 📦 **DELIVERABLES**

Create evidence package at: `{self.evidence_dir}/phase{phase_num}_{phase_name}/`

### **Required Files**:
**CRITICAL**: You MUST create ALL of these files or evaluation will FAIL

{self._format_evidence_files(evidence_files)}

## ✅ **SUCCESS CRITERIA (100/100 REQUIRED)**
{success_criteria}

## 🚫 **CONSTRAINTS**
- NO access to other phase implementations
- Must work standalone
- Complete documentation required
- Production-ready code only

## 🎬 **EVIDENCE REQUIREMENTS**
Your evidence must prove all success criteria through executable code.
"""
        
        with open(phase_dir / "CLAUDE.md", "w") as f:
            f.write(instructions)
        
        # Create evaluation criteria
        criteria = f"""# Evaluation Criteria: {phase_name.replace('_', ' ').title()}

**Success Threshold**: Must achieve exactly 100/100 points to PASS

## 📊 **EVALUATION CRITERIA**

### **1. Functional Correctness (40 points)**
**Test the implementation:**
```bash
cd {self.evidence_dir}/phase{phase_num}_{phase_name}
python working_implementation.py
```

**Scoring**:
- 40 points: Perfect functionality, all requirements met
- 0 points: Any functional failures

### **2. Test Coverage (30 points)**
**Run test suite:**
```bash
python -m pytest {self.evidence_dir}/phase{phase_num}_{phase_name}/ -v
```

**Scoring**:
- 30 points: All tests pass, comprehensive coverage
- 0 points: Any test failures or inadequate coverage

### **3. Code Quality (20 points)**
**Review implementation quality:**
- Clean, readable code
- Proper documentation
- Error handling
- Best practices

**Scoring**:
- 20 points: Excellent code quality
- 0 points: Poor code quality

### **4. Performance & Requirements (10 points)**
**Verify performance and requirements:**
- Meets specified performance requirements
- Handles specified load/constraints
- Resource usage appropriate

**Scoring**:
- 10 points: All requirements met
- 0 points: Requirements not met

## ✅ **PASS CRITERIA**
**PASS (100 points ONLY)**: Perfect implementation meeting all criteria
**FAIL (<100 points)**: Any deficiencies prevent progression

## 📄 **EVALUATION REPORT FORMAT**
Write evaluation to: `{self.evaluation_dir}/phase{phase_num}_evaluation_result.md`

Execute all tests yourself and verify all claims in the evidence.
"""
        
        with open(phase_dir / "evaluation_criteria.md", "w") as f:
            f.write(criteria)
        
        return phase_dir
    
    def run_implementation_phase(self, phase_num: int, phase_name: str):
        """
        Run implementation agent for a phase
        
        Args:
            phase_num: Phase number
            phase_name: Phase name
            
        Returns:
            Task object for the implementation
        """
        from claude_code import Task
        
        phase_dir = self.phases_dir / f"phase{phase_num}_{phase_name}_isolated"
        claude_md = phase_dir / "CLAUDE.md"
        
        if not claude_md.exists():
            raise FileNotFoundError(f"Phase instructions not found: {claude_md}")
        
        prompt = f"""You are an implementation agent for Phase {phase_num}: {phase_name}. Read the implementation instructions in {claude_md} and implement the complete system according to those specifications. You have NO context from previous implementations and should work only from the instructions provided. Create all required evidence files in the specified location."""
        
        return Task(description=f"Implement Phase {phase_num}", prompt=prompt)
    
    def run_evaluation_phase(self, phase_num: int, phase_name: str):
        """
        Run evaluation agent for a phase
        
        Args:
            phase_num: Phase number  
            phase_name: Phase name
            
        Returns:
            Task object for the evaluation
        """
        from claude_code import Task
        
        phase_dir = self.phases_dir / f"phase{phase_num}_{phase_name}_isolated"
        criteria_file = phase_dir / "evaluation_criteria.md"
        
        if not criteria_file.exists():
            raise FileNotFoundError(f"Evaluation criteria not found: {criteria_file}")
        
        prompt = f"""You are an external evaluator for Phase {phase_num}: {phase_name}. You have NO knowledge of the implementation process. Read the evaluation criteria in {criteria_file} and evaluate the evidence accordingly. Execute all provided code, run tests, and verify against criteria. Score must be exactly 100/100 to PASS. Write your evaluation result to {self.evaluation_dir}/phase{phase_num}_evaluation_result.md."""
        
        return Task(description=f"Evaluate Phase {phase_num}", prompt=prompt)
    
    def check_phase_result(self, phase_num: int) -> Tuple[bool, int]:
        """
        Check if phase passed evaluation
        
        Args:
            phase_num: Phase number to check
            
        Returns:
            (passed: bool, score: int)
        """
        result_file = self.evaluation_dir / f"phase{phase_num}_evaluation_result.md"
        
        if not result_file.exists():
            return False, 0
        
        with open(result_file) as f:
            content = f.read()
        
        # Extract score
        score_match = re.search(r'Overall Score:\s*(\d+)/100', content)
        if not score_match:
            return False, 0
        
        score = int(score_match.group(1))
        passed = score == 100
        
        return passed, score
    
    def run_complete_phase(self, 
                          phase_num: int, 
                          phase_name: str, 
                          max_attempts: int = 3) -> bool:
        """
        Run complete phase with automatic remediation
        
        Args:
            phase_num: Phase number
            phase_name: Phase name  
            max_attempts: Maximum remediation attempts
            
        Returns:
            True if phase achieved 100/100, False otherwise
        """
        
        for attempt in range(1, max_attempts + 1):
            print(f"\n🎯 Phase {phase_num}: {phase_name} - Attempt {attempt}")
            
            # Implementation
            impl_task = self.run_implementation_phase(phase_num, phase_name)
            if not impl_task:
                continue
            
            # Evaluation
            eval_task = self.run_evaluation_phase(phase_num, phase_name)
            if not eval_task:
                continue
            
            # Check results
            passed, score = self.check_phase_result(phase_num)
            
            print(f"📊 Score: {score}/100 - {'PASS' if passed else 'FAIL'}")
            
            if passed:
                return True
            
            if attempt < max_attempts:
                print(f"🔧 Launching remediation for attempt {attempt + 1}")
                # Remediation would go here
        
        return False
    
    def _format_evidence_files(self, files: List[str]) -> str:
        """Format evidence files list for instructions"""
        formatted = []
        for i, file in enumerate(files, 1):
            formatted.append(f"{i}. **{file}** - Evidence file {i}")
        return "\n".join(formatted)

# Convenience functions for quick usage
def quick_phase(project_root: str,
                phase_num: int,
                phase_name: str, 
                goal: str,
                requirements: str) -> bool:
    """
    Quick helper to create and run a simple phase
    
    Args:
        project_root: Your project directory
        phase_num: Phase number
        phase_name: Phase name  
        goal: What to build
        requirements: Implementation requirements
        
    Returns:
        True if phase achieved 100/100
    """
    
    toolkit = MultiAgentToolkit(project_root)
    
    # Create phase with standard files
    evidence_files = [
        "implementation_summary.md",
        "test_results.txt", 
        "working_implementation.py"
    ]
    
    success_criteria = """
1. **Functional**: Implementation works perfectly
2. **Tested**: All tests pass
3. **Quality**: Clean, documented code
4. **Complete**: All requirements met
"""
    
    toolkit.create_phase(
        phase_num=phase_num,
        phase_name=phase_name,
        goal=goal,
        requirements=requirements,
        success_criteria=success_criteria,
        evidence_files=evidence_files
    )
    
    return toolkit.run_complete_phase(phase_num, phase_name)

if __name__ == "__main__":
    # Example usage
    success = quick_phase(
        project_root="/tmp/test_project",
        phase_num=1,
        phase_name="hello_world",
        goal="Create a simple hello world program",
        requirements="Create a function that prints 'Hello, World!' and returns the string"
    )
    
    print(f"Phase result: {'SUCCESS' if success else 'FAILED'}")