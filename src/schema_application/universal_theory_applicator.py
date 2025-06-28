#!/usr/bin/env python3
"""
Universal Theory Applicator - Generalizable framework for applying any theory schema
"""

import os
import sys
import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field, create_model
from abc import ABC, abstractmethod

# Load environment
load_dotenv()
client = OpenAI()
MODEL = os.getenv("OPENAI_MODEL", "o3")

class StageResult(BaseModel):
    """Generic result from any stage"""
    stage_name: str
    data: Dict[str, Any]
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TheoryApplication(BaseModel):
    """Final theory application result"""
    theory_name: str
    stages: List[StageResult]
    final_output: Dict[str, Any]
    summary: Dict[str, Any]

class UniversalTheoryApplicator:
    """Framework for applying any theory schema with multi-stage processing"""
    
    def __init__(self, schema_path: str):
        """Initialize with a theory schema"""
        with open(schema_path, 'r') as f:
            self.schema = yaml.safe_load(f)
        
        self.theory_name = self.schema.get('theory_name', 'Unknown Theory')
        self.stages = self.schema.get('application_stages', self._get_default_stages())
        
    def _get_default_stages(self) -> List[Dict]:
        """Default stages if not specified in schema"""
        return [
            {
                "name": "extraction",
                "description": "Extract all relevant elements from text"
            },
            {
                "name": "filtering", 
                "description": "Filter elements based on theory criteria"
            },
            {
                "name": "structuring",
                "description": "Build theoretical structures"
            },
            {
                "name": "analysis",
                "description": "Calculate derived measures"
            }
        ]
    
    def apply(self, text: str, domain: str = "general") -> TheoryApplication:
        """Apply theory through all stages"""
        print(f"Applying {self.theory_name} to {domain} text...")
        
        stages_results = []
        context = {
            "text": text,
            "domain": domain,
            "previous_stages": {}
        }
        
        # Execute each stage
        for stage_config in self.stages:
            stage_name = stage_config['name']
            print(f"\nExecuting stage: {stage_name}")
            
            stage_result = self._execute_stage(stage_config, context)
            stages_results.append(stage_result)
            
            # Add to context for next stages
            context['previous_stages'][stage_name] = stage_result.data
            
            # Print stage summary
            if 'items' in stage_result.data:
                print(f"  Extracted {len(stage_result.data['items'])} items")
            print(f"  Metadata: {stage_result.metadata}")
        
        # Generate final output
        final_output = self._generate_final_output(stages_results)
        
        # Calculate summary
        summary = self._calculate_summary(final_output)
        
        return TheoryApplication(
            theory_name=self.theory_name,
            stages=stages_results,
            final_output=final_output,
            summary=summary
        )
    
    def _execute_stage(self, stage_config: Dict, context: Dict) -> StageResult:
        """Execute a single stage based on configuration"""
        stage_name = stage_config['name']
        
        # Build prompt from stage configuration
        prompt = self._build_stage_prompt(stage_config, context)
        
        # Get expected output format
        output_format = stage_config.get('output_format', {})
        
        # Call LLM
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system", 
                    "content": f"Execute {stage_name} stage of {self.theory_name} analysis."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        result_data = json.loads(response.choices[0].message.content)
        
        # Post-process if needed
        if 'post_processing' in stage_config:
            result_data = self._post_process(result_data, stage_config['post_processing'])
        
        # Extract metadata
        metadata = self._extract_metadata(result_data, stage_config)
        
        return StageResult(
            stage_name=stage_name,
            data=result_data,
            metadata=metadata
        )
    
    def _build_stage_prompt(self, stage_config: Dict, context: Dict) -> str:
        """Build prompt for a stage from configuration"""
        base_prompt = stage_config.get('prompt_template', '')
        
        # Replace placeholders
        replacements = {
            '{text}': context['text'][:180000],  # Use full O3 capacity
            '{domain}': context['domain'],
            '{theory_name}': self.theory_name
        }
        
        # Add theory-specific elements
        if 'nodes' in self.schema:
            replacements['{node_types}'] = json.dumps(self.schema['nodes'], indent=2)
        if 'connections' in self.schema:
            replacements['{connection_types}'] = json.dumps(self.schema['connections'], indent=2)
        if 'properties' in self.schema:
            replacements['{properties}'] = json.dumps(self.schema['properties'], indent=2)
        if 'modifiers' in self.schema:
            replacements['{modifiers}'] = json.dumps(self.schema['modifiers'], indent=2)
        
        # Add previous stage results
        for stage_name, stage_data in context['previous_stages'].items():
            replacements[f'{{previous.{stage_name}}}'] = json.dumps(stage_data, indent=2)
        
        # Add stage-specific criteria
        if 'criteria' in stage_config:
            criteria_text = "\n".join([f"- {c}" for c in stage_config['criteria']])
            replacements['{criteria}'] = criteria_text
        
        # Add examples if provided
        if 'examples' in stage_config:
            replacements['{examples}'] = json.dumps(stage_config['examples'], indent=2)
        
        # Add output format specification
        if 'output_format' in stage_config:
            replacements['{output_format}'] = json.dumps(stage_config['output_format'], indent=2)
        
        # Perform replacements
        prompt = base_prompt
        for key, value in replacements.items():
            prompt = prompt.replace(key, str(value))
        
        return prompt
    
    def _post_process(self, data: Dict, rules: List[Dict]) -> Dict:
        """Apply post-processing rules to stage output"""
        for rule in rules:
            if rule['type'] == 'filter':
                if 'items' in data:
                    data['items'] = [
                        item for item in data['items']
                        if self._evaluate_filter(item, rule['condition'])
                    ]
            elif rule['type'] == 'transform':
                if 'items' in data:
                    data['items'] = [
                        self._apply_transform(item, rule['operation'])
                        for item in data['items']
                    ]
        return data
    
    def _evaluate_filter(self, item: Dict, condition: Dict) -> bool:
        """Evaluate filter condition"""
        field = condition.get('field')
        operator = condition.get('operator', 'equals')
        value = condition.get('value')
        
        if field not in item:
            return False
            
        if operator == 'equals':
            return item[field] == value
        elif operator == 'contains':
            return value in str(item[field])
        elif operator == 'greater_than':
            return item[field] > value
        elif operator == 'in':
            return item[field] in value
        
        return True
    
    def _apply_transform(self, item: Dict, operation: Dict) -> Dict:
        """Apply transformation to item"""
        op_type = operation.get('type')
        
        if op_type == 'add_field':
            item[operation['field']] = operation['value']
        elif op_type == 'rename_field':
            if operation['from'] in item:
                item[operation['to']] = item.pop(operation['from'])
        
        return item
    
    def _extract_metadata(self, data: Dict, stage_config: Dict) -> Dict:
        """Extract metadata from stage results"""
        metadata = {}
        
        # Count items if present
        if 'items' in data:
            metadata['item_count'] = len(data['items'])
        
        # Extract specified metadata fields
        if 'metadata_fields' in stage_config:
            for field in stage_config['metadata_fields']:
                if field in data:
                    metadata[field] = data[field]
        
        return metadata
    
    def _generate_final_output(self, stages: List[StageResult]) -> Dict:
        """Generate final output from all stages"""
        output = {}
        
        # Get output mapping from schema
        output_mapping = self.schema.get('output_mapping', {})
        
        for mapping_key, mapping_config in output_mapping.items():
            source_stage = mapping_config.get('from_stage')
            source_field = mapping_config.get('from_field')
            
            # Find the stage
            for stage in stages:
                if stage.stage_name == source_stage:
                    if source_field in stage.data:
                        output[mapping_key] = stage.data[source_field]
                    break
        
        # If no mapping, use last stage data
        if not output and stages:
            output = stages[-1].data
        
        return output
    
    def _calculate_summary(self, final_output: Dict) -> Dict:
        """Calculate summary statistics"""
        summary = {}
        
        # Get summary rules from schema
        summary_rules = self.schema.get('summary_rules', [])
        
        for rule in summary_rules:
            if rule['type'] == 'count':
                if rule['field'] in final_output:
                    summary[rule['name']] = len(final_output[rule['field']])
            elif rule['type'] == 'calculate':
                if rule['operation'] == 'connectedness':
                    # Example calculation
                    nodes = len(final_output.get(rule['nodes_field'], []))
                    edges = len(final_output.get(rule['edges_field'], []))
                    if nodes + edges > 0:
                        summary[rule['name']] = edges / (nodes + edges)
        
        return summary

