#!/usr/bin/env python3
"""
Visualize Carter's Cognitive Map from Young 1996 Analysis
Creates network visualization using the faithful schema application results
"""
import yaml
import matplotlib.pyplot as plt
import networkx as nx
from pathlib import Path
import numpy as np

def load_carter_analysis():
    """Load the Carter cognitive map analysis"""
    analysis_path = Path('/home/brian/lit_review/carter_young1996_faithful_analysis.yml')
    
    # Clean the YAML content (remove code block markers)
    with open(analysis_path, 'r') as f:
        content = f.read()
    
    if content.startswith('```yaml'):
        content = content[7:]  # Remove ```yaml
    if content.endswith('```'):
        content = content[:-3]  # Remove ```
    
    return yaml.safe_load(content)

def create_network_graph(analysis):
    """Create NetworkX graph from the cognitive map"""
    G = nx.DiGraph()
    
    # Extract concepts and relationships
    concepts = analysis['cognitive_map']['concepts']
    relationships = analysis['cognitive_map']['relationships']
    
    # Create concept lookup
    concept_lookup = {c['id']: c['label'] for c in concepts}
    
    # Add nodes
    for concept in concepts:
        G.add_node(concept['id'], 
                  label=concept['label'],
                  node_type=concept['node_type'])
    
    # Add edges with attributes
    for rel in relationships:
        G.add_edge(rel['from'], rel['to'],
                  relationship=rel['relationship_category'],
                  truth_value=rel['truth_value'],
                  modifiers=rel.get('modifiers', []),
                  salience=rel.get('salience', 1),
                  action=rel.get('action_category', ''))
    
    return G, concept_lookup

