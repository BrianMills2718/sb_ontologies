# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a literature review and knowledge modeling project that processes academic papers through an improved multiphase workflow to create structured, machine-readable representations of academic theories using JSON Schema and semantic networks.

For detailed project goals and methodology, see **PROJECT_OVERVIEW.md**.

## Current System Architecture

### Multiphase Processing System (Primary Approach)

The project uses a three-phase processing pipeline that separates concerns for better semantic accuracy:

1. **Phase 1: Vocabulary Extraction** - Comprehensively extracts all theoretical terms from papers
2. **Phase 2: Ontological Classification** - Classifies terms into proper categories with specific domain/range
3. **Phase 3: Schema Generation** - Creates theory-adaptive schemas based on the classified vocabulary

#### Key Processors:
- **multiphase_processor_improved.py** - Main processor with O3 support and comprehensive extraction
- **multiphase_processor_simple.py** - Simplified version for quick testing
- **multiphase_processor.py** - Original basic version (legacy)

#### Supporting Files:
- **MULTIPHASE_README.md** - Detailed documentation of the multiphase approach
- **compare_processors.py** - Tool to compare outputs between different processors
- **problems_to_fix.txt** - Identified issues with original approach

### Archive

Old schemas and raw outputs have been moved to `archive/old_schemas/` for reference.

## Key Improvements in Current System

1. **No Domain/Range on Entities** - Only relationships and actions have domain/range constraints
2. **Comprehensive Extraction** - No artificial limits on vocabulary size
3. **Specific Domain/Range** - Uses theory-specific types (Actor→Statement, not Entity→Entity)
4. **Preserved Subcategories** - Maintains theory-specific categories
5. **Complete Ontology** - Includes modifiers, truth values, and operators
6. **Theory-Adaptive Schemas** - Genuinely selects appropriate model type
7. **Hierarchical Support** - Preserves subTypeOf relationships

## Processing Workflow

```bash
# Process a new paper with the improved processor
python multiphase_processor_improved.py "path/to/paper.txt" "path/to/output.yml"

# Compare different processor outputs
python compare_processors.py
```

### Input Requirements
- Academic papers in plain text format (.txt)
- Papers should be placed in appropriate subdirectories under `literature/`

### Output Structure
```yaml
citation: Full bibliographic citation
annotation: 2-3 sentence summary
model_type: property_graph|table_matrix|sequence|tree|timeline|other
rationale: Detailed justification for model type
schema_blueprint:
  title: Theory-specific title
  description: Comprehensive description
  root_properties: Model-specific structure
  definitions: All terms with proper categorization
  modifiers_supported: Temporal/modal modifiers
  truth_values_supported: Truth value system
```

## Model Requirements

- **OpenAI Model**: O3 (configured in .env)
- **API Key**: Required in .env file
- **Dependencies**: See requirements.txt

## Data Organization

```
literature/
├── category_name/
│   ├── paper_name.txt (input)
│   ├── paper_name_improved.yml (output)
│   └── debug_improved/ (phase outputs)
└── Index.md (paper registry)

archive/
└── old_schemas/ (legacy outputs)
```

## Quality Standards

1. **Entities** must NOT have domain/range properties
2. **Relationships/Actions** must have specific domain/range types
3. **Subcategories** should preserve theoretical terminology
4. **Model Type** must match theory structure with detailed rationale
5. **Modifiers** should be included when present in the theory

## Debugging

Check `debug_improved/` folders for intermediate phase outputs:
- `*_phase1.json` - Extracted vocabulary
- `*_phase2.json` - Classified terms
- `*_phase3.json` - Generated schema

## Notes

- O3 model does not support temperature parameters
- Processing may take 1-2 minutes per paper with O3
- Always verify outputs maintain theoretical accuracy