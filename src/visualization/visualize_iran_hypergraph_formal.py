#!/usr/bin/env python3
"""
Visualize Semantic Hypergraph from Iran debate using FORMAL type system
Respects the actual theory: C, P, B, T, M, J for atoms and R, S for hyperedges
"""

import json
import networkx as nx
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Set, Optional
import re
from pathlib import Path

class HyperedgeParser:
    """Parse semantic hypergraph notation into structured data"""
    
    def __init__(self):
        self.node_counter = 0
        self.nodes = {}  # id -> node data
        self.edges = []  # list of edges
        
    def parse(self, hyperedge_str: str) -> Optional[str]:
        """Parse a hyperedge string and return its node ID"""
        hyperedge_str = hyperedge_str.strip()
        
        # Base case: atomic element like "iran/C" or "warns/P"
        if '(' not in hyperedge_str and '/' in hyperedge_str:
            parts = hyperedge_str.split('/')
            if len(parts) == 2:
                term, type_label = parts
                node_id = f"n{self.node_counter}"
                self.node_counter += 1
                self.nodes[node_id] = {
                    'term': term,
                    'type': type_label,
                    'label': f"{term}/{type_label}",
                    'is_atomic': True
                }
                return node_id
        
        # Complex case: (element/TYPE args...)
        if hyperedge_str.startswith('(') and hyperedge_str.endswith(')'):
            inner = hyperedge_str[1:-1]
            
            # Find the connector (first element/TYPE)
            match = re.match(r'^([^/\s]+/[A-Z])\s*(.*)', inner)
            if match:
                connector_str = match.group(1)
                args_str = match.group(2)
                
                # Parse connector
                connector_id = self.parse(connector_str)
                
                # Parse arguments
                arg_ids = []
                if args_str:
                    args = self._split_args(args_str)
                    for arg in args:
                        arg_id = self.parse(arg)
                        if arg_id:
                            arg_ids.append(arg_id)
                
                # Create hyperedge node
                node_id = f"h{self.node_counter}"
                self.node_counter += 1
                
                # Determine hyperedge type based on connector
                connector_data = self.nodes.get(connector_id, {})
                connector_type = connector_data.get('type', '')
                
                if connector_type == 'P':
                    he_type = 'R'  # Relation
                elif connector_type == 'T':
                    he_type = 'S'  # Specifier
                elif connector_type == 'B':
                    he_type = 'C'  # Builder creates concept
                else:
                    he_type = 'H'  # Generic hyperedge
                
                # Create label
                connector_term = connector_data.get('term', '')
                if len(arg_ids) <= 2:
                    arg_labels = [self.nodes.get(aid, {}).get('term', aid) for aid in arg_ids]
                    label = f"({connector_term} {' '.join(arg_labels)})"
                else:
                    label = f"({connector_term} ...{len(arg_ids)} args...)"
                
                self.nodes[node_id] = {
                    'term': hyperedge_str,
                    'type': he_type,
                    'label': label,
                    'is_atomic': False,
                    'connector': connector_id,
                    'arguments': arg_ids
                }
                
                # Add edges (only if valid IDs)
                if connector_id and node_id:
                    self.edges.append((connector_id, node_id, 'connector'))
                for i, arg_id in enumerate(arg_ids):
                    if node_id and arg_id:
                        self.edges.append((node_id, arg_id, f'arg{i+1}'))
                
                return node_id
        
        return None
    
    def _split_args(self, args_str: str) -> List[str]:
        """Split arguments respecting parentheses"""
        args = []
        current = []
        depth = 0
        
        for char in args_str:
            if char == '(':
                depth += 1
            elif char == ')':
                depth -= 1
            elif char == ' ' and depth == 0:
                if current:
                    args.append(''.join(current))
                    current = []
                continue
            current.append(char)
            
        if current:
            args.append(''.join(current))
            
        return args

