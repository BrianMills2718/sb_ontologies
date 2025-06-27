# Phase: Semantic Extractor Implementation

**Implementation Agent Instructions - Completely Isolated**

You are implementing the Semantic Extractor for hybrid blueprint generation. This extracts user intent using LLMs without generating code directly.

## 🎯 **GOAL**
Implement a semantic extractor that:
1. Takes natural language input
2. Uses LLM to extract SEMANTIC INTENT only (not code/YAML)
3. Returns structured JSON with system requirements
4. Replaces current LLM-generated-YAML approach

## 📋 **IMPLEMENTATION REQUIREMENTS**

### **1. Create Semantic Extractor Component**
Location: `/home/brian/autocoder3_cc/blueprint_language/semantic_extractor.py`

```python
class SemanticExtractor:
    """Extract semantic intent from natural language requests"""
    
    def __init__(self):
        # Initialize LLM client (OpenAI/Anthropic)
        # Load from environment variables (.env file available)
        import os
        from openai import OpenAI
        from dotenv import load_dotenv
        
        load_dotenv()  # Load .env file
        
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = os.getenv('OPENAI_MODEL', 'o3')  # Default to o3
        
        if not os.getenv('OPENAI_API_KEY'):
            raise ValueError("OPENAI_API_KEY not found in environment")
    
    def extract_intent(self, natural_language: str) -> Dict:
        """
        Extract what the user wants (not how to build it)
        
        Uses carefully engineered prompts for reliable intent extraction.
        
        Returns:
        {
            "system_name": "snake_case_name",
            "description": "One sentence purpose",
            "needs_api": True/False,
            "api_operations": ["create", "read", "update", "delete"],
            "needs_database": True/False,
            "needs_ui": True/False,
            "data_types": ["orders", "customers"],
            "integrations": ["external_api_name"],
            "complexity": "simple|medium|complex"
        }
        """
        
        # Use structured prompt with examples and constraints
        system_prompt = """You are a system requirements analyst. Extract ONLY the semantic intent from user requests.

CRITICAL RULES:
1. Never generate code, YAML, or implementation details
2. Extract only what the user explicitly requested
3. Be conservative - don't add features they didn't mention
4. Return valid JSON matching the exact schema provided
5. If unclear, mark as "unknown" rather than guessing

SCHEMA (you must return exactly this structure):
{
  "system_name": "snake_case_identifier",
  "description": "one sentence summary", 
  "needs_api": boolean,
  "api_operations": ["operation1", "operation2"],
  "needs_database": boolean,
  "needs_ui": boolean,
  "data_types": ["type1", "type2"],
  "integrations": ["service1", "service2"],
  "complexity": "simple|medium|complex"
}

EXAMPLES:
Request: "Create a todo API"
Response: {"system_name": "todo_api", "description": "API for managing todo items", "needs_api": true, "api_operations": ["create", "read", "update", "delete"], "needs_database": false, "needs_ui": false, "data_types": ["todos"], "integrations": [], "complexity": "simple"}

Request: "Build a real-time analytics dashboard with database"
Response: {"system_name": "analytics_dashboard", "description": "Real-time analytics dashboard", "needs_api": true, "api_operations": ["read"], "needs_database": true, "needs_ui": true, "data_types": ["analytics"], "integrations": [], "complexity": "complex"}"""

        user_prompt = f"Extract intent from: {natural_language}"
        
        # Call OpenAI with structured output
        response = self.client.chat.completions.create(
            model=self.model,  # Use configured model (o3)
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1  # Low temperature for consistency
        )
        
        return json.loads(response.choices[0].message.content)
```

**Critical Requirements**:
- Use structured LLM prompts that extract intent, never generate code
- Return consistent JSON schema
- Handle edge cases (ambiguous requests, missing info)
- Add validation for extracted intent

**Advanced Prompt Engineering Techniques to Implement**:

1. **Chain-of-Thought for Complex Requests**:
```python
def extract_complex_intent(self, natural_language: str) -> Dict:
    """For complex requests, use chain-of-thought reasoning"""
    
    reasoning_prompt = f"""
    Analyze this request step by step:
    "{natural_language}"
    
    Step 1: What is the main system purpose?
    Step 2: What data needs to be stored?
    Step 3: What operations need to be performed?
    Step 4: What interfaces are needed?
    Step 5: What external systems are mentioned?
    
    Based on this analysis, extract the intent as JSON.
    """
```

2. **Few-Shot Learning with Domain-Specific Examples**:
   - Include examples for common domains (e-commerce, analytics, social media)
   - Show how to handle ambiguous terms consistently
   - Demonstrate conservative interpretation patterns

