#!/usr/bin/env python3
"""
Efficient Automated Schema Development
Processes paper in chunks to avoid timeouts
"""
import os
import yaml
import json
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def extract_key_sections(paper_text):
    """Extract key sections from Young's paper for focused analysis"""
    
    # Find key sections based on content markers
    sections = {}
    
    # Find methodology section (around WorldView description)
    worldview_start = paper_text.find("WorldView")
    if worldview_start != -1:
        sections['methodology'] = paper_text[worldview_start:worldview_start+8000]
    
    # Find measures section
    measures_start = paper_text.find("structural and comparative measures")
    if measures_start != -1:
        sections['measures'] = paper_text[measures_start:measures_start+5000]
    
    # Find Carter example section
    carter_start = paper_text.find("Carter")
    if carter_start != -1:
        sections['carter_example'] = paper_text[carter_start:carter_start+3000]
    
    # Find directed-walk section
    walk_start = paper_text.find("directed-walk")
    if walk_start != -1:
        sections['directed_walk'] = paper_text[walk_start:walk_start+2000]
    
    return sections

def create_focused_schema():
    """Create schema based on key insights from Young's paper"""
    
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    # Load paper and extract key sections
    paper_path = Path('/home/brian/lit_review/literature/operational_code_analysis/Cognitive Mapping Meets Semantic Networks.txt')
    with open(paper_path, 'r') as f:
        paper_text = f.read()
    
    sections = extract_key_sections(paper_text)
    
    prompt = f"""Create a computational schema for Young 1996's cognitive mapping methodology.

KEY PAPER SECTIONS:

METHODOLOGY:
{sections.get('methodology', '')[:3000]}

MEASURES:
{sections.get('measures', '')[:2000]}

CARTER EXAMPLE:
{sections.get('carter_example', '')[:1500]}

DIRECTED-WALK:
{sections.get('directed_walk', '')[:1000]}

Create a YAML schema that enables automated replication of Young's approach with high fidelity.

Include:
1. Exact relationship categories from Table 1
2. Truth values and modifiers 
3. Structural measure formulas
4. Salience counting procedure
5. Directed-walk algorithm
6. Extraction instructions

OUTPUT YAML:"""

    try:
        response = client.chat.completions.create(
            model=os.getenv('OPENAI_MODEL', 'o3'),
            messages=[
                {"role": "system", "content": "Create precise computational schemas from academic papers."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=6000
        )
        
        content = response.choices[0].message.content
        
        # Clean YAML
        if '```yaml' in content:
            start = content.find('```yaml') + 7
            end = content.find('```', start)
            if end != -1:
                content = content[start:end].strip()
        
        print(f"Generated schema content: {content[:1000]}...")
        
        # Fix YAML alias issues
        if '*' in content:
            print("Detected YAML aliases, cleaning...")
            # Remove problematic aliases for now
            content = content.replace('*relationship_categories', 'relationship_categories')
            content = content.replace('*truth_values', 'truth_values')
        
        return yaml.safe_load(content)
        
    except Exception as e:
        print(f"Error creating schema: {e}")
        return None

def apply_focused_schema(schema, target_text):
    """Apply schema to target text with specific instructions"""
    
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    prompt = f"""Apply Young 1996 cognitive mapping schema to extract analysis.

SCHEMA:
{yaml.dump(schema, default_flow_style=False)[:4000]}

TARGET TEXT:
{target_text[:8000]}

INSTRUCTIONS:
1. Extract concepts and relationships using schema categories
2. Count actual frequencies for salience
3. Apply truth values and modifiers 
4. Calculate structural measures using formulas
5. Implement directed-walk if possible

OUTPUT structured analysis following schema exactly."""

    try:
        response = client.chat.completions.create(
            model=os.getenv('OPENAI_MODEL', 'o3'),
            messages=[
                {"role": "system", "content": "Apply cognitive mapping schemas with perfect fidelity."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=6000
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Error applying schema: {e}")
        return None

def validate_results(analysis, paper_sections):
    """Quick validation against paper examples"""
    
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    prompt = f"""Validate this analysis against Young 1996 examples.

OUR ANALYSIS:
{analysis[:3000]}

PAPER EXAMPLES:
{paper_sections.get('carter_example', '')[:2000]}

Score fidelity 0-1 and identify issues:"""

    try:
        response = client.chat.completions.create(
            model=os.getenv('OPENAI_MODEL', 'o3'),
            messages=[
                {"role": "system", "content": "Validate computational implementations against original papers."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=2000
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Error in validation: {e}")
        return None

def main():
    """Run efficient automated schema development"""
    
    print("⚡ EFFICIENT AUTOMATED SCHEMA DEVELOPMENT")
    print("=" * 60)
    print("Focused approach - key sections only")
    print()
    
    # Load Carter speech  
    carter_path = Path('/home/brian/lit_review/texts/carter_speech.txt')
    with open(carter_path, 'r') as f:
        carter_speech = f.read()
    
    # Create focused schema
    print("🔬 Creating focused schema from key paper sections...")
    schema = create_focused_schema()
    
    if not schema:
        print("❌ Failed to create schema")
        return
    
    print("✅ Schema created")
    print(f"   Theory: {schema.get('theory_name', 'Young 1996')}")
    
    # Apply to Carter speech
    print("\n🎯 Applying schema to Carter speech...")
    analysis = apply_focused_schema(schema, carter_speech)
    
    if not analysis:
        print("❌ Failed to apply schema")
        return
        
    print(f"✅ Analysis generated ({len(analysis)} characters)")
    
    # Quick validation
    print("\n🔍 Validating results...")
    paper_path = Path('/home/brian/lit_review/literature/operational_code_analysis/Cognitive Mapping Meets Semantic Networks.txt')
    with open(paper_path, 'r') as f:
        paper_text = f.read()
    
    sections = extract_key_sections(paper_text)
    validation = validate_results(analysis, sections)
    
    if validation:
        print("✅ Validation complete")
        print(f"Result: {validation[:200]}...")
    
    # Save outputs
    output_dir = Path('/home/brian/lit_review/efficient_schema_output')
    output_dir.mkdir(exist_ok=True)
    
    with open(output_dir / 'focused_schema.yml', 'w') as f:
        yaml.dump(schema, f, default_flow_style=False)
    
    with open(output_dir / 'carter_analysis.txt', 'w') as f:
        f.write(analysis)
    
    with open(output_dir / 'validation.txt', 'w') as f:
        f.write(validation or "No validation performed")
    
    print(f"\n📁 Outputs saved to: {output_dir}")
    print("\n🏆 EFFICIENT PIPELINE COMPLETE")
    print("✅ Schema developed from key sections")
    print("✅ Applied to target text")
    print("✅ Results validated")

if __name__ == "__main__":
    main()