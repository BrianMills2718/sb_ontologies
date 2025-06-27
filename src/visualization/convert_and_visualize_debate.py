#!/usr/bin/env python3
"""
Convert and visualize debate SH instance with enhanced format
"""

import yaml
import json
from pathlib import Path

def convert_debate_instance(input_path: str, output_path: str):
    """Convert debate instance to standard format"""
    
    with open(input_path, 'r') as f:
        data = yaml.safe_load(f)
    
    # Create converted instance
    converted = {
        "schema_reference": data.get("schema_reference"),
        "model_type": data.get("model_type"),
        "instance": {
            "vertices": [],
            "hyperedges": [],
            "atoms": [],
            "connectors": []
        }
    }
    
    # Convert atoms
    for atom in data['instance']['atoms']:
        atom_data = {
            "id": atom['id'],
            "term": atom['term'],
            "type": atom['type']
        }
        if atom.get('roles'):
            atom_data['roles'] = atom['roles']
            
        converted['instance']['atoms'].append(atom_data)
        
        # Add concepts as vertices
        if atom['type'] == 'C':
            converted['instance']['vertices'].append({
                "id": atom['id'],
                "label": atom['term'].replace('_', ' '),
                "type": "concept"
            })
        
        # Track connectors
        if atom['type'] in ['P', 'B', 'M', 'T', 'J']:
            connector_data = {
                "id": atom['id'],
                "term": atom['term'],
                "type": atom['type']
            }
            if atom.get('roles'):
                connector_data['roles'] = atom['roles']
            converted['instance']['connectors'].append(connector_data)
    
    # Convert hyperedges
    for he in data['instance']['hyperedges']:
        he_data = {
            "id": he['id'],
            "connector_id": he['connector']['id'],
            "connector_type": he['connector']['type'],
            "arguments": he['arguments'],
            "ordered": he.get('ordered', True)
        }
        
        # Add roles if present
        if he['connector'].get('roles'):
            he_data['connector_roles'] = he['connector']['roles']
        if he.get('argument_roles'):
            he_data['argument_roles'] = he['argument_roles']
        if he.get('truth_value'):
            he_data['truth_value'] = he['truth_value']
        if he.get('modifiers'):
            he_data['modifiers'] = he['modifiers']
            
        converted['instance']['hyperedges'].append(he_data)
    
    converted['instance']['main_hyperedge'] = data['instance']['main_hyperedge']
    
    # Save converted version
    with open(output_path, 'w') as f:
        yaml.dump(converted, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    
    print(f"Converted instance saved to: {output_path}")

if __name__ == "__main__":
    input_file = "/home/brian/lit_review/results/semantic_hypergraph/iran_debate/iran_debate_sh_instance.yml"
    output_file = "/home/brian/lit_review/results/semantic_hypergraph/iran_debate/iran_debate_converted.yml"
    
    convert_debate_instance(input_file, output_file)