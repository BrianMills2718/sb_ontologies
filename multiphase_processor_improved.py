#!/usr/bin/env python3
"""
Improved Multiphase Academic Paper Processor
Addresses weaknesses in the original multiphase approach:
- Extracts comprehensive vocabulary (not limited to 20-30 terms)
- Preserves theoretical subcategories and nuance
- Infers specific domain/range types
- Includes modifiers, truth values, and operators
- Generates theory-adaptive schemas
"""

import os
import sys
import json
import yaml
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")

# Phase 1: Comprehensive Vocabulary Extraction Models
class VocabularyTerm(BaseModel):
    term: str = Field(description="The theoretical term from the paper")
    definition: str = Field(description="Clear, concise definition from the paper")
    source_context: str = Field(description="Brief quote or context where term appears")
    page_reference: Optional[str] = Field(description="Page number or section reference if available")
    theoretical_category: Optional[str] = Field(description="Theory-specific category (e.g., 'core-construct', 'strategy-type')")

class Phase1Output(BaseModel):
    citation: str = Field(description="Full bibliographic citation")
    annotation: str = Field(description="2-3 sentence summary of the paper's contribution")
    theory_type: str = Field(description="Type of theory: cognitive, behavioral, social, organizational, etc.")
    vocabulary: List[VocabularyTerm] = Field(description="ALL theoretical terms extracted from the paper")

# Phase 2: Enhanced Ontological Classification Models
class ClassifiedTerm(BaseModel):
    term: str = Field(description="The theoretical term")
    term_type: str = Field(description="Primary type: entity, relationship, property, action, measure, modifier, truth-value, operator")
    subtype: Optional[str] = Field(description="Theory-specific subtype (e.g., 'core-construct', 'psychological-process')")
    domain: Optional[List[str]] = Field(description="For relationships/actions: specific valid subject types")
    range: Optional[List[str]] = Field(description="For relationships/actions: specific valid object types")
    parent_concept: Optional[str] = Field(description="Parent term if this is a subtype")
    constraints: Optional[Dict[str, str]] = Field(description="Additional semantic constraints")

class Phase2Output(BaseModel):
    entities: List[ClassifiedTerm] = Field(description="Terms that represent things/concepts/actors")
    relationships: List[ClassifiedTerm] = Field(description="Terms that connect entities")
    properties: List[ClassifiedTerm] = Field(description="Terms that describe attributes of entities")
    actions: List[ClassifiedTerm] = Field(description="Terms that represent behaviors/operations")
    measures: List[ClassifiedTerm] = Field(description="Terms that represent metrics/measurements")
    modifiers: List[ClassifiedTerm] = Field(description="Terms that modify statements (temporal, modal)")
    truth_values: List[ClassifiedTerm] = Field(description="Terms representing truth conditions")
    operators: List[ClassifiedTerm] = Field(description="Logical or structural operators")

# Phase 3: Adaptive Schema Generation Models
class NodeType(BaseModel):
    name: str = Field(description="Node type name")
    properties: List[str] = Field(description="Properties this node type can have")
    description: str = Field(description="What this node type represents")
    subtypes: Optional[List[str]] = Field(description="Subtypes of this node")
    constraints: Optional[Dict[str, str]] = Field(description="Additional constraints")

class EdgeType(BaseModel):
    name: str = Field(description="Edge type name")
    from_types: List[str] = Field(description="Specific valid source node types")
    to_types: List[str] = Field(description="Specific valid target node types")
    properties: Optional[List[str]] = Field(description="Properties this edge can have")
    description: str = Field(description="What this relationship represents")
    inverse: Optional[str] = Field(description="Inverse relationship if applicable")

