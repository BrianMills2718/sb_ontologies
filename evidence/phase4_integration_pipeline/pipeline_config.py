"""
Pipeline Configuration for Balanced Multi-Purpose Processing
Configures the integration pipeline for optimal balanced processing across all theoretical purposes.
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

class ProcessingMode(Enum):
    """Processing modes for the pipeline"""
    BALANCED = "balanced"
    COMPREHENSIVE = "comprehensive"
    RAPID = "rapid"
    QUALITY_FOCUSED = "quality_focused"

class BalanceStrategy(Enum):
    """Strategies for maintaining balance"""
    EQUAL_WEIGHTS = "equal_weights"
    DYNAMIC_ADJUSTMENT = "dynamic_adjustment"
    THRESHOLD_BASED = "threshold_based"
    ADAPTIVE = "adaptive"

@dataclass
class QualityThresholds:
    """Quality thresholds for pipeline processing"""
    balance_ratio_minimum: float = 0.7
    purpose_confidence_minimum: float = 0.25
    vocabulary_extraction_minimum: int = 5
    schema_complexity_minimum: int = 3
    integration_completeness_minimum: float = 0.8
    sophistication_variance_maximum: float = 1.0

@dataclass
class BalanceWeights:
    """Weight configuration for balanced processing"""
    descriptive: float = 1.0
    explanatory: float = 1.0
    predictive: float = 1.0
    causal: float = 1.0
    intervention: float = 1.0
    
    def normalize(self) -> 'BalanceWeights':
        """Normalize weights to sum to 1.0"""
        total = sum([self.descriptive, self.explanatory, self.predictive, 
                    self.causal, self.intervention])
        if total > 0:
            return BalanceWeights(
                descriptive=self.descriptive / total,
                explanatory=self.explanatory / total,
                predictive=self.predictive / total,
                causal=self.causal / total,
                intervention=self.intervention / total
            )
        return self

@dataclass
class StageConfiguration:
    """Configuration for individual pipeline stages"""
    enabled: bool = True
    timeout_seconds: float = 30.0
    quality_check_enabled: bool = True
    balance_validation_enabled: bool = True
    retry_on_failure: bool = True
    max_retries: int = 2

@dataclass
class IntegrationConfiguration:
    """Configuration for cross-purpose integration"""
    enable_bidirectional_interfaces: bool = True
    enable_unified_workflows: bool = True
    enable_cross_validation: bool = True
    minimum_interface_count: int = 4
    integration_depth: str = "comprehensive"  # minimal, moderate, comprehensive

@dataclass
class OptimizationConfiguration:
    """Configuration for pipeline optimization"""
    enable_caching: bool = True
    enable_parallel_processing: bool = False  # Set to False for deterministic results
    enable_adaptive_thresholds: bool = True
    enable_performance_monitoring: bool = True
    cache_ttl_seconds: int = 3600

class PipelineConfiguration:
    """Complete configuration for the balanced multi-purpose pipeline"""
    
    def __init__(self, mode: ProcessingMode = ProcessingMode.BALANCED):
        """Initialize configuration with specified processing mode"""
        self.mode = mode
        self.balance_strategy = BalanceStrategy.EQUAL_WEIGHTS
        
        # Core configuration components
        self.quality_thresholds = QualityThresholds()
        self.balance_weights = BalanceWeights()
        self.integration_config = IntegrationConfiguration()
        self.optimization_config = OptimizationConfiguration()
        
        # Stage configurations
        self.stages = {
            'theory_count_detection': StageConfiguration(),
            'purpose_classification': StageConfiguration(),
            'vocabulary_extraction': StageConfiguration(),
            'schema_generation': StageConfiguration(),
            'balance_validation': StageConfiguration(),
            'optimization': StageConfiguration()
        }
        
        # Apply mode-specific configurations
        self._apply_mode_configuration(mode)
    
    def _apply_mode_configuration(self, mode: ProcessingMode) -> None:
        """Apply configuration specific to processing mode"""
        if mode == ProcessingMode.BALANCED:
            self.quality_thresholds.balance_ratio_minimum = 0.7
            self.balance_strategy = BalanceStrategy.EQUAL_WEIGHTS
            self.integration_config.integration_depth = "comprehensive"
            
        elif mode == ProcessingMode.COMPREHENSIVE:
            self.quality_thresholds.balance_ratio_minimum = 0.8
            self.quality_thresholds.vocabulary_extraction_minimum = 8
            self.balance_strategy = BalanceStrategy.DYNAMIC_ADJUSTMENT
            self.integration_config.minimum_interface_count = 6
            
        elif mode == ProcessingMode.RAPID:
            self.quality_thresholds.balance_ratio_minimum = 0.6
            self.quality_thresholds.vocabulary_extraction_minimum = 3
            for stage_config in self.stages.values():
                stage_config.timeout_seconds = 15.0
                stage_config.max_retries = 1
            self.optimization_config.enable_caching = True
            
        elif mode == ProcessingMode.QUALITY_FOCUSED:
            self.quality_thresholds.balance_ratio_minimum = 0.85
            self.quality_thresholds.sophistication_variance_maximum = 0.5
            self.balance_strategy = BalanceStrategy.ADAPTIVE
            for stage_config in self.stages.values():
                stage_config.timeout_seconds = 60.0
                stage_config.max_retries = 3
    
    def get_stage_config(self, stage_name: str) -> StageConfiguration:
        """Get configuration for a specific stage"""
        return self.stages.get(stage_name, StageConfiguration())
    
    def update_balance_weights(self, **kwargs) -> None:
        """Update balance weights for specific purposes"""
        for purpose, weight in kwargs.items():
            if hasattr(self.balance_weights, purpose):
                setattr(self.balance_weights, purpose, weight)
        
        # Normalize weights to maintain balance
        self.balance_weights = self.balance_weights.normalize()
    
    def set_quality_threshold(self, threshold_name: str, value: float) -> None:
        """Set a specific quality threshold"""
        if hasattr(self.quality_thresholds, threshold_name):
            setattr(self.quality_thresholds, threshold_name, value)
    
    def enable_stage(self, stage_name: str, enabled: bool = True) -> None:
        """Enable or disable a specific pipeline stage"""
        if stage_name in self.stages:
            self.stages[stage_name].enabled = enabled
    
    def configure_integration(self, **kwargs) -> None:
        """Configure integration settings"""
        for setting, value in kwargs.items():
            if hasattr(self.integration_config, setting):
                setattr(self.integration_config, setting, value)
    
    def configure_optimization(self, **kwargs) -> None:
        """Configure optimization settings"""
        for setting, value in kwargs.items():
            if hasattr(self.optimization_config, setting):
                setattr(self.optimization_config, setting, value)
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate the current configuration"""
        validation_results = {
            'valid': True,
            'warnings': [],
            'errors': [],
            'recommendations': []
        }
        
        # Validate balance weights
        weight_sum = sum([
            self.balance_weights.descriptive,
            self.balance_weights.explanatory,
            self.balance_weights.predictive,
            self.balance_weights.causal,
            self.balance_weights.intervention
        ])
        
        if abs(weight_sum - 1.0) > 0.01:
            validation_results['warnings'].append(
                f"Balance weights sum to {weight_sum:.3f}, should be 1.0"
            )
        
        # Validate quality thresholds
        if self.quality_thresholds.balance_ratio_minimum < 0.5:
            validation_results['warnings'].append(
                "Balance ratio minimum is very low, may allow poor balance"
            )
        
        if self.quality_thresholds.balance_ratio_minimum > 0.9:
            validation_results['recommendations'].append(
                "High balance ratio threshold may be difficult to achieve"
            )
        
        # Validate stage configurations
        for stage_name, stage_config in self.stages.items():
            if stage_config.timeout_seconds < 5.0:
                validation_results['warnings'].append(
                    f"Stage {stage_name} has very short timeout ({stage_config.timeout_seconds}s)"
                )
            
            if stage_config.timeout_seconds > 120.0:
                validation_results['recommendations'].append(
                    f"Stage {stage_name} has long timeout, consider optimization"
                )
        
        # Validate integration configuration
        if not self.integration_config.enable_bidirectional_interfaces:
            validation_results['recommendations'].append(
                "Consider enabling bidirectional interfaces for better integration"
            )
        
        return validation_results
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'mode': self.mode.value,
            'balance_strategy': self.balance_strategy.value,
            'quality_thresholds': asdict(self.quality_thresholds),
            'balance_weights': asdict(self.balance_weights),
            'integration_config': asdict(self.integration_config),
            'optimization_config': asdict(self.optimization_config),
            'stages': {name: asdict(config) for name, config in self.stages.items()}
        }
    
    def save_to_file(self, filename: str) -> None:
        """Save configuration to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load_from_file(cls, filename: str) -> 'PipelineConfiguration':
        """Load configuration from JSON file"""
        with open(filename, 'r') as f:
            config_dict = json.load(f)
        
        # Create instance with mode from file
        mode = ProcessingMode(config_dict.get('mode', 'balanced'))
        instance = cls(mode)
        
        # Update with loaded configuration
        if 'quality_thresholds' in config_dict:
            for key, value in config_dict['quality_thresholds'].items():
                setattr(instance.quality_thresholds, key, value)
        
        if 'balance_weights' in config_dict:
            for key, value in config_dict['balance_weights'].items():
                setattr(instance.balance_weights, key, value)
        
        if 'integration_config' in config_dict:
            for key, value in config_dict['integration_config'].items():
                setattr(instance.integration_config, key, value)
        
        if 'optimization_config' in config_dict:
            for key, value in config_dict['optimization_config'].items():
                setattr(instance.optimization_config, key, value)
        
        return instance
    
    def get_balanced_processing_config(self) -> Dict[str, Any]:
        """Get configuration optimized for balanced processing"""
        return {
            'balance_enforcement': {
                'strategy': self.balance_strategy.value,
                'weights': asdict(self.balance_weights),
                'minimum_ratio': self.quality_thresholds.balance_ratio_minimum,
                'dynamic_adjustment': self.balance_strategy == BalanceStrategy.DYNAMIC_ADJUSTMENT
            },
            'quality_assurance': {
                'thresholds': asdict(self.quality_thresholds),
                'validation_enabled': all(
                    config.balance_validation_enabled for config in self.stages.values()
                ),
                'retry_on_failure': any(
                    config.retry_on_failure for config in self.stages.values()
                )
            },
            'integration_requirements': {
                'cross_purpose_enabled': self.integration_config.enable_bidirectional_interfaces,
                'minimum_interfaces': self.integration_config.minimum_interface_count,
                'depth': self.integration_config.integration_depth
            }
        }
    
    def get_performance_config(self) -> Dict[str, Any]:
        """Get configuration for performance optimization"""
        return {
            'caching': {
                'enabled': self.optimization_config.enable_caching,
                'ttl_seconds': self.optimization_config.cache_ttl_seconds
            },
            'parallel_processing': {
                'enabled': self.optimization_config.enable_parallel_processing
            },
            'monitoring': {
                'enabled': self.optimization_config.enable_performance_monitoring
            },
            'timeouts': {
                stage_name: config.timeout_seconds 
                for stage_name, config in self.stages.items()
            }
        }


# Predefined configurations for common use cases
class PredefinedConfigurations:
    """Factory class for predefined pipeline configurations"""
    
    @staticmethod
    def create_research_configuration() -> PipelineConfiguration:
        """Configuration optimized for research use"""
        config = PipelineConfiguration(ProcessingMode.COMPREHENSIVE)
        config.quality_thresholds.balance_ratio_minimum = 0.8
        config.quality_thresholds.sophistication_variance_maximum = 0.5
        return config
    
    @staticmethod
    def create_production_configuration() -> PipelineConfiguration:
        """Configuration optimized for production use"""
        config = PipelineConfiguration(ProcessingMode.BALANCED)
        config.optimization_config.enable_caching = True
        config.optimization_config.enable_performance_monitoring = True
        return config
    
    @staticmethod
    def create_development_configuration() -> PipelineConfiguration:
        """Configuration optimized for development/testing"""
        config = PipelineConfiguration(ProcessingMode.RAPID)
        config.quality_thresholds.balance_ratio_minimum = 0.6
        for stage_config in config.stages.values():
            stage_config.timeout_seconds = 10.0
        return config
    
    @staticmethod
    def create_high_quality_configuration() -> PipelineConfiguration:
        """Configuration optimized for highest quality results"""
        config = PipelineConfiguration(ProcessingMode.QUALITY_FOCUSED)
        config.quality_thresholds.balance_ratio_minimum = 0.9
        config.quality_thresholds.integration_completeness_minimum = 0.95
        config.balance_strategy = BalanceStrategy.ADAPTIVE
        return config
    
    @staticmethod
    def create_balanced_configuration() -> PipelineConfiguration:
        """Configuration specifically optimized for balance"""
        config = PipelineConfiguration(ProcessingMode.BALANCED)
        
        # Strict balance requirements
        config.quality_thresholds.balance_ratio_minimum = 0.75
        config.quality_thresholds.sophistication_variance_maximum = 0.8
        
        # Equal weights enforcement
        config.balance_strategy = BalanceStrategy.EQUAL_WEIGHTS
        config.balance_weights = BalanceWeights()  # All 1.0 by default
        
        # Comprehensive integration
        config.integration_config.enable_bidirectional_interfaces = True
        config.integration_config.enable_unified_workflows = True
        config.integration_config.minimum_interface_count = 4
        
        return config


def main():
    """Demonstration of pipeline configuration"""
    
    print("=== PIPELINE CONFIGURATION DEMONSTRATION ===\n")
    
    # Create different configurations
    configs = {
        'Balanced': PredefinedConfigurations.create_balanced_configuration(),
        'Research': PredefinedConfigurations.create_research_configuration(),
        'Production': PredefinedConfigurations.create_production_configuration(),
        'High Quality': PredefinedConfigurations.create_high_quality_configuration()
    }
    
    # Display configurations
    for name, config in configs.items():
        print(f"{name.upper()} CONFIGURATION:")
        print(f"  Mode: {config.mode.value}")
        print(f"  Balance strategy: {config.balance_strategy.value}")
        print(f"  Balance ratio minimum: {config.quality_thresholds.balance_ratio_minimum}")
        print(f"  Integration depth: {config.integration_config.integration_depth}")
        
        # Validate configuration
        validation = config.validate_configuration()
        print(f"  Valid: {validation['valid']}")
        if validation['warnings']:
            print(f"  Warnings: {len(validation['warnings'])}")
        if validation['recommendations']:
            print(f"  Recommendations: {len(validation['recommendations'])}")
        print()
    
    # Demonstrate configuration customization
    print("CONFIGURATION CUSTOMIZATION:")
    custom_config = PipelineConfiguration(ProcessingMode.BALANCED)
    
    # Update balance weights for specific emphasis (while maintaining balance)
    custom_config.update_balance_weights(causal=1.2, intervention=1.2)
    print(f"  Updated weights: {asdict(custom_config.balance_weights)}")
    
    # Set custom quality threshold
    custom_config.set_quality_threshold('balance_ratio_minimum', 0.8)
    print(f"  Updated balance threshold: {custom_config.quality_thresholds.balance_ratio_minimum}")
    
    # Configure integration
    custom_config.configure_integration(minimum_interface_count=6)
    print(f"  Updated minimum interfaces: {custom_config.integration_config.minimum_interface_count}")
    
    print()
    
    # Show balanced processing configuration
    print("BALANCED PROCESSING CONFIGURATION:")
    balanced_config = custom_config.get_balanced_processing_config()
    for section, settings in balanced_config.items():
        print(f"  {section}:")
        for key, value in settings.items():
            print(f"    {key}: {value}")
        print()


if __name__ == "__main__":
    main()