3. **Validation Prompts for Quality Control**:
```python
def validate_extracted_intent(self, intent: Dict, original_request: str) -> bool:
    """Use LLM to validate extracted intent makes sense"""
    
    validation_prompt = f"""
    Original request: "{original_request}"
    Extracted intent: {json.dumps(intent)}
    
    Does the extracted intent accurately reflect what the user asked for?
    Are there any missing requirements or over-interpretations?
    Return: {{"valid": true/false, "issues": ["issue1", "issue2"]}}
    """
```

4. **Confidence Scoring**:
   - Add confidence scores to extracted fields
   - Flag ambiguous requests for clarification
   - Provide alternative interpretations for unclear requests

### **2. Create Intent Validation**
Location: `/home/brian/autocoder3_cc/blueprint_language/intent_validator.py`

```python
class IntentValidator:
    """Validate extracted semantic intent"""
    
    def validate_intent(self, intent: Dict) -> Tuple[bool, List[str]]:
        """Validate intent has required fields and logical consistency"""
        pass
    
    def sanitize_system_name(self, name: str) -> str:
        """Ensure valid Python identifier"""
        pass
```

### **3. Integration Test Suite**
Location: `/home/brian/autocoder3_cc/tests/test_semantic_extraction.py`

Test cases:
- Simple API request: "Create a todo API"
- Complex system: "Build analytics platform with real-time data"
- Ambiguous request: "Make something for customers"
- Edge cases: Very long requests, malformed input

### **4. Demo Script**
Location: `/home/brian/autocoder3_cc/demo_semantic_extraction.py`

Show before/after comparison:
- Current: LLM generates YAML (show failure cases)
- New: LLM extracts intent → deterministic YAML (show reliability)

## 🧪 **TESTING REQUIREMENTS**

### **Unit Tests**
- Test intent extraction with various request types
- Test validation logic
- Test edge case handling
- Test LLM prompt engineering

### **Integration Tests**
- Test with real OpenAI/Anthropic APIs
- Test with malformed natural language
- Test performance (latency, cost)

### **Demo Verification**
Test with these specific requests to show prompt engineering quality:

**Simple Requests:**
1. "Create a todo API"
2. "Build a blog website"
3. "Make a calculator API"

**Medium Complexity:**
4. "Create a customer management system with database"
5. "Build an e-commerce API with inventory tracking"
6. "Make a chat application with real-time messaging"

**Complex Requests:**
7. "Build a real-time analytics dashboard with live data processing and alerts"
8. "Create a multi-tenant SaaS platform with user management and billing"
9. "Build a fraud detection system with machine learning integration"

**Edge Cases:**
10. "Make something for customers" (ambiguous)
11. "I need a system that does everything" (overly broad)
12. "" (empty string)

Show JSON output is consistent, logical, and demonstrates conservative interpretation.

## 📦 **DELIVERABLES**

Create evidence package at: `/home/brian/autocoder3_cc/evidence/phase9_semantic_extractor/`

### **Required Files**:
**CRITICAL**: You MUST create ALL of these files or the evaluation will FAIL

1. **implementation_summary.md** - What was built and how it works
2. **test_results.txt** - All test outputs proving functionality
3. **demo_output.txt** - Demo script results showing before/after
4. **integration_test_results.json** - Structured test results
5. **performance_metrics.txt** - Latency and accuracy measurements
6. **working_implementation.py** - Main implementation file that external evaluator can run

### **Code Requirements**:
- All code must be production-ready with error handling
- Include comprehensive docstrings
- Follow existing codebase patterns
- Add logging for debugging

## 🚫 **CONSTRAINTS**

- NO access to other phase implementations or conversation history
- Must work standalone without dependencies on other phases
- Cannot modify existing blueprint generation yet (that's next phase)
- Focus only on semantic extraction, not full pipeline integration

## ✅ **SUCCESS CRITERIA**

1. **Functional**: Semantic extractor works with 95%+ accuracy on test cases
2. **Reliable**: Never crashes, handles edge cases gracefully
3. **Fast**: <2 seconds for typical requests
4. **Cost-effective**: <50% token usage vs current YAML generation
5. **Testable**: Complete test suite with passing results
6. **Demonstrable**: Clear before/after demo showing improvement

## 🎬 **EVIDENCE REQUIREMENTS**

Your evidence must prove:
- Semantic extractor extracts correct intent from natural language
- Validation catches malformed/incomplete intent
- System is more reliable than current LLM-YAML approach
- Performance is acceptable for production use
- External evaluator can run your tests and verify claims

All code must be executable by external evaluator without additional setup beyond standard Python packages.