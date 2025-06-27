#!/usr/bin/env python3
"""
Automated End-to-End Schema Development from Academic Papers
Reads paper -> Develops schema -> Applies schema -> Validates results
No manual intervention - purely API-driven
"""
import os
import yaml
import json
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class AutomatedSchemaBuilder:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = os.getenv('OPENAI_MODEL', 'o3')
    
    def extract_theory_specification(self, paper_text):
        """Phase 1: Extract complete theory specification from paper"""
        
        prompt = f"""You are analyzing an academic paper to extract its complete theoretical framework for computational implementation.

PAPER TEXT:
{paper_text}

TASK: Extract the complete theoretical specification that would allow perfect replication of the author's methodology.

Focus on:
1. EXACT terminology the author uses (not generic equivalents)
2. Specific formulas, algorithms, procedures
3. Data structures and representations
4. Processing steps and workflows
5. Measurement calculations
6. Examples and demonstrations
7. Implementation details

OUTPUT JSON:
{{
  "theory_name": "exact name from paper",
  "core_concepts": [
    {{
      "name": "exact term from paper",
      "definition": "author's definition",
      "type": "entity/relationship/measure/process/etc",
      "implementation_details": "how to operationalize"
    }}
  ],
  "data_structures": [
    {{
      "name": "structure name", 
      "description": "what it represents",
      "components": ["list of elements"],
      "relationships": "how components relate"
    }}
  ],
  "algorithms": [
    {{
      "name": "algorithm name",
      "purpose": "what it does", 
      "steps": ["step 1", "step 2", ...],
      "formulas": ["exact formulas from paper"],
      "examples": "author's examples"
    }}
  ],
  "measures": [
    {{
      "name": "exact measure name",
      "symbol": "mathematical symbol",
      "formula": "exact formula",
      "interpretation": "what it means",
      "calculation_procedure": "how to compute"
    }}
  ],
  "processing_workflow": [
    "step 1 of overall process",
    "step 2 of overall process"
  ],
  "validation_criteria": [
    "how to verify correct implementation"
  ]
}}

Extract EVERYTHING needed for computational replication. Use author's exact terminology."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You extract complete computational specifications from academic papers with perfect fidelity to the original."},
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=8000
            )
            
            content = response.choices[0].message.content
            
            # Clean and extract JSON
            if '```json' in content:
                start = content.find('```json') + 7
                end = content.find('```', start)
                if end != -1:
                    content = content[start:end].strip()
            elif '{' in content:
                start = content.find('{')
                end = content.rfind('}') + 1
                content = content[start:end]
            
            return json.loads(content)
            
        except Exception as e:
            print(f"Error in theory extraction: {e}")
            # Debug the response
            try:
                content = response.choices[0].message.content
                print(f"Raw response: {content[:500]}...")
            except:
                print("Could not access response content")
            return None
    
    def generate_computational_schema(self, theory_spec):
        """Phase 2: Generate computational schema from theory specification"""
        
        prompt = f"""Convert this theory specification into a computational schema for automated application.

THEORY SPECIFICATION:
{json.dumps(theory_spec, indent=2)}

TASK: Create a computational schema that enables automated application with the same fidelity as the original author.

Requirements:
1. Include ALL algorithms, measures, and procedures
2. Specify exact computational steps
3. Enable automated extraction and processing
4. Maintain theoretical fidelity
5. Include validation procedures

