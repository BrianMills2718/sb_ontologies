#!/usr/bin/env python3
"""Debug OpenAI API connection"""

import os
from dotenv import load_dotenv
from openai import OpenAI
import time

# Load environment variables
load_dotenv()

print("Loading environment...")
api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")

print(f"API Key present: {bool(api_key)}")
print(f"API Key length: {len(api_key) if api_key else 0}")
print(f"Model: {model}")

try:
    # Initialize client
    print("\nInitializing OpenAI client...")
    client = OpenAI(api_key=api_key)
    
    # Simple test
    print("\nTesting simple completion...")
    start_time = time.time()
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello, API is working!'"}
        ],
        max_tokens=50
    )
    
    end_time = time.time()
    print(f"Response received in {end_time - start_time:.2f} seconds")
    print(f"Response: {response.choices[0].message.content}")
    
except Exception as e:
    print(f"\nError: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()