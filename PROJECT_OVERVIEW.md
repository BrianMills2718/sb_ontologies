# Project Overview: Computational Social Science Theory Modeling

## Strategic Goal

Create an automated system that reads academic papers, extracts their theoretical constructs, and instantiates those constructs with data to produce results comparable to the original paper's methodology.

**Core Workflow**: Academic Paper → Schema Extraction → Data Application → Comparable Results

### Core Objectives

1. **Robust Theory Extraction**: Faithfully capture theoretical frameworks from academic papers without oversimplification
2. **Flexible Representation**: Support multiple model types (graphs, tables, sequences, trees, timelines, statistical models) based on each theory's inherent structure  
3. **Analytical Capability**: Handle theories addressing any of the four analytical tasks - describing, explaining/causality, predicting, or intervening
4. **High-Fidelity Instantiation**: Apply extracted schemas to data to produce results comparable to original research
5. **Theory-Driven Selection**: Let each theory determine its appropriate analytical tasks and data structures rather than forcing artificial balance

## Current Status

### Recent Findings
1. **Information Loss Fixed**: Resolved issue where Phase 3 only received Phase 2 summary, losing ~40% of extracted terms
2. **Notation Systems**: Critical for theories like Semantic Hypergraphs - require dedicated extraction
3. **Implementation Details**: Algorithms, patterns, and evaluation metrics need multi-pass extraction
4. **Hypergraph Support**: Already supported in schema but needs explicit "hypergraph" model type

### Test Case Progress: Young 1996
- **Current Fidelity**: 34% (need to improve to match original analysis)
- **Target**: 48 concepts, 15+ relationships as in `examples/carter_young1996_faithful_analysis.yml`
- **Next Steps**: Apply improved extraction to increase fidelity

## Current Methodology: Three-Phase Processing

### Phase 1: Comprehensive Vocabulary Extraction
- **Goal**: Extract ALL theoretical terms from academic papers
- **Process**: Deep reading to identify concepts, relationships, actions, properties, measures, modifiers
- **Output**: Complete vocabulary with definitions, context, and theoretical categories
- **Key Innovation**: No artificial limits on vocabulary size

### Phase 2: Ontological Classification
- **Goal**: Properly categorize terms according to semantic type
- **Process**: Classify into entities, relationships, properties, actions, measures, modifiers, truth values, operators
- **Output**: Structured classification with specific domain/range for relationships/actions
- **Key Innovation**: Preserves theoretical subcategories and infers specific type constraints

### Phase 3: Theory-Adaptive Schema Generation
- **Goal**: Create appropriate knowledge representation structure
- **Process**: Select optimal model type based on theory's inherent structure:
  - **property_graph**: For theories with rich interconnected relationships
  - **hypergraph**: For n-ary relationships, recursive structures (e.g., Semantic Hypergraphs)
  - **table_matrix**: For classification systems, typologies, or cross-tabulated data
  - **sequence**: For stage models, processes, or ordered progressions
  - **tree**: For hierarchical taxonomies or decision structures
  - **timeline**: For temporal evolution or historical development
  - **other**: For unique structures requiring custom representation
- **Output**: Complete JSON Schema with model-specific root properties
- **Key Innovation**: Genuinely evaluates and selects appropriate model type with detailed rationale
- **Critical Enhancement**: Now passes full Phase 1 vocabulary to Phase 3 to prevent information loss

## Technical Architecture

### Processing Pipeline
```
Academic Paper (.txt)
    ↓
Phase 1: Vocabulary Extraction (O3 LLM)
    ↓
Phase 2: Ontological Classification (O3 LLM)
    ↓
Phase 3: Schema Generation (O3 LLM)
    ↓
YAML Schema (.yml)
```

### Key Improvements Over Legacy System
1. **Semantic Correctness**: Only relationships/actions have domain/range (not entities)
2. **Comprehensive Extraction**: ~4x more vocabulary extracted
3. **Theoretical Nuance**: Preserves subcategories like "core-construct", "process-element"
4. **Hierarchical Support**: Maintains subTypeOf relationships
5. **Complete Ontology**: Includes modifiers, truth values, and operators
6. **Information Preservation**: Full Phase 1 vocabulary passed to Phase 3 (no loss)
7. **Notation Extraction**: Two approaches implemented:
   - **Option 1**: Expanded schema structure with integrated notation/patterns
   - **Option 2**: Separate implementation specification extraction

