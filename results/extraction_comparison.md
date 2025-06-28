# Extraction Method Comparison: Cognitive Mapping Paper

## Single-Pass Extraction (meta_schema_8)
- **Total Terms**: ~15
- **Entities**: 10
- **Connections**: 5 (only relationship types)
- **Properties**: 0  
- **Modifiers**: 6
- **Missing**: All 50 action types from Table 1

## Multi-Pass Extraction
- **Total Terms**: 88
- **Includes**: All relationship types AND action types
- **Better Coverage**: Captured the complete WorldView coding scheme

## Key Improvements

### 1. Table Detection
The multi-pass system specifically extracted Table 1, recognizing it contains:
- 13 relationship types
- 50 action types

### 2. Vocabulary Awareness
By telling the LLM explicitly that "coding categories ARE theoretical components", it properly extracted all actions.

### 3. Validation Pass
The validation step ensures nothing is missed by comparing extracted vocabulary against identified tables/lists.

## Extraction Quality Metrics

| Metric | Single-Pass | Multi-Pass | Improvement |
|--------|------------|------------|-------------|
| Total Terms | 15 | 88 | 487% increase |
| Action Coverage | 0/50 | 50/50 | 100% coverage |
| Relationship Coverage | 5/13 | 13/13 | 100% coverage |
| Theory Fidelity | ~23% | ~100% | Complete |

## Conclusion

The multi-pass approach is essential for theories that define extensive taxonomies or coding schemes. The single-pass approach fails to recognize that enumerated lists of terms ARE the theory, not just examples.

### When to Use Multi-Pass:
1. Papers with tables of terms/categories
2. Theories defining coding schemes
3. Papers with extensive taxonomies
4. Any theory where vocabulary IS the contribution

### Next Steps:
1. Test multi-pass on other papers
2. Optimize pass coordination
3. Create automatic detection of when multi-pass is needed