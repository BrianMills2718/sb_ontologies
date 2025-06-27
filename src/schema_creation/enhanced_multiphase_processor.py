#!/usr/bin/env python3
"""
Enhanced multiphase processor with additional notation extraction phase

This processor adds a Phase 3b specifically for extracting notation systems,
pattern languages, and implementation details that are often missed in the
standard 3-phase extraction.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
import yaml
from openai import OpenAI
from datetime import datetime
import json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the standard processor components
from schema_creation.multiphase_processor_improved import (
    Phase1Result, Phase2Result, Phase3Result, load_text_file,
    extract_vocabulary, classify_vocabulary, generate_schema
)
from schema_creation.prompt_loader import get_phase1_prompt, get_phase2_prompt, get_phase3_prompt

# Initialize OpenAI client
client = OpenAI()

class NotationSystem(BaseModel):
    """Notation system extraction"""
    argument_roles: Dict[str, str] = Field(
        default_factory=dict,
        description="Role codes and meanings (e.g., 'sa': 'subject-argument', 'soa': 'subject-object-action')"
    )
    special_symbols: Dict[str, str] = Field(
        default_factory=dict,
        description="Special operators and symbols (e.g., '+/B': 'builder conjunction', ':/J': 'join')"
    )
    position_meanings: Dict[str, str] = Field(
        default_factory=dict,
        description="Position-based semantics in notations"
    )
    
class PatternLanguage(BaseModel):
    """Pattern extraction rules"""
    syntactic_patterns: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Pattern matching rules with examples"
    )
    transformation_rules: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Transformation rules (e.g., 'X of Y' → 'Y has X')"
    )
    type_inference_rules: List[str] = Field(
        default_factory=list,
        description="Rules for inferring types from context"
    )
    
class ImplementationDetails(BaseModel):
    """Implementation specifics"""
    algorithms: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Step-by-step algorithms"
    )
    edge_cases: List[str] = Field(
        default_factory=list,
        description="Special cases and exceptions"
    )
    validation_rules: List[str] = Field(
        default_factory=list,
        description="Constraints and validation logic"
    )

class Phase3bResult(BaseModel):
    """Enhanced extraction for notation and patterns"""
    notation_system: NotationSystem
    pattern_language: PatternLanguage
    implementation_details: ImplementationDetails
    extracted_at: str

def extract_notation_and_patterns(
    paper_text: str,
    phase2_result: Phase2Result
) -> Phase3bResult:
    """Extract notation systems and pattern languages"""
    
    prompt = f"""
You are an expert in formal notation systems and pattern languages.

Given this academic paper and its classified vocabulary, extract:

1. **Notation Systems**:
   - Look for role codes like 'P.sa' (predicate with subject-argument)
   - Find special symbols (+/B, :/J, *, etc.) and their meanings
   - Identify position-based semantics in multi-part notations
   - Look in methodology sections, examples, and figures

2. **Pattern Language**:
   - Syntactic patterns used for extraction (with examples from the paper)
   - Transformation rules (how text patterns map to formal structures)
   - Type inference rules (how types are determined from context)
   - Look for regular expressions, matching rules, or pattern descriptions

3. **Implementation Details**:
   - Step-by-step algorithms (even if informal)
   - Edge cases mentioned
   - Validation rules or constraints
   - Ordering requirements

PAPER TEXT:
{paper_text[:8000]}

CLASSIFIED VOCABULARY:
Core Constructs: {', '.join([f"{c['term']} ({c['type']})" for c in phase2_result.core_constructs[:10]])}

