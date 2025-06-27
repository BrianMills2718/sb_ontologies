#!/usr/bin/env python3
"""
Simplified Implementation Extractor - Option 2
"""

import os
import yaml
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
client = OpenAI()

def extract_implementation_simple(paper_path: str, schema_path: str = None) -> dict:
    """Extract implementation details using simple prompt"""
    
    # Load paper text
    with open(paper_path, 'r', encoding='utf-8') as f:
        paper_text = f.read()
    
    # Load schema context if provided
    schema_context = ""
    if schema_path and os.path.exists(schema_path):
        with open(schema_path, 'r') as f:
            schema = yaml.safe_load(f)
            schema_context = f"Theory: {schema.get('citation', '')}"
    
    prompt = f"""
Extract the complete IMPLEMENTATION SPECIFICATION from this academic paper.
{schema_context}

Extract in this exact format:

NOTATION SYSTEM:
Type codes: (list all type codes like C, P, M with meanings)
Argument roles: (list all role codes like sa, pa with meanings)
Special symbols: (list all symbols like +/B with meanings)
Examples: (show complete notation examples)

PATTERN LIBRARY:
(List each pattern with:)
Pattern: [exact syntax]
Matches: [what it matches]
Example: [example text]
Result: [transformation result]

ALGORITHMS:
(List each algorithm with name and steps)

EVALUATION:
Metrics: (list metrics used)
Results: (key results)

COMPLETE EXAMPLES:
(Show 2-3 complete worked examples from paper)

PAPER TEXT:
{paper_text[:20000]}

Be extremely thorough - capture ALL notation details, patterns, and algorithms.
"""

    response = client.chat.completions.create(
        model="o3",
        messages=[
            {"role": "system", "content": "Extract complete implementation specifications."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content

def parse_and_save_implementation(content: str, output_path: str):
    """Parse the text response and save as structured YAML"""
    
    # This is a simple parser - in production you'd want something more robust
    lines = content.split('\n')
    
    implementation = {
        "implementation_specification": {
            "notation_system": {
                "type_codes": {},
                "argument_roles": {},
                "special_symbols": {},
                "examples": []
            },
            "pattern_library": [],
            "algorithms": [],
            "evaluation": {
                "metrics": [],
                "results": []
            },
            "examples": []
        }
    }
    
    current_section = None
    current_pattern = {}
    current_algo = {}
    
    for line in lines:
        line = line.strip()
        
        # Section headers
        if line == "NOTATION SYSTEM:":
            current_section = "notation"
        elif line == "PATTERN LIBRARY:":
            current_section = "patterns"
        elif line == "ALGORITHMS:":
            current_section = "algorithms"
        elif line == "EVALUATION:":
            current_section = "evaluation"
        elif line == "COMPLETE EXAMPLES:":
            current_section = "examples"
        
        # Parse content based on section
        elif current_section == "notation" and line.startswith("Type codes:"):
            # Parse type codes in subsequent lines
            pass
        elif current_section == "notation" and ":" in line and not line.startswith("Type") and not line.startswith("Argument"):
            # Parse individual codes
            if " - " in line or ": " in line:
                parts = line.split(" - " if " - " in line else ": ", 1)
                if len(parts) == 2:
                    code, desc = parts
                    if len(code) <= 3:  # Likely a code
                        if code.isupper():
                            implementation["implementation_specification"]["notation_system"]["type_codes"][code] = desc
                        else:
                            implementation["implementation_specification"]["notation_system"]["argument_roles"][code] = desc
        
        elif current_section == "patterns" and line.startswith("Pattern:"):
            if current_pattern:
                implementation["implementation_specification"]["pattern_library"].append(current_pattern)
            current_pattern = {"pattern": line.replace("Pattern:", "").strip()}
        elif current_section == "patterns" and line.startswith("Matches:"):
            current_pattern["matches"] = line.replace("Matches:", "").strip()
        elif current_section == "patterns" and line.startswith("Example:"):
            current_pattern["example"] = line.replace("Example:", "").strip()
        elif current_section == "patterns" and line.startswith("Result:"):
            current_pattern["result"] = line.replace("Result:", "").strip()
    
    # Add final pattern if exists
    if current_pattern:
        implementation["implementation_specification"]["pattern_library"].append(current_pattern)
    
    # Save to YAML
    with open(output_path, 'w') as f:
        # First save the raw content
        f.write("# RAW EXTRACTION OUTPUT\n")
        f.write("# " + "="*50 + "\n")
        for line in content.split('\n')[:100]:  # First 100 lines
            f.write(f"# {line}\n")
        f.write("# " + "="*50 + "\n\n")
        
        # Then save structured version
        yaml.dump(implementation, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

def main():
    paper_path = "/home/brian/lit_review/semantic_hypergraphs.txt"
    schema_path = "schemas/semantic_hypergraph/semantic_hypergraph_fixed.yml"
    output_path = "schemas/semantic_hypergraph/sh_option2_implementation.yml"
    
    print("=== OPTION 2: SEPARATE IMPLEMENTATION EXTRACTION ===")
    print(f"Processing: {paper_path}")
    
    print("\nExtracting implementation specification...")
    content = extract_implementation_simple(paper_path, schema_path)
    
    # Show preview
    print("\nExtraction preview:")
    print(content[:500] + "...")
    
    # Parse and save
    parse_and_save_implementation(content, output_path)
    print(f"\nSaved to: {output_path}")

if __name__ == "__main__":
    main()