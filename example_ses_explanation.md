# Social-Ecological Systems Schema Example Explained

## Why Hybrid Model?

Social-Ecological Systems (SES) theory cannot be adequately represented by a single model type because it encompasses:

1. **Complex relationships** between actors, resources, and governance (→ property graph)
2. **Structured access rights** that are naturally tabular (→ matrix)
3. **Hierarchical governance** structures (→ tree)
4. **Dynamic feedback loops** with time delays (→ requires temporal reasoning)
5. **Game-theoretic** collective action problems (→ requires statistical/mathematical reasoning)

## How the Schema Works

### Component 1: Property Graph
The core relationships capture the dynamic interactions:

```
Actor --[harvests]--> ResourceUnit
  ↓                        ↓
[monitors]              [part_of]
  ↓                        ↓
ResourceSystem <--[affects]--> GovernanceSystem
                               ↑
                          [governs]
                               |
                             Actor
```

Key features:
- **Bidirectional effects** with time lags
- **Sustainability constraints** (e.g., extraction_rate <= productivity)
- **OWL characteristics** for proper reasoning (symmetric, functional, transitive)

### Component 2: Access Rights Matrix
Represented as a 4-ary relation:

| Actor Group | Resource Type | Access Right | Season |
|------------|---------------|--------------|---------|
| Fishers    | Coastal Fish  | Harvest      | Summer  |
| Fishers    | Coastal Fish  | Exclude      | Summer  |
| Tourists   | Coastal Fish  | Access       | All     |
| Government | Coastal Fish  | Manage       | All     |

This captures:
- Who can do what with which resources when
- Multiple overlapping rights
- Seasonal/temporal constraints

### Component 3: Governance Hierarchy
```
International Treaty
    ↓
National Legislation
    ↓
Regional Management Plan
    ↓
Local User Association
    ↓
Individual Rules
```

With transitive nesting relationships allowing multi-level analysis.

## Inter-Component Mappings

The same "Actor" entity appears in:
- Property graph (as node with relationships)
- Access matrix (as actor_group in rows)
- Governance hierarchy (as governed entity)

These are linked via `inter_component_mappings`, ensuring consistency.

## Advanced Features

### 1. Reasoning Requirements
The schema explicitly declares needed reasoning:
- **Constraint satisfaction**: Check if extraction rates are sustainable
- **Game theoretic**: Analyze cooperation vs defection
- **Dynamic systems**: Model feedback loops
- **Institutional analysis**: Evaluate rule effectiveness

### 2. Statistical Parameters
Includes stochastic elements:
```yaml
cooperation_probability:
  distribution: "beta"
  parameters: ["group_size", "social_capital", "sanctioning_strength"]
```

### 3. Temporal Modifiers
System states can be:
- "equilibrium" - stable
- "transitioning" - changing
- "collapsed" - degraded

### 4. Validation Rules
Embedded constraints like:
```yaml
sustainability_condition: "extraction_rate <= ResourceSystem.productivity"
level_ordering: "domain.governance_level < range.governance_level"
```

## Query Examples

This hybrid schema enables diverse queries:

1. **Graph query** (Cypher-like):
   ```
   MATCH (a:Actor)-[h:harvests]->(r:ResourceUnit)
   WHERE h.extraction_rate > r.ResourceSystem.productivity
   RETURN a as Unsustainable_Actors
   ```

2. **Matrix query** (SQL-like):
   ```sql
   SELECT actor_group, COUNT(DISTINCT resource_type) as resource_diversity
   FROM resource_access
   WHERE access_right IN ('harvest', 'manage')
   GROUP BY actor_group
   ```

3. **Hierarchical query**:
   ```
   Find all governance systems that nest within "National Legislation"
   AND have property_rights_system = "common"
   ```

4. **Cross-component query**:
   ```
   Find actors with high social_capital
   WHO have harvest rights to mobile resources
   AND are governed by local institutions
   ```

## Benefits of This Approach

1. **Theoretical Fidelity**: Captures all aspects of SES theory
2. **Computational Flexibility**: Different analyses on different components  
3. **Reasoning Support**: Explicit requirements for inference engines
4. **Validation**: Built-in sustainability constraints
5. **Interoperability**: Can export to Neo4j (graph), SQL (matrix), or OWL (hierarchy)

This demonstrates how our unified entity/relation approach can represent complex theories requiring multiple paradigms while maintaining semantic consistency and computational tractability.