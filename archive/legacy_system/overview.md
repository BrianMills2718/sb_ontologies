Here is a comprehensive overview of the goal we are trying to accomplish and the specific requirements of the methodology we have designed.
I. The Strategic Goal: The "Why"
The overarching goal is to create a unified, large-scale, and computationally analyzable knowledge base from a corpus of 100+ academic papers in the social and behavioral sciences.
This project aims to solve a fundamental challenge: translating nuanced, qualitative, and often text-exclusive theories into a formal, structured, and interoperable format.
The core objectives are:
	1. High-Fidelity Modeling: To capture the unique logic, vocabulary, and semantic structure of each individual theory with the highest possible fidelity, avoiding oversimplification. This includes modeling not just concepts, but also their categorized relationships, logical axioms, and argumentative structures.
	2. Creating a Knowledge Asset: To convert each academic paper from a static document into a dynamic, structured data asset. This asset can then be queried, visualized, and used as a foundation for further analysis.
	3. Enabling Computational Analysis: The ultimate purpose is to make these complex theories accessible to computational tools. This opens the door to large-scale analysis, such as identifying common patterns across disparate theories, testing theoretical consistency, and potentially simulating theoretical dynamics.
	4. Ensuring Interoperability: A critical requirement is that all individual models are built upon a common foundational ontology. This ensures that a concept like an "Actor" or a property like "salience" has the same basic definition across the entire knowledge base, making meaningful cross-theory comparison possible.
II. The Methodology & Requirements: The "How" and "What"
To achieve the strategic goal, we have designed a sophisticated two-stage "Analyst & Assembler" workflow. This methodology carefully divides the labor between a Large Language Model (LLM) and a deterministic post-processing script to maximize both analytical quality and technical reliability.
A. The Two-Stage Workflow
Stage 1: The LLM's Role as "The Analyst" The LLM is tasked with the complex, human-like work of deep reading and interpretation.
	• Input: A raw academic paper.
	• Core Task: Its job is analysis, not syntax generation. It must read and understand the paper's theoretical framework, make critical analytical judgments, and extract the "essence" of the theory.
	• Output: A simple, structured YAML "Schema Blueprint." This document contains only the variable, analytical output and is free of all complex JSON syntax and boilerplate.
Stage 2: The Script's Role as "The Assembler" A local, deterministic script acts as a "general contractor" that builds the final product.
	• Input: The LLM-generated YAML "Schema Blueprint."
	• Core Task: Its job is assembly, not analysis. It reads the blueprint and carries out a set of precise, repetitive instructions.
	• Process: 
		1. It reads the model_type specified in the blueprint.
		2. Based on that type, it generates the correct top-level JSON Schema structure (e.g., the nodes and edges properties for a property_graph).
		3. It reads the structured vocabulary from the blueprint's definitions section to create the custom, categorized $defs in the schema.
		4. It injects the universal, unchanging CORE ontology and sharedProps definitions.
	• Output: The final, complete, and valid YAML artifact containing the full JSON Schema, ready for use.
B. Requirements for the "Schema Blueprint" (The LLM's Output)
The prompt we designed instructs the LLM to produce a YAML file with the following five top-level keys: citation, annotation, model_type, rationale, and schema_blueprint.
The schema_blueprint itself must contain:
	1. title and description: For the final schema.
	2. root_properties: A description of the top-level schema shape that corresponds to the chosen model_type.
	3. definitions: This is the core analytical output. It must be an exhaustive catalog of every theoretical term in the paper, where each term is a structured object with keys for its name, category, description, and inferred logical constraints like domain, range, or subTypeOf.
C. Requirements for the Final Assembled Artifact
The end product, after the script runs, must be a schema with these powerful capabilities:
	• Structurally Valid: It is a valid JSON Schema (draft-2020-12) nested within a clean YAML wrapper.
	• Semantically Rich: It captures the paper's nuanced vocabulary by sorting terms into distinct categories.
	• Logically Aware: It can formally represent ontological axioms like subClassOf and domain/range constraints.
	• Advanced Modeling: It supports sophisticated patterns like Reification (to model the structure of arguments) and N-ary relations (to model complex events with multiple participants).
	• Complete and Self-Contained: After injection, it contains all necessary definitions to be a fully functional and valid schema.
