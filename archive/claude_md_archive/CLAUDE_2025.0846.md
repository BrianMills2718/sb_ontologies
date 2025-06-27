# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a literature review and knowledge modeling project that processes academic papers through an improved multiphase workflow to create structured, machine-readable representations of academic theories using JSON Schema and semantic networks.

For detailed project goals and methodology, see **PROJECT_OVERVIEW.md**.

## Current System Architecture and Critical Problems Identified

### Validated Problems Requiring Immediate Solution

**CRITICAL FINDINGS from systematic validation (75% complete):**

1. **Property Graph Bias Problem**: Single-prompt approach defaults to property_graph when it should select table_matrix for experimental/comparative theories
2. **Multi-Theory Papers Problem**: System incorrectly unifies multiple distinct theories from review papers into single schemas
3. **Model Type Selection Accuracy**: Inverse relationship between theory complexity and baseline accuracy
4. **Missing Specialized Detection**: Need paradigm-specific prompts for accurate structure identification

### Current Validation Status: 75% Complete ✅

- **Phase 1: Academic Paper Processing** ✅ COMPLETED - Political science methodology validated
- **Phase 2: Cross-Domain Validation** ✅ COMPLETED - Economics/psychology patterns identified  
- **Phase 3: Complexity Testing** 🔄 IN PROGRESS - Simple theory completed (excellent results)
- **Phase 4: Discourse Type Diversification** ⏳ PENDING

**Key Discovery**: Inverse complexity-accuracy relationship - simple theories show perfect baseline performance while complex theories need manual correction.

### Next Phase: Comprehensive Prompt Testing and Strategy Optimization

**IMMEDIATE OBJECTIVE**: Test multiple prompting approaches systematically to solve identified problems before completing final validation phases.

#### Prompt Testing Plan

**Test 1: Multi-Theory Detection**
- Test theory count detection prompts on review papers
- Compare single vs multiple theory processing results
- Validate segmentation accuracy

**Test 2: Specialized Model Type Detection**
- Test parallel specialized prompts (table, graph, sequence, statistical, logical)
- Compare confidence scores vs current single-prompt approach
- Measure accuracy improvement on known cases

**Test 3: Hybrid Theory Detection and Processing** 
- Test automatic hybrid detection triggers
- Test component-specific extraction prompts
- Test integration mapping generation

**Test 4: Sequential vs Parallel Processing**
- Test sequential refinement (detect → classify → extract)
- Test parallel processing (multiple simultaneous prompts)
- Compare cost, time, and accuracy

### Experimental Prompt Architectures

#### Architecture 1: Multi-Phase Sequential Detection
```
Paper → Theory Count Detection → Theory Segmentation → Parallel Specialized Detection → Integration
```

#### Architecture 2: Parallel Specialized Classification
```
Paper → Simultaneous: [Table Detector, Graph Detector, Sequence Detector, Statistical Detector] → Confidence Integration
```

#### Architecture 3: Hierarchical Refinement
```
Paper → General Analysis → Specialized Refinement → Validation Pass → Final Schema
```

### Implementation Strategy: Comprehensive Testing

**Phase A: Prompt Development and Testing**
1. Develop specialized detection prompts for each model type
2. Create theory count detection prompts
3. Design hybrid theory integration prompts
4. Test on validation cases with known ground truth

**Phase B: Architecture Comparison**
1. Test sequential vs parallel processing approaches
2. Measure accuracy, cost, and processing time for each
3. Identify optimal architecture for different theory types

**Phase C: Validation Completion**
1. Apply optimized prompting to complete Phase 3 (medium/complex theories)
2. Complete Phase 4 (discourse type diversification)
3. Update automation priorities based on final results

**Phase D: System Integration**
1. Implement best-performing prompt architecture
2. Build automated theory type detection pipeline
3. Create comprehensive evaluation framework

### Current Processing Systems

#### Existing Processors:
- **multiphase_processor_improved.py** - Current system with identified problems
- **multiphase_processor_simple.py** - Simplified version for testing
- **multiphase_processor.py** - Original basic version (legacy)

#### New Experimental Processors (To Be Built):
- **experimental_multi_theory_processor.py** - Tests theory count detection
- **experimental_specialized_detector.py** - Tests parallel specialized prompts
- **experimental_hybrid_processor.py** - Tests automatic hybrid handling
- **experimental_sequential_processor.py** - Tests sequential refinement approach

### Testing Methodology

#### Validation Cases for Testing:
- **Young 1996**: Medium complexity, potential multi-theory (cognitive mapping vs semantic networks)
- **Heilman Framing**: Medium complexity, definite multi-theory (3 distinct framing types)
- **Lofland-Stark**: Simple, single theory (baseline for comparison)
- **Complex Hybrid**: Our stress test case (maximum complexity)

#### Success Metrics:
- **Model Type Accuracy**: Correct identification of optimal representation
- **Theory Segmentation**: Accurate separation of multiple theories in review papers
- **Vocabulary Completeness**: Comprehensive extraction maintained
- **Processing Efficiency**: Time and cost considerations
- **Integration Quality**: Hybrid theory handling effectiveness

### Directory Structure for Experimental Testing

```
experimental_testing/
├── prompt_variations/
│   ├── theory_count_detection/
│   ├── specialized_model_detection/
│   ├── hybrid_integration/
│   └── sequential_refinement/
├── architecture_comparison/
│   ├── sequential_results/
│   ├── parallel_results/
│   └── hybrid_results/
├── validation_retesting/
│   ├── young1996_multi_theory/
│   ├── heilman_segmented/
│   └── lofland_baseline/
└── optimization_findings.md
```

### Implementation Requirements

**Critical Success Factors:**
1. **Solve Property Graph Bias**: Specialized prompts must correctly identify table_matrix for experimental theories
2. **Handle Multi-Theory Papers**: Automatic detection and segmentation of review papers
3. **Maintain Quality**: Vocabulary extraction quality must not degrade
4. **Enable Hybrid Processing**: Automatic detection and handling of complex multi-paradigm theories

**Quality Standards (Updated):**
1. **Model Type Accuracy**: >90% correct identification across all theory types
2. **Theory Segmentation**: Automatic detection of multi-theory papers with accurate separation
3. **Vocabulary Completeness**: Maintain current extraction quality (20-120 terms depending on complexity)
4. **Hybrid Handling**: Automatic processing of multi-paradigm theories without human intervention
5. **Processing Efficiency**: Reasonable cost/time performance for large-scale processing

### Testing Plan Execution Order

1. **Multi-Theory Detection Testing** (solve segmentation problem)
2. **Specialized Model Type Detection** (solve property graph bias)
3. **Architecture Comparison** (optimize processing approach)
4. **Hybrid Theory Processing** (handle complex cases)
5. **Validation Completion** (finish systematic validation)
6. **Final System Integration** (implement best approach)

**CRITICAL**: Do not proceed to automation implementation until all experimental testing is complete and optimal approach is validated. Each experimental approach must be thoroughly tested and documented before moving to the next phase.

## Model Requirements

- **OpenAI Model**: O3 (configured in .env)
- **API Key**: Required in .env file
- **Dependencies**: See requirements.txt

## Notes

- O3 model does not support temperature parameters
- Processing may take 1-2 minutes per paper with O3
- Always verify outputs maintain theoretical accuracy
- Current validation shows 75% completion with critical architectural problems identified
- Comprehensive prompt testing required before final validation completion