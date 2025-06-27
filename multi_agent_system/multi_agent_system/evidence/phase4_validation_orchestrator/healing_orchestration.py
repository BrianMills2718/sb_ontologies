#!/usr/bin/env python3
"""
Healing Orchestration for ValidationDrivenOrchestrator
====================================================

Coordinates healing systems for automatic correction of validation failures
across all four validation levels. Integrates AST healing, semantic healing,
and configuration regeneration with the orchestration pipeline.

Healing Systems:
1. AST Healing - Level 2 component logic failures
2. Configuration Regeneration - Level 3 integration failures  
3. Semantic Healing - Level 4 semantic failures
"""

import asyncio
import logging
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

from validation_result_types import (
    OrchestratedHealingResult, OrchestratedRegenerationResult,
    HealingType, create_healing_success, create_healing_failure,
    create_regeneration_success, create_regeneration_failure
)


@dataclass
class HealingStrategy:
    """Strategy for healing specific types of validation failures"""
    failure_type: str
    healing_method: str
    healing_system: str
    confidence_level: float
    estimated_success_rate: float


class OrchestratedASTHealer:
    """
    AST healer integration for ValidationDrivenOrchestrator Level 2 failures.
    
    Integrates with Phase 1 cleaned AST healing system to automatically
    correct component logic errors identified during Level 2 validation.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("OrchestratedASTHealer")
        
        # AST healing configuration
        self.healing_strategies = {
            'syntax_error': HealingStrategy(
                failure_type='syntax_error',
                healing_method='syntax_correction',
                healing_system='ast_parser',
                confidence_level=0.9,
                estimated_success_rate=0.85
            ),
            'import_error': HealingStrategy(
                failure_type='import_error',
                healing_method='import_resolution',
                healing_system='dependency_resolver',
                confidence_level=0.8,
                estimated_success_rate=0.75
            ),
            'type_error': HealingStrategy(
                failure_type='type_error',
                healing_method='type_annotation_fix',
                healing_system='type_checker',
                confidence_level=0.7,
                estimated_success_rate=0.65
            ),
            'configuration_error': HealingStrategy(
                failure_type='configuration_error',
                healing_method='config_schema_fix',
                healing_system='config_validator',
                confidence_level=0.8,
                estimated_success_rate=0.70
            )
        }
        
        self.logger.info("✅ OrchestratedASTHealer initialized")
    
    async def heal_component_logic(self, component: Dict[str, Any], validation_failures: List[str]) -> OrchestratedHealingResult:
        """
        Heal component logic issues identified in Level 2 validation.
        
        This method analyzes validation failures and applies appropriate
        AST healing techniques to automatically correct component logic errors.
        
        Args:
            component: Component dictionary with logic errors
            validation_failures: List of validation failure messages
            
        Returns:
            OrchestratedHealingResult with healing outcome
        """
        component_name = component.get('name', 'unnamed')
        self.logger.info(f"🔧 Attempting AST healing for component: {component_name}")
        
        try:
            # Analyze validation failures to determine healing strategy
            healing_plan = await self._analyze_failures_for_healing(validation_failures)
            
            if not healing_plan['healable']:
                return create_healing_failure(
                    f"Component logic failures not suitable for AST healing: {healing_plan['reason']}",
                    HealingType.AST_HEALING
                )
            
            # Apply AST healing transformations
            healed_component = await self._apply_ast_healing(component, healing_plan)
            
            # Validate healing success
            healing_validation = await self._validate_healing_success(component, healed_component)
            
            if healing_validation['successful']:
                self.logger.info(f"✅ AST healing successful for component: {component_name}")
                
                return create_healing_success(
                    healing_type=HealingType.AST_HEALING,
                    healed_artifact=healed_component,
                    details={
                        'healing_plan': healing_plan,
                        'transformations_applied': healing_validation['transformations'],
                        'issues_fixed': len(validation_failures),
                        'confidence_score': healing_plan['confidence']
                    }
                )
            else:
                return create_healing_failure(
                    f"AST healing validation failed: {healing_validation['error']}",
                    HealingType.AST_HEALING
                )
                
        except Exception as e:
            self.logger.error(f"❌ AST healing error for {component_name}: {e}")
            return create_healing_failure(
                f"AST healing failed due to error: {e}",
                HealingType.AST_HEALING
            )
    
    async def _analyze_failures_for_healing(self, validation_failures: List[str]) -> Dict[str, Any]:
        """Analyze validation failures to determine if AST healing is applicable"""
        healable_failures = []
        healing_strategies = []
        total_confidence = 0.0
        
        for failure in validation_failures:
            failure_lower = failure.lower()
            
            # Check for syntax errors
            if any(term in failure_lower for term in ['syntax', 'parse', 'invalid syntax']):
                strategy = self.healing_strategies['syntax_error']
                healable_failures.append(failure)
                healing_strategies.append(strategy)
                total_confidence += strategy.confidence_level
            
            # Check for import errors
            elif any(term in failure_lower for term in ['import', 'module', 'not found']):
                strategy = self.healing_strategies['import_error']
                healable_failures.append(failure)
                healing_strategies.append(strategy)
                total_confidence += strategy.confidence_level
            
            # Check for type errors
            elif any(term in failure_lower for term in ['type', 'attribute', 'method']):
                strategy = self.healing_strategies['type_error']
                healable_failures.append(failure)
                healing_strategies.append(strategy)
                total_confidence += strategy.confidence_level
            
            # Check for configuration errors
            elif any(term in failure_lower for term in ['config', 'required', 'missing']):
                strategy = self.healing_strategies['configuration_error']
                healable_failures.append(failure)
                healing_strategies.append(strategy)
                total_confidence += strategy.confidence_level
        
        # Determine if healing is feasible
        healable_ratio = len(healable_failures) / len(validation_failures) if validation_failures else 0
        average_confidence = total_confidence / len(healing_strategies) if healing_strategies else 0
        
        if healable_ratio >= 0.7 and average_confidence >= 0.6:
            return {
                'healable': True,
                'confidence': average_confidence,
                'healable_failures': healable_failures,
                'strategies': healing_strategies,
                'healable_ratio': healable_ratio
            }
        else:
            return {
                'healable': False,
                'reason': f"Low healability (ratio: {healable_ratio:.2f}, confidence: {average_confidence:.2f})",
                'healable_failures': healable_failures,
                'healable_ratio': healable_ratio
            }
    
    async def _apply_ast_healing(self, component: Dict[str, Any], healing_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Apply AST healing transformations to the component"""
        healed_component = component.copy()
        transformations_applied = []
        
        for strategy in healing_plan['strategies']:
            if strategy.failure_type == 'syntax_error':
                transformation = await self._heal_syntax_errors(healed_component)
                transformations_applied.append(transformation)
            elif strategy.failure_type == 'import_error':
                transformation = await self._heal_import_errors(healed_component)
                transformations_applied.append(transformation)
            elif strategy.failure_type == 'type_error':
                transformation = await self._heal_type_errors(healed_component)
                transformations_applied.append(transformation)
            elif strategy.failure_type == 'configuration_error':
                transformation = await self._heal_configuration_errors(healed_component)
                transformations_applied.append(transformation)
        
        # Store healing metadata
        healed_component['_healing_metadata'] = {
            'healing_applied': True,
            'healing_type': 'ast_healing',
            'transformations': transformations_applied,
            'original_component': component
        }
        
        return healed_component
    
    async def _heal_syntax_errors(self, component: Dict[str, Any]) -> Dict[str, str]:
        """Heal syntax errors in component configuration"""
        transformation = {
            'type': 'syntax_correction',
            'description': 'Fixed syntax errors in component configuration',
            'changes': []
        }
        
        # Fix common syntax issues in configuration
        configuration = component.get('configuration', {})
        
        # Ensure all required fields are present and properly formatted
        if 'resource_requirements' in configuration:
            resources = configuration['resource_requirements']
            
            # Fix numeric type issues
            for field in ['memory_mb', 'cpu_cores', 'disk_gb']:
                if field in resources:
                    try:
                        # Ensure numeric values are properly typed
                        if isinstance(resources[field], str):
                            if '.' in resources[field]:
                                resources[field] = float(resources[field])
                            else:
                                resources[field] = int(resources[field])
                            transformation['changes'].append(f"Fixed {field} type conversion")
                    except ValueError:
                        # Set reasonable defaults
                        defaults = {'memory_mb': 512, 'cpu_cores': 1, 'disk_gb': 10}
                        resources[field] = defaults.get(field, 1)
                        transformation['changes'].append(f"Set default value for {field}")
        
        return transformation
    
    async def _heal_import_errors(self, component: Dict[str, Any]) -> Dict[str, str]:
        """Heal import-related errors"""
        transformation = {
            'type': 'import_resolution',
            'description': 'Resolved import and dependency issues',
            'changes': []
        }
        
        # Fix dependency specifications
        dependencies = component.get('dependencies', [])
        for dependency in dependencies:
            # Ensure required fields are present
            if 'component_name' not in dependency:
                if 'name' in dependency:
                    dependency['component_name'] = dependency['name']
                    transformation['changes'].append("Fixed dependency component_name reference")
            
            if 'dependency_type' not in dependency:
                dependency['dependency_type'] = 'service_dependency'  # Default
                transformation['changes'].append("Added default dependency_type")
        
        return transformation
    
    async def _heal_type_errors(self, component: Dict[str, Any]) -> Dict[str, str]:
        """Heal type-related errors"""
        transformation = {
            'type': 'type_correction',
            'description': 'Fixed type annotation and attribute errors',
            'changes': []
        }
        
        # Ensure component has required fields with correct types
        if not isinstance(component.get('name'), str):
            component['name'] = str(component.get('name', 'healed_component'))
            transformation['changes'].append("Fixed component name type")
        
        if not isinstance(component.get('type'), str):
            component['type'] = 'web_service'  # Default component type
            transformation['changes'].append("Set default component type")
        
        # Fix configuration structure
        if 'configuration' not in component:
            component['configuration'] = {}
            transformation['changes'].append("Added missing configuration section")
        
        return transformation
    
    async def _heal_configuration_errors(self, component: Dict[str, Any]) -> Dict[str, str]:
        """Heal configuration-related errors"""
        transformation = {
            'type': 'configuration_fix',
            'description': 'Fixed configuration schema and validation errors',
            'changes': []
        }
        
        configuration = component.get('configuration', {})
        
        # Add missing required configuration sections
        if component.get('type') == 'web_service':
            if 'ports' not in configuration:
                configuration['ports'] = [{'port': 8080, 'protocol': 'http'}]
                transformation['changes'].append("Added default port configuration for web service")
        
        # Fix resource requirements structure
        if 'resource_requirements' in configuration:
            resources = configuration['resource_requirements']
            required_fields = ['memory_mb', 'cpu_cores', 'disk_gb']
            defaults = {'memory_mb': 512, 'cpu_cores': 1, 'disk_gb': 10}
            
            for field in required_fields:
                if field not in resources:
                    resources[field] = defaults[field]
                    transformation['changes'].append(f"Added missing {field} resource requirement")
        
        return transformation
    
    async def _validate_healing_success(self, original_component: Dict[str, Any], healed_component: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that healing was successful"""
        
        # Basic validation checks
        validation_checks = []
        
        # Check required fields are present
        required_fields = ['name', 'type']
        for field in required_fields:
            if field in healed_component and healed_component[field]:
                validation_checks.append(f"Required field '{field}' present")
            else:
                return {
                    'successful': False,
                    'error': f"Required field '{field}' missing after healing"
                }
        
        # Check configuration structure
        if 'configuration' in healed_component:
            config = healed_component['configuration']
            if isinstance(config, dict):
                validation_checks.append("Configuration structure valid")
            else:
                return {
                    'successful': False,
                    'error': "Configuration is not a valid dictionary after healing"
                }
        
        # Check dependencies structure
        if 'dependencies' in healed_component:
            deps = healed_component['dependencies']
            if isinstance(deps, list):
                validation_checks.append("Dependencies structure valid")
            else:
                return {
                    'successful': False,
                    'error': "Dependencies is not a valid list after healing"
                }
        
        return {
            'successful': True,
            'transformations': healed_component.get('_healing_metadata', {}).get('transformations', []),
            'validation_checks': validation_checks
        }


class OrchestratedSemanticHealer:
    """
    Semantic healer integration for ValidationDrivenOrchestrator Level 4 failures.
    
    Integrates with Phase 1 cleaned semantic healing system to automatically
    correct semantic issues identified during Level 4 validation.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("OrchestratedSemanticHealer")
        
        # Semantic healing configuration
        self.healing_strategies = {
            'naming_inconsistency': HealingStrategy(
                failure_type='naming_inconsistency',
                healing_method='name_standardization',
                healing_system='naming_analyzer',
                confidence_level=0.8,
                estimated_success_rate=0.75
            ),
            'architectural_issue': HealingStrategy(
                failure_type='architectural_issue',
                healing_method='component_restructure',
                healing_system='architecture_optimizer',
                confidence_level=0.6,
                estimated_success_rate=0.55
            ),
            'coherence_issue': HealingStrategy(
                failure_type='coherence_issue',
                healing_method='coherence_improvement',
                healing_system='coherence_analyzer',
                confidence_level=0.7,
                estimated_success_rate=0.65
            )
        }
        
        self.logger.info("✅ OrchestratedSemanticHealer initialized")
    
    async def heal_system_semantics(self, blueprint: 'SystemBlueprint', validation_failures: List[str]) -> OrchestratedHealingResult:
        """
        Heal semantic issues identified in Level 4 validation.
        
        This method analyzes semantic validation failures and applies appropriate
        semantic healing techniques to improve system coherence and reasonableness.
        
        Args:
            blueprint: SystemBlueprint with semantic issues
            validation_failures: List of semantic validation failure messages
            
        Returns:
            OrchestratedHealingResult with healing outcome
        """
        self.logger.info("🧠 Attempting semantic healing for system blueprint")
        
        try:
            # Analyze semantic failures for healing opportunities
            healing_plan = await self._analyze_semantic_failures(validation_failures)
            
            if not healing_plan['healable']:
                return create_healing_failure(
                    f"Semantic failures not suitable for automatic healing: {healing_plan['reason']}",
                    HealingType.SEMANTIC_HEALING
                )
            
            # Apply semantic healing transformations
            healed_blueprint = await self._apply_semantic_healing(blueprint, healing_plan)
            
            # Validate semantic healing success
            healing_validation = await self._validate_semantic_healing(blueprint, healed_blueprint)
            
            if healing_validation['successful']:
                self.logger.info("✅ Semantic healing successful")
                
                return create_healing_success(
                    healing_type=HealingType.SEMANTIC_HEALING,
                    healed_artifact=healed_blueprint,
                    details={
                        'healing_plan': healing_plan,
                        'transformations_applied': healing_validation['transformations'],
                        'issues_fixed': len(validation_failures),
                        'semantic_improvements': healing_validation['improvements']
                    }
                )
            else:
                return create_healing_failure(
                    f"Semantic healing validation failed: {healing_validation['error']}",
                    HealingType.SEMANTIC_HEALING
                )
                
        except Exception as e:
            self.logger.error(f"❌ Semantic healing error: {e}")
            return create_healing_failure(
                f"Semantic healing failed due to error: {e}",
                HealingType.SEMANTIC_HEALING
            )
    
    async def _analyze_semantic_failures(self, validation_failures: List[str]) -> Dict[str, Any]:
        """Analyze semantic failures to determine healing feasibility"""
        healable_failures = []
        healing_strategies = []
        total_confidence = 0.0
        
        for failure in validation_failures:
            failure_lower = failure.lower()
            
            # Check for naming issues
            if any(term in failure_lower for term in ['naming', 'name', 'convention', 'inconsistent']):
                strategy = self.healing_strategies['naming_inconsistency']
                healable_failures.append(failure)
                healing_strategies.append(strategy)
                total_confidence += strategy.confidence_level
            
            # Check for architectural issues
            elif any(term in failure_lower for term in ['architectural', 'architecture', 'component', 'dependency']):
                strategy = self.healing_strategies['architectural_issue']
                healable_failures.append(failure)
                healing_strategies.append(strategy)
                total_confidence += strategy.confidence_level
            
            # Check for coherence issues
            elif any(term in failure_lower for term in ['coherence', 'semantic', 'description', 'alignment']):
                strategy = self.healing_strategies['coherence_issue']
                healable_failures.append(failure)
                healing_strategies.append(strategy)
                total_confidence += strategy.confidence_level
        
        # Determine healing feasibility
        healable_ratio = len(healable_failures) / len(validation_failures) if validation_failures else 0
        average_confidence = total_confidence / len(healing_strategies) if healing_strategies else 0
        
        if healable_ratio >= 0.5 and average_confidence >= 0.6:
            return {
                'healable': True,
                'confidence': average_confidence,
                'healable_failures': healable_failures,
                'strategies': healing_strategies,
                'healable_ratio': healable_ratio
            }
        else:
            return {
                'healable': False,
                'reason': f"Low semantic healability (ratio: {healable_ratio:.2f}, confidence: {average_confidence:.2f})",
                'healable_failures': healable_failures
            }
    
    async def _apply_semantic_healing(self, blueprint: 'SystemBlueprint', healing_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Apply semantic healing transformations to the blueprint"""
        healed_blueprint = {
            'description': blueprint.description,
            'components': [comp.copy() for comp in blueprint.components],
            'reasonableness_checks': blueprint.reasonableness_checks.copy(),
            'metadata': blueprint.metadata.copy() if hasattr(blueprint, 'metadata') else {}
        }
        
        transformations = []
        
        for strategy in healing_plan['strategies']:
            if strategy.failure_type == 'naming_inconsistency':
                transformation = await self._heal_naming_issues(healed_blueprint)
                transformations.append(transformation)
            elif strategy.failure_type == 'architectural_issue':
                transformation = await self._heal_architectural_issues(healed_blueprint)
                transformations.append(transformation)
            elif strategy.failure_type == 'coherence_issue':
                transformation = await self._heal_coherence_issues(healed_blueprint)
                transformations.append(transformation)
        
        # Store healing metadata
        healed_blueprint['_semantic_healing_metadata'] = {
            'healing_applied': True,
            'healing_type': 'semantic_healing',
            'transformations': transformations,
            'original_blueprint': blueprint
        }
        
        return healed_blueprint
    
    async def _heal_naming_issues(self, blueprint: Dict[str, Any]) -> Dict[str, str]:
        """Heal naming consistency issues"""
        transformation = {
            'type': 'naming_standardization',
            'description': 'Standardized component naming conventions',
            'changes': []
        }
        
        components = blueprint['components']
        
        # Standardize to snake_case convention
        for component in components:
            original_name = component.get('name', '')
            
            # Convert to snake_case
            standardized_name = self._to_snake_case(original_name)
            
            if standardized_name != original_name and standardized_name:
                component['name'] = standardized_name
                transformation['changes'].append(f"Renamed '{original_name}' to '{standardized_name}'")
                
                # Update references in dependencies
                for comp in components:
                    dependencies = comp.get('dependencies', [])
                    for dep in dependencies:
                        if dep.get('component_name') == original_name:
                            dep['component_name'] = standardized_name
                            transformation['changes'].append(f"Updated dependency reference from '{original_name}' to '{standardized_name}'")
        
        return transformation
    
    def _to_snake_case(self, name: str) -> str:
        """Convert name to snake_case convention"""
        if not name:
            return name
        
        # Handle camelCase
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
        
        # Handle kebab-case
        s3 = s2.replace('-', '_')
        
        # Convert to lowercase and clean up
        return re.sub(r'_+', '_', s3.lower()).strip('_')
    
    async def _heal_architectural_issues(self, blueprint: Dict[str, Any]) -> Dict[str, str]:
        """Heal architectural semantic issues"""
        transformation = {
            'type': 'architectural_improvement',
            'description': 'Improved architectural coherence',
            'changes': []
        }
        
        components = blueprint['components']
        component_types = [comp.get('type', '') for comp in components]
        
        # Add missing logical dependencies
        for component in components:
            component_name = component.get('name', '')
            component_type = component.get('type', '')
            dependencies = component.get('dependencies', [])
            dep_names = [dep.get('component_name', '') for dep in dependencies]
            
            # Web services should depend on databases if available
            if component_type == 'web_service':
                available_databases = [comp.get('name', '') for comp in components if comp.get('type') == 'database']
                
                for db_name in available_databases:
                    if db_name not in dep_names:
                        dependencies.append({
                            'component_name': db_name,
                            'dependency_type': 'data_dependency'
                        })
                        transformation['changes'].append(f"Added database dependency from {component_name} to {db_name}")
                
                component['dependencies'] = dependencies
        
        return transformation
    
    async def _heal_coherence_issues(self, blueprint: Dict[str, Any]) -> Dict[str, str]:
        """Heal semantic coherence issues"""
        transformation = {
            'type': 'coherence_improvement',
            'description': 'Improved system semantic coherence',
            'changes': []
        }
        
        # Improve description to match components
        components = blueprint['components']
        component_types = [comp.get('type', '') for comp in components]
        description = blueprint['description']
        
        # Add missing functionality mentions in description
        missing_mentions = []
        
        if 'database' in component_types and 'data' not in description.lower():
            missing_mentions.append('data storage')
        
        if 'authentication_service' in component_types and 'auth' not in description.lower():
            missing_mentions.append('user authentication')
        
        if any(t in component_types for t in ['web_service', 'api_gateway']) and 'web' not in description.lower():
            missing_mentions.append('web services')
        
        if missing_mentions:
            enhanced_description = description
            if not enhanced_description.endswith('.'):
                enhanced_description += '.'
            
            enhanced_description += f" The system includes {', '.join(missing_mentions)}."
            blueprint['description'] = enhanced_description
            transformation['changes'].append(f"Enhanced description to mention: {', '.join(missing_mentions)}")
        
        return transformation
    
    async def _validate_semantic_healing(self, original_blueprint: 'SystemBlueprint', healed_blueprint: Dict[str, Any]) -> Dict[str, Any]:
        """Validate semantic healing success"""
        improvements = []
        
        # Check naming consistency improvements
        original_names = [comp.get('name', '') for comp in original_blueprint.components]
        healed_names = [comp.get('name', '') for comp in healed_blueprint['components']]
        
        if len(set(self._get_naming_styles(healed_names))) < len(set(self._get_naming_styles(original_names))):
            improvements.append("Improved naming consistency")
        
        # Check description coherence
        if len(healed_blueprint['description']) > len(original_blueprint.description):
            improvements.append("Enhanced description coherence")
        
        # Check dependency completeness
        original_dep_count = sum(len(comp.get('dependencies', [])) for comp in original_blueprint.components)
        healed_dep_count = sum(len(comp.get('dependencies', [])) for comp in healed_blueprint['components'])
        
        if healed_dep_count > original_dep_count:
            improvements.append("Added missing logical dependencies")
        
        return {
            'successful': len(improvements) > 0,
            'transformations': healed_blueprint.get('_semantic_healing_metadata', {}).get('transformations', []),
            'improvements': improvements,
            'error': None if len(improvements) > 0 else "No semantic improvements were made"
        }
    
    def _get_naming_styles(self, names: List[str]) -> List[str]:
        """Identify naming styles used in component names"""
        styles = []
        for name in names:
            if '_' in name and name.islower():
                styles.append('snake_case')
            elif '-' in name:
                styles.append('kebab-case')
            elif any(c.isupper() for c in name):
                styles.append('camelCase')
            else:
                styles.append('lowercase')
        return styles


class OrchestratedConfigRegenerator:
    """
    Configuration regeneration for ValidationDrivenOrchestrator Level 3 failures.
    
    Regenerates system configuration to resolve integration failures identified
    during Level 3 validation. Focuses on safer regeneration rather than modification.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("OrchestratedConfigRegenerator")
        
        # Configuration regeneration strategies
        self.regeneration_strategies = {
            'port_conflict': {
                'method': 'port_reassignment',
                'confidence': 0.9,
                'safety_level': 'high'
            },
            'resource_conflict': {
                'method': 'resource_optimization',
                'confidence': 0.8,
                'safety_level': 'medium'
            },
            'service_connectivity': {
                'method': 'connectivity_fix',
                'confidence': 0.7,
                'safety_level': 'medium'
            }
        }
        
        self.logger.info("✅ OrchestratedConfigRegenerator initialized")
    
    async def regenerate_system_configuration(self, blueprint: 'SystemBlueprint', integration_failures: List[str]) -> OrchestratedRegenerationResult:
        """
        Regenerate system configuration to address integration failures.
        
        This method analyzes integration failures and regenerates configuration
        to resolve conflicts and connectivity issues.
        
        Args:
            blueprint: SystemBlueprint with integration failures
            integration_failures: List of integration failure messages
            
        Returns:
            OrchestratedRegenerationResult with regeneration outcome
        """
        self.logger.info("🔧 Attempting configuration regeneration for integration failures")
        
        try:
            # Analyze integration failures for regeneration opportunities
            regen_plan = await self._analyze_integration_failures(integration_failures)
            
            if not regen_plan['regenerable']:
                return create_regeneration_failure(
                    f"Integration failures not suitable for configuration regeneration: {regen_plan['reason']}"
                )
            
            # Apply configuration regeneration
            updated_blueprint = await self._apply_configuration_regeneration(blueprint, regen_plan)
            
            # Validate regeneration success
            regen_validation = await self._validate_regeneration_success(blueprint, updated_blueprint)
            
            if regen_validation['successful']:
                self.logger.info("✅ Configuration regeneration successful")
                
                return create_regeneration_success(
                    updated_blueprint=updated_blueprint,
                    details={
                        'regeneration_plan': regen_plan,
                        'changes_applied': regen_validation['changes'],
                        'issues_resolved': len(integration_failures),
                        'safety_assessment': regen_validation['safety_assessment']
                    }
                )
            else:
                return create_regeneration_failure(
                    f"Configuration regeneration validation failed: {regen_validation['error']}"
                )
                
        except Exception as e:
            self.logger.error(f"❌ Configuration regeneration error: {e}")
            return create_regeneration_failure(
                f"Configuration regeneration failed due to error: {e}"
            )
    
    async def _analyze_integration_failures(self, integration_failures: List[str]) -> Dict[str, Any]:
        """Analyze integration failures for regeneration feasibility"""
        regenerable_failures = []
        regeneration_methods = []
        total_safety_score = 0.0
        
        for failure in integration_failures:
            failure_lower = failure.lower()
            
            # Check for port conflicts
            if any(term in failure_lower for term in ['port', 'conflict', 'address']):
                regenerable_failures.append(failure)
                regeneration_methods.append(self.regeneration_strategies['port_conflict'])
                total_safety_score += 0.9  # High safety
            
            # Check for resource conflicts
            elif any(term in failure_lower for term in ['resource', 'memory', 'cpu', 'disk']):
                regenerable_failures.append(failure)
                regeneration_methods.append(self.regeneration_strategies['resource_conflict'])
                total_safety_score += 0.8  # Medium safety
            
            # Check for connectivity issues
            elif any(term in failure_lower for term in ['connect', 'reachable', 'service']):
                regenerable_failures.append(failure)
                regeneration_methods.append(self.regeneration_strategies['service_connectivity'])
                total_safety_score += 0.7  # Medium safety
        
        # Determine regeneration feasibility
        regenerable_ratio = len(regenerable_failures) / len(integration_failures) if integration_failures else 0
        average_safety = total_safety_score / len(regeneration_methods) if regeneration_methods else 0
        
        if regenerable_ratio >= 0.6 and average_safety >= 0.7:
            return {
                'regenerable': True,
                'safety_score': average_safety,
                'regenerable_failures': regenerable_failures,
                'methods': regeneration_methods,
                'regenerable_ratio': regenerable_ratio
            }
        else:
            return {
                'regenerable': False,
                'reason': f"Low regenerability (ratio: {regenerable_ratio:.2f}, safety: {average_safety:.2f})",
                'regenerable_failures': regenerable_failures
            }
    
    async def _apply_configuration_regeneration(self, blueprint: 'SystemBlueprint', regen_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Apply configuration regeneration transformations"""
        updated_blueprint = {
            'description': blueprint.description,
            'components': [comp.copy() for comp in blueprint.components],
            'reasonableness_checks': blueprint.reasonableness_checks.copy(),
            'metadata': blueprint.metadata.copy() if hasattr(blueprint, 'metadata') else {}
        }
        
        changes_applied = []
        
        for method in regen_plan['methods']:
            if method['method'] == 'port_reassignment':
                changes = await self._regenerate_port_configuration(updated_blueprint)
                changes_applied.extend(changes)
            elif method['method'] == 'resource_optimization':
                changes = await self._regenerate_resource_configuration(updated_blueprint)
                changes_applied.extend(changes)
            elif method['method'] == 'connectivity_fix':
                changes = await self._regenerate_connectivity_configuration(updated_blueprint)
                changes_applied.extend(changes)
        
        # Store regeneration metadata
        updated_blueprint['_regeneration_metadata'] = {
            'regeneration_applied': True,
            'changes_applied': changes_applied,
            'original_blueprint': blueprint
        }
        
        return updated_blueprint
    
    async def _regenerate_port_configuration(self, blueprint: Dict[str, Any]) -> List[str]:
        """Regenerate port configuration to resolve conflicts"""
        changes = []
        used_ports = set()
        port_counter = 8000
        
        for component in blueprint['components']:
            configuration = component.get('configuration', {})
            ports = configuration.get('ports', [])
            
            for port_config in ports:
                original_port = port_config.get('port', 0)
                
                # If port is already used, assign new one
                if original_port in used_ports:
                    # Find next available port
                    while port_counter in used_ports:
                        port_counter += 1
                    
                    port_config['port'] = port_counter
                    changes.append(f"Reassigned port for {component.get('name', 'unknown')} from {original_port} to {port_counter}")
                    used_ports.add(port_counter)
                    port_counter += 1
                else:
                    used_ports.add(original_port)
        
        return changes
    
    async def _regenerate_resource_configuration(self, blueprint: Dict[str, Any]) -> List[str]:
        """Regenerate resource configuration to resolve conflicts"""
        changes = []
        
        # Calculate total resource usage
        total_memory = 0
        total_cpu = 0
        total_disk = 0
        
        for component in blueprint['components']:
            configuration = component.get('configuration', {})
            resources = configuration.get('resource_requirements', {})
            
            total_memory += resources.get('memory_mb', 0)
            total_cpu += resources.get('cpu_cores', 0)
            total_disk += resources.get('disk_gb', 0)
        
        # If over-allocated, scale down proportionally
        memory_limit = 16384  # 16GB
        cpu_limit = 8         # 8 cores
        disk_limit = 500      # 500GB
        
        memory_scale = min(1.0, memory_limit / total_memory) if total_memory > 0 else 1.0
        cpu_scale = min(1.0, cpu_limit / total_cpu) if total_cpu > 0 else 1.0
        disk_scale = min(1.0, disk_limit / total_disk) if total_disk > 0 else 1.0
        
        scale_factor = min(memory_scale, cpu_scale, disk_scale)
        
        if scale_factor < 1.0:
            for component in blueprint['components']:
                configuration = component.get('configuration', {})
                resources = configuration.get('resource_requirements', {})
                
                if 'memory_mb' in resources:
                    old_memory = resources['memory_mb']
                    resources['memory_mb'] = max(256, int(old_memory * scale_factor))
                    changes.append(f"Scaled memory for {component.get('name', 'unknown')} from {old_memory}MB to {resources['memory_mb']}MB")
                
                if 'cpu_cores' in resources:
                    old_cpu = resources['cpu_cores']
                    resources['cpu_cores'] = max(0.5, round(old_cpu * scale_factor, 1))
                    changes.append(f"Scaled CPU for {component.get('name', 'unknown')} from {old_cpu} to {resources['cpu_cores']} cores")
                
                if 'disk_gb' in resources:
                    old_disk = resources['disk_gb']
                    resources['disk_gb'] = max(5, int(old_disk * scale_factor))
                    changes.append(f"Scaled disk for {component.get('name', 'unknown')} from {old_disk}GB to {resources['disk_gb']}GB")
        
        return changes
    
    async def _regenerate_connectivity_configuration(self, blueprint: Dict[str, Any]) -> List[str]:
        """Regenerate connectivity configuration to resolve issues"""
        changes = []
        
        # Add default port configurations for components that need them
        for component in blueprint['components']:
            component_type = component.get('type', '')
            configuration = component.get('configuration', {})
            
            if component_type == 'web_service' and 'ports' not in configuration:
                configuration['ports'] = [{'port': 8080, 'protocol': 'http'}]
                changes.append(f"Added default port configuration for web service {component.get('name', 'unknown')}")
            
            elif component_type == 'database' and 'ports' not in configuration:
                configuration['ports'] = [{'port': 5432, 'protocol': 'tcp', 'internal_only': True}]
                changes.append(f"Added default port configuration for database {component.get('name', 'unknown')}")
        
        return changes
    
    async def _validate_regeneration_success(self, original_blueprint: 'SystemBlueprint', updated_blueprint: Dict[str, Any]) -> Dict[str, Any]:
        """Validate configuration regeneration success"""
        
        # Check that no ports conflict in updated configuration
        used_ports = set()
        port_conflicts = []
        
        for component in updated_blueprint['components']:
            configuration = component.get('configuration', {})
            ports = configuration.get('ports', [])
            
            for port_config in ports:
                port_num = port_config.get('port', 0)
                if port_num in used_ports:
                    port_conflicts.append(f"Port {port_num} still conflicts")
                else:
                    used_ports.add(port_num)
        
        # Check resource allocation is reasonable
        total_memory = sum(
            comp.get('configuration', {}).get('resource_requirements', {}).get('memory_mb', 0)
            for comp in updated_blueprint['components']
        )
        
        resource_reasonable = total_memory <= 16384  # 16GB limit
        
        # Safety assessment
        changes_applied = updated_blueprint.get('_regeneration_metadata', {}).get('changes_applied', [])
        safety_assessment = {
            'changes_count': len(changes_applied),
            'port_changes': len([c for c in changes_applied if 'port' in c.lower()]),
            'resource_changes': len([c for c in changes_applied if any(term in c.lower() for term in ['memory', 'cpu', 'disk'])]),
            'safety_level': 'high' if len(changes_applied) <= 5 else 'medium'
        }
        
        success = len(port_conflicts) == 0 and resource_reasonable
        
        return {
            'successful': success,
            'changes': changes_applied,
            'safety_assessment': safety_assessment,
            'error': None if success else f"Regeneration validation failed: port conflicts={port_conflicts}, resource_reasonable={resource_reasonable}"
        }


# Convenience functions for external use
async def heal_component_ast(component: Dict[str, Any], failures: List[str]) -> OrchestratedHealingResult:
    """Heal component AST using OrchestratedASTHealer"""
    healer = OrchestratedASTHealer()
    return await healer.heal_component_logic(component, failures)


async def heal_system_semantics(blueprint: 'SystemBlueprint', failures: List[str]) -> OrchestratedHealingResult:
    """Heal system semantics using OrchestratedSemanticHealer"""
    healer = OrchestratedSemanticHealer()
    return await healer.heal_system_semantics(blueprint, failures)


async def regenerate_configuration(blueprint: 'SystemBlueprint', failures: List[str]) -> OrchestratedRegenerationResult:
    """Regenerate configuration using OrchestratedConfigRegenerator"""
    regenerator = OrchestratedConfigRegenerator()
    return await regenerator.regenerate_system_configuration(blueprint, failures)


# Main execution for testing
if __name__ == "__main__":
    async def main():
        """Test healing orchestration systems"""
        
        print("🔧 Testing Healing Orchestration Systems")
        
        # Test AST healing
        print("\n🎯 Testing AST Healing:")
        ast_healer = OrchestratedASTHealer()
        
        test_component = {
            "name": "test-component",  # Has naming issue
            "type": "web_service",
            "configuration": {
                "resource_requirements": {
                    "memory_mb": "1024",  # String instead of int
                    "cpu_cores": 2
                    # Missing disk_gb
                }
            }
        }
        
        test_failures = [
            "Component configuration validation failed: memory_mb should be integer",
            "Missing required field: disk_gb"
        ]
        
        ast_result = await ast_healer.heal_component_logic(test_component, test_failures)
        print(f"AST Healing result: {'✅ SUCCESS' if ast_result.healing_successful else '❌ FAILED'}")
        if ast_result.healing_successful:
            print(f"  Healed component: {ast_result.healed_component.get('name', 'unknown')}")
        
        # Test semantic healing
        print("\n🧠 Testing Semantic Healing:")
        semantic_healer = OrchestratedSemanticHealer()
        
        class MockBlueprint:
            def __init__(self, description, components):
                self.description = description
                self.components = components
                self.reasonableness_checks = []
                self.metadata = {}
        
        test_blueprint = MockBlueprint(
            description="A system",  # Vague description
            components=[
                {"name": "webService", "type": "web_service"},  # camelCase name
                {"name": "data-store", "type": "database"}      # kebab-case name
            ]
        )
        
        semantic_failures = [
            "Inconsistent naming convention: mix of camelCase and kebab-case",
            "Description too brief and lacks coherence"
        ]
        
        semantic_result = await semantic_healer.heal_system_semantics(test_blueprint, semantic_failures)
        print(f"Semantic Healing result: {'✅ SUCCESS' if semantic_result.healing_successful else '❌ FAILED'}")
        
        # Test configuration regeneration
        print("\n🔧 Testing Configuration Regeneration:")
        config_regenerator = OrchestratedConfigRegenerator()
        
        test_blueprint_config = MockBlueprint(
            description="Web system with port conflicts",
            components=[
                {
                    "name": "web1",
                    "type": "web_service",
                    "configuration": {
                        "ports": [{"port": 8080, "protocol": "http"}]
                    }
                },
                {
                    "name": "web2", 
                    "type": "web_service",
                    "configuration": {
                        "ports": [{"port": 8080, "protocol": "http"}]  # Conflict!
                    }
                }
            ]
        )
        
        integration_failures = [
            "Port 8080 conflict between web1 and web2"
        ]
        
        regen_result = await config_regenerator.regenerate_system_configuration(test_blueprint_config, integration_failures)
        print(f"Configuration Regeneration result: {'✅ SUCCESS' if regen_result.regeneration_successful else '❌ FAILED'}")
        
        print("\n✅ Healing orchestration testing complete")
    
    # Run the test
    asyncio.run(main())