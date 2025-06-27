#!/usr/bin/env python3
"""Debug imports and initialization"""

print("1. Starting imports...")

import os
print("2. Imported os")

import sys
print("3. Imported sys")

from dotenv import load_dotenv
print("4. Imported dotenv")

load_dotenv()
print("5. Loaded .env")

from openai import OpenAI
print("6. Imported OpenAI")

api_key = os.getenv("OPENAI_API_KEY")
print(f"7. API key present: {bool(api_key)}")

model = os.getenv("OPENAI_MODEL")
print(f"8. Model: {model}")

try:
    client = OpenAI(api_key=api_key)
    print("9. Created OpenAI client")
except Exception as e:
    print(f"9. Error creating client: {e}")

print("10. All imports successful!")

# Now try importing the processor
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print("11. Added path")

try:
    from schema_creation import multiphase_processor_improved
    print("12. Imported multiphase_processor_improved")
except Exception as e:
    print(f"12. Error importing processor: {e}")
    import traceback
    traceback.print_exc()