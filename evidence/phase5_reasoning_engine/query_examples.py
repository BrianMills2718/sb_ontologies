"""
Query Examples for Cross-Purpose Reasoning Engine
Demonstrates sophisticated reasoning capabilities across all five theoretical purposes
"""

from reasoning_engine import CrossPurposeReasoningEngine
from cross_purpose_integration import CrossPurposeIntegrator
import json


def demonstrate_query_capabilities():
    """Demonstrate reasoning engine capabilities with various query types"""
    
    engine = CrossPurposeReasoningEngine()
    integrator = CrossPurposeIntegrator()
    
    # Example schema for demonstrations
    example_schema = {
        'entities': {
            'urban_system': {
                'type': 'complex_adaptive_system',
                'properties': ['dynamic', 'multi_scale', 'emergent'],
                'components': ['infrastructure', 'population', 'governance', 'economy', 'environment']
            },
            'transportation_network': {
                'type': 'infrastructure_system',
                'properties': ['networked', 'flow_dependent', 'capacity_limited'],
                'components': ['roads', 'public_transit', 'pedestrian_pathways', 'cycling_infrastructure']
            },
            'community_organizations': {
                'type': 'social_institutions',
                'properties': ['participatory', 'adaptive', 'resource_dependent'],
                'components': ['neighborhood_groups', 'advocacy_organizations', 'service_providers']
            },
            'environmental_systems': {
                'type': 'ecological_infrastructure',
                'properties': ['self_regulating', 'interconnected', 'vulnerable'],
                'components': ['green_spaces', 'water_systems', 'air_quality', 'urban_biodiversity']
            }
        },
        'relationships': {
            'system_integration': {
                'type': 'multi_directional_coupling',
                'strength': 'strong',
                'dynamics': 'coevolutionary'
            },
            'resource_flows': {
                'type': 'material_energy_information',
                'strength': 'variable',
                'patterns': 'network_dependent'
            },
            'governance_coordination': {
                'type': 'institutional_oversight',
                'strength': 'moderate',
                'scope': 'multi_level'
            }
        },
        'properties': {
            'complexity': 'very_high',
            'domain': 'urban_sustainability',
            'temporal_dynamics': 'multi_scale',
            'spatial_scale': 'city_region'
        }
    }
    
    # Query examples demonstrating different analytical purposes
    query_examples = {
        'descriptive_focused': {
            'query': "What are the main types of urban systems and how are they organized? Classify the key components and describe their structural relationships.",
            'expected_purpose': 'descriptive',
            'analytical_focus': 'classification and structural analysis'
        },
        
        'explanatory_focused': {
            'query': "How do urban transportation networks function and why do certain patterns emerge? Explain the mechanisms that drive system behavior.",
            'expected_purpose': 'explanatory',
            'analytical_focus': 'mechanisms and processes'
        },
        
        'predictive_focused': {
            'query': "What trends can we expect in urban development over the next decade? What scenarios are most likely given current patterns?",
            'expected_purpose': 'predictive',
            'analytical_focus': 'forecasting and scenario analysis'
        },
        
        'causal_focused': {
            'query': "What causes urban sustainability challenges and how do different factors influence outcomes? What are the key causal pathways?",
            'expected_purpose': 'causal',
            'analytical_focus': 'causal analysis and inference'
        },
        
        'intervention_focused': {
            'query': "What actions should be taken to improve urban sustainability? How should interventions be designed and implemented?",
            'expected_purpose': 'intervention',
            'analytical_focus': 'action design and implementation'
        },
        
        'multi_purpose_integrated': {
            'query': "Analyze urban sustainability comprehensively across all theoretical purposes: describe the system structure, explain how it works, predict future developments, identify causal relationships, and design effective interventions.",
            'expected_purpose': 'all_purposes',
            'analytical_focus': 'comprehensive multi-purpose analysis'
        },
        
        'complex_integration': {
            'query': "Provide an integrated analysis that combines descriptive taxonomy of urban systems, explanatory understanding of mechanisms, predictive assessment of future scenarios, causal analysis of key relationships, and intervention strategies for sustainability improvement.",
            'expected_purpose': 'all_purposes_integrated',
            'analytical_focus': 'sophisticated cross-purpose synthesis'
        },
        
        'balanced_comprehensive': {
            'query': "Examine this urban system with equal analytical depth across all five theoretical dimensions: systematic classification, mechanistic explanation, predictive modeling, causal inference, and intervention design. Ensure equal sophistication in each analytical approach.",
            'expected_purpose': 'balanced_all_purposes',
            'analytical_focus': 'equal analytical sophistication'
        },
        
        'emergent_synthesis': {
            'query': "Beyond individual analytical approaches, what emergent insights arise from integrating descriptive, explanatory, predictive, causal, and intervention perspectives? Generate novel understanding through cross-purpose synthesis.",
            'expected_purpose': 'emergent_integration',
            'analytical_focus': 'emergent property identification'
        },
        
        'theoretical_framework': {
            'query': "Develop a unified theoretical framework that systematically integrates classification schemes, explanatory mechanisms, predictive models, causal theories, and intervention strategies for urban sustainability analysis.",
            'expected_purpose': 'unified_framework',
            'analytical_focus': 'theoretical framework development'
        }
    }
    
    print("=" * 80)
    print("CROSS-PURPOSE REASONING ENGINE - QUERY EXAMPLES DEMONSTRATION")
    print("=" * 80)
    
    results = {}
    
    for query_id, query_info in query_examples.items():
        print(f"\n{'-' * 60}")
        print(f"QUERY EXAMPLE: {query_id.upper().replace('_', ' ')}")
        print(f"Focus: {query_info['analytical_focus']}")
        print(f"{'-' * 60}")
        print(f"Query: {query_info['query']}")
        print(f"\nExpected Purpose: {query_info['expected_purpose']}")
        
        try:
            # Execute reasoning based on query type
            if query_info['expected_purpose'] in ['all_purposes', 'all_purposes_integrated', 'balanced_all_purposes', 'emergent_integration', 'unified_framework']:
                # Multi-purpose analysis
                result = engine.analyze_multi_purpose(example_schema, query_info['query'])
                
                # Additional integration for complex queries
                if query_info['expected_purpose'] in ['emergent_integration', 'unified_framework']:
                    purpose_analyses = {
                        'descriptive_analysis': result.get('descriptive_analysis', {}),
                        'explanatory_analysis': result.get('explanatory_analysis', {}),
                        'predictive_analysis': result.get('predictive_analysis', {}),
                        'causal_analysis': result.get('causal_analysis', {}),
                        'intervention_analysis': result.get('intervention_analysis', {})
                    }
                    
                    integration_result = integrator.integrate_purposes(purpose_analyses)
                    result['advanced_integration'] = integration_result
            
            else:
                # Single-purpose focused analysis
                if query_info['expected_purpose'] == 'descriptive':
                    result = engine.reason_descriptive(example_schema, query_info['query'])
                elif query_info['expected_purpose'] == 'explanatory':
                    result = engine.reason_explanatory(example_schema, query_info['query'])
                elif query_info['expected_purpose'] == 'predictive':
                    result = engine.reason_predictive(example_schema, query_info['query'])
                elif query_info['expected_purpose'] == 'causal':
                    result = engine.reason_causal(example_schema, query_info['query'])
                elif query_info['expected_purpose'] == 'intervention':
                    result = engine.reason_intervention(example_schema, query_info['query'])
                else:
                    result = {'error': f"Unknown purpose: {query_info['expected_purpose']}"}
            
            # Assess result quality
            result_assessment = assess_query_result(result, query_info)
            
            print(f"\nResult Assessment:")
            print(f"  Success: {'✓' if result_assessment['success'] else '✗'}")
            print(f"  Quality Score: {result_assessment['quality_score']:.2f}")
            print(f"  Analytical Depth: {result_assessment['analytical_depth']}")
            print(f"  Purpose Coverage: {result_assessment['purpose_coverage']}")
            
            if result_assessment['key_insights']:
                print(f"\nKey Insights Generated:")
                for i, insight in enumerate(result_assessment['key_insights'][:3], 1):
                    print(f"  {i}. {insight}")
            
            results[query_id] = {
                'query_info': query_info,
                'result_assessment': result_assessment,
                'execution_status': 'success' if result_assessment['success'] else 'failed'
            }
            
        except Exception as e:
            print(f"\n✗ Query execution failed: {str(e)}")
            results[query_id] = {
                'query_info': query_info,
                'execution_status': 'error',
                'error': str(e)
            }
    
    # Generate summary
    print(f"\n{'=' * 80}")
    print("QUERY EXAMPLES SUMMARY")
    print(f"{'=' * 80}")
    
    total_queries = len(query_examples)
    successful_queries = sum(1 for result in results.values() 
                           if result.get('execution_status') == 'success')
    
    print(f"Total Query Examples: {total_queries}")
    print(f"Successful Executions: {successful_queries}")
    print(f"Success Rate: {successful_queries/total_queries:.1%}")
    
    # Purpose coverage analysis
    purpose_coverage = analyze_purpose_coverage(results)
    print(f"\nPurpose Coverage Analysis:")
    for purpose, coverage in purpose_coverage.items():
        print(f"  {purpose.capitalize()}: {coverage['count']} queries, avg quality {coverage['avg_quality']:.2f}")
    
    return results


