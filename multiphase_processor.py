#!/usr/bin/env python3
"""
Multiphase Academic Paper Processor
Converts academic papers into structured schemas through a three-phase approach:
1. Vocabulary Extraction
2. Ontological Classification  
3. Graph Schema Generation
"""

import os
import sys
import json
import yaml
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "o3")

# Phase 1: Vocabulary Extraction Models
class VocabularyTerm(BaseModel):
    term: str = Field(description="The theoretical term from the paper")
    definition: str = Field(description="Clear, concise definition from the paper")
    source_context: str = Field(description="Brief quote or context where term appears")
    page_reference: Optional[str] = Field(description="Page number or section reference if available")

class Phase1Output(BaseModel):
    citation: str = Field(description="MLA-9 format citation")
    annotation: str = Field(description="1-2 sentence summary of the paper")
    vocabulary: List[VocabularyTerm] = Field(description="All theoretical terms extracted from the paper")

# Phase 2: Ontological Classification Models
class ClassifiedTerm(BaseModel):
    term: str = Field(description="The theoretical term")
    term_type: str = Field(description="Type: entity, relationship, property, action, or measure")
    domain: Optional[List[str]] = Field(description="For relationships/actions: valid subject types")
    range: Optional[List[str]] = Field(description="For relationships/actions: valid object types")
    parent_concept: Optional[str] = Field(description="Parent term if this is a subtype")

class Phase2Output(BaseModel):
    entities: List[str] = Field(description="Terms that represent things/concepts/actors")
    relationships: List[ClassifiedTerm] = Field(description="Terms that connect entities")
    properties: List[str] = Field(description="Terms that describe attributes of entities")
    actions: List[ClassifiedTerm] = Field(description="Terms that represent behaviors/operations")
    measures: List[str] = Field(description="Terms that represent metrics/measurements")

# Phase 3: Graph Schema Generation Models  
class NodeType(BaseModel):
    name: str = Field(description="Node type name")
    properties: List[str] = Field(description="Properties this node type can have")
    description: str = Field(description="What this node type represents")

class EdgeType(BaseModel):
    name: str = Field(description="Edge type name")
    from_types: List[str] = Field(description="Valid source node types")
    to_types: List[str] = Field(description="Valid target node types")
    properties: Optional[List[str]] = Field(description="Properties this edge can have")
    description: str = Field(description="What this relationship represents")

class Phase3Output(BaseModel):
    title: str = Field(description="Human-readable schema title")
    description: str = Field(description="One-sentence description of the schema")
    model_type: str = Field(description="property_graph, table_matrix, sequence, tree, timeline, or other")
    rationale: str = Field(description="Why this model type was chosen")
    node_types: List[NodeType] = Field(description="Node type definitions")
    edge_types: List[EdgeType] = Field(description="Edge type definitions")
    property_definitions: Dict[str, str] = Field(description="Definitions of all properties used")

# Prompts for each phase
PHASE1_PROMPT = """You are an expert at extracting theoretical vocabulary from academic papers.

Your task is to read the provided academic paper and extract ALL theoretical terms, concepts, relationships, and specialized vocabulary that the authors define or use.

Be exhaustive - capture every term that has theoretical significance in the paper. Include:
- Core concepts and constructs
- Relationships and connections  
- Actions and processes
- Properties and attributes
- Measures and metrics
- Any specialized terminology

For each term, provide:
1. The exact term as used in the paper
2. A clear, concise definition based on the paper's usage
3. Brief context showing where/how the term is used
4. Page reference if available

Also provide the paper's citation in MLA-9 format and a 1-2 sentence annotation summarizing the paper's contribution."""

