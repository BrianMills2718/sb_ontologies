#!/usr/bin/env python3
"""
Visualize Semantic Hypergraph from Iran debate with full text labels
Uses the notation: (element/TYPE args...)
"""

import json
import networkx as nx
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Set
import re
from pathlib import Path

def parse_hyperedge(edge_str: str) -> Dict:
    """Parse a hyperedge string like '(warns/P x y z)' into components"""
    # Remove outer parentheses and clean
    edge_str = edge_str.strip()
    if edge_str.startswith('(') and edge_str.endswith(')'):
        edge_str = edge_str[1:-1]
    
    # Extract the main element and type
    parts = edge_str.split(' ', 1)
    if '/' in parts[0]:
        element, edge_type = parts[0].split('/')
    else:
        element = parts[0]
        edge_type = 'unknown'
    
    # Extract arguments if any
    args = []
    if len(parts) > 1:
        # Simple parsing - in real case would need recursive parser
        args_str = parts[1]
        # Split by spaces but respect parentheses
        depth = 0
        current_arg = []
        for char in args_str:
            if char == '(':
                depth += 1
            elif char == ')':
                depth -= 1
            elif char == ' ' and depth == 0:
                if current_arg:
                    args.append(''.join(current_arg))
                    current_arg = []
                continue
            current_arg.append(char)
        if current_arg:
            args.append(''.join(current_arg))
    
    return {
        'element': element,
        'type': edge_type,
        'args': args,
        'full': edge_str
    }

def extract_hyperedges_from_text(text: str) -> List[str]:
    """Extract hyperedge strings from the raw output text"""
    hyperedges = []
    
    # Pattern to match hyperedges: (something/TYPE ...)
    pattern = r'\([^/\s]+/[A-Z](?:\s+[^\)]+)?\)'
    
    # Also match complex ones with nested parentheses
    complex_pattern = r'\((?:[^()]|\([^()]*\))*\)'
    
    matches = re.findall(complex_pattern, text)
    
    for match in matches:
        if '/' in match and any(t in match for t in ['/C', '/P', '/B', '/T', '/M', '/J', '/R', '/S']):
            hyperedges.append(match)
    
    return hyperedges

def create_hypergraph_network(hyperedges: List[str]) -> nx.DiGraph:
    """Create a NetworkX graph from hyperedges"""
    g = nx.DiGraph()
    
    # Parse all hyperedges
    parsed_edges = []
    for edge_str in hyperedges:
        parsed = parse_hyperedge(edge_str)
        if parsed['element']:
            parsed_edges.append(parsed)
    
    # Create nodes and edges
    node_id = 0
    edge_to_node = {}  # Map edge strings to node IDs
    
    for parsed in parsed_edges:
        # Create node for this hyperedge
        node_label = f"{parsed['element']}/{parsed['type']}"
        
        # For predicates and relations, include more context
        if parsed['type'] in ['P', 'R']:
            node_label = parsed['full'][:50] + '...' if len(parsed['full']) > 50 else parsed['full']
        
        # Add node
        g.add_node(node_id, 
                  label=node_label,
                  element=parsed['element'],
                  type=parsed['type'],
                  full_edge=parsed['full'])
        
        edge_to_node[parsed['full']] = node_id
        node_id += 1
    
    # Second pass: create connections between nodes
    for i, parsed in enumerate(parsed_edges):
        source_id = i
        
        # Connect to any referenced nodes in arguments
        for arg in parsed['args']:
            # Check if this argument is another hyperedge
            for j, other_parsed in enumerate(parsed_edges):
                if i != j and (
                    arg == other_parsed['full'] or 
                    arg == f"{other_parsed['element']}/{other_parsed['type']}" or
                    other_parsed['full'] in arg
                ):
                    g.add_edge(source_id, j)
    
    return g

