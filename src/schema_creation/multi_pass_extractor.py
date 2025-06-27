#!/usr/bin/env python3
"""
Multi-Pass Extraction System
Implements specialized extractors for complete theory capture
"""

import os
import sys
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

# Load environment
load_dotenv()
client = OpenAI()
MODEL = os.getenv("OPENAI_MODEL", "o3")

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import base components
from schema_creation.multiphase_processor_improved import (
    Phase1Output, Phase2Output,
    phase1_extract_vocabulary, phase2_classify_terms
)
from schema_creation.multiphase_processor_expanded import (
    phase3_generate_expanded_schema, convert_to_expanded_yaml
)

# Pass 1: Notation and Symbols
class NotationExtraction(BaseModel):
    """Extract all notation systems and symbols"""
    type_codes: Dict[str, str] = Field(default_factory=dict, description="All type codes with descriptions")
    argument_roles: Dict[str, str] = Field(default_factory=dict, description="All role codes with meanings")
    special_symbols: Dict[str, str] = Field(default_factory=dict, description="Special operators and symbols")
    composite_notations: List[str] = Field(default_factory=list, description="Examples of composite notations")
    notation_examples: List[Dict[str, str]] = Field(default_factory=list, description="Complete notation examples")

# Pass 2: Tables and Formal Rules
class FormalRulesExtraction(BaseModel):
    """Extract tables, rules, and formal specifications"""
    tables: List[Dict[str, Any]] = Field(default_factory=list, description="All tables from the paper")
    inference_rules: List[Dict[str, str]] = Field(default_factory=list, description="Formal inference rules")
    constraints: List[str] = Field(default_factory=list, description="Syntactic and semantic constraints")
    formal_definitions: Dict[str, Any] = Field(default_factory=dict, description="Formal mathematical definitions")

# Pass 3: Algorithms and Procedures
class AlgorithmExtraction(BaseModel):
    """Extract algorithms and computational procedures"""
    algorithms: List[Dict[str, Any]] = Field(default_factory=list, description="Step-by-step algorithms")
    pseudocode: List[Dict[str, str]] = Field(default_factory=list, description="Pseudocode blocks")
    computational_complexity: Dict[str, str] = Field(default_factory=dict, description="Complexity analysis")
    implementation_notes: List[str] = Field(default_factory=list, description="Implementation details")

# Pass 4: Metrics and Evaluation
class EvaluationExtraction(BaseModel):
    """Extract evaluation metrics and results"""
    metrics: List[Dict[str, str]] = Field(default_factory=list, description="Evaluation metrics used")
    benchmarks: List[Dict[str, Any]] = Field(default_factory=list, description="Benchmark results")
    baselines: List[str] = Field(default_factory=list, description="Baseline systems compared")
    performance_results: Dict[str, Any] = Field(default_factory=dict, description="Performance measurements")
    statistical_tests: List[Dict[str, str]] = Field(default_factory=list, description="Statistical analyses")

# Pass 5: Complete Examples
class ExampleExtraction(BaseModel):
    """Extract complete worked examples"""
    examples: List[Dict[str, Any]] = Field(default_factory=list, description="Complete examples from paper")
    walkthroughs: List[Dict[str, Any]] = Field(default_factory=list, description="Step-by-step walkthroughs")
    case_studies: List[Dict[str, Any]] = Field(default_factory=list, description="Detailed case studies")
    edge_cases: List[Dict[str, str]] = Field(default_factory=list, description="Edge cases and exceptions")