class Phase3Output(BaseModel):
    title: str = Field(description="Theory-specific schema title")
    description: str = Field(description="Comprehensive description of the schema")
    model_type: str = Field(description="property_graph, table_matrix, sequence, tree, timeline, or other")
    rationale: str = Field(description="Detailed justification for model type selection")
    node_types: List[NodeType] = Field(description="Comprehensive node type definitions")
    edge_types: List[EdgeType] = Field(description="Comprehensive edge type definitions")
    property_definitions: Optional[Dict[str, str]] = Field(description="Definitions of all properties used", default=None)
    modifiers_supported: Optional[List[str]] = Field(description="Temporal and modal modifiers", default=None)
    truth_values_supported: Optional[List[str]] = Field(description="Truth value system used", default=None)
    operators_supported: Optional[List[str]] = Field(description="Logical operators supported", default=None)

# Enhanced Prompts for each phase
PHASE1_PROMPT = """You are an expert at extracting theoretical vocabulary from academic papers.

Your task is to EXHAUSTIVELY extract ALL theoretical terms, concepts, relationships, and specialized vocabulary from the provided academic paper. Do not limit yourself to a specific number - capture everything that has theoretical significance.

For each term, provide:
1. The exact term as used in the paper
2. A clear, concise definition based on the paper's usage
3. Brief context showing where/how the term is used
4. Page reference if available
5. Theory-specific category if the paper uses one (e.g., 'core-construct', 'strategy-type', 'psychological-process')

Also identify:
- The type of theory (cognitive, behavioral, social, organizational, etc.)
- Full bibliographic citation
- 2-3 sentence annotation summarizing the paper's theoretical contribution

Be comprehensive - include:
- All core concepts and constructs
- All types of relationships mentioned
- All actions, processes, and operations
- All properties, attributes, and characteristics
- All measures, metrics, and assessments
- All modifiers (temporal, modal, conditional)
- Any truth values or logical operators
- Domain-specific terminology
- Theoretical subcategories and hierarchies"""

PHASE2_PROMPT = """You are an expert in knowledge representation and ontology design.

Given the vocabulary from an academic paper, classify each term into ontological categories with maximum specificity.

Primary Categories:
1. **Entity** - Things that exist (actors, concepts, objects, events, statements)
2. **Relationship** - Connections between entities (with specific domain/range)
3. **Property** - Attributes or characteristics of entities
4. **Action** - Behaviors or operations (with specific domain/range)
5. **Measure** - Metrics, measurements, or assessment methods
6. **Modifier** - Temporal (past/present/future) or modal (hypothetical/normative/goal) qualifiers
7. **Truth-Value** - Truth conditions (true/false/possible/impossible/partial)
8. **Operator** - Logical or structural operators (and/or/not)

For each term:
- Assign primary type and theory-specific subtype if applicable
- For relationships/actions: infer SPECIFIC domain/range types (not generic "Entity")
  - Use the most specific types possible based on the theory
  - Examples: Actor→Statement, Leader→Follower, Message→Audience
- Identify hierarchical relationships (parent concepts)
- Note any additional semantic constraints

Preserve all theoretical nuance and subcategorizations from the original paper."""

PHASE3_PROMPT = """You are an expert in schema design for knowledge representation.

Given the classified vocabulary from an academic theory, design a comprehensive schema that:

1. **Selects the optimal model type** based on the theory's actual structure:
   - property_graph: Rich relationships between diverse entities
   - table_matrix: Structured classifications or typologies
   - sequence: Ordered processes or stages
   - tree: Hierarchical taxonomies or decision trees
   - timeline: Temporal evolution or historical development
   - other: Unique structures requiring custom representation

2. **Designs comprehensive node types** with:
   - Specific node types matching the theory's entities
   - All relevant properties for each node type
   - Hierarchical subtypes where applicable
   - Semantic constraints

3. **Defines precise edge types** with:
   - Specific from/to type constraints (not generic)
   - Edge properties where applicable
   - Inverse relationships where relevant

4. **Includes all supporting elements**:
   - Complete property definitions
   - Modifiers (temporal/modal) used in the theory
   - Truth value system if applicable
   - Logical operators if used

5. **Adapts to the specific theory**:
   - Title should reference the theory name
   - Description should explain the theory's focus
   - Structure should match the theory's conceptual model

Do not default to property_graph - genuinely evaluate which model type best represents this specific theory."""