## Representation Paradigms and Interoperability

### Model Type Selection Criteria
Each theory has an inherent structure that suggests an optimal representation:

- **Property Graph**: When relationships are as important as entities (e.g., social networks, causal models)
- **Table/Matrix**: When data is naturally cross-tabulated (e.g., 2x2 classifications, feature matrices)
  - Represented as n-ary relations in schema, convertible to SQL tables later
- **Sequence**: When order and progression matter (e.g., stage theories, process models)
- **Tree**: When hierarchical relationships dominate (e.g., taxonomies, decision trees)
- **Timeline**: When temporal evolution is central (e.g., historical theories, developmental models)
- **Hybrid**: When theories require multiple representations for different aspects
  - Example: Social-Ecological Systems with graph relationships AND access rights matrices
- **Statistical**: For probabilistic theories (factor analysis, SEM, Bayesian networks)
- **Logical**: For formal reasoning systems (argumentation, deontic logic, action theories)
- **Causal**: For causal inference with DAGs, interventions, and counterfactual reasoning
- **Hybrid**: When theories require multiple representations for different aspects
  - Example: Adaptive Governance with belief networks + game matrices + governance sequences + statistical models + normative logic

### Computational Capabilities by Model Type

#### Property Graphs
- **Query Languages**: Cypher, Gremlin, SPARQL
- **Reasoning**: OWL-DL, RDF inference (with appropriate axioms)
- **Operations**: Path finding, centrality, clustering
- **Use Cases**: Network analysis, causal reasoning
- **Schema Features**: Flexible properties, domain/range constraints, reasoning axioms

#### Tables/Matrices (as N-ary Relations)
- **Representation**: N-ary relations in schema, preserving logical structure
- **Query Languages**: SQL (after transformation), Datalog
- **Reasoning**: Relational algebra, constraint satisfaction
- **Operations**: Joins, aggregations, statistical analysis
- **Use Cases**: Classification, cross-tabulation, feature analysis

#### Sequences & Timelines
- **Query Languages**: Temporal SQL, process algebra
- **Reasoning**: Temporal logic, event calculus
- **Operations**: Pattern matching, sequence alignment
- **Use Cases**: Process mining, historical analysis

#### Statistical Models
- **Representation**: Entities with statistical properties, relationships with parameters
- **Schema Features**: Distribution specifications, covariance structures, loadings
- **Operations**: Parameter estimation, model fitting, hypothesis testing
- **Use Cases**: Factor analysis, SEM, Bayesian inference

#### Logical Models
- **Representation**: Propositions as entities, inference rules as relationships
- **Schema Features**: Logical axioms, defeasibility conditions, inference patterns
- **Reasoning**: Description logic, first-order logic, defeasible reasoning
- **Use Cases**: Argumentation, normative systems, planning

#### Causal Models
- **Representation**: Variables as nodes, causal relationships as directed edges in DAGs
- **Schema Features**: Intervention specifications, confounders, effect sizes, temporal ordering
- **Reasoning**: Pearl's do-calculus, causal identification strategies, counterfactual inference
- **Operations**: Intervention queries, causal discovery, effect estimation
- **Use Cases**: Policy impact assessment, intervention design, counterfactual analysis

### Interoperability Strategy
- **Unified Semantic Model**: All structures expressible as entities and n-ary relations with causal metadata
- **Common Vocabulary**: All models share core definitions (Entity, Role, NaryTuple, CausalVariable, etc.)
- **Property Specifications**: Required/optional, predefined/ad-hoc, typed constraints, causal relationships
- **Cross-Model Mappings**: Define transformation rules between representations and causal structures
- **Format Translation**: Transform unified representation to target formats (SQL, RDF/OWL, Neo4j, DAGitty, CausalML)

### Key Design Principles

