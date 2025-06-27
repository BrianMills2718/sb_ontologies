#!/usr/bin/env python3
"""
Multi-Agent Template V2 - Project Generator
Generates isolated directory structure with real context separation
"""

import os
import yaml
import shutil
from pathlib import Path

def load_config():
    """Load project configuration"""
    with open('config.yaml', 'r') as f:
        return yaml.safe_load(f)

def create_directory_structure(config):
    """Create the isolated directory structure"""
    project_name = config['project_name']
    phases = config['phases']
    
    # Create main project directory
    project_dir = Path(project_name)
    project_dir.mkdir(exist_ok=True)
    
    # Create shared directory
    shared_dir = project_dir / 'shared'
    shared_dir.mkdir(exist_ok=True)
    
    evidence_dir = shared_dir / 'evidence'
    evidence_dir.mkdir(exist_ok=True)
    
    # Copy config to shared
    shutil.copy('config.yaml', shared_dir / 'config.yaml')
    
    # Create phase directories
    for phase in phases:
        phase_name = phase['name']
        
        # Implementation directory
        impl_dir = project_dir / f"{phase_name}_implementation"
        impl_dir.mkdir(exist_ok=True)
        
        # Evaluation directory  
        eval_dir = project_dir / f"{phase_name}_evaluation"
        eval_dir.mkdir(exist_ok=True)
        
        # Create symlink to evidence in evaluation directory
        evidence_link = eval_dir / 'evidence'
        if not evidence_link.exists():
            evidence_link.symlink_to('../../shared/evidence')
    
    return project_dir

def generate_claude_md_files(config, project_dir):
    """Generate CLAUDE.md files for each directory"""
    phases = config['phases']
    
    # Implementation CLAUDE.md template
    impl_claude_content = """# Implementation Agent Context

You are an isolated implementation agent. Your task:
1. Read instructions.md in this directory
2. Complete the implementation task exactly as specified
3. Store all evidence in ../shared/evidence/ directory
4. Work completely independently with no external context

## Available Tools
- Read/Write files in current directory and ../shared/evidence/
- Execute code and bash commands as needed
- Use standard development tools

## Isolation Requirements
- Do NOT reference any context outside this directory
- Do NOT access other phase directories
- Base work only on instructions.md and files you create
- Store ALL outputs in ../shared/evidence/

## Success Criteria
Your implementation will be evaluated by a separate agent based only on evidence you provide.
Make sure evidence clearly demonstrates successful completion.
"""

    # Evaluation CLAUDE.md template
    eval_claude_content = """# Evaluation Agent Context

You are an isolated evaluation agent. Your task:
1. Read evaluation.md in this directory for assessment criteria
2. Examine evidence in ./evidence/ directory
3. Provide objective PASS/FAIL assessment
4. Work completely independently with no implementation context

## Available Tools
- Read files in current directory and evidence/ subdirectory
- Analyze and assess evidence objectively
- NO modification or creation of files

## Isolation Requirements
- Do NOT access implementation directories
- Do NOT reference implementation process
- Base assessment ONLY on evidence provided and evaluation criteria
- Provide objective, evidence-based evaluation

## Evaluation Requirements
- Either PASS (70+ score) or FAIL (below 70)
- No conditional passes or partial credit
- Must justify assessment with specific evidence references
"""

    # Create CLAUDE.md for each phase
    for phase in phases:
        phase_name = phase['name']
        
        # Implementation CLAUDE.md
        impl_dir = project_dir / f"{phase_name}_implementation"
        with open(impl_dir / 'CLAUDE.md', 'w') as f:
            f.write(impl_claude_content)
        
        # Evaluation CLAUDE.md
        eval_dir = project_dir / f"{phase_name}_evaluation"  
        with open(eval_dir / 'CLAUDE.md', 'w') as f:
            f.write(eval_claude_content)