def save_application_result(result: TheoryApplication, output_path: str):
    """Save theory application result as YAML"""
    
    # Convert to serializable format
    output = {
        'theory': result.theory_name,
        'stages_executed': [s.stage_name for s in result.stages],
        'final_output': result.final_output,
        'summary': result.summary,
        'stage_details': []
    }
    
    # Add stage details
    for stage in result.stages:
        stage_detail = {
            'stage': stage.stage_name,
            'metadata': stage.metadata
        }
        # Include sample data if not too large
        if 'items' in stage.data and len(stage.data['items']) > 0:
            stage_detail['sample_items'] = stage.data['items'][:3]
            stage_detail['total_items'] = len(stage.data['items'])
        output['stage_details'].append(stage_detail)
    
    with open(output_path, 'w') as f:
        yaml.dump(output, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    
    print(f"\nResults saved to: {output_path}")

def main():
    if len(sys.argv) < 4:
        print("Usage: python universal_theory_applicator.py <text_file> <schema_file> <output_file> [domain]")
        sys.exit(1)
    
    text_path = sys.argv[1]
    schema_path = sys.argv[2]
    output_path = sys.argv[3]
    domain = sys.argv[4] if len(sys.argv) > 4 else "general"
    
    # Load text
    with open(text_path, 'r') as f:
        text = f.read()
    
    # Create applicator
    applicator = UniversalTheoryApplicator(schema_path)
    
    # Apply theory
    result = applicator.apply(text, domain)
    
    # Save results
    save_application_result(result, output_path)

if __name__ == "__main__":
    main()