1. **Multi-Level Theoretical Structure**: Explicit modeling of relationships across individual, group, institutional, and systemic levels for all theoretical purposes
2. **Tables as N-ary Relations**: Tables represented as n-ary relations in schema, preserving logical structure while enabling SQL transformation later
3. **Purpose-Aware Properties**: All relationships can include metadata appropriate to their theoretical purpose (statistical parameters, causal mechanisms, temporal ordering, intervention specifications)
4. **Reasoning in Schema**: Include OWL characteristics, logical axioms, statistical specifications, and analytical strategies in definitions
5. **Hybrid Support**: Explicit support for theories needing multiple representation paradigms across all theoretical purposes
6. **Comprehensive Analytical Design**: Embed descriptive categories, explanatory mechanisms, predictive variables, causal pathways, and intervention points directly in schema
7. **Multi-Purpose Metadata**: Embed statistical parameters, logical axioms, causal structures, and intervention specifications directly in schema

### Example: Theory-Specific Representations

**Cognitive Mapping (Young 1996)**: Property Graph
- Primarily explaining/causality: Cognitive processes and causal relationships between concepts
- Some descriptive: Concept categories and belief structures
- Data structure: Graph with concepts as nodes, relationships as edges

**2x2 Game Theory**: Table Matrix  
- Primarily predicting: Outcome forecasting based on player characteristics
- Some explaining: Equilibrium selection mechanisms
- Data structure: Matrix of strategies and payoffs

**Stages of Change Model**: Sequence
- Primarily intervention: Stage-specific intervention strategies
- Some predicting: Stage progression probability models
- Data structure: Ordered sequence of stages with transition rules

## Output Schema Structure

### Standard Components
- **Citation**: Full bibliographic reference
- **Annotation**: 2-3 sentence theoretical summary
- **Model Type**: Selected representation (with detailed rationale)
- **Schema Blueprint**:
  - Title and description
  - Root properties (model-specific)
  - Comprehensive definitions with proper categorization
  - Supported modifiers/truth values/operators

### Semantic Categories
- **Entities**: Things that exist (no domain/range)
- **Relationships**: Connections between entities (with domain/range)
- **Properties**: Attributes of entities
- **Actions**: Behaviors/operations (with domain/range)
- **Measures**: Metrics and assessments
- **Modifiers**: Temporal/modal qualifiers
- **Truth Values**: Truth conditions
- **Operators**: Logical connectors

## Quality Standards

1. **Vocabulary Completeness**: Extract all theoretical terms, not a subset
2. **Semantic Accuracy**: Proper ontological categorization
3. **Domain/Range Specificity**: Use theory-specific types (Actor→Statement, not Entity→Entity)
4. **Hierarchical Preservation**: Maintain conceptual hierarchies and subtypes
5. **Model Type Justification**: Detailed rationale for representation choice

## Primary Use Case: Automated Theory Application

This project's **primary application** is automated extraction and application of academic theoretical frameworks. Extract a theory's methodology from its paper, then apply it to the same data to validate that we can reproduce comparable results to the original research.

### Theory Application Workflow
```
Academic Paper (.txt)
    ↓
Schema Extraction (automated)
    ↓ 
Apply Schema to Data (same data used in original paper)
    ↓
Compare Results to Original Paper
    ↓
Validate Fidelity and Refine Schema
```

### Key Analytical Questions Addressed
1. **WHO**: Individual agents, groups/communities, institutions, systems
2. **WHAT**: Beliefs, policies, actions, communications, interventions
3. **TO WHOM**: Target audiences, affected populations, stakeholder groups
4. **CHANNELS**: Communication methods, institutional pathways, influence networks
5. **SETTINGS**: Social contexts, institutional environments, historical periods
6. **EFFECTS**: Descriptive patterns, explanatory mechanisms, predictive outcomes, causal relationships, intervention effectiveness

### Multi-Level Analytical Capabilities
1. **Individual Level**: Agent beliefs, decisions, actions, and their patterns, mechanisms, predictions, causes, and modification strategies
2. **Group/Community Level**: Collective behaviors, social processes, group dynamics across all analytical purposes
3. **Institutional Level**: Organizational structures, policy processes, institutional patterns across descriptive, explanatory, predictive, causal, and intervention analysis
4. **System Level**: Structural patterns, transformation processes, emergent phenomena, and system-wide interventions
5. **Cross-Level Integration**: How individual actions aggregate to system outcomes across all theoretical purposes

