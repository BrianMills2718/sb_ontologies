#!/usr/bin/env python3
"""
Implementation Extractor - Option 2
Extracts notation, patterns, and algorithms as a separate implementation specification
"""

import os
import sys
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

class NotationSpec(BaseModel):
    """Complete notation specification"""
    type_system: Dict[str, str] = Field(description="All type codes with descriptions")
    argument_roles: Dict[str, str] = Field(description="All role codes with meanings")
    special_operators: Dict[str, str] = Field(description="Special symbols and operators")
    notation_examples: List[str] = Field(description="Complete notation examples from paper")
    combination_rules: List[str] = Field(description="How notations combine (e.g., TYPE.role)")

class PatternSpec(BaseModel):
    """Pattern matching specification"""
    pattern_syntax: str = Field(description="Description of pattern language syntax")
    patterns: List[Dict[str, str]] = Field(description="All patterns with syntax, purpose, examples")
    wildcards: Dict[str, str] = Field(description="Wildcard symbols and meanings")
    quantifiers: Dict[str, str] = Field(description="Quantifier symbols and meanings")
    transformation_rules: List[Dict[str, str]] = Field(description="Pattern transformation rules")

class AlgorithmSpec(BaseModel):
    """Algorithm specification"""
    name: str
    purpose: str
    input: str
    output: str
    steps: List[str]
    complexity: Optional[str] = None
    implementation_notes: Optional[str] = None

class EvaluationSpec(BaseModel):
    """Evaluation metrics and methods"""
    metrics: List[str] = Field(description="Metrics used (precision, recall, etc.)")
    benchmarks: List[str] = Field(description="Benchmarks or datasets used")
    baselines: List[str] = Field(description="Baseline systems compared against")
    results: Optional[List[str]] = Field(description="Key results if provided")

class ImplementationSpecification(BaseModel):
    """Complete implementation specification separate from theoretical schema"""
    theory_name: str
    notation: NotationSpec
    patterns: PatternSpec
    algorithms: List[AlgorithmSpec]
    evaluation: Optional[EvaluationSpec] = None
    tools: Optional[List[str]] = Field(description="Software tools/libraries mentioned")
    examples: List[Dict[str, str]] = Field(description="Complete worked examples from paper")

def extract_implementation_spec(
    paper_path: str,
    schema_path: Optional[str] = None
) -> ImplementationSpecification:
    """Extract implementation details as separate specification"""
    
    # Load paper text
    with open(paper_path, 'r', encoding='utf-8') as f:
        paper_text = f.read()
    
    # Load schema if provided for context
    schema_context = ""
    if schema_path and os.path.exists(schema_path):
        with open(schema_path, 'r') as f:
            schema = yaml.safe_load(f)
            schema_context = f"\nTHEORY CONTEXT:\n{schema.get('annotation', '')}\n"
    
    prompt = f"""
Extract the complete IMPLEMENTATION SPECIFICATION from this academic paper.
This should include all notation systems, pattern languages, algorithms, and evaluation details.
{schema_context}

Focus on extracting:

1. NOTATION SPECIFICATION:
   - ALL type codes (C, P, M, B, T, J, R, S, etc.) with exact meanings
   - ALL argument role codes (sa, pa, ma, etc.) with exact meanings  
   - ALL special symbols (+/B, :/J, *, etc.) with exact meanings
   - Examples showing complete notations (e.g., "applaud/P.sa")
   - Rules for combining notations

2. PATTERN SPECIFICATION:
   - Complete pattern syntax description
   - ALL patterns mentioned with:
     * Exact syntax
     * What it matches
     * Example text
     * Result/transformation
   - Wildcard meanings
   - Quantifier meanings
   - Transformation rules

3. ALGORITHMS:
   - ALL algorithms/procedures mentioned
   - Step-by-step details
   - Input/output specifications
   - Complexity if mentioned

4. EVALUATION:
   - Metrics used
   - Benchmarks/datasets
   - Baseline comparisons
   - Results

5. COMPLETE EXAMPLES:
   - Full worked examples from the paper
   - Input text → processing → output

Look especially in:
- Methodology sections
- Implementation sections
- Examples and figures
- Appendices
- Tables

PAPER TEXT:
{paper_text[:15000]}

[CONTINUATION IF NEEDED...]
{paper_text[15000:25000] if len(paper_text) > 15000 else ""}

Extract EVERYTHING related to implementation, notation, and patterns.
Be extremely thorough - these details are often in examples, figures, or footnotes.
"""

    response = client.beta.chat.completions.parse(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are an expert at extracting complete implementation specifications from academic papers."},
            {"role": "user", "content": prompt}
        ],
        response_format=ImplementationSpecification
    )
    
    return response.choices[0].message.parsed