def extract_notation_and_symbols(paper_text: str) -> NotationExtraction:
    """Pass 1: Extract all notation systems and symbols"""
    
    prompt = f"""
You are an expert at extracting formal notation systems from academic papers.

Extract ALL notation systems and symbols from this paper:

1. Type codes: Look for a table or list showing type codes (single letters like C, P, M, B, T, J, R, S) with their meanings (e.g., "C - concept", "P - predicate", etc.)
2. Argument role codes: Look for a table or list showing argument roles (like s, p, a, c, o, i, t, j, x, r) with their meanings (e.g., "s - active subject", "p - passive subject")
3. Special symbols and operators: Extract symbols like +/B (compound builder), :/J (implicit conjunction), and pattern matching symbols
4. Composite notations: Examples combining types and roles (like P.sa, B.ma, P.sio)
5. Complete notation examples with their meanings

Look especially in:
- Type system sections
- Methodology sections
- Examples and figures
- Tables
- Footnotes

PAPER TEXT:
{paper_text[:30000]}

Be EXTREMELY thorough - capture every notation detail.

Return as JSON with these fields:
- type_codes: object mapping codes to descriptions
- argument_roles: object mapping roles to meanings
- special_symbols: object mapping symbols to uses
- composite_notations: array of composite notation examples
- notation_examples: array of objects with notation examples
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Extract all formal notations and symbols. Return valid JSON."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    result = json.loads(response.choices[0].message.content)
    # Debug print
    if "type_codes" not in result or len(result.get("type_codes", {})) == 0:
        print(f"[DEBUG] Notation extraction result: {json.dumps(result, indent=2)[:500]}...")
    return NotationExtraction(**result)

def extract_tables_and_rules(paper_text: str) -> FormalRulesExtraction:
    """Pass 2: Extract all tables and formal rules"""
    
    prompt = f"""
You are an expert at extracting formal rules and tables from academic papers.

Extract ALL tables and formal rules:

1. Tables: Look for "Table 1", "Table 2", etc. Extract the COMPLETE table including:
   - Table title/caption
   - Column headers
   - ALL rows of data
   - Any footnotes
2. Inference rules: Look for type inference rules (often with arrows like →)
3. Constraints: Any syntactic or semantic constraints mentioned
4. Formal definitions: Mathematical definitions using set notation

Look for:
- Table 1, Table 2, etc.
- Rules in any format
- Constraints listed anywhere
- Mathematical definitions

PAPER TEXT:
{paper_text[:30000]}

Preserve exact table structure and rule formulations.

Return as JSON with these fields:
- tables: array of table objects (each with title, headers, rows)
- inference_rules: array of rule objects (each with name, formula/description)
- constraints: array of constraint strings
- formal_definitions: object mapping terms to definitions
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Extract all tables and formal rules exactly. Return valid JSON."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    result = json.loads(response.choices[0].message.content)
    return FormalRulesExtraction(**result)

def extract_algorithms(paper_text: str) -> AlgorithmExtraction:
    """Pass 3: Extract all algorithms and procedures"""
    
    prompt = f"""
You are an expert at extracting algorithms from academic papers.

Extract ALL algorithms and computational procedures:

1. Named algorithms (with steps)
2. Pseudocode blocks
3. Complexity analysis
4. Implementation details

Look for:
- Algorithm 1, Algorithm 2, etc.
- Function definitions
- Step-by-step procedures
- Complexity statements (O(n), etc.)

PAPER TEXT:
{paper_text[20000:40000]}

Include complete algorithm specifications.

Return as JSON with these fields:
- algorithms: array of algorithm objects (each with name, steps, description)
- pseudocode: array of pseudocode objects (each with name, code)
- computational_complexity: object mapping algorithm names to complexity
- implementation_notes: array of implementation detail strings
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Extract all algorithms and procedures. Return valid JSON."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    result = json.loads(response.choices[0].message.content)
    return AlgorithmExtraction(**result)

def extract_evaluation_metrics(paper_text: str) -> EvaluationExtraction:
    """Pass 4: Extract evaluation metrics and results"""
    
    prompt = f"""
You are an expert at extracting evaluation metrics from academic papers.

Extract ALL evaluation information:

1. Metrics (precision, recall, F1, etc.)
2. Benchmark results (with numbers)
3. Baseline comparisons
4. Performance measurements
5. Statistical tests

Look in:
- Evaluation sections
- Results sections
- Tables with numbers
- Comparison discussions

PAPER TEXT:
{paper_text[30000:50000]}

Include specific numbers and test conditions.

Return as JSON with these fields:
- metrics: array of metric objects (each with name, description)
- benchmarks: array of benchmark objects (each with name, dataset, results)
- baselines: array of baseline system names
- performance_results: object mapping metrics to values
- statistical_tests: array of test objects (each with test_name, results)
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Extract all evaluation metrics and results. Return valid JSON."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    result = json.loads(response.choices[0].message.content)
    return EvaluationExtraction(**result)

