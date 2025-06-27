#!/usr/bin/env python3
"""
Visualize Semantic Hypergraph instances using networkx
Based on the decomposition approach from Alessandro Angioi's article
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

def extract_hyperedges_from_instance(instance: Dict) -> Tuple[Set[str], List[List[str]]]:
    """Extract nodes and hyperedges from SH instance"""
    nodes = set()
    edges = []
    
    # Get all vertices (concepts)
    for vertex in instance['instance']['vertices']:
        nodes.add(vertex['id'])
    
    # Get all atoms that might not be vertices
    for atom in instance['instance']['atoms']:
        if atom['type'] == 'C':  # Concepts
            nodes.add(atom['id'])
    
    # Process hyperedges
    for he in instance['instance']['hyperedges']:
        # Get participants (excluding modifiers)
        participants = []
        
        # Add connector if it's a concept
        connector_id = he['connector_id']
        
        # Add arguments
        for arg_id in he['arguments']:
            # Check if argument is an atom or another hyperedge
            if arg_id.startswith('a'):  # It's an atom
                # Find the atom
                atom = next((a for a in instance['instance']['atoms'] if a['id'] == arg_id), None)
                if atom and atom['type'] == 'C':  # Only add concepts
                    participants.append(arg_id)
            elif arg_id.startswith('h'):  # It's a hyperedge reference
                # For nested hyperedges, we'll add a special node
                participants.append(arg_id)
                nodes.add(arg_id)  # Add hyperedge as a node for visualization
        
        if len(participants) >= 2:  # Only add if we have at least 2 participants
            edges.append(participants)
            
    return nodes, edges

def decompose_edges_by_cardinality(edges: List[List[str]]) -> Dict[int, List[List[str]]]:
    """Decompose edges by their cardinality"""
    decomposed_edges = defaultdict(list)
    for edge in edges:
        decomposed_edges[len(edge)].append(edge)
    return dict(decomposed_edges)

def plot_hypergraph_components(nodes: Set[str], edges: List[List[str]], instance: Dict, title: str = "Semantic Hypergraph"):
    """Plot hypergraph components by edge cardinality"""
    decomposed_edges = decompose_edges_by_cardinality(edges)
    
    if not decomposed_edges:
        print("No edges to visualize")
        return
    
    # Create subplots
    n_subplots = len(decomposed_edges)
    fig, axes = plt.subplots(1, n_subplots, figsize=(6*n_subplots, 6))
    
    if n_subplots == 1:
        axes = [axes]
    
    # Get node labels
    node_labels = {}
    for vertex in instance['instance']['vertices']:
        node_labels[vertex['id']] = vertex['label']
    
    # Add labels for hyperedge nodes
    for he in instance['instance']['hyperedges']:
        he_id = he['id']
        if he_id in nodes:
            # Find connector atom
            connector = next((a for a in instance['instance']['atoms'] if a['id'] == he['connector_id']), None)
            if connector:
                node_labels[he_id] = f"{he_id}:{connector['term']}"
    
    # Plot each cardinality
    for idx, (cardinality, edges_subset) in enumerate(sorted(decomposed_edges.items())):
        ax = axes[idx]
        
        if cardinality == 2:
            # For binary edges, create simple graph
            g = nx.DiGraph()
            g.add_nodes_from(nodes)
            g.add_edges_from(edges_subset)
        else:
            # For hyperedges, use star expansion
            g = nx.DiGraph()
            g.add_nodes_from(nodes)
            
            # Add hyperedge nodes and connections
            for edge_idx, edge in enumerate(edges_subset):
                # Create a unique node for this hyperedge
                hyperedge_node = f"he_{cardinality}_{edge_idx}"
                g.add_node(hyperedge_node)
                
                # Connect all nodes in the edge to the hyperedge node
                for node in edge:
                    g.add_edge(node, hyperedge_node)
        
        # Layout
        try:
            pos = nx.spring_layout(g, k=2, iterations=50)
        except:
            pos = nx.random_layout(g)
        
        # Draw nodes
        concept_nodes = [n for n in g.nodes() if n in nodes and not n.startswith('h')]
        hyperedge_ref_nodes = [n for n in g.nodes() if n.startswith('h')]
        star_nodes = [n for n in g.nodes() if n.startswith('he_')]
        
        # Draw concept nodes (blue)
        nx.draw_networkx_nodes(g, pos, nodelist=concept_nodes, 
                              node_color='lightblue', node_size=500, ax=ax)
        
        # Draw hyperedge reference nodes (green)
        nx.draw_networkx_nodes(g, pos, nodelist=hyperedge_ref_nodes,
                              node_color='lightgreen', node_size=500, ax=ax)
        
        # Draw star expansion nodes (red)
        nx.draw_networkx_nodes(g, pos, nodelist=star_nodes,
                              node_color='red', node_size=300, ax=ax)
        
        # Draw edges
        if cardinality == 2:
            nx.draw_networkx_edges(g, pos, ax=ax, edge_color='gray', 
                                 connectionstyle='arc3,rad=0.1', arrows=True)
        else:
            nx.draw_networkx_edges(g, pos, ax=ax, edge_color='red',
                                 connectionstyle='arc3,rad=0.1', arrows=False)
        
        # Labels
        labels = {}
        for node in g.nodes():
            if node in node_labels:
                labels[node] = node_labels[node]
            elif node.startswith('he_'):
                # Label for star expansion nodes
                edge_idx = int(node.split('_')[-1])
                edge = edges_subset[edge_idx]
                labels[node] = f"({','.join(edge)})"
            else:
                labels[node] = node
        
        nx.draw_networkx_labels(g, pos, labels, font_size=8, ax=ax)
        
        ax.set_title(f"{cardinality}-ary relationships")
        ax.axis('off')
    
    plt.suptitle(title, fontsize=16)
    plt.tight_layout()
    return fig

def visualize_sh_claims(instance: Dict) -> nx.DiGraph:
    """Create a specialized visualization for claim structures"""
    g = nx.DiGraph()
    
    # Track claim relationships
    claims = []
    
    for he in instance['instance']['hyperedges']:
        connector = next((a for a in instance['instance']['atoms'] if a['id'] == he['connector_id']), None)
        if connector and connector['term'] in ['say', 'describe', 'condemn', 'allege']:
            # This is a claim
            claims.append(he)
    
    # Build claim graph
    for claim in claims:
        claim_id = claim['id']
        g.add_node(claim_id, type='claim')
        
        # Add actor (first argument)
        if claim['arguments']:
            actor_id = claim['arguments'][0]
            actor = next((v for v in instance['instance']['vertices'] if v['id'] == actor_id), None)
            if actor:
                g.add_node(actor_id, type='actor', label=actor['label'])
                g.add_edge(actor_id, claim_id, rel='makes_claim')
        
        # Add claim content (remaining arguments)
        for arg_id in claim['arguments'][1:]:
            if arg_id.startswith('h'):  # Nested claim
                g.add_edge(claim_id, arg_id, rel='claims_about')
            else:
                atom = next((a for a in instance['instance']['atoms'] if a['id'] == arg_id), None)
                if atom and atom['type'] == 'C':
                    g.add_node(arg_id, type='concept', label=atom['term'])
                    g.add_edge(claim_id, arg_id, rel='claims')
    
    return g

def main():
    parser = argparse.ArgumentParser(description='Visualize Semantic Hypergraph instances')
    parser.add_argument('yaml_file', help='Path to SH instance YAML file')
    parser.add_argument('--output', '-o', help='Output image file (default: show plot)')
    parser.add_argument('--claims', action='store_true', help='Show claims visualization')
    
    args = parser.parse_args()
    
    # Load instance
    instance = load_sh_instance(args.yaml_file)
    
    if args.claims:
        # Claims-specific visualization
        g = visualize_sh_claims(instance)
        
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(g, k=3, iterations=50)
        
        # Color by node type
        colors = {'actor': 'lightblue', 'claim': 'lightcoral', 'concept': 'lightgreen'}
        node_colors = [colors.get(g.nodes[n].get('type', 'concept'), 'gray') for n in g.nodes()]
        
        nx.draw(g, pos, node_color=node_colors, with_labels=True, 
                node_size=1000, font_size=8, arrows=True)
        
        # Edge labels
        edge_labels = nx.get_edge_attributes(g, 'rel')
        nx.draw_networkx_edge_labels(g, pos, edge_labels, font_size=6)
        
        plt.title("Claim Structure in Semantic Hypergraph")
    else:
        # General hypergraph visualization
        nodes, edges = extract_hyperedges_from_instance(instance)
        fig = plot_hypergraph_components(nodes, edges, instance, 
                                       title=f"SH: {Path(args.yaml_file).stem}")
    
    if args.output:
        plt.savefig(args.output, dpi=300, bbox_inches='tight')
        print(f"Saved visualization to {args.output}")
    else:
        plt.show()

if __name__ == "__main__":
    main()