def visualize_network(G, concept_lookup):
    """Create visualization of the cognitive map"""
    
    # Set up the plot
    fig, ax = plt.subplots(figsize=(20, 16))
    
    # Create layout
    pos = nx.spring_layout(G, k=3, iterations=50, seed=42)
    
    # Define colors for different relationship types
    edge_colors = []
    edge_styles = []
    edge_widths = []
    
    for edge in G.edges(data=True):
        rel_type = edge[2]['relationship']
        if rel_type == '+':
            edge_colors.append('green')
            edge_styles.append('-')
        elif rel_type == '-':
            edge_colors.append('red')
            edge_styles.append('-')
        elif rel_type == 'strategy':
            edge_colors.append('blue')
            edge_styles.append('--')
        elif rel_type == 'if-then':
            edge_colors.append('orange')
            edge_styles.append(':')
        elif rel_type == 'warrant-for':
            edge_colors.append('purple')
            edge_styles.append('-.')
        else:
            edge_colors.append('gray')
            edge_styles.append('-')
        
        # Edge width based on salience
        edge_widths.append(edge[2].get('salience', 1) * 2)
    
    # Draw edges
    for i, edge in enumerate(G.edges()):
        nx.draw_networkx_edges(G, pos, 
                             edgelist=[edge],
                             edge_color=[edge_colors[i]],
                             style=edge_styles[i],
                             width=edge_widths[i],
                             alpha=0.7,
                             arrowsize=20,
                             arrowstyle='->')
    
    # Define node categories for coloring
    key_concepts = ['C1', 'C2', 'C14', 'C12', 'C11']  # US, Soviet, Peace, Arms Control, Nuclear
    node_colors = []
    node_sizes = []
    
    for node in G.nodes():
        if node in key_concepts:
            node_colors.append('lightcoral')
            node_sizes.append(2000)
        else:
            node_colors.append('lightblue')
            node_sizes.append(1200)
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos,
                          node_color=node_colors,
                          node_size=node_sizes,
                          alpha=0.9)
    
    # Add labels
    labels = {node: concept_lookup[node][:20] + '...' if len(concept_lookup[node]) > 20 
              else concept_lookup[node] for node in G.nodes()}
    
    nx.draw_networkx_labels(G, pos, labels, font_size=8, font_weight='bold')
    
    # Create legend
    legend_elements = [
        plt.Line2D([0], [0], color='green', lw=2, label='Positive Cause (+)'),
        plt.Line2D([0], [0], color='red', lw=2, label='Negative Cause (-)'),
        plt.Line2D([0], [0], color='blue', lw=2, linestyle='--', label='Strategy'),
        plt.Line2D([0], [0], color='orange', lw=2, linestyle=':', label='If-Then'),
        plt.Line2D([0], [0], color='purple', lw=2, linestyle='-.', label='Warrant-For'),
        plt.scatter([], [], c='lightcoral', s=100, label='Key Concepts'),
        plt.scatter([], [], c='lightblue', s=100, label='Other Concepts')
    ]
    
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0, 1))
    
    # Set title and labels
    plt.title("Carter's Cognitive Map of US-Soviet Relations\n(Young 1996 Analysis)", 
              fontsize=16, fontweight='bold', pad=20)
    
    # Add subtitle with metrics
    structural_measures = analysis.get('structural_measures', {})
    size = structural_measures.get('size', 'N/A')
    connectedness = structural_measures.get('connectedness', {}).get('value', 'N/A')
    
    plt.suptitle(f"Size: {size} concepts | Connectedness: {connectedness} | 15 relationships", 
                 fontsize=12, y=0.02)
    
    ax.set_axis_off()
    plt.tight_layout()
    
    # Save the plot
    output_path = Path('/home/brian/lit_review/carter_cognitive_map_visualization.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    
    return output_path

def print_network_summary(G, analysis):
    """Print summary of the network structure"""
    print("🧠 CARTER'S COGNITIVE MAP SUMMARY")
    print("=" * 50)
    print(f"Schema: Young 1996 Cognitive Mapping")
    print(f"Citation: {analysis.get('citation', 'N/A')}")
    print()
    
    print(f"📊 NETWORK STRUCTURE:")
    print(f"   Concepts (nodes): {len(G.nodes())}")
    print(f"   Relationships (edges): {len(G.edges())}")
    print()
    
    # Structural measures
    measures = analysis.get('structural_measures', {})
    print(f"📏 YOUNG'S STRUCTURAL MEASURES:")
    print(f"   Size: {measures.get('size', 'N/A')}")
    print(f"   Connectedness (C_G): {measures.get('connectedness', {}).get('value', 'N/A')}")
    print()
    
    # Relationship type breakdown
    rel_types = {}
    for edge in G.edges(data=True):
        rel_type = edge[2]['relationship']
        rel_types[rel_type] = rel_types.get(rel_type, 0) + 1
    
    print(f"🔗 RELATIONSHIP TYPES (Young's Categories):")
    for rel_type, count in sorted(rel_types.items()):
        print(f"   {rel_type}: {count}")
    print()
    
    # Key concepts
    concept_lookup = {c['id']: c['label'] for c in analysis['cognitive_map']['concepts']}
    key_nodes = ['C1', 'C2', 'C14', 'C12', 'C11']
    
    print(f"🎯 KEY CONCEPTS:")
    for node in key_nodes:
        if node in concept_lookup:
            print(f"   {node}: {concept_lookup[node]}")

def main():
    """Main execution function"""
    print("🎨 VISUALIZING CARTER'S COGNITIVE MAP")
    print("=" * 60)
    print("Using Young 1996 faithful schema analysis")
    print()
    
    # Load the analysis
    analysis = load_carter_analysis()
    
    # Create network graph
    G, concept_lookup = create_network_graph(analysis)
    
    # Print summary
    print_network_summary(G, analysis)
    print()
    
    # Create visualization
    print("🎨 Creating network visualization...")
    output_path = visualize_network(G, concept_lookup)
    
    print(f"✅ Visualization saved to: {output_path}")
    print()
    print("🔍 The visualization shows:")
    print("   • Green arrows: Positive causal relationships (+)")
    print("   • Red arrows: Negative causal relationships (-)")
    print("   • Blue dashed: Strategy relationships")
    print("   • Orange dotted: If-then conditional relationships")
    print("   • Purple dash-dot: Warrant-for relationships")
    print("   • Red nodes: Key concepts (US, Soviet, Peace, Arms Control, Nuclear)")
    print("   • Blue nodes: Supporting concepts")

if __name__ == "__main__":
    main()