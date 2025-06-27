#!/usr/bin/env python3
"""
Test enhanced extraction with notation and pattern focus
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
import yaml
from openai import OpenAI
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()
client = OpenAI()

class NotationSystem(BaseModel):
    """Notation system extraction"""
    argument_roles: Dict[str, str] = Field(
        default_factory=dict,
        description="Role codes and meanings (e.g., 'sa': 'subject-argument')"
    )
    special_symbols: Dict[str, str] = Field(
        default_factory=dict,
        description="Special operators and symbols (e.g., '+/B': 'builder conjunction')"
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

class EnhancedExtractionResult(BaseModel):
    """Enhanced extraction focusing on notation and patterns"""
    notation_system: NotationSystem
    pattern_language: PatternLanguage
    type_system: Dict[str, Any] = Field(description="Complete type system with all types and their properties")
    examples: List[Dict[str, str]] = Field(description="Examples from the paper showing notation usage")

def extract_notation_focused(paper_path: str) -> EnhancedExtractionResult:
    """Extract with focus on notation systems and patterns"""
    
    # Load paper text
    with open(paper_path, 'r', encoding='utf-8') as f:
        paper_text = f.read()
    
    prompt = f"""
You are an expert in formal notation systems and theoretical frameworks.

Analyze this academic paper and extract:

1. **NOTATION SYSTEMS** (CRITICAL):
   - Look for argument role codes like 'P.sa', 'B.ma', 'P.soa' etc.
   - Find ALL special symbols: +/B (builder), :/J (conjunction), * (starred atoms), etc.
   - Identify what each position means in multi-part notations
   - Look especially in examples and methodology sections

2. **PATTERN LANGUAGE**:
   - Syntactic patterns for extraction (with specific examples from paper)
   - Transformation rules (e.g., "X of Y" becomes what structure?)
   - Rules for inferring types from context
   - Any regular expressions or pattern matching descriptions

3. **COMPLETE TYPE SYSTEM**:
   - ALL types mentioned (C, P, M, B, T, J, R, S, etc.)
   - What each type represents
   - Subtypes and hierarchies
   - Constraints on type usage

4. **EXAMPLES**:
   - Extract 3-5 examples from the paper showing the notation in use
   - Include the original text and its representation

Look especially in:
- Methodology sections
- Examples and figures
- Tables showing notations
- Footnotes and appendices

PAPER TEXT (focusing on methodology and examples):
{paper_text[10000:25000]}  # Middle section often has methodology

BE EXTREMELY THOROUGH - notation details are often subtle and easy to miss.
"""

    try:
        response = client.beta.chat.completions.parse(
            model="o3-mini",
            messages=[
                {"role": "system", "content": "You are an expert at extracting formal notation systems from academic papers."},
                {"role": "user", "content": prompt}
            ],
            response_format=EnhancedExtractionResult
        )
        
        return response.choices[0].message.parsed
        
    except Exception as e:
        print(f"Error in extraction: {e}")
        raise

def main():
    paper_path = "/home/brian/lit_review/data/papers/computational_linguistics/menezes_roth_semantic_hypergraphs.txt"
    output_dir = Path("/home/brian/lit_review/results/semantic_hypergraph/enhanced_extraction")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Extracting notation systems and patterns from Semantic Hypergraph paper...")
    result = extract_notation_focused(paper_path)
    
    # Save results
    output_path = output_dir / "sh_notation_extraction.yml"
    with open(output_path, 'w') as f:
        yaml.dump(result.model_dump(), f, allow_unicode=True, sort_keys=False)
    
    print(f"\nExtraction complete! Saved to: {output_path}")
    
    # Print summary
    print("\n=== NOTATION SYSTEM ===")
    print(f"Argument roles found: {len(result.notation_system.argument_roles)}")
    for code, meaning in list(result.notation_system.argument_roles.items())[:5]:
        print(f"  {code}: {meaning}")
    
    print(f"\nSpecial symbols found: {len(result.notation_system.special_symbols)}")
    for symbol, meaning in result.notation_system.special_symbols.items():
        print(f"  {symbol}: {meaning}")
    
    print(f"\n=== PATTERN LANGUAGE ===")
    print(f"Syntactic patterns: {len(result.pattern_language.syntactic_patterns)}")
    print(f"Transformation rules: {len(result.pattern_language.transformation_rules)}")
    
    print(f"\n=== TYPE SYSTEM ===")
    print(f"Types found: {len(result.type_system)}")
    for type_name, details in list(result.type_system.items())[:5]:
        print(f"  {type_name}: {details}")

if __name__ == "__main__":
    main()