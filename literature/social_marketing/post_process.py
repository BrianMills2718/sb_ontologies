import yaml
import json
import sys
import os

# --- CONFIGURATION ---
# The names of your input files.
AI_OUTPUT_FILE = 'social_marketing_kotler_zaltman_raw.yml'
CORE_DEFS_FILE = 'CORE.json'
SHARED_PROPS_FILE = 'sharedProps.json'

# The name for the final, processed output file.
FINAL_OUTPUT_FILE = 'social_marketing_kotler_zaltman_schema.yml'

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
    # The JSON schema is within schema_blueprint.schema
    json_schema_data = main_data['schema_blueprint']['schema']
    
    defs_block = json_schema_data.get('$defs', {})

    # Use .update() to merge the dictionaries. This adds all key-value pairs
    # from the boilerplate files into the existing $defs block.
    defs_block.update(core_definitions)
    defs_block.update(shared_props_definition)
    print("Successfully injected CORE and sharedProps definitions.")

    # Place the modified $defs block back
    json_schema_data['$defs'] = defs_block

    # The schema is already in the correct location in the data structure
    main_data['schema_blueprint']['schema'] = json_schema_data

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
    # Change to the script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    post_process_schema(AI_OUTPUT_FILE, CORE_DEFS_FILE, SHARED_PROPS_FILE, FINAL_OUTPUT_FILE)