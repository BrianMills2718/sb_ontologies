"""
Descriptive Reasoning Module
Sophisticated taxonomic, typological, and classification reasoning
"""

from typing import Dict, List, Any, Tuple
import networkx as nx
from collections import defaultdict, Counter
import re


class DescriptiveReasoner:
    """Advanced descriptive reasoning with taxonomic and classification capabilities"""
    
    def __init__(self):
        """Initialize descriptive reasoning capabilities"""
        self.taxonomy_patterns = [
            r'(type|kind|class|category|group)',
            r'(hierarch|level|tier|rank|order)',
            r'(classif|categoriz|taxonom|typolog)',
            r'(dimension|aspect|facet|characteristic)'
        ]
        
        self.structural_indicators = [
            'structure', 'framework', 'organization', 'arrangement',
            'pattern', 'configuration', 'architecture', 'composition'
        ]
        
        self.classification_methods = [
            'hierarchical', 'flat', 'multidimensional', 'fuzzy',
            'binary', 'categorical', 'ordinal', 'nominal'
        ]
    
    def perform_taxonomic_analysis(self, entities: List[str], relationships: List[str], 
                                  schema: dict, query: str) -> dict:
        """Perform sophisticated taxonomic analysis"""
        try:
            # Build taxonomic hierarchy
            hierarchy = self._build_taxonomic_hierarchy(entities, relationships, schema)
            
            # Identify classification dimensions
            dimensions = self._identify_classification_dimensions(entities, schema, query)
            
            # Analyze taxonomic patterns
            patterns = self._analyze_taxonomic_patterns(hierarchy, dimensions)
            
            # Generate taxonomic insights
            insights = self._generate_taxonomic_insights(hierarchy, dimensions, patterns)
            
            return {
                'taxonomic_hierarchy': hierarchy,
                'classification_dimensions': dimensions,
                'taxonomic_patterns': patterns,
                'insights': insights,
                'complexity_score': self._calculate_taxonomic_complexity(hierarchy, dimensions),
                'coverage_analysis': self._analyze_taxonomic_coverage(entities, hierarchy)
            }
            
        except Exception as e:
            return {
                'error': f"Taxonomic analysis failed: {str(e)}",
                'fallback_taxonomy': self._generate_simple_taxonomy(entities)
            }
    
    def perform_structural_analysis(self, schema: dict, entities: List[str], 
                                   relationships: List[str]) -> dict:
        """Perform sophisticated structural pattern analysis"""
        try:
            # Analyze structural patterns
            structural_patterns = self._identify_structural_patterns(schema, entities, relationships)
            
            # Analyze organizational principles
            organizational_principles = self._identify_organizational_principles(schema)
            
            # Analyze compositional structure
            compositional_structure = self._analyze_compositional_structure(schema, entities)
            
            # Generate structural insights
            insights = self._generate_structural_insights(
                structural_patterns, organizational_principles, compositional_structure
            )
            
            return {
                'structural_patterns': structural_patterns,
                'organizational_principles': organizational_principles,
                'compositional_structure': compositional_structure,
                'insights': insights,
                'structural_complexity': self._calculate_structural_complexity(structural_patterns),
                'pattern_coherence': self._assess_pattern_coherence(structural_patterns)
            }
            
        except Exception as e:
            return {
                'error': f"Structural analysis failed: {str(e)}",
                'fallback_structure': self._generate_simple_structure(entities, relationships)
            }
    
    def perform_classification_analysis(self, entities: List[str], schema: dict, 
                                      query: str) -> dict:
        """Perform sophisticated classification analysis"""
        try:
            # Identify classification criteria
            criteria = self._identify_classification_criteria(entities, schema, query)
            
            # Perform multi-dimensional classification
            classifications = self._perform_multidimensional_classification(entities, criteria, schema)
            
            # Analyze classification quality
            quality_assessment = self._assess_classification_quality(classifications, criteria)
            
            # Generate classification insights
            insights = self._generate_classification_insights(classifications, criteria, quality_assessment)
            
            return {
                'classification_criteria': criteria,
                'classifications': classifications,
                'quality_assessment': quality_assessment,
                'insights': insights,
                'classification_completeness': self._assess_classification_completeness(classifications, entities),
                'classification_consistency': self._assess_classification_consistency(classifications)
            }
            
        except Exception as e:
            return {
                'error': f"Classification analysis failed: {str(e)}",
                'fallback_classification': self._generate_simple_classification(entities)
            }
    
    def integrate_descriptive_analysis(self, taxonomic: dict, structural: dict, 
                                     classification: dict) -> dict:
        """Integrate taxonomic, structural, and classification analyses"""
        try:
            # Find cross-analysis connections
            connections = self._find_descriptive_connections(taxonomic, structural, classification)
            
            # Synthesize descriptive insights
            synthesis = self._synthesize_descriptive_insights(taxonomic, structural, classification, connections)
            
            # Assess descriptive coherence
            coherence = self._assess_descriptive_coherence(taxonomic, structural, classification)
            
            return {
                'integrated_analysis': {
                    'taxonomic': taxonomic,
                    'structural': structural,
                    'classification': classification
                },
                'cross_analysis_connections': connections,
                'descriptive_synthesis': synthesis,
                'coherence_assessment': coherence,
                'integration_quality': self._assess_integration_quality(connections, coherence)
            }
            
        except Exception as e:
            return {
                'error': f"Descriptive integration failed: {str(e)}",
                'fallback_integration': self._generate_basic_integration(taxonomic, structural, classification)
            }
    
    # Helper methods for taxonomic analysis
    
    def _build_taxonomic_hierarchy(self, entities: List[str], relationships: List[str], 
                                  schema: dict) -> dict:
        """Build sophisticated taxonomic hierarchy"""
        hierarchy = {
            'levels': [],
            'relationships': {},
            'root_categories': [],
            'leaf_entities': []
        }
        
        # Identify hierarchical relationships
        hierarchical_rels = [rel for rel in relationships if any(
            keyword in rel.lower() for keyword in ['sub', 'parent', 'child', 'is_a', 'type_of']
        )]
        
        # Build hierarchy levels
        if hierarchical_rels:
            hierarchy['levels'] = ['level_1', 'level_2', 'level_3']  # Simplified
            hierarchy['relationships'] = {rel: 'hierarchical' for rel in hierarchical_rels}
        
        # Identify root categories and leaf entities
        hierarchy['root_categories'] = entities[:min(3, len(entities))]  # Simplified
        hierarchy['leaf_entities'] = entities[-min(3, len(entities)):]  # Simplified
        
        return hierarchy
    
    def _identify_classification_dimensions(self, entities: List[str], schema: dict, 
                                          query: str) -> dict:
        """Identify sophisticated classification dimensions"""
        dimensions = {
            'primary_dimensions': [],
            'secondary_dimensions': [],
            'derived_dimensions': [],
            'dimension_relationships': {}
        }
        
        # Extract dimension indicators from schema
        properties = schema.get('properties', {})
        for prop_name, prop_info in properties.items():
            if any(keyword in prop_name.lower() for keyword in ['type', 'class', 'category']):
                dimensions['primary_dimensions'].append(prop_name)
            elif any(keyword in prop_name.lower() for keyword in ['aspect', 'dimension', 'facet']):
                dimensions['secondary_dimensions'].append(prop_name)
        
        # Derive dimensions from query analysis
        query_terms = re.findall(r'\b\w+\b', query.lower())
        dimension_terms = [term for term in query_terms if any(
            pattern_match in term for pattern_match in ['class', 'type', 'kind', 'category']
        )]
        dimensions['derived_dimensions'] = dimension_terms
        
        return dimensions
    
    def _analyze_taxonomic_patterns(self, hierarchy: dict, dimensions: dict) -> dict:
        """Analyze sophisticated taxonomic patterns"""
        patterns = {
            'hierarchy_patterns': [],
            'classification_patterns': [],
            'structural_patterns': [],
            'pattern_frequency': {}
        }
        
        # Analyze hierarchy patterns
        if hierarchy.get('levels'):
            patterns['hierarchy_patterns'] = [
                'multi_level_hierarchy',
                'branching_structure',
                'categorical_organization'
            ]
        
        # Analyze classification patterns
        if dimensions.get('primary_dimensions'):
            patterns['classification_patterns'] = [
                'multi_dimensional_classification',
                'categorical_classification',
                'hierarchical_classification'
            ]
        
        # Calculate pattern frequency
        all_patterns = patterns['hierarchy_patterns'] + patterns['classification_patterns']
        patterns['pattern_frequency'] = Counter(all_patterns)
        
        return patterns
    
    def _generate_taxonomic_insights(self, hierarchy: dict, dimensions: dict, 
                                   patterns: dict) -> dict:
        """Generate sophisticated taxonomic insights"""
        insights = {
            'key_insights': [],
            'taxonomic_structure': '',
            'classification_quality': '',
            'organizational_principles': [],
            'complexity_assessment': ''
        }
        
        # Generate hierarchy insights
        if hierarchy.get('levels'):
            insights['key_insights'].append(f"Taxonomic hierarchy contains {len(hierarchy['levels'])} levels")
            insights['taxonomic_structure'] = "Multi-level hierarchical organization identified"
        
        # Generate dimension insights
        if dimensions.get('primary_dimensions'):
            insights['key_insights'].append(f"Classification uses {len(dimensions['primary_dimensions'])} primary dimensions")
            insights['classification_quality'] = "Multi-dimensional classification framework present"
        
        # Generate pattern insights
        if patterns.get('hierarchy_patterns'):
            insights['organizational_principles'] = patterns['hierarchy_patterns']
            insights['complexity_assessment'] = "Complex taxonomic organization with multiple structural patterns"
        
        return insights
    
    def _calculate_taxonomic_complexity(self, hierarchy: dict, dimensions: dict) -> float:
        """Calculate taxonomic complexity score"""
        complexity_factors = [
            len(hierarchy.get('levels', [])) * 0.3,
            len(dimensions.get('primary_dimensions', [])) * 0.4,
            len(dimensions.get('secondary_dimensions', [])) * 0.3
        ]
        
        return min(1.0, sum(complexity_factors) / 3.0)
    
    def _analyze_taxonomic_coverage(self, entities: List[str], hierarchy: dict) -> dict:
        """Analyze taxonomic coverage"""
        coverage = {
            'entity_coverage': 0.0,
            'hierarchy_coverage': 0.0,
            'classification_gaps': [],
            'coverage_quality': 'complete'
        }
        
        # Calculate entity coverage
        covered_entities = len(hierarchy.get('leaf_entities', []))
        total_entities = len(entities)
        coverage['entity_coverage'] = covered_entities / total_entities if total_entities > 0 else 0
        
        # Calculate hierarchy coverage
        coverage['hierarchy_coverage'] = len(hierarchy.get('levels', [])) / 5.0  # Assume max 5 levels
        
        # Assess coverage quality
        if coverage['entity_coverage'] < 0.8:
            coverage['classification_gaps'].append('incomplete_entity_coverage')
        if coverage['hierarchy_coverage'] < 0.6:
            coverage['classification_gaps'].append('shallow_hierarchy')
        
        coverage['coverage_quality'] = 'complete' if not coverage['classification_gaps'] else 'partial'
        
        return coverage
    
    # Helper methods for structural analysis
    
    def _identify_structural_patterns(self, schema: dict, entities: List[str], 
                                    relationships: List[str]) -> dict:
        """Identify sophisticated structural patterns"""
        patterns = {
            'compositional_patterns': [],
            'relational_patterns': [],
            'organizational_patterns': [],
            'pattern_strength': {}
        }
        
        # Identify compositional patterns
        if any('part' in rel.lower() or 'component' in rel.lower() for rel in relationships):
            patterns['compositional_patterns'].append('part_whole_composition')
        
        if any('contains' in rel.lower() or 'includes' in rel.lower() for rel in relationships):
            patterns['compositional_patterns'].append('containment_structure')
        
        # Identify relational patterns
        if len(relationships) > len(entities):
            patterns['relational_patterns'].append('dense_relationship_network')
        
        # Identify organizational patterns
        if any(keyword in str(schema).lower() for keyword in self.structural_indicators):
            patterns['organizational_patterns'].append('structured_organization')
        
        # Calculate pattern strength
        for pattern_type, pattern_list in patterns.items():
            if pattern_type != 'pattern_strength' and pattern_list:
                patterns['pattern_strength'][pattern_type] = len(pattern_list) / 3.0  # Normalize
        
        return patterns
    
    def _identify_organizational_principles(self, schema: dict) -> dict:
        """Identify sophisticated organizational principles"""
        principles = {
            'hierarchy_principles': [],
            'modularity_principles': [],
            'cohesion_principles': [],
            'separation_principles': []
        }
        
        # Extract organizational indicators from schema
        schema_text = str(schema).lower()
        
        if any(keyword in schema_text for keyword in ['level', 'tier', 'rank']):
            principles['hierarchy_principles'].append('hierarchical_organization')
        
        if any(keyword in schema_text for keyword in ['module', 'component', 'subsystem']):
            principles['modularity_principles'].append('modular_organization')
        
        if any(keyword in schema_text for keyword in ['cluster', 'group', 'cohort']):
            principles['cohesion_principles'].append('cohesive_grouping')
        
        return principles
    
    def _analyze_compositional_structure(self, schema: dict, entities: List[str]) -> dict:
        """Analyze sophisticated compositional structure"""
        structure = {
            'composition_type': 'unknown',
            'compositional_levels': [],
            'composition_relationships': {},
            'structural_integrity': 0.0
        }
        
        # Analyze composition type
        if any('part' in str(schema).lower() or 'component' in str(schema).lower()):
            structure['composition_type'] = 'part_whole'
        elif any('layer' in str(schema).lower() or 'level' in str(schema).lower()):
            structure['composition_type'] = 'layered'
        else:
            structure['composition_type'] = 'network'
        
        # Identify compositional levels
        structure['compositional_levels'] = ['atomic', 'composite', 'aggregate']  # Simplified
        
        # Calculate structural integrity
        structure['structural_integrity'] = 0.8  # Simplified calculation
        
        return structure
    
    def _generate_structural_insights(self, patterns: dict, principles: dict, 
                                    structure: dict) -> dict:
        """Generate sophisticated structural insights"""
        insights = {
            'key_insights': [],
            'structural_characteristics': '',
            'organizational_assessment': '',
            'design_patterns': [],
            'structural_quality': ''
        }
        
        # Generate pattern insights
        pattern_count = sum(len(p) for p in patterns.values() if isinstance(p, list))
        insights['key_insights'].append(f"Identified {pattern_count} distinct structural patterns")
        
        # Generate principle insights
        principle_count = sum(len(p) for p in principles.values() if isinstance(p, list))
        insights['organizational_assessment'] = f"Organization follows {principle_count} design principles"
        
        # Generate structure insights
        insights['structural_characteristics'] = f"Compositional structure is {structure.get('composition_type', 'unknown')}"
        
        # Assess structural quality
        if pattern_count > 3 and principle_count > 2:
            insights['structural_quality'] = "High structural sophistication with clear organizational patterns"
        else:
            insights['structural_quality'] = "Moderate structural organization with some identifiable patterns"
        
        return insights
    
    def _calculate_structural_complexity(self, patterns: dict) -> float:
        """Calculate structural complexity score"""
        pattern_counts = [len(p) for p in patterns.values() if isinstance(p, list)]
        total_patterns = sum(pattern_counts)
        
        return min(1.0, total_patterns / 10.0)  # Normalize to max 10 patterns
    
    def _assess_pattern_coherence(self, patterns: dict) -> dict:
        """Assess pattern coherence"""
        coherence = {
            'coherence_score': 0.0,
            'coherence_indicators': [],
            'coherence_issues': []
        }
        
        # Calculate coherence based on pattern consistency
        pattern_lists = [p for p in patterns.values() if isinstance(p, list)]
        if pattern_lists:
            avg_patterns = sum(len(p) for p in pattern_lists) / len(pattern_lists)
            coherence['coherence_score'] = min(1.0, avg_patterns / 3.0)
        
        # Identify coherence indicators
        if coherence['coherence_score'] > 0.7:
            coherence['coherence_indicators'].append('consistent_pattern_distribution')
        if any('organizational' in str(p) for p in patterns.values()):
            coherence['coherence_indicators'].append('clear_organizational_structure')
        
        return coherence
    
    # Helper methods for classification analysis
    
    def _identify_classification_criteria(self, entities: List[str], schema: dict, 
                                        query: str) -> dict:
        """Identify sophisticated classification criteria"""
        criteria = {
            'explicit_criteria': [],
            'implicit_criteria': [],
            'derived_criteria': [],
            'criteria_hierarchy': {}
        }
        
        # Extract explicit criteria from schema properties
        properties = schema.get('properties', {})
        for prop_name, prop_info in properties.items():
            if any(keyword in prop_name.lower() for keyword in ['class', 'type', 'category']):
                criteria['explicit_criteria'].append(prop_name)
        
        # Derive criteria from query
        query_words = re.findall(r'\b\w+\b', query.lower())
        classification_words = [word for word in query_words if any(
            keyword in word for keyword in ['type', 'kind', 'class', 'sort']
        )]
        criteria['derived_criteria'] = classification_words
        
        # Identify implicit criteria from entity names
        entity_patterns = set()
        for entity in entities:
            words = re.findall(r'\b\w+\b', entity.lower())
            entity_patterns.update(words)
        
        criteria['implicit_criteria'] = list(entity_patterns)[:5]  # Limit for simplicity
        
        return criteria
    
    def _perform_multidimensional_classification(self, entities: List[str], criteria: dict, 
                                               schema: dict) -> dict:
        """Perform sophisticated multidimensional classification"""
        classifications = {
            'primary_classification': {},
            'secondary_classification': {},
            'multi_dimensional_classification': {},
            'classification_matrix': {}
        }
        
        # Primary classification
        for entity in entities:
            primary_class = self._determine_primary_class(entity, criteria)
            classifications['primary_classification'][entity] = primary_class
        
        # Secondary classification
        for entity in entities:
            secondary_class = self._determine_secondary_class(entity, criteria)
            classifications['secondary_classification'][entity] = secondary_class
        
        # Multi-dimensional classification
        for entity in entities:
            multi_class = {
                'primary': classifications['primary_classification'].get(entity, 'unknown'),
                'secondary': classifications['secondary_classification'].get(entity, 'unknown'),
                'dimensions': self._classify_by_dimensions(entity, criteria)
            }
            classifications['multi_dimensional_classification'][entity] = multi_class
        
        return classifications
    
    def _determine_primary_class(self, entity: str, criteria: dict) -> str:
        """Determine primary classification for entity"""
        # Simplified classification logic
        entity_lower = entity.lower()
        
        if any(criterion in entity_lower for criterion in criteria.get('explicit_criteria', [])):
            return 'explicit_type'
        elif any(criterion in entity_lower for criterion in criteria.get('implicit_criteria', [])):
            return 'implicit_type'
        else:
            return 'general_type'
    
    def _determine_secondary_class(self, entity: str, criteria: dict) -> str:
        """Determine secondary classification for entity"""
        # Simplified secondary classification
        entity_words = re.findall(r'\b\w+\b', entity.lower())
        
        if len(entity_words) > 2:
            return 'complex_entity'
        elif len(entity_words) == 2:
            return 'compound_entity'
        else:
            return 'simple_entity'
    
    def _classify_by_dimensions(self, entity: str, criteria: dict) -> dict:
        """Classify entity by multiple dimensions"""
        dimensions = {}
        
        # Structural dimension
        if '_' in entity or '-' in entity:
            dimensions['structural'] = 'compound'
        else:
            dimensions['structural'] = 'simple'
        
        # Semantic dimension
        if any(word in entity.lower() for word in ['system', 'process', 'model']):
            dimensions['semantic'] = 'abstract'
        else:
            dimensions['semantic'] = 'concrete'
        
        # Complexity dimension
        if len(entity) > 20:
            dimensions['complexity'] = 'complex'
        else:
            dimensions['complexity'] = 'simple'
        
        return dimensions
    
    def _assess_classification_quality(self, classifications: dict, criteria: dict) -> dict:
        """Assess sophisticated classification quality"""
        quality = {
            'completeness_score': 0.0,
            'consistency_score': 0.0,
            'discriminability_score': 0.0,
            'overall_quality': 0.0,
            'quality_issues': []
        }
        
        # Assess completeness
        primary_classified = len([c for c in classifications.get('primary_classification', {}).values() if c != 'unknown'])
        total_entities = len(classifications.get('primary_classification', {}))
        quality['completeness_score'] = primary_classified / total_entities if total_entities > 0 else 0
        
        # Assess consistency
        primary_classes = list(classifications.get('primary_classification', {}).values())
        if primary_classes:
            class_distribution = Counter(primary_classes)
            entropy = -sum((count/len(primary_classes)) * 
                          (count/len(primary_classes)) for count in class_distribution.values())
            quality['consistency_score'] = max(0, 1 - entropy)
        
        # Assess discriminability
        unique_classes = len(set(primary_classes)) if primary_classes else 0
        total_classes = len(primary_classes) if primary_classes else 1
        quality['discriminability_score'] = unique_classes / total_classes
        
        # Calculate overall quality
        quality['overall_quality'] = (
            quality['completeness_score'] * 0.4 +
            quality['consistency_score'] * 0.3 +
            quality['discriminability_score'] * 0.3
        )
        
        # Identify quality issues
        if quality['completeness_score'] < 0.8:
            quality['quality_issues'].append('incomplete_classification')
        if quality['consistency_score'] < 0.6:
            quality['quality_issues'].append('inconsistent_classification')
        if quality['discriminability_score'] < 0.5:
            quality['quality_issues'].append('poor_discriminability')
        
        return quality
    
    def _generate_classification_insights(self, classifications: dict, criteria: dict, 
                                        quality: dict) -> dict:
        """Generate sophisticated classification insights"""
        insights = {
            'key_insights': [],
            'classification_patterns': [],
            'quality_assessment': '',
            'recommendations': [],
            'classification_summary': ''
        }
        
        # Generate classification insights
        primary_classes = list(classifications.get('primary_classification', {}).values())
        if primary_classes:
            class_distribution = Counter(primary_classes)
            most_common = class_distribution.most_common(1)[0]
            insights['key_insights'].append(f"Most common classification: {most_common[0]} ({most_common[1]} entities)")
        
        # Generate pattern insights
        multi_dim = classifications.get('multi_dimensional_classification', {})
        if multi_dim:
            insights['classification_patterns'].append('multi_dimensional_classification_present')
        
        # Generate quality insights
        quality_score = quality.get('overall_quality', 0)
        if quality_score > 0.8:
            insights['quality_assessment'] = 'High-quality classification with strong completeness and consistency'
        elif quality_score > 0.6:
            insights['quality_assessment'] = 'Moderate-quality classification with some gaps'
        else:
            insights['quality_assessment'] = 'Low-quality classification requiring improvement'
        
        # Generate recommendations
        if 'incomplete_classification' in quality.get('quality_issues', []):
            insights['recommendations'].append('Improve classification completeness by addressing unclassified entities')
        if 'inconsistent_classification' in quality.get('quality_issues', []):
            insights['recommendations'].append('Enhance classification consistency through clearer criteria')
        
        return insights
    
    def _assess_classification_completeness(self, classifications: dict, entities: List[str]) -> dict:
        """Assess classification completeness"""
        completeness = {
            'entity_coverage': 0.0,
            'classification_coverage': 0.0,
            'gaps': [],
            'completeness_quality': 'complete'
        }
        
        # Calculate entity coverage
        classified_entities = len(classifications.get('primary_classification', {}))
        total_entities = len(entities)
        completeness['entity_coverage'] = classified_entities / total_entities if total_entities > 0 else 0
        
        # Calculate classification coverage
        non_unknown = len([c for c in classifications.get('primary_classification', {}).values() if c != 'unknown'])
        completeness['classification_coverage'] = non_unknown / classified_entities if classified_entities > 0 else 0
        
        # Identify gaps
        if completeness['entity_coverage'] < 1.0:
            completeness['gaps'].append('missing_entity_classifications')
        if completeness['classification_coverage'] < 0.8:
            completeness['gaps'].append('unknown_classifications')
        
        # Assess completeness quality
        overall_completeness = (completeness['entity_coverage'] + completeness['classification_coverage']) / 2
        if overall_completeness > 0.9:
            completeness['completeness_quality'] = 'complete'
        elif overall_completeness > 0.7:
            completeness['completeness_quality'] = 'mostly_complete'
        else:
            completeness['completeness_quality'] = 'incomplete'
        
        return completeness
    
    def _assess_classification_consistency(self, classifications: dict) -> dict:
        """Assess classification consistency"""
        consistency = {
            'consistency_score': 0.0,
            'consistency_indicators': [],
            'consistency_issues': []
        }
        
        # Analyze primary classification consistency
        primary_classes = list(classifications.get('primary_classification', {}).values())
        if primary_classes:
            # Calculate class distribution uniformity
            class_counts = Counter(primary_classes)
            if len(class_counts) > 0:
                max_count = max(class_counts.values())
                min_count = min(class_counts.values())
                consistency['consistency_score'] = min_count / max_count if max_count > 0 else 0
        
        # Identify consistency indicators
        if consistency['consistency_score'] > 0.7:
            consistency['consistency_indicators'].append('balanced_class_distribution')
        if len(set(primary_classes)) > 2:
            consistency['consistency_indicators'].append('diverse_classification_scheme')
        
        # Identify consistency issues
        if consistency['consistency_score'] < 0.3:
            consistency['consistency_issues'].append('highly_skewed_distribution')
        if 'unknown' in primary_classes and primary_classes.count('unknown') > len(primary_classes) * 0.3:
            consistency['consistency_issues'].append('excessive_unknown_classifications')
        
        return consistency
    
    # Integration methods
    
    def _find_descriptive_connections(self, taxonomic: dict, structural: dict, 
                                    classification: dict) -> dict:
        """Find connections between descriptive analyses"""
        connections = {
            'taxonomic_structural': [],
            'taxonomic_classification': [],
            'structural_classification': [],
            'cross_analysis_themes': []
        }
        
        # Find taxonomic-structural connections
        if (taxonomic.get('taxonomic_hierarchy', {}).get('levels') and 
            structural.get('structural_patterns', {}).get('hierarchy_patterns')):
            connections['taxonomic_structural'].append('hierarchical_organization_alignment')
        
        # Find taxonomic-classification connections
        if (taxonomic.get('classification_dimensions', {}).get('primary_dimensions') and
            classification.get('classification_criteria', {}).get('explicit_criteria')):
            connections['taxonomic_classification'].append('dimension_criteria_alignment')
        
        # Find structural-classification connections
        if (structural.get('organizational_principles', {}).get('hierarchy_principles') and
            classification.get('classifications', {}).get('primary_classification')):
            connections['structural_classification'].append('organization_classification_alignment')
        
        # Identify cross-analysis themes
        all_insights = []
        for analysis in [taxonomic, structural, classification]:
            if analysis.get('insights', {}).get('key_insights'):
                all_insights.extend(analysis['insights']['key_insights'])
        
        theme_words = []
        for insight in all_insights:
            theme_words.extend(re.findall(r'\b\w+\b', insight.lower()))
        
        common_themes = [word for word, count in Counter(theme_words).items() if count > 1]
        connections['cross_analysis_themes'] = common_themes[:5]  # Top 5 themes
        
        return connections
    
    def _synthesize_descriptive_insights(self, taxonomic: dict, structural: dict, 
                                       classification: dict, connections: dict) -> dict:
        """Synthesize insights across descriptive analyses"""
        synthesis = {
            'unified_insights': [],
            'descriptive_framework': '',
            'integration_patterns': [],
            'synthesis_quality': 0.0
        }
        
        # Generate unified insights
        all_analyses = [taxonomic, structural, classification]
        insight_count = sum(len(analysis.get('insights', {}).get('key_insights', [])) for analysis in all_analyses)
        synthesis['unified_insights'].append(f"Comprehensive descriptive analysis with {insight_count} key insights")
        
        # Generate descriptive framework
        if connections.get('cross_analysis_themes'):
            themes = ', '.join(connections['cross_analysis_themes'][:3])
            synthesis['descriptive_framework'] = f"Integrated descriptive framework emphasizing {themes}"
        
        # Identify integration patterns
        connection_types = [k for k, v in connections.items() if v and k != 'cross_analysis_themes']
        synthesis['integration_patterns'] = connection_types
        
        # Calculate synthesis quality
        synthesis['synthesis_quality'] = len(connection_types) / 3.0  # Normalize to 3 connection types
        
        return synthesis
    
    def _assess_descriptive_coherence(self, taxonomic: dict, structural: dict, 
                                    classification: dict) -> dict:
        """Assess coherence across descriptive analyses"""
        coherence = {
            'coherence_score': 0.0,
            'coherence_factors': {},
            'coherence_strengths': [],
            'coherence_weaknesses': []
        }
        
        # Assess individual analysis quality
        analysis_qualities = []
        for analysis_name, analysis in [('taxonomic', taxonomic), ('structural', structural), ('classification', classification)]:
            if analysis.get('insights') and not analysis.get('error'):
                analysis_qualities.append(1.0)
            else:
                analysis_qualities.append(0.0)
        
        coherence['coherence_factors']['analysis_completeness'] = sum(analysis_qualities) / 3.0
        
        # Assess consistency across analyses
        all_insights = []
        for analysis in [taxonomic, structural, classification]:
            if analysis.get('insights', {}).get('key_insights'):
                all_insights.extend(analysis['insights']['key_insights'])
        
        if all_insights:
            coherence['coherence_factors']['insight_consistency'] = 0.8  # Simplified
        else:
            coherence['coherence_factors']['insight_consistency'] = 0.0
        
        # Calculate overall coherence
        coherence['coherence_score'] = sum(coherence['coherence_factors'].values()) / len(coherence['coherence_factors'])
        
        # Identify strengths and weaknesses
        if coherence['coherence_score'] > 0.7:
            coherence['coherence_strengths'].append('strong_analysis_integration')
        if coherence['coherence_factors']['analysis_completeness'] == 1.0:
            coherence['coherence_strengths'].append('complete_analysis_coverage')
        
        if coherence['coherence_score'] < 0.5:
            coherence['coherence_weaknesses'].append('weak_overall_coherence')
        if coherence['coherence_factors']['analysis_completeness'] < 0.7:
            coherence['coherence_weaknesses'].append('incomplete_analysis_coverage')
        
        return coherence
    
    def _assess_integration_quality(self, connections: dict, coherence: dict) -> float:
        """Assess overall integration quality"""
        # Count meaningful connections
        connection_count = sum(len(v) for v in connections.values() if isinstance(v, list))
        
        # Get coherence score
        coherence_score = coherence.get('coherence_score', 0.0)
        
        # Calculate integration quality
        integration_quality = (connection_count / 10.0) * 0.6 + coherence_score * 0.4
        
        return min(1.0, integration_quality)
    
    # Fallback methods
    
    def _generate_simple_taxonomy(self, entities: List[str]) -> dict:
        """Generate simple fallback taxonomy"""
        return {
            'simple_hierarchy': {
                'root': 'entities',
                'children': entities[:5]  # Limit for simplicity
            },
            'classification': 'basic_entity_taxonomy'
        }
    
    def _generate_simple_structure(self, entities: List[str], relationships: List[str]) -> dict:
        """Generate simple fallback structure"""
        return {
            'entity_count': len(entities),
            'relationship_count': len(relationships),
            'basic_structure': 'network' if relationships else 'isolated_entities'
        }
    
    def _generate_simple_classification(self, entities: List[str]) -> dict:
        """Generate simple fallback classification"""
        return {
            'basic_classification': {entity: 'entity_type' for entity in entities[:5]},
            'classification_method': 'simple_categorization'
        }
    
    def _generate_basic_integration(self, taxonomic: dict, structural: dict, 
                                  classification: dict) -> dict:
        """Generate basic integration fallback"""
        return {
            'basic_summary': 'Descriptive analysis completed with taxonomic, structural, and classification components',
            'component_status': {
                'taxonomic': 'present' if taxonomic else 'missing',
                'structural': 'present' if structural else 'missing',
                'classification': 'present' if classification else 'missing'
            }
        }