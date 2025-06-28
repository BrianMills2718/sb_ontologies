#!/usr/bin/env python3
"""
Test the universal applicator with a small example
"""

import os
import json
import yaml
from universal_theory_applicator import UniversalTheoryApplicator, save_application_result

def create_test_schema():
    """Create a simple test schema to demonstrate universality"""
    
    test_schema = {
        "theory_name": "Simple Entity-Relationship Extraction",
        
        "nodes": [
            {
                "type": "entity",
                "description": "Things discussed in text"
            }
        ],
        
        "connections": [
            {
                "type": "relationship",
                "vocabulary": ["relates_to", "interacts_with", "affects"]
            }
        ],
        
        "application_stages": [
            {
                "name": "extraction",
                "description": "Extract all entities",
                "prompt_template": """Extract all entities (people, places, things, concepts) from this text.

TEXT:
{text}

Return as JSON:
{
  "items": [
    {"entity": "entity_name", "type": "person|place|thing|concept"}
  ]
}""",
                "output_format": {
                    "items": [
                        {"entity": "string", "type": "string"}
                    ]
                }
            },
            {
                "name": "filtering",
                "description": "Filter for domain relevance",
                "prompt_template": """Filter these entities for relevance to {domain}.

ENTITIES:
{previous.extraction}

For {domain} domain, apply these criteria:
{criteria}

Return as JSON:
{
  "items": [
    {"id": "e1", "label": "entity_name", "type": "type", "included": true, "reason": "why included/excluded"}
  ]
}""",
                "criteria": [
                    "INCLUDE: Main topics and subjects",
                    "INCLUDE: Key actors and participants", 
                    "EXCLUDE: Passing mentions",
                    "EXCLUDE: Generic references"
                ],
                "post_processing": [
                    {
                        "type": "filter",
                        "condition": {
                            "field": "included",
                            "operator": "equals",
                            "value": True
                        }
                    }
                ]
            },
            {
                "name": "structuring",
                "description": "Find relationships",
                "prompt_template": """Find relationships between these entities.

ENTITIES:
{previous.filtering}

TEXT:
{text}

Return as JSON:
{
  "relationships": [
    {"source": "entity_id", "type": "relationship_type", "target": "entity_id"}
  ]
}"""
            }
        ],
        
        "output_mapping": {
            "entities": {
                "from_stage": "filtering",
                "from_field": "items"
            },
            "relationships": {
                "from_stage": "structuring",
                "from_field": "relationships"
            }
        },
        
        "summary_rules": [
            {
                "name": "total_entities",
                "type": "count",
                "field": "entities"
            },
            {
                "name": "total_relationships",
                "type": "count",
                "field": "relationships"
            }
        ]
    }
    
    # Save test schema
    with open('/tmp/test_schema.yml', 'w') as f:
        yaml.dump(test_schema, f)
    
    return '/tmp/test_schema.yml'

def test_with_sample_text():
    """Test with a simple text"""
    
    sample_text = """
    Alice works at TechCorp, a leading software company in Silicon Valley. 
    She collaborates with Bob on the new AI project. 
    The project aims to revolutionize customer service.
    Bob reports to Carol, the head of engineering.
    TechCorp recently partnered with DataSystems to expand their capabilities.
    """
    
    # Save sample text
    with open('/tmp/test_text.txt', 'w') as f:
        f.write(sample_text)
    
    # Create test schema
    schema_path = create_test_schema()
    
    # Create applicator
    applicator = UniversalTheoryApplicator(schema_path)
    
    # Apply theory
    print("Testing Universal Theory Applicator\n")
    print(f"Theory: {applicator.theory_name}")
    print(f"Stages: {[s['name'] for s in applicator.stages]}")
    print("\nApplying to test text...")
    
    result = applicator.apply(sample_text, domain="technology")
    
    # Save results
    save_application_result(result, '/tmp/test_output.yml')
    
    # Print summary
    print("\n=== RESULTS ===")
    print(f"Theory: {result.theory_name}")
    print(f"Stages executed: {[s.stage_name for s in result.stages]}")
    print(f"\nSummary: {result.summary}")
    
    # Show sample output
    if 'entities' in result.final_output:
        print(f"\nSample entities: {result.final_output['entities'][:3]}")
    if 'relationships' in result.final_output:
        print(f"\nSample relationships: {result.final_output['relationships'][:3]}")
    
    print("\nDemonstration complete! This same framework works for ANY theory.")
    
    return result

def demonstrate_young_universal():
    """Show how Young theory works with universal applicator"""
    
    print("\n\n=== DEMONSTRATING WITH YOUNG 1996 ===")
    
    # Sample political text
    carter_excerpt = """
    The United States and the Soviet Union must negotiate to reduce nuclear weapons.
    President Carter believes that peace requires cooperation between the superpowers.
    The SALT talks represent our commitment to arms control and global security.
    """
    
    with open('/tmp/carter_excerpt.txt', 'w') as f:
        f.write(carter_excerpt)
    
    # Use enhanced Young schema
    young_schema_path = 'schemas/young1996/young1996_enhanced.yml'
    
    if os.path.exists(young_schema_path):
        applicator = UniversalTheoryApplicator(young_schema_path)
        result = applicator.apply(carter_excerpt, domain="diplomatic speech")
        
        print(f"\nYoung 1996 Results:")
        print(f"Stages: {[s.stage_name for s in result.stages]}")
        print(f"Summary: {result.summary}")
    else:
        print("Enhanced Young schema not found - create it first!")

if __name__ == "__main__":
    # Test with simple schema
    test_result = test_with_sample_text()
    
    # Demonstrate with Young if available
    demonstrate_young_universal()