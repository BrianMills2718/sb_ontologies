"""
Utility for loading prompts from external files
"""

import os
from pathlib import Path
from functools import lru_cache

# Get the directory containing this file
SCHEMA_CREATION_DIR = Path(__file__).parent
PROMPTS_DIR = SCHEMA_CREATION_DIR / "prompts"

@lru_cache(maxsize=None)
def load_prompt(prompt_path: str) -> str:
    """
    Load a prompt from file with caching
    
    Args:
        prompt_path: Relative path from prompts directory (e.g., "simple/extraction_prompt.txt")
    
    Returns:
        Prompt content as string
    
    Raises:
        FileNotFoundError: If prompt file doesn't exist
    """
    full_path = PROMPTS_DIR / prompt_path
    
    if not full_path.exists():
        raise FileNotFoundError(f"Prompt not found: {full_path}")
    
    with open(full_path, 'r', encoding='utf-8') as f:
        return f.read().strip()

# Convenience functions for common prompts
def get_simple_extraction_prompt() -> str:
    """Get the simple extraction prompt"""
    return load_prompt("simple/extraction_prompt.txt")

def get_phase1_prompt() -> str:
    """Get Phase 1 vocabulary extraction prompt"""
    return load_prompt("multiphase/phase1_vocabulary_extraction.txt")

def get_phase2_prompt() -> str:
    """Get Phase 2 ontological classification prompt"""
    return load_prompt("multiphase/phase2_ontological_classification.txt")

def get_phase3_prompt() -> str:
    """Get Phase 3 schema generation prompt"""
    return load_prompt("multiphase/phase3_schema_generation.txt")

# Clear cache if needed (useful for development)
def clear_prompt_cache():
    """Clear the prompt cache to reload from disk"""
    load_prompt.cache_clear()