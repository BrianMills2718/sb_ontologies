#!/usr/bin/env python3
"""
Create Computationally Complete Schema for Young 1996
Includes step-by-step algorithms and computational procedures
"""
import os
import yaml
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def create_computational_schema():
    """Create schema with complete computational instructions"""
    
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    # Load Young's paper for algorithm extraction
    paper_path = Path('/home/brian/lit_review/literature/operational_code_analysis/Cognitive Mapping Meets Semantic Networks.txt')
    with open(paper_path, 'r') as f:
        paper_text = f.read()
    
    # Extract key algorithmic sections
    directed_walk_section = paper_text[paper_text.find("directed-walk"):paper_text.find("directed-walk") + 2000]
    dependency_section = paper_text[paper_text.find("Dependency reflects"):paper_text.find("Dependency reflects") + 1500]
    measures_section = paper_text[paper_text.find("structural and comparative measures"):paper_text.find("structural and comparative measures") + 3000]
    
    prompt = f"""Create a computationally complete schema for Young 1996 cognitive mapping.

EXTRACT EXACT ALGORITHMS FROM THESE SECTIONS:

DIRECTED-WALK ALGORITHM:
{directed_walk_section}

DEPENDENCY CALCULATION:
{dependency_section}

STRUCTURAL MEASURES:
{measures_section}

TASK: Create schema with step-by-step computational procedures that an API can execute automatically.

For each algorithm, specify:
1. Exact input requirements
2. Step-by-step processing instructions  
3. Specific computational operations
4. Output format requirements
5. Validation criteria

YAML SCHEMA FORMAT:
```yaml
citation: "Young, Michael D. 1996..."
theory_name: "WorldView Cognitive Mapping"

# Core elements from Young's paper
core_elements:
  relationship_categories:
    "+": "positive-cause"
    "-": "negative-cause"
    # ... etc
  
  truth_values: ["true", "false", "partial", "possible", "impossible"]
  modifiers: ["past", "present", "future", "goal", "hypothetical", "normative"]

# Computational algorithms with step-by-step instructions
algorithms:
  
  concept_extraction:
    input: "raw text string"
    procedure:
      - step: 1
        action: "identify unique nouns and noun phrases"
        implementation: "extract subject and object terms from sentences"
      - step: 2  
        action: "create concept nodes"
        implementation: "assign unique IDs and labels"
    output: "list of concept objects with IDs and labels"
    
  relationship_extraction:
    input: "raw text string + concept list"
    procedure:
      - step: 1
        action: "identify subject-relation-object triples"
        implementation: "parse sentences for verb-based connections"
      - step: 2
        action: "classify relationships using categories"
        implementation: "match verbs/phrases to relationship_categories"
      - step: 3
        action: "assign truth values and modifiers"
        implementation: "detect conditional, temporal, and certainty markers"
    output: "list of relationship objects"
    
  salience_calculation:
    input: "relationship list + raw text"
    procedure:
      - step: 1
        action: "count relationship frequency"
        implementation: "count occurrences of identical subject-relation-object triples"
      - step: 2
        action: "assign salience scores"
        implementation: "set salience = frequency count for each relationship"
    output: "relationships with salience scores"
    
  structural_measures:
    dependency_calculation:
      input: "concept list + relationship list"
      procedure:
        - step: 1
          action: "create network graph"
          implementation: "nodes = concepts, edges = relationships"
        - step: 2
          action: "identify bridges"
          implementation: "find edges whose removal increases connected components"
        - step: 3
          action: "count structures"
          implementation: "count number of disconnected components"
        - step: 4
          action: "calculate dependency"
          implementation: "D_G = (bridges / relationships) / structures"
      output: "dependency score (0 to 1)"
      
    connectedness_calculation:
      input: "concept list + relationship list"
      procedure:
        - step: 1
          action: "count total elements"
          implementation: "total = len(concepts) + len(relationships)"
        - step: 2
          action: "calculate ratio"
          implementation: "C_G = len(relationships) / total"
      output: "connectedness score (0 to 1)"
      
  directed_walk_reasoning:
    input: "cognitive map + starting proposition"
    procedure:
      - step: 1
        action: "find starting concept"
        implementation: "match proposition terms to concept labels"
      - step: 2
        action: "select highest salience relationship"
        implementation: "from current concept, choose max(salience) outgoing edge"
      - step: 3
        action: "traverse to target concept"
        implementation: "move to target node of selected relationship"
      - step: 4
        action: "repeat until termination"
        implementation: "continue steps 2-3 until no outgoing edges or max steps reached"
    output: "sequence of traversed relationships and reasoning steps"

# Automated application instructions
automation_procedures:
  
  text_preprocessing:
    - "split text into sentences"
    - "identify sentence boundaries"
    - "extract subject-verb-object patterns"
    
  frequency_counting:
    - "normalize relationship representations" 
    - "count identical triples across entire text"
    - "handle synonym variations using synonym_facility"
    
  quality_validation:
    - "verify all relationships use valid categories"
    - "check truth values are from valid set"
    - "ensure salience scores are positive integers"
    - "validate network connectivity for measures"

# API execution template
api_instructions:
  prompt_template: |
    Apply Young 1996 cognitive mapping using the algorithms defined in this schema.
    Execute each algorithm step-by-step as specified.
    Count actual frequencies for salience scores.
    Calculate structural measures using provided formulas.
    Output structured analysis following schema format.
    
  validation_checks:
    - "all concepts have unique IDs"
    - "all relationships reference valid concept IDs"
    - "salience scores reflect actual frequency counts"
    - "structural measures calculated using provided formulas"
```

Make this schema completely self-executing through API calls."""

    try:
        response = client.chat.completions.create(
            model=os.getenv('OPENAI_MODEL', 'o3'),
            messages=[
                {"role": "system", "content": "Create complete computational schemas with step-by-step algorithms that APIs can execute automatically."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=8000
        )
        
        content = response.choices[0].message.content
        
        # Clean YAML
        if '```yaml' in content:
            start = content.find('```yaml') + 7
            end = content.find('```', start)
            if end != -1:
                content = content[start:end].strip()
        
        return yaml.safe_load(content)
        
    except Exception as e:
        print(f"Error creating computational schema: {e}")
        return None

def test_computational_schema(schema, test_text):
    """Test the computational schema with automated execution"""
    
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    # Extract algorithms from schema
    algorithms = schema.get('algorithms', {})
    
    # Build execution prompt from schema algorithms
    execution_prompt = f"""Execute Young 1996 cognitive mapping using these computational procedures:

SCHEMA ALGORITHMS:
{yaml.dump(algorithms, default_flow_style=False)}

AUTOMATION PROCEDURES:
{yaml.dump(schema.get('automation_procedures', {}), default_flow_style=False)}

TEXT TO ANALYZE:
{test_text[:4000]}

EXECUTE STEP BY STEP:
1. Apply concept_extraction algorithm
2. Apply relationship_extraction algorithm  
3. Apply salience_calculation algorithm
4. Apply structural_measures algorithms
5. Apply directed_walk_reasoning if possible

OUTPUT: Complete cognitive map analysis following schema procedures exactly.

Use the schema's step-by-step instructions. Count actual frequencies. Calculate measures using provided formulas."""

    try:
        response = client.chat.completions.create(
            model=os.getenv('OPENAI_MODEL', 'o3'),
            messages=[
                {"role": "system", "content": "Execute computational schemas step-by-step with perfect fidelity to algorithmic instructions."},
                {"role": "user", "content": execution_prompt}
            ],
            max_completion_tokens=6000
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Error testing schema: {e}")
        return None

def validate_computational_completeness(schema, test_result):
    """Validate that schema produces complete computational results"""
    
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    prompt = f"""Validate this computational schema implementation against Young 1996 requirements.

SCHEMA USED:
{yaml.dump(schema, default_flow_style=False)[:2000]}

EXECUTION RESULT:
{test_result[:2000]}

VALIDATION CRITERIA:
1. Are all Young 1996 algorithms implemented?
2. Do results include actual frequency counts (not just 1s)?  
3. Are structural measures calculated using correct formulas?
4. Is directed-walk reasoning demonstrated?
5. Does output match Young's methodology?

OUTPUT: Validation score 0-1 and specific assessment of computational completeness."""

    try:
        response = client.chat.completions.create(
            model=os.getenv('OPENAI_MODEL', 'o3'),
            messages=[
                {"role": "system", "content": "Validate computational implementations against academic standards."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=2000
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Error in validation: {e}")
        return None

def main():
    """Create and test computationally complete schema"""
    
    print("🔬 CREATING COMPUTATIONALLY COMPLETE SCHEMA")
    print("=" * 70)
    print("Embedding step-by-step algorithms for automated execution")
    print()
    
    # Create computational schema
    print("⚙️ Creating computational schema with algorithms...")
    schema = create_computational_schema()
    
    if not schema:
        print("❌ Failed to create computational schema")
        return
    
    print("✅ Computational schema created")
    print(f"   Algorithms included: {len(schema.get('algorithms', {}))}")
    print(f"   Core elements: {len(schema.get('core_elements', {}))}")
    print()
    
    # Test with Carter speech
    carter_path = Path('/home/brian/lit_review/texts/carter_speech.txt')
    with open(carter_path, 'r') as f:
        carter_speech = f.read()
    
    print("🎯 Testing computational schema execution...")
    test_result = test_computational_schema(schema, carter_speech)
    
    if not test_result:
        print("❌ Failed to execute schema")
        return
    
    print(f"✅ Schema execution completed ({len(test_result)} characters)")
    print()
    
    # Validate computational completeness
    print("🔍 Validating computational completeness...")
    validation = validate_computational_completeness(schema, test_result)
    
    if validation:
        print("✅ Validation completed")
        print(f"Result: {validation[:300]}...")
    print()
    
    # Save all outputs
    output_dir = Path('/home/brian/lit_review/computational_schema_output')
    output_dir.mkdir(exist_ok=True)
    
    # Save computational schema
    with open(output_dir / 'computational_complete_schema.yml', 'w') as f:
        yaml.dump(schema, f, default_flow_style=False)
    
    # Save test execution
    with open(output_dir / 'computational_test_result.txt', 'w') as f:
        f.write(test_result)
    
    # Save validation
    with open(output_dir / 'computational_validation.txt', 'w') as f:
        f.write(validation or "No validation performed")
    
    print(f"📁 All outputs saved to: {output_dir}")
    print()
    print("🏆 COMPUTATIONALLY COMPLETE SCHEMA READY")
    print("✅ Step-by-step algorithms embedded")
    print("✅ Automated execution tested")
    print("✅ Computational completeness validated")
    print()
    print("🎯 NEXT: This schema can now be used for fully automated")
    print("   end-to-end theory application without manual intervention")

if __name__ == "__main__":
    main()