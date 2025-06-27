# Multi-Agent Phase Implementation System

This directory implements isolated phase development with clean evaluation.

## Directory Structure

```
phases/
├── phase2_isolated/
│   ├── CLAUDE.md                   # Phase 2 isolated implementation instructions
│   └── evidence/                   # Phase 2 outputs here (auto-created by agent)
├── phase3_blueprint_isolated/
│   ├── CLAUDE.md                   # Phase 3 isolated implementation instructions  
│   └── evidence/                   # Phase 3 outputs here (auto-created by agent)
└── evaluation_clean/
    ├── evaluation_criteria.md      # External evaluation criteria
    ├── current_evidence/            # Copy evidence here for evaluation
    └── evaluation_result.md        # Evaluator writes result here
```

## Workflow

### Step 1: Launch Implementation Agent
```bash
# For Phase 2
Task: "Read /home/brian/autocoder3_cc/phases/phase2_isolated/CLAUDE.md and implement Phase 2 completely. Create evidence directory and output all evidence files."

# For Phase 3  
Task: "Read /home/brian/autocoder3_cc/phases/phase3_blueprint_isolated/CLAUDE.md and implement Phase 3 completely. Create evidence directory and output all evidence files."
```

### Step 2: Copy Evidence for Evaluation
```bash
# Copy phase evidence to evaluation directory
cp phases/phase2_isolated/evidence/* phases/evaluation_clean/current_evidence/
# or
cp phases/phase3_blueprint_isolated/evidence/* phases/evaluation_clean/current_evidence/
```

### Step 3: Launch Evaluation Agent
```bash
Task: "You are an external evaluator. Read /home/brian/autocoder3_cc/phases/evaluation_clean/evaluation_criteria.md and evaluate the evidence in /home/brian/autocoder3_cc/phases/evaluation_clean/current_evidence/ directory. Write your evaluation result to /home/brian/autocoder3_cc/phases/evaluation_clean/evaluation_result.md"
```

### Step 4: Read Result and Decide
- Read `phases/evaluation_clean/evaluation_result.md`
- If PASS: Setup next phase
- If FAIL: Provide feedback to implementation agent

## Key Benefits

1. **Zero Context Leakage** - Each agent only sees its specific instructions
2. **Complete Isolation** - Implementation agents don't know about other phases
3. **Rigorous Evaluation** - Evaluation agents have no implementation context
4. **Clean Handoffs** - Clear evidence packages between phases
5. **Verifiable Process** - Full audit trail of what each agent received

## Ready to Use

The system is set up and ready. Start with Phase 2 or Phase 3 evaluation as needed.