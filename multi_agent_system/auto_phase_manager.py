#!/usr/bin/env python3
"""
Auto Phase Manager - Manages automatic progression through phases
Requires 100/100 score to pass, auto-launches next phase
"""
import json
import time
from pathlib import Path

class AutoPhaseManager:
    """Manages automatic phase progression with 100/100 requirement"""
    
    def __init__(self):
        self.phases_dir = Path("/home/brian/autocoder3_cc/tools/multi_agent_system/multi_agent_system/phases")
        self.evaluation_dir = self.phases_dir / "evaluation_clean"
        
    def launch_implementation_agent(self, phase_num: int, phase_name: str):
        """Launch implementation agent for specified phase"""
        from claude_code import Task
        
        phase_dir = f"phase{phase_num}_{phase_name}_isolated"
        claude_md = self.phases_dir / phase_dir / "CLAUDE.md"
        
        if not claude_md.exists():
            raise FileNotFoundError(f"Phase {phase_num} instructions not found: {claude_md}")
            
        prompt = f"""You are an implementation agent for Phase {phase_num}: {phase_name}. Read the implementation instructions in {claude_md} and implement the complete system according to those specifications. You have NO context from previous implementations and should work only from the instructions provided. Create all required evidence files in the specified location."""
        
        print(f"🚀 Launching Phase {phase_num} Implementation Agent...")
        return Task(description=f"Implement Phase {phase_num}", prompt=prompt)
        
    def launch_evaluation_agent(self, phase_num: int, phase_name: str):
        """Launch evaluation agent for specified phase"""
        from claude_code import Task
        
        phase_dir = f"phase{phase_num}_{phase_name}_isolated"
        criteria_file = self.phases_dir / phase_dir / "evaluation_criteria.md"
        
        if not criteria_file.exists():
            raise FileNotFoundError(f"Evaluation criteria not found: {criteria_file}")
            
        prompt = f"""You are an external evaluator for Phase {phase_num}: {phase_name}. You have NO knowledge of the implementation process. Read the evaluation criteria in {criteria_file} and evaluate the evidence accordingly. Execute all provided code, run tests, and verify against criteria. Score must be exactly 100/100 to PASS. Write your evaluation result to {self.evaluation_dir}/phase{phase_num}_evaluation_result.md."""
        
        print(f"🔍 Launching Phase {phase_num} Evaluation Agent...")
        return Task(description=f"Evaluate Phase {phase_num}", prompt=prompt)
        
    def check_evaluation_result(self, phase_num: int) -> tuple[bool, int]:
        """Check if phase passed (100/100) and return score"""
        result_file = self.evaluation_dir / f"phase{phase_num}_evaluation_result.md"
        
        if not result_file.exists():
            return False, 0
            
        with open(result_file) as f:
            content = f.read()
            
        # Extract score from evaluation result
        import re
        score_match = re.search(r'Overall Score:\s*(\d+)/100', content)
        if not score_match:
            return False, 0
            
        score = int(score_match.group(1))
        passed = score == 100
        
        return passed, score
        
    def launch_remediation_agent(self, phase_num: int, phase_name: str, issues: str):
        """Launch remediation agent to fix issues"""
        from claude_code import Task
        
        prompt = f"""You are a remediation agent for Phase {phase_num}: {phase_name}. The external evaluation found specific failures that prevented a 100/100 score.

CRITICAL ISSUES TO FIX:
{issues}

Fix these specific issues in the evidence located at the appropriate phase directory. Address ALL failed criteria and re-test until 100/100 score is achieved. You must achieve PERFECT functionality - no partial success allowed."""

        print(f"🔧 Launching Phase {phase_num} Remediation Agent...")
        return Task(description=f"Remediate Phase {phase_num}", prompt=prompt)
        
    def auto_run_phase(self, phase_num: int, phase_name: str, max_attempts: int = 3):
        """Automatically run a phase until 100/100 or max attempts"""
        
        for attempt in range(1, max_attempts + 1):
            print(f"\n{'='*50}")
            print(f"PHASE {phase_num}: {phase_name.upper()} - ATTEMPT {attempt}")
            print(f"{'='*50}")
            
            # Step 1: Implementation
            impl_result = self.launch_implementation_agent(phase_num, phase_name)
            if not impl_result:
                print(f"❌ Implementation failed on attempt {attempt}")
                continue
                
            # Step 2: Evaluation  
            eval_result = self.launch_evaluation_agent(phase_num, phase_name)
            if not eval_result:
                print(f"❌ Evaluation failed on attempt {attempt}")
                continue
                
            # Step 3: Check results
            passed, score = self.check_evaluation_result(phase_num)
            
            print(f"\n📊 PHASE {phase_num} RESULTS:")
            print(f"   Score: {score}/100")
            print(f"   Status: {'PASS' if passed else 'FAIL'}")
            
            if passed:
                print(f"✅ Phase {phase_num} PASSED! Score: {score}/100")
                return True
            else:
                print(f"❌ Phase {phase_num} FAILED! Score: {score}/100")
                
                if attempt < max_attempts:
                    # Extract issues for remediation
                    result_file = self.evaluation_dir / f"phase{phase_num}_evaluation_result.md"
                    with open(result_file) as f:
                        issues = f.read()
                    
                    # Launch remediation
                    remediation_result = self.launch_remediation_agent(phase_num, phase_name, issues)
                    
        print(f"💥 Phase {phase_num} FAILED after {max_attempts} attempts")
        return False

# Phase sequence configuration
PHASE_SEQUENCE = [
    (10, "blueprint_builder"),
    (11, "blueprint_integration_testing"), 
    (12, "rabbitmq_integration"),
    (13, "system_testing"),
    (14, "enterprise_integration")
]

def run_all_phases():
    """Run all phases automatically"""
    manager = AutoPhaseManager()
    
    print("🚀 STARTING AUTOMATIC PHASE PROGRESSION")
    print("📋 Requirement: 100/100 score to pass each phase")
    print("🔄 Auto-progression: Phases launch automatically after PASS")
    
    for phase_num, phase_name in PHASE_SEQUENCE:
        print(f"\n🎯 Starting Phase {phase_num}: {phase_name}")
        
        success = manager.auto_run_phase(phase_num, phase_name)
        
        if not success:
            print(f"🛑 STOPPING: Phase {phase_num} failed after max attempts")
            return False
            
        print(f"✅ Phase {phase_num} COMPLETE - Auto-progressing to next phase...")
        time.sleep(2)  # Brief pause between phases
        
    print("\n🎉 ALL PHASES COMPLETE!")
    return True

if __name__ == "__main__":
    # Start with Phase 10 (Phase 9 already complete)
    manager = AutoPhaseManager()
    success = manager.auto_run_phase(10, "blueprint_builder")
    
    if success:
        print("\n🎯 Phase 10 PASSED - Ready for automatic progression!")
    else:
        print("\n❌ Phase 10 FAILED - Fix required before progression")