#!/usr/bin/env python3
"""
Generate enhanced SH schema with notation details
"""

import yaml
from pathlib import Path
from datetime import datetime

def generate_enhanced_sh_schema():
    """Create schema with complete notation system"""
    
    # Load existing schema as base
    existing_schema_path = "/home/brian/lit_review/schemas/semantic_hypergraph/semantic_hypergraph_complete.yml"
    with open(existing_schema_path, 'r') as f:
        base_schema = yaml.safe_load(f)
    
    # Add notation system section
    notation_system = {
        "argument_roles": {
            "sa": "subject-agent (P.sa = predicate's canonical subject)",
            "pa": "patient/direct-object (P.pa = DO)",
            "ioa": "indirect-object/addressee (P.ioa = IO)",
            "soa": "subject-or-object underspecified (P.soa = ambiguous)",
            "ma": "modifier-argument (B.ma = thing modified by binder)",
            "ta": "temporal adjunct (P.ta)",
            "ra": "reason/cause adjunct (P.ra)",
            "ga": "goal/directive adjunct (P.ga)",
            "ca": "comparative adjunct (P.ca)",
            "da": "determiner-argument (P.da or C.da)",
            "la": "locative adjunct (P.la)",
            "na": "negation argument (P.na)",
            "qa": "quantity argument (P.qa)"
        },
        "special_symbols": {
            "+/B": "one or more Binder nodes",
            "*/M": "zero or more Modifier nodes",
            ":/J": "exactly one Junction node",
            "+": "one or more (quantifier)",
            "*": "zero or more (quantifier)",
            "?": "optional (0 or 1)",
            ":": "exactly one",
            "|": "logical OR in patterns",
            "⊕": "root/focus of current sub-graph (diagram only)",
            "⊗": "already-reduced fragment (diagram only)",
            "◊": "ellipsis/content omitted (diagram only)"
        },
        "pattern_syntax": {
            "/T": "any node of type T (where T ∈ {C,P,M,B,T,J,R,S})",
            "P.sa:SUBJ": "binds matched node to variable SUBJ",
            ":\"text\"/C": "concept whose surface form is 'text'",
            "⇒": "rewrite rule arrow (LHS pattern → RHS action)",
            "(...)": "grouping in patterns"
        }
    }
    
    # Add pattern language examples
    pattern_examples = [
        {
            "pattern": "P.sa +/B P.pa",
            "description": "Predicate's subject, followed by any number of Binder phrases, followed by predicate's object",
            "example": "subject VERB (preposition-phrases) object"
        },
        {
            "pattern": "/P :/J /P",
            "description": "Two predicates connected by exactly one junction",
            "example": "run AND jump"
        },
        {
            "pattern": ":/C (*/M) :/P",
            "description": "Exactly one concept, optionally modified, followed by exactly one predicate",
            "example": "the big dog barks"
        }
    ]
    
    # Add type inference rules
    type_inference_rules = [
        "Verbs → P (Predicate) type",
        "Nouns/Proper names → C (Concept) type",
        "Adjectives/Adverbs → M (Modifier) type",
        "Prepositions/Case markers → B (Binder) type",
        "Conjunctions → J (Junction) type",
        "Pronouns/Demonstratives → R (Reference) type",
        "Tense/Aspect markers → T (Temporal) type",
        "Reified propositions → S (Statement) type"
    ]
    
    # Update schema
    enhanced_schema = base_schema.copy()
    enhanced_schema["notation_system"] = notation_system
    enhanced_schema["pattern_examples"] = pattern_examples
    enhanced_schema["type_inference_rules"] = type_inference_rules
    
    # Add notation info to relevant definitions
    for definition in enhanced_schema.get("definitions", []):
        if definition["name"] == "Atom":
            definition["notation"] = "Written as term/TYPE or term/TYPE.role (e.g., run/P.sa)"
        elif definition["name"] == "Connector":
            definition["role_codes"] = list(notation_system["argument_roles"].keys())
            definition["notation_format"] = "TYPE.role where TYPE is uppercase, role is lowercase"
    
    # Add implementation algorithms
    enhanced_schema["implementation_algorithms"] = {
        "hyperedge_creation": [
            "1. Identify predicate/connector atom",
            "2. Extract argument atoms based on role codes",
            "3. Order arguments according to role semantics",
            "4. Create hyperedge with connector and ordered arguments",
            "5. Add modifiers and truth values if present"
        ],
        "pattern_matching": [
            "1. Parse pattern string into typed components",
            "2. Match against hypergraph structure",
            "3. Bind variables for matched nodes",
            "4. Apply rewrite rules to create new hyperedges"
        ]
    }
    
    return enhanced_schema

def main():
    enhanced_schema = generate_enhanced_sh_schema()
    
    # Save enhanced schema
    output_path = Path("/home/brian/lit_review/schemas/semantic_hypergraph/semantic_hypergraph_enhanced.yml")
    with open(output_path, 'w') as f:
        yaml.dump(enhanced_schema, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
    
    print(f"Enhanced schema saved to: {output_path}")
    
    # Summary
    print("\n=== ENHANCEMENTS ADDED ===")
    print(f"Argument roles: {len(enhanced_schema['notation_system']['argument_roles'])}")
    print(f"Special symbols: {len(enhanced_schema['notation_system']['special_symbols'])}")
    print(f"Pattern examples: {len(enhanced_schema['pattern_examples'])}")
    print(f"Type inference rules: {len(enhanced_schema['type_inference_rules'])}")

if __name__ == "__main__":
    main()