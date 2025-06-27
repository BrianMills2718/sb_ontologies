# Automated Theory Extraction and Application System

## 🎯 **PROJECT GOAL**
Create an automated system that reads academic papers, extracts theoretical schemas with high fidelity, and applies them to data to produce results comparable to the original paper.

**Core Workflow**: Academic Paper → Schema Extraction → Data Application → Comparable Results

## 📂 **CODEBASE ORGANIZATION** (MANDATORY STRUCTURE)

### **Required Directory Structure**
```
/home/brian/lit_review/
├── src/                              # ALL CODE GOES HERE
│   ├── schema_creation/              # Schema generation scripts
│   │   ├── multiphase_processor_improved.py    # Main 3-phase processor
│   │   ├── multiphase_processor_expanded.py    # Option 1: Integrated notation
│   │   ├── implementation_extractor.py         # Option 2: Separate implementation
│   │   └── prompts/                            # External prompt files
│   ├── schema_application/           # Scripts that apply schemas to data  
│   ├── visualization/                # Network plots, diagrams, charts
│   ├── testing/                      # Test scripts and validation
│   └── ui/                          # User interface and analysis tools
├── schemas/                          # Generated schemas organized by theory
│   └── {theory_name}/               # One folder per theory
├── results/                          # Test results and validation reports
│   └── {theory_name}/               # Results organized by theory
├── data/                            # All data files
│   ├── papers/                      # PDF/txt source papers
│   └── test_texts/                  # Text files for testing schemas
├── examples/                        # Example schemas and analyses
└── docs/                           # Documentation files
```

### **File Naming Rules**
1. **ALL new code** must go in appropriate `src/` subdirectory
2. **Schemas**: Save to `schemas/{theory_name}/schema_name.yml`
3. **Results**: Save to `results/{theory_name}/result_name.txt`
4. **NO loose Python files** in root directory

## 🛠️ **CURRENT CAPABILITIES**

### **Schema Extraction** (3-Phase Process)
1. **Phase 1**: Extract ALL vocabulary terms with definitions
2. **Phase 2**: Classify into entities, relationships, properties, actions, etc.
3. **Phase 3**: Generate theory-adaptive schema with appropriate model type
   - **NEW**: Full Phase 1 vocabulary passed to Phase 3 (prevents information loss)

### **Model Types Supported**
- `property_graph`: Rich relationships between entities
- `hypergraph`: N-ary relationships, recursive structures ✅ NEW
- `table_matrix`: Classifications, typologies
- `sequence`: Ordered processes, stages
- `tree`: Hierarchical taxonomies
- `timeline`: Temporal evolution
- `other`: Custom representations

### **Notation Extraction** (Two Approaches)
1. **Option 1**: Expanded schema with integrated notation/patterns
2. **Option 2**: Separate implementation specification
3. **Recommendation**: Use hybrid approach for theories with formal notation

## 🔄 **CURRENT STATUS**

### **Recent Improvements**
1. ✅ Fixed information loss between phases (was losing 40% of terms)
2. ✅ Added explicit hypergraph model type
3. ✅ Implemented notation extraction (Options 1 & 2)
4. ✅ Separated prompts from code for maintainability

### **Test Case: Young 1996**
- **Current**: 34% fidelity 
- **Target**: Match `examples/carter_young1996_faithful_analysis.yml`
- **Status**: Need to apply improved extraction methods

### **Semantic Hypergraph Case Study**
- Successfully extracted basic schema
- Option 2 captured 60% of implementation details
- Missing: Type inference rules, algorithms, complete patterns

## 📋 **NEXT STEPS**

### **1. Multi-Pass Extraction** (Priority: HIGH)
Implement specialized extractors for:
- Pass 1: Notation and symbols
- Pass 2: Tables and formal rules  
- Pass 3: Algorithms and pseudocode
- Pass 4: Metrics and evaluation
- Pass 5: Complete examples

### **2. Test Improved Young 1996 Extraction**
Apply enhanced methods to achieve target fidelity

### **3. Create Hybrid Pipeline**
Combine Option 1 (structure) + Option 2 (detail) for optimal extraction

## 💡 **KEY INSIGHTS**

### **Information Preservation**
- Phase 3 must receive FULL Phase 1 vocabulary
- Implementation details need dedicated extraction
- Notation systems are part of theory, not just implementation

### **Extraction Strategies**
- **Simple theories**: Standard 3-phase sufficient
- **Formal theories**: Need multi-pass + notation extraction
- **Complex theories**: Hybrid approach recommended

## 🚀 **QUICK START COMMANDS**

```bash
# Standard extraction
python -m src.schema_creation.multiphase_processor_improved paper.txt schemas/theory/schema.yml

# With notation (Option 1)
python src/schema_creation/multiphase_processor_expanded.py paper.txt schemas/theory/expanded.yml

# Implementation details (Option 2)
python src/schema_creation/implementation_extractor.py paper.txt schemas/theory/implementation.yml

# Apply schema to data
python src/schema_application/apply_schema.py schema.yml data.txt results/output.yml
```

## 📐 **TECHNICAL CONFIG**
- **Model**: OpenAI O3
- **Environment**: Set OPENAI_API_KEY in .env
- **Python**: 3.10+

## 🎯 **SUCCESS METRICS**
- Extract 90%+ of theoretical terms
- Capture formal notation when present
- Match fidelity of manual extraction
- Reproduce paper's original results