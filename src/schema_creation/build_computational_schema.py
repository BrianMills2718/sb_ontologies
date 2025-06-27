#!/usr/bin/env python3
"""
Build Computationally Complete Schema Programmatically
Avoids YAML parsing issues by constructing schema directly
"""
import yaml
from pathlib import Path

def build_young1996_computational_schema():
    """Build complete computational schema for Young 1996"""
    
    schema = {
        'citation': 'Young, Michael D. 1996. "Cognitive Mapping Meets Semantic Networks." Journal of Conflict Resolution 40(3): 395-414.',
        'theory_name': 'WorldView Cognitive Mapping',
        'version': 'computational_complete_1.0',
        'description': 'Complete computational implementation of Young 1996 with step-by-step algorithms',
        
        # Core elements from Young's paper
        'core_elements': {
            'relationship_categories': {
                '+': 'positive-cause',
                '-': 'negative-cause', 
                '=': 'equal',
                '>': 'condition component preference / greater-than',
                'attribute': 'property (attribute) relationship',
                'is-a': 'class inclusion',
                'if-then': 'conditional relationship',
                'possess': 'ownership relationship',
                'strategy': 'means–ends relationship',
                'know': 'knowledge relationship',
                'warrant-for': 'justification relationship',
                'location': 'spatial relationship'
            },
            
            'truth_values': ['true', 'false', 'partial', 'possible', 'impossible'],
            'modifiers': ['past', 'present', 'future', 'goal', 'hypothetical', 'normative'],
            'conjunctions': ['and', 'or']
        },
        
        # Step-by-step computational algorithms
        'algorithms': {
            'concept_extraction': {
                'input': 'raw text string',
                'description': 'Extract unique concepts from text as cognitive map nodes',
                'procedure': [
                    {
                        'step': 1,
                        'action': 'identify_entities',
                        'implementation': 'Extract nouns, noun phrases, and proper names from text',
                        'instruction': 'Find all unique entities mentioned (people, places, concepts, objects)'
                    },
                    {
                        'step': 2,
                        'action': 'create_concept_nodes',
                        'implementation': 'Assign unique IDs (C1, C2, etc.) and canonical labels',
                        'instruction': 'Create concept objects with id, label, and node_type=Concept'
                    },
                    {
                        'step': 3,
                        'action': 'apply_synonym_facility',
                        'implementation': 'Merge synonymous concepts into single nodes',
                        'instruction': 'Identify and collapse different terms for same concept'
                    }
                ],
                'output': 'List of concept objects with unique IDs and labels'
            },
            
            'relationship_extraction': {
                'input': 'raw text string + concept list',
                'description': 'Extract typed relationships between concepts',
                'procedure': [
                    {
                        'step': 1,
                        'action': 'identify_subject_relation_object_triples',
                        'implementation': 'Parse sentences for subject-verb-object patterns',
                        'instruction': 'Find statements connecting concepts through verbs or relationships'
                    },
                    {
                        'step': 2,
                        'action': 'classify_relationship_type',
                        'implementation': 'Match verbs/phrases to relationship_categories',
                        'instruction': 'Use Young category list: +, -, =, strategy, is-a, if-then, etc.'
                    },
                    {
                        'step': 3,
                        'action': 'assign_truth_values',
                        'implementation': 'Detect certainty indicators in text',
                        'instruction': 'Assign true/false/partial/possible/impossible based on language'
                    },
                    {
                        'step': 4,
                        'action': 'assign_modifiers',
                        'implementation': 'Detect temporal and logical modifiers',
                        'instruction': 'Apply past/present/future/goal/hypothetical/normative from context'
                    }
                ],
                'output': 'List of relationship objects with from/to concept IDs, category, truth_value, modifiers'
            },
            
            'salience_calculation': {
                'input': 'relationship list + raw text',
                'description': 'Count actual frequency of relationships for salience scores',
                'procedure': [
                    {
                        'step': 1,
                        'action': 'normalize_relationships',
                        'implementation': 'Standardize relationship representations',
                        'instruction': 'Convert all relationships to canonical subject-relation-object form'
                    },
                    {
                        'step': 2,
                        'action': 'count_frequencies',
                        'implementation': 'Count occurrences of identical relationships across text',
                        'instruction': 'For each unique relationship, count how many times it appears'
                    },
                    {
                        'step': 3,
                        'action': 'assign_salience_scores',
                        'implementation': 'Set salience = frequency count for each relationship',
                        'instruction': 'Replace default salience=1 with actual frequency counts'
                    }
                ],
                'output': 'Relationships with accurate salience scores reflecting frequency'
            },
            
            'dependency_calculation': {
                'input': 'concept list + relationship list',
                'description': 'Calculate Young dependency measure: D_G = (bridges/relationships)/structures',
                'procedure': [
                    {
                        'step': 1,
                        'action': 'create_network_graph',
                        'implementation': 'Build graph with concepts as nodes, relationships as edges',
                        'instruction': 'Create undirected graph for structural analysis'
                    },
                    {
                        'step': 2,
                        'action': 'identify_bridges',
                        'implementation': 'Find edges whose removal increases connected components',
                        'instruction': 'Bridge = relationship that is only path to a concept'
                    },
                    {
                        'step': 3,
                        'action': 'count_structures',
                        'implementation': 'Count number of disconnected components',
                        'instruction': 'Structure = connected subgraph in cognitive map'
                    },
                    {
                        'step': 4,
                        'action': 'calculate_dependency',
                        'implementation': 'Apply Young formula: D_G = (bridges/relationships)/structures',
                        'instruction': 'Compute final dependency score (0 to 1)'
                    }
                ],
                'output': 'Dependency score with bridge count and structure count'
            },
            
            'connectedness_calculation': {
                'input': 'concept list + relationship list',
                'description': 'Calculate Young connectedness measure: C_G = relationships/(concepts+relationships)',
                'procedure': [
                    {
                        'step': 1,
                        'action': 'count_elements',
                        'implementation': 'Count total concepts and relationships',
                        'instruction': 'Get len(concepts) and len(relationships)'
                    },
                    {
                        'step': 2,
                        'action': 'calculate_connectedness',
                        'implementation': 'Apply Young formula: C_G = relationships/(concepts+relationships)',
                        'instruction': 'Compute connectedness ratio (0 to 1)'
                    }
                ],
                'output': 'Connectedness score showing network integration'
            },
            
            'directed_walk_reasoning': {
                'input': 'cognitive map + starting proposition',
                'description': 'Implement Young directed-walk algorithm using salience heuristic',
                'procedure': [
                    {
                        'step': 1,
                        'action': 'find_starting_concept',
                        'implementation': 'Match proposition terms to concept labels',
                        'instruction': 'Identify which concept in map corresponds to input proposition'
                    },
                    {
                        'step': 2,
                        'action': 'select_highest_salience_relationship',
                        'implementation': 'From current concept, choose outgoing edge with max salience',
                        'instruction': 'Use salience heuristic to guide activation'
                    },
                    {
                        'step': 3,
                        'action': 'traverse_to_target',
                        'implementation': 'Move to target concept of selected relationship',
                        'instruction': 'Follow relationship to next concept in reasoning chain'
                    },
                    {
                        'step': 4,
                        'action': 'repeat_until_termination',
                        'implementation': 'Continue steps 2-3 until no outgoing edges or max steps',
                        'instruction': 'End when reaching terminal concept or step limit'
                    }
                ],
                'output': 'Sequence of reasoning steps with concepts and relationships traversed'
            }
        },
        
        # Automated execution instructions
        'execution_template': {
            'preprocessing': [
                'Split text into sentences',
                'Identify sentence boundaries', 
                'Extract grammatical patterns'
            ],
            'main_processing': [
                'Execute concept_extraction algorithm',
                'Execute relationship_extraction algorithm',
                'Execute salience_calculation algorithm',
                'Execute dependency_calculation algorithm',
                'Execute connectedness_calculation algorithm'
            ],
            'optional_processing': [
                'Execute directed_walk_reasoning if starting proposition provided'
            ],
            'output_format': {
                'concepts': 'List of concept objects with id, label, frequency',
                'relationships': 'List with from/to, category, truth_value, modifiers, salience',
                'structural_measures': 'Object with dependency, connectedness, size',
                'directed_walk': 'Optional reasoning sequence if executed'
            }
        },
        
        # Validation criteria
        'validation': {
            'required_elements': [
                'All concepts have unique IDs',
                'All relationships reference valid concept IDs',
                'Relationship categories from Young taxonomy only',
                'Truth values from Young list only',
                'Salience scores are positive integers',
                'Structural measures calculated with provided formulas'
            ],
            'quality_checks': [
                'Salience scores > 1 indicate actual frequency counting',
                'Dependency score between 0 and 1',
                'Connectedness score between 0 and 1',
                'At least 3 relationship categories used',
                'Multiple truth values and modifiers applied'
            ]
        }
    }
    
    return schema

