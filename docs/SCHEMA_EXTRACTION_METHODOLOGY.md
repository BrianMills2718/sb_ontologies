# Schema Extraction Methodology

## Overview

This document describes the three-phase methodology for automatically extracting theoretical schemas from academic papers. The system transforms academic papers into structured knowledge representations that can be computationally instantiated with data.

**Core Workflow**: Academic Paper → Schema Extraction → Data Application → Comparable Results

## Architecture

```
┌─────────────────┐
│  Academic Paper │
│     (.txt)      │
└────────┬────────┘
         │
    ┌────▼────┐
    │ Phase 1 │ Comprehensive Vocabulary Extraction
    └────┬────┘
         │
    ┌────▼────┐
    │ Phase 2 │ Ontological Classification
    └────┬────┘
         │
    ┌────▼────┐
    │ Phase 3 │ Theory-Adaptive Schema Generation
    └────┬────┘
         │
┌────────▼────────┐
│  YAML Schema    │
│     (.yml)      │
└─────────────────┘
```

## Phase 1: Comprehensive Vocabulary Extraction

### Purpose
Extract ALL theoretical terms, concepts, relationships, and specialized vocabulary from academic papers without artificial limits.

### Input
- Raw text of academic paper (UTF-8 encoded)
- No preprocessing required

### Process
The OpenAI model (O3) analyzes the paper to identify:

1. **Core Concepts and Constructs**
   - Primary theoretical entities
   - Abstract concepts
   - Domain-specific terminology
   
2. **Relationships**
   - All types of connections between concepts
   - Causal links
   - Associations
   - Dependencies

3. **Actions and Processes**
   - Behaviors
   - Operations
   - Transformations
   - Procedures

4. **Properties and Attributes**
   - Characteristics of entities
   - Qualities
   - States
   - Conditions

5. **Measures and Metrics**
   - Assessment methods
   - Quantification approaches
   - Evaluation criteria

6. **Modifiers**
   - Temporal qualifiers (past, present, future)
   - Modal qualifiers (hypothetical, normative, goal)
   - Conditional modifiers

7. **Truth Values and Operators**
   - Boolean conditions
   - Logical operators
   - Truth states

### Output Structure
```python
Phase1Output:
  citation: str              # Full bibliographic citation
  annotation: str            # 2-3 sentence summary
  theory_type: str           # cognitive, behavioral, social, etc.
  vocabulary: List[VocabularyTerm]
    - term: str             # Exact term from paper
    - definition: str       # Clear, concise definition
    - source_context: str   # Quote showing usage
    - page_reference: str   # Page/section reference
    - theoretical_category: str  # Theory-specific category
```

### Key Features
- **No vocabulary limits** - Extracts all relevant terms
- **Preserves context** - Maintains original usage and meaning
- **Theory-aware** - Captures domain-specific categorizations

## Phase 2: Ontological Classification

### Purpose
Classify extracted vocabulary into semantic categories with maximum specificity for knowledge representation.

### Input
- Complete vocabulary from Phase 1
- Terms grouped by theoretical category

### Classification Categories

1. **Entity** - Things that exist
   - Actors (individuals, groups, organizations)
   - Concepts (abstract ideas)
   - Objects (physical things)
   - Events (occurrences)
   - Statements (propositions)

2. **Relationship** - Connections between entities
   - Must specify domain types (what can be source)
   - Must specify range types (what can be target)
   - Examples: causes, influences, contains

3. **Property** - Attributes of entities
   - Descriptive characteristics
   - States or conditions
   - Qualities

4. **Action** - Behaviors or operations
   - Must specify domain types (who/what can perform)
   - Must specify range types (what is affected)
   - Examples: decides, implements, transforms

5. **Measure** - Metrics and assessments
   - Quantification methods
   - Evaluation approaches
   - Measurement scales

6. **Modifier** - Qualifiers that modify statements
   - Temporal: past, present, future
   - Modal: hypothetical, normative, goal
   - Conditional: if-then qualifiers

7. **Truth-Value** - Truth conditions
   - true, false
   - possible, impossible
   - partial, uncertain

8. **Operator** - Logical/structural operators
   - and, or, not
   - implies, equivalent

### Output Structure
```python
Phase2Output:
  entities: List[ClassifiedTerm]
  relationships: List[ClassifiedTerm]
  properties: List[ClassifiedTerm]
  actions: List[ClassifiedTerm]
  measures: List[ClassifiedTerm]
  modifiers: List[ClassifiedTerm]
  truth_values: List[ClassifiedTerm]
  operators: List[ClassifiedTerm]

ClassifiedTerm:
  term: str                    # The term
  term_type: str               # Primary category
  subtype: str                 # Theory-specific subtype
  domain: List[str]            # For relationships/actions
  range: List[str]             # For relationships/actions
  parent_concept: str          # For hierarchies
  constraints: Dict[str, str]  # Additional constraints
```

### Key Features
- **Specific type inference** - Not generic "Entity" but specific types
- **Domain/range precision** - Actor→Statement not Entity→Entity
- **Hierarchy preservation** - Maintains subtype relationships
- **Theory-specific subtypes** - Preserves original categorizations

## Phase 3: Theory-Adaptive Schema Generation

### Purpose
Generate appropriate knowledge representation schema based on the theory's inherent structure.

### Input
- Classified vocabulary from Phase 2
- Theory type and characteristics

### Model Type Selection

