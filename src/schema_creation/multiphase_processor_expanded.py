#!/usr/bin/env python3
"""
Expanded Multiphase Processor - Option 1
Includes notation systems and pattern libraries as part of the schema structure
"""

import os
import sys
import json
import yaml
from typing import Dict, List, Optional, Any
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "o3")

# Import base models from improved processor
sys.path.insert(0, str(Path(__file__).parent.parent))
from schema_creation.multiphase_processor_improved import (
    Phase1Output, Phase2Output, 
    phase1_extract_vocabulary, phase2_classify_terms,
    VocabularyTerm, ClassifiedTerm, NodeType, EdgeType
)

# Expanded Phase 3 models with notation and patterns
class NotationSystem(BaseModel):
    """Formal notation system used by the theory"""
    type_codes: Optional[Dict[str, str]] = Field(description="Type codes and their meanings (e.g., 'C': 'Concept')")
    role_codes: Optional[Dict[str, str]] = Field(description="Argument role codes (e.g., 'sa': 'subject-agent')")
    special_symbols: Optional[Dict[str, str]] = Field(description="Special operators and symbols")
    composite_notations: Optional[List[str]] = Field(description="Examples of composite notations (e.g., 'P.sa')")

class PatternDefinition(BaseModel):
    """Pattern matching rule"""
    pattern: str = Field(description="Pattern syntax (e.g., 'P.sa +/B P.pa')")
    description: str = Field(description="What this pattern matches")
    example: Optional[str] = Field(description="Example text that matches this pattern")
    action: Optional[str] = Field(description="Transformation or extraction action")

class AlgorithmStep(BaseModel):
    """Single step in an algorithm"""
    step_number: int
    description: str
    substeps: Optional[List[str]] = None

class ImplementationAlgorithm(BaseModel):
    """Detailed algorithm specification"""
    name: str
    purpose: str
    steps: List[AlgorithmStep]
    complexity: Optional[str] = None

class ExpandedPhase3Output(BaseModel):
    """Enhanced schema with notation and patterns"""
    # Standard schema elements
    title: str
    description: str
    model_type: str
    rationale: str
    node_types: List[NodeType]
    edge_types: List[EdgeType]
    
    # New: Notation system
    notation_system: Optional[NotationSystem] = None
    
    # New: Pattern library
    pattern_library: Optional[List[PatternDefinition]] = None
    
    # New: Implementation algorithms
    algorithms: Optional[List[ImplementationAlgorithm]] = None
    
    # New: Domain applications
    domain_applications: Optional[Dict[str, List[str]]] = Field(
        description="Patterns/rules for specific applications",
        default=None
    )
    
    # Standard supporting elements
    property_definitions: Optional[Dict[str, str]] = None
    modifiers_supported: Optional[List[str]] = None
    truth_values_supported: Optional[List[str]] = None
    operators_supported: Optional[List[str]] = None

def phase3_generate_expanded_schema(
    phase1_output: Phase1Output, 
    phase2_output: Phase2Output,
    paper_text: str
) -> ExpandedPhase3Output:
    """Generate schema with expanded structure including notation and patterns"""
    
    # Include full vocabulary and paper text excerpt
    full_vocabulary_json = json.dumps([{
        "term": v.term,
        "definition": v.definition,
        "context": v.source_context,
        "category": v.theoretical_category
    } for v in phase1_output.vocabulary], indent=2)
    
    # Find methodology section if possible
    methodology_start = paper_text.lower().find("method")
    methodology_excerpt = paper_text[methodology_start:methodology_start+3000] if methodology_start > 0 else ""
    
    prompt = f"""
You are designing a comprehensive schema for an academic theory that includes ALL formal elements.

THEORY INFORMATION:
{phase1_output.citation}
{phase1_output.annotation}

COMPLETE VOCABULARY ({len(phase1_output.vocabulary)} terms):
{full_vocabulary_json}

METHODOLOGY EXCERPT:
{methodology_excerpt[:1500]}

PHASE 2 CLASSIFICATION SUMMARY:
Entities: {len(phase2_output.entities)}
Relationships: {len(phase2_output.relationships)}
Actions: {len(phase2_output.actions)}
Properties: {len(phase2_output.properties)}

Generate a comprehensive schema that includes:

1. Standard elements (node types, edge types, etc.)

2. NOTATION SYSTEM (if any):
   - Type codes (like C, P, M, B, T, J, R, S)
   - Argument role codes (like sa, pa, ma)
   - Special symbols (like +/B, :/J)
   - How notations combine (like P.sa)

3. PATTERN LIBRARY (if any):
   - Extraction patterns with syntax
   - What each pattern matches
   - Examples from the paper
   - Transformation rules

4. IMPLEMENTATION ALGORITHMS (if any):
   - Step-by-step procedures
   - Parsing stages
   - Search strategies
   - Scoring functions

5. DOMAIN APPLICATIONS (if mentioned):
   - Application-specific patterns
   - Domain rules

Look especially for:
- Notation explained in examples
- Pattern syntax in methodology
- Algorithms in implementation sections
- Special symbols in figures

IMPORTANT: Include ALL {len(phase1_output.vocabulary)} vocabulary terms in your schema.
"""

    response = client.beta.chat.completions.parse(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are an expert at extracting complete theoretical schemas including notation systems and patterns."},
            {"role": "user", "content": prompt}
        ],
        response_format=ExpandedPhase3Output
    )
    
    return response.choices[0].message.parsed

