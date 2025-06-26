# Multiphase Academic Paper Processor

This script implements a three-phase approach to converting academic papers into structured schemas, addressing the confusion issues identified in the single-phase approach.

## Why Multiphase?

The original single-phase approach tried to do everything at once:
- Extract vocabulary
- Classify concepts  
- Define relationships
- Specify constraints
- Map to graph structure

This created confused hybrid schemas that mixed ontological concepts with implementation details.

## The Three Phases

### Phase 1: Vocabulary Extraction
**Goal**: Extract all theoretical terms from the paper

**Output**:
- Citation and annotation
- Complete list of terms with definitions and context
- No classification or structure yet

**Example**:
```yaml
vocabulary:
  - term: "influence_strategy"
    definition: "Approaches used to affect target audience behavior"
    source_context: "...three main influence strategies: persuasion, coercion..."
    page_reference: "p. 42"
```

### Phase 2: Ontological Classification  
**Goal**: Classify terms into semantic categories

**Output**:
- Entities (things that exist)
- Relationships (connections with domain/range)
- Properties (attributes)
- Actions (behaviors with domain/range)
- Measures (metrics)

**Key**: Only relationships and actions have domain/range constraints

**Example**:
```yaml
relationships:
  - term: "influences"
    domain: ["Actor", "Strategy"]
    range: ["Audience", "Outcome"]
```

### Phase 3: Graph Schema Generation
**Goal**: Design implementable graph structure

**Output**:
- Model type selection with rationale
- Node type definitions
- Edge type definitions  
- Property definitions

**Example**:
```yaml
node_types:
  - name: "Actor"
    properties: ["name", "authority_level", "resources"]
edge_types:
  - name: "INFLUENCES"
    from_types: ["Actor", "Strategy"]
    to_types: ["Audience", "Outcome"]
```

## Usage

```bash
# Basic usage
python multiphase_processor.py paper.txt output.yml

# Example
python multiphase_processor.py literature/young1996.txt literature/young1996_multiphase.yml
```

## Benefits

1. **Clear Separation**: Each phase has a specific goal
2. **No Mixed Concepts**: Entities don't have domain/range
3. **Better Model Selection**: Phase 3 can properly evaluate model type
4. **Debugging**: Intermediate outputs saved in debug/ folder
5. **Quality Control**: Can verify each phase independently

## Output Structure

The final YAML maintains compatibility with existing format but with cleaner semantics:
- Entities are clearly entities (no domain/range)
- Only relationships/actions have domain/range
- Model type selection is based on actual structure
- No confusion between vocabulary and schema

## Debugging

Check the `debug/` folder for intermediate outputs:
- `*_phase1.json`: Raw vocabulary extraction
- `*_phase2.json`: Classification results
- `*_phase3.json`: Schema design

This helps identify which phase might need adjustment for specific papers.