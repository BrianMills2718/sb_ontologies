#!/usr/bin/env python3
"""
Visualize Semantic Hypergraph instances with human-readable labels
Enhanced version with string substitution for IDs
"""

import yaml
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
from typing import Dict, List, Tuple, Set
import argparse
from pathlib import Path

def load_sh_instance(yaml_path: str) -> Dict:
    """Load SH instance from YAML file"""
    with open(yaml_path, 'r') as f:
        return yaml.safe_load(f)

def create_readable_labels(instance: Dict) -> Dict[str, str]:
    """Create human-readable labels for all IDs"""
    labels = {}
    
    # Map atoms to readable labels
    for atom in instance['instance']['atoms']:
        atom_id = atom['id']
        term = atom['term']
        atom_type = atom['type']
        
        # Clean up the term
        if term.startswith('num_'):
            # Convert num_56259 to 56,259
            num_str = term[4:]
            if num_str.isdigit():
                term = f"{int(num_str):,}"
        elif term == 'unspecified_agent':
            term = '[someone]'
        elif '_' in term:
            # Convert spain_pm_sanchez to "Spain PM Sanchez"
            term = ' '.join(word.capitalize() for word in term.split('_'))
        
        # Add type suffix only for non-concepts
        if atom_type != 'C':
            type_map = {'P': '(action)', 'M': '(mod)', 'T': '(where)', 'B': '(and)'}
            term = f"{term}{type_map.get(atom_type, '')}"
            
        labels[atom_id] = term
    
    # Map hyperedges to readable descriptions
    for he in instance['instance']['hyperedges']:
        he_id = he['id']
        connector_id = he['connector_id']
        connector_label = labels.get(connector_id, connector_id)
        
        # Build a description of the hyperedge
        args = []
        for arg_id in he['arguments']:
            if arg_id in labels:
                args.append(labels[arg_id])
            elif arg_id.startswith('h'):
                # It's a nested hyperedge - we'll update this later
                args.append(f"[{arg_id}]")
            else:
                args.append(arg_id)
        
        # Format based on connector type
        if 'say' in connector_label or 'allege' in connector_label:
            if len(args) >= 2:
                labels[he_id] = f"{args[0]} says: {' '.join(args[1:])}"
            else:
                labels[he_id] = f"{connector_label}: {' '.join(args)}"
        elif 'kill' in connector_label:
            if len(args) >= 2:
                labels[he_id] = f"{args[0]} killed {args[1]}"
            else:
                labels[he_id] = f"killed: {' '.join(args)}"
        elif 'describe' in connector_label:
            if len(args) >= 3:
                labels[he_id] = f"{args[0]} calls {args[1]} '{args[2]}'"
            else:
                labels[he_id] = f"{connector_label}: {' '.join(args)}"
        elif 'condemn' in connector_label:
            if len(args) >= 2:
                labels[he_id] = f"{args[0]} condemns {args[1]}"
            else:
                labels[he_id] = f"{connector_label}: {' '.join(args)}"
        else:
            labels[he_id] = f"{connector_label}({', '.join(args)})"
    
    # Second pass to resolve nested hyperedge references
    for he in instance['instance']['hyperedges']:
        he_id = he['id']
        current_label = labels[he_id]
        
        # Replace any [hX] references with actual descriptions
        for other_he_id, other_label in labels.items():
            if other_he_id.startswith('h') and f"[{other_he_id}]" in current_label:
                current_label = current_label.replace(f"[{other_he_id}]", f'"{other_label}"')
        
        labels[he_id] = current_label
    
    return labels

def create_readable_visualization(instance: Dict, title: str = "Semantic Hypergraph"):
    """Create a single, readable visualization of the main claims"""
    g = nx.DiGraph()
    labels_map = create_readable_labels(instance)
    
    # Focus on main claim structures
    main_claims = []
    sub_claims = []
    
    for he in instance['instance']['hyperedges']:
        he_id = he['id']
        he_label = labels_map.get(he_id, he_id)
        
        # Identify claim types
        connector = next((a for a in instance['instance']['atoms'] if a['id'] == he['connector_id']), None)
        if connector:
            if connector['term'] in ['say', 'allege', 'describe', 'condemn']:
                main_claims.append((he, he_label))
            elif connector['term'] in ['kill']:
                sub_claims.append((he, he_label))
    
    # Build the graph
    claim_nodes = []
    
    # Add main claims as nodes
    for he, label in main_claims:
        he_id = he['id']
        g.add_node(he_id, label=label, node_type='main_claim')
        claim_nodes.append(he_id)
        
        # Add actor
        if he['arguments']:
            actor_id = he['arguments'][0]
            actor_label = labels_map.get(actor_id, actor_id)
            g.add_node(actor_id, label=actor_label, node_type='actor')
            g.add_edge(actor_id, he_id, label='claims')
    
    # Add sub-claims
    for he, label in sub_claims:
        he_id = he['id']
        g.add_node(he_id, label=label, node_type='sub_claim')
        
        # Find which main claims reference this sub-claim
        for main_he, _ in main_claims:
            if he_id in main_he['arguments']:
                g.add_edge(main_he['id'], he_id, label='about')
    
    # Add the main AND node if it exists
    main_he_id = instance['instance'].get('main_hyperedge')
    if main_he_id:
        main_label = labels_map.get(main_he_id, 'All statements')
        g.add_node(main_he_id, label=main_label, node_type='conjunction')
        
        # Connect to all top-level claims
        for node in g.nodes():
            if g.nodes[node].get('node_type') == 'main_claim' and g.in_degree(node) <= 1:
                g.add_edge(main_he_id, node, label='includes')
    
    return g, labels_map