def phase1_extract_vocabulary(paper_text: str) -> Phase1Output:
    """Phase 1: Extract comprehensive vocabulary from academic paper"""
    messages = [
        {"role": "system", "content": PHASE1_PROMPT},
        {"role": "user", "content": f"Extract all theoretical vocabulary from this paper:\n\n{paper_text}"}
    ]
    
    print(f"Phase 1: Extracting vocabulary with {MODEL}...")
    
    # O3 doesn't support temperature parameter
    kwargs = {
        "model": MODEL,
        "messages": messages,
        "response_format": Phase1Output
    }
    if MODEL not in ["o3", "o3-mini"]:
        kwargs["temperature"] = 0.3  # Lower temperature for more consistent extraction
    
    response = client.beta.chat.completions.parse(**kwargs)
    
    return response.choices[0].message.parsed

def phase2_classify_terms(phase1_output: Phase1Output) -> Phase2Output:
    """Phase 2: Classify vocabulary with enhanced specificity"""
    # Group terms by theoretical category for better context
    terms_by_category = {}
    for term in phase1_output.vocabulary:
        cat = term.theoretical_category or "general"
        if cat not in terms_by_category:
            terms_by_category[cat] = []
        terms_by_category[cat].append(f"{term.term}: {term.definition}")
    
    vocab_summary = f"Theory Type: {phase1_output.theory_type}\n\nVocabulary by Category:\n"
    for cat, terms in terms_by_category.items():
        vocab_summary += f"\n{cat}:\n" + "\n".join(f"  - {t}" for t in terms)
    
    messages = [
        {"role": "system", "content": PHASE2_PROMPT},
        {"role": "user", "content": f"Paper: {phase1_output.citation}\n\n{vocab_summary}"}
    ]
    
    print("Phase 2: Classifying terms with enhanced ontology...")
    
    kwargs = {
        "model": MODEL,
        "messages": messages,
        "response_format": Phase2Output
    }
    if MODEL not in ["o3", "o3-mini"]:
        kwargs["temperature"] = 0.3
    
    response = client.beta.chat.completions.parse(**kwargs)
    
    return response.choices[0].message.parsed

def phase3_generate_schema(phase1_output: Phase1Output, phase2_output: Phase2Output) -> Phase3Output:
    """Phase 3: Generate theory-adaptive schema"""
    # Create detailed classification summary
    classification_summary = f"""
Theory Type: {phase1_output.theory_type}
Paper: {phase1_output.citation}
Summary: {phase1_output.annotation}

Entities ({len(phase2_output.entities)}):
{chr(10).join([f"- {e.term} ({e.subtype or 'general'})" for e in phase2_output.entities[:10]])}
{f"... and {len(phase2_output.entities) - 10} more" if len(phase2_output.entities) > 10 else ""}

Relationships ({len(phase2_output.relationships)}):
{chr(10).join([f"- {r.term}: {r.domain} → {r.range}" for r in phase2_output.relationships[:10]])}
{f"... and {len(phase2_output.relationships) - 10} more" if len(phase2_output.relationships) > 10 else ""}

Actions ({len(phase2_output.actions)}):
{chr(10).join([f"- {a.term}: {a.domain} → {a.range}" for a in phase2_output.actions[:10]])}
{f"... and {len(phase2_output.actions) - 10} more" if len(phase2_output.actions) > 10 else ""}

Properties: {', '.join([p.term for p in phase2_output.properties[:10]])}
Measures: {', '.join([m.term for m in phase2_output.measures[:10]])}
Modifiers: {', '.join([m.term for m in phase2_output.modifiers])}
Truth Values: {', '.join([t.term for t in phase2_output.truth_values])}
Operators: {', '.join([o.term for o in phase2_output.operators])}
"""
    
    messages = [
        {"role": "system", "content": PHASE3_PROMPT},
        {"role": "user", "content": classification_summary}
    ]
    
    print("Phase 3: Generating theory-adaptive schema...")
    
    kwargs = {
        "model": MODEL,
        "messages": messages,
        "response_format": Phase3Output
    }
    if MODEL not in ["o3", "o3-mini"]:
        kwargs["temperature"] = 0.4  # Slightly higher for creative schema design
    
    response = client.beta.chat.completions.parse(**kwargs)
    
    return response.choices[0].message.parsed