def save_implementation_spec(spec: ImplementationSpecification, output_path: str):
    """Save implementation specification to YAML"""
    
    # Convert to clean YAML structure
    yaml_output = {
        "implementation_specification": {
            "theory_name": spec.theory_name,
            "notation": {
                "type_system": spec.notation.type_system,
                "argument_roles": spec.notation.argument_roles,
                "special_operators": spec.notation.special_operators,
                "notation_examples": spec.notation.notation_examples,
                "combination_rules": spec.notation.combination_rules
            },
            "patterns": {
                "syntax_description": spec.patterns.pattern_syntax,
                "pattern_definitions": spec.patterns.patterns,
                "wildcards": spec.patterns.wildcards,
                "quantifiers": spec.patterns.quantifiers,
                "transformations": spec.patterns.transformation_rules
            },
            "algorithms": [
                {
                    "name": algo.name,
                    "purpose": algo.purpose,
                    "input": algo.input,
                    "output": algo.output,
                    "steps": algo.steps,
                    "complexity": algo.complexity,
                    "notes": algo.implementation_notes
                } for algo in spec.algorithms
            ],
            "examples": spec.examples
        }
    }
    
    if spec.evaluation:
        yaml_output["implementation_specification"]["evaluation"] = {
            "metrics": spec.evaluation.metrics,
            "benchmarks": spec.evaluation.benchmarks,
            "baselines": spec.evaluation.baselines,
            "results": spec.evaluation.results
        }
    
    if spec.tools:
        yaml_output["implementation_specification"]["tools"] = spec.tools
    
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(yaml_output, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

def process_implementation_extraction(
    paper_path: str, 
    output_path: str,
    schema_path: Optional[str] = None
):
    """Process paper to extract implementation specification"""
    
    print("=== OPTION 2: SEPARATE IMPLEMENTATION EXTRACTION ===")
    print(f"Processing: {paper_path}")
    if schema_path:
        print(f"Using schema context: {schema_path}")
    
    print("\nExtracting implementation specification...")
    spec = extract_implementation_spec(paper_path, schema_path)
    
    print(f"\nResults:")
    print(f"  Theory: {spec.theory_name}")
    print(f"  Type codes: {len(spec.notation.type_system)}")
    print(f"  Argument roles: {len(spec.notation.argument_roles)}")
    print(f"  Special operators: {len(spec.notation.special_operators)}")
    print(f"  Patterns: {len(spec.patterns.patterns)}")
    print(f"  Algorithms: {len(spec.algorithms)}")
    print(f"  Examples: {len(spec.examples)}")
    if spec.evaluation:
        print(f"  Evaluation metrics: {len(spec.evaluation.metrics)}")
    
    # Show sample notation
    if spec.notation.argument_roles:
        print("\nSample argument roles:")
        for code, meaning in list(spec.notation.argument_roles.items())[:3]:
            print(f"    {code}: {meaning}")
    
    # Save specification
    save_implementation_spec(spec, output_path)
    print(f"\nSaved to: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python implementation_extractor.py <paper.txt> <output.yml> [schema.yml]")
        sys.exit(1)
    
    schema_path = sys.argv[3] if len(sys.argv) > 3 else None
    process_implementation_extraction(sys.argv[1], sys.argv[2], schema_path)