"""
Causal Reasoning Module
Sophisticated causal pathway and intervention reasoning
"""

from typing import Dict, List, Any, Tuple, Optional
import networkx as nx
from collections import defaultdict, Counter
import re
import itertools


class CausalReasoner:
    """Advanced causal reasoning with pathway analysis and intervention design capabilities"""
    
    def __init__(self):
        """Initialize causal reasoning capabilities"""
        self.causal_patterns = [
            r'(caus|effect|impact|influenc)',
            r'(lead|result|consequenc|outcome)',
            r'(determin|produc|generat|trigger)',
            r'(enable|prevent|facilitat|block)'
        ]
        
        self.causal_indicators = [
            'cause', 'effect', 'impact', 'influence',
            'determine', 'produce', 'generate', 'result',
            'lead_to', 'result_in', 'bring_about'
        ]
        
        self.causal_types = [
            'direct_causation', 'indirect_causation', 'common_cause',
            'reciprocal_causation', 'threshold_causation', 'probabilistic_causation'
        ]
    
    def perform_causal_pathway_analysis(self, schema: dict, entities: List[str], 
                                      relationships: List[str], query: str) -> dict:
        """Perform sophisticated causal pathway analysis"""
        try:
            # Identify causal relationships
            causal_relationships = self._identify_causal_relationships(schema, entities, relationships)
            
            # Build causal graph
            causal_graph = self._build_causal_graph(causal_relationships, entities)
            
            # Analyze causal pathways
            pathways = self._analyze_causal_pathways(causal_graph, causal_relationships)
            
            # Assess pathway strength
            pathway_strength = self._assess_pathway_strength(pathways, causal_graph)
            
            # Identify mediators and moderators
            mediators_moderators = self._identify_mediators_moderators(causal_graph, pathways)
            
            # Generate pathway insights
            insights = self._generate_pathway_insights(pathways, pathway_strength, mediators_moderators)
            
            return {
                'causal_relationships': causal_relationships,
                'causal_graph': causal_graph,
                'causal_pathways': pathways,
                'pathway_strength': pathway_strength,
                'mediators_moderators': mediators_moderators,
                'insights': insights,
                'pathway_complexity': self._calculate_pathway_complexity(pathways, causal_graph),
                'causal_hierarchy': self._build_causal_hierarchy(causal_graph, pathways)
            }
            
        except Exception as e:
            return {
                'error': f"Causal pathway analysis failed: {str(e)}",
                'fallback_pathways': self._generate_basic_pathways(entities, relationships)
            }
    
    def perform_causal_inference(self, schema: dict, entities: List[str], 
                               relationships: List[str], query: str) -> dict:
        """Perform sophisticated causal inference"""
        try:
            # Identify causal claims
            causal_claims = self._identify_causal_claims(schema, entities, relationships, query)
            
            # Assess causal evidence
            evidence_assessment = self._assess_causal_evidence(causal_claims, schema)
            
            # Analyze confounders
            confounder_analysis = self._analyze_confounders(causal_claims, entities, relationships)
            
            # Apply causal criteria
            criteria_assessment = self._apply_causal_criteria(causal_claims, evidence_assessment)
            
            # Generate causal inferences
            inferences = self._generate_causal_inferences(causal_claims, criteria_assessment)
            
            # Assess inference validity
            validity_assessment = self._assess_inference_validity(inferences, evidence_assessment)
            
            # Generate inference insights
            insights = self._generate_inference_insights(inferences, validity_assessment, criteria_assessment)
            
            return {
                'causal_claims': causal_claims,
                'evidence_assessment': evidence_assessment,
                'confounder_analysis': confounder_analysis,
                'criteria_assessment': criteria_assessment,
                'causal_inferences': inferences,
                'validity_assessment': validity_assessment,
                'insights': insights,
                'inference_strength': self._calculate_inference_strength(inferences, validity_assessment),
                'alternative_explanations': self._identify_alternative_explanations(causal_claims, confounder_analysis)
            }
            
        except Exception as e:
            return {
                'error': f"Causal inference failed: {str(e)}",
                'fallback_inferences': self._generate_basic_inferences(entities, relationships)
            }
    
    def perform_intervention_analysis(self, schema: dict, entities: List[str], 
                                    relationships: List[str], query: str) -> dict:
        """Perform sophisticated intervention analysis"""
        try:
            # Identify intervention targets
            targets = self._identify_intervention_targets(schema, entities, query)
            
            # Design intervention strategies
            strategies = self._design_intervention_strategies(targets, schema, relationships)
            
            # Analyze intervention mechanisms
            mechanisms = self._analyze_intervention_mechanisms(strategies, targets)
            
            # Assess intervention feasibility
            feasibility = self._assess_intervention_feasibility(strategies, mechanisms)
            
            # Predict intervention effects
            predicted_effects = self._predict_intervention_effects(strategies, targets, mechanisms)
            
            # Analyze side effects and unintended consequences
            side_effects = self._analyze_side_effects(strategies, predicted_effects, schema)
            
            # Generate intervention insights
            insights = self._generate_intervention_insights(strategies, predicted_effects, feasibility)
            
            return {
                'intervention_targets': targets,
                'intervention_strategies': strategies,
                'intervention_mechanisms': mechanisms,
                'feasibility_assessment': feasibility,
                'predicted_effects': predicted_effects,
                'side_effects_analysis': side_effects,
                'insights': insights,
                'intervention_complexity': self._calculate_intervention_complexity(strategies, mechanisms),
                'implementation_roadmap': self._create_implementation_roadmap(strategies, feasibility)
            }
            
        except Exception as e:
            return {
                'error': f"Intervention analysis failed: {str(e)}",
                'fallback_interventions': self._generate_basic_interventions(entities, query)
            }
    
    def perform_counterfactual_analysis(self, schema: dict, entities: List[str], 
                                      relationships: List[str], query: str) -> dict:
        """Perform sophisticated counterfactual analysis"""
        try:
            # Identify counterfactual scenarios
            scenarios = self._identify_counterfactual_scenarios(schema, entities, relationships)
            
            # Build counterfactual models
            models = self._build_counterfactual_models(scenarios, schema)
            
            # Analyze counterfactual outcomes
            outcomes = self._analyze_counterfactual_outcomes(models, scenarios)
            
            # Compare factual vs counterfactual
            comparisons = self._compare_factual_counterfactual(outcomes, schema)
            
            # Assess counterfactual validity
            validity = self._assess_counterfactual_validity(scenarios, models, outcomes)
            
            # Generate counterfactual insights
            insights = self._generate_counterfactual_insights(scenarios, outcomes, comparisons)
            
            return {
                'counterfactual_scenarios': scenarios,
                'counterfactual_models': models,
                'counterfactual_outcomes': outcomes,
                'factual_counterfactual_comparisons': comparisons,
                'validity_assessment': validity,
                'insights': insights,
                'counterfactual_complexity': self._calculate_counterfactual_complexity(scenarios, models),
                'causal_attribution': self._perform_causal_attribution(outcomes, comparisons)
            }
            
        except Exception as e:
            return {
                'error': f"Counterfactual analysis failed: {str(e)}",
                'fallback_counterfactuals': self._generate_basic_counterfactuals(entities, relationships)
            }
    
    def integrate_causal_analysis(self, pathway: dict, inference: dict, 
                                intervention: dict, counterfactual: dict) -> dict:
        """Integrate pathway, inference, intervention, and counterfactual analyses"""
        try:
            # Find cross-analysis connections
            connections = self._find_causal_connections(pathway, inference, intervention, counterfactual)
            
            # Synthesize causal insights
            synthesis = self._synthesize_causal_insights(pathway, inference, intervention, counterfactual, connections)
            
            # Assess causal coherence
            coherence = self._assess_causal_coherence(pathway, inference, intervention, counterfactual)
            
            # Generate unified causal model
            unified_model = self._generate_unified_causal_model(pathway, inference, intervention, counterfactual)
            
            # Assess causal certainty
            certainty = self._assess_causal_certainty(pathway, inference, intervention, counterfactual)
            
            return {
                'integrated_analysis': {
                    'pathway': pathway,
                    'inference': inference,
                    'intervention': intervention,
                    'counterfactual': counterfactual
                },
                'cross_analysis_connections': connections,
                'causal_synthesis': synthesis,
                'coherence_assessment': coherence,
                'unified_causal_model': unified_model,
                'causal_certainty': certainty,
                'integration_quality': self._assess_causal_integration_quality(connections, coherence)
            }
            
        except Exception as e:
            return {
                'error': f"Causal integration failed: {str(e)}",
                'fallback_integration': self._generate_basic_causal_integration(pathway, inference, intervention, counterfactual)
            }
    
    # Helper methods for causal pathway analysis
    
    def _identify_causal_relationships(self, schema: dict, entities: List[str], 
                                     relationships: List[str]) -> dict:
        """Identify sophisticated causal relationships"""
        causal_rels = {
            'direct_causal': [],
            'indirect_causal': [],
            'bidirectional_causal': [],
            'conditional_causal': [],
            'threshold_causal': []
        }
        
        schema_text = str(schema).lower()
        
        # Identify direct causal relationships
        for rel in relationships:
            if any(keyword in rel.lower() for keyword in ['cause', 'trigger', 'generate', 'produce']):
                causal_rels['direct_causal'].append({
                    'relationship': rel,
                    'type': 'direct',
                    'strength': 'strong',
                    'mechanism': 'direct_effect'
                })
        
        # Identify indirect causal relationships
        if any(keyword in schema_text for keyword in ['through', 'via', 'mediated', 'indirect']):
            causal_rels['indirect_causal'].append({
                'relationship': 'mediated_causation',
                'type': 'indirect',
                'strength': 'moderate',
                'mechanism': 'mediated_effect'
            })
        
        # Identify bidirectional causal relationships
        if any(keyword in schema_text for keyword in ['mutual', 'reciprocal', 'feedback', 'bidirectional']):
            causal_rels['bidirectional_causal'].append({
                'relationship': 'mutual_causation',
                'type': 'bidirectional',
                'strength': 'variable',
                'mechanism': 'feedback_loop'
            })
        
        # Identify conditional causal relationships
        if any(keyword in schema_text for keyword in ['if', 'when', 'conditional', 'context']):
            causal_rels['conditional_causal'].append({
                'relationship': 'conditional_causation',
                'type': 'conditional',
                'strength': 'context_dependent',
                'mechanism': 'conditional_effect'
            })
        
        # Identify threshold causal relationships
        if any(keyword in schema_text for keyword in ['threshold', 'critical', 'tipping', 'minimum']):
            causal_rels['threshold_causal'].append({
                'relationship': 'threshold_causation',
                'type': 'threshold',
                'strength': 'nonlinear',
                'mechanism': 'threshold_effect'
            })
        
        return causal_rels
    
    def _build_causal_graph(self, causal_relationships: dict, entities: List[str]) -> nx.DiGraph:
        """Build sophisticated causal graph"""
        graph = nx.DiGraph()
        
        # Add entity nodes
        for entity in entities:
            graph.add_node(entity, node_type='entity')
        
        # Add causal edges
        for rel_type, rel_list in causal_relationships.items():
            for rel_info in rel_list:
                if len(entities) >= 2:
                    # Simple mapping: assign relationships to entity pairs
                    source = entities[0]
                    target = entities[1] if len(entities) > 1 else entities[0]
                    
                    graph.add_edge(source, target, 
                                 relationship=rel_info['relationship'],
                                 causal_type=rel_info['type'],
                                 strength=rel_info['strength'],
                                 mechanism=rel_info['mechanism'])
        
        # Add intermediate nodes for complex pathways
        if len(entities) > 2:
            mediator = entities[2] if len(entities) > 2 else f"mediator_node"
            if mediator in entities:
                graph.add_edge(entities[0], mediator, causal_type='direct', strength='moderate')
                graph.add_edge(mediator, entities[1], causal_type='direct', strength='moderate')
        
        return graph
    
    def _analyze_causal_pathways(self, causal_graph: nx.DiGraph, 
                               causal_relationships: dict) -> dict:
        """Analyze sophisticated causal pathways"""
        pathways = {
            'direct_pathways': [],
            'indirect_pathways': [],
            'complex_pathways': [],
            'pathway_metrics': {}
        }
        
        if not causal_graph.nodes():
            return pathways
        
        nodes = list(causal_graph.nodes())
        
        # Identify direct pathways (single edges)
        for edge in causal_graph.edges(data=True):
            source, target, data = edge
            pathways['direct_pathways'].append({
                'source': source,
                'target': target,
                'pathway_length': 1,
                'pathway_type': 'direct',
                'strength': data.get('strength', 'unknown'),
                'mechanism': data.get('mechanism', 'unknown')
            })
        
        # Identify indirect pathways (multiple edges)
        try:
            for source in nodes:
                for target in nodes:
                    if source != target:
                        try:
                            simple_paths = list(nx.all_simple_paths(causal_graph, source, target, cutoff=3))
                            for path in simple_paths:
                                if len(path) > 2:  # Indirect pathway
                                    pathways['indirect_pathways'].append({
                                        'source': source,
                                        'target': target,
                                        'pathway': path,
                                        'pathway_length': len(path) - 1,
                                        'pathway_type': 'indirect',
                                        'intermediates': path[1:-1]
                                    })
                        except nx.NetworkXNoPath:
                            continue
        except Exception:
            # Handle graph analysis errors gracefully
            pass
        
        # Identify complex pathways (cycles, feedback loops)
        try:
            cycles = list(nx.simple_cycles(causal_graph))
            for cycle in cycles:
                pathways['complex_pathways'].append({
                    'pathway': cycle,
                    'pathway_type': 'cyclical',
                    'cycle_length': len(cycle),
                    'feedback_type': 'positive' if len(cycle) % 2 == 0 else 'negative'
                })
        except Exception:
            pass
        
        # Calculate pathway metrics
        pathways['pathway_metrics'] = {
            'total_pathways': len(pathways['direct_pathways']) + len(pathways['indirect_pathways']),
            'direct_pathway_count': len(pathways['direct_pathways']),
            'indirect_pathway_count': len(pathways['indirect_pathways']),
            'complex_pathway_count': len(pathways['complex_pathways']),
            'average_pathway_length': self._calculate_average_pathway_length(pathways),
            'pathway_density': len(pathways['direct_pathways']) / max(1, len(nodes) * (len(nodes) - 1))
        }
        
        return pathways
    
    def _calculate_average_pathway_length(self, pathways: dict) -> float:
        """Calculate average pathway length"""
        all_lengths = []
        
        for pathway in pathways.get('direct_pathways', []):
            all_lengths.append(pathway.get('pathway_length', 1))
        
        for pathway in pathways.get('indirect_pathways', []):
            all_lengths.append(pathway.get('pathway_length', 2))
        
        return sum(all_lengths) / len(all_lengths) if all_lengths else 0
    
    def _assess_pathway_strength(self, pathways: dict, causal_graph: nx.DiGraph) -> dict:
        """Assess sophisticated pathway strength"""
        strength_assessment = {
            'individual_strengths': {},
            'aggregate_strength': 0.0,
            'strength_distribution': {},
            'critical_pathways': []
        }
        
        # Assess individual pathway strengths
        for pathway in pathways.get('direct_pathways', []):
            pathway_id = f"{pathway['source']}_to_{pathway['target']}"
            strength_score = self._calculate_pathway_strength_score(pathway, 'direct')
            strength_assessment['individual_strengths'][pathway_id] = {
                'strength_score': strength_score,
                'pathway_type': 'direct',
                'strength_factors': ['directness', 'mechanism_clarity']
            }
        
        for pathway in pathways.get('indirect_pathways', []):
            pathway_id = f"{pathway['source']}_to_{pathway['target']}_indirect"
            strength_score = self._calculate_pathway_strength_score(pathway, 'indirect')
            strength_assessment['individual_strengths'][pathway_id] = {
                'strength_score': strength_score,
                'pathway_type': 'indirect',
                'strength_factors': ['pathway_length', 'intermediary_reliability']
            }
        
        # Calculate aggregate strength
        individual_scores = [info['strength_score'] for info in strength_assessment['individual_strengths'].values()]
        if individual_scores:
            strength_assessment['aggregate_strength'] = sum(individual_scores) / len(individual_scores)
        
        # Analyze strength distribution
        if individual_scores:
            strength_assessment['strength_distribution'] = {
                'strong_pathways': len([s for s in individual_scores if s > 0.7]),
                'moderate_pathways': len([s for s in individual_scores if 0.4 <= s <= 0.7]),
                'weak_pathways': len([s for s in individual_scores if s < 0.4]),
                'strength_variance': sum((s - strength_assessment['aggregate_strength'])**2 for s in individual_scores) / len(individual_scores)
            }
        
        # Identify critical pathways
        for pathway_id, info in strength_assessment['individual_strengths'].items():
            if info['strength_score'] > 0.8:
                strength_assessment['critical_pathways'].append({
                    'pathway_id': pathway_id,
                    'strength_score': info['strength_score'],
                    'criticality_reason': 'high_strength_score'
                })
        
        return strength_assessment
    
    def _calculate_pathway_strength_score(self, pathway: dict, pathway_type: str) -> float:
        """Calculate pathway strength score"""
        base_strength = 0.5
        
        if pathway_type == 'direct':
            # Direct pathways start with higher base strength
            base_strength = 0.8
            # Adjust based on strength annotation
            strength_text = pathway.get('strength', 'moderate')
            if strength_text == 'strong':
                base_strength += 0.2
            elif strength_text == 'weak':
                base_strength -= 0.2
        
        elif pathway_type == 'indirect':
            # Indirect pathways penalized by length
            pathway_length = pathway.get('pathway_length', 2)
            base_strength = 0.6 - (pathway_length - 2) * 0.1
        
        return max(0.0, min(1.0, base_strength))
    
    def _identify_mediators_moderators(self, causal_graph: nx.DiGraph, pathways: dict) -> dict:
        """Identify sophisticated mediators and moderators"""
        mediators_moderators = {
            'mediators': [],
            'moderators': [],
            'mediator_analysis': {},
            'moderator_analysis': {}
        }
        
        if not causal_graph.nodes():
            return mediators_moderators
        
        nodes = list(causal_graph.nodes())
        
        # Identify mediators (nodes in indirect pathways)
        for pathway in pathways.get('indirect_pathways', []):
            intermediates = pathway.get('intermediates', [])
            for intermediate in intermediates:
                if intermediate not in [m['node'] for m in mediators_moderators['mediators']]:
                    mediators_moderators['mediators'].append({
                        'node': intermediate,
                        'mediation_type': 'sequential',
                        'mediation_strength': 'moderate',
                        'pathway_involvement': [pathway['source'], pathway['target']]
                    })
        
        # Identify potential moderators (nodes with high degree)
        if causal_graph.nodes():
            node_degrees = dict(causal_graph.degree())
            high_degree_nodes = [node for node, degree in node_degrees.items() if degree > 1]
            
            for node in high_degree_nodes:
                if node not in [m['node'] for m in mediators_moderators['moderators']]:
                    mediators_moderators['moderators'].append({
                        'node': node,
                        'moderation_type': 'interaction',
                        'moderation_strength': 'moderate',
                        'moderated_relationships': list(causal_graph.neighbors(node))
                    })
        
        # Analyze mediator effects
        for mediator in mediators_moderators['mediators']:
            mediator_node = mediator['node']
            mediators_moderators['mediator_analysis'][mediator_node] = {
                'mediation_effect_size': 0.6,  # Simplified
                'proportion_mediated': 0.4,
                'direct_effect_remaining': 0.6,
                'mediation_significance': 'significant'
            }
        
        # Analyze moderator effects
        for moderator in mediators_moderators['moderators']:
            moderator_node = moderator['node']
            mediators_moderators['moderator_analysis'][moderator_node] = {
                'moderation_effect_size': 0.3,  # Simplified
                'interaction_strength': 'moderate',
                'moderation_direction': 'positive',
                'conditional_effects': {'low': 0.2, 'medium': 0.5, 'high': 0.8}
            }
        
        return mediators_moderators
    
    def _generate_pathway_insights(self, pathways: dict, pathway_strength: dict, 
                                 mediators_moderators: dict) -> dict:
        """Generate sophisticated pathway insights"""
        insights = {
            'key_insights': [],
            'pathway_characterization': '',
            'strength_assessment': '',
            'complexity_assessment': '',
            'intervention_implications': []
        }
        
        # Generate key insights
        total_pathways = pathways.get('pathway_metrics', {}).get('total_pathways', 0)
        insights['key_insights'].append(f"Identified {total_pathways} distinct causal pathways")
        
        if pathways.get('complex_pathways'):
            insights['key_insights'].append("Complex feedback loops indicate dynamic causal relationships")
        
        mediator_count = len(mediators_moderators.get('mediators', []))
        if mediator_count > 0:
            insights['key_insights'].append(f"Identified {mediator_count} mediating variables in causal pathways")
        
        # Generate pathway characterization
        direct_count = len(pathways.get('direct_pathways', []))
        indirect_count = len(pathways.get('indirect_pathways', []))
        
        if direct_count > indirect_count:
            insights['pathway_characterization'] = "Causal structure dominated by direct pathways"
        elif indirect_count > direct_count:
            insights['pathway_characterization'] = "Causal structure features complex indirect pathways"
        else:
            insights['pathway_characterization'] = "Balanced causal structure with direct and indirect pathways"
        
        # Generate strength assessment
        aggregate_strength = pathway_strength.get('aggregate_strength', 0.0)
        if aggregate_strength > 0.8:
            insights['strength_assessment'] = "Strong causal pathways with high reliability"
        elif aggregate_strength > 0.6:
            insights['strength_assessment'] = "Moderate causal pathway strength with good reliability"
        else:
            insights['strength_assessment'] = "Weaker causal pathways requiring careful interpretation"
        
        # Generate complexity assessment
        avg_length = pathways.get('pathway_metrics', {}).get('average_pathway_length', 0)
        complex_count = len(pathways.get('complex_pathways', []))
        
        if avg_length > 2 and complex_count > 0:
            insights['complexity_assessment'] = "High causal complexity with multiple levels and feedback"
        elif avg_length > 1.5 or complex_count > 0:
            insights['complexity_assessment'] = "Moderate causal complexity with some indirect effects"
        else:
            insights['complexity_assessment'] = "Simple causal structure with primarily direct effects"
        
        # Generate intervention implications
        critical_pathways = pathway_strength.get('critical_pathways', [])
        if critical_pathways:
            insights['intervention_implications'].append("Target critical pathways for maximum intervention impact")
        
        if mediators_moderators.get('mediators'):
            insights['intervention_implications'].append("Consider mediator-focused interventions for pathway modification")
        
        if pathways.get('complex_pathways'):
            insights['intervention_implications'].append("Account for feedback effects in intervention design")
        
        return insights
    
    def _calculate_pathway_complexity(self, pathways: dict, causal_graph: nx.DiGraph) -> float:
        """Calculate pathway complexity score"""
        complexity_factors = []
        
        # Pathway count factor
        total_pathways = pathways.get('pathway_metrics', {}).get('total_pathways', 0)
        complexity_factors.append(min(1.0, total_pathways / 10.0))
        
        # Pathway length factor
        avg_length = pathways.get('pathway_metrics', {}).get('average_pathway_length', 0)
        complexity_factors.append(min(1.0, avg_length / 3.0))
        
        # Complex pathway factor
        complex_count = len(pathways.get('complex_pathways', []))
        complexity_factors.append(min(1.0, complex_count / 3.0))
        
        # Graph density factor
        if causal_graph.nodes():
            density = nx.density(causal_graph)
            complexity_factors.append(density)
        else:
            complexity_factors.append(0.0)
        
        return sum(complexity_factors) / len(complexity_factors)
    
    def _build_causal_hierarchy(self, causal_graph: nx.DiGraph, pathways: dict) -> dict:
        """Build causal hierarchy"""
        hierarchy = {
            'levels': {},
            'root_causes': [],
            'intermediate_causes': [],
            'ultimate_effects': [],
            'hierarchy_depth': 0
        }
        
        if not causal_graph.nodes():
            return hierarchy
        
        # Identify root causes (no incoming edges)
        for node in causal_graph.nodes():
            if causal_graph.in_degree(node) == 0:
                hierarchy['root_causes'].append(node)
        
        # Identify ultimate effects (no outgoing edges)
        for node in causal_graph.nodes():
            if causal_graph.out_degree(node) == 0:
                hierarchy['ultimate_effects'].append(node)
        
        # Identify intermediate causes
        all_nodes = set(causal_graph.nodes())
        root_and_ultimate = set(hierarchy['root_causes'] + hierarchy['ultimate_effects'])
        hierarchy['intermediate_causes'] = list(all_nodes - root_and_ultimate)
        
        # Build hierarchy levels
        try:
            # Simple level assignment based on shortest path from roots
            hierarchy['levels'] = {}
            for root in hierarchy['root_causes']:
                paths = nx.single_source_shortest_path_length(causal_graph, root)
                for node, distance in paths.items():
                    if node not in hierarchy['levels'] or distance < hierarchy['levels'][node]:
                        hierarchy['levels'][node] = distance
            
            if hierarchy['levels']:
                hierarchy['hierarchy_depth'] = max(hierarchy['levels'].values())
        except Exception:
            # Handle graph analysis errors
            hierarchy['hierarchy_depth'] = 1
        
        return hierarchy
    
    # Helper methods for causal inference
    
    def _identify_causal_claims(self, schema: dict, entities: List[str], 
                              relationships: List[str], query: str) -> dict:
        """Identify sophisticated causal claims"""
        claims = {
            'explicit_claims': [],
            'implicit_claims': [],
            'query_derived_claims': [],
            'claim_types': {}
        }
        
        schema_text = str(schema).lower()
        query_lower = query.lower()
        
        # Identify explicit causal claims from relationships
        for rel in relationships:
            if any(keyword in rel.lower() for keyword in self.causal_indicators):
                claims['explicit_claims'].append({
                    'claim': rel,
                    'claim_type': 'explicit_relationship',
                    'strength': 'stated',
                    'source': 'relationship_specification'
                })
        
        # Identify implicit causal claims from schema
        if any(keyword in schema_text for keyword in ['influence', 'affect', 'impact']):
            claims['implicit_claims'].append({
                'claim': 'system_influences_detected',
                'claim_type': 'implicit_influence',
                'strength': 'suggested',
                'source': 'schema_structure'
            })
        
        # Identify query-derived causal claims
        if any(keyword in query_lower for keyword in ['cause', 'effect', 'impact', 'influence']):
            causal_terms = [term for term in re.findall(r'\b\w+\b', query_lower) 
                          if any(keyword in term for keyword in self.causal_indicators)]
            for term in causal_terms:
                claims['query_derived_claims'].append({
                    'claim': f'query_causal_interest_{term}',
                    'claim_type': 'query_derived',
                    'strength': 'query_indicated',
                    'source': 'user_query'
                })
        
        # Categorize claim types
        all_claims = claims['explicit_claims'] + claims['implicit_claims'] + claims['query_derived_claims']
        claim_type_counts = Counter(claim['claim_type'] for claim in all_claims)
        claims['claim_types'] = dict(claim_type_counts)
        
        return claims
    
    def _assess_causal_evidence(self, causal_claims: dict, schema: dict) -> dict:
        """Assess sophisticated causal evidence"""
        evidence = {
            'evidence_types': {},
            'evidence_strength': {},
            'evidence_quality': {},
            'evidence_gaps': []
        }
        
        # Assess evidence for explicit claims
        for claim in causal_claims.get('explicit_claims', []):
            claim_id = claim['claim']
            evidence['evidence_types'][claim_id] = 'structural_specification'
            evidence['evidence_strength'][claim_id] = 'moderate'
            evidence['evidence_quality'][claim_id] = {
                'specificity': 'high',
                'clarity': 'moderate',
                'completeness': 'partial'
            }
        
        # Assess evidence for implicit claims
        for claim in causal_claims.get('implicit_claims', []):
            claim_id = claim['claim']
            evidence['evidence_types'][claim_id] = 'inferential'
            evidence['evidence_strength'][claim_id] = 'weak'
            evidence['evidence_quality'][claim_id] = {
                'specificity': 'low',
                'clarity': 'low',
                'completeness': 'incomplete'
            }
        
        # Identify evidence gaps
        total_claims = len(causal_claims.get('explicit_claims', []) + 
                         causal_claims.get('implicit_claims', []) + 
                         causal_claims.get('query_derived_claims', []))
        
        if total_claims > len(evidence['evidence_strength']):
            evidence['evidence_gaps'].append('unsupported_claims')
        
        weak_evidence_count = sum(1 for strength in evidence['evidence_strength'].values() 
                                if strength in ['weak', 'very_weak'])
        if weak_evidence_count > total_claims * 0.5:
            evidence['evidence_gaps'].append('insufficient_evidence_strength')
        
        incomplete_quality = sum(1 for quality in evidence['evidence_quality'].values() 
                               if quality.get('completeness') == 'incomplete')
        if incomplete_quality > total_claims * 0.3:
            evidence['evidence_gaps'].append('incomplete_evidence_quality')
        
        return evidence
    
    def _analyze_confounders(self, causal_claims: dict, entities: List[str], 
                           relationships: List[str]) -> dict:
        """Analyze sophisticated confounders"""
        confounders = {
            'identified_confounders': [],
            'potential_confounders': [],
            'confounder_analysis': {},
            'confounding_assessment': {}
        }
        
        # Identify potential confounders from entities
        # Look for entities that could influence both cause and effect
        all_claims = (causal_claims.get('explicit_claims', []) + 
                     causal_claims.get('implicit_claims', []))
        
        for entity in entities:
            # Simple heuristic: entities mentioned in multiple relationships
            relationship_count = sum(1 for rel in relationships if entity.lower() in rel.lower())
            if relationship_count > 1:
                confounders['potential_confounders'].append({
                    'confounder': entity,
                    'confounder_type': 'common_cause',
                    'relationship_involvement': relationship_count,
                    'confounding_strength': 'moderate'
                })
        
        # Analyze confounding for each claim
        for claim in all_claims:
            claim_id = claim['claim']
            confounders['confounder_analysis'][claim_id] = {
                'relevant_confounders': [c['confounder'] for c in confounders['potential_confounders'][:2]],
                'confounding_severity': 'moderate',
                'adjustment_needed': True,
                'adjustment_method': 'statistical_control'
            }
        
        # Overall confounding assessment
        total_confounders = len(confounders['potential_confounders'])
        confounders['confounding_assessment'] = {
            'overall_confounding_risk': 'moderate' if total_confounders > 0 else 'low',
            'confounding_complexity': 'simple' if total_confounders <= 2 else 'complex',
            'control_feasibility': 'feasible' if total_confounders <= 3 else 'challenging',
            'bias_direction': 'mixed' if total_confounders > 1 else 'positive'
        }
        
        return confounders
    
    def _apply_causal_criteria(self, causal_claims: dict, evidence_assessment: dict) -> dict:
        """Apply sophisticated causal criteria"""
        criteria = {
            'criteria_assessment': {},
            'criteria_scores': {},
            'overall_causal_support': {},
            'criteria_weights': {}
        }
        
        # Define causal criteria (Hill's criteria adapted)
        causal_criteria = [
            'temporal_precedence',
            'strength_of_association',
            'dose_response_relationship',
            'consistency_across_contexts',
            'biological_plausibility',
            'coherence_with_knowledge',
            'experimental_evidence'
        ]
        
        # Assess each claim against criteria
        all_claims = (causal_claims.get('explicit_claims', []) + 
                     causal_claims.get('implicit_claims', []))
        
        for claim in all_claims:
            claim_id = claim['claim']
            criteria['criteria_assessment'][claim_id] = {}
            criteria['criteria_scores'][claim_id] = {}
            
            for criterion in causal_criteria:
                # Simplified assessment based on claim type and evidence
                evidence_strength = evidence_assessment.get('evidence_strength', {}).get(claim_id, 'weak')
                claim_type = claim.get('claim_type', 'unknown')
                
                if claim_type == 'explicit_relationship':
                    score = self._score_criterion(criterion, evidence_strength, 'explicit')
                elif claim_type == 'implicit_influence':
                    score = self._score_criterion(criterion, evidence_strength, 'implicit')
                else:
                    score = self._score_criterion(criterion, evidence_strength, 'derived')
                
                criteria['criteria_assessment'][claim_id][criterion] = score
                criteria['criteria_scores'][claim_id][criterion] = score
        
        # Calculate overall causal support
        for claim in all_claims:
            claim_id = claim['claim']
            scores = list(criteria['criteria_scores'][claim_id].values())
            criteria['overall_causal_support'][claim_id] = {
                'average_score': sum(scores) / len(scores) if scores else 0,
                'criteria_met': sum(1 for score in scores if score > 0.6),
                'support_level': self._determine_support_level(scores),
                'confidence': self._calculate_confidence(scores)
            }
        
        # Set criteria weights
        criteria['criteria_weights'] = {
            'temporal_precedence': 0.20,
            'strength_of_association': 0.15,
            'dose_response_relationship': 0.10,
            'consistency_across_contexts': 0.15,
            'biological_plausibility': 0.10,
            'coherence_with_knowledge': 0.15,
            'experimental_evidence': 0.15
        }
        
        return criteria
    
    def _score_criterion(self, criterion: str, evidence_strength: str, claim_type: str) -> float:
        """Score individual causal criterion"""
        base_scores = {
            'explicit': 0.7,
            'implicit': 0.4,
            'derived': 0.3
        }
        
        strength_multipliers = {
            'strong': 1.2,
            'moderate': 1.0,
            'weak': 0.7,
            'very_weak': 0.4
        }
        
        base_score = base_scores.get(claim_type, 0.3)
        multiplier = strength_multipliers.get(evidence_strength, 0.7)
        
        # Criterion-specific adjustments
        criterion_adjustments = {
            'temporal_precedence': 0.1,
            'strength_of_association': 0.0,
            'experimental_evidence': -0.1,  # Harder to satisfy
            'coherence_with_knowledge': 0.05
        }
        
        adjustment = criterion_adjustments.get(criterion, 0.0)
        final_score = base_score * multiplier + adjustment
        
        return max(0.0, min(1.0, final_score))
    
    def _determine_support_level(self, scores: List[float]) -> str:
        """Determine causal support level"""
        if not scores:
            return 'no_support'
        
        avg_score = sum(scores) / len(scores)
        criteria_met = sum(1 for score in scores if score > 0.6)
        
        if avg_score > 0.8 and criteria_met >= 5:
            return 'strong_support'
        elif avg_score > 0.6 and criteria_met >= 3:
            return 'moderate_support'
        elif avg_score > 0.4 and criteria_met >= 2:
            return 'weak_support'
        else:
            return 'insufficient_support'
    
    def _calculate_confidence(self, scores: List[float]) -> float:
        """Calculate confidence in causal assessment"""
        if not scores:
            return 0.0
        
        avg_score = sum(scores) / len(scores)
        score_variance = sum((score - avg_score)**2 for score in scores) / len(scores)
        consistency = 1.0 - min(1.0, score_variance)
        
        return (avg_score * 0.7) + (consistency * 0.3)
    
    # Continue with more helper methods for remaining functionality...
    
    def _generate_causal_inferences(self, causal_claims: dict, criteria_assessment: dict) -> dict:
        """Generate sophisticated causal inferences"""
        inferences = {
            'strong_inferences': [],
            'moderate_inferences': [],
            'weak_inferences': [],
            'rejected_inferences': [],
            'inference_confidence': {}
        }
        
        # Categorize inferences based on support level
        all_claims = (causal_claims.get('explicit_claims', []) + 
                     causal_claims.get('implicit_claims', []))
        
        for claim in all_claims:
            claim_id = claim['claim']
            support_info = criteria_assessment.get('overall_causal_support', {}).get(claim_id, {})
            support_level = support_info.get('support_level', 'insufficient_support')
            confidence = support_info.get('confidence', 0.0)
            
            inference = {
                'claim': claim['claim'],
                'inference': f"causal_relationship_{claim_id}",
                'support_level': support_level,
                'confidence': confidence,
                'evidence_base': claim.get('source', 'unknown')
            }
            
            if support_level == 'strong_support':
                inferences['strong_inferences'].append(inference)
            elif support_level == 'moderate_support':
                inferences['moderate_inferences'].append(inference)
            elif support_level == 'weak_support':
                inferences['weak_inferences'].append(inference)
            else:
                inferences['rejected_inferences'].append(inference)
            
            inferences['inference_confidence'][claim_id] = confidence
        
        return inferences
    
    def _assess_inference_validity(self, inferences: dict, evidence_assessment: dict) -> dict:
        """Assess inference validity"""
        validity = {
            'internal_validity': {},
            'external_validity': {},
            'construct_validity': {},
            'overall_validity': {}
        }
        
        # Assess internal validity (causal conclusions)
        strong_count = len(inferences.get('strong_inferences', []))
        total_count = sum(len(inf_list) for inf_list in inferences.values() if isinstance(inf_list, list))
        
        validity['internal_validity'] = {
            'validity_score': strong_count / max(1, total_count),
            'threats': ['confounding', 'reverse_causation', 'selection_bias'],
            'controls': ['statistical_adjustment', 'temporal_ordering'],
            'confidence': 'moderate'
        }
        
        # Assess external validity (generalizability)
        validity['external_validity'] = {
            'validity_score': 0.6,  # Simplified
            'generalizability': 'limited',
            'scope_conditions': ['specific_context', 'defined_population'],
            'confidence': 'moderate'
        }
        
        # Assess construct validity (measurement)
        validity['construct_validity'] = {
            'validity_score': 0.7,  # Simplified
            'measurement_quality': 'adequate',
            'conceptual_clarity': 'moderate',
            'confidence': 'moderate'
        }
        
        # Overall validity assessment
        validity['overall_validity'] = {
            'composite_score': (validity['internal_validity']['validity_score'] * 0.5 +
                              validity['external_validity']['validity_score'] * 0.3 +
                              validity['construct_validity']['validity_score'] * 0.2),
            'validity_level': 'moderate',
            'key_limitations': ['limited_generalizability', 'potential_confounding'],
            'confidence': 'moderate'
        }
        
        return validity
    
    def _generate_inference_insights(self, inferences: dict, validity_assessment: dict, 
                                   criteria_assessment: dict) -> dict:
        """Generate sophisticated inference insights"""
        insights = {
            'key_insights': [],
            'inference_summary': '',
            'validity_assessment': '',
            'confidence_assessment': '',
            'limitations_and_caveats': []
        }
        
        # Generate key insights
        strong_count = len(inferences.get('strong_inferences', []))
        moderate_count = len(inferences.get('moderate_inferences', []))
        weak_count = len(inferences.get('weak_inferences', []))
        
        insights['key_insights'].append(f"Causal analysis yields {strong_count} strong, {moderate_count} moderate, and {weak_count} weak inferences")
        
        if strong_count > 0:
            insights['key_insights'].append("Strong causal relationships identified with high confidence")
        
        if weak_count > strong_count + moderate_count:
            insights['key_insights'].append("Limited causal evidence requires cautious interpretation")
        
        # Generate inference summary
        total_inferences = strong_count + moderate_count + weak_count
        if total_inferences > 0:
            if strong_count / total_inferences > 0.5:
                insights['inference_summary'] = "Robust causal relationships with strong evidentiary support"
            elif (strong_count + moderate_count) / total_inferences > 0.6:
                insights['inference_summary'] = "Moderate causal relationships with reasonable support"
            else:
                insights['inference_summary'] = "Weak causal relationships requiring additional evidence"
        else:
            insights['inference_summary'] = "Insufficient evidence for reliable causal inferences"
        
        # Generate validity assessment
        overall_validity = validity_assessment.get('overall_validity', {}).get('composite_score', 0.0)
        if overall_validity > 0.7:
            insights['validity_assessment'] = "High validity with robust causal conclusions"
        elif overall_validity > 0.5:
            insights['validity_assessment'] = "Moderate validity with reasonable causal conclusions"
        else:
            insights['validity_assessment'] = "Limited validity requiring cautious interpretation"
        
        # Generate confidence assessment
        avg_confidence = 0.0
        confidence_values = list(inferences.get('inference_confidence', {}).values())
        if confidence_values:
            avg_confidence = sum(confidence_values) / len(confidence_values)
        
        if avg_confidence > 0.8:
            insights['confidence_assessment'] = "High confidence in causal inferences"
        elif avg_confidence > 0.6:
            insights['confidence_assessment'] = "Moderate confidence in causal inferences"
        else:
            insights['confidence_assessment'] = "Low confidence requiring additional validation"
        
        # Identify limitations and caveats
        if validity_assessment.get('internal_validity', {}).get('validity_score', 0) < 0.6:
            insights['limitations_and_caveats'].append("Internal validity concerns limit causal conclusions")
        
        if len(inferences.get('rejected_inferences', [])) > 0:
            insights['limitations_and_caveats'].append("Some causal claims lack sufficient support")
        
        if overall_validity < 0.6:
            insights['limitations_and_caveats'].append("Limited validity restricts generalizability")
        
        return insights
    
    # Placeholder implementations for remaining methods
    
    def _calculate_inference_strength(self, inferences: dict, validity_assessment: dict) -> float:
        """Calculate inference strength"""
        strong_count = len(inferences.get('strong_inferences', []))
        total_count = sum(len(inf_list) for inf_list in inferences.values() if isinstance(inf_list, list))
        strength_ratio = strong_count / max(1, total_count)
        
        validity_score = validity_assessment.get('overall_validity', {}).get('composite_score', 0.0)
        
        return (strength_ratio * 0.7) + (validity_score * 0.3)
    
    def _identify_alternative_explanations(self, causal_claims: dict, confounder_analysis: dict) -> dict:
        """Identify alternative explanations"""
        return {
            'alternative_explanations': ['reverse_causation', 'third_variable', 'spurious_correlation'],
            'explanation_plausibility': {'reverse_causation': 0.3, 'third_variable': 0.5},
            'explanation_assessment': 'moderate_alternatives_exist'
        }
    
    # Intervention analysis methods (simplified implementations)
    
    def _identify_intervention_targets(self, schema: dict, entities: List[str], query: str) -> dict:
        """Identify intervention targets"""
        return {
            'primary_targets': entities[:2],
            'secondary_targets': entities[2:4] if len(entities) > 2 else [],
            'target_rationale': 'high_leverage_points'
        }
    
    def _design_intervention_strategies(self, targets: dict, schema: dict, relationships: List[str]) -> dict:
        """Design intervention strategies"""
        return {
            'direct_interventions': ['target_modification', 'direct_manipulation'],
            'indirect_interventions': ['mediator_targeting', 'pathway_modification'],
            'multi_level_interventions': ['system_wide_change', 'coordinated_approach']
        }
    
    def _analyze_intervention_mechanisms(self, strategies: dict, targets: dict) -> dict:
        """Analyze intervention mechanisms"""
        return {
            'mechanism_types': ['behavioral', 'structural', 'environmental'],
            'mechanism_pathways': ['direct_effect', 'mediated_effect'],
            'mechanism_strength': 'moderate'
        }
    
    def _assess_intervention_feasibility(self, strategies: dict, mechanisms: dict) -> dict:
        """Assess intervention feasibility"""
        return {
            'feasibility_score': 0.7,
            'feasibility_factors': ['resource_requirements', 'implementation_complexity'],
            'feasibility_assessment': 'moderately_feasible'
        }
    
    def _predict_intervention_effects(self, strategies: dict, targets: dict, mechanisms: dict) -> dict:
        """Predict intervention effects"""
        return {
            'predicted_effects': ['primary_effect', 'secondary_effect'],
            'effect_magnitude': 'moderate',
            'effect_timeline': 'medium_term'
        }
    
    def _analyze_side_effects(self, strategies: dict, predicted_effects: dict, schema: dict) -> dict:
        """Analyze side effects"""
        return {
            'potential_side_effects': ['unintended_consequences', 'system_disruption'],
            'side_effect_probability': 'moderate',
            'mitigation_strategies': ['monitoring', 'adaptive_implementation']
        }
    
    def _generate_intervention_insights(self, strategies: dict, predicted_effects: dict, feasibility: dict) -> dict:
        """Generate intervention insights"""
        return {
            'key_insights': ['intervention_opportunities_identified', 'feasibility_assessed'],
            'intervention_recommendations': ['targeted_approach', 'phased_implementation'],
            'success_factors': ['stakeholder_engagement', 'resource_allocation']
        }
    
    def _calculate_intervention_complexity(self, strategies: dict, mechanisms: dict) -> float:
        """Calculate intervention complexity"""
        strategy_count = sum(len(v) if isinstance(v, list) else 1 for v in strategies.values())
        mechanism_count = sum(len(v) if isinstance(v, list) else 1 for v in mechanisms.values())
        return min(1.0, (strategy_count + mechanism_count) / 10.0)
    
    def _create_implementation_roadmap(self, strategies: dict, feasibility: dict) -> dict:
        """Create implementation roadmap"""
        return {
            'implementation_phases': ['planning', 'pilot', 'full_implementation'],
            'timeline': 'medium_term',
            'milestones': ['phase_1_completion', 'evaluation_checkpoint'],
            'resource_requirements': 'moderate'
        }
    
    # Counterfactual analysis methods (simplified implementations)
    
    def _identify_counterfactual_scenarios(self, schema: dict, entities: List[str], relationships: List[str]) -> dict:
        """Identify counterfactual scenarios"""
        return {
            'baseline_scenario': 'current_state',
            'counterfactual_scenarios': ['alternative_1', 'alternative_2'],
            'scenario_differences': ['key_variable_change', 'relationship_modification']
        }
    
    def _build_counterfactual_models(self, scenarios: dict, schema: dict) -> dict:
        """Build counterfactual models"""
        return {
            'model_specifications': {'scenario_1': 'model_spec_1', 'scenario_2': 'model_spec_2'},
            'model_assumptions': ['ceteris_paribus', 'stable_relationships'],
            'model_validity': 'moderate'
        }
    
    def _analyze_counterfactual_outcomes(self, models: dict, scenarios: dict) -> dict:
        """Analyze counterfactual outcomes"""
        return {
            'outcome_predictions': {'scenario_1': 'outcome_1', 'scenario_2': 'outcome_2'},
            'outcome_differences': 'moderate_difference',
            'outcome_confidence': 'moderate'
        }
    
    def _compare_factual_counterfactual(self, outcomes: dict, schema: dict) -> dict:
        """Compare factual vs counterfactual"""
        return {
            'comparison_metrics': ['difference_magnitude', 'direction_of_change'],
            'comparison_results': 'significant_difference',
            'comparison_confidence': 'moderate'
        }
    
    def _assess_counterfactual_validity(self, scenarios: dict, models: dict, outcomes: dict) -> dict:
        """Assess counterfactual validity"""
        return {
            'validity_score': 0.7,
            'validity_factors': ['scenario_plausibility', 'model_adequacy'],
            'validity_limitations': ['assumption_violations', 'model_uncertainty']
        }
    
    def _generate_counterfactual_insights(self, scenarios: dict, outcomes: dict, comparisons: dict) -> dict:
        """Generate counterfactual insights"""
        return {
            'key_insights': ['counterfactual_analysis_completed', 'alternative_outcomes_explored'],
            'causal_implications': ['treatment_effect_estimation', 'causal_attribution'],
            'practical_implications': ['policy_recommendations', 'intervention_design']
        }
    
    def _calculate_counterfactual_complexity(self, scenarios: dict, models: dict) -> float:
        """Calculate counterfactual complexity"""
        scenario_count = len(scenarios.get('counterfactual_scenarios', []))
        model_count = len(models.get('model_specifications', {}))
        return min(1.0, (scenario_count + model_count) / 6.0)
    
    def _perform_causal_attribution(self, outcomes: dict, comparisons: dict) -> dict:
        """Perform causal attribution"""
        return {
            'attribution_analysis': 'difference_based_attribution',
            'causal_contribution': 'moderate_contribution',
            'attribution_confidence': 'moderate'
        }
    
    # Integration methods
    
    def _find_causal_connections(self, pathway: dict, inference: dict, intervention: dict, counterfactual: dict) -> dict:
        """Find causal connections"""
        return {
            'pathway_inference_alignment': 'consistent',
            'inference_intervention_coherence': 'moderate',
            'intervention_counterfactual_consistency': 'good',
            'cross_method_validation': 'positive'
        }
    
    def _synthesize_causal_insights(self, pathway: dict, inference: dict, intervention: dict, counterfactual: dict, connections: dict) -> dict:
        """Synthesize causal insights"""
        return {
            'unified_causal_understanding': 'comprehensive_causal_model',
            'causal_confidence': 'moderate',
            'causal_recommendations': ['evidence_based_interventions', 'causal_monitoring']
        }
    
    def _assess_causal_coherence(self, pathway: dict, inference: dict, intervention: dict, counterfactual: dict) -> dict:
        """Assess causal coherence"""
        return {
            'coherence_score': 0.75,
            'coherence_factors': ['method_consistency', 'result_alignment'],
            'coherence_issues': []
        }
    
    def _generate_unified_causal_model(self, pathway: dict, inference: dict, intervention: dict, counterfactual: dict) -> dict:
        """Generate unified causal model"""
        return {
            'model_components': ['pathways', 'inferences', 'interventions', 'counterfactuals'],
            'model_integration': 'comprehensive_framework',
            'model_validity': 'good'
        }
    
    def _assess_causal_certainty(self, pathway: dict, inference: dict, intervention: dict, counterfactual: dict) -> dict:
        """Assess causal certainty"""
        return {
            'certainty_level': 'moderate',
            'certainty_factors': ['evidence_strength', 'method_convergence'],
            'uncertainty_sources': ['measurement_error', 'model_assumptions']
        }
    
    def _assess_causal_integration_quality(self, connections: dict, coherence: dict) -> float:
        """Assess causal integration quality"""
        return coherence.get('coherence_score', 0.7)
    
    # Fallback methods
    
    def _generate_basic_pathways(self, entities: List[str], relationships: List[str]) -> dict:
        """Generate basic pathway fallback"""
        return {
            'basic_pathways': [f'pathway_from_{rel}' for rel in relationships[:2]],
            'pathway_count': len(relationships),
            'fallback_type': 'relationship_based_pathways'
        }
    
    def _generate_basic_inferences(self, entities: List[str], relationships: List[str]) -> dict:
        """Generate basic inference fallback"""
        return {
            'basic_inferences': ['weak_causal_relationship', 'potential_influence'],
            'inference_confidence': 'low',
            'fallback_type': 'minimal_inference'
        }
    
    def _generate_basic_interventions(self, entities: List[str], query: str) -> dict:
        """Generate basic intervention fallback"""
        return {
            'basic_interventions': ['modify_primary_entity', 'adjust_system_parameters'],
            'intervention_feasibility': 'unknown',
            'fallback_type': 'generic_interventions'
        }
    
    def _generate_basic_counterfactuals(self, entities: List[str], relationships: List[str]) -> dict:
        """Generate basic counterfactual fallback"""
        return {
            'basic_counterfactuals': ['alternative_scenario_1', 'alternative_scenario_2'],
            'counterfactual_plausibility': 'moderate',
            'fallback_type': 'simple_alternatives'
        }
    
    def _generate_basic_causal_integration(self, pathway: dict, inference: dict, intervention: dict, counterfactual: dict) -> dict:
        """Generate basic causal integration fallback"""
        present_analyses = sum(1 for analysis in [pathway, inference, intervention, counterfactual] if analysis and not analysis.get('error'))
        
        return {
            'basic_integration': f'Causal analysis completed with {present_analyses}/4 components',
            'component_status': {
                'pathway': 'present' if pathway and not pathway.get('error') else 'missing',
                'inference': 'present' if inference and not inference.get('error') else 'missing',
                'intervention': 'present' if intervention and not intervention.get('error') else 'missing',
                'counterfactual': 'present' if counterfactual and not counterfactual.get('error') else 'missing'
            },
            'integration_quality': present_analyses / 4.0
        }