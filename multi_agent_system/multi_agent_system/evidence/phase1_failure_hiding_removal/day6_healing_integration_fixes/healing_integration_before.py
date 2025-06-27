# EXCERPT from healing_integration.py showing PROPER healing patterns

class HealingIntegratedGenerator:
    def __init__(self, 
                 output_dir: Path,
                 max_healing_attempts: int = 3,  # BOUNDED ATTEMPTS
                 strict_validation: bool = True,
                 enable_metrics: bool = True):
        # ... initialization
        
    async def _component_healing_loop(self, 
                                    parsed_blueprint: ParsedSystemBlueprint,
                                    system_output_dir: Path,
                                    result: HealingPipelineResult) -> Tuple[bool, Optional[ValidationGateResult]]:
        """
        Execute the component generation + validation + healing loop.
        
        This loop continues until either:
        1. All components pass validation (success)
        2. Max healing attempts reached (failure)  # HARD FAILURE
        3. No healing fixes can be applied (failure)
        """
        
        for attempt in range(self.max_healing_attempts + 1):  # +1 for initial attempt
            self.logger.info(f"\n🔄 Component validation attempt {attempt + 1}")  # VISIBLE LOGGING
            
            # ... validation logic ...
            
            # If this was the last attempt, don't try healing
            if attempt >= self.max_healing_attempts:
                self.logger.error("   ❌ Max healing attempts reached")  # HARD FAILURE
                return False, validation_result
            
            # ... healing logic with circuit breaker detection ...
            
            circuit_breaker_activated = any(
                "Circuit breaker activated" in (r.error_message or "") 
                for r in healing_results
            )
            
            if circuit_breaker_activated:
                self.logger.warning("   ⚡ Circuit breaker activated for one or more components")  # VISIBLE
            
            if not healing_success:
                self.logger.error("   ❌ Healing failed - cannot fix component issues")  # HARD FAILURE
                return False, validation_result
        
        # Final hard failure after all attempts
        self.logger.error(f"   ❌ Exhausted all {self.max_healing_attempts} healing attempts without success")
        return False, None