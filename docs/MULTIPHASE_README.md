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

### Phase 3: Theory-Adaptive Schema Generation
**Goal**: Design appropriate knowledge representation structure

**Output**:
- Model type selection with rationale (property_graph, table_matrix, sequence, tree, timeline, hybrid, statistical, logical)
- Component-specific definitions
- Inter-component mappings (for hybrid models)
- Reasoning requirements and constraints

**Example** (Simple):
```yaml
model_type: "property_graph"
node_types:
  - name: "Actor"
    properties: ["name", "authority_level", "resources"]
edge_types:
  - name: "INFLUENCES"
    from_types: ["Actor", "Strategy"]
    to_types: ["Audience", "Outcome"]
```

**Example** (Hybrid):
```yaml
model_type: "hybrid"
hybrid_components:
  - component_id: "belief_network"
    component_type: "property_graph"
  - component_id: "payoff_matrix"
    component_type: "table_matrix"
inter_component_mappings:
  - from_component: "belief_network"
    from_element: "Agent"
    to_component: "payoff_matrix"
    to_element: "player"
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

## Handling Complex Theories

### Phase 1 Extensions for Complex Theories

When processing theories that span multiple paradigms, Phase 1 extracts:

1. **Multi-Paradigm Vocabulary**:
   - Game-theoretic terms (payoffs, equilibria, strategies)
   - Statistical terms (distributions, parameters, correlations)
   - Logical terms (axioms, inference rules, modal operators)
   - Network terms (nodes, edges, centrality)
   - Process terms (stages, transitions, sequences)

2. **Cross-Paradigm Indicators**:
   - Terms suggesting hybrid needs: "both...and", "integrates", "multi-level"
   - Mathematical formulas and their semantic meaning
   - Temporal qualifiers and modal operators
   - N-ary relationship indicators (tables, matrices, tuples)

**Example Phase 1 Output for Complex Theory**:
```json
{
  "vocabulary": [
    {
      "term": "belief_update",
      "definition": "Bayesian updating of agent beliefs based on evidence",
      "paradigm_hints": ["statistical", "cognitive"],
      "formula": "P(H|E) = P(E|H)P(H)/P(E)"
    },
    {
      "term": "institutional_payoff",
      "definition": "Game payoff dependent on institutional configuration",
      "paradigm_hints": ["game_theory", "institutional"],
      "arity_hint": 5  // player, action, others, institution, payoff
    }
  ]
}
```

### Phase 2 Extensions for Complex Theories

Phase 2 performs paradigm-aware classification:

1. **Statistical Elements**:
   - Distributions (with family and parameters)
   - Stochastic processes
   - Latent variables
   - Correlation structures

2. **Logical Elements**:
   - Propositions vs predicates
   - Modal operators (necessary, possible)
   - Inference rules
   - Consistency constraints

3. **N-ary Relations**:
   - Identify arity > 2
   - Role specifications
   - Constraint types

**Example Phase 2 Output for Complex Theory**:
```json
{
  "entities": [
    {
      "term": "Agent",
      "properties": {
        "belief_state": {
          "type": "probabilistic",
          "structure": "vector[Belief]"
        }
      }
    }
  ],
  "statistical_elements": [
    {
      "term": "competence",
      "variable_type": "latent",
      "distribution": "Beta(α, β)",
      "estimation_method": "hierarchical_bayes"
    }
  ],
  "n_ary_relations": [
    {
      "term": "institutional_game",
      "arity": 5,
      "roles": ["player", "action", "others_profile", "institution", "payoff"]
    }
  ],
  "logical_axioms": [
    {
      "term": "norm_consistency",
      "type": "constraint",
      "formula": "¬(Obligatory(A) ∧ Forbidden(A))"
    }
  ]
}
```

### Phase 3 Extensions for Complex Theories

Phase 3 determines optimal representation:

1. **Hybrid Model Detection**:
   - Multiple paradigm indicators from Phase 2
   - Incompatible representation needs
   - Cross-cutting concerns

2. **Component Design**:
   - Assign vocabulary to appropriate components
   - Design inter-component mappings
   - Specify transformation functions

3. **Advanced Features**:
   - OWL characteristics (transitive, symmetric, functional)
   - Reasoning requirements (engines needed)
   - Statistical parameters and update rules
   - Validation constraints and formulas

**Example Phase 3 Output for Complex Theory**:
```json
{
  "model_type": "hybrid",
  "rationale": "Theory requires game-theoretic payoffs (table), belief dynamics (graph), and normative reasoning (logic)",
  "hybrid_components": [
    {
      "component_id": "belief_network",
      "component_type": "property_graph",
      "vocabulary_assignment": ["Agent", "Belief", "influences", "updates_belief"]
    },
    {
      "component_id": "payoff_structure",
      "component_type": "table_matrix",
      "vocabulary_assignment": ["institutional_game", "Action", "Payoff"],
      "representation": "5-ary relation"
    }
  ],
  "inter_component_mappings": [
    {
      "mapping_type": "entity_correspondence",
      "source": "belief_network.Agent",
      "target": "payoff_structure.player"
    }
  ],
  "reasoning_requirements": [
    {
      "type": "bayesian_inference",
      "component": "belief_network",
      "implementation": "hierarchical_bayes"
    }
  ]
}
```

## Advanced Processing Features

### Handling Statistical Models

When Phase 1 detects statistical vocabulary:
- Extract distribution families and parameters
- Identify latent vs observed variables
- Capture update rules and estimation methods

Phase 2 classifies into:
- Random variables with distributions
- Structural equation specifications
- Covariance matrices
- Hierarchical model levels

Phase 3 creates:
- Statistical model component with proper metadata
- Links to other components via shared entities
- Inference algorithm specifications

### Handling Logical Models

When Phase 1 detects formal logic:
- Extract operators (∀, ∃, □, ◇, O, P, F)
- Identify axioms and theorems
- Capture inference rules

Phase 2 classifies into:
- Propositions vs predicates
- Modal vs deontic operators
- Defeasible vs strict rules

Phase 3 creates:
- Logical system specification
- Consistency checking requirements
- Proof obligation declarations

### Handling N-ary Relations (Tables)

When Phase 1 detects tabular structures:
- Identify all participating entities
- Extract role names
- Capture constraints

Phase 2 determines:
- Exact arity
- Role types and constraints
- Completeness requirements

Phase 3 creates:
- N-ary relation specification
- Role bindings
- Query transformation rules

## Quality Assurance

### Validation Checks

1. **Phase 1 Completeness**:
   - No paradigm indicators missed
   - All formulas captured with semantics
   - Cross-references preserved

2. **Phase 2 Consistency**:
   - No entity has domain/range
   - All relationships have proper domain/range
   - Statistical/logical elements properly typed

3. **Phase 3 Coherence**:
   - All vocabulary assigned to components
   - Inter-component mappings are complete
   - Reasoning requirements match theory needs

### Common Pitfalls and Solutions

1. **Missing Hybrid Indicators**:
   - Solution: Look for integration language, multiple methodologies

2. **Oversimplifying to Property Graph**:
   - Solution: Check if tables/sequences/trees better fit parts

3. **Losing Statistical/Logical Precision**:
   - Solution: Preserve formulas and formal specifications

4. **Incomplete Inter-component Mappings**:
   - Solution: Trace each entity across all components

## Debugging

Check the `debug/` folder for intermediate outputs:
- `*_phase1.json`: Raw vocabulary extraction
- `*_phase2.json`: Classification results
- `*_phase3.json`: Schema design

For complex theories, also check:
- `*_paradigm_analysis.json`: Multi-paradigm detection
- `*_component_assignment.json`: Vocabulary-to-component mapping
- `*_validation_report.json`: Constraint checking results

This helps identify which phase might need adjustment for specific papers.