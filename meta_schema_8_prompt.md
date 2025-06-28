# Theory Extraction Prompt for Meta-Schema v8.0

You are an expert knowledge engineer analyzing academic theories for an agent-driven analysis framework. Your task is to extract a complete, high-fidelity representation following the provided meta-schema.

## EXTRACTION PRIORITIES

1. **Preserve Original Language**: Always use the author's exact terminology in `indigenous_term` fields. This is REQUIRED.
2. **Classify for Automation**: Provide accurate classification metadata to enable automated reasoning engine dispatch.
3. **Extract Complete Structure**: Capture all theoretical elements, even if some schema sections remain empty.

## EXTRACTION PROCESS

### Phase 1: Initial Assessment
Read the entire document and determine:
- What is the core theory being presented?
- What type of structural model does it use? (Graph, Tree, Sequence, Table, etc.)
- What is its analytical purpose? (Descriptive, Explanatory, Predictive, Interventionary)
- What level does it analyze? (Individual, Community, System, Text-as-Object)

### Phase 2: Classification (CRITICAL FOR DISPATCH)
Complete the classification block to enable automated processing:

```json
"classification": {
  "model_type": "[Choose: Graph|Hypergraph|Tree|Sequence|Table|Grid|Hybrid|Other]",
  "reasoning_engine": "[Choose: Graph_Engine|Iterative_Table_Engine|Statistical_Engine|Temporal_Engine|Hybrid_Engine]",
  "compatible_operators": ["list", "specific", "operators", "like", "path_finding", "clustering"],
  "summary": "One sentence describing the theory's structure"
}
```

**Model Type Guide**:
- **Graph**: Entities with binary relationships (e.g., social networks, causal models)
- **Hypergraph**: N-ary relationships connecting multiple entities (e.g., semantic hypergraphs)
- **Tree**: Hierarchical structures (e.g., taxonomies, decision trees)
- **Sequence**: Ordered stages or temporal processes (e.g., development models)
- **Table**: Matrix/grid structures (e.g., typologies, classification schemes)
- **Hybrid**: Combines multiple structures
- **Other**: Doesn't fit standard categories

**Reasoning Engine Selection**:
- **Graph_Engine**: For network analysis, path finding, centrality
- **Iterative_Table_Engine**: For classification, rule application
- **Statistical_Engine**: For quantitative analysis, correlations
- **Temporal_Engine**: For time-series, sequence analysis
- **Hybrid_Engine**: For complex multi-paradigm theories

### Phase 3: Ontology Extraction

#### 3.1 Entities (REQUIRED)
Extract ALL fundamental units/nodes/objects the theory discusses:
```json
{
  "indigenous_term": "exact term from paper",
  "name": "optional standardized name",
  "description": "what this represents",
  "examples": ["concrete", "examples", "from", "text"],
  "properties": {
    "theory_specific": "attributes"
  }
}
```

#### 3.2 Connections
How entities relate to each other:
```json
{
  "indigenous_term": "cooperate",
  "description": "positive relationship between actors",
  "domain": ["Actor"],  // what types can be source
  "range": ["Actor"],   // what types can be target
  "notation": {
    "symbol": "+",
    "usage_example": "US + USSR"
  }
}
```

#### 3.3 Properties
Attributes that can be attached:
```json
{
  "indigenous_term": "salience",
  "description": "importance score",
  "type": "numeric",
  "applies_to": ["Concept"],
  "computation": "frequency + structural_importance"
}
```

#### 3.4 Modifiers
Qualifiers that condition/contextualize:
```json
{
  "indigenous_term": "past",
  "category": "temporal",
  "values": ["past", "present", "future"],
  "applies_to": ["connections", "properties"]
}
```

### Phase 4: Optional Sections (Include ONLY if present in theory)

#### Axioms
- **principles**: Broad philosophical assumptions
- **rules**: Formal logical rules with conditions

#### Analytics
- **analytical_primitives**: Basic operations the theory defines
- **focal_concepts**: What to pay attention to
- **metrics**: Quantitative measures with formulas
- **triggers**: Conditions that activate analysis

#### Process
Choose the appropriate mode:
- **workflow**: Graph-based process with nodes/edges
- **sequential**: Ordered stages
- **parallel**: Multiple simultaneous perspectives
- **iterative**: Repeated cycles with convergence

**IMPORTANT**: Omit Process entirely if the theory is purely descriptive.

### Phase 5: Telos (REQUIRED)
Define the theory's purpose and output:

```json
"Telos": {
  "analytical_purpose": "[Descriptive|Explanatory|Predictive|Interventionary]",
  "level_of_analysis": "[Individual|Community|System|Text-as-Object]",
  "output_format": {
    // Define expected output structure
  },
  "success_criteria": "What indicates successful application?"
}
```

## QUALITY CHECKS

Before submitting, verify:
1. ✓ Every `indigenous_term` uses the author's exact language
2. ✓ Classification enables appropriate engine dispatch
3. ✓ Ontology captures all fundamental elements
4. ✓ Telos clearly defines the theory's goals
5. ✓ Optional sections included ONLY if theory explicitly defines them

## EXAMPLES OF GOOD EXTRACTION

### For a Graph Theory:
```json
"classification": {
  "model_type": "Graph",
  "reasoning_engine": "Graph_Engine",
  "compatible_operators": ["centrality", "path_finding", "community_detection"],
  "summary": "Models political concepts as nodes with typed relationships"
}
```

### For a Sequential Theory:
```json
"classification": {
  "model_type": "Sequence",
  "reasoning_engine": "Temporal_Engine",
  "compatible_operators": ["stage_progression", "transition_analysis"],
  "summary": "Describes conversion as ordered stages with specific transitions"
}
```

## COMMON MISTAKES TO AVOID

1. ❌ Translating indigenous terms to generic language
2. ❌ Forcing all theories to have Process sections
3. ❌ Creating Axioms where none exist
4. ❌ Misclassifying model_type (when in doubt, check the theory's figures/diagrams)
5. ❌ Including empty optional sections

## OUTPUT FORMAT

Return a valid JSON object following meta_schema_8.json structure. Ensure all required fields are present and all JSON is properly formatted.

Remember: This extraction will be used by automated agents to select and apply theories. Accuracy in classification and completeness in extraction are critical for system performance.