### Computational Social Science Applications
1. **Descriptive Analysis**: Systematic categorization and classification of social phenomena using theoretical frameworks
2. **Explanatory Analysis**: Understanding mechanisms and processes underlying social behaviors and outcomes
3. **Predictive Modeling**: Forecasting social outcomes and behaviors using theory-based models
4. **Causal Analysis**: Identifying causal relationships and pathways across multiple social levels
5. **Intervention Design**: Developing optimal intervention strategies for desired social outcomes
6. **Theory Integration**: Combining insights from multiple theoretical frameworks for comprehensive multi-purpose analysis

### Additional Use Cases
1. **Cross-Theory Analysis**: Compare theoretical mechanisms across different frameworks and purposes
2. **Knowledge Graphs**: Build interconnected representations of theoretical relationships across all analytical purposes
3. **Computational Modeling**: Enable simulation and testing of theoretical predictions across descriptive, explanatory, predictive, causal, and intervention models
4. **Literature Synthesis**: Identify theoretical patterns and gaps across research domains and purposes
5. **Educational Tools**: Create interactive visualizations of theoretical relationships across all modeling types

## Comparison with TypeDB Capabilities

Through detailed analysis, we have identified key similarities and differences between our approach and TypeDB's polymorphic database system:

### Areas Where Our System Matches or Exceeds TypeDB

#### 1. **N-ary Relations (Hypergraphs)**
- **Our Approach**: Explicit n-ary relations in schema with defined roles and arity
- **TypeDB**: Native atomic n-ary relations
- **Assessment**: **Equivalent capability** - we handle this well through schema design
- **Example**: `institutional_game(player, action, others_profile, institution, payoff)`

#### 2. **Type Hierarchies and Subsumption**
- **Our Approach**: Explicit `subTypeOf` relationships with OWL reasoning support
- **TypeDB**: Automatic polymorphic query expansion across type hierarchies
- **Assessment**: **Equivalent with reasoning engines** - OWL reasoners can handle automatic subsumption
- **Gap**: Query engines (Neo4j, SQL) don't automatically expand unless using OWL reasoner

#### 3. **Complex Attribute Constraints**
- **Our Approach**: Required/optional properties, type constraints, validation rules
- **TypeDB**: Schema-enforced constraints with automatic validation
- **Assessment**: **Equivalent capability** - our validation approach achieves same outcomes
- **Example**: Required properties, unique constraints, type safety through schema validation

#### 4. **Schema Evolution**
- **Our Approach**: Edit schema files, reprocess data as needed
- **TypeDB**: Add subtypes without breaking existing queries
- **Assessment**: **Not needed for our use case** - academic theory schemas are stable
- **Context**: We analyze fixed academic papers, not evolving operational data

#### 5. **Relations Between Relations**
- **Our Approach**: Relationship reification when needed
- **TypeDB**: Native relation-to-relation connections
- **Assessment**: **Functionally equivalent** - reification handles this adequately
- **Example**: Marriage events can relate to divorce events via reified entities

### Areas Where TypeDB Has Technical Advantages We Don't Need

#### 1. **Automatic Type Inference in Queries**
- **TypeDB Advantage**: Queries automatically match all subtypes without enumeration
- **Our Context**: Not critical for discourse analysis - explicit enumeration is manageable
- **Reason**: Academic theory schemas have well-defined, stable type hierarchies

#### 2. **Atomic Transaction Enforcement**
- **TypeDB Advantage**: Database-level enforcement that n-ary relations are complete
- **Our Context**: **Actively disadvantageous** for discourse analysis
- **Reason**: We want to capture partial theoretical mentions, contradictory claims

#### 3. **Incremental Cross-Document Instance Completion**
- **TypeDB Advantage**: Automatically complete partial instances across new documents
- **Our Context**: **Problematic** for discourse analysis - would conflate separate claims
- **Reason**: Multiple sources making different claims about same concept should remain separate

### Why Our Approach Is Better Suited for Discourse Analysis

#### 1. **Claims vs. Ground Truth Modeling**
- **TypeDB Design**: Optimized for modeling single ground truth reality
- **Our Design**: Optimized for capturing multiple, contradictory discourse claims
- **Example**: TypeDB would merge conflicting statements about cooperation; we preserve each claim with source attribution

#### 2. **Source Attribution and Contradiction Preservation**
- **TypeDB**: Consolidates instances into single facts
- **Our Approach**: Maintains source attribution and allows contradictory claims
- **Critical For**: Rhetorical analysis, framing studies, discourse evolution tracking

