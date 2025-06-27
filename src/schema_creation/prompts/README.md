# Schema Extraction Prompts

This directory contains all prompts used by the schema extraction system. Prompts are stored as separate text files for easy maintenance and modification.

## Directory Structure

```
prompts/
├── simple/                 # Simple processor prompts
│   └── extraction_prompt.txt
└── multiphase/            # Multiphase processor prompts
    ├── phase1_vocabulary_extraction.txt
    ├── phase2_ontological_classification.txt
    └── phase3_schema_generation.txt
```

## Simple Processor

**File**: `simple/extraction_prompt.txt`
- Single-pass extraction for quick results
- Extracts 20-30 key terms
- Recommends model type

## Multiphase Processor

### Phase 1: Vocabulary Extraction
**File**: `multiphase/phase1_vocabulary_extraction.txt`
- Exhaustive extraction of all theoretical terms
- Captures definitions, context, and categories
- No artificial limits on vocabulary size

### Phase 2: Ontological Classification  
**File**: `multiphase/phase2_ontological_classification.txt`
- Classifies terms into 8 semantic categories
- Specifies domain/range for relationships
- Preserves theoretical hierarchies

### Phase 3: Schema Generation
**File**: `multiphase/phase3_schema_generation.txt`
- Selects optimal model type (including hypergraph)
- Designs comprehensive node and edge types
- Includes modifiers and operators

## Model Types

Current supported model types:
- **property_graph**: Rich binary relationships between entities
- **hypergraph**: N-ary relationships, recursive structures, hyperedges
- **table_matrix**: Classifications or typologies
- **sequence**: Ordered processes or stages
- **tree**: Hierarchical taxonomies
- **timeline**: Temporal evolution
- **other**: Unique structures

## Modifying Prompts

1. Edit the relevant `.txt` file
2. Changes take effect immediately (prompts are loaded dynamically)
3. Test changes with a sample paper
4. Clear prompt cache if needed: `prompt_loader.clear_prompt_cache()`

## Best Practices

1. **Be Specific**: Include clear instructions and examples
2. **List Options**: Explicitly list all model types and categories
3. **Preserve Structure**: Maintain consistent formatting
4. **Test Changes**: Always test prompt changes with multiple papers
5. **Document Updates**: Note significant changes in commit messages

## Adding New Model Types

To add a new model type:
1. Update `phase3_schema_generation.txt` with the new type
2. Update Pydantic models in processors to include the type
3. Add handling in `convert_to_yaml_format()` function
4. Update this README

## Examples

### Adding a New Model Type
```text
   - property_graph: Rich relationships between diverse entities
   - hypergraph: N-ary relationships where edges connect multiple vertices
   - YOUR_NEW_TYPE: Description of when to use this type
```

### Emphasizing N-ary Relations
```text
2. **Considers hypergraph indicators**:
   - Relationships involving 3+ participants
   - Recursive or nested structures
   - Ordered sequences in relationships
```