def convert_to_expanded_yaml(
    phase1: Phase1Output,
    phase2: Phase2Output, 
    phase3: ExpandedPhase3Output
) -> Dict[str, Any]:
    """Convert to YAML with expanded structure"""
    
    # Start with standard structure
    yaml_output = {
        "citation": phase1.citation,
        "annotation": phase1.annotation,
        "model_type": phase3.model_type,
        "rationale": phase3.rationale,
        "schema_blueprint": {
            "title": phase3.title,
            "description": phase3.description,
            "root_properties": {},
            "definitions": []
        }
    }
    
    # Add notation system if present
    if phase3.notation_system:
        yaml_output["notation_system"] = {
            "type_codes": phase3.notation_system.type_codes or {},
            "role_codes": phase3.notation_system.role_codes or {},
            "special_symbols": phase3.notation_system.special_symbols or {},
            "composite_notations": phase3.notation_system.composite_notations or []
        }
    
    # Add pattern library if present
    if phase3.pattern_library:
        yaml_output["pattern_library"] = [
            {
                "pattern": p.pattern,
                "description": p.description,
                "example": p.example,
                "action": p.action
            } for p in phase3.pattern_library
        ]
    
    # Add algorithms if present
    if phase3.algorithms:
        yaml_output["algorithms"] = []
        for algo in phase3.algorithms:
            algo_dict = {
                "name": algo.name,
                "purpose": algo.purpose,
                "steps": []
            }
            for step in algo.steps:
                step_dict = {
                    "step": step.step_number,
                    "description": step.description
                }
                if step.substeps:
                    step_dict["substeps"] = step.substeps
                algo_dict["steps"].append(step_dict)
            if algo.complexity:
                algo_dict["complexity"] = algo.complexity
            yaml_output["algorithms"].append(algo_dict)
    
    # Add domain applications if present
    if phase3.domain_applications:
        yaml_output["domain_applications"] = phase3.domain_applications
    
    # Add all vocabulary terms as definitions
    for term in phase1.vocabulary:
        # Find classification from phase 2
        term_type = "entity"  # default
        for t in phase2.entities:
            if t.term == term.term:
                term_type = t.subtype or "entity"
                break
        for t in phase2.relationships:
            if t.term == term.term:
                term_type = "relationship"
                break
        for t in phase2.actions:
            if t.term == term.term:
                term_type = "action"
                break
        
        definition = {
            "name": term.term,
            "category": term.theoretical_category or term_type,
            "description": term.definition
        }
        yaml_output["schema_blueprint"]["definitions"].append(definition)
    
    # Set root properties based on model type
    if phase3.model_type == "hypergraph":
        yaml_output["schema_blueprint"]["root_properties"] = {
            "vertices": {"description": "Nodes in the hypergraph", "item_type": "Entity"},
            "hyperedges": {"description": "N-ary relationships", "item_type": "Hyperedge"},
            "atoms": {"description": "Atomic semantic units", "item_type": "Atom"},
            "connectors": {"description": "Hyperedge connectors", "item_type": "Connector"}
        }
    
    return yaml_output

def process_paper_expanded(paper_path: str, output_path: str):
    """Process paper with expanded schema structure"""
    
    print("=== OPTION 1: EXPANDED SCHEMA STRUCTURE ===")
    print(f"Processing: {paper_path}")
    
    # Load paper text
    with open(paper_path, 'r', encoding='utf-8') as f:
        paper_text = f.read()
    
    # Phase 1: Extract vocabulary
    print("\nPhase 1: Extracting vocabulary...")
    phase1_output = phase1_extract_vocabulary(paper_text)
    print(f"  Extracted {len(phase1_output.vocabulary)} terms")
    
    # Phase 2: Classify vocabulary
    print("\nPhase 2: Classifying vocabulary...")
    phase2_output = phase2_classify_terms(phase1_output)
    
    # Phase 3: Generate expanded schema
    print("\nPhase 3: Generating expanded schema...")
    phase3_output = phase3_generate_expanded_schema(phase1_output, phase2_output, paper_text)
    
    # Check what was captured
    print(f"\nResults:")
    print(f"  Model type: {phase3_output.model_type}")
    print(f"  Definitions: {len(phase1_output.vocabulary)}")
    print(f"  Notation system: {'Yes' if phase3_output.notation_system else 'No'}")
    if phase3_output.notation_system:
        print(f"    - Type codes: {len(phase3_output.notation_system.type_codes or {})}")
        print(f"    - Role codes: {len(phase3_output.notation_system.role_codes or {})}")
        print(f"    - Special symbols: {len(phase3_output.notation_system.special_symbols or {})}")
    print(f"  Pattern library: {len(phase3_output.pattern_library or [])}")
    print(f"  Algorithms: {len(phase3_output.algorithms or [])}")
    print(f"  Domain applications: {len(phase3_output.domain_applications or {})}")
    
    # Convert and save
    yaml_data = convert_to_expanded_yaml(phase1_output, phase2_output, phase3_output)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(yaml_data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    
    print(f"\nSaved to: {output_path}")
    return yaml_data

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python multiphase_processor_expanded.py <paper.txt> <output.yml>")
        sys.exit(1)
    
    process_paper_expanded(sys.argv[1], sys.argv[2])