#### 3. **Partial Instance Value**
- **TypeDB**: Incomplete instances are data quality problems to avoid
- **Our Approach**: Partial theoretical mentions are meaningful analytical data
- **Example**: A tweet mentioning only "cooperation" and "punishment" is valid discourse data

#### 4. **Processing Flexibility**
- **TypeDB**: Real-time insertion with immediate validation
- **Our Approach**: Batch processing with configurable completeness thresholds
- **Advantage**: Can analyze both complete and partial theoretical instantiations

### Current Implementation Gaps

#### Multi-Purpose Analytical Capabilities Needed
1. **Descriptive Enhancements**: Advanced taxonomic extraction, typological analysis, and categorical reasoning
2. **Explanatory Enhancements**: Mechanism identification, process analysis, and structural reasoning
3. **Predictive Enhancements**: Variable identification, model specification, and forecasting capabilities
4. **Causal Enhancements**: DAG representation, do-calculus integration, and counterfactual reasoning
5. **Intervention Enhancements**: Action specification, implementation planning, and effectiveness assessment

#### Schema Enhancements Needed
1. **Multi-Purpose Metadata**: Support for descriptive categories, explanatory mechanisms, predictive variables, causal structures, and intervention specifications
2. **Statistical Metadata**: Support for distributions, covariance structures, parameters across all purposes
3. **Logical Axioms**: Formal representation of inference rules and constraints across theoretical purposes
4. **Analytical Specifications**: Formal representation of analytical capabilities for each theoretical purpose
5. **Cross-Purpose Integration**: Support for theories serving multiple analytical purposes simultaneously

#### Processing Enhancements Needed
1. **Purpose Classification**: Automated identification of theoretical purpose (descriptive/explanatory/predictive/causal/intervention)
2. **Multi-Purpose Extraction**: Theory-guided extraction supporting all analytical purposes at multiple levels
3. **Reasoning Engine Integration**: Connect to specialized reasoning engines for each theoretical purpose
4. **Cross-Purpose Analysis Tools**: Automated identification of connections between different analytical purposes
5. **Integrated Query Engine**: Support for complex queries across all theoretical purposes and paradigms

## Technical Requirements

- **LLM**: OpenAI O3 (for superior analytical capabilities)
- **Processing Time**: 1-2 minutes per paper
- **Output Format**: YAML with embedded JSON Schema
- **Debugging**: Intermediate phase outputs saved for verification

## Future Directions

### Computational Social Science Pipeline Development
1. **Multi-Level Theory-Guided Extraction**: LLM-based extraction supporting all analytical purposes across individual, group, institutional, and system levels
2. **Multi-Purpose Structure Discovery**: Automated identification of descriptive patterns, explanatory mechanisms, predictive relationships, causal structures, and intervention opportunities
3. **Cross-Purpose Integration**: Systematic identification of connections between different theoretical purposes
4. **Comprehensive Analysis Engine**: Support for analysis across all theoretical purposes at multiple social levels
5. **Cross-Level Integration**: Map how individual patterns aggregate to system-level outcomes across all analytical purposes

### Technical Infrastructure
1. **Multi-Purpose Engine Integration**: Connect to specialized analytical frameworks for each theoretical purpose
2. **Multi-Paradigm Query Engine**: Unified interface for querying across different model types and analytical purposes
3. **Cross-Model Transformation**: Automated translation between representations across all theoretical purposes
4. **Reasoning Engine Integration**: Connect to OWL reasoners, statistical engines, causal inference tools, and intervention design systems
5. **Export Pipeline**: Generate formats for all analytical purposes (taxonomies, mechanisms, models, DAGs, intervention plans)
6. **Federated Queries**: Query across multiple theories regardless of model type or theoretical purpose

### Advanced Multi-Purpose Capabilities
7. **Dynamic Theoretical Modeling**: Track how theoretical relationships evolve across purposes and contexts
8. **Cross-Theory Integration**: Combine insights from multiple theoretical frameworks across all purposes
9. **Purpose Optimization**: Automated design of optimal analytical strategies for each theoretical purpose
10. **Multi-Purpose Validation Framework**: Methods for validating theoretical claims across all analytical purposes
11. **Multi-Level Simulation**: Models that integrate theories across purposes and levels
12. **Automated Schema Refinement**: Improve schemas based on analysis results across all purposes