PHASE2_PROMPT = """You are an expert in knowledge representation and ontology design.

Given the vocabulary extracted from an academic paper, classify each term into one of these categories:

1. **Entity** - Things that exist (actors, concepts, objects, events)
   - Examples: "government", "policy", "decision-maker", "outcome"

2. **Relationship** - Connections between entities  
   - Examples: "influences", "causes", "belongs-to", "follows"
   - Must specify domain (what can be the subject) and range (what can be the object)

3. **Property** - Attributes or characteristics of entities
   - Examples: "credibility", "stability", "effectiveness"

4. **Action** - Behaviors or operations performed by entities
   - Examples: "negotiate", "implement", "evaluate"  
   - Must specify domain (who can perform) and range (what is acted upon)

5. **Measure** - Metrics, measurements, or assessment methods
   - Examples: "success-rate", "influence-score", "response-time"

For relationships and actions, determine the valid domain and range constraints.
For hierarchical terms, identify parent concepts where applicable."""

PHASE3_PROMPT = """You are an expert in graph database schema design.

Given the classified vocabulary from an academic theory, design a property graph schema that can represent the theory's concepts and relationships.

First, determine the optimal model type:
- **property_graph**: For theories with rich relationships between entities
- **table_matrix**: For theories based on structured classifications  
- **sequence**: For theories focused on ordered processes
- **tree**: For theories with hierarchical structures
- **timeline**: For theories centered on temporal evolution
- **other**: For theories that don't fit standard patterns

Then design the schema with:
1. Node types - What kinds of entities exist
2. Edge types - What relationships connect entities
3. Properties - What attributes describe nodes and edges

Ensure all vocabulary terms are represented in the schema design."""

def phase1_extract_vocabulary(paper_text: str) -> Phase1Output:
    """Phase 1: Extract vocabulary from academic paper"""
    messages = [
        {"role": "system", "content": PHASE1_PROMPT},
        {"role": "user", "content": f"Here is the academic paper to analyze:\n\n{paper_text}"}
    ]
    
    print(f"  Using model: {MODEL}")
    response = client.beta.chat.completions.parse(
        model=MODEL,
        messages=messages,
        response_format=Phase1Output
    )
    
    return response.choices[0].message.parsed

def phase2_classify_terms(phase1_output: Phase1Output) -> Phase2Output:
    """Phase 2: Classify vocabulary into ontological categories"""
    vocab_summary = "\n".join([
        f"- {t.term}: {t.definition}" 
        for t in phase1_output.vocabulary
    ])
    
    messages = [
        {"role": "system", "content": PHASE2_PROMPT},
        {"role": "user", "content": f"Paper: {phase1_output.citation}\n\nVocabulary to classify:\n{vocab_summary}"}
    ]
    
    response = client.beta.chat.completions.parse(
        model=MODEL,
        messages=messages,
        response_format=Phase2Output
    )
    
    return response.choices[0].message.parsed

def phase3_generate_schema(phase1_output: Phase1Output, phase2_output: Phase2Output) -> Phase3Output:
    """Phase 3: Generate graph schema from classified terms"""
    classification_summary = f"""
Entities: {', '.join(phase2_output.entities)}

Relationships:
{chr(10).join([f"- {r.term} (from: {r.domain} to: {r.range})" for r in phase2_output.relationships])}

Properties: {', '.join(phase2_output.properties)}

Actions:
{chr(10).join([f"- {a.term} (from: {a.domain} to: {a.range})" for a in phase2_output.actions])}

Measures: {', '.join(phase2_output.measures)}
"""
    
    messages = [
        {"role": "system", "content": PHASE3_PROMPT},
        {"role": "user", "content": f"Paper: {phase1_output.citation}\n\n{phase1_output.annotation}\n\nClassified vocabulary:\n{classification_summary}"}
    ]
    
    response = client.beta.chat.completions.parse(
        model=MODEL,
        messages=messages,
        response_format=Phase3Output
    )
    
    return response.choices[0].message.parsed