def generate_instruction_files(config, project_dir):
    """Generate instructions.md and evaluation.md files"""
    phases = config['phases']
    
    for phase in phases:
        phase_name = phase['name']
        phase_desc = phase['description']
        
        # Generate instructions.md
        impl_dir = project_dir / f"{phase_name}_implementation"
        instructions_content = f"""# Phase {phase_name}: {phase_desc}

## Task Description
{phase_desc}

## Requirements
<!-- Customize these requirements for your specific phase -->
1. Complete the implementation as specified
2. Verify the implementation works correctly
3. Document what was accomplished
4. Store all evidence in ../shared/evidence/

## Success Criteria
<!-- Customize these criteria for your specific phase -->
- Implementation is complete and functional
- All requirements are met
- Evidence clearly demonstrates success
- Documentation is accurate and complete

## Evidence Requirements
Create these files in ../shared/evidence/:
- `{phase_name}_output.txt` - Primary deliverable/result
- `{phase_name}_summary.txt` - Summary of what was accomplished
- `{phase_name}_verification.txt` - Proof that implementation works

## Implementation Notes
- Work completely independently
- Focus only on this specific phase
- Base work only on these instructions
- Create comprehensive evidence for evaluation

## Completion Checklist
- [ ] All requirements implemented
- [ ] Implementation verified to work
- [ ] Evidence files created
- [ ] Summary documentation complete
"""
        
        with open(impl_dir / 'instructions.md', 'w') as f:
            f.write(instructions_content)
        
        # Generate evaluation.md
        eval_dir = project_dir / f"{phase_name}_evaluation"
        evaluation_content = f"""# Phase {phase_name}: {phase_desc} - Evaluation

## Evaluation Task
Assess whether Phase {phase_name} was completed successfully by examining evidence.

## Files to Check
Examine these files in ./evidence/:
- `{phase_name}_output.txt` - Primary deliverable
- `{phase_name}_summary.txt` - Implementation summary  
- `{phase_name}_verification.txt` - Verification proof

## Pass Requirements (ALL must be met)
<!-- Customize these requirements for your specific phase -->
1. **Files Exist**: All required evidence files exist and are readable
2. **Content Quality**: Files contain substantive, accurate content
3. **Requirements Met**: Implementation meets specified requirements
4. **Verification Provided**: Evidence demonstrates implementation works
5. **Summary Accurate**: Summary correctly describes accomplishments

## Fail Conditions (ANY causes failure)
<!-- Customize these conditions for your specific phase -->
- Required files missing or empty
- Content is placeholder text or incomplete
- Implementation doesn't meet requirements
- No verification provided
- Summary is inaccurate or missing

## Evaluation Process
1. Check each required evidence file exists
2. Verify content quality and completeness
3. Assess implementation against requirements
4. Validate verification claims
5. Score objectively based only on evidence

## Output Format
Provide result in exactly this format:

```
RESULT: PASS
SCORE: [0-100]
ISSUES: [list any issues found, or "None"]
SUMMARY: [brief description of what was accomplished]
```

OR

```
RESULT: FAIL  
SCORE: [0-100]
ISSUES: [list specific failures]
SUMMARY: [brief description of what was attempted]
```

## Scoring Guidelines
- **90-100**: Excellent, exceeds requirements
- **70-89**: Good, meets all requirements (minimum for PASS)
- **50-69**: Acceptable, minor issues (FAIL)
- **30-49**: Poor, major issues (FAIL)
- **0-29**: Failed, requirements not met (FAIL)

## Isolation Requirements
- Base assessment ONLY on evidence provided
- Do NOT access implementation directories
- Do NOT reference implementation process
- Evaluate objectively and independently
"""
        
        with open(eval_dir / 'evaluation.md', 'w') as f:
            f.write(evaluation_content)