def convert_to_yaml_format(phase1: Phase1Output, phase2: Phase2Output, phase3: Phase3Output) -> Dict:
    """Convert phases to enhanced YAML format preserving all richness"""
    definitions = []
    
    # Helper to add term with all metadata
    def add_term(term: ClassifiedTerm, primary_category: str):
        def_item = {
            "name": term.term,
            "category": term.subtype or primary_category,
            "description": next((t.definition for t in phase1.vocabulary if t.term == term.term), "")
        }
        
        # Add domain/range only for relationships and actions
        if primary_category in ["relationship", "action"] and term.domain and term.range:
            def_item["domain"] = term.domain
            def_item["range"] = term.range
        
        # Add parent concept for hierarchies
        if term.parent_concept:
            def_item["subTypeOf"] = term.parent_concept
        
        # Add constraints if present
        if term.constraints:
            for key, value in term.constraints.items():
                def_item[key] = value
        
        definitions.append(def_item)
    
    # Add all classified terms preserving subcategories
    for entity in phase2.entities:
        add_term(entity, "entity")
    
    for rel in phase2.relationships:
        add_term(rel, "relationship")
    
    for prop in phase2.properties:
        add_term(prop, "property")
    
    for action in phase2.actions:
        add_term(action, "action")
    
    for measure in phase2.measures:
        add_term(measure, "measure")
    
    for modifier in phase2.modifiers:
        add_term(modifier, "modifier")
    
    for truth in phase2.truth_values:
        add_term(truth, "truth-value")
    
    for op in phase2.operators:
        add_term(op, "operator")
    
    # Build comprehensive YAML structure
    yaml_output = {
        "citation": phase1.citation,
        "annotation": phase1.annotation,
        "model_type": phase3.model_type,
        "rationale": phase3.rationale,
        "schema_blueprint": {
            "title": phase3.title,
            "description": phase3.description,
            "root_properties": {
                "nodes": {
                    "description": "The entities and concepts in the theoretical model",
                    "item_type": "Entity"
                },
                "edges": {
                    "description": "The relationships and actions connecting entities",
                    "item_type": "NaryTuple"
                }
            },
            "definitions": definitions
        }
    }
    
    # Add model-specific root properties if not property_graph
    if phase3.model_type == "table_matrix":
        yaml_output["schema_blueprint"]["root_properties"] = {
            "rows": {"description": "Row categories in the matrix", "item_type": "Entity"},
            "columns": {"description": "Column categories in the matrix", "item_type": "Entity"},
            "cells": {"description": "Values or relationships in matrix cells", "item_type": "Value"}
        }
    elif phase3.model_type == "sequence":
        yaml_output["schema_blueprint"]["root_properties"] = {
            "stages": {"description": "Sequential stages or steps", "item_type": "Stage"},
            "transitions": {"description": "Transitions between stages", "item_type": "Transition"}
        }
    elif phase3.model_type == "tree":
        yaml_output["schema_blueprint"]["root_properties"] = {
            "root": {"description": "Root node of the hierarchy", "item_type": "Entity"},
            "branches": {"description": "Hierarchical relationships", "item_type": "Hierarchy"}
        }
    elif phase3.model_type == "timeline":
        yaml_output["schema_blueprint"]["root_properties"] = {
            "events": {"description": "Events in temporal order", "item_type": "Event"},
            "periods": {"description": "Time periods or phases", "item_type": "Period"}
        }
    
    # Add metadata about supported features
    if phase3.modifiers_supported:
        yaml_output["schema_blueprint"]["modifiers_supported"] = phase3.modifiers_supported
    if phase3.truth_values_supported:
        yaml_output["schema_blueprint"]["truth_values_supported"] = phase3.truth_values_supported
    if phase3.operators_supported:
        yaml_output["schema_blueprint"]["operators_supported"] = phase3.operators_supported
    
    return yaml_output

