#!/usr/bin/env python3
"""
Script to analyze all YAML files in the literature directory and extract comprehensive statistics.
"""

import os
import yaml
import sys
from collections import defaultdict, Counter
from pathlib import Path
import glob

def analyze_yaml_file(file_path):
    """Analyze a single YAML file and extract statistics."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # Extract basic information
        citation = data.get('citation', 'N/A')
        annotation = data.get('annotation', 'N/A')
        model_type = data.get('model_type', 'N/A')
        rationale = data.get('rationale', 'N/A')
        
        # Extract schema blueprint information
        schema_blueprint = data.get('schema_blueprint', {})
        title = schema_blueprint.get('title', 'N/A')
        description = schema_blueprint.get('description', 'N/A')
        definitions = schema_blueprint.get('definitions', [])
        
        # Check for JSON schema
        has_json_schema = 'json_schema' in data and data['json_schema'] is not None
        
        # Count definitions by category
        categories = Counter()
        total_definitions = len(definitions)
        
        for definition in definitions:
            if isinstance(definition, dict):
                category = definition.get('category', 'unknown')
                categories[category] += 1
        
        # Calculate file size metrics
        file_size = os.path.getsize(file_path)
        
        return {
            'file_path': file_path,
            'citation': citation,
            'annotation': annotation,
            'model_type': model_type,
            'rationale': rationale,
            'title': title,
            'description': description,
            'total_definitions': total_definitions,
            'categories': dict(categories),
            'has_json_schema': has_json_schema,
            'file_size_bytes': file_size,
            'annotation_length': len(annotation) if annotation != 'N/A' else 0,
            'rationale_length': len(rationale) if rationale != 'N/A' else 0
        }
    
    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")
        return None

def main():
    """Main analysis function."""
    literature_dir = "/home/brian/lit_review/literature"
    
    # Find all YAML files
    yaml_files = []
    for root, dirs, files in os.walk(literature_dir):
        for file in files:
            if file.endswith('.yml'):
                yaml_files.append(os.path.join(root, file))
    
    print(f"Found {len(yaml_files)} YAML files")
    print("=" * 80)
    
    # Analyze each file
    results = []
    for yaml_file in sorted(yaml_files):
        result = analyze_yaml_file(yaml_file)
        if result:
            results.append(result)
    
    # Aggregate statistics
    print(f"Successfully analyzed {len(results)} files")
    print("\nSUMMARY STATISTICS")
    print("=" * 80)
    
    # Model types distribution
    model_types = Counter(r['model_type'] for r in results)
    print(f"\nModel Types Distribution:")
    for model_type, count in model_types.most_common():
        print(f"  {model_type}: {count}")
    
    # JSON schema presence
    with_json_schema = sum(1 for r in results if r['has_json_schema'])
    print(f"\nJSON Schema Presence:")
    print(f"  With JSON schema: {with_json_schema}")
    print(f"  Without JSON schema: {len(results) - with_json_schema}")
    print(f"  Percentage with schema: {with_json_schema/len(results)*100:.1f}%")
    
    # Definition counts
    definition_counts = [r['total_definitions'] for r in results]
    print(f"\nDefinition Counts:")
    print(f"  Total definitions across all files: {sum(definition_counts)}")
    print(f"  Average definitions per file: {sum(definition_counts)/len(results):.1f}")
    print(f"  Minimum definitions: {min(definition_counts)}")
    print(f"  Maximum definitions: {max(definition_counts)}")
    
    # Most common categories
    all_categories = Counter()
    for result in results:
        for category, count in result['categories'].items():
            all_categories[category] += count
    
    print(f"\nTop 15 Most Common Vocabulary Categories:")
    for category, count in all_categories.most_common(15):
        print(f"  {category}: {count}")
    
    # File size statistics
    file_sizes = [r['file_size_bytes'] for r in results]
    print(f"\nFile Size Statistics:")
    print(f"  Average file size: {sum(file_sizes)/len(results):.0f} bytes")
    print(f"  Smallest file: {min(file_sizes)} bytes")
    print(f"  Largest file: {max(file_sizes)} bytes")
    
    # Print detailed results for each file
    print(f"\nDETAILED FILE ANALYSIS")
    print("=" * 80)
    
    for result in sorted(results, key=lambda x: x['total_definitions'], reverse=True):
        print(f"\nFile: {os.path.basename(result['file_path'])}")
        print(f"  Model Type: {result['model_type']}")
        print(f"  Total Definitions: {result['total_definitions']}")
        print(f"  Has JSON Schema: {result['has_json_schema']}")
        print(f"  File Size: {result['file_size_bytes']} bytes")
        print(f"  Top Categories: {', '.join([f'{cat}({count})' for cat, count in Counter(result['categories']).most_common(5)])}")
        
        # Print citation (truncated)
        citation = result['citation']
        if len(citation) > 100:
            citation = citation[:97] + "..."
        print(f"  Citation: {citation}")
    
    print(f"\nTotal files analyzed: {len(results)}")
    print(f"Total definitions across all schemas: {sum(r['total_definitions'] for r in results)}")
    print(f"Total unique categories: {len(all_categories)}")

if __name__ == "__main__":
    main()