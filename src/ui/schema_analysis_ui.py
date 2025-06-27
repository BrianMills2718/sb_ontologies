#!/usr/bin/env python3

import streamlit as st
import os
import json
import yaml
from typing import List, Dict, Optional
from pathlib import Path
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import networkx as nx
from datetime import datetime
import numpy as np
import re

# Load environment variables
load_dotenv('/home/brian/lit_review/.env')

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Configuration
LITERATURE_DIR = "/home/brian/lit_review/literature"
TEXTS_DIR = "/home/brian/lit_review/texts"
RESULTS_DIR = "/home/brian/lit_review/analysis_results"

# Ensure results directory exists
os.makedirs(RESULTS_DIR, exist_ok=True)

class SchemaAnalysisUI:
    def __init__(self):
        self.schema_tree = self.build_schema_tree()
        self.text_files = self.get_text_files()
        
    def build_schema_tree(self) -> Dict:
        """Build hierarchical tree of available schemas"""
        schema_tree = {}
        
        for root, dirs, files in os.walk(LITERATURE_DIR):
            for file in files:
                if file.endswith('_raw.yml'):
                    # Get relative path from literature dir
                    rel_path = os.path.relpath(root, LITERATURE_DIR)
                    category = rel_path.replace('/', '_').replace('\\', '_')
                    
                    if category not in schema_tree:
                        schema_tree[category] = []
                    
                    schema_info = {
                        'file': file,
                        'path': os.path.join(root, file),
                        'name': file.replace('_raw.yml', '').replace('_', ' ').title()
                    }
                    schema_tree[category].append(schema_info)
        
        return schema_tree
    
    def get_text_files(self) -> List[Dict]:
        """Get available text files for analysis"""
        text_files = []
        
        if os.path.exists(TEXTS_DIR):
            for file in os.listdir(TEXTS_DIR):
                if file.endswith('.txt'):
                    text_files.append({
                        'name': file,
                        'path': os.path.join(TEXTS_DIR, file),
                        'size': os.path.getsize(os.path.join(TEXTS_DIR, file))
                    })
        
        return text_files
    
    def load_schema(self, schema_path: str) -> Dict:
        """Load YAML schema file"""
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            st.error(f"Error loading schema: {e}")
            return {}
    
    def load_text(self, text_path: str) -> str:
        """Load text file for analysis"""
        try:
            with open(text_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            st.error(f"Error loading text: {e}")
            return ""
    
    def analyze_with_openai(self, schema: Dict, text_content: str, schema_name: str) -> Optional[Dict]:
        """Run OpenAI analysis using the selected schema"""
        
        # Create a simplified Pydantic model based on schema
        system_prompt = f"""
        You are an expert analyst applying the {schema_name} theoretical framework to analyze text.
        
        FRAMEWORK OVERVIEW:
        {schema.get('annotation', 'Theoretical framework for analyzing text')}
        
        ANALYSIS APPROACH:
        Extract information according to the framework's specifications, identifying:
        - Key entities and concepts defined in the framework
        - Relationships and processes described by the theory
        - Patterns that match the theoretical constructs
        - Evidence supporting or contradicting framework predictions
        
        Provide a structured analysis that captures the essential elements of this theoretical framework.
        """
        
        user_prompt = f"""
        Analyze this text using the {schema_name} framework:
        
        TEXT TO ANALYZE:
        {text_content[:8000]}  # Limit for API
        
        Provide a comprehensive analysis structured according to the framework's key concepts and relationships.
        """
        
        try:
            response = client.chat.completions.create(
                model=os.getenv('OPENAI_MODEL', 'gpt-4o-2024-08-06'),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            # Parse the JSON response
            analysis_result = json.loads(response.choices[0].message.content)
            
            # Add metadata
            analysis_result['_metadata'] = {
                'schema_used': schema_name,
                'schema_citation': schema.get('citation', 'Unknown'),
                'analysis_timestamp': datetime.now().isoformat(),
                'text_length': len(text_content),
                'model_used': os.getenv('OPENAI_MODEL', 'gpt-4o-2024-08-06')
            }
            
            return analysis_result
            
        except Exception as e:
            st.error(f"Error calling OpenAI API: {e}")
            return None
    
    def save_results(self, results: Dict, schema_name: str, text_name: str) -> str:
        """Save analysis results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{schema_name}_{text_name}_{timestamp}.json"
        filepath = os.path.join(RESULTS_DIR, filename)
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)
        
        return filepath
    
    def load_previous_results(self) -> List[Dict]:
        """Load previous analysis results"""
        results = []
        
        if os.path.exists(RESULTS_DIR):
            for file in os.listdir(RESULTS_DIR):
                if file.endswith('.json'):
                    try:
                        with open(os.path.join(RESULTS_DIR, file), 'r') as f:
                            data = json.load(f)
                            data['filename'] = file
                            results.append(data)
                    except Exception as e:
                        st.warning(f"Could not load {file}: {e}")
        
        return results

def main():
    st.set_page_config(
        page_title="Schema Analysis Pipeline",
        page_icon="🔬",
        layout="wide"
    )
    
    st.title("🔬 Schema Analysis Pipeline")
    st.markdown("Apply theoretical frameworks to analyze texts using AI")
    
    # Initialize the UI
    ui = SchemaAnalysisUI()
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    mode = st.sidebar.radio(
        "Select Mode:",
        ["New Analysis", "Browse Results", "Chat with Results"]
    )
    
    if mode == "New Analysis":
        run_new_analysis(ui)
    elif mode == "Browse Results":
        browse_results(ui)
    elif mode == "Chat with Results":
        chat_with_results(ui)

def run_new_analysis(ui: SchemaAnalysisUI):
    """Run a new schema analysis"""
    
    st.header("🆕 New Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. Select Theoretical Framework")
        
        # Schema category selection
        categories = list(ui.schema_tree.keys())
        if not categories:
            st.error("No schemas found in literature directory")
            return
        
        selected_category = st.selectbox(
            "Framework Category:",
            categories,
            format_func=lambda x: x.replace('_', ' ').title()
        )
        
        # Schema selection within category
        schemas_in_category = ui.schema_tree[selected_category]
        if not schemas_in_category:
            st.error(f"No schemas found in {selected_category}")
            return
        
        selected_schema_info = st.selectbox(
            "Specific Framework:",
            schemas_in_category,
            format_func=lambda x: x['name']
        )
        
        # Load and display schema info
        schema = ui.load_schema(selected_schema_info['path'])
        if schema:
            st.success(f"✅ Loaded: {schema.get('citation', 'Unknown citation')}")
            
            with st.expander("Framework Details"):
                st.write("**Annotation:**", schema.get('annotation', 'No description available'))
                st.write("**Model Type:**", schema.get('model_type', 'Unknown'))
                st.write("**Rationale:**", schema.get('rationale', 'No rationale provided'))
    
    with col2:
        st.subheader("2. Select Text to Analyze")
        
        if not ui.text_files:
            st.error("No text files found in texts directory")
            return
        
        selected_text_info = st.selectbox(
            "Text File:",
            ui.text_files,
            format_func=lambda x: f"{x['name']} ({x['size']} bytes)"
        )
        
        # Load and preview text
        text_content = ui.load_text(selected_text_info['path'])
        if text_content:
            st.success(f"✅ Loaded: {len(text_content)} characters")
            
            with st.expander("Text Preview"):
                st.text_area("Preview:", text_content[:1000] + "..." if len(text_content) > 1000 else text_content, height=200)
    
    # Analysis section
    st.subheader("3. Run Analysis")
    
    if st.button("🚀 Analyze Text", type="primary"):
        if schema and text_content:
            with st.spinner("Running AI analysis..."):
                results = ui.analyze_with_openai(
                    schema, 
                    text_content, 
                    selected_schema_info['name']
                )
                
                if results:
                    # Save results
                    filepath = ui.save_results(
                        results, 
                        selected_schema_info['name'].replace(' ', '_'),
                        selected_text_info['name'].replace('.txt', '')
                    )
                    
                    st.success(f"✅ Analysis complete! Results saved to: {filepath}")
                    
                    # Display results
                    display_analysis_results(results)
                else:
                    st.error("Analysis failed")

def display_analysis_results(results: Dict):
    """Display analysis results in a structured format with visualizations"""
    
    st.subheader("📊 Analysis Results")
    
    # Metadata
    if '_metadata' in results:
        metadata = results['_metadata']
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Schema Used", metadata.get('schema_used', 'Unknown'))
        with col2:
            st.metric("Text Length", f"{metadata.get('text_length', 0):,} chars")
        with col3:
            st.metric("Model", metadata.get('model_used', 'Unknown'))
        with col4:
            schema_type = detect_schema_type(results)
            st.metric("Framework Type", schema_type)
        
        st.caption(f"Analysis completed: {metadata.get('analysis_timestamp', 'Unknown time')}")
    
    # Main results
    main_results = {k: v for k, v in results.items() if not k.startswith('_')}
    
    # Create main tabs
    if main_results:
        tab_names = ["📈 Visualizations", "📋 Data Tables", "🕸️ Network View", "🔍 Raw Data"]
        main_tabs = st.tabs(tab_names)
        
        with main_tabs[0]:  # Visualizations
            create_visualizations(main_results, results)
        
        with main_tabs[1]:  # Data Tables
            display_data_tables(main_results)
        
        with main_tabs[2]:  # Network View
            create_network_visualization(main_results, results)
        
        with main_tabs[3]:  # Raw Data
            display_raw_data(main_results)

def detect_schema_type(results: Dict) -> str:
    """Detect what type of schema/framework was used based on result structure"""
    
    keys = list(results.keys())
    
    # Information Disorder framework
    if 'agents' in keys and 'messages' in keys and 'interpreters' in keys:
        return "Information Disorder"
    
    # Argumentation frameworks
    if any(k in keys for k in ['arguments', 'claims', 'premises', 'conclusions']):
        return "Argumentation"
    
    # Behavior Change frameworks
    if any(k in keys for k in ['behavior_change_techniques', 'interventions', 'barriers']):
        return "Behavior Change"
    
    # Memetic/Cultural Evolution
    if any(k in keys for k in ['memes', 'replication', 'transmission', 'selection']):
        return "Cultural Evolution"
    
    # Action Theory
    if any(k in keys for k in ['metatheories', 'action_drivers', 'needs']):
        return "Action Theory"
    
    # Generic framework
    return "Generic Framework"

def create_visualizations(main_results: Dict, full_results: Dict):
    """Create dynamic visualizations based on the analysis results"""
    
    st.subheader("🎯 Key Insights Visualizations")
    
    # Create different visualizations based on detected framework type
    schema_type = detect_schema_type(full_results)
    
    if schema_type == "Information Disorder":
        create_info_disorder_charts(main_results)
    elif schema_type == "Argumentation":
        create_argumentation_charts(main_results)
    elif schema_type == "Behavior Change":
        create_behavior_change_charts(main_results)
    elif schema_type == "Cultural Evolution":
        create_memetic_charts(main_results)
    else:
        create_generic_charts(main_results)

def create_info_disorder_charts(results: Dict):
    """Create visualizations for Information Disorder framework"""
    
    # Agent Types Distribution
    if 'agents' in results and results['agents']:
        agents_df = pd.DataFrame(results['agents'])
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'type' in agents_df.columns:
                agent_counts = agents_df['type'].value_counts()
                fig = px.pie(values=agent_counts.values, names=agent_counts.index,
                           title="Distribution of Agent Types")
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'motivations' in agents_df.columns:
                # Flatten motivations and count
                all_motivations = []
                for motivations in agents_df['motivations']:
                    if isinstance(motivations, list):
                        all_motivations.extend(motivations)
                
                if all_motivations:
                    motivation_counts = pd.Series(all_motivations).value_counts().head(10)
                    fig = px.bar(x=motivation_counts.values, y=motivation_counts.index,
                               orientation='h', title="Top Agent Motivations")
                    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
                    st.plotly_chart(fig, use_container_width=True)
    
    # Information Types Analysis
    if 'messages' in results and results['messages']:
        messages_df = pd.DataFrame(results['messages'])
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'information_type' in messages_df.columns:
                info_types = messages_df['information_type'].value_counts()
                fig = px.bar(x=info_types.index, y=info_types.values,
                           title="Information Types Distribution",
                           color=info_types.values,
                           color_continuous_scale="Viridis")
                fig.update_xaxes(tickangle=45)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'credibility_indicators' in messages_df.columns:
                # Count credibility indicators
                all_indicators = []
                for indicators in messages_df['credibility_indicators']:
                    if isinstance(indicators, list):
                        all_indicators.extend(indicators)
                
                if all_indicators:
                    indicator_counts = pd.Series(all_indicators).value_counts().head(8)
                    fig = px.scatter(x=range(len(indicator_counts)), y=indicator_counts.values,
                                   size=indicator_counts.values, hover_name=indicator_counts.index,
                                   title="Credibility Indicators Frequency")
                    st.plotly_chart(fig, use_container_width=True)
    
    # Interpretation Modes
    if 'interpreters' in results and results['interpreters']:
        interpreters_df = pd.DataFrame(results['interpreters'])
        
        if 'likely_interpretation_mode' in interpreters_df.columns:
            mode_counts = interpreters_df['likely_interpretation_mode'].value_counts()
            fig = px.funnel(y=mode_counts.index, x=mode_counts.values,
                          title="Interpretation Modes Distribution")
            st.plotly_chart(fig, use_container_width=True)

def create_argumentation_charts(results: Dict):
    """Create visualizations for Argumentation frameworks"""
    
    # Look for common argumentation structures
    arg_keys = ['arguments', 'claims', 'premises', 'conclusions', 'evidence', 'rebuttals']
    found_keys = [k for k in arg_keys if k in results]
    
    if found_keys:
        col1, col2 = st.columns(2)
        
        with col1:
            # Count elements by type
            element_counts = {}
            for key in found_keys:
                if isinstance(results[key], list):
                    element_counts[key.title()] = len(results[key])
            
            if element_counts:
                fig = px.bar(x=list(element_counts.keys()), y=list(element_counts.values()),
                           title="Argument Structure Elements",
                           color=list(element_counts.values()),
                           color_continuous_scale="Blues")
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Argument strength or quality metrics if available
            if 'arguments' in results and results['arguments']:
                args_df = pd.DataFrame(results['arguments'])
                
                if 'strength' in args_df.columns or 'quality' in args_df.columns:
                    strength_col = 'strength' if 'strength' in args_df.columns else 'quality'
                    fig = px.histogram(args_df, x=strength_col, 
                                     title=f"Distribution of Argument {strength_col.title()}",
                                     nbins=10)
                    st.plotly_chart(fig, use_container_width=True)

def create_behavior_change_charts(results: Dict):
    """Create visualizations for Behavior Change frameworks"""
    
    # BCT categories, intervention types, etc.
    if 'behavior_change_techniques' in results:
        bct_data = results['behavior_change_techniques']
        if isinstance(bct_data, list) and bct_data:
            bct_df = pd.DataFrame(bct_data)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if 'category' in bct_df.columns:
                    category_counts = bct_df['category'].value_counts()
                    fig = px.treemap(names=category_counts.index, values=category_counts.values,
                                   title="BCT Categories Distribution")
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                if 'effectiveness' in bct_df.columns:
                    fig = px.box(bct_df, y='effectiveness', title="BCT Effectiveness Distribution")
                    st.plotly_chart(fig, use_container_width=True)
    
    # Intervention characteristics
    if 'interventions' in results and results['interventions']:
        interventions_df = pd.DataFrame(results['interventions'])
        
        if 'target_behavior' in interventions_df.columns:
            behavior_counts = interventions_df['target_behavior'].value_counts()
            fig = px.pie(values=behavior_counts.values, names=behavior_counts.index,
                       title="Target Behaviors")
            st.plotly_chart(fig, use_container_width=True)

def create_memetic_charts(results: Dict):
    """Create visualizations for Cultural Evolution/Memetic frameworks"""
    
    # Meme transmission, selection criteria, etc.
    if 'memes' in results and results['memes']:
        memes_df = pd.DataFrame(results['memes'])
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'fitness_score' in memes_df.columns:
                fig = px.histogram(memes_df, x='fitness_score', 
                                 title="Meme Fitness Distribution",
                                 nbins=15)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'transmission_rate' in memes_df.columns:
                fig = px.scatter(memes_df, x='fitness_score', y='transmission_rate',
                               title="Fitness vs Transmission Rate",
                               hover_data=['content'] if 'content' in memes_df.columns else None)
                st.plotly_chart(fig, use_container_width=True)
    
    # Selection criteria analysis
    if 'selection_criteria' in results:
        criteria_data = results['selection_criteria']
        if isinstance(criteria_data, list):
            criteria_df = pd.DataFrame(criteria_data)
            
            if 'strength' in criteria_df.columns and 'criterion_type' in criteria_df.columns:
                fig = px.violin(criteria_df, y='strength', x='criterion_type',
                              title="Selection Criteria Strength by Type")
                fig.update_xaxes(tickangle=45)
                st.plotly_chart(fig, use_container_width=True)

def create_generic_charts(results: Dict):
    """Create generic visualizations for any framework"""
    
    st.info("📊 Generating generic visualizations based on detected data patterns...")
    
    # Count different data types
    data_summary = {}
    for key, value in results.items():
        if isinstance(value, list):
            data_summary[key] = len(value)
        elif isinstance(value, dict):
            data_summary[key] = len(value.keys())
        elif isinstance(value, str):
            data_summary[key] = len(value.split())
    
    if data_summary:
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(x=list(data_summary.keys()), y=list(data_summary.values()),
                       title="Data Elements by Category",
                       color=list(data_summary.values()),
                       color_continuous_scale="Plasma")
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Word cloud-style frequency for text fields
            text_lengths = {}
            for key, value in results.items():
                if isinstance(value, str) and len(value) > 50:
                    text_lengths[key] = len(value)
            
            if text_lengths:
                fig = px.pie(values=list(text_lengths.values()), names=list(text_lengths.keys()),
                           title="Text Content Distribution")
                st.plotly_chart(fig, use_container_width=True)

def create_network_visualization(main_results: Dict, full_results: Dict):
    """Create network graph visualizations"""
    
    st.subheader("🕸️ Relationship Network")
    
    # Create network based on detected relationships
    G = nx.Graph()
    
    schema_type = detect_schema_type(full_results)
    
    if schema_type == "Information Disorder":
        create_info_disorder_network(G, main_results)
    elif schema_type == "Argumentation":
        create_argumentation_network(G, main_results)
    else:
        create_generic_network(G, main_results)
    
    if G.nodes():
        plot_network_graph(G)
    else:
        st.info("No relationship data available for network visualization")

def create_info_disorder_network(G: nx.Graph, results: Dict):
    """Create network for Information Disorder framework"""
    
    # Add agents as nodes
    if 'agents' in results:
        for agent in results['agents']:
            if isinstance(agent, dict) and 'name' in agent:
                G.add_node(agent['name'], 
                          node_type='agent',
                          agent_type=agent.get('type', 'unknown'),
                          size=10)
    
    # Add messages as nodes
    if 'messages' in results:
        for i, message in enumerate(results['messages']):
            if isinstance(message, dict):
                msg_id = f"Message_{i+1}"
                G.add_node(msg_id,
                          node_type='message',
                          info_type=message.get('information_type', 'unknown'),
                          size=8)
                
                # Connect to source if available
                if 'source' in message:
                    source = message['source']
                    if source in G.nodes():
                        G.add_edge(source, msg_id, edge_type='creates')
    
    # Add interpreters as nodes
    if 'interpreters' in results:
        for interpreter in results['interpreters']:
            if isinstance(interpreter, dict) and 'audience_type' in interpreter:
                G.add_node(interpreter['audience_type'],
                          node_type='interpreter',
                          interpretation_mode=interpreter.get('likely_interpretation_mode', 'unknown'),
                          size=6)

def create_argumentation_network(G: nx.Graph, results: Dict):
    """Create network for Argumentation frameworks"""
    
    # Add claims/arguments as nodes
    if 'claims' in results:
        for i, claim in enumerate(results['claims']):
            claim_id = f"Claim_{i+1}"
            if isinstance(claim, dict):
                G.add_node(claim_id, 
                          node_type='claim',
                          content=str(claim.get('content', ''))[:50],
                          size=8)
            else:
                G.add_node(claim_id, node_type='claim', content=str(claim)[:50], size=8)
    
    # Add evidence nodes and connect to claims
    if 'evidence' in results:
        for i, evidence in enumerate(results['evidence']):
            ev_id = f"Evidence_{i+1}"
            G.add_node(ev_id, node_type='evidence', size=6)
            
            # Connect evidence to relevant claims (simplified)
            claim_nodes = [n for n in G.nodes() if G.nodes[n].get('node_type') == 'claim']
            if claim_nodes and i < len(claim_nodes):
                G.add_edge(ev_id, claim_nodes[i], edge_type='supports')

def create_generic_network(G: nx.Graph, results: Dict):
    """Create generic network from any structured data"""
    
    # Find list-type data that could represent entities
    for key, value in results.items():
        if isinstance(value, list) and value:
            for i, item in enumerate(value[:10]):  # Limit to avoid overcrowding
                if isinstance(item, dict):
                    # Use first string value as node name
                    node_name = None
                    for k, v in item.items():
                        if isinstance(v, str) and len(v) < 100:
                            node_name = f"{key}_{i}: {v[:30]}"
                            break
                    
                    if not node_name:
                        node_name = f"{key}_{i+1}"
                    
                    G.add_node(node_name, 
                              category=key,
                              node_type=key,
                              size=8)
                elif isinstance(item, str):
                    G.add_node(f"{key}_{i+1}: {item[:30]}", 
                              category=key,
                              node_type=key,
                              size=6)

def plot_network_graph(G: nx.Graph):
    """Plot network graph using plotly"""
    
    if len(G.nodes()) == 0:
        st.warning("No nodes to display in network")
        return
    
    # Calculate layout
    pos = nx.spring_layout(G, k=1, iterations=50)
    
    # Extract node information
    node_trace = go.Scatter(
        x=[pos[node][0] for node in G.nodes()],
        y=[pos[node][1] for node in G.nodes()],
        mode='markers+text',
        text=[node[:20] + "..." if len(node) > 20 else node for node in G.nodes()],
        textposition="middle center",
        hoverinfo='text',
        hovertext=[f"{node}<br>Type: {G.nodes[node].get('node_type', 'unknown')}" 
                   for node in G.nodes()],
        marker=dict(
            size=[G.nodes[node].get('size', 10) for node in G.nodes()],
            color=[hash(G.nodes[node].get('node_type', 'default')) % 10 
                   for node in G.nodes()],
            colorscale='Viridis',
            line=dict(width=2)
        )
    )
    
    # Extract edge information
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=2, color='rgba(125,125,125,0.3)'),
        hoverinfo='none',
        mode='lines'
    )
    
    # Create figure
    fig = go.Figure(data=[edge_trace, node_trace],
                   layout=go.Layout(
                       title="Relationship Network",
                       titlefont_size=16,
                       showlegend=False,
                       hovermode='closest',
                       margin=dict(b=20,l=5,r=5,t=40),
                       annotations=[ dict(
                           text="",
                           showarrow=False,
                           xref="paper", yref="paper",
                           x=0.005, y=-0.002 ) ],
                       xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       height=600
                   ))
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Network statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Nodes", len(G.nodes()))
    with col2:
        st.metric("Edges", len(G.edges()))
    with col3:
        st.metric("Density", f"{nx.density(G):.3f}")
    with col4:
        components = nx.number_connected_components(G)
        st.metric("Components", components)

def display_data_tables(main_results: Dict):
    """Display structured data tables"""
    
    st.subheader("📋 Structured Data")
    
    for key, value in main_results.items():
        with st.expander(f"📊 {key.replace('_', ' ').title()} ({type(value).__name__})"):
            if isinstance(value, list):
                if value and isinstance(value[0], dict):
                    # Convert to DataFrame for better display
                    df = pd.DataFrame(value)
                    st.dataframe(df, use_container_width=True)
                    
                    # Add download button
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label=f"Download {key}.csv",
                        data=csv,
                        file_name=f"{key}.csv",
                        mime="text/csv"
                    )
                else:
                    # Simple list
                    for i, item in enumerate(value, 1):
                        st.write(f"{i}. {item}")
            elif isinstance(value, dict):
                # Nested dictionary
                st.json(value)
            else:
                # Simple value
                st.write(value)

def display_raw_data(main_results: Dict):
    """Display raw JSON data with search functionality"""
    
    st.subheader("🔍 Raw Data Explorer")
    
    # Search functionality
    search_term = st.text_input("🔍 Search in results:", placeholder="Enter search term...")
    
    # Filter results based on search
    if search_term:
        filtered_results = {}
        for key, value in main_results.items():
            value_str = json.dumps(value, default=str).lower()
            if search_term.lower() in value_str:
                filtered_results[key] = value
        
        if filtered_results:
            st.success(f"Found {len(filtered_results)} sections containing '{search_term}'")
            st.json(filtered_results)
        else:
            st.warning(f"No results found for '{search_term}'")
    else:
        st.json(main_results)
    
    # Download raw JSON
    json_str = json.dumps(main_results, indent=2, default=str)
    st.download_button(
        label="📥 Download Raw JSON",
        data=json_str,
        file_name="analysis_results.json",
        mime="application/json"
    )

def browse_results(ui: SchemaAnalysisUI):
    """Browse previous analysis results"""
    
    st.header("📁 Browse Previous Results")
    
    previous_results = ui.load_previous_results()
    
    if not previous_results:
        st.info("No previous analysis results found")
        return
    
    # Results overview
    st.subheader(f"Found {len(previous_results)} previous analyses")
    
    # Create summary table
    summary_data = []
    for result in previous_results:
        metadata = result.get('_metadata', {})
        summary_data.append({
            'File': result['filename'],
            'Schema': metadata.get('schema_used', 'Unknown'),
            'Date': metadata.get('analysis_timestamp', 'Unknown')[:19] if metadata.get('analysis_timestamp') else 'Unknown',
            'Text Length': metadata.get('text_length', 0),
            'Model': metadata.get('model_used', 'Unknown')
        })
    
    df = pd.DataFrame(summary_data)
    st.dataframe(df)
    
    # Select result to view
    selected_result = st.selectbox(
        "Select result to view:",
        previous_results,
        format_func=lambda x: f"{x['filename']} - {x.get('_metadata', {}).get('schema_used', 'Unknown')}"
    )
    
    if selected_result:
        display_analysis_results(selected_result)

def chat_with_results(ui: SchemaAnalysisUI):
    """Chat interface for querying analysis results"""
    
    st.header("💬 Chat with Analysis Results")
    
    previous_results = ui.load_previous_results()
    
    if not previous_results:
        st.info("No analysis results available for chat. Run some analyses first!")
        return
    
    # Select result to chat about
    selected_result = st.selectbox(
        "Select analysis to discuss:",
        previous_results,
        format_func=lambda x: f"{x['filename']} - {x.get('_metadata', {}).get('schema_used', 'Unknown')}"
    )
    
    if not selected_result:
        return
    
    # Display result summary
    metadata = selected_result.get('_metadata', {})
    st.info(f"Chatting about: **{metadata.get('schema_used', 'Unknown')}** analysis")
    
    # Chat interface
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    
    # Display chat history
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask a question about the analysis results..."):
        # Add user message to chat history
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = generate_chat_response(prompt, selected_result)
                st.markdown(response)
                st.session_state.chat_messages.append({"role": "assistant", "content": response})

def generate_chat_response(question: str, analysis_result: Dict) -> str:
    """Generate AI response about the analysis results"""
    
    system_prompt = f"""
    You are an expert research assistant helping to interpret and discuss analysis results.
    
    The user has asked a question about an analysis that was performed using the following framework:
    Schema: {analysis_result.get('_metadata', {}).get('schema_used', 'Unknown')}
    Citation: {analysis_result.get('_metadata', {}).get('schema_citation', 'Unknown')}
    
    Here are the analysis results:
    {json.dumps(analysis_result, indent=2)}
    
    Please answer the user's question based on these results. Be specific and reference the actual data from the analysis.
    If the question cannot be answered from the available data, say so clearly.
    """
    
    try:
        response = client.chat.completions.create(
            model=os.getenv('OPENAI_MODEL', 'gpt-4o-2024-08-06'),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            max_tokens=1000
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error generating response: {e}"

if __name__ == "__main__":
    main()