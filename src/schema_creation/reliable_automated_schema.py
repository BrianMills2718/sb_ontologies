#!/usr/bin/env python3
"""
Reliable Automated Schema Development
Simple, robust approach that focuses on core Young 1996 elements
"""
import os
import yaml
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def create_young1996_schema_automated():
    """Create Young 1996 schema through structured API calls"""
    
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    # Load key sections from Young's paper
    paper_path = Path('/home/brian/lit_review/literature/operational_code_analysis/Cognitive Mapping Meets Semantic Networks.txt')
    with open(paper_path, 'r') as f:
        paper_text = f.read()
    
    # Extract Table 1 relationships
    table1_section = paper_text[paper_text.find("equal ="):paper_text.find("equal =") + 1000]
    
    prompt = f"""Extract Young 1996's cognitive mapping elements for computational schema.

From Young's paper, extract:

1. Relationship categories from Table 1:
{table1_section}

2. Truth values: true, false, partial, possible, impossible
3. Modifiers: past, present, future, goal, hypothetical, normative
4. Structural measures with exact formulas

Create simple JSON output:
{{
  "relationship_categories": {{
    "+": "positive-cause",
    "-": "negative-cause", 
    "=": "equal",
    "strategy": "means-ends relationship"
  }},
  "truth_values": ["true", "false", "partial", "possible", "impossible"],
  "modifiers": ["past", "present", "future", "goal", "hypothetical", "normative"],
  "structural_measures": {{
    "dependency": {{
      "formula": "exact formula from paper",
      "description": "what it measures"
    }}
  }}
}}

Extract Young's EXACT terms and formulas."""

    try:
        response = client.chat.completions.create(
            model=os.getenv('OPENAI_MODEL', 'o3'),
            messages=[
                {"role": "system", "content": "Extract precise computational elements from academic papers."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=3000
        )
        
        content = response.choices[0].message.content
        
        # Clean JSON
        if '```json' in content:
            start = content.find('```json') + 7
            end = content.find('```', start)
            if end != -1:
                content = content[start:end].strip()
        elif '{' in content:
            start = content.find('{')
            end = content.rfind('}') + 1
            content = content[start:end]
        
        import json
        elements = json.loads(content)
        
        # Convert to YAML schema
        schema = {
            'citation': 'Young, Michael D. 1996. "Cognitive Mapping Meets Semantic Networks." Journal of Conflict Resolution 40(3): 395-414.',
            'theory_name': 'WorldView Cognitive Mapping',
            'automated_extraction': True,
            'elements': elements,
            'processing_instructions': {
                'concept_extraction': 'Identify unique terms in text as concept nodes',
                'relationship_extraction': 'Find subject-relation-object triples using relationship categories',
                'salience_counting': 'Count frequency of each unique relationship across text',
                'structural_calculation': 'Apply formulas to calculate measures from graph structure',
                'truth_assignment': 'Assign truth values based on text indicators',
                'modifier_assignment': 'Apply temporal and logical modifiers from context'
            }
        }
        
        return schema
        
    except Exception as e:
        print(f"Error creating schema: {e}")
        return None

def apply_automated_schema(schema, text):
    """Apply schema using structured API call"""
    
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    # Create focused prompt
    elements = schema['elements']
    
    prompt = f"""Apply Young 1996 cognitive mapping to this text using these exact elements:

RELATIONSHIP CATEGORIES: {elements['relationship_categories']}
TRUTH VALUES: {elements['truth_values']}
MODIFIERS: {elements['modifiers']}

TEXT TO ANALYZE:
{text[:6000]}

TASK:
1. Extract concepts (unique terms)
2. Find relationships using ONLY the categories above
3. Count actual frequency of each relationship for salience
4. Assign truth values and modifiers
5. Calculate network size and connectedness

OUTPUT JSON:
{{
  "concepts": [
    {{"id": "C1", "label": "concept name", "frequency": 3}}
  ],
  "relationships": [
    {{"from": "C1", "to": "C2", "category": "+", "truth": "true", "modifiers": ["present"], "salience": 2}}
  ],
  "measures": {{
    "size": 10,
    "connectedness": 0.25
  }}
}}

Use ONLY schema elements. Count actual frequencies."""

    try:
        response = client.chat.completions.create(
            model=os.getenv('OPENAI_MODEL', 'o3'),
            messages=[
                {"role": "system", "content": "Apply cognitive mapping schemas exactly as specified."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=4000
        )
        
        content = response.choices[0].message.content
        
        # Clean JSON
        if '```json' in content:
            start = content.find('```json') + 7
            end = content.find('```', start)
            if end != -1:
                content = content[start:end].strip()
        elif '{' in content:
            start = content.find('{')
            end = content.rfind('}') + 1
            content = content[start:end]
        
        import json
        return json.loads(content)
        
    except Exception as e:
        print(f"Error applying schema: {e}")
        return None

def validate_automated_results(analysis, schema):
    """Validate results against schema requirements"""
    
    if not analysis:
        return {"valid": False, "errors": ["No analysis provided"]}
    
    errors = []
    
    # Check required fields
    if 'concepts' not in analysis:
        errors.append("Missing concepts")
    if 'relationships' not in analysis:
        errors.append("Missing relationships")
    if 'measures' not in analysis:
        errors.append("Missing measures")
    
    # Check relationship categories
    valid_categories = set(schema['elements']['relationship_categories'].keys())
    for rel in analysis.get('relationships', []):
        if rel.get('category') not in valid_categories:
            errors.append(f"Invalid relationship category: {rel.get('category')}")
    
    # Check truth values
    valid_truth = set(schema['elements']['truth_values'])
    for rel in analysis.get('relationships', []):
        if rel.get('truth') not in valid_truth:
            errors.append(f"Invalid truth value: {rel.get('truth')}")
    
    # Check measures
    measures = analysis.get('measures', {})
    if 'size' not in measures:
        errors.append("Missing size measure")
    if 'connectedness' not in measures:
        errors.append("Missing connectedness measure")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "fidelity_score": 1.0 if len(errors) == 0 else max(0, 1.0 - len(errors) * 0.1)
    }

def main():
    """Run reliable automated schema development"""
    
    print("🎯 RELIABLE AUTOMATED SCHEMA DEVELOPMENT")
    print("=" * 60)
    print("Simple, robust approach using structured API calls")
    print()
    
    # Create schema automatically
    print("🔬 Creating Young 1996 schema automatically...")
    schema = create_young1996_schema_automated()
    
    if not schema:
        print("❌ Failed to create schema")
        return
    
    print("✅ Schema created successfully")
    print(f"   Relationship categories: {len(schema['elements']['relationship_categories'])}")
    print(f"   Truth values: {len(schema['elements']['truth_values'])}")
    print(f"   Modifiers: {len(schema['elements']['modifiers'])}")
    print()
    
    # Load Carter speech
    carter_path = Path('/home/brian/lit_review/texts/carter_speech.txt')
    with open(carter_path, 'r') as f:
        carter_speech = f.read()
    
    # Apply schema automatically
    print("🎯 Applying schema to Carter speech...")
    analysis = apply_automated_schema(schema, carter_speech)
    
    if not analysis:
        print("❌ Failed to apply schema")
        return
    
    print("✅ Analysis completed")
    print(f"   Concepts extracted: {len(analysis.get('concepts', []))}")
    print(f"   Relationships found: {len(analysis.get('relationships', []))}")
    print(f"   Measures calculated: {len(analysis.get('measures', {}))}")
    print()
    
    # Validate results
    print("🔍 Validating results...")
    validation = validate_automated_results(analysis, schema)
    
    print(f"✅ Validation complete")
    print(f"   Valid: {validation['valid']}")
    print(f"   Fidelity score: {validation['fidelity_score']:.2f}")
    if validation['errors']:
        print(f"   Errors: {validation['errors']}")
    print()
    
    # Save outputs
    output_dir = Path('/home/brian/lit_review/reliable_schema_output')
    output_dir.mkdir(exist_ok=True)
    
    # Save schema
    with open(output_dir / 'automated_schema.yml', 'w') as f:
        yaml.dump(schema, f, default_flow_style=False)
    
    # Save analysis
    with open(output_dir / 'automated_analysis.json', 'w') as f:
        import json
        json.dump(analysis, f, indent=2)
    
    # Save validation
    with open(output_dir / 'validation_report.json', 'w') as f:
        import json
        json.dump(validation, f, indent=2)
    
    print(f"📁 All outputs saved to: {output_dir}")
    print()
    print("🏆 RELIABLE AUTOMATED PIPELINE COMPLETE")
    print("✅ Schema automatically extracted from Young 1996 paper")
    print("✅ Schema applied to Carter speech automatically") 
    print("✅ Results validated against schema requirements")
    print(f"✅ Final fidelity score: {validation['fidelity_score']:.2f}")
    print()
    print("🎯 This demonstrates end-to-end automation:")
    print("   Paper → Schema → Application → Validation")
    print("   No manual intervention required")

if __name__ == "__main__":
    main()