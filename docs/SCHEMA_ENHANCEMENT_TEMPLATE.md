# Schema Enhancement Template

This template shows how to enhance any theory schema to work with the Universal Theory Applicator.

## Required Additions to Any Schema

### 1. Theory Name
```yaml
theory_name: "Your Theory Name"
```

### 2. Application Stages
Define the stages for applying your theory. Common patterns:

#### Pattern A: Extract → Filter → Structure → Analyze
```yaml
application_stages:
  - name: "extraction"
    description: "Extract all potential elements"
    prompt_template: |
      Extract all [YOUR_ELEMENT_TYPE] from this {domain} text.
      
      Include:
      - [Specific types to look for]
      
      TEXT:
      {text}
      
      Return as JSON:
      {output_format}
    output_format:
      items:
        - [your fields]
    
  - name: "filtering"
    description: "Filter based on theory criteria"
    prompt_template: |
      Filter these elements based on [YOUR_CRITERIA].
      
      Apply these criteria:
      {criteria}
      
      ELEMENTS:
      {previous.extraction}
      
      Return filtered results as JSON:
      {output_format}
    criteria:
      - "INCLUDE: [criterion 1]"
      - "EXCLUDE: [criterion 2]"
    output_format:
      items:
        - [filtered fields]
    post_processing:
      - type: "filter"
        condition:
          field: "included"
          operator: "equals"
          value: true
```

#### Pattern B: Type → Build → Compose (for formal systems)
```yaml
application_stages:
  - name: "typing"
    description: "Assign types to elements"
    prompt_template: |
      Assign types from this type system:
      {node_types}
      
      To these elements in the text:
      {text}
    
  - name: "construction"
    description: "Build structures using rules"
    prompt_template: |
      Apply these construction rules:
      {properties}
      
      To build structures from:
      {previous.typing}
```

### 3. Output Mapping
Map stage outputs to final schema structure:

```yaml
output_mapping:
  # Map your schema's main components
  concepts:
    from_stage: "final_stage_name"
    from_field: "concepts_field"
  relationships:
    from_stage: "structuring_stage"
    from_field: "relationships_field"
```

### 4. Summary Rules
Define how to calculate summary statistics:

```yaml
summary_rules:
  - name: "total_elements"
    type: "count"
    field: "elements"
  
  - name: "your_measure"
    type: "calculate"
    operation: "custom"
    # Define calculation details
```

## Stage Configuration Options

### Prompt Template Variables
Available in all prompt templates:
- `{text}` - The input text (up to 180k chars)
- `{domain}` - Domain context (e.g., "news", "academic")
- `{theory_name}` - Name of the theory
- `{node_types}` - From schema's nodes section
- `{connection_types}` - From schema's connections
- `{properties}` - From schema's properties
- `{modifiers}` - From schema's modifiers
- `{criteria}` - From stage's criteria list
- `{examples}` - From stage's examples
- `{output_format}` - From stage's output_format
- `{previous.STAGE_NAME}` - Results from any previous stage

### Post-Processing Rules
```yaml
post_processing:
  - type: "filter"
    condition:
      field: "field_name"
      operator: "equals|contains|greater_than|in"
      value: "value_to_match"
  
  - type: "transform"
    operation:
      type: "add_field|rename_field"
      # operation-specific params
```

### Metadata Extraction
```yaml
metadata_fields: ["count", "distribution", "custom_field"]
```

## Example: Adding to a Network Analysis Theory

```yaml
theory_name: "Social Network Analysis"

# Original theory elements (keep these)
nodes:
  - type: "actor"
    description: "Social entities"
  - type: "organization"
    description: "Groups and institutions"

connections:
  - type: "social_tie"
    vocabulary: ["knows", "works_with", "manages"]

# Add application stages
application_stages:
  - name: "entity_extraction"
    description: "Extract all social entities"
    prompt_template: |
      Extract all people and organizations from this {domain} text.
      [...]
    criteria:
      - "INCLUDE: Named individuals"
      - "INCLUDE: Organizations and groups"
      - "EXCLUDE: Generic role references"
  
  - name: "tie_detection"
    description: "Identify social ties"
    prompt_template: |
      Find all social relationships between these entities:
      {previous.entity_extraction}
      
      Using these relationship types:
      {connection_types}
      [...]

# Add output mapping
output_mapping:
  nodes:
    from_stage: "entity_extraction"
    from_field: "entities"
  edges:
    from_stage: "tie_detection"
    from_field: "ties"

# Add summary rules  
summary_rules:
  - name: "network_density"
    type: "calculate"
    operation: "density"
    nodes_field: "nodes"
    edges_field: "edges"
```

## Best Practices

1. **Make stages theory-agnostic where possible** - Use generic names like "extraction", "filtering", "structuring"

2. **Put theory-specific knowledge in criteria/examples** - Not hard-coded in prompts

3. **Use previous stage results** - Each stage should build on previous work

4. **Include domain parameters** - Allow same schema to work across domains

5. **Provide clear output formats** - Specify exact JSON structure expected

6. **Add post-processing for robustness** - Filter/transform to ensure quality

7. **Extract meaningful metadata** - Help users understand what happened in each stage

8. **Map to standard schema structure** - Maintain compatibility with existing tools

## Testing Your Enhanced Schema

```bash
# Test with the universal applicator
python src/schema_application/universal_theory_applicator.py \
  test_text.txt \
  your_enhanced_schema.yml \
  output.yml \
  domain_type
```

The enhanced schema will work with ANY text and produce theory-appropriate structured output!