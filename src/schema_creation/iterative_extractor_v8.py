#!/usr/bin/env python3
"""
Iterative self-correcting extraction for meta_schema_8
Continues refining until optimal extraction is achieved
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from openai import OpenAI
from dotenv import load_dotenv
import time

load_dotenv()

class IterativeExtractorV8:
    """Iterative extraction with self-correction loops"""
    
    def __init__(self):
        self.client = OpenAI()
        self.max_iterations = 5
        self.max_tokens = 100000  # o1 model limit
        
    def initial_extraction(self, content: str) -> Dict[str, Any]:
        """First attempt at full extraction"""
        
        with open("/home/brian/lit_review/prompt_2025.06280355.txt", 'r') as f:
            base_prompt = f.read()
            
        with open("/home/brian/lit_review/meta_schema_8.json", 'r') as f:
            schema_def = json.dumps(json.load(f), indent=2)
        
        prompt = f"""{base_prompt}

META-SCHEMA STRUCTURE:
{schema_def}

CRITICAL REQUIREMENTS:
1. Extract EVERYTHING - tables, lists, taxonomies are core theory components
2. Follow the meta_schema_8 structure EXACTLY
3. Properly categorize: entities vs connections vs properties vs modifiers
4. Include ALL formulas, metrics, and processes

Extract the complete theory from the provided paper."""

        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Extract theory from:\n\n{content}"}
        ]
        
        print("Initial extraction attempt...")
        response = self.client.chat.completions.create(
            model="o1",
            messages=messages,
            max_completion_tokens=self.max_tokens
        )
        
        return self._parse_json_response(response.choices[0].message.content)
    
    def analyze_extraction(self, extraction: Dict, paper_content: str) -> Dict[str, Any]:
        """Analyze extraction for completeness and correctness"""
        
        prompt_template = """You are a meticulous theory extraction validator. Analyze this extraction for issues.

EXTRACTION TO VALIDATE:
```json
{extraction}
```

ORIGINAL PAPER (first 40k chars):
{content}

VALIDATION TASKS:
1. Check if extraction follows meta_schema_8 structure correctly
2. Look for tables/lists in the paper - are ALL items extracted?
3. Count items in each category - do the numbers seem right?
4. Check for missing components mentioned in the paper
5. Verify proper categorization (entities vs connections vs properties vs modifiers)
6. Look for key innovations/contributions mentioned - are they captured?

BE EXTREMELY CRITICAL. Look for:
- Missing vocabulary (especially from tables)
- Wrong categorization
- Missing sections (truth values, formulas, etc.)
- Structural issues

Output as JSON with this structure:
{{
  "structural_issues": ["list of schema structure problems"],
  "missing_components": [
    {{
      "component": "what's missing",
      "evidence": "quote from paper showing it exists",
      "category": "entities|connections|properties|modifiers|other"
    }}
  ],
  "categorization_errors": [
    {{
      "item": "misplaced item",
      "current_category": "where it is",
      "correct_category": "where it should be"
    }}
  ],
  "completeness_score": 0-100,
  "is_optimal": false,
  "improvement_instructions": "specific instructions for fixing issues"
}}"""

        extraction_str = json.dumps(extraction, indent=2)
        if len(extraction_str) > 30000:
            extraction_str = extraction_str[:30000] + "\n... (truncated)"

        messages = [
            {"role": "system", "content": prompt_template.format(
                extraction=extraction_str,
                content=paper_content[:40000]
            )},
            {"role": "user", "content": "Validate this extraction thoroughly."}
        ]
        
        print("Analyzing extraction for issues...")
        response = self.client.chat.completions.create(
            model="o1",
            messages=messages,
            max_completion_tokens=50000
        )
        
        return self._parse_json_response(response.choices[0].message.content)
    
    def improve_extraction(self, current_extraction: Dict, analysis: Dict, paper_content: str) -> Dict[str, Any]:
        """Improve extraction based on analysis"""
        
        prompt_template = """Fix the issues identified in this extraction.