def extract_complete_examples(paper_text: str) -> ExampleExtraction:
    """Pass 5: Extract complete worked examples"""
    
    prompt = f"""
You are an expert at extracting examples from academic papers.

Extract ALL complete examples:

1. Worked examples (input → process → output)
2. Step-by-step walkthroughs
3. Case studies
4. Edge cases and exceptions

Look for:
- "For example"
- "Consider"
- Example sections
- Figures with examples
- Case study sections

PAPER TEXT:
{paper_text[10000:30000]}

Include complete examples with all steps.

Return as JSON with these fields:
- examples: array of example objects (each with description, input, process, output)
- walkthroughs: array of walkthrough objects (each with title, steps as array of strings)
- case_studies: array of case study objects (each with name, description, results)
- edge_cases: array of edge case objects (each with condition, behavior)
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Extract all complete examples. Return valid JSON."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    result = json.loads(response.choices[0].message.content)
    return ExampleExtraction(**result)

def merge_extractions(
    phase1: Phase1Output,
    phase2: Phase2Output,
    phase3: Any,
    notation: NotationExtraction,
    rules: FormalRulesExtraction,
    algorithms: AlgorithmExtraction,
    evaluation: EvaluationExtraction,
    examples: ExampleExtraction
) -> Dict[str, Any]:
    """Merge all extraction passes into comprehensive schema"""
    
    # Start with Phase 3 expanded schema
    schema = phase3.model_dump() if hasattr(phase3, 'model_dump') else phase3
    
    # Add detailed notation (merging with any existing)
    if notation:
        schema['notation_system'] = {
            'type_codes': notation.type_codes,
            'argument_roles': notation.argument_roles,
            'special_symbols': notation.special_symbols,
            'composite_notations': notation.composite_notations,
            'examples': notation.notation_examples
        }
    
    # Add formal rules
    if rules:
        schema['formal_rules'] = {
            'tables': rules.tables,
            'inference_rules': rules.inference_rules,
            'constraints': rules.constraints,
            'formal_definitions': rules.formal_definitions
        }
    
    # Add algorithms
    if algorithms:
        schema['algorithms'] = algorithms.algorithms
        schema['implementation'] = {
            'pseudocode': algorithms.pseudocode,
            'complexity': algorithms.computational_complexity,
            'notes': algorithms.implementation_notes
        }
    
    # Add evaluation
    if evaluation:
        schema['evaluation'] = {
            'metrics': evaluation.metrics,
            'benchmarks': evaluation.benchmarks,
            'baselines': evaluation.baselines,
            'results': evaluation.performance_results,
            'statistical_tests': evaluation.statistical_tests
        }
    
    # Add examples
    if examples:
        schema['complete_examples'] = examples.examples
        schema['walkthroughs'] = examples.walkthroughs
        schema['case_studies'] = examples.case_studies
        schema['edge_cases'] = examples.edge_cases
    
    return schema

def process_paper_multi_pass(paper_path: str, output_path: str):
    """Process paper with comprehensive multi-pass extraction"""
    
    print("=== MULTI-PASS EXTRACTION SYSTEM ===")
    print(f"Processing: {paper_path}")
    
    # Load paper
    with open(paper_path, 'r', encoding='utf-8') as f:
        paper_text = f.read()
    
    # Standard 3 phases
    print("\n[Phase 1] Extracting vocabulary...")
    phase1 = phase1_extract_vocabulary(paper_text)
    print(f"  → {len(phase1.vocabulary)} terms extracted")
    
    print("\n[Phase 2] Classifying vocabulary...")
    phase2 = phase2_classify_terms(phase1)
    
    print("\n[Phase 3] Generating base schema...")
    phase3 = phase3_generate_expanded_schema(phase1, phase2, paper_text)
    
    # Multi-pass extraction
    print("\n[Pass 1] Extracting notation and symbols...")
    notation = extract_notation_and_symbols(paper_text)
    print(f"  → {len(notation.type_codes)} type codes")
    print(f"  → {len(notation.argument_roles)} role codes") 
    print(f"  → {len(notation.special_symbols)} special symbols")
    if len(notation.type_codes) == 0:
        print(f"  [DEBUG] Raw notation result: {notation}")
    
    print("\n[Pass 2] Extracting tables and rules...")
    rules = extract_tables_and_rules(paper_text)
    print(f"  → {len(rules.tables)} tables")
    print(f"  → {len(rules.inference_rules)} inference rules")
    
    print("\n[Pass 3] Extracting algorithms...")
    algorithms = extract_algorithms(paper_text)
    print(f"  → {len(algorithms.algorithms)} algorithms")
    print(f"  → {len(algorithms.pseudocode)} pseudocode blocks")
    
    print("\n[Pass 4] Extracting evaluation metrics...")
    evaluation = extract_evaluation_metrics(paper_text)
    print(f"  → {len(evaluation.metrics)} metrics")
    print(f"  → {len(evaluation.benchmarks)} benchmarks")
    
    print("\n[Pass 5] Extracting complete examples...")
    examples = extract_complete_examples(paper_text)
    print(f"  → {len(examples.examples)} examples")
    print(f"  → {len(examples.walkthroughs)} walkthroughs")
    
    # Merge all extractions
    print("\n[Merge] Combining all extractions...")
    final_schema = merge_extractions(
        phase1, phase2, phase3,
        notation, rules, algorithms, evaluation, examples
    )
    
    # Convert to basic YAML format first
    yaml_output = {
        "citation": phase1.citation,
        "annotation": phase1.annotation,
        "model_type": getattr(phase3, 'model_type', 'hypergraph'),
        "rationale": getattr(phase3, 'rationale', 'Multi-pass extraction for complete capture'),
        "schema_blueprint": {
            "title": getattr(phase3, 'title', 'Semantic Hypergraph'),
            "description": getattr(phase3, 'description', 'Complete semantic hypergraph extraction'),
            "root_properties": getattr(phase3, 'root_properties', {}),
            "definitions": []
        }
    }
    
    # Add definitions from phase3
    if hasattr(phase3, 'definitions') and phase3.definitions:
        for term in phase3.definitions:
            yaml_output["schema_blueprint"]["definitions"].append({
                "term": term.term,
                "type": term.term_type,
                "definition": term.definition,
                "constraints": getattr(term, 'constraints', {}),
                "relationships": getattr(term, 'relationships', {})
            })
    
    # Add multi-pass results
    yaml_output.update({
        'multi_pass_extraction': {
            'timestamp': datetime.now().isoformat(),
            'passes_completed': 5,
            'notation_system': final_schema.get('notation_system', {}),
            'formal_rules': final_schema.get('formal_rules', {}),
            'algorithms': final_schema.get('algorithms', []),
            'implementation': final_schema.get('implementation', {}),
            'evaluation': final_schema.get('evaluation', {}),
            'complete_examples': final_schema.get('complete_examples', [])
        }
    })
    
    # Save result
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(yaml_output, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    
    print(f"\n✓ Multi-pass extraction complete!")
    print(f"✓ Saved to: {output_path}")
    
    # Summary statistics
    print("\n=== EXTRACTION SUMMARY ===")
    print(f"Vocabulary terms: {len(phase1.vocabulary)}")
    print(f"Type codes: {len(notation.type_codes)}")
    print(f"Role codes: {len(notation.argument_roles)}")
    print(f"Tables extracted: {len(rules.tables)}")
    print(f"Algorithms: {len(algorithms.algorithms)}")
    print(f"Evaluation metrics: {len(evaluation.metrics)}")
    print(f"Complete examples: {len(examples.examples)}")
    
    return yaml_output

def main():
    if len(sys.argv) != 3:
        print("Usage: python multi_pass_extractor.py <paper.txt> <output.yml>")
        sys.exit(1)
    
    paper_path = sys.argv[1]
    output_path = sys.argv[2]
    
    if not os.path.exists(paper_path):
        print(f"Error: Paper not found: {paper_path}")
        sys.exit(1)
    
    process_paper_multi_pass(paper_path, output_path)

if __name__ == "__main__":
    main()