def create_formal_hypergraph(json_path: str) -> nx.DiGraph:
    """Create a formal hypergraph visualization"""
    
    # Load the results
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # Get the full response text
    full_text = data.get('full_response', '')
    
    # Extract the main hyperedges from the examples
    main_hyperedges = [
        # Statement 1: U.S. Intelligence assessment
        "((consistently/M assessed/P) (+/B u.s./C intelligence/C) ((not/M engaged/P) iran/C (in/T (+/B weapons/C research/C))))",
        
        # Statement 2: Bret Stephens position
        "(applauds/P (+/B bret/C stephens/C) (of/B (+/B president/C trump/C) (+/B strikes/C (in/T iran/C))))",
        
        # Statement 3: Kelanic warning
        "(warns/P (+/B rosemary/C kelanic/C) (+/B united/C states/C) (against/T (strike/P iran/C)))",
        
        # Statement 4: Netanyahu historical claim
        "(warned/P (+/B benjamin/C netanyahu/C) (+/B israeli/C knesset/C) (in/T 1992/C) (be/P iran/C (+/B few/M years/C (from/T (+/B nuclear/C bomb/C)))))"
    ]
    
    # Parse all hyperedges
    parser = HyperedgeParser()
    root_nodes = []
    
    for he in main_hyperedges:
        root_id = parser.parse(he)
        if root_id:
            root_nodes.append(root_id)
    
    # Create NetworkX graph
    g = nx.DiGraph()
    
    # Add all nodes with proper formatting
    for node_id, node_data in parser.nodes.items():
        g.add_node(node_id, **node_data)
    
    # Add all edges (skip any with None values)
    for src, dst, edge_type in parser.edges:
        if src is not None and dst is not None:
            g.add_edge(src, dst, type=edge_type)
    
    # Mark root nodes
    for root_id in root_nodes:
        g.nodes[root_id]['is_root'] = True
    
    return g

def plot_formal_hypergraph(g: nx.DiGraph, title: str = "Iran Debate: Formal Semantic Hypergraph"):
    """Plot the hypergraph using formal type system"""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 12))
    
    # Left plot: Full graph
    plot_subgraph(g, ax1, "Complete Hypergraph Structure")
    
    # Right plot: Simplified view focusing on main relations
    g_simple = create_simplified_view(g)
    plot_subgraph(g_simple, ax2, "Simplified View (Main Relations)")
    
    plt.suptitle(title, fontsize=20, fontweight='bold')
    plt.tight_layout()
    
    return fig

def plot_subgraph(g: nx.DiGraph, ax: plt.Axes, subtitle: str):
    """Plot a subgraph on given axes"""
    
    # Layout
    pos = nx.spring_layout(g, k=3, iterations=100, seed=42)
    
    # Adjust positions for hierarchy
    # Move root nodes to top
    root_nodes = [n for n, d in g.nodes(data=True) if d.get('is_root')]
    for node in root_nodes:
        x, y = pos[node]
        pos[node] = (x, y + 0.5)
    
    # Color scheme based on FORMAL types
    type_colors = {
        'C': '#4CAF50',  # Green - Concepts
        'P': '#2196F3',  # Blue - Predicates  
        'B': '#FF9800',  # Orange - Builders
        'T': '#9C27B0',  # Purple - Triggers
        'M': '#F44336',  # Red - Modifiers
        'J': '#795548',  # Brown - Conjunctions
        'R': '#00BCD4',  # Cyan - Relations
        'S': '#E91E63',  # Pink - Specifiers
        'H': '#607D8B'   # Blue Grey - Generic hyperedges
    }
    
    # Node properties
    node_colors = []
    node_sizes = []
    node_shapes = []
    
    for node in g.nodes():
        node_type = g.nodes[node].get('type', 'H')
        is_atomic = g.nodes[node].get('is_atomic', False)
        
        node_colors.append(type_colors.get(node_type, '#757575'))
        
        if is_atomic:
            node_sizes.append(1500)
        else:
            node_sizes.append(3000)
    
    # Draw nodes
    nx.draw_networkx_nodes(g, pos, node_color=node_colors, node_size=node_sizes,
                          alpha=0.9, linewidths=2, edgecolors='black', ax=ax)
    
    # Draw edges with different styles
    edge_types = nx.get_edge_attributes(g, 'type')
    
    connector_edges = [(u,v) for (u,v), t in edge_types.items() if t == 'connector']
    arg_edges = [(u,v) for (u,v), t in edge_types.items() if t.startswith('arg')]
    
    nx.draw_networkx_edges(g, pos, connector_edges, edge_color='black',
                          arrows=True, arrowsize=15, width=2, alpha=0.8, 
                          arrowstyle='-|>', ax=ax)
    nx.draw_networkx_edges(g, pos, arg_edges, edge_color='gray',
                          arrows=True, arrowsize=15, width=1.5, alpha=0.6,
                          style='dashed', ax=ax)
    
    # Labels
    labels = nx.get_node_attributes(g, 'label')
    
    # Wrap long labels
    wrapped_labels = {}
    for node, label in labels.items():
        if len(label) > 25:
            # Truncate very long labels
            wrapped_labels[node] = label[:25] + "..."
        else:
            wrapped_labels[node] = label
    
    nx.draw_networkx_labels(g, pos, wrapped_labels, font_size=8, 
                           font_weight='bold', ax=ax)
    
    # Type legend
    legend_elements = []
    for type_code, color in sorted(type_colors.items()):
        type_names = {
            'C': 'Concept', 'P': 'Predicate', 'B': 'Builder',
            'T': 'Trigger', 'M': 'Modifier', 'J': 'Conjunction',
            'R': 'Relation', 'S': 'Specifier', 'H': 'Hyperedge'
        }
        legend_elements.append(
            plt.Line2D([0], [0], marker='o', color='w', 
                      label=f'{type_code} - {type_names.get(type_code, type_code)}',
                      markerfacecolor=color, markersize=10, markeredgecolor='black')
        )
    
    ax.legend(handles=legend_elements, loc='upper left', frameon=True, 
             fancybox=True, shadow=True)
    
    ax.set_title(subtitle, fontsize=14, fontweight='bold', pad=10)
    ax.axis('off')