OUTPUT YAML SCHEMA:
```yaml
citation: "full citation"
theory_name: "exact name"
computational_model:
  
  # Core theoretical constructs
  entities:
    - name: "exact term"
      definition: "author's definition"
      extraction_pattern: "how to identify in text"
      
  relationships:
    - name: "exact term"
      definition: "author's definition" 
      representation: "how to encode"
      
  # Computational procedures
  algorithms:
    algorithm_name:
      purpose: "what it does"
      inputs: ["required inputs"]
      steps:
        - step: 1
          action: "specific action"
          computation: "exact computation"
      outputs: ["what it produces"]
      validation: "how to verify"
      
  # Measurement procedures  
  measures:
    measure_name:
      symbol: "symbol"
      formula: "exact formula"
      computation_steps: ["step 1", "step 2"]
      interpretation: "meaning"
      
  # Processing pipeline
  workflow:
    - phase: 1
      name: "phase name"
      procedure: "what to do"
      outputs: "what it produces"
      
  # Automated application instructions
  extraction_instructions:
    text_processing: "how to process input text"
    concept_identification: "how to find concepts"
    relationship_extraction: "how to find relationships"
    frequency_counting: "how to count occurrences"
    
  # Validation procedures
  validation:
    fidelity_checks: ["check 1", "check 2"]
    expected_outputs: "what results should look like"
    comparison_criteria: "how to compare to original"
```