def create_execution_prompt(schema, text):
    """Create API prompt using computational schema"""
    
    algorithms = schema['algorithms']
    core_elements = schema['core_elements']
    
    prompt = f"""Execute Young 1996 cognitive mapping analysis using computational algorithms.

RELATIONSHIP CATEGORIES TO USE:
{core_elements['relationship_categories']}

TRUTH VALUES TO USE:
{core_elements['truth_values']}

MODIFIERS TO USE:
{core_elements['modifiers']}

STEP-BY-STEP EXECUTION:

1. CONCEPT EXTRACTION:
{algorithms['concept_extraction']['procedure']}

2. RELATIONSHIP EXTRACTION:
{algorithms['relationship_extraction']['procedure']}

3. SALIENCE CALCULATION:
{algorithms['salience_calculation']['procedure']}

4. STRUCTURAL MEASURES:
- Dependency: {algorithms['dependency_calculation']['procedure']}
- Connectedness: {algorithms['connectedness_calculation']['procedure']}

TEXT TO ANALYZE:
{text[:6000]}

EXECUTE EACH ALGORITHM STEP-BY-STEP. 
COUNT ACTUAL FREQUENCIES FOR SALIENCE.
CALCULATE MEASURES USING FORMULAS.

OUTPUT JSON:
{{
  "concepts": [
    {{"id": "C1", "label": "concept name", "frequency": count}}
  ],
  "relationships": [
    {{"from": "C1", "to": "C2", "category": "+", "truth_value": "true", "modifiers": ["present"], "salience": actual_count}}
  ],
  "structural_measures": {{
    "dependency": {{"value": calculated_value, "bridges": count, "structures": count}},
    "connectedness": {{"value": calculated_value}},
    "size": concept_count
  }}
}}"""

    return prompt