def assess_query_result(result: dict, query_info: dict) -> dict:
    """Assess the quality of a query result"""
    
    assessment = {
        'success': False,
        'quality_score': 0.0,
        'analytical_depth': 'unknown',
        'purpose_coverage': 'none',
        'key_insights': [],
        'sophistication_indicators': []
    }
    
    try:
        # Check for errors
        if result.get('error'):
            return assessment
        
        assessment['success'] = True
        
        # Assess analytical depth
        depth_indicators = []
        
        # Check for sophisticated analysis markers
        sophisticated_terms = ['sophisticated', 'complex', 'comprehensive', 'integrated', 'multi_level']
        result_text = str(result).lower()
        
        for term in sophisticated_terms:
            if term in result_text:
                depth_indicators.append(term)
                assessment['sophistication_indicators'].append(term)
        
        # Assess based on query type
        expected_purpose = query_info.get('expected_purpose', 'unknown')
        
        if expected_purpose in ['all_purposes', 'all_purposes_integrated', 'balanced_all_purposes']:
            # Multi-purpose analysis assessment
            purposes = ['descriptive_analysis', 'explanatory_analysis', 'predictive_analysis', 'causal_analysis', 'intervention_analysis']
            present_purposes = sum(1 for purpose in purposes if purpose in result)
            
            assessment['purpose_coverage'] = f"{present_purposes}/5 purposes"
            
            # Quality based on purpose coverage and integration
            purpose_quality = present_purposes / 5.0
            integration_quality = 1.0 if result.get('cross_purpose_insights') else 0.5
            assessment['quality_score'] = (purpose_quality * 0.7) + (integration_quality * 0.3)
            
        else:
            # Single-purpose analysis assessment
            assessment['purpose_coverage'] = 'single_purpose'
            
            # Check for insights
            insights = result.get('insights', {})
            if insights:
                key_insights = insights.get('key_insights', [])
                assessment['key_insights'] = key_insights
                
                # Quality based on insight count and sophistication
                insight_quality = min(1.0, len(key_insights) / 3.0)
                sophistication_quality = len(depth_indicators) / 5.0
                assessment['quality_score'] = (insight_quality * 0.6) + (sophistication_quality * 0.4)
        
        # Determine analytical depth
        if assessment['quality_score'] > 0.8:
            assessment['analytical_depth'] = 'very_high'
        elif assessment['quality_score'] > 0.6:
            assessment['analytical_depth'] = 'high'
        elif assessment['quality_score'] > 0.4:
            assessment['analytical_depth'] = 'moderate'
        elif assessment['quality_score'] > 0.2:
            assessment['analytical_depth'] = 'basic'
        else:
            assessment['analytical_depth'] = 'minimal'
        
        # Extract key insights
        if not assessment['key_insights']:
            # Try to extract from different result structures
            for key, value in result.items():
                if isinstance(value, dict) and 'insights' in value:
                    insights = value['insights']
                    if isinstance(insights, dict) and 'key_insights' in insights:
                        assessment['key_insights'].extend(insights['key_insights'][:2])
        
    except Exception as e:
        assessment['error'] = str(e)
    
    return assessment