def create_readable_hypergraph(json_path: str) -> Tuple[nx.DiGraph, Dict]:
    """Create a readable hypergraph visualization from Iran debate results"""
    
    # Load the results
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # Get the full response text
    full_text = data.get('full_response', '')
    
    # Extract hyperedges
    hyperedges = extract_hyperedges_from_text(full_text)
    
    # Create focused graph with key statements
    g = nx.DiGraph()
    
    # Extract key statements from the structured analysis
    key_statements = [
        {
            'id': 'stmt1',
            'label': 'U.S. intel: Iran not in weapons research',
            'full': '((consistently/M assessed/P) (+/B u.s./C intelligence/C) ((not/M engaged/P) iran/C (in/T (+/B weapons/C research/C))))',
            'type': 'main_claim',
            'actors': ['U.S. Intelligence'],
            'objects': ['Iran', 'weapons research']
        },
        {
            'id': 'stmt2', 
            'label': 'Bret Stephens applauds Trump strikes',
            'full': '(applauds/P (+/B bret/C stephens/C) (of/B (+/B president/C trump/C) (+/B strikes/C (in/T iran/C))))',
            'type': 'policy_position',
            'actors': ['Bret Stephens'],
            'objects': ['Trump', 'strikes in Iran']
        },
        {
            'id': 'stmt3',
            'label': 'Kelanic warns U.S. against strikes',
            'full': '(warns/P (+/B rosemary/C kelanic/C) (+/B united/C states/C) (against/T (strike/P iran/C)))',
            'type': 'policy_position',
            'actors': ['Rosemary Kelanic'],
            'objects': ['United States', 'Iran']
        },
        {
            'id': 'stmt4',
            'label': 'Netanyahu 1992: Iran years from bomb',
            'full': '(warned/P (+/B benjamin/C netanyahu/C) (+/B israeli/C knesset/C) (in/T 1992/C) (be/P iran/C (+/B few/M years/C (from/T (+/B nuclear/C bomb/C)))))',
            'type': 'historical',
            'actors': ['Netanyahu'],
            'objects': ['Israeli Knesset', 'Iran', 'nuclear bomb']
        }
    ]
    
    # Add nodes for statements
    for stmt in key_statements:
        g.add_node(stmt['id'], 
                  label=stmt['label'],
                  hyperedge=stmt['full'],
                  node_type=stmt['type'])
        
        # Add actor nodes
        for actor in stmt['actors']:
            actor_id = f"actor_{actor.replace(' ', '_')}"
            if not g.has_node(actor_id):
                g.add_node(actor_id, label=actor, node_type='actor')
            g.add_edge(actor_id, stmt['id'], relation='makes_claim')
        
        # Add key object nodes
        for obj in stmt['objects']:
            if 'Iran' in obj or 'nuclear' in obj or 'weapons' in obj:
                obj_id = f"obj_{obj.replace(' ', '_')}"
                if not g.has_node(obj_id):
                    g.add_node(obj_id, label=obj, node_type='object')
                g.add_edge(stmt['id'], obj_id, relation='about')
    
    # Add connections between related statements
    # Stephens vs Kelanic (opposing positions)
    g.add_edge('stmt2', 'stmt3', relation='opposes')
    
    # Intel assessment relates to nuclear claims
    g.add_edge('stmt1', 'stmt4', relation='contradicts')
    
    return g, key_statements