def main():
    """Build and save computational schema"""
    
    print("🔧 BUILDING COMPUTATIONALLY COMPLETE SCHEMA")
    print("=" * 60)
    print("Programmatic construction with step-by-step algorithms")
    print()
    
    # Build schema programmatically
    schema = build_young1996_computational_schema()
    
    print("✅ Schema built successfully:")
    print(f"   Core elements: {len(schema['core_elements'])}")
    print(f"   Algorithms: {len(schema['algorithms'])}")
    print(f"   Relationship categories: {len(schema['core_elements']['relationship_categories'])}")
    print()
    
    # Save schema
    output_dir = Path('/home/brian/lit_review/computational_schema_final')
    output_dir.mkdir(exist_ok=True)
    
    schema_path = output_dir / 'young1996_computational_complete.yml'
    with open(schema_path, 'w') as f:
        yaml.dump(schema, f, default_flow_style=False, sort_keys=False)
    
    print(f"📁 Schema saved to: {schema_path}")
    print()
    
    # Create sample execution prompt
    carter_path = Path('/home/brian/lit_review/texts/carter_speech.txt')
    with open(carter_path, 'r') as f:
        carter_speech = f.read()
    
    execution_prompt = create_execution_prompt(schema, carter_speech)
    
    prompt_path = output_dir / 'execution_prompt_example.txt'
    with open(prompt_path, 'w') as f:
        f.write(execution_prompt)
    
    print(f"📄 Execution prompt saved to: {prompt_path}")
    print()
    
    print("🏆 COMPUTATIONALLY COMPLETE SCHEMA READY")
    print("✅ All Young 1996 algorithms embedded with step-by-step instructions")
    print("✅ Relationship categories, truth values, modifiers included")
    print("✅ Salience calculation, dependency, connectedness procedures")
    print("✅ Directed-walk reasoning algorithm included")
    print("✅ Validation criteria specified")
    print("✅ Execution template for API automation provided")
    print()
    print("🎯 READY FOR AUTOMATED END-TO-END APPLICATION")
    print("   This schema contains everything needed for fully automated")
    print("   theory application without manual intervention.")

if __name__ == "__main__":
    main()