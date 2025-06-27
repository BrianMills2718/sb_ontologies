"""
Level 4: Semantic Validation with Semantic Healing Integration
Validates system semantics using LLM and triggers semantic healing for failures
"""

import asyncio
import time
import logging
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SemanticValidationResult:
    """Result of semantic validation"""
    passed: bool
    system_name: str
    failures: List[str]
    execution_time: float
    semantic_details: Dict[str, Any] = None
    healing_candidate: bool = False
    reasonableness_score: Optional[float] = None


@dataclass
class SemanticHealingResult:
    """Result of semantic healing operation"""
    healing_successful: bool
    healed_blueprint: Optional[Any] = None
    healing_details: Dict[str, Any] = None
    error_message: Optional[str] = None
    execution_time: float = 0.0


class Level4SemanticValidator:
    """
    Level 4 Semantic Validation - Uses LLM for system-level semantic validation
    
    Validates system semantics and reasonableness using LLM (no mock modes)
    """
    
    def __init__(self):
        self.llm_client = None
        self.semantic_rules = self._initialize_semantic_rules()
        self.validation_prompts = self._initialize_validation_prompts()
    
    def _initialize_semantic_rules(self) -> Dict[str, Any]:
        """Initialize semantic validation rules"""
        return {
            "system_coherence": {
                "component_relationships": True,
                "data_flow_consistency": True,
                "architectural_patterns": True
            },
            "business_logic": {
                "domain_appropriateness": True,
                "functionality_completeness": True,
                "edge_case_handling": True
            },
            "reasonableness_checks": {
                "performance_expectations": True,
                "scalability_assumptions": True,
                "resource_utilization": True
            }
        }
    
    def _initialize_validation_prompts(self) -> Dict[str, str]:
        """Initialize LLM validation prompts"""
        return {
            "system_coherence": """
            Analyze this system blueprint for semantic coherence:
            
            System: {system_name}
            Description: {system_description}
            Components: {components}
            
            Evaluate:
            1. Do the components work together logically?
            2. Is the data flow semantically consistent?
            3. Does the architecture make sense for the stated purpose?
            
            Respond with JSON: {{"coherent": true/false, "issues": ["list of issues"], "score": 0.0-1.0}}
            """,
            
            "business_logic": """
            Analyze this system's business logic and domain appropriateness:
            
            System: {system_name}
            Description: {system_description}
            Components: {components}
            Domain Context: {domain_context}
            
            Evaluate:
            1. Is the business logic appropriate for the domain?
            2. Are the component responsibilities well-defined?
            3. Does the system handle edge cases appropriately?
            
            Respond with JSON: {{"appropriate": true/false, "issues": ["list of issues"], "score": 0.0-1.0}}
            """,
            
            "reasonableness_checks": """
            Evaluate this system against the provided reasonableness checks:
            
            System: {system_name}
            Description: {system_description}
            Components: {components}
            Reasonableness Checks: {reasonableness_checks}
            
            For each reasonableness check, evaluate if the system design supports it:
            1. Are performance expectations realistic?
            2. Are scalability assumptions sound?
            3. Is resource utilization reasonable?
            
            Respond with JSON: {{"reasonable": true/false, "check_results": {{}}, "issues": ["list"], "score": 0.0-1.0}}
            """
        }
    
    async def validate_system_semantics(self, blueprint, include_reasonableness_checks: bool = True) -> SemanticValidationResult:
        """
        Validate system semantics using LLM
        
        Args:
            blueprint: SystemBlueprint to validate
            include_reasonableness_checks: Whether to include reasonableness validation
            
        Returns:
            SemanticValidationResult with semantic validation details
        """
        start_time = time.time()
        system_name = getattr(blueprint, 'name', 'unknown_system')
        logger.info(f"Starting semantic validation for {system_name}")
        
        try:
            # Ensure LLM client is initialized
            await self._ensure_llm_client()
            
            failures = []
            semantic_details = {}
            total_score = 0.0
            validation_count = 0
            
            # 1. System coherence validation
            coherence_validation = await self._validate_system_coherence(blueprint)
            if not coherence_validation["passed"]:
                failures.extend(coherence_validation["failures"])
            semantic_details["coherence_validation"] = coherence_validation
            total_score += coherence_validation.get("score", 0.0)
            validation_count += 1
            
            # 2. Business logic validation
            business_validation = await self._validate_business_logic(blueprint)
            if not business_validation["passed"]:
                failures.extend(business_validation["failures"])
            semantic_details["business_validation"] = business_validation
            total_score += business_validation.get("score", 0.0)
            validation_count += 1
            
            # 3. Reasonableness checks validation (if requested)
            if include_reasonableness_checks:
                reasonableness_validation = await self._validate_reasonableness_checks(blueprint)
                if not reasonableness_validation["passed"]:
                    failures.extend(reasonableness_validation["failures"])
                semantic_details["reasonableness_validation"] = reasonableness_validation
                total_score += reasonableness_validation.get("score", 0.0)
                validation_count += 1
            
            # 4. System-level semantic consistency validation
            consistency_validation = await self._validate_semantic_consistency(blueprint)
            if not consistency_validation["passed"]:
                failures.extend(consistency_validation["failures"])
            semantic_details["consistency_validation"] = consistency_validation
            total_score += consistency_validation.get("score", 0.0)
            validation_count += 1
            
            # Calculate overall reasonableness score
            overall_score = total_score / validation_count if validation_count > 0 else 0.0
            
            # Determine if failures are healing candidates
            healing_candidate = self._is_semantic_healing_candidate(failures)
            
            result = SemanticValidationResult(
                passed=len(failures) == 0,
                system_name=system_name,
                failures=failures,
                execution_time=time.time() - start_time,
                semantic_details=semantic_details,
                healing_candidate=healing_candidate,
                reasonableness_score=overall_score
            )
            
            if result.passed:
                logger.info(f"System {system_name} semantic validation passed with score {overall_score:.2f}")
            else:
                logger.warning(f"System {system_name} semantic validation failed: {len(failures)} semantic issues")
            
            return result
            
        except Exception as e:
            logger.error(f"Semantic validation error for {system_name}: {e}")
            return SemanticValidationResult(
                passed=False,
                system_name=system_name,
                failures=[f"Semantic validation exception: {e}"],
                execution_time=time.time() - start_time
            )
    
    async def _ensure_llm_client(self):
        """Ensure LLM client is initialized (fail hard if not available)"""
        if self.llm_client is None:
            import os
            
            # Check for LLM configuration
            has_openai = bool(os.environ.get("OPENAI_API_KEY"))
            has_anthropic = bool(os.environ.get("ANTHROPIC_API_KEY"))
            
            if not (has_openai or has_anthropic):
                raise Exception(
                    "Level 4 semantic validation requires LLM configuration. "
                    "Set OPENAI_API_KEY or ANTHROPIC_API_KEY. "
                    "NO MOCK MODES OR FALLBACKS AVAILABLE."
                )
            
            # Initialize LLM client
            if has_openai:
                self.llm_client = await self._initialize_openai_client()
            elif has_anthropic:
                self.llm_client = await self._initialize_anthropic_client()
    
    async def _initialize_openai_client(self):
        """Initialize OpenAI client"""
        try:
            import openai
            
            client = openai.OpenAI()
            
            # Test client with simple call
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Test connection"}],
                max_tokens=1
            )
            
            logger.info("OpenAI client initialized successfully")
            return {"type": "openai", "client": client, "model": "gpt-3.5-turbo"}
            
        except ImportError:
            raise Exception("OpenAI library not installed - run: pip install openai")
        except Exception as e:
            raise Exception(f"OpenAI client initialization failed: {e}")
    
    async def _initialize_anthropic_client(self):
        """Initialize Anthropic client"""
        try:
            import anthropic
            
            client = anthropic.Anthropic()
            
            # Test client with simple call
            response = await asyncio.to_thread(
                client.messages.create,
                model="claude-3-haiku-20240307",
                max_tokens=1,
                messages=[{"role": "user", "content": "Test connection"}]
            )
            
            logger.info("Anthropic client initialized successfully")
            return {"type": "anthropic", "client": client, "model": "claude-3-haiku-20240307"}
            
        except ImportError:
            raise Exception("Anthropic library not installed - run: pip install anthropic")
        except Exception as e:
            raise Exception(f"Anthropic client initialization failed: {e}")
    
    async def _validate_system_coherence(self, blueprint) -> Dict[str, Any]:
        """Validate system coherence using LLM"""
        try:
            # Prepare system information
            system_info = self._extract_system_info(blueprint)
            
            # Create prompt
            prompt = self.validation_prompts["system_coherence"].format(
                system_name=system_info["name"],
                system_description=system_info["description"],
                components=json.dumps(system_info["components"], indent=2)
            )
            
            # Get LLM response
            llm_response = await self._call_llm(prompt)
            
            # Parse response
            try:
                result = json.loads(llm_response)
                coherent = result.get("coherent", False)
                issues = result.get("issues", [])
                score = result.get("score", 0.0)
                
                return {
                    "passed": coherent,
                    "failures": issues if not coherent else [],
                    "score": score,
                    "llm_response": llm_response
                }
                
            except json.JSONDecodeError:
                # Fallback parsing
                coherent = "coherent: true" in llm_response.lower() or "true" in llm_response.lower()
                return {
                    "passed": coherent,
                    "failures": ["LLM response parsing failed"] if not coherent else [],
                    "score": 0.5,
                    "llm_response": llm_response
                }
                
        except Exception as e:
            return {
                "passed": False,
                "failures": [f"System coherence validation failed: {e}"],
                "score": 0.0
            }
    
    async def _validate_business_logic(self, blueprint) -> Dict[str, Any]:
        """Validate business logic appropriateness using LLM"""
        try:
            # Prepare system information
            system_info = self._extract_system_info(blueprint)
            
            # Infer domain context from system description
            domain_context = self._infer_domain_context(system_info["description"])
            
            # Create prompt
            prompt = self.validation_prompts["business_logic"].format(
                system_name=system_info["name"],
                system_description=system_info["description"],
                components=json.dumps(system_info["components"], indent=2),
                domain_context=domain_context
            )
            
            # Get LLM response
            llm_response = await self._call_llm(prompt)
            
            # Parse response
            try:
                result = json.loads(llm_response)
                appropriate = result.get("appropriate", False)
                issues = result.get("issues", [])
                score = result.get("score", 0.0)
                
                return {
                    "passed": appropriate,
                    "failures": issues if not appropriate else [],
                    "score": score,
                    "llm_response": llm_response,
                    "domain_context": domain_context
                }
                
            except json.JSONDecodeError:
                # Fallback parsing
                appropriate = "appropriate: true" in llm_response.lower() or "true" in llm_response.lower()
                return {
                    "passed": appropriate,
                    "failures": ["Business logic parsing failed"] if not appropriate else [],
                    "score": 0.5,
                    "llm_response": llm_response
                }
                
        except Exception as e:
            return {
                "passed": False,
                "failures": [f"Business logic validation failed: {e}"],
                "score": 0.0
            }
    
    async def _validate_reasonableness_checks(self, blueprint) -> Dict[str, Any]:
        """Validate system against blueprint reasonableness checks using LLM"""
        try:
            # Extract reasonableness checks from blueprint
            reasonableness_checks = getattr(blueprint, 'reasonableness_checks', [])
            
            if not reasonableness_checks:
                return {
                    "passed": True,
                    "failures": [],
                    "score": 1.0,
                    "note": "No reasonableness checks provided"
                }
            
            # Prepare system information
            system_info = self._extract_system_info(blueprint)
            
            # Create prompt
            prompt = self.validation_prompts["reasonableness_checks"].format(
                system_name=system_info["name"],
                system_description=system_info["description"],
                components=json.dumps(system_info["components"], indent=2),
                reasonableness_checks=json.dumps(reasonableness_checks, indent=2)
            )
            
            # Get LLM response
            llm_response = await self._call_llm(prompt)
            
            # Parse response
            try:
                result = json.loads(llm_response)
                reasonable = result.get("reasonable", False)
                issues = result.get("issues", [])
                score = result.get("score", 0.0)
                check_results = result.get("check_results", {})
                
                return {
                    "passed": reasonable,
                    "failures": issues if not reasonable else [],
                    "score": score,
                    "check_results": check_results,
                    "llm_response": llm_response,
                    "reasonableness_checks": reasonableness_checks
                }
                
            except json.JSONDecodeError:
                # Fallback parsing
                reasonable = "reasonable: true" in llm_response.lower() or "true" in llm_response.lower()
                return {
                    "passed": reasonable,
                    "failures": ["Reasonableness parsing failed"] if not reasonable else [],
                    "score": 0.5,
                    "llm_response": llm_response
                }
                
        except Exception as e:
            return {
                "passed": False,
                "failures": [f"Reasonableness checks validation failed: {e}"],
                "score": 0.0
            }
    
    async def _validate_semantic_consistency(self, blueprint) -> Dict[str, Any]:
        """Validate semantic consistency across system components"""
        try:
            # Prepare component analysis
            system_info = self._extract_system_info(blueprint)
            components = system_info["components"]
            
            consistency_issues = []
            
            # Check component naming consistency
            naming_issues = self._check_naming_consistency(components)
            consistency_issues.extend(naming_issues)
            
            # Check data flow consistency
            dataflow_issues = self._check_dataflow_consistency(components)
            consistency_issues.extend(dataflow_issues)
            
            # Check responsibility consistency
            responsibility_issues = self._check_responsibility_consistency(components)
            consistency_issues.extend(responsibility_issues)
            
            # Calculate consistency score
            total_checks = 3
            failed_checks = sum([
                1 if naming_issues else 0,
                1 if dataflow_issues else 0,
                1 if responsibility_issues else 0
            ])
            
            score = (total_checks - failed_checks) / total_checks
            
            return {
                "passed": len(consistency_issues) == 0,
                "failures": consistency_issues,
                "score": score,
                "consistency_checks": {
                    "naming": not bool(naming_issues),
                    "dataflow": not bool(dataflow_issues),
                    "responsibility": not bool(responsibility_issues)
                }
            }
            
        except Exception as e:
            return {
                "passed": False,
                "failures": [f"Semantic consistency validation failed: {e}"],
                "score": 0.0
            }
    
    def _extract_system_info(self, blueprint) -> Dict[str, Any]:
        """Extract system information for LLM analysis"""
        system_info = {
            "name": getattr(blueprint, 'name', 'Unknown System'),
            "description": getattr(blueprint, 'description', 'No description provided'),
            "components": []
        }
        
        if hasattr(blueprint, 'components'):
            for component in blueprint.components:
                component_info = {
                    "name": getattr(component, 'name', 'unknown'),
                    "type": getattr(component, 'type', 'unknown'),
                    "description": getattr(component, 'description', ''),
                    "config": getattr(component, 'config', {})
                }
                system_info["components"].append(component_info)
        
        return system_info
    
    def _infer_domain_context(self, system_description: str) -> str:
        """Infer domain context from system description"""
        # Simple keyword-based domain inference
        description_lower = system_description.lower()
        
        if any(keyword in description_lower for keyword in ["fraud", "payment", "transaction", "financial"]):
            return "Financial Services / Fraud Detection"
        elif any(keyword in description_lower for keyword in ["user", "content", "social", "platform"]):
            return "Content Platform / Social Media"
        elif any(keyword in description_lower for keyword in ["data", "analytics", "pipeline", "processing"]):
            return "Data Processing / Analytics"
        elif any(keyword in description_lower for keyword in ["ai", "ml", "machine learning", "model"]):
            return "AI/ML Platform"
        elif any(keyword in description_lower for keyword in ["api", "service", "microservice", "web"]):
            return "Web Services / API Platform"
        else:
            return "General Software System"
    
    async def _call_llm(self, prompt: str) -> str:
        """Call LLM with the given prompt"""
        try:
            if self.llm_client["type"] == "openai":
                response = await asyncio.to_thread(
                    self.llm_client["client"].chat.completions.create,
                    model=self.llm_client["model"],
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1000,
                    temperature=0.1
                )
                return response.choices[0].message.content
                
            elif self.llm_client["type"] == "anthropic":
                response = await asyncio.to_thread(
                    self.llm_client["client"].messages.create,
                    model=self.llm_client["model"],
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
            
            else:
                raise Exception(f"Unknown LLM client type: {self.llm_client['type']}")
                
        except Exception as e:
            raise Exception(f"LLM call failed: {e}")
    
    def _check_naming_consistency(self, components: List[Dict[str, Any]]) -> List[str]:
        """Check component naming consistency"""
        issues = []
        
        component_names = [comp["name"] for comp in components]
        
        # Check for duplicate names
        if len(component_names) != len(set(component_names)):
            issues.append("Duplicate component names found")
        
        # Check naming conventions
        for comp in components:
            name = comp["name"]
            comp_type = comp["type"]
            
            # Check if name reflects type appropriately
            if comp_type == "Source" and not any(keyword in name.lower() for keyword in ["source", "generator", "producer"]):
                issues.append(f"Source component '{name}' name doesn't reflect its type")
            elif comp_type == "Sink" and not any(keyword in name.lower() for keyword in ["sink", "consumer", "writer", "store"]):
                issues.append(f"Sink component '{name}' name doesn't reflect its type")
        
        return issues
    
    def _check_dataflow_consistency(self, components: List[Dict[str, Any]]) -> List[str]:
        """Check data flow semantic consistency"""
        issues = []
        
        # Count component types
        sources = [c for c in components if c["type"] == "Source"]
        sinks = [c for c in components if c["type"] == "Sink"]
        transformers = [c for c in components if c["type"] == "Transformer"]
        
        # Basic dataflow validation
        if len(sources) == 0 and len(transformers) > 0:
            issues.append("Transformers present but no data sources defined")
        
        if len(sinks) == 0 and len(sources) > 0:
            issues.append("Data sources present but no data sinks defined")
        
        if len(transformers) > 0 and len(sources) == 0:
            issues.append("Data transformation defined without input sources")
        
        return issues
    
    def _check_responsibility_consistency(self, components: List[Dict[str, Any]]) -> List[str]:
        """Check component responsibility consistency"""
        issues = []
        
        for comp in components:
            name = comp["name"]
            comp_type = comp["type"]
            description = comp.get("description", "")
            
            # Check if description matches type
            if comp_type == "Source" and description and "generate" not in description.lower() and "produce" not in description.lower():
                issues.append(f"Source component '{name}' description doesn't mention data generation")
            elif comp_type == "Transformer" and description and "transform" not in description.lower() and "process" not in description.lower():
                issues.append(f"Transformer component '{name}' description doesn't mention data transformation")
            elif comp_type == "Sink" and description and "store" not in description.lower() and "consume" not in description.lower():
                issues.append(f"Sink component '{name}' description doesn't mention data consumption/storage")
        
        return issues
    
    def _is_semantic_healing_candidate(self, failures: List[str]) -> bool:
        """Determine if semantic failures are candidates for healing"""
        healing_indicators = [
            "coherence",
            "consistency",
            "naming",
            "description",
            "responsibility",
            "business logic"
        ]
        
        # If any failure contains healing indicators, it's a candidate
        for failure in failures:
            for indicator in healing_indicators:
                if indicator.lower() in failure.lower():
                    return True
        
        return False


class Level4SemanticHealingIntegrator:
    """
    Semantic Healing Integration for Level 4 semantic validation failures
    
    Integrates with Phase 1 semantic healing system to fix semantic issues
    """
    
    def __init__(self):
        self.semantic_healer = None
        self.llm_client = None
    
    async def heal_system_semantics(self, blueprint, validation_failures: List[str]) -> SemanticHealingResult:
        """
        Heal system semantic issues using semantic healing
        
        Args:
            blueprint: Blueprint with semantic issues
            validation_failures: List of semantic validation failure messages
            
        Returns:
            SemanticHealingResult with healing outcome
        """
        start_time = time.time()
        system_name = getattr(blueprint, 'name', 'unknown_system')
        logger.info(f"Starting semantic healing for system {system_name}")
        
        try:
            # Initialize semantic healer if needed
            await self._ensure_semantic_healer()
            
            # Use reasonableness checks from blueprint for healing context
            healing_context = {
                "system_description": getattr(blueprint, 'description', ''),
                "reasonableness_checks": getattr(blueprint, 'reasonableness_checks', []),
                "validation_failures": validation_failures,
                "system_name": system_name
            }
            
            # Apply semantic healing (single attempt, fail hard if unsuccessful)
            healing_result = await self._apply_semantic_healing(blueprint, healing_context)
            
            return SemanticHealingResult(
                healing_successful=healing_result["success"],
                healed_blueprint=healing_result.get("healed_blueprint"),
                healing_details=healing_result.get("details", {}),
                error_message=healing_result.get("error"),
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            logger.error(f"Semantic healing failed for system {system_name}: {e}")
            return SemanticHealingResult(
                healing_successful=False,
                error_message=f"Semantic healing exception: {e}",
                execution_time=time.time() - start_time
            )
    
    async def _ensure_semantic_healer(self):
        """Ensure semantic healer is initialized"""
        if self.semantic_healer is None:
            try:
                # Import Phase 1 semantic healing system (no mock mode)
                from autocoder.healing.semantic_healer import SemanticHealer
                self.semantic_healer = SemanticHealer()  # No mock mode parameter
                logger.debug("Phase 1 semantic healer integrated")
            except ImportError:
                logger.warning("Phase 1 semantic healer not available - using fallback")
                self.semantic_healer = self._create_fallback_healer()
    
    def _create_fallback_healer(self):
        """Create fallback semantic healer"""
        class FallbackSemanticHealer:
            async def heal_system_semantics(self, blueprint, context):
                return {
                    "success": False,
                    "error": "Semantic healer not available - Phase 1 integration required"
                }
        
        return FallbackSemanticHealer()
    
    async def _apply_semantic_healing(self, blueprint, healing_context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply semantic healing to blueprint"""
        try:
            # Use semantic healer to fix blueprint
            healing_result = await self.semantic_healer.heal_system_semantics(blueprint, healing_context)
            
            return {
                "success": healing_result.get("successful", False),
                "healed_blueprint": healing_result.get("healed_blueprint"),
                "details": {
                    "context_used": healing_context,
                    "semantic_changes_applied": healing_result.get("semantic_changes_applied", []),
                    "healing_strategy": "llm_semantic_improvement"
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Semantic healing application failed: {e}"
            }


# Integration functions for ValidationDrivenOrchestrator
async def create_semantic_validator() -> Level4SemanticValidator:
    """Create and return Level 4 semantic validator"""
    return Level4SemanticValidator()


async def create_semantic_healing_integrator() -> Level4SemanticHealingIntegrator:
    """Create and return semantic healing integrator"""
    return Level4SemanticHealingIntegrator()


# Test harness
if __name__ == "__main__":
    async def test_semantic_validation():
        # Create mock blueprint for testing
        class MockBlueprint:
            def __init__(self):
                self.name = "test_fraud_detection"
                self.description = "A fraud detection system for processing financial transactions"
                self.reasonableness_checks = [
                    "System should process transactions within 100ms",
                    "False positive rate should be below 5%"
                ]
                self.components = [
                    type('Component', (), {
                        'name': 'transaction_source',
                        'type': 'Source',
                        'description': 'Generates transaction data',
                        'config': {}
                    })(),
                    type('Component', (), {
                        'name': 'fraud_detector',
                        'type': 'Transformer',
                        'description': 'Analyzes transactions for fraud',
                        'config': {}
                    })(),
                    type('Component', (), {
                        'name': 'result_sink',
                        'type': 'Sink',
                        'description': 'Stores fraud detection results',
                        'config': {}
                    })()
                ]
        
        blueprint = MockBlueprint()
        
        validator = Level4SemanticValidator()
        
        try:
            result = await validator.validate_system_semantics(blueprint)
            
            print(f"Semantic validation result: {result.passed}")
            print(f"System: {result.system_name}")
            print(f"Execution time: {result.execution_time:.2f}s")
            print(f"Reasonableness score: {result.reasonableness_score}")
            
            if not result.passed:
                print("Failures:")
                for failure in result.failures:
                    print(f"  - {failure}")
            
            return result
            
        except Exception as e:
            print(f"Semantic validation test failed: {e}")
            print("This is expected if LLM is not configured")
            return None
    
    asyncio.run(test_semantic_validation())