CURRENT EXTRACTION:
```json
{extraction}
```

ISSUES FOUND:
```json
{analysis}
```

ORIGINAL PAPER (relevant sections):
{content}

INSTRUCTIONS:
{instructions}

Produce a COMPLETE corrected extraction following meta_schema_8 structure.
Include ALL components from the current extraction PLUS fixes for identified issues.

CRITICAL:
- Don't just add missing items - ensure proper categorization
- Maintain all correct parts from current extraction
- Follow meta_schema_8 structure exactly
- Truth values might be properties or modifiers - choose appropriately

Output the complete corrected theory extraction as JSON."""

        # Truncate if needed
        extraction_str = json.dumps(current_extraction, indent=2)
        if len(extraction_str) > 25000:
            extraction_str = extraction_str[:25000] + "\n... (truncated)"
            
        analysis_str = json.dumps(analysis, indent=2)
        instructions = analysis.get('improvement_instructions', 'Fix all identified issues')

        messages = [
            {"role": "system", "content": prompt_template.format(
                extraction=extraction_str,
                analysis=analysis_str,
                content=paper_content[:30000],
                instructions=instructions
            )},
            {"role": "user", "content": "Generate the corrected extraction."}
        ]
        
        print("Generating improved extraction...")
        response = self.client.chat.completions.create(
            model="o1",
            messages=messages,
            max_completion_tokens=self.max_tokens
        )
        
        return self._parse_json_response(response.choices[0].message.content)
    
    def compare_extractions(self, old_extraction: Dict, new_extraction: Dict) -> Dict[str, Any]:
        """Compare two extractions to verify improvement"""
        
        prompt_template = """Compare these two extractions to verify improvement.

PREVIOUS EXTRACTION:
```json
{old}
```

NEW EXTRACTION:
```json
{new}
```

Check:
1. Were the identified issues fixed?
2. Was anything lost from the previous extraction?
3. Is the new extraction structurally correct?
4. Are the improvements meaningful?

