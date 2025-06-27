#!/usr/bin/env python3
"""
Compare outputs from original and improved multiphase processors
"""

import yaml
import json
from pathlib import Path
from typing import Dict, List, Set

def load_yaml(path: str) -> Dict:
    """Load YAML file"""
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def analyze_schema(data: Dict) -> Dict:
    """Analyze schema structure and content"""
    definitions = data.get('schema_blueprint', {}).get('definitions', [])
    
    # Count by category
    categories = {}
    domain_range_pairs = set()
    subcategories = set()
    
    for defn in definitions:
        cat = defn.get('category', 'unknown')
        categories[cat] = categories.get(cat, 0) + 1
        
        # Track domain/range specificity
        if 'domain' in defn and 'range' in defn:
            for d in defn['domain']:
                for r in defn['range']:
                    if d != 'Entity' or r != 'Entity':  # Non-generic
                        domain_range_pairs.add(f"{d}→{r}")
        
        # Track subcategories
        if cat not in ['entity', 'relationship', 'property', 'action', 'measure', 'modifier', 'truth-value', 'operator']:
            subcategories.add(cat)
        
        # Track subTypeOf hierarchies
        if 'subTypeOf' in defn:
            subcategories.add(f"{defn['name']} subTypeOf {defn['subTypeOf']}")
    
    return {
        'total_definitions': len(definitions),
        'categories': categories,
        'specific_domain_range': len(domain_range_pairs),
        'domain_range_examples': list(domain_range_pairs)[:10],
        'subcategories': len(subcategories),
        'subcategory_examples': list(subcategories)[:10],
        'model_type': data.get('model_type', 'unknown'),
        'has_modifiers': any(d.get('category') == 'modifier' for d in definitions),
        'has_truth_values': any(d.get('category') == 'truth-value' for d in definitions),
        'has_operators': any(d.get('category') == 'operator' for d in definitions),
    }

def compare_schemas(original_path: str, improved_path: str):
    """Compare original and improved schemas"""
    print(f"\nComparing schemas:")
    print(f"Original: {original_path}")
    print(f"Improved: {improved_path}")
    print("=" * 80)
    
    # Load schemas
    original = load_yaml(original_path)
    improved = load_yaml(improved_path)
    
    # Analyze both
    orig_analysis = analyze_schema(original)
    imp_analysis = analyze_schema(improved)
    
    # Compare total definitions
    print(f"\nTotal Definitions:")
    print(f"  Original: {orig_analysis['total_definitions']}")
    print(f"  Improved: {imp_analysis['total_definitions']}")
    print(f"  Change: {imp_analysis['total_definitions'] - orig_analysis['total_definitions']:+d}")
    
    # Compare categories
    print(f"\nCategories:")
    all_cats = set(orig_analysis['categories'].keys()) | set(imp_analysis['categories'].keys())
    for cat in sorted(all_cats):
        orig_count = orig_analysis['categories'].get(cat, 0)
        imp_count = imp_analysis['categories'].get(cat, 0)
        if orig_count != imp_count:
            print(f"  {cat}: {orig_count} → {imp_count} ({imp_count - orig_count:+d})")
    
    # Compare domain/range specificity
    print(f"\nDomain/Range Specificity:")
    print(f"  Original specific pairs: {orig_analysis['specific_domain_range']}")
    print(f"  Improved specific pairs: {imp_analysis['specific_domain_range']}")
    if imp_analysis['domain_range_examples']:
        print(f"  Examples: {', '.join(imp_analysis['domain_range_examples'][:5])}")
    
    # Compare subcategorization
    print(f"\nSubcategorization:")
    print(f"  Original subcategories: {orig_analysis['subcategories']}")
    print(f"  Improved subcategories: {imp_analysis['subcategories']}")
    if imp_analysis['subcategory_examples']:
        print(f"  Examples: {', '.join(imp_analysis['subcategory_examples'][:5])}")
    
    # Compare features
    print(f"\nFeatures:")
    print(f"  Model Type: {orig_analysis['model_type']} → {imp_analysis['model_type']}")
    print(f"  Has Modifiers: {orig_analysis['has_modifiers']} → {imp_analysis['has_modifiers']}")
    print(f"  Has Truth Values: {orig_analysis['has_truth_values']} → {imp_analysis['has_truth_values']}")
    print(f"  Has Operators: {orig_analysis['has_operators']} → {imp_analysis['has_operators']}")
    
    # Show improved rationale
    if imp_analysis['model_type'] != orig_analysis['model_type']:
        print(f"\nModel Type Rationale:")
        print(f"  {improved.get('rationale', 'No rationale provided')}")

def main():
    """Run comparisons"""
    # Find pairs to compare
    comparisons = [
        ("literature/operational_code_analysis/young1996_multiphase.yml",
         "literature/operational_code_analysis/young1996_improved.yml"),
        ("literature/influence_operations/foundations_framework_multiphase.yml",
         "literature/influence_operations/foundations_framework_improved.yml"),
    ]
    
    for orig, imp in comparisons:
        if Path(orig).exists() and Path(imp).exists():
            compare_schemas(orig, imp)
        else:
            print(f"\nSkipping comparison - files not found:")
            print(f"  {orig}: {'exists' if Path(orig).exists() else 'missing'}")
            print(f"  {imp}: {'exists' if Path(imp).exists() else 'missing'}")

if __name__ == "__main__":
    main()