def create_simplified_view(g: nx.DiGraph) -> nx.DiGraph:
    """Create a simplified view showing only main relations and key concepts"""
    g_simple = nx.DiGraph()
    
    # Find root relations (type R)
    root_relations = [n for n, d in g.nodes(data=True) 
                     if d.get('type') == 'R' and d.get('is_root')]
    
    # Add simplified nodes for each main statement
    simplified_nodes = [
        ('s1', {'label': 'U.S. Intel:\nIran not in\nweapons research', 'type': 'R'}),
        ('s2', {'label': 'Stephens:\napplauds\nTrump strikes', 'type': 'R'}),
        ('s3', {'label': 'Kelanic:\nwarns against\nstrikes', 'type': 'R'}),
        ('s4', {'label': 'Netanyahu 1992:\nIran years from\nnuclear bomb', 'type': 'R'})
    ]
    
    for node_id, attrs in simplified_nodes:
        g_simple.add_node(node_id, **attrs)
    
    # Add key concept nodes
    key_concepts = [
        ('iran', {'label': 'iran/C', 'type': 'C'}),
        ('nuclear', {'label': 'nuclear/C', 'type': 'C'}),
        ('strikes', {'label': 'strikes/C', 'type': 'C'}),
        ('weapons', {'label': 'weapons research/C', 'type': 'C'})
    ]
    
    for node_id, attrs in key_concepts:
        g_simple.add_node(node_id, **attrs)
    
    # Connect statements to concepts
    g_simple.add_edge('s1', 'iran')
    g_simple.add_edge('s1', 'weapons')
    g_simple.add_edge('s2', 'strikes')
    g_simple.add_edge('s3', 'strikes')
    g_simple.add_edge('s4', 'iran')
    g_simple.add_edge('s4', 'nuclear')
    
    return g_simple

def print_type_statistics(g: nx.DiGraph):
    """Print statistics about node and edge types"""
    print("\n" + "="*60)
    print("FORMAL TYPE STATISTICS")
    print("="*60)
    
    # Count node types
    type_counts = {}
    for node, data in g.nodes(data=True):
        node_type = data.get('type', 'unknown')
        type_counts[node_type] = type_counts.get(node_type, 0) + 1
    
    print("\nNode Types:")
    for type_code, count in sorted(type_counts.items()):
        print(f"  {type_code}: {count} nodes")
    
    print(f"\nTotal nodes: {g.number_of_nodes()}")
    print(f"Total edges: {g.number_of_edges()}")
    
    # Print some example nodes of each type
    print("\nExample nodes by type:")
    for type_code in ['C', 'P', 'B', 'T', 'M', 'R', 'S']:
        examples = [data.get('label', node) 
                   for node, data in g.nodes(data=True) 
                   if data.get('type') == type_code][:3]
        if examples:
            print(f"  {type_code}: {', '.join(examples)}")

def main():
    # Load and visualize
    json_path = "/home/brian/lit_review/results/iran_debate_hypergraph.json"
    
    g = create_formal_hypergraph(json_path)
    
    # Plot
    fig = plot_formal_hypergraph(g, title="Iran Nuclear Debate: Formal Semantic Hypergraph")
    
    # Save
    output_path = "/home/brian/lit_review/results/iran_debate_hypergraph_formal.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Saved formal visualization to {output_path}")
    
    # Print statistics
    print_type_statistics(g)
    
    plt.show()

if __name__ == "__main__":
    main()