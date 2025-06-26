Here is a comprehensive guide on everything you need to know to post-process the AI-generated YAML output.

The goal of this post-processing script is to take the high-level, human-reviewed blueprint from the AI and transform it into the final, complete, and programmatically valid artifact. It’s a simple but crucial assembly step.
Objective: The "Injector" Script

Your script's only job is to inject the universal, boilerplate definitions (CORE and sharedProps) into the $defs section of the json_schema that the LLM generated.
1. What You Will Need (Prerequisites)

You'll need three files to start:

    The AI-Generated YAML file: Let's call it young1996_raw.yml. This is the output you provided in the last message.
    The CORE Definitions file: Create a JSON file named CORE.json. Copy the Entity, Role, NaryTuple, and Argument definitions from the prompt's reference section into this file.
    The sharedProps Definition file: Create a JSON file named sharedProps.json. Copy the sharedProps definition from the prompt's reference section into this file.

CORE.json should contain:
JSON

{
  "Entity": { "type": "object", "additionalProperties": false, "required": ["id", "label", "entityType"], "properties": { "id": { "type": "string" }, "label": { "type": "string" }, "entityType": { "type": "string", "description": "Concept | Actor | Event | Statement | Class | Property | Individual | Rule" }, "props": { "type": "object" } } },
  "Role": { "type": "string", "enum": ["subject", "object", "attribute", "owner", "class", "property", "subClass", "superClass", "left", "right", "instance", "verb", "pattern", "rule", "warrant", "justification"] },
  "NaryTuple": { "type": "object", "additionalProperties": false, "required": ["id", "relation", "arguments"], "properties": { "id": { "type": "string" }, "relation": { "type": "string" }, "arguments": { "type": "array", "minItems": 1, "items": { "$ref": "#/$defs/Argument" } }, "props": { "type": "object" }, "representsStatementId": { "type": "string", "description": "Links an edge to the Statement node that reifies it." } } },
  "Argument": { "type": "object", "additionalProperties": false, "required": ["role", "entityId"], "properties": { "role": {"$ref": "#/$defs/Role"}, "entityId": {"type": "string"} } }
}

sharedProps.json should contain:
JSON

{
  "sharedProps": {
    "type": "object",
    "additionalProperties": true,
    "properties": {
      "truthValue": { "enum": ["true", "false", "partial", "possible", "impossible"] },
      "modifier":   { "enum": ["past", "present", "future", "goal", "hypothetical", "normative"] },
      "salience":   { "type": "integer", "minimum": 0 },
      "temporal": {
        "type": "object",
        "properties": {
          "startTime": { "type": "string", "format": "date-time" },
          "endTime":   { "type": "string", "format": "date-time" }
        }
      }
    }
  }
}

2. Step-by-Step Implementation Guide

Here is the logical flow for your script. Python is an ideal language for this due to its excellent PyYAML and json libraries.

Step 1: Setup

    Install the PyYAML library if you haven't already: pip install pyyaml.
    Place your three files (young1996_raw.yml, CORE.json, sharedProps.json) in the same directory as your script.

Step 2: Load All Inputs into Memory

    Read and parse the AI-generated young1996_raw.yml file into a Python dictionary.
    Read and parse CORE.json into a second Python dictionary.
    Read and parse sharedProps.json into a third Python dictionary.

Step 3: Perform the Injection

    Navigate to the $defs dictionary within your main data structure (e.g., data['json_schema']['$defs']).
    Merge the CORE definitions dictionary into the $defs dictionary.
    Merge the sharedProps definition dictionary into the $defs dictionary.

Step 4: Serialize and Save the Final Artifact

    Convert the modified Python dictionary back into a YAML formatted string.
    Save this string to a new file, for example young1996_processed.yml. It's good practice not to overwrite the original AI output.

3. Complete Python Script Example

Here is a fully functional Python script that accomplishes the entire post-processing task.
Python

import yaml
import json
import sys

# --- CONFIGURATION ---
# The names of your input files.
AI_OUTPUT_FILE = 'young1996_raw.yml'
CORE_DEFS_FILE = 'CORE.json'
SHARED_PROPS_FILE = 'sharedProps.json'

# The name for the final, processed output file.
FINAL_OUTPUT_FILE = 'young1996_processed.yml'

def post_process_schema(ai_yaml_path, core_defs_path, shared_props_path, final_yaml_path):
    """
    Loads an AI-generated schema YAML, injects boilerplate, and saves the final artifact.
    """
    print("Starting post-processing...")

    # --- Step 2: Load All Inputs ---
    try:
        with open(ai_yaml_path, 'r') as f:
            # Use safe_load to parse the main YAML file
            main_data = yaml.safe_load(f)
            print(f"Successfully loaded AI output from '{ai_yaml_path}'.")

        with open(core_defs_path, 'r') as f:
            core_definitions = json.load(f)
            print(f"Successfully loaded CORE definitions from '{core_defs_path}'.")

        with open(shared_props_path, 'r') as f:
            shared_props_definition = json.load(f)
            print(f"Successfully loaded sharedProps definition from '{shared_props_path}'.")

    except FileNotFoundError as e:
        print(f"ERROR: File not found - {e}. Please ensure all input files exist.")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to load files. Reason: {e}")
        sys.exit(1)


    # --- Step 3: Perform the Injection ---
    
    # Navigate to the target $defs block in the parsed data
    # The JSON string from the YAML is loaded as a string, so we need to parse it first.
    json_schema_string = main_data['json_schema']
    json_schema_data = json.loads(json_schema_string)
    
    defs_block = json_schema_data.get('$defs', {})

    # Use .update() to merge the dictionaries. This adds all key-value pairs
    # from the boilerplate files into the existing $defs block.
    defs_block.update(core_definitions)
    defs_block.update(shared_props_definition)
    print("Successfully injected CORE and sharedProps definitions.")

    # Place the modified $defs block back
    json_schema_data['$defs'] = defs_block

    # Put the modified (and now complete) JSON schema back into the main data structure
    # We need to convert it back to a JSON string to fit the YAML literal block style
    main_data['json_schema'] = json.dumps(json_schema_data, indent=2)

    # --- Step 4: Serialize and Save ---
    try:
        with open(final_yaml_path, 'w') as f:
            # Use dump() to write the Python dict back to YAML.
            # sort_keys=False preserves the key order from the prompt.
            yaml.dump(main_data, f, sort_keys=False, indent=2)
            print(f"Success! Final processed artifact saved to '{final_yaml_path}'.")
    except Exception as e:
        print(f"ERROR: Failed to save the final YAML file. Reason: {e}")
        sys.exit(1)


if __name__ == '__main__':
    post_process_schema(AI_OUTPUT_FILE, CORE_DEFS_FILE, SHARED_PROPS_FILE, FINAL_OUTPUT_FILE)

4. The Final, Processed Output

After running the script, the $defs block inside your young1996_processed.yml file will be complete. It will have been transformed from the AI's partial output...

Before (AI Output $defs):
JSON

"$defs": {
  "MyTheory_Relationships": { /* ... */ },
  "MyTheory_Actions": { /* ... */ }
}

...to the final, complete version:

After (Processed $defs):
JSON

"$defs": {
  "MyTheory_Relationships": { /* ... */ },
  "MyTheory_Actions": { /* ... */ },
  "Entity": { /* ... full definition ... */ },
  "Role": { /* ... full definition ... */ },
  "NaryTuple": { /* ... full definition ... */ },
  "Argument": { /* ... full definition ... */ },
  "sharedProps": { /* ... full definition ... */ }
}

This final artifact is now a self-contained, valid, and complete schema ready for use in your knowledge base.
