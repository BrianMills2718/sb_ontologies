# Universal Meta-Schema for Theory Extraction

## Overview
This document defines the simplified universal meta-schema used for extracting theoretical constructs from academic papers. This schema replaces the previous 8-category ontology with a more flexible 4-component structure.

## Core Components

### 1. **Nodes/Units**
The fundamental elements of the theory. These are the basic building blocks that the theory operates with.

**Examples:**
- Cognitive Mapping: Concepts (political entities, policies) - nodes are things like "United States", connections include action types like "cooperate"
- Semantic Hypergraph: Atoms with type codes (e.g., "berlin/C", "is/P", "very/M")
- Social Networks: Actors, groups, institutions
- Game Theory: Players, strategies, outcomes

**Key Principle:** Don't over-categorize. Let the theory define what constitutes a unit.

### 2. **Connections**
How the nodes/units relate to each other. The structure can vary by theory type.

**Examples:**
- Cognitive Mapping: Directed edges with relationship types (+, -, attribute, strategy)
- Semantic Hypergraph: Ordered hyperedges connecting multiple atoms
- Social Networks: Ties, interactions, flows
- Taxonomies: Parent-child, is-a relationships

**Key Properties:**
- Direction (directed/undirected)
- Arity (binary/n-ary)
- Type labels
- Ordering (when position matters)

### 3. **Properties**
Attributes, measures, and metadata associated with nodes and connections.

**Examples:**
- Salience scores, centrality measures
- Type codes, role annotations
- Timestamps, frequencies
- Quantitative values, probabilities

**Key Principle:** Properties enrich the basic structure without changing the fundamental model.

### 4. **Modifiers**
Qualifiers that condition or contextualize the relationships.

**Examples:**
- Truth values: true, false, possible, partial
- Temporal: past, present, future
- Modal: hypothetical, normative, goal
- Certainty: definite, probable, possible

**Key Principle:** Modifiers don't create new structures, they annotate existing ones.

## Model Types

Each theory declares its fundamental structure type:

### **graph**
- Binary relationships between nodes
- Directed or undirected
- Example: Traditional cognitive maps

### **hypergraph**
- N-ary relationships (edges connect multiple nodes)
- Ordered or unordered
- Example: Semantic Hypergraphs

### **table**
- Rows and columns with defined schema
- Cross-tabulations, matrices
- Example: 2x2 game theory payoffs

### **sequence**
- Ordered progression of elements
- Temporal or logical ordering
- Example: Stage theories, processes

### **tree**
- Hierarchical parent-child relationships
- Single inheritance paths
- Example: Taxonomies, decision trees

### **network**
- Complex graph with multiple edge types
- Often includes node attributes
- Example: Multi-modal social networks

## Schema Structure

```yaml
# Required fields
model_type: [graph|hypergraph|table|sequence|tree|network]
theory_name: "Name of the theoretical framework"

# Core components
nodes:
  - id: "unique_identifier"
    label: "human_readable_label"
    type: "theory_specific_type"  # optional
    properties: {}  # any additional attributes

connections:
  # Format depends on model_type
  # Graph/Network:
  - source: "node_id"
    target: "node_id" 
    type: "relationship_type"
    properties: {}
    modifiers: []
  
  # Hypergraph:
  - id: "edge_id"
    nodes: ["node1", "node2", "node3"]  # n-ary
    type: "hyperedge_type"
    ordered: true/false
    
  # Table:
  - row: "row_label"
    column: "column_label"
    value: "cell_value"

properties:
  # Theory-specific metadata
  type_system: {}  # if theory has type codes
  inference_rules: []  # if theory has rules
  measures: {}  # quantitative assessments
  constraints: []  # structural constraints

modifiers:
  # Available modifiers in this theory
  truth_values: []
  temporal: []
  modal: []
  certainty: []
```

## Key Principles

1. **Theory-First**: Let each theory define its own categories rather than forcing predefined ones
2. **Simplicity**: Use the simplest structure that captures the theory's essence
3. **Completeness**: Capture all theoretical elements, even if they don't fit perfectly
4. **Properties Over Categories**: Use properties and descriptions rather than complex type hierarchies
5. **Faithful Representation**: Preserve the theory's own terminology and structure

## Migration from 8-Category System

The previous 8 categories map as follows:
- Entity → Node/Unit
- Relationship → Connection
- Property → Property (unchanged)
- Action → Node/Unit (just another type of concept)
- Measure → Property
- Modifier → Modifier (unchanged)
- Truth-Value → Modifier
- Operator → Either Node/Unit or Connection (depending on theory)

## Examples

### Cognitive Mapping (Young 1996)
```yaml
model_type: graph
nodes: # All concepts are just nodes
  - {id: "US", label: "United States"}
  - {id: "cooperate", label: "cooperate"}
connections:
  - {source: "US", target: "cooperate", type: "+", modifiers: ["true", "present"]}
```

### Semantic Hypergraph
```yaml
model_type: hypergraph  
nodes: # Atoms with type codes
  - {id: "berlin", type: "C", label: "berlin"}
  - {id: "is", type: "P", label: "is"}
connections: # Ordered hyperedges
  - {id: "h1", nodes: ["is", "berlin", "nice"], ordered: true, type: "R"}
```