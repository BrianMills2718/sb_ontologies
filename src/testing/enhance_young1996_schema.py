#!/usr/bin/env python3
"""
Enhance Young 1996 schema to include missing components
Add reasoning methods, dependency calculation, and salience tracking
"""
import yaml
import os
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def create_enhanced_schema():
    """Create enhanced Young 1996 schema with missing components"""
    
    enhanced_schema = {
        'citation': "Young, Michael D. 1996. Cognitive Mapping Meets Semantic Networks. Journal of Conflict Resolution 40(3): 395-414.",
        'model_type': "WorldView enhanced cognitive mapping using semantic‐network formalism",
        'rationale': """Young introduces WorldView to eliminate the limits of adjacency–matrix cognitive maps by
(a) elevating relationships to nodes within a semantic network,
(b) differentiating relationship kinds, truth-values and modifiers,
(c) retaining conjunctions, actions and salience counts,
(d) supplying a synonym facility and aggregation routines, and
(e) providing structural and comparative measures (dependency, connectedness, size, uniformity of salience, concept comparison, transformation cost, incongruence),
(f) enabling dynamic reasoning through directed-walk and spreading activation.""",
        
        'schema_blueprint': {
            'title': "Young 1996 Cognitive Mapping Schema (Complete Implementation)",
            'description': """Complete transcription of WorldView system including reasoning methods, 
all structural measures, and dynamic processing capabilities as described in Young 1996.""",
            
            'definitions': {
                'node_types': {
                    'Concept': "Unique term appearing in the text; becomes a node.",
                    'Relationship': "A node that links concepts; carries truth-value, modifier, salience.",
                    'Conjunction': "Node representing 'and' or 'or' used with compound concepts."
                },
                
                'relationship_categories': {
                    '=': "equal",
                    '>': "condition component preference / greater-than", 
                    '+': "positive-cause",
                    '-': "negative-cause",
                    'attribute': "property (attribute) relationship",
                    'is-a': "class inclusion",
                    'if-then': "conditional relationship",
                    'possess': "ownership relationship",
                    'strategy': "means–ends relationship",
                    'know': "knowledge relationship",
                    'warrant-for': "justification relationship",
                    'location': "spatial relationship"
                },
                
                'truth_values': ['true', 'false', 'partial', 'possible', 'impossible'],
                'relationship_modifiers': ['past', 'present', 'future', 'goal', 'hypothetical', 'normative'],
                'conjunctions': ['and', 'or'],
                
                'salience': {
                    'definition': "Integer count of how often a unique relationship occurs in the data set.",
                    'calculation': "Count frequency of identical subject-relation-object triples across text"
                },
                
                'structural_measures': {
                    'dependency': {
                        'symbol': "D_G",
                        'formula': "D_G = ( Σ bridges_G / Σ relationships_G ) / Σ structures_G",
                        'interpretation': "Vertical organization; proportion of bridges per structure.",
                        'implementation': "Count relationships that are the only path to a concept (bridges)"
                    },
                    'connectedness': {
                        'symbol': "C_G", 
                        'formula': "C_G = Σ relationships_G / ( Σ concepts_G + Σ relationships_G )",
                        'interpretation': "Degree to which concepts are interrelated.",
                        'implementation': "Calculate ratio of relationships to total elements"
                    },
                    'size': {
                        'definition': "Count of concepts in the cognitive map.",
                        'implementation': "Count unique concept nodes"
                    },
                    'uniformity_of_salience': {
                        'definition': "Standard deviation of relationship salience values within the map.",
                        'implementation': "Calculate std dev of all relationship salience scores"
                    }
                },
                
                'comparative_measures': {
                    'concept_comparison': "Lists identical, altered and unique concepts across two maps.",
                    'transformation_cost': {
                        'definition': """Minimum number of discrete changes (relationship-addition, relationship-deletion,
salience increment/decrement, concept-deletion, concept-addition) needed to turn one map into another; each change has cost 1.""",
                        'implementation': "Levenshtein-style edit distance between cognitive maps"
                    },
                    'incongruence': {
                        'definition': """Measure combining transformation cost and concept comparison, restricted to
concepts common to both maps; zero only for identical structures.""",
                        'implementation': "Compare overlapping concepts between maps over time"
                    }
                },
                
                'reasoning_methods': {
                    'directed_walk': {
                        'description': "Spreading activation reasoning model using salience heuristic",
                        'algorithm': """1. Start with input proposition
2. Find proposition with highest salience to activate
3. Process indicated operations
4. Select most salient proposition from conclusion
5. Repeat until no further progress (policy output or integration complete)""",
                        'implementation': "Search cognitive map using salience weights to guide activation",
                        'example_output': """(soviet-union invade true present afghanistan)
→ (soviet-union is-a true present sovereign-nation)
→ (united-states resist true hypothetical (sovereign-nation invade true present sovereign-nation))"""
                    },
                    'spreading_activation': {
                        'description': "Generate definition of situation through network traversal",
                        'implementation': "Activate related concepts based on semantic network connections"
                    },
                    'explanation_based_reasoning': {
                        'description': "Use belief system structure to explain and predict decisions",
                        'implementation': "Follow causal chains and strategic relationships"
                    }
                },
                
                'support_features': {
                    'synonym_facility': {
                        'definition': "User-defined mapping that collapses synonymous concepts during compilation.",
                        'implementation': "Create synonym dictionary and apply during concept aggregation"
                    },
                    'aggregation': {
                        'definition': "Combines multiple texts or subject responses into a composite map.",
                        'implementation': "Merge concept nodes and sum relationship saliences across texts"
                    },
                    'manipulable_map': {
                        'definition': "Semantic-network format that reasoning models can traverse.",
                        'implementation': "Store as graph structure with node/edge attributes accessible to algorithms"
                    },
                    'content_analysis': {
                        'definition': "Systematic coding to extract subject-relation-object triples from text",
                        'implementation': "Parse text to identify concepts and relationships using coding rules"
                    }
                },
                
                'extraction_requirements': {
                    'salience_counting': "Count frequency of each unique relationship across all text",
                    'bridge_identification': "Identify relationships that are sole paths to concepts",
                    'structure_counting': "Count disconnected components in cognitive map",
                    'multi_text_processing': "Process multiple texts and aggregate results",
                    'temporal_tracking': "Track belief structure changes over time"
                }
            }
        }
    }
    
    return enhanced_schema

