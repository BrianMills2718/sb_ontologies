#!/usr/bin/env python3
"""Test O3 model with parse method"""

import os
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

class SimpleOutput(BaseModel):
    message: str = Field(description="A simple message")
    number: int = Field(description="A number")

print("Testing O3 with parse method...")

try:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Test 1: Simple completion (no parse)
    print("\nTest 1: Simple completion...")
    response = client.chat.completions.create(
        model="o3",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello and return the number 42"}
        ]
    )
    print(f"Success! Response: {response.choices[0].message.content}")
    
    # Test 2: Parse method
    print("\nTest 2: Parse method...")
    try:
        response = client.beta.chat.completions.parse(
            model="o3",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Return a message saying hello and the number 42"}
            ],
            response_format=SimpleOutput
        )
        print(f"Success! Parsed: {response.choices[0].message.parsed}")
    except Exception as e:
        print(f"Parse method error: {type(e).__name__}: {e}")
        
        # Try alternative approach
        print("\nTrying alternative structured output approach...")
        response = client.chat.completions.create(
            model="o3",
            messages=[
                {"role": "system", "content": "Return JSON with fields 'message' and 'number'"},
                {"role": "user", "content": "message should be 'hello' and number should be 42"}
            ],
            response_format={"type": "json_object"}
        )
        print(f"JSON response: {response.choices[0].message.content}")
        
except Exception as e:
    print(f"\nError: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()