def analyze_purpose_coverage(results: dict) -> dict:
    """Analyze coverage across different analytical purposes"""
    
    purpose_analysis = {
        'descriptive': {'count': 0, 'total_quality': 0.0, 'avg_quality': 0.0},
        'explanatory': {'count': 0, 'total_quality': 0.0, 'avg_quality': 0.0},
        'predictive': {'count': 0, 'total_quality': 0.0, 'avg_quality': 0.0},
        'causal': {'count': 0, 'total_quality': 0.0, 'avg_quality': 0.0},
        'intervention': {'count': 0, 'total_quality': 0.0, 'avg_quality': 0.0},
        'multi_purpose': {'count': 0, 'total_quality': 0.0, 'avg_quality': 0.0}
    }
    
    for query_id, result_info in results.items():
        if result_info.get('execution_status') == 'success':
            query_info = result_info.get('query_info', {})
            result_assessment = result_info.get('result_assessment', {})
            
            expected_purpose = query_info.get('expected_purpose', 'unknown')
            quality_score = result_assessment.get('quality_score', 0.0)
            
            # Categorize by purpose
            if expected_purpose == 'descriptive':
                purpose_analysis['descriptive']['count'] += 1
                purpose_analysis['descriptive']['total_quality'] += quality_score
            elif expected_purpose == 'explanatory':
                purpose_analysis['explanatory']['count'] += 1
                purpose_analysis['explanatory']['total_quality'] += quality_score
            elif expected_purpose == 'predictive':
                purpose_analysis['predictive']['count'] += 1
                purpose_analysis['predictive']['total_quality'] += quality_score
            elif expected_purpose == 'causal':
                purpose_analysis['causal']['count'] += 1
                purpose_analysis['causal']['total_quality'] += quality_score
            elif expected_purpose == 'intervention':
                purpose_analysis['intervention']['count'] += 1
                purpose_analysis['intervention']['total_quality'] += quality_score
            else:
                purpose_analysis['multi_purpose']['count'] += 1
                purpose_analysis['multi_purpose']['total_quality'] += quality_score
    
    # Calculate average qualities
    for purpose, data in purpose_analysis.items():
        if data['count'] > 0:
            data['avg_quality'] = data['total_quality'] / data['count']
    
    return purpose_analysis


def main():
    """Main demonstration function"""
    print("Initializing Cross-Purpose Reasoning Engine Query Examples...")
    
    try:
        results = demonstrate_query_capabilities()
        
        # Save results
        import time
        timestamp = int(time.time())
        results_file = f"/home/brian/lit_review/evidence/phase5_reasoning_engine/query_examples_results_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\nQuery examples results saved to: {results_file}")
        
        return results
        
    except Exception as e:
        print(f"Query examples demonstration failed: {str(e)}")
        return None


if __name__ == "__main__":
    main()