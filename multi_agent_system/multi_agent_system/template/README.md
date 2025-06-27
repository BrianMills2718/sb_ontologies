# Multi-Agent Template V2 - Real Context Isolation

**Purpose**: Multi-agent automation using real context isolation via separate Claude Code instances and directory-based context control.

## 🚀 Key Innovation: Real Isolation

Unlike V1 (roleplay isolation), V2 uses **actual technical isolation**:
- Separate directories with different CLAUDE.md files
- Each agent runs in its own Claude Code instance
- No shared context between implementation and evaluation

## 📁 Generated Project Structure

```
my_project/
├── shared/
│   ├── config.yaml
│   ├── evidence/
│   └── run_all_phases.sh
├── phase_a_implementation/
│   ├── CLAUDE.md (implementation context)
│   └── instructions.md
├── phase_a_evaluation/
│   ├── CLAUDE.md (evaluation context)
│   ├── evaluation.md
│   └── evidence/ (symlink to shared/evidence)
├── phase_b_implementation/
│   ├── CLAUDE.md
│   └── instructions.md
└── phase_b_evaluation/
    ├── CLAUDE.md
    ├── evaluation.md
    └── evidence/ (symlink)
```

## 🔧 How Real Isolation Works

### **Implementation Agent**
```bash
cd phase_a_implementation/
claude  # Sees only implementation CLAUDE.md and instructions.md
```

### **Evaluation Agent**  
```bash
cd phase_a_evaluation/
claude  # Sees only evaluation CLAUDE.md, evaluation.md, and evidence/
```

### **No Shared Context**
- Implementation agent cannot see evaluation criteria
- Evaluation agent cannot see implementation instructions
- Both work with evidence in shared directory

## 🛠️ Setup Instructions

```bash
# 1. Copy template
cp -r multi_agent_template_v2 my_new_project
cd my_new_project

# 2. Configure project
cp config.yaml.example config.yaml
edit config.yaml

# 3. Generate isolated directories
python generate_project.py

# 4. Run multi-agent process
./run_all_phases.sh
```

## 📊 Template Files

- `config.yaml.example` - Project configuration
- `generate_project.py` - Creates isolated directory structure
- `templates/` - Templates for CLAUDE.md and instruction files
- `run_all_phases.sh` - Automated orchestration script