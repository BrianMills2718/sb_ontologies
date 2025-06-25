#!/usr/bin/env python3

import os
import json
import yaml
from typing import List, Optional
from pydantic import BaseModel, Field
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/home/brian/lit_review/.env')

class Agent(BaseModel):
    class Config:
        extra = "forbid"
    
    name: str = Field(description="Name or identifier of the agent")
    type: str = Field(description="Type of agent (government, witness, media, etc.)")
    role: str = Field(description="Role in the information ecosystem")
    motivations: List[str] = Field(description="Motivations driving this agent")

class Message(BaseModel):
    class Config:
        extra = "forbid"
    
    content: str = Field(description="Core message content")
    information_type: str = Field(description="Type: mis-information, dis-information, mal-information, or verified-information")
    source: str = Field(description="Who created this message")
    credibility_indicators: List[str] = Field(description="Factors affecting credibility")

class Interpreter(BaseModel):
    class Config:
        extra = "forbid"
    
    audience_type: str = Field(description="Type of audience/interpreter")
    likely_interpretation_mode: str = Field(description="hegemonic, negotiated, or oppositional reading")
    cognitive_factors: List[str] = Field(description="Cognitive processes affecting interpretation")

class InformationDisorderPhase(BaseModel):
    class Config:
        extra = "forbid"
    
    phase: str = Field(description="creation, production, or dissemination phase")
    description: str = Field(description="What happens in this phase")
    key_actors: List[str] = Field(description="Who is involved in this phase")

class CredibilityDynamics(BaseModel):
    class Config:
        extra = "forbid"
    
    credibility_factor: str = Field(description="Factor affecting credibility")
    impact: str = Field(description="How this factor impacts credibility")
    evidence: str = Field(description="Evidence from the text")

class TransparencyAnalysis(BaseModel):
    class Config:
        extra = "forbid"
    
    transparency_theme: str = Field(description="Specific transparency issue")
    position: str = Field(description="Position taken on this issue")
    supporting_evidence: str = Field(description="Evidence from testimony")

class InformationDisorderAnalysis(BaseModel):
    """
    Analysis of the Grusch testimony using the Information Disorder framework
    """
    class Config:
        extra = "forbid"
    
    # Core framework elements
    agents: List[Agent] = Field(description="Key information agents identified")
    messages: List[Message] = Field(description="Core messages being disseminated")
    interpreters: List[Interpreter] = Field(description="Target audiences and interpretation modes")
    
    # Process phases
    information_phases: List[InformationDisorderPhase] = Field(description="Creation, production, dissemination phases")
    
    # Credibility and transparency dynamics
    credibility_dynamics: List[CredibilityDynamics] = Field(description="Factors affecting information credibility")
    transparency_themes: List[TransparencyAnalysis] = Field(description="Government transparency vs opacity dynamics")
    
    # Potential information disorder
    potential_misinformation: List[str] = Field(description="Potential mis-information elements identified")
    potential_disinformation: List[str] = Field(description="Potential dis-information elements identified")
    potential_malinformation: List[str] = Field(description="Potential mal-information elements identified")
    
    # Overall assessment
    dominant_narrative: str = Field(description="Primary narrative being constructed")
    information_contest: str = Field(description="How different narratives compete")
    framework_insights: List[str] = Field(description="Key insights from applying the Information Disorder framework")

def load_schema(yaml_path):
    """Load the YAML schema file"""
    with open(yaml_path, 'r') as f:
        return yaml.safe_load(f)

def load_text(text_path):
    """Load the text file to analyze"""
    with open(text_path, 'r') as f:
        return f.read()

def analyze_with_openai(schema_yaml, text_content):
    """Use OpenAI to extract information using the schema"""
    
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    # Create the system prompt that explains the framework
    system_prompt = f"""
    You are an expert analyst applying the Information Disorder theoretical framework to analyze text.
    
    FRAMEWORK OVERVIEW:
    The Information Disorder framework (Wardle & Derakhshan, 2017) analyzes how information flows through three types (mis-, dis-, mal-information), three elements (agents, messages, interpreters), and three phases (creation, production, dissemination).
    
    KEY CONCEPTS FROM THE SCHEMA:
    - AGENTS: People/organizations creating, producing, or disseminating information
    - MESSAGES: Information content with varying credibility and accuracy
    - INTERPRETERS: Audiences who receive and make sense of messages
    - PHASES: Creation (initial creation), Production (turning into media), Dissemination (distribution)
    - MOTIVATIONS: Financial, political, social, psychological
    - INTERPRETATION MODES: Hegemonic (accept as encoded), Negotiated (partial acceptance), Oppositional (reject dominant meaning)
    - CREDIBILITY FACTORS: Source expertise, institutional authority, evidence quality, consistency
    
    INFORMATION TYPES:
    - Mis-information: False but without harmful intent
    - Dis-information: False and deliberately harmful
    - Mal-information: True but used to cause harm
    
    Analyze the provided text systematically using this framework. Extract specific examples and evidence.
    """
    
    user_prompt = f"""
    Analyze this congressional testimony transcript using the Information Disorder framework.
    
    Focus on:
    1. Who are the agents creating/disseminating information?
    2. What messages are being created and how credible are they?
    3. Who are the interpreters and how might they read these messages?
    4. What transparency vs. secrecy dynamics are at play?
    5. Are there any elements of information disorder (mis/dis/mal-information)?
    
    TEXT TO ANALYZE:
    {text_content[:8000]}  # Limit text length for API
    """
    
    try:
        response = client.chat.completions.create(
            model=os.getenv('OPENAI_MODEL', 'gpt-4o-2024-08-06'),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_schema", "json_schema": {
                "name": "information_disorder_analysis",
                "strict": True,
                "schema": InformationDisorderAnalysis.model_json_schema()
            }}
        )
        
        # Parse the JSON response
        analysis_json = json.loads(response.choices[0].message.content)
        return InformationDisorderAnalysis(**analysis_json)
        
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return None

def main():
    # Paths
    schema_path = "/home/brian/lit_review/literature/information_disorder/wardle_derakhshan_2017_raw.yml"
    text_path = "/home/brian/lit_review/texts/grusch_testimony.txt"
    output_path = "/home/brian/lit_review/grusch_analysis_results.json"
    
    print("Loading schema and text...")
    schema = load_schema(schema_path)
    text_content = load_text(text_path)
    
    print(f"Schema loaded: {schema['citation']}")
    print(f"Text loaded: {len(text_content)} characters")
    
    print("Analyzing with OpenAI...")
    analysis = analyze_with_openai(schema, text_content)
    
    if analysis:
        # Save results
        with open(output_path, 'w') as f:
            json.dump(analysis.model_dump(), f, indent=2)
        
        print(f"Analysis complete! Results saved to: {output_path}")
        
        # Print summary
        print("\n=== ANALYSIS SUMMARY ===")
        print(f"Agents identified: {len(analysis.agents)}")
        print(f"Messages analyzed: {len(analysis.messages)}")
        print(f"Interpreters identified: {len(analysis.interpreters)}")
        print(f"Credibility factors: {len(analysis.credibility_dynamics)}")
        print(f"Transparency themes: {len(analysis.transparency_themes)}")
        print(f"\nDominant narrative: {analysis.dominant_narrative}")
        
        return analysis
    else:
        print("Analysis failed.")
        return None

if __name__ == "__main__":
    analysis = main()