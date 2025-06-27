# N-ary Relations Handling Guide

## Overview
This guide clarifies how our schema extraction system handles n-ary relations (relationships involving more than 2 entities) across different model types.

## What are N-ary Relations?

N-ary relations involve multiple participants in a single relationship:
- **Binary (2-ary)**: "John likes Mary"
- **Ternary (3-ary)**: "John gave Mary a book"
- **N-ary (n participants)**: "The committee (5 people) voted on proposal X with outcome Y"

## How Each Model Type Handles N-ary Relations

### 1. Property Graph
**Approach**: Reification - convert n-ary relation into a node
```yaml
# Original n-ary: analyze(researcher, data, method, tool)
nodes:
  - {id: R1, type: Researcher, name: "Dr. Smith"}
  - {id: D1, type: Data, name: "Survey Data"}
  - {id: M1, type: Method, name: "Regression"}
  - {id: T1, type: Tool, name: "SPSS"}
  - {id: A1, type: AnalysisEvent}  # Reified relation

edges:
  - {from: A1, to: R1, type: has_researcher}
  - {from: A1, to: D1, type: has_data}
  - {from: A1, to: M1, type: uses_method}
  - {from: A1, to: T1, type: uses_tool}
```

### 2. Table/Matrix
**Approach**: Native n-ary through columns
```yaml
# Game theory example: game(player1, player2, strategy1, strategy2, outcome)
table_structure:
  columns: [player1, player2, strategy1, strategy2, outcome]
  rows:
    - ["Alice", "Bob", "Cooperate", "Defect", "3,5"]
    - ["Alice", "Bob", "Defect", "Cooperate", "5,3"]
```

### 3. Hypergraph
**Approach**: Direct representation as hyperedges
```yaml
# Semantic Hypergraph example
hyperedges:
  - id: HE1
    type: "believes"
    connects: ["John", "Proposition1"]  # Binary
  
  - id: HE2
    type: "transfer"
    connects: ["John", "Mary", "Funds", "BankA", "BankB"]  # 5-ary
    ordered: true
    roles: ["agent", "recipient", "object", "source", "destination"]
```

### 4. Sequence
**Approach**: N-ary through stage properties
```yaml
stages:
  - id: S1
    participants: ["Actor1", "Actor2", "Actor3"]  # Multiple participants
    action: "Negotiate"
    outcome: "Agreement"
```

## Decision Criteria

### When to Use Which Model?

1. **Use Hypergraph when:**
   - N-ary relations are the primary focus
   - Relations frequently involve 3+ participants
   - Order of participants matters semantically
   - Relations can be recursive/nested
   - Theory explicitly uses hypergraph concepts (e.g., Semantic Hypergraphs)

2. **Use Property Graph when:**
   - Most relations are binary
   - N-ary relations are occasional
   - You need rich properties on both nodes and edges
   - Path queries are important
   - N-ary relations can be effectively reified

3. **Use Table/Matrix when:**
   - Fixed arity (all relations have same number of participants)
   - Natural rows/columns structure
   - Statistical analysis needed
   - Cross-tabulation is central to the theory

## Examples from Academic Theories

### Example 1: Institutional Analysis (Ostrom)
- **Pattern**: "Actor uses Resource under Rule in Context"
- **N-ary**: 4 participants
- **Best Model**: Property graph with reified "ResourceUse" events

### Example 2: Semantic Hypergraphs (Menezes & Roth)
- **Pattern**: Hyperedge(connector, arg1, arg2, ..., argN)
- **N-ary**: Unlimited participants
- **Best Model**: Hypergraph (designed for this)

### Example 3: Multi-party Negotiations
- **Pattern**: "Parties A,B,C negotiate over Issues X,Y,Z"
- **N-ary**: 6+ participants
- **Best Model**: Hypergraph or reified property graph

## Implementation in Schema

### Property Graph N-ary Pattern
```yaml
definitions:
  - name: "AnalysisEvent"
    category: "entity"
    description: "Reified analysis relationship"
    properties: ["timestamp", "method", "confidence"]
  
  - name: "performs"
    category: "relationship"
    domain: ["Researcher"]
    range: ["AnalysisEvent"]
  
  - name: "analyzes"
    category: "relationship"  
    domain: ["AnalysisEvent"]
    range: ["Data"]
```

### Hypergraph N-ary Pattern
```yaml
definitions:
  - name: "transfer"
    category: "hyperedge_type"
    arity: 5
    roles: 
      - {position: 0, name: "agent", types: ["Actor"]}
      - {position: 1, name: "recipient", types: ["Actor"]}
      - {position: 2, name: "object", types: ["Resource"]}
      - {position: 3, name: "source", types: ["Location"]}
      - {position: 4, name: "destination", types: ["Location"]}
```

## Validation Checklist

When reviewing a theory for n-ary relations:

1. **Identify all relationships** in the theory
2. **Count participants** in each relationship type
3. **Check for patterns**:
   - Mostly binary → Property graph
   - Many n-ary with varying participants → Hypergraph
   - Fixed n-ary structure → Table/matrix
4. **Consider queries needed**:
   - Path finding → Property graph
   - Set operations → Hypergraph
   - Statistical → Table/matrix

## Common Mistakes to Avoid

1. **Don't force binary decomposition** when it loses meaning
   - Bad: "John gives Mary" + "gives involves book"
   - Good: Give(John, Mary, book)

2. **Don't ignore participant roles**
   - Bad: Transfer(A, B, C, D, E)
   - Good: Transfer(agent:A, recipient:B, object:C, from:D, to:E)

3. **Don't mix patterns unnecessarily**
   - Keep consistent representation within a theory
   - Use hybrid only when theory truly requires it

## Conclusion

N-ary relations are first-class citizens in our schema system. The key is selecting the right model type based on:
- Frequency of n-ary relations
- Whether arity is fixed or variable
- Importance of participant roles
- Query patterns needed

When in doubt, explain the n-ary patterns found in the theory and let Phase 3 select the optimal representation.