Please extract all notation systems, patterns, and implementation details.
Be extremely thorough - these details are often in examples or footnotes.
"""

    try:
        response = client.beta.chat.completions.parse(
            model="o3-mini",
            messages=[
                {"role": "system", "content": "Extract notation systems and patterns from academic papers."},
                {"role": "user", "content": prompt}
            ],
            response_format=Phase3bResult,
            temperature=0.2
        )
        
        result = response.choices[0].message.parsed
        result.extracted_at = datetime.now().isoformat()
        return result
        
    except Exception as e:
        print(f"Error in phase 3b extraction: {e}")
        # Return empty result on error
        return Phase3bResult(
            notation_system=NotationSystem(),
            pattern_language=PatternLanguage(),
            implementation_details=ImplementationDetails(),
            extracted_at=datetime.now().isoformat()
        )

def generate_enhanced_schema(
    phase2_result: Phase2Result,
    phase3b_result: Phase3bResult,
    paper_text: str
) -> Dict[str, Any]:
    """Generate schema with notation and pattern information"""
    
    # Build enhanced prompt with notation details
    notation_section = ""
    if phase3b_result.notation_system.argument_roles:
        notation_section += "\nARGUMENT ROLES:\n"
        for code, meaning in phase3b_result.notation_system.argument_roles.items():
            notation_section += f"- {code}: {meaning}\n"
    
    if phase3b_result.notation_system.special_symbols:
        notation_section += "\nSPECIAL SYMBOLS:\n"
        for symbol, meaning in phase3b_result.notation_system.special_symbols.items():
            notation_section += f"- {symbol}: {meaning}\n"
    
    pattern_section = ""
    if phase3b_result.pattern_language.syntactic_patterns:
        pattern_section += "\nEXTRACTION PATTERNS:\n"
        for pattern in phase3b_result.pattern_language.syntactic_patterns:
            pattern_section += f"- {pattern}\n"
    
    # Include notation and patterns in schema generation
    enhanced_prompt = get_phase3_prompt() + f"""

ADDITIONAL NOTATION AND PATTERN INFORMATION:
{notation_section}
{pattern_section}

Please ensure the schema includes:
1. Notation systems as part of type definitions
2. Pattern matching rules in extraction methods
3. Implementation algorithms where applicable
"""

    # Continue with standard schema generation but with enhanced prompt
    # ... rest of schema generation logic ...
    
    return schema

def process_paper_enhanced(paper_path: str, output_dir: str = "schemas"):
    """Process paper with enhanced extraction"""
    
    print(f"Processing paper: {paper_path}")
    
    # Phase 1: Extract vocabulary
    paper_text = load_text_file(paper_path)
    phase1_result = extract_vocabulary(paper_text)
    
    # Phase 2: Classify vocabulary
    phase2_result = classify_vocabulary(phase1_result, paper_text)
    
    # Phase 3b: Extract notation and patterns
    print("Phase 3b: Extracting notation systems and patterns...")
    phase3b_result = extract_notation_and_patterns(paper_text, phase2_result)
    
    # Phase 3: Generate enhanced schema
    print("Phase 3: Generating enhanced schema...")
    schema = generate_enhanced_schema(phase2_result, phase3b_result, paper_text)
    
    # Save results including notation extraction
    theory_name = schema.get('title', 'unknown').lower().replace(' ', '_')
    output_path = Path(output_dir) / theory_name
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Save phase 3b results
    with open(output_path / f"{theory_name}_notation.yml", 'w') as f:
        yaml.dump(phase3b_result.model_dump(), f, allow_unicode=True, sort_keys=False)
    
    # Save enhanced schema
    with open(output_path / f"{theory_name}_enhanced.yml", 'w') as f:
        yaml.dump(schema, f, allow_unicode=True, sort_keys=False)
    
    print(f"Enhanced schema saved to: {output_path}")
    return schema

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python enhanced_multiphase_processor.py <paper.txt>")
        sys.exit(1)
    
    paper_path = sys.argv[1]
    if not os.path.exists(paper_path):
        print(f"Error: File not found: {paper_path}")
        sys.exit(1)
    
    schema = process_paper_enhanced(paper_path)
    print(f"\nGenerated enhanced schema: {schema.get('title', 'Unknown')}")