def process_paper(paper_path: str, output_path: Optional[str] = None) -> Dict:
    """Process a paper through all three enhanced phases"""
    print(f"\nProcessing {paper_path} with improved multiphase processor...")
    
    # Read paper
    with open(paper_path, 'r', encoding='utf-8') as f:
        paper_text = f.read()
    
    # Phase 1: Extract comprehensive vocabulary
    print("\nPhase 1: Extracting comprehensive vocabulary...")
    phase1_output = phase1_extract_vocabulary(paper_text)
    print(f"  Extracted {len(phase1_output.vocabulary)} terms")
    print(f"  Theory type: {phase1_output.theory_type}")
    
    # Phase 2: Classify with enhanced specificity
    print("\nPhase 2: Classifying terms with enhanced ontology...")
    phase2_output = phase2_classify_terms(phase1_output)
    print(f"  Entities: {len(phase2_output.entities)}")
    print(f"  Relationships: {len(phase2_output.relationships)}")
    print(f"  Actions: {len(phase2_output.actions)}")
    print(f"  Properties: {len(phase2_output.properties)}")
    print(f"  Measures: {len(phase2_output.measures)}")
    print(f"  Modifiers: {len(phase2_output.modifiers)}")
    print(f"  Truth values: {len(phase2_output.truth_values)}")
    
    # Phase 3: Generate theory-adaptive schema
    print("\nPhase 3: Generating theory-adaptive schema...")
    phase3_output = phase3_generate_schema(phase1_output, phase2_output)
    print(f"  Model type: {phase3_output.model_type}")
    print(f"  Node types: {len(phase3_output.node_types)}")
    print(f"  Edge types: {len(phase3_output.edge_types)}")
    
    # Convert to enhanced YAML format
    yaml_data = convert_to_yaml_format(phase1_output, phase2_output, phase3_output)
    
    # Save output
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(yaml_data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        print(f"\nSaved to {output_path}")
    
    # Save detailed debug outputs
    debug_dir = Path(output_path).parent / "debug_improved" if output_path else Path("debug_improved")
    debug_dir.mkdir(exist_ok=True)
    
    base_name = Path(paper_path).stem
    with open(debug_dir / f"{base_name}_phase1.json", 'w') as f:
        json.dump(phase1_output.model_dump(), f, indent=2)
    with open(debug_dir / f"{base_name}_phase2.json", 'w') as f:
        json.dump(phase2_output.model_dump(), f, indent=2)
    with open(debug_dir / f"{base_name}_phase3.json", 'w') as f:
        json.dump(phase3_output.model_dump(), f, indent=2)
    
    print(f"Debug outputs saved to {debug_dir}/")
    
    return yaml_data

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python multiphase_processor_improved.py <paper.txt> [output.yml]")
        sys.exit(1)
    
    paper_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(paper_path):
        print(f"Error: Paper file '{paper_path}' not found")
        sys.exit(1)
    
    try:
        result = process_paper(paper_path, output_path)
        print("\nProcessing complete!")
        print(f"Total definitions: {len(result['schema_blueprint']['definitions'])}")
        
    except Exception as e:
        print(f"Error processing paper: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()