def generate_orchestration_script(config, project_dir):
    """Generate the run_all_phases.sh orchestration script"""
    phases = config['phases']
    project_name = config['project_name']
    
    script_content = f"""#!/bin/bash
# Multi-Agent Orchestration Script V2 - Real Isolation
# Project: {project_name}

set -e  # Exit on any error

PROJECT_DIR="{project_name}"
SHARED_DIR="$PROJECT_DIR/shared"
EVIDENCE_DIR="$SHARED_DIR/evidence"

echo "🚀 Starting Multi-Agent Process: {project_name}"
echo "📁 Project Directory: $PROJECT_DIR"
echo "📊 Evidence Directory: $EVIDENCE_DIR"
echo ""

# Function to run implementation phase
run_implementation() {{
    local phase_name=$1
    local phase_dir="$PROJECT_DIR/${{phase_name}}_implementation"
    
    echo "🔧 Phase $phase_name: Implementation"
    echo "📂 Directory: $phase_dir"
    
    # Check that directory exists
    if [ ! -d "$phase_dir" ]; then
        echo "❌ ERROR: Implementation directory not found: $phase_dir"
        exit 1
    fi
    
    # Manual step - requires user to run Claude Code
    echo "👤 MANUAL STEP REQUIRED:"
    echo "   1. Open new terminal"
    echo "   2. cd $phase_dir"
    echo "   3. Run: claude"
    echo "   4. Implementation agent will read instructions.md and complete task"
    echo "   5. Press Enter here when implementation complete..."
    read -p "   Implementation done? Press Enter to continue: " 
    
    echo "✅ Implementation phase complete"
    echo ""
}}

# Function to run evaluation phase  
run_evaluation() {{
    local phase_name=$1
    local phase_dir="$PROJECT_DIR/${{phase_name}}_evaluation"
    
    echo "📊 Phase $phase_name: Evaluation"
    echo "📂 Directory: $phase_dir"
    
    # Check that directory exists
    if [ ! -d "$phase_dir" ]; then
        echo "❌ ERROR: Evaluation directory not found: $phase_dir"
        exit 1
    fi
    
    # Manual step - requires user to run Claude Code
    echo "👤 MANUAL STEP REQUIRED:"
    echo "   1. Open new terminal" 
    echo "   2. cd $phase_dir"
    echo "   3. Run: claude"
    echo "   4. Evaluation agent will read evaluation.md and assess evidence"
    echo "   5. Press Enter here when evaluation complete..."
    read -p "   Evaluation done? Press Enter to continue: "
    
    echo "✅ Evaluation phase complete"
    echo ""
}}

# Run all phases
"""

    # Add phase execution
    for phase in phases:
        phase_name = phase['name']
        script_content += f"""
echo "=========================================="
echo "Phase: {phase_name}"
echo "Description: {phase['description']}"
echo "=========================================="

run_implementation "{phase_name}"
run_evaluation "{phase_name}"

echo "🎉 Phase {phase_name} complete!"
echo ""
"""

    script_content += f"""
echo "🎊 All phases complete for {project_name}!"
echo "📊 Check evidence in: $EVIDENCE_DIR"
echo ""
echo "📋 Summary of completed phases:"
"""

    for phase in phases:
        script_content += f'echo "  ✅ {phase["name"]}: {phase["description"]}"' + '\n'

    script_content += """
echo ""
echo "🏁 Multi-agent process finished successfully!"
"""
    
    script_path = project_dir / 'run_all_phases.sh'
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    # Make executable
    os.chmod(script_path, 0o755)

def main():
    """Main generation function"""
    if not os.path.exists('config.yaml'):
        print("❌ Error: config.yaml not found")
        print("Copy config.yaml.example to config.yaml and customize it")
        return
    
    config = load_config()
    print(f"🚀 Generating project: {config['project_name']}")
    
    # Create directory structure
    project_dir = create_directory_structure(config)
    print(f"📁 Created directory structure in: {project_dir}")
    
    # Generate CLAUDE.md files
    generate_claude_md_files(config, project_dir)
    print("📝 Generated CLAUDE.md files for context isolation")
    
    # Generate instruction files
    generate_instruction_files(config, project_dir)
    print("📋 Generated instructions.md and evaluation.md files")
    
    # Generate orchestration script
    generate_orchestration_script(config, project_dir)
    print("🔧 Generated run_all_phases.sh orchestration script")
    
    print("\n🎉 Project generation complete!")
    print(f"\nNext steps:")
    print(f"1. cd {project_dir}")
    print(f"2. Customize instructions.md and evaluation.md files")
    print(f"3. ./run_all_phases.sh")

if __name__ == "__main__":
    main()