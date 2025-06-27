#!/usr/bin/env python3
"""
Literature Review Multi-Agent Implementation Runner
Implements balanced multi-purpose computational social science framework
"""
import sys
from pathlib import Path

# Add multi-agent system to path
sys.path.append(str(Path(__file__).parent / "multi_agent_system"))

from auto_phase_manager import AutoPhaseManager

class LiteratureReviewMultiAgent:
    """Multi-agent implementation for balanced literature review framework"""
    
    def __init__(self):
        self.manager = AutoPhaseManager()
        # Configure for literature review project
        self.manager.phases_dir = Path("/home/brian/lit_review/multi_agent_system/phases")
        self.manager.evaluation_dir = self.manager.phases_dir / "evaluation_clean"
        
    def run_all_phases(self):
        """Run all 6 phases for balanced multi-purpose framework"""
        
        print("🚀 STARTING BALANCED MULTI-PURPOSE COMPUTATIONAL SOCIAL SCIENCE IMPLEMENTATION")
        print("📋 Requirement: 100/100 score to pass each phase")
        print("🔄 Auto-progression: Phases launch automatically after PASS")
        print("⚖️ CRITICAL: Equal sophistication across all five purposes required")
        
        phases = [
            (1, "purpose_classification"),
            (2, "vocabulary_extraction"), 
            (3, "schema_generation"),
            (4, "integration_pipeline"),
            (5, "reasoning_engine"),
            (6, "production_validation")
        ]
        
        for phase_num, phase_name in phases:
            print(f"\n🎯 Starting Phase {phase_num}: {phase_name}")
            print(f"📍 Balance Requirement: Equal treatment of descriptive/explanatory/predictive/causal/intervention")
            
            success = self.manager.auto_run_phase(phase_num, phase_name)
            
            if not success:
                print(f"🛑 STOPPING: Phase {phase_num} failed after max attempts")
                print(f"❌ Balance requirement not met or implementation issues")
                return False
                
            print(f"✅ Phase {phase_num} COMPLETE - Balanced implementation validated")
            print(f"🔄 Auto-progressing to next phase...")
            
        print("\n🎉 ALL PHASES COMPLETE!")
        print("✅ Balanced Multi-Purpose Computational Social Science Framework READY")
        print("📊 Equal sophistication across all five analytical purposes achieved")
        return True

def main():
    """Main execution function"""
    runner = LiteratureReviewMultiAgent()
    success = runner.run_all_phases()
    
    if success:
        print("\n🌟 IMPLEMENTATION SUCCESS!")
        print("The balanced computational social science framework is ready for production use.")
        print("All five purposes (descriptive/explanatory/predictive/causal/intervention) are equally supported.")
    else:
        print("\n💥 IMPLEMENTATION FAILED!")
        print("Balance requirements not met. Review phase failures and remediate.")

if __name__ == "__main__":
    main()