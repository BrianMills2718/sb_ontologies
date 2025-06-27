#!/usr/bin/env python3
"""
Create a faithful Young 1996 schema directly from the original paper
Uses OpenAI API to extract ONLY what Young actually defines
"""
import os
import yaml
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def load_young1996_paper():
    """Load the original Young 1996 paper text"""
    paper_path = Path('/home/brian/lit_review/literature/operational_code_analysis/Cognitive Mapping Meets Semantic Networks.txt')
    with open(paper_path, 'r') as f:
        return f.read()

def create_faithful_schema_via_api(paper_text):
    """Use OpenAI API to create schema using ONLY Young's exact concepts"""
    
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    prompt = f"""You are creating a computational schema for Young 1996's cognitive mapping theory.

CRITICAL REQUIREMENTS:
- Extract ONLY concepts, relationships, and measures that Young explicitly defines in his paper
- Use Young's EXACT terminology, not generic network science terms
- Do NOT add concepts from general network analysis (centrality, betweenness, etc.)
- Do NOT use generic property graph assumptions
- Stay strictly within Young's theoretical framework

YOUNG 1996 PAPER:
{paper_text}

TASK: Create a YAML schema that represents ONLY what Young 1996 actually defines.

Focus on:
1. Young's specific entity types (WorldView, Cognitive mapping, Semantic network, etc.)
2. Young's relationship types (is-a, part-of, positive causal link, negative causal link, etc.)
3. Young's specific measures (dependency, connectedness, size, uniformity of salience)
4. Young's properties (synonym facility, aggregation, hidden information, etc.)
5. Young's actions (content analysis, belief change, decision making, reasoning)

OUTPUT FORMAT:
```yaml
citation: "Young, Michael D. 1996. Cognitive Mapping Meets Semantic Networks. Journal of Conflict Resolution 40(3): 395-414."
model_type: [Young's actual model type from paper]
rationale: [Young's explanation of the approach]
schema_blueprint:
  title: "Young 1996 Cognitive Mapping Schema (Faithful Extraction)"
  description: [description based on Young's paper]
  definitions:
    # Only Young's actual concepts
```

VERIFICATION: Every element must be traceable to Young's paper. Do not invent or generalize."""

    try:
        response = client.chat.completions.create(
            model=os.getenv('OPENAI_MODEL', 'o3'),
            messages=[
                {"role": "system", "content": "You are a precise academic theory extraction system. Extract only what the author explicitly defines, using their exact terminology."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=6000
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"API Error: {str(e)}"

def main():
    """Main execution function"""
    print("📚 CREATING FAITHFUL YOUNG 1996 SCHEMA FROM ORIGINAL PAPER")
    print("=" * 80)
    print("Using OpenAI O3 to extract ONLY Young's actual definitions")
    print()
    
    # Load Young's original paper
    print("📖 Loading Young 1996 original paper...")
    paper = load_young1996_paper()
    print(f"📊 Paper length: {len(paper):,} characters")
    print()
    
    # Create faithful schema via API
    print("🔬 Extracting Young's concepts via API...")
    schema_content = create_faithful_schema_via_api(paper)
    
    # Clean the response (remove code block markers if present)
    if schema_content.startswith('```yaml'):
        schema_content = schema_content[7:]  # Remove ```yaml
    if schema_content.endswith('```'):
        schema_content = schema_content[:-3]  # Remove ```
    
    # Save the faithful schema
    output_path = Path('/home/brian/lit_review/literature/operational_code_analysis/young1996_faithful.yml')
    with open(output_path, 'w') as f:
        f.write(schema_content)
    
    print("✅ FAITHFUL SCHEMA CREATED")
    print(f"📄 Saved to: {output_path}")
    print()
    
    # Validate the schema can be loaded
    try:
        with open(output_path, 'r') as f:
            schema_data = yaml.safe_load(f)
        print("✅ Schema validation: Valid YAML")
        print(f"📊 Schema elements: {len(schema_data.get('schema_blueprint', {}).get('definitions', []))}")
    except Exception as e:
        print(f"❌ Schema validation error: {e}")
    
    print()
    print("Schema preview:")
    print("-" * 50)
    print(schema_content[:1500] + "..." if len(schema_content) > 1500 else schema_content)

if __name__ == "__main__":
    main()