The system analyzes the classified vocabulary to select the optimal representation:

1. **property_graph**
   - When: Rich relationships between diverse entities
   - Features: Nodes, edges, properties
   - Use cases: Social networks, causal models

2. **table_matrix**
   - When: Natural cross-tabulation of categories
   - Features: Rows, columns, cell values
   - Use cases: 2x2 classifications, feature matrices

3. **sequence**
   - When: Order and progression matter
   - Features: Stages, transitions
   - Use cases: Process models, stage theories

4. **tree**
   - When: Hierarchical relationships dominate
   - Features: Root, branches, leaves
   - Use cases: Taxonomies, decision trees

5. **timeline**
   - When: Temporal evolution is central
   - Features: Events, periods
   - Use cases: Historical theories, development models

6. **other**
   - When: Unique structure required
   - Features: Custom representation
   - Use cases: Novel theoretical frameworks

### Schema Components

1. **Node Types** (for graph-based models)
   ```yaml
   - name: str
   - properties: List[str]
   - description: str
   - subtypes: List[str]
   - constraints: Dict
   ```

2. **Edge Types** (for relationships)
   ```yaml
   - name: str
   - from_types: List[str]  # Specific valid sources
   - to_types: List[str]   # Specific valid targets
   - properties: List[str]
   - description: str
   - inverse: str          # Inverse relationship
   ```

3. **Model-Specific Elements**
   - Tables: Row/column definitions
   - Sequences: Stage definitions
   - Trees: Hierarchy rules
   - Timelines: Period definitions

### Output Structure
```yaml
citation: "Full citation"
annotation: "Theory summary"
model_type: "Selected model type"
rationale: "Justification for model selection"
schema_blueprint:
  title: "Schema title"
  description: "Comprehensive description"
  root_properties:
    # Model-specific root properties
  definitions:
    - name: "Term name"
      category: "Semantic category"
      description: "Term definition"
      domain: ["Specific types"]  # For relationships
      range: ["Specific types"]   # For relationships
  modifiers_supported: ["List of modifiers"]
  truth_values_supported: ["List of truth values"]
  operators_supported: ["List of operators"]
```

## Implementation Details

### Technology Stack
- **Language**: Python 3.10+
- **LLM**: OpenAI O3 model
- **Output Format**: YAML
- **Type Safety**: Pydantic models for validation

### File Organization
```
src/schema_creation/
├── multiphase_processor_improved.py  # Main implementation
├── prompts/                         # LLM prompts
├── models/                          # Pydantic models
└── utils/                           # Helper functions

schemas/{theory_name}/
└── {schema_name}.yml               # Generated schemas

results/{theory_name}/
└── validation_reports/             # Quality checks
```

### Quality Assurance

1. **Vocabulary Completeness**
   - No artificial limits on extraction
   - Cross-reference with paper's index/glossary
   - Verify key concepts captured

2. **Classification Accuracy**
   - Domain/range specificity check
   - Hierarchy consistency
   - Semantic correctness

3. **Schema Appropriateness**
   - Model type matches theory structure
   - All vocabulary represented
   - Computationally tractable

## Best Practices

### 1. Paper Preparation
- Use clean text extraction (no headers/footers)
- Maintain paragraph structure
- Include figure/table captions if relevant

### 2. Vocabulary Extraction
- Run extraction on complete paper
- Don't exclude technical terms
- Preserve original terminology

### 3. Classification
- Use most specific types possible
- Maintain theoretical distinctions
- Document ambiguous cases

### 4. Schema Generation
- Let theory drive model selection
- Don't force inappropriate models
- Include all necessary metadata

### 5. Validation
- Compare against paper's own diagrams/models
- Test with paper's example data
- Verify computational completeness

## Common Patterns

### Cognitive Theories
- Often use property graphs
- Rich relationship types
- Multiple truth values
- Temporal modifiers

### Classification Systems
- Natural fit for table/matrix
- Clear row/column categories
- Cell values represent relationships

### Process Theories
- Sequence models work well
- Stages with transitions
- Temporal ordering critical

### Hierarchical Theories
- Tree structures appropriate
- Parent-child relationships
- Inheritance of properties

## Troubleshooting

### Issue: Missing Key Concepts
- **Cause**: Incomplete text extraction
- **Solution**: Verify full paper text included

### Issue: Generic Classifications
- **Cause**: Insufficient context in Phase 2
- **Solution**: Provide more vocabulary context

### Issue: Wrong Model Type
- **Cause**: Misunderstood theory structure
- **Solution**: Review theory characteristics

### Issue: Low Fidelity Results
- **Cause**: Schema doesn't capture theory nuance
- **Solution**: Iterate on vocabulary/classification

## Future Enhancements

1. **Multi-Paper Integration**
   - Combine vocabularies across papers
   - Identify theoretical evolution
   - Build comprehensive ontologies

2. **Automated Validation**
   - Compare against ground truth
   - Measure extraction completeness
   - Verify classification accuracy

3. **Domain Adaptations**
   - Psychology-specific extractors
   - Economics-specific classifiers
   - Policy-specific schemas

4. **Hybrid Models**
   - Support multiple representations
   - Cross-model mappings
   - Integrated schemas

## References

- Young, M. D. (1996). Cognitive Mapping Meets Semantic Networks. Journal of Conflict Resolution, 40(3), 395-414.
- PROJECT_OVERVIEW.md - Complete project documentation
- multiphase_processor_improved.py - Reference implementation