def plot_hypergraph(g: nx.DiGraph, title: str = "Iran Debate: Semantic Hypergraph"):
    """Plot the hypergraph with readable labels"""
    
    plt.figure(figsize=(16, 12))
    
    # Create hierarchical layout
    pos = nx.spring_layout(g, k=4, iterations=100, seed=42)
    
    # Adjust positions by node type
    node_types = nx.get_node_attributes(g, 'node_type')
    for node, (x, y) in pos.items():
        if node_types.get(node) == 'actor':
            pos[node] = (x - 0.3, y + 0.4)  # Actors on left and up
        elif node_types.get(node) == 'object':
            pos[node] = (x + 0.3, y - 0.3)  # Objects on right and down
    
    # Color scheme
    color_map = {
        'actor': '#2E7D32',  # Dark green
        'main_claim': '#1565C0',  # Dark blue
        'policy_position': '#F57C00',  # Dark orange
        'historical': '#6A1B9A',  # Dark purple
        'object': '#D32F2F'  # Dark red
    }
    
    node_colors = []
    node_sizes = []
    for node in g.nodes():
        node_type = node_types.get(node, 'default')
        node_colors.append(color_map.get(node_type, '#757575'))
        if node_type == 'actor':
            node_sizes.append(2500)
        elif node_type == 'object':
            node_sizes.append(2000)
        else:
            node_sizes.append(4000)
    
    # Draw nodes
    nx.draw_networkx_nodes(g, pos, node_color=node_colors, node_size=node_sizes, 
                          alpha=0.85, linewidths=2, edgecolors='black')
    
    # Draw edges with different styles
    edge_types = nx.get_edge_attributes(g, 'relation')
    
    # Group edges by type
    claim_edges = [(u,v) for (u,v), t in edge_types.items() if t == 'makes_claim']
    about_edges = [(u,v) for (u,v), t in edge_types.items() if t == 'about']
    relation_edges = [(u,v) for (u,v), t in edge_types.items() if t in ['opposes', 'contradicts']]
    
    # Draw different edge types
    nx.draw_networkx_edges(g, pos, claim_edges, edge_color='green', 
                          arrows=True, arrowsize=20, width=2, alpha=0.7, style='solid')
    nx.draw_networkx_edges(g, pos, about_edges, edge_color='blue',
                          arrows=True, arrowsize=20, width=2, alpha=0.7, style='dashed')
    nx.draw_networkx_edges(g, pos, relation_edges, edge_color='red',
                          arrows=True, arrowsize=20, width=3, alpha=0.8, style='dotted')
    
    # Node labels with text wrapping
    labels = nx.get_node_attributes(g, 'label')
    wrapped_labels = {}
    
    for node, label in labels.items():
        # Wrap long labels
        if len(label) > 30:
            words = label.split()
            lines = []
            current_line = []
            current_length = 0
            
            for word in words:
                if current_length + len(word) > 30:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                    current_length = len(word)
                else:
                    current_line.append(word)
                    current_length += len(word) + 1
            
            if current_line:
                lines.append(' '.join(current_line))
            
            wrapped_labels[node] = '\n'.join(lines)
        else:
            wrapped_labels[node] = label
    
    nx.draw_networkx_labels(g, pos, wrapped_labels, font_size=10, font_weight='bold')
    
    # Edge labels
    edge_labels = {
        **{e: 'claims' for e in claim_edges},
        **{e: 'about' for e in about_edges},
        **{e: edge_types[e] for e in relation_edges}
    }
    nx.draw_networkx_edge_labels(g, pos, edge_labels, font_size=9, 
                               font_color='darkred', font_weight='bold')
    
    # Add hyperedge notation examples
    ax = plt.gca()
    examples = [
        "Hyperedge Examples:",
        "(+/B u.s./C intelligence/C) = 'U.S. Intelligence'",
        "((not/M engaged/P) iran/C ...) = 'Iran not engaged in...'",
        "(against/T (strike/P iran/C)) = 'against striking Iran'"
    ]
    
    y_pos = 0.95
    for example in examples:
        ax.text(0.02, y_pos, example, transform=ax.transAxes,
               fontsize=9, fontfamily='monospace',
               bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", alpha=0.8))
        y_pos -= 0.05
    
    # Legend
    legend_elements = [
        plt.scatter([], [], c='#2E7D32', s=200, label='Actor/Source', edgecolors='black', linewidths=2),
        plt.scatter([], [], c='#1565C0', s=200, label='Intelligence Claim', edgecolors='black', linewidths=2),
        plt.scatter([], [], c='#F57C00', s=200, label='Policy Position', edgecolors='black', linewidths=2),
        plt.scatter([], [], c='#6A1B9A', s=200, label='Historical Claim', edgecolors='black', linewidths=2),
        plt.scatter([], [], c='#D32F2F', s=200, label='Object/Topic', edgecolors='black', linewidths=2)
    ]
    plt.legend(handles=legend_elements, loc='upper right', frameon=True, 
              fancybox=True, shadow=True)
    
    plt.title(title, fontsize=18, fontweight='bold', pad=20)
    plt.axis('off')
    plt.tight_layout()
    
    return plt.gcf()

def print_hyperedge_details(statements: List[Dict]):
    """Print the full hyperedge notation for reference"""
    print("\n" + "="*80)
    print("SEMANTIC HYPERGRAPH NOTATION DETAILS")
    print("="*80)
    
    for stmt in statements:
        print(f"\n{stmt['label']}:")
        print(f"Full hyperedge: {stmt['full']}")
        print(f"Type: {stmt['type']}")
        print(f"Actors: {', '.join(stmt['actors'])}")
        print(f"Objects: {', '.join(stmt['objects'])}")
        print("-"*60)

def main():
    # Load and visualize
    json_path = "/home/brian/lit_review/results/iran_debate_hypergraph.json"
    
    g, statements = create_readable_hypergraph(json_path)
    
    # Plot
    fig = plot_hypergraph(g, title="Iran Nuclear Debate: Semantic Hypergraph Visualization")
    
    # Save
    output_path = "/home/brian/lit_review/results/iran_debate_hypergraph_viz.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Saved visualization to {output_path}")
    
    # Also save as PDF for better quality
    pdf_path = "/home/brian/lit_review/results/iran_debate_hypergraph_viz.pdf"
    plt.savefig(pdf_path, format='pdf', bbox_inches='tight', facecolor='white')
    print(f"Saved PDF version to {pdf_path}")
    
    # Print details
    print_hyperedge_details(statements)
    
    plt.show()

if __name__ == "__main__":
    main()