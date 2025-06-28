#!/usr/bin/env python3
"""
Multi-pass extraction system for meta_schema_8
Combines focused passes to ensure complete extraction
"""
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class MultiPassV8Extractor:
    """Multi-pass extraction system optimized for completeness"""
    
    def __init__(self):
        self.client = OpenAI()
        self.max_tokens = 60000
        
    def extract_tables_and_lists(self, content: str) -> Dict[str, Any]:
        """Pass 1: Extract all tables, lists, and enumerations"""
        prompt = """You are extracting structured data from an academic paper.

TASK: Find and extract ALL tables, lists, enumerations, and taxonomies.

CRITICAL: 
- Tables often contain the CORE VOCABULARY of a theory
- Lists of terms/categories ARE theoretical components, not just examples
- Coding schemes, taxonomies, and ontologies are CENTRAL to the theory

Extract:
1. All tables (preserve structure and ALL entries)
2. All bulleted or numbered lists
3. All enumerations (e.g., "these include X, Y, Z")
4. All taxonomies or classification schemes
5. All coding categories or schemes

For each found structure, provide:
- Location context (section name, surrounding text)
- Type (table, list, enumeration, etc.)
- Complete contents (EVERY item, no summarization)
- Purpose/role in the theory

Output as JSON with structure:
{
  "tables": [...],
  "lists": [...],
  "enumerations": [...],
  "coding_schemes": [...]
}"""

        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Extract all structured data from:\n\n{content}"}
        ]
        
        response = self.client.chat.completions.create(
            model="o1",
            messages=messages,
            max_completion_tokens=self.max_tokens
        )
        
        try:
            content = response.choices[0].message.content
            # Find JSON in response
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                result = json.loads(content[json_start:json_end])
                return result
            else:
                print("Warning: No JSON found in tables extraction")
                return {"tables": [], "lists": [], "enumerations": [], "coding_schemes": []}
        except Exception as e:
            print(f"Warning: Error parsing tables response: {e}")
            return {"tables": [], "lists": [], "enumerations": [], "coding_schemes": []}
    
    def extract_notation_and_formulas(self, content: str) -> Dict[str, Any]:
        """Pass 2: Extract notation, symbols, and formulas"""
        prompt = """Extract ALL mathematical notation, symbols, and formulas from this paper.

For each item found, capture:
1. Symbol/notation as written
2. Definition/meaning
3. Usage context
4. Related formulas
5. LaTeX representation if applicable

Also extract:
- Relationship symbols (e.g., +, -, →, ⊃)
- Special notation (e.g., subscripts, superscripts)
- Abbreviated codes (e.g., 's' for subject, 'o' for object)

Output as JSON."""

        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": content[:50000]}  # Focus on first part
        ]
        
        response = self.client.chat.completions.create(
            model="o1",
            messages=messages,
            max_completion_tokens=30000
        )
        
        try:
            result = json.loads(response.choices[0].message.content)
            if isinstance(result, list):
                return {"notations": result, "formulas": []}
            return result
        except:
            return {"notations": [], "formulas": []}
    
    def extract_vocabulary_enhanced(self, content: str, tables_data: Dict) -> Dict[str, Any]:
        """Pass 3: Extract vocabulary with awareness of tables/lists"""
        
        # Build context from tables
        table_context = "IMPORTANT: The following items were found in tables/lists and MUST be included:\n\n"
        
        for table in tables_data.get("tables", []):
            table_context += f"Table: {table.get('context', '')}\n"
            table_context += f"Contents: {table.get('contents', '')}\n\n"
            
        for lst in tables_data.get("lists", []):
            table_context += f"List: {lst.get('context', '')}\n" 
            table_context += f"Items: {lst.get('items', [])}\n\n"
            
        prompt = f"""Extract a complete theoretical vocabulary from this paper.

{table_context}

CRITICAL REQUIREMENTS:
1. If a table lists 50 actions, you MUST extract all 50 as connections/actions
2. Coding categories ARE theoretical components, not examples
3. Every term in a taxonomy/ontology must be captured
4. Preserve exact terminology (indigenous_term)

For each term, identify:
- Indigenous term (exact as written)
- Category: entity, connection, property, modifier, action
- Definition/description
- If it's part of a larger taxonomy

Remember: Lists of coding categories (like action types) are THE THEORY, not optional details."""

        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": content}
        ]
        
        response = self.client.chat.completions.create(
            model="o1",
            messages=messages,
            max_completion_tokens=self.max_tokens
        )
        
        try:
            return json.loads(response.choices[0].message.content)
        except:
            return {"vocabulary": []}
    
    def validate_and_merge(self, vocabulary: Dict, tables_data: Dict) -> Dict[str, Any]:
        """Pass 4: Validate extraction completeness"""
        
        # Count expected items from tables
        expected_counts = {}
        
        for table in tables_data.get("tables", []):
            if "Actions" in str(table.get("context", "")):
                # Count action items
                contents = str(table.get("contents", ""))
                actions = re.findall(r'\b\w+\b', contents)
                expected_counts["actions"] = len([a for a in actions if len(a) > 2])
                
        validation_prompt = f"""Validate extraction completeness.

Expected from tables/lists:
{json.dumps(expected_counts, indent=2)}

Current vocabulary:
{json.dumps(vocabulary, indent=2)}

Check:
1. Are all table items represented?
2. Are coding categories properly classified?
3. Is anything missing?

If items are missing, list them explicitly."""

        messages = [
            {"role": "system", "content": validation_prompt},
            {"role": "user", "content": "Validate and identify any missing items."}
        ]
        
        response = self.client.chat.completions.create(
            model="o1", 
            messages=messages,
            max_completion_tokens=30000
        )
        
        return response.choices[0].message.content
    
    def final_assembly(self, content: str, all_passes_data: Dict) -> Dict[str, Any]:
        """Final pass: Assemble complete schema using all extracted data"""
        
        # Load the meta_schema_8 structure
        with open("/home/brian/lit_review/meta_schema_8.json", 'r') as f:
            meta_schema = json.load(f)
            
        # Load the standard prompt
        with open("/home/brian/lit_review/prompt_2025.06280355.txt", 'r') as f:
            base_prompt = f.read()
            
        enhanced_prompt = f"""{base_prompt}

ADDITIONAL CONTEXT FROM FOCUSED EXTRACTION:

Tables and Lists Found:
{json.dumps(all_passes_data.get('tables_lists', {}), indent=2)}

Notation Extracted:
{json.dumps(all_passes_data.get('notation', {}), indent=2)}

Complete Vocabulary:
{json.dumps(all_passes_data.get('vocabulary', {}), indent=2)}

Validation Notes:
{all_passes_data.get('validation', '')}

CRITICAL: Your extraction MUST include every item identified in the focused passes above."""

        messages = [
            {"role": "system", "content": enhanced_prompt},
            {"role": "user", "content": f"Create the complete theory schema:\n\n{content}"}
        ]
        
        response = self.client.chat.completions.create(
            model="o1",
            messages=messages,
            max_completion_tokens=80000
        )
        
        # Extract JSON from response
        content = response.choices[0].message.content
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        
        if json_start != -1 and json_end > json_start:
            return json.loads(content[json_start:json_end])
        else:
            raise ValueError("No valid JSON found in response")
    
    def extract(self, paper_path: Path, output_path: Path) -> Dict[str, Any]:
        """Run complete multi-pass extraction"""
        
        print(f"\nMulti-Pass Extraction: {paper_path.name}")
        print("="*60)
        
        # Read paper
        with open(paper_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        if len(content) > 80000:
            print(f"Warning: Truncating from {len(content)} to 80k chars")
            content = content[:80000]
            
        all_passes_data = {}
        
        # Pass 1: Tables and Lists
        print("\nPass 1: Extracting tables and lists...")
        tables_data = self.extract_tables_and_lists(content)
        all_passes_data['tables_lists'] = tables_data
        
        # Report findings
        print(f"  Found {len(tables_data.get('tables', []))} tables")
        print(f"  Found {len(tables_data.get('lists', []))} lists")
        print(f"  Found {len(tables_data.get('coding_schemes', []))} coding schemes")
        
        # Pass 2: Notation
        print("\nPass 2: Extracting notation and formulas...")
        notation_data = self.extract_notation_and_formulas(content)
        all_passes_data['notation'] = notation_data
        print(f"  Found {len(notation_data.get('notations', []))} notations")
        
        # Pass 3: Enhanced Vocabulary
        print("\nPass 3: Extracting complete vocabulary...")
        vocabulary_data = self.extract_vocabulary_enhanced(content, tables_data)
        all_passes_data['vocabulary'] = vocabulary_data
        
        # Pass 4: Validation
        print("\nPass 4: Validating completeness...")
        validation = self.validate_and_merge(vocabulary_data, tables_data)
        all_passes_data['validation'] = validation
        
        # Final Assembly
        print("\nFinal Pass: Assembling complete schema...")
        final_schema = self.final_assembly(content, all_passes_data)
        
        # Save output
        with open(output_path, 'w') as f:
            json.dump(final_schema, f, indent=2)
            
        print(f"\n✓ Saved to: {output_path}")
        
        # Summary
        for theory_name, theory_data in final_schema.items():
            if 'schema' in theory_data and 'Ontology' in theory_data['schema']:
                ont = theory_data['schema']['Ontology']
                print(f"\nExtraction Summary for {theory_name}:")
                print(f"  Entities: {len(ont.get('entities', []))}")
                print(f"  Connections: {len(ont.get('connections', []))}")
                print(f"  Properties: {len(ont.get('properties', []))}")
                print(f"  Modifiers: {len(ont.get('modifiers', []))}")
                
        return final_schema

def main():
    """Test multi-pass extraction"""
    extractor = MultiPassV8Extractor()
    
    # Test on Cognitive Mapping paper
    paper_path = Path("/home/brian/lit_review/literature/operational_code_analysis/Cognitive Mapping Meets Semantic Networks.txt")
    output_path = Path("/home/brian/lit_review/results/cognitive_mapping_multipass_v8.json")
    
    if paper_path.exists():
        result = extractor.extract(paper_path, output_path)
    else:
        print(f"Error: Paper not found at {paper_path}")

if __name__ == "__main__":
    main()