Output as JSON:
{{
  "issues_fixed": ["list of fixed issues"],
  "issues_remaining": ["list of remaining issues"],
  "regressions": ["things that got worse"],
  "improvement_score": 0-100,
  "continue_iterating": true/false
}}"""

        old_str = json.dumps(old_extraction, indent=2)[:20000]
        new_str = json.dumps(new_extraction, indent=2)[:20000]

        messages = [
            {"role": "system", "content": prompt_template.format(old=old_str, new=new_str)},
            {"role": "user", "content": "Compare the extractions."}
        ]
        
        response = self.client.chat.completions.create(
            model="o1",
            messages=messages,
            max_completion_tokens=30000
        )
        
        return self._parse_json_response(response.choices[0].message.content)
    
    def extract_with_iterations(self, paper_path: Path, output_path: Path) -> Dict[str, Any]:
        """Main extraction loop with iterations"""
        
        print(f"\nIterative Extraction: {paper_path.name}")
        print("="*70)
        
        # Read paper
        with open(paper_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        if len(content) > 80000:
            print(f"Warning: Truncating from {len(content)} to 80k chars")
            content = content[:80000]
        
        # Initial extraction
        print("\nIteration 1: Initial extraction")
        current_extraction = self.initial_extraction(content)
        
        if not current_extraction:
            print("ERROR: Initial extraction failed")
            return {}
        
        # Save initial version
        temp_path = output_path.with_suffix('.iter1.json')
        with open(temp_path, 'w') as f:
            json.dump(current_extraction, f, indent=2)
        print(f"  Saved iteration 1 to: {temp_path}")
        
        # Iterative improvement loop
        for iteration in range(2, self.max_iterations + 1):
            print(f"\nIteration {iteration}: Analysis and improvement")
            
            # Analyze current extraction
            analysis = self.analyze_extraction(current_extraction, content)
            
            if not analysis:
                print("  ERROR: Analysis failed")
                break
                
            print(f"  Completeness score: {analysis.get('completeness_score', 'N/A')}")
            print(f"  Issues found: {len(analysis.get('missing_components', []))} missing components")
            
            # Check if optimal
            if analysis.get('is_optimal', False):
                print("  ✓ Extraction is optimal!")
                break
            
            # Improve extraction
            new_extraction = self.improve_extraction(current_extraction, analysis, content)
            
            if not new_extraction:
                print("  ERROR: Improvement failed")
                break
            
            # Compare old vs new
            comparison = self.compare_extractions(current_extraction, new_extraction)
            
            print(f"  Improvement score: {comparison.get('improvement_score', 'N/A')}")
            print(f"  Issues fixed: {len(comparison.get('issues_fixed', []))}")
            
            # Save iteration
            temp_path = output_path.with_suffix(f'.iter{iteration}.json')
            with open(temp_path, 'w') as f:
                json.dump(new_extraction, f, indent=2)
            print(f"  Saved iteration {iteration} to: {temp_path}")
            
            # Update current extraction
            current_extraction = new_extraction
            
            # Check if we should continue
            if not comparison.get('continue_iterating', True):
                print("  ✓ No further improvements needed")
                break
                
            # Prevent infinite loops
            if comparison.get('improvement_score', 0) < 10:
                print("  ⚠️  Minimal improvement, stopping iterations")
                break
        
        # Final validation
        print("\nFinal validation...")
        final_analysis = self.analyze_extraction(current_extraction, content)
        
        # Save final version
        with open(output_path, 'w') as f:
            json.dump(current_extraction, f, indent=2)
        print(f"\n✓ Final extraction saved to: {output_path}")
        
        # Print summary
        self._print_summary(current_extraction, final_analysis)
        
        return current_extraction
    
    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        """Parse JSON from LLM response"""
        try:
            # Find JSON in response
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = content[json_start:json_end]
                return json.loads(json_str)
            else:
                # Try to find JSON array
                json_start = content.find('[')
                json_end = content.rfind(']') + 1
                if json_start != -1 and json_end > json_start:
                    json_str = content[json_start:json_end]
                    return {"result": json.loads(json_str)}
                    
                print("Warning: No JSON found in response")
                return {}
        except Exception as e:
            print(f"Error parsing JSON: {e}")
            return {}
    
    def _print_summary(self, extraction: Dict, analysis: Dict):
        """Print extraction summary"""
        print("\n" + "="*70)
        print("EXTRACTION SUMMARY")
        print("="*70)
        
        # Count components
        for theory_name, theory in extraction.items():
            if isinstance(theory, dict) and 'schema' in theory:
                schema = theory['schema']
                if 'Ontology' in schema:
                    ont = schema['Ontology']
                    print(f"\nTheory: {theory_name}")
                    print(f"  Entities: {len(ont.get('entities', []))}")
                    print(f"  Connections: {len(ont.get('connections', []))}")
                    print(f"  Properties: {len(ont.get('properties', []))}")
                    print(f"  Modifiers: {len(ont.get('modifiers', []))}")
        
        if analysis:
            print(f"\nFinal Assessment:")
            print(f"  Completeness: {analysis.get('completeness_score', 'N/A')}%")
            print(f"  Remaining issues: {len(analysis.get('missing_components', []))}")
            
            if analysis.get('missing_components'):
                print("\n  Still missing:")
                for item in analysis['missing_components'][:3]:
                    print(f"    - {item.get('component', 'Unknown')}")

def main():
    """Test iterative extraction"""
    extractor = IterativeExtractorV8()
    
    paper_path = Path("/home/brian/lit_review/literature/operational_code_analysis/Cognitive Mapping Meets Semantic Networks.txt")
    output_path = Path("/home/brian/lit_review/results/cognitive_mapping_iterative_v8.json")
    
    if paper_path.exists():
        result = extractor.extract_with_iterations(paper_path, output_path)
    else:
        print(f"Error: Paper not found at {paper_path}")

if __name__ == "__main__":
    main()