def convert_to_yaml_format(phase1: Phase1Output, phase2: Phase2Output, phase3: Phase3Output) -> Dict:
    """Convert the three phases into the expected YAML format"""
    # Build definitions list from all phases
    definitions = []
    
    # Add entities
    for entity in phase2.entities:
        term_info = next((t for t in phase1.vocabulary if t.term == entity), None)
        if term_info:
            definitions.append({
                "name": entity,
                "category": "entity",
                "description": term_info.definition
            })
    
    # Add relationships with domain/range
    for rel in phase2.relationships:
        term_info = next((t for t in phase1.vocabulary if t.term == rel.term), None)
        if term_info:
            def_item = {
                "name": rel.term,
                "category": "relationship",
                "description": term_info.definition
            }
            if rel.domain:
                def_item["domain"] = rel.domain
            if rel.range:
                def_item["range"] = rel.range
            definitions.append(def_item)
    
    # Add properties
    for prop in phase2.properties:
        term_info = next((t for t in phase1.vocabulary if t.term == prop), None)
        if term_info:
            definitions.append({
                "name": prop,
                "category": "property",
                "description": term_info.definition
            })
    
    # Add actions with domain/range
    for action in phase2.actions:
        term_info = next((t for t in phase1.vocabulary if t.term == action.term), None)
        if term_info:
            def_item = {
                "name": action.term,
                "category": "action",
                "description": term_info.definition
            }
            if action.domain:
                def_item["domain"] = action.domain
            if action.range:
                def_item["range"] = action.range
            definitions.append(def_item)
    
    # Add measures
    for measure in phase2.measures:
        term_info = next((t for t in phase1.vocabulary if t.term == measure), None)
        if term_info:
            definitions.append({
                "name": measure,
                "category": "measure",
                "description": term_info.definition
            })
    
    # Build final YAML structure
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
                    "description": "The entities and concepts in the model",
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
    
    return yaml_output

def process_paper(paper_path: str, output_path: Optional[str] = None) -> Dict:
    """Process a paper through all three phases"""
    print(f"Processing {paper_path}...")
    
    # Read paper
    with open(paper_path, 'r', encoding='utf-8') as f:
        paper_text = f.read()
    
    # Phase 1: Extract vocabulary
    print("Phase 1: Extracting vocabulary...")
    phase1_output = phase1_extract_vocabulary(paper_text)
    print(f"  Extracted {len(phase1_output.vocabulary)} terms")
    
    # Phase 2: Classify terms
    print("Phase 2: Classifying terms...")
    phase2_output = phase2_classify_terms(phase1_output)
    print(f"  Classified into {len(phase2_output.entities)} entities, "
          f"{len(phase2_output.relationships)} relationships, "
          f"{len(phase2_output.actions)} actions")
    
    # Phase 3: Generate schema
    print("Phase 3: Generating schema...")
    phase3_output = phase3_generate_schema(phase1_output, phase2_output)
    print(f"  Generated {phase3_output.model_type} schema with "
          f"{len(phase3_output.node_types)} node types and "
          f"{len(phase3_output.edge_types)} edge types")
    
    # Convert to YAML format
    yaml_data = convert_to_yaml_format(phase1_output, phase2_output, phase3_output)
    
    # Save output
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(yaml_data, f, allow_unicode=True, default_flow_style=False)
        print(f"Saved to {output_path}")
    
    # Also save intermediate outputs for debugging
    debug_dir = Path(output_path).parent / "debug" if output_path else Path("debug")
    debug_dir.mkdir(exist_ok=True)
    
    base_name = Path(paper_path).stem
    with open(debug_dir / f"{base_name}_phase1.json", 'w') as f:
        json.dump(phase1_output.model_dump(), f, indent=2)
    with open(debug_dir / f"{base_name}_phase2.json", 'w') as f:
        json.dump(phase2_output.model_dump(), f, indent=2)
    with open(debug_dir / f"{base_name}_phase3.json", 'w') as f:
        json.dump(phase3_output.model_dump(), f, indent=2)
    
    return yaml_data

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python multiphase_processor.py <paper.txt> [output.yml]")
        sys.exit(1)
    
    paper_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(paper_path):
        print(f"Error: Paper file '{paper_path}' not found")
        sys.exit(1)
    
    try:
        result = process_paper(paper_path, output_path)
        print("\nProcessing complete!")
        
    except Exception as e:
        print(f"Error processing paper: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()