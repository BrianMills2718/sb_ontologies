#!/usr/bin/env python3
"""Test O3 model with simple request"""

import os
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "o3")

class SimpleTest(BaseModel):
    word: str
    definition: str

print(f"Testing model: {MODEL}")
print("Sending request...")

try:
    response = client.beta.chat.completions.parse(
        model=MODEL,
        messages=[
            {"role": "user", "content": "Define the word 'hello'"}
        ],
        response_format=SimpleTest
    )
    print("Response:", response.choices[0].message.parsed)
except Exception as e:
    print(f"Error: {e}")