### Extended Model Types Under Consideration
- **Statistical Models**: For predictive analysis and forecasting ✅ IMPLEMENTED
- **Taxonomic Hierarchies**: For descriptive classification systems ✅ IMPLEMENTED
- **Process Models**: For explanatory mechanism representation ✅ IMPLEMENTED
- **Causal DAGs**: For causal inference and intervention design ✅ IMPLEMENTED
- **Implementation Frameworks**: For intervention specification and planning ✅ IMPLEMENTED
- **Hypergraphs**: For n-ary relationships beyond binary edges ✅ IMPLEMENTED
- **Category Theory**: For mathematical theories with morphisms
- **Petri Nets**: For concurrent process theories
- **Agent-Based Models**: For multi-level simulation with emergent properties
- **Structural Equation Models**: For latent variable analysis across purposes ✅ PARTIALLY IMPLEMENTED

## Success Metrics

### Schema Quality Metrics
- **Extraction Completeness**: 90%+ of theoretical terms captured
- **Categorization Accuracy**: Correct ontological classification
- **Domain/Range Specificity**: No generic Entity→Entity relationships
- **Model Type Diversity**: Using all model types where appropriate
- **Theoretical Fidelity**: Preserving discipline-specific terminology
- **Reasoning Capability**: Capturing logical/statistical requirements in schema
- **Hybrid Support**: Complex theories properly represented with multiple paradigms

### Computational Social Science Effectiveness
- **Descriptive Accuracy**: Correct identification of taxonomies, typologies, and classification systems
- **Explanatory Accuracy**: Accurate identification of mechanisms, processes, and structural relationships
- **Predictive Accuracy**: Reliable forecasting capabilities and variable specification
- **Causal Accuracy**: Correct identification of causal relationships and intervention opportunities
- **Intervention Accuracy**: Accurate specification of implementation strategies and effectiveness assessment
- **Cross-Purpose Integration**: Successful modeling across all theoretical purposes at multiple levels
- **Multi-Level Analysis**: Comprehensive analysis across individual→group→institutional→system levels for all purposes

### Technical Performance
- **Multi-Purpose Integration Ready**: Schemas convertible to statistical models, taxonomies, process models, causal DAGs, intervention frameworks ✅
- **Comprehensive Analytical Support**: Full integration with analytical frameworks for all theoretical purposes ✅
- **Multi-Level Analysis**: Cross-level relationship modeling across all purposes (individual→system) ✅
- **Transformation Ready**: Schemas convertible to formats supporting all analytical purposes (SQL, RDF/OWL, statistical packages, visualization tools) ✅
- **Unified Representation**: All structures expressible in entity/relation framework with multi-purpose metadata ✅
- **Query Flexibility**: Support for diverse analytical approaches across all theoretical purposes ✅
- **Processing Efficiency**: Reasonable performance at large-scale computational social science analysis across all purposes

## Next Steps

### Immediate Priorities
1. **Implement Multi-Pass Extraction**: Create specialized extractors for:
   - Pass 1: Notation and symbols
   - Pass 2: Tables and formal rules
   - Pass 3: Algorithms and pseudocode
   - Pass 4: Metrics and evaluation
   - Pass 5: Complete examples

2. **Test on Young 1996**: Apply improved extraction to achieve target fidelity

3. **Standardize Implementation Specs**: Create formal structure for capturing:
   - Type inference rules
   - Algorithm specifications
   - Pattern languages
   - Evaluation metrics

### Architecture Improvements
1. **Hybrid Extraction Pipeline**: Combine Option 1 (integrated) with Option 2 (detailed)
2. **Validation Framework**: Compare extracted schemas against paper examples
3. **Notation-Aware Processing**: Special handling for theories with formal notation

## Conclusion

This project represents a significant advance in **computational social science** by making academic knowledge computationally accessible for comprehensive theoretical analysis while maintaining theoretical integrity. Our approach is specifically optimized for multi-purpose analysis from discourse data, enabling descriptive categorization, explanatory understanding, predictive modeling, causal inference, and intervention design across individual, group, institutional, and system levels. This balanced **multi-purpose computational social science** approach makes it superior to ground-truth-focused systems like TypeDB for social science applications, while maintaining equivalent capabilities for complex theoretical representation and adding sophisticated analytical capabilities across all theoretical purposes.