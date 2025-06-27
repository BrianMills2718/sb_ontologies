#!/bin/bash
# Multi-Agent Orchestration Script V2 - Real Isolation
# Project: hello_world_test_v2

set -e  # Exit on any error

PROJECT_DIR="hello_world_test_v2"
SHARED_DIR="$PROJECT_DIR/shared"
EVIDENCE_DIR="$SHARED_DIR/evidence"

echo "🚀 Starting Multi-Agent Process: hello_world_test_v2"
echo "📁 Project Directory: $PROJECT_DIR"
echo "📊 Evidence Directory: $EVIDENCE_DIR"
echo ""

# Function to run implementation phase
run_implementation() {
    local phase_name=$1
    local phase_dir="$PROJECT_DIR/${phase_name}_implementation"
    
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
}

# Function to run evaluation phase  
run_evaluation() {
    local phase_name=$1
    local phase_dir="$PROJECT_DIR/${phase_name}_evaluation"
    
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
}

# Run all phases

echo "=========================================="
echo "Phase: create_file"
echo "Description: Create a simple hello world text file"
echo "=========================================="

run_implementation "create_file"
run_evaluation "create_file"

echo "🎉 Phase create_file complete!"
echo ""

echo "=========================================="
echo "Phase: modify_file"
echo "Description: Modify the file to add additional content"
echo "=========================================="

run_implementation "modify_file"
run_evaluation "modify_file"

echo "🎉 Phase modify_file complete!"
echo ""

echo "=========================================="
echo "Phase: verify_result"
echo "Description: Verify the final file has expected content"
echo "=========================================="

run_implementation "verify_result"
run_evaluation "verify_result"

echo "🎉 Phase verify_result complete!"
echo ""

echo "🎊 All phases complete for hello_world_test_v2!"
echo "📊 Check evidence in: $EVIDENCE_DIR"
echo ""
echo "📋 Summary of completed phases:"
echo "  ✅ create_file: Create a simple hello world text file"
echo "  ✅ modify_file: Modify the file to add additional content"
echo "  ✅ verify_result: Verify the final file has expected content"

echo ""
echo "🏁 Multi-agent process finished successfully!"