def plot_readable_graph(g: nx.DiGraph, title: str = "News Claims Structure"):
    """Plot the graph with readable labels"""
    plt.figure(figsize=(14, 10))
    
    # Layout
    pos = nx.spring_layout(g, k=3, iterations=50, seed=42)
    
    # Adjust positions to create hierarchy
    node_types = nx.get_node_attributes(g, 'node_type')
    for node, (x, y) in pos.items():
        if node_types.get(node) == 'actor':
            pos[node] = (x, y + 0.3)  # Move actors up
        elif node_types.get(node) == 'sub_claim':
            pos[node] = (x, y - 0.3)  # Move sub-claims down
    
    # Node colors and sizes
    color_map = {
        'actor': '#4CAF50',  # Green
        'main_claim': '#2196F3',  # Blue
        'sub_claim': '#FFC107',  # Amber
        'conjunction': '#9C27B0'  # Purple
    }
    
    node_colors = [color_map.get(node_types.get(node, 'default'), '#757575') for node in g.nodes()]
    node_sizes = [2000 if node_types.get(node) == 'actor' else 3000 for node in g.nodes()]
    
    # Draw nodes
    nx.draw_networkx_nodes(g, pos, node_color=node_colors, node_size=node_sizes, alpha=0.9)
    
    # Draw edges
    nx.draw_networkx_edges(g, pos, edge_color='gray', arrows=True, 
                          arrowsize=20, arrowstyle='->', width=2, alpha=0.6)
    
    # Node labels with wrapping
    labels = nx.get_node_attributes(g, 'label')
    wrapped_labels = {}
    for node, label in labels.items():
        # Wrap long labels
        if len(label) > 40:
            words = label.split()
            lines = []
            current_line = []
            current_length = 0
            
            for word in words:
                if current_length + len(word) > 40:
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
    
    nx.draw_networkx_labels(g, pos, wrapped_labels, font_size=9, font_weight='bold')
    
    # Edge labels
    edge_labels = nx.get_edge_attributes(g, 'label')
    nx.draw_networkx_edge_labels(g, pos, edge_labels, font_size=8, font_color='red')
    
    # Legend
    legend_elements = [
        plt.scatter([], [], c='#4CAF50', s=200, label='Actor/Source'),
        plt.scatter([], [], c='#2196F3', s=200, label='Main Claim'),
        plt.scatter([], [], c='#FFC107', s=200, label='Sub-claim/Event'),
        plt.scatter([], [], c='#9C27B0', s=200, label='All Statements')
    ]
    plt.legend(handles=legend_elements, loc='upper left', frameon=True, fancybox=True)
    
    plt.title(title, fontsize=16, fontweight='bold')
    plt.axis('off')
    plt.tight_layout()
    
    return plt.gcf()

def main():
    parser = argparse.ArgumentParser(description='Visualize SH with readable labels')
    parser.add_argument('yaml_file', help='Path to SH instance YAML file')
    parser.add_argument('--output', '-o', help='Output image file')
    
    args = parser.parse_args()
    
    # Load instance
    instance = load_sh_instance(args.yaml_file)
    
    # Create readable visualization
    g, labels_map = create_readable_visualization(instance)
    
    # Plot
    fig = plot_readable_graph(g, title="Ground News: Gaza Conflict Claims Structure")
    
    if args.output:
        plt.savefig(args.output, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"Saved readable visualization to {args.output}")
    else:
        plt.show()
    
    # Also print the claim structure in text
    print("\nCLAIM STRUCTURE:")
    print("=" * 60)
    for he in instance['instance']['hyperedges']:
        if he['id'] in labels_map:
            print(f"• {labels_map[he['id']]}")
            if he.get('modifiers'):
                mod_labels = [labels_map.get(m, m) for m in he['modifiers']]
                print(f"  [Modifiers: {', '.join(mod_labels)}]")
    print("=" * 60)

if __name__ == "__main__":
    main()