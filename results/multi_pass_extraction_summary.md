# Multi-Pass Extraction System Summary

## Implementation Status

### System Architecture
Created a 5-pass extraction system (`src/schema_creation/multi_pass_extractor.py`) that performs specialized extraction:

1. **Pass 1**: Notation and symbols extraction
2. **Pass 2**: Tables and formal rules extraction  
3. **Pass 3**: Algorithms and procedures extraction
4. **Pass 4**: Metrics and evaluation extraction
5. **Pass 5**: Complete examples extraction

### Key Features
- Uses OpenAI O3 model with JSON output format (due to O3 limitations with structured outputs)
- Processes different sections of the paper in each pass
- Merges all extractions into comprehensive schema
- Includes debugging output to diagnose extraction issues

## Test Results

### Semantic Hypergraph Paper
**Extraction Summary**:
- Vocabulary terms: 71
- Type codes: 0 ❌ (should be 8)
- Role codes: 0 ❌ (should be 10)
- Special symbols: 15 ✓
- Tables extracted: 0 ❌ (should be 3+)
- Algorithms: 3 ✓
- Evaluation metrics: 2 ✓
- Complete examples: 1 ✓

**Critical Gaps**:
1. **Tables not detected**: The system failed to extract Table 1 (type codes), Table 2 (inference rules), and Table 3 (argument roles)
2. **Plain text table format**: Tables in the paper are formatted as plain text, not recognized by the model
3. **Core notation missed**: The 8 type codes (C, P, M, B, T, J, R, S) and 10 argument roles are fundamental but weren't extracted

### Young 1996 Paper
**Extraction Summary**:
- Vocabulary terms: 82 ✓
- Special symbols: 25 ✓ (relationship types like +, -, ->, etc.)
- Tables extracted: 1 ✓ (WorldView Coding Categories)
- Algorithms: 9 ✓
- Evaluation metrics: 7 ✓
- Complete examples: 12 ✓

**Better Performance**:
- Successfully extracted relationship types and modifiers
- Found the WorldView Coding Categories table
- Captured multiple algorithms and metrics
- Extracted rich examples

## Comparison with Previous Approaches

### vs Option 2 (Separate Implementation Extraction)
**Option 2 captured**:
- 8 type codes ✓
- 14 role codes ✓
- Basic patterns

**Multi-pass captured**:
- More algorithms (3-9 vs 0)
- More evaluation metrics (2-7 vs 0)
- More complete examples (1-12 vs 0)
- But missed the core notation tables

### Key Insight
The multi-pass system excels at extracting:
- Algorithms and procedures
- Evaluation metrics and results
- Complete examples and walkthroughs
- Mathematical symbols and notation

But struggles with:
- Plain text tables in academic papers
- Type/role code listings
- Pattern syntax specifications

## Recommendations

### 1. Hybrid Approach
Combine the best of both:
- Use Option 2 for notation/pattern extraction
- Use multi-pass for algorithms/metrics/examples
- Merge results for comprehensive schemas

### 2. Improved Table Detection
- Add dedicated table detection patterns
- Look for "Table N:" followed by formatted text
- Extract content between table markers

### 3. Pattern-Specific Prompts
- Create specialized prompts for type codes
- Look for patterns like "C - concept" or "P - predicate"
- Search for role listings like "s - subject"

### 4. Text Window Optimization
- Ensure tables aren't split across extraction windows
- Use overlapping windows for better coverage
- Focus on sections likely to contain formal specifications

## Next Steps

1. **Enhance Table Detection**: Add specific patterns for academic paper tables
2. **Improve Type/Role Extraction**: Create dedicated extractors for notation systems
3. **Test on More Papers**: Validate improvements across different theoretical frameworks
4. **Optimize for Fidelity**: Focus on achieving target fidelity for Young 1996 (48 concepts, 15 relationships)