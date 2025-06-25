# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a literature review and knowledge modeling project that processes academic papers through a two-stage "Analyst & Assembler" workflow. The project creates structured, machine-readable representations of academic theories using JSON Schema and semantic networks.

## Core Components

- **AI Analysis Stage**: Uses LLM to analyze academic papers and generate YAML schema blueprints
- **Post-processing Stage**: Python script that injects universal definitions into AI-generated schemas
- **Output**: Complete JSON Schema artifacts that model theoretical frameworks

## Key Files

- `prompt.txt` - Complete system prompt for "SchemaSage" AI analyst
- `post_processing.md` - Technical guide for Python post-processing script
- `overview.md` - Project methodology and requirements documentation
- `literature1.txt` - Sample academic paper (Young 1996 on cognitive mapping)

## Data Processing Workflow

1. **Input**: Academic paper text
2. **Analysis**: AI generates YAML with 5 keys: citation, annotation, model_type, rationale, schema_blueprint
3. **Assembly**: Python script injects CORE.json and sharedProps.json definitions into schema
4. **Output**: Complete, valid JSON Schema for theoretical framework

## Required Dependencies

```bash
pip install pyyaml
```

## Post-processing Script Requirements

The post-processing script needs three input files:
- AI-generated YAML output (e.g., `young1996_raw.yml`)
- `CORE.json` - Universal entity definitions (Entity, Role, NaryTuple, Argument)
- `sharedProps.json` - Shared property definitions (truthValue, modifier, salience, temporal)

## Model Types Supported

- property_graph (most common - nodes and edges structure)
- table_matrix
- sequence
- tree
- timeline
- other

## Schema Structure

Final schemas contain:
- **Nodes**: Concepts, actors, events, statements (Entity type)
- **Edges**: Relationships, actions, axioms (NaryTuple type)
- **$defs**: Complete vocabulary with categorized theoretical terms

## Analysis Categories

**Relationships**: equal, positive-cause, negative-cause, attribute, is-a, strategy, etc.
**Actions**: accept, attack, cooperate, negotiate, support, threaten, etc.
**Modifiers**: past, present, future, goal, hypothetical, normative
**Truth Values**: true, false, possible, impossible, partial

## Processing Instructions

**Continuous Processing Requirement**: You must systematically identify and process ALL papers in the literature directory that don't yet have corresponding YAML schemas. Do not stop until every text file has been analyzed and converted to a schema.

**Quality Assurance Process**: 
1. After creating each YAML schema, examine the underlying paper again to verify completeness
2. Check for missing theoretical concepts, relationships, or categorizations 
3. Improve and enhance schemas when gaps are identified
4. Ensure all key theoretical vocabulary from each paper is captured

**Workflow**:
1. Scan literature directory for unprocessed .txt files
2. Create subdirectories for new papers as needed
3. Analyze each paper systematically using the SchemaSage methodology
4. Generate comprehensive YAML schema with complete theoretical vocabulary
5. Update Index.md with proper citations, annotations, and topic codes
6. Review and improve schema quality before moving to next paper
7. Continue until all papers are processed

**Never stop processing** until the entire literature corpus has been converted to structured schemas.