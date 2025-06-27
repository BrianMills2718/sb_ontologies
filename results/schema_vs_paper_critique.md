# Critique: Simplified Schemas vs Original Papers

## Semantic Hypergraph Schema Critique

### What the Schema Got Right ✅

1. **All 8 Type Codes**: Correctly captured C, P, M, B, T, J, R, S with accurate descriptions
2. **Type Inference Rules**: All 5 rules from Table 2 with correct patterns:
   - (M x) → x
   - (B C C+) → C  
   - (T [CR]) → S
   - (P [CRS]+) → R
   - (J x y'+) → x
3. **Special Symbols**: Captured +/B and :/J correctly
4. **Model Type**: Correctly identified as hypergraph
5. **Recursive Nature**: Properly described ordered, recursive hyperedges

### What the Schema Missed or Got Wrong ❌

1. **Incomplete Argument Roles** (Table 3):
   - Schema mentions roles in properties but doesn't list all 10
   - Missing complete list: s, p, a, c, o, i, t, j, x, r
   - Only gave examples: "s = active subject, p = passive subject..."

2. **Missing Pattern Library**:
   - Paper has extensive patterns (Section 5.2)
   - Schema only mentions general pattern structure
   - Missing specific patterns like:
     - Simple transitive: ($v:P sa $sub:C) + ($v pa $obj:C)
     - Copular: ($copP:P cop $attr:C) + ($copP sa $ent:C)
     - Conjunction expansion patterns

3. **Missing α-Stage and β-Stage Details**:
   - Paper describes two-stage parsing architecture
   - α-stage: Random Forest classifier with 15 features
   - β-stage: Pattern matching with wildcard inference
   - Schema doesn't capture this parsing methodology

4. **Incomplete Examples**:
   - Schema shows notation but not complete parsing examples
   - Paper shows full traces like:
     ```
     Input: "Telmo likes bananas and apples"
     α-stage: telmo/C likes/P bananas/C and/J apples/C
     β-stage: (and/J (likes/P telmo/C bananas/C) (likes/P telmo/C apples/C))
     ```

5. **Missing Evaluation Results**:
   - Paper reports 94% accuracy on diverse text
   - Specific performance on Reddit (96%), Blog (93.6%), News (94.1%)
   - OIE benchmark comparisons not captured

### Severity: Medium
The core type system is captured well, but implementation details needed for replication are missing.

## Young 1996 Schema Critique  

### What the Schema Got Right ✅

1. **Model Type**: Correctly identified as network (semantic network)
2. **Node Classes**: Properly abstracted to concept/relationship/conjunction
3. **Relationship Types**: Comprehensive list including +, -, attribute, strategy, etc.
4. **Action Verbs**: All 44 actions captured
5. **Modifiers**: Complete truth values and temporal/modal modifiers
6. **Structural Measures**: All calculations (dependency, connectedness, etc.)
7. **Key Innovation**: Correctly captured relationship-as-node elevation

### What the Schema Missed or Got Wrong ❌

1. **Too Abstract**:
   - Schema describes the framework but not the actual cognitive map
   - Young's paper analyzes Carter's speech with 48 specific concepts
   - Schema has node classes but not the actual nodes

2. **Missing Specific Concepts** (from Carter analysis):
   - United States, Soviet Union, Congress
   - Nuclear weapons, Arms control (SALT)
   - Peace, tension, cooperation
   - All 48 concepts from Table in paper

3. **Missing Actual Relationships**:
   - Paper shows specific relationships like:
     - "United States" --[positive-cause]--> "cooperation"
     - "nuclear weapons" --[negative-cause]--> "peace"
   - Schema only lists relationship types, not instances

4. **No Salience Values**:
   - Paper calculates specific salience scores for concepts
   - Schema mentions salience as a property but no values

5. **Missing Structural Analysis Results**:
   - Paper reports connectedness = 0.24 for Carter map
   - Specific bridge counts, dependency values not in schema
   - Comparison between Carter/Brezhnev maps not captured

### Severity: High
The schema captures Young's methodology perfectly but completely misses the actual cognitive map analysis that demonstrates the methodology.

## Key Insight

Both schemas suffer from the same issue: **they extract the theoretical framework but not the application of that framework**.

- **Semantic Hypergraph**: Got the type system but not the parsing examples
- **Young 1996**: Got the methodology but not Carter's actual cognitive map

This suggests we need a **two-phase extraction**:
1. **Phase 1**: Extract the theoretical framework (what we did)
2. **Phase 2**: Extract the application/instantiation of that framework

## Recommendations

1. **Add Example Extraction**: Create a separate extractor for pulling out complete worked examples
2. **Instance Extraction**: For Young, extract the actual 48 concepts and relationships
3. **Results Extraction**: Capture quantitative results and evaluation metrics
4. **Pattern Library**: For SH, extract the complete pattern library with examples
5. **Full Parse Traces**: Show input → α-stage → β-stage transformations

The simplified meta-schema works well for capturing theoretical structure, but we need additional extraction to capture how theories are actually applied to data.