def save_enhanced_schema():
    """Save the enhanced schema to file"""
    schema = create_enhanced_schema()
    
    output_path = Path('/home/brian/lit_review/literature/operational_code_analysis/young1996_complete.yml')
    with open(output_path, 'w') as f:
        yaml.dump(schema, f, default_flow_style=False, sort_keys=False)
    
    return output_path

def main():
    """Create enhanced Young 1996 schema"""
    print("🔧 ENHANCING YOUNG 1996 SCHEMA")
    print("=" * 50)
    print("Adding missing components:")
    print("• Directed-walk reasoning algorithm")
    print("• Dependency calculation method") 
    print("• Salience frequency tracking")
    print("• Multi-text aggregation")
    print("• Complete structural measures")
    print()
    
    output_path = save_enhanced_schema()
    print(f"✅ Enhanced schema saved to: {output_path}")
    
    # Validate schema
    with open(output_path, 'r') as f:
        schema = yaml.safe_load(f)
    
    reasoning_methods = len(schema['schema_blueprint']['definitions']['reasoning_methods'])
    structural_measures = len(schema['schema_blueprint']['definitions']['structural_measures'])
    
    print()
    print("📊 ENHANCED SCHEMA COMPONENTS:")
    print(f"   Reasoning methods: {reasoning_methods}")
    print(f"   Structural measures: {structural_measures}")
    print(f"   Relationship categories: {len(schema['schema_blueprint']['definitions']['relationship_categories'])}")
    print(f"   Support features: {len(schema['schema_blueprint']['definitions']['support_features'])}")
    print()
    print("🎯 NOW INCLUDES:")
    print("✓ Directed-walk algorithm specification")
    print("✓ Dependency calculation instructions")
    print("✓ Salience frequency counting")
    print("✓ Bridge identification method")
    print("✓ Multi-text aggregation process")
    print("✓ All comparative measures")

if __name__ == "__main__":
    main()