Make this schema completely self-sufficient for automated application."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You create computational schemas that enable perfect automated replication of academic theories."},
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=8000
            )
            
            content = response.choices[0].message.content
            if content.startswith('```yaml'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
                
            return yaml.safe_load(content)
            
        except Exception as e:
            print(f"Error in schema generation: {e}")
            return None
    
    def apply_schema_to_text(self, schema, target_text):
        """Phase 3: Apply computational schema to target text"""
        
        prompt = f"""Apply this computational schema to extract theoretical analysis from the target text.

COMPUTATIONAL SCHEMA:
{yaml.dump(schema, default_flow_style=False)}

TARGET TEXT:
{target_text}

TASK: Execute the schema's procedures exactly to produce theoretical analysis.

Follow the schema's:
1. Extraction instructions
2. Processing workflow  
3. Algorithm steps
4. Measurement procedures
5. Validation checks

OUTPUT: Complete analysis following schema specifications exactly.

Use the schema's exact terminology and procedures. Count actual frequencies. Calculate all measures using provided formulas."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You execute computational schemas with perfect fidelity to produce theoretical analyses."},
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=8000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error in schema application: {e}")
            return None
    
    def validate_against_original(self, analysis_result, original_paper, theory_spec):
        """Phase 4: Validate results against original paper examples"""
        
        prompt = f"""Compare this automated analysis with the original paper's examples to validate fidelity.

AUTOMATED ANALYSIS RESULT:
{analysis_result}

ORIGINAL PAPER (for reference examples):
{original_paper[:10000]}  # Truncated for context

THEORY SPECIFICATION:
{json.dumps(theory_spec, indent=2)}

VALIDATION TASK:
1. Compare our results to any examples in the original paper
2. Check if we used the author's exact terminology
3. Verify our measures match the author's calculations
4. Assess overall theoretical fidelity
5. Identify any deviations or improvements needed

OUTPUT JSON:
{{
  "fidelity_score": 0.0-1.0,
  "terminology_match": "assessment of term usage",
  "measurement_accuracy": "assessment of calculations", 
  "example_comparisons": [
    {{
      "original_example": "from paper",
      "our_result": "from analysis",
      "match_quality": "assessment"
    }}
  ],
  "deviations_identified": ["list of issues"],
  "improvements_needed": ["specific fixes"],
  "overall_assessment": "summary of fidelity"
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You validate computational implementations against original academic theories with rigorous standards."},
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=4000
            )
            
            content = response.choices[0].message.content
            
            # Clean and extract JSON  
            if '```json' in content:
                start = content.find('```json') + 7
                end = content.find('```', start)
                if end != -1:
                    content = content[start:end].strip()
            elif '{' in content:
                start = content.find('{')
                end = content.rfind('}') + 1
                content = content[start:end]
            
            return json.loads(content)
            
        except Exception as e:
            print(f"Error in validation: {e}")
            return None

def main():
    """Run automated end-to-end schema development and application"""
    
    print("🤖 AUTOMATED END-TO-END SCHEMA DEVELOPMENT")
    print("=" * 70)
    print("Reading paper → Developing schema → Applying schema → Validating results")
    print("No manual intervention - purely API-driven")
    print()
    
    builder = AutomatedSchemaBuilder()
    
    # Load source materials
    young_paper_path = Path('/home/brian/lit_review/literature/operational_code_analysis/Cognitive Mapping Meets Semantic Networks.txt')
    carter_speech_path = Path('/home/brian/lit_review/texts/carter_speech.txt')
    
    with open(young_paper_path, 'r') as f:
        young_paper = f.read()
    
    with open(carter_speech_path, 'r') as f:
        carter_speech = f.read()
    
    print("📖 Loaded Young 1996 paper and Carter speech")
    print()
    
    # Phase 1: Extract theory specification
    print("🔬 PHASE 1: Extracting complete theory specification...")
    theory_spec = builder.extract_theory_specification(young_paper)
    
    if not theory_spec:
        print("❌ Failed to extract theory specification")
        return
    
    print(f"✅ Extracted theory specification:")
    print(f"   Core concepts: {len(theory_spec.get('core_concepts', []))}")
    print(f"   Algorithms: {len(theory_spec.get('algorithms', []))}")
    print(f"   Measures: {len(theory_spec.get('measures', []))}")
    print()
    
    # Phase 2: Generate computational schema
    print("⚙️ PHASE 2: Generating computational schema...")
    schema = builder.generate_computational_schema(theory_spec)
    
    if not schema:
        print("❌ Failed to generate computational schema")
        return
    
    print(f"✅ Generated computational schema:")
    print(f"   Theory: {schema.get('theory_name', 'N/A')}")
    print(f"   Algorithms: {len(schema.get('computational_model', {}).get('algorithms', {}))}")
    print(f"   Measures: {len(schema.get('computational_model', {}).get('measures', {}))}")
    print()
    
    # Phase 3: Apply schema to Carter speech
    print("🎯 PHASE 3: Applying schema to Carter speech...")
    analysis_result = builder.apply_schema_to_text(schema, carter_speech)
    
    if not analysis_result:
        print("❌ Failed to apply schema")
        return
    
    print(f"✅ Generated analysis ({len(analysis_result)} characters)")
    print()
    
    # Phase 4: Validate against original
    print("🔍 PHASE 4: Validating against original paper...")
    validation = builder.validate_against_original(analysis_result, young_paper, theory_spec)
    
    if not validation:
        print("❌ Failed to validate results")
        return
    
    print(f"✅ Validation complete:")
    print(f"   Fidelity score: {validation.get('fidelity_score', 'N/A')}")
    print(f"   Deviations: {len(validation.get('deviations_identified', []))}")
    print()
    
    # Save all outputs
    output_dir = Path('/home/brian/lit_review/automated_schema_output')
    output_dir.mkdir(exist_ok=True)
    
    # Save theory specification
    with open(output_dir / 'theory_specification.json', 'w') as f:
        json.dump(theory_spec, f, indent=2)
    
    # Save computational schema
    with open(output_dir / 'computational_schema.yml', 'w') as f:
        yaml.dump(schema, f, default_flow_style=False)
    
    # Save analysis result
    with open(output_dir / 'carter_analysis.txt', 'w') as f:
        f.write(analysis_result)
    
    # Save validation
    with open(output_dir / 'validation_report.json', 'w') as f:
        json.dump(validation, f, indent=2)
    
    print(f"📁 All outputs saved to: {output_dir}")
    print()
    print("🏆 AUTOMATED PIPELINE COMPLETE")
    print("✅ Paper read and theory extracted")
    print("✅ Computational schema generated") 
    print("✅ Schema applied to target text")
    print("✅ Results validated against original")
    print(f"✅ Fidelity score: {validation.get('fidelity_score', 'N/A')}")

if __name__ == "__main__":
    main()