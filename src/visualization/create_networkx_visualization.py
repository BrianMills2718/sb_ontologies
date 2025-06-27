#!/usr/bin/env python3
"""
Create NetworkX visualization of Carter's cognitive map
Generates actual network graph image file
"""
import yaml
import matplotlib.pyplot as plt
import networkx as nx
from pathlib import Path
import matplotlib.patches as mpatches

def load_carter_analysis():
    """Load the Carter cognitive map analysis"""
    analysis_path = Path('/home/brian/lit_review/carter_young1996_faithful_analysis.yml')
    
    with open(analysis_path, 'r') as f:
        content = f.read()
    
    if content.startswith('```yaml'):
        content = content[7:]
    if content.endswith('```'):
        content = content[:-3]
    
    return yaml.safe_load(content)

def create_networkx_graph(analysis):
    """Create NetworkX directed graph from cognitive map"""
    G = nx.DiGraph()
    
    concepts = analysis['cognitive_map']['concepts']
    relationships = analysis['cognitive_map']['relationships']
    
    # Create concept lookup
    concept_lookup = {c['id']: c['label'] for c in concepts}
    
    # Add nodes with attributes
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

def visualize_network(G, concept_lookup, analysis):
    """Create NetworkX visualization"""
    
    # Create figure
    plt.figure(figsize=(20, 16))
    
    # Create layout - use spring layout with more iterations for better spacing
    pos = nx.spring_layout(G, k=2, iterations=100, seed=42)
    
    # Define node categories and colors
    key_concepts = ['C1', 'C2', 'C14', 'C12', 'C11', 'C17', 'C18']  # US, Soviet, Peace, Arms Control, Nuclear, HR, Cooperation
    
    node_colors = []
    node_sizes = []
    
    for node in G.nodes():
        if node in key_concepts:
            node_colors.append('#FF6B6B')  # Red for key concepts
            node_sizes.append(2000)
        else:
            node_colors.append('#4ECDC4')  # Teal for other concepts
            node_sizes.append(1200)
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos,
                          node_color=node_colors,
                          node_size=node_sizes,
                          alpha=0.8,
                          edgecolors='black',
                          linewidths=1)
    
    # Prepare edges by relationship type
    edge_lists = {
        '+': [],
        '-': [],
        'strategy': [],
        'if-then': [],
        'warrant-for': []
    }
    
    for edge in G.edges(data=True):
        rel_type = edge[2]['relationship']
        edge_lists[rel_type].append((edge[0], edge[1]))
    
    # Draw edges by type with different colors and styles
    # Positive causal (green)
    if edge_lists['+']: 
        nx.draw_networkx_edges(G, pos, 
                             edgelist=edge_lists['+'],
                             edge_color='green',
                             width=3,
                             alpha=0.8,
                             arrowsize=25,
                             arrowstyle='->')
    
    # Negative causal (red)
    if edge_lists['-']:
        nx.draw_networkx_edges(G, pos, 
                             edgelist=edge_lists['-'],
                             edge_color='red',
                             width=3,
                             alpha=0.8,
                             arrowsize=25,
                             arrowstyle='->')
    
    # Strategy (blue, dashed)
    if edge_lists['strategy']:
        nx.draw_networkx_edges(G, pos, 
                             edgelist=edge_lists['strategy'],
                             edge_color='blue',
                             width=2,
                             alpha=0.7,
                             style='dashed',
                             arrowsize=20,
                             arrowstyle='->')
    
    # If-then (orange, dotted)
    if edge_lists['if-then']:
        nx.draw_networkx_edges(G, pos, 
                             edgelist=edge_lists['if-then'],
                             edge_color='orange',
                             width=2,
                             alpha=0.7,
                             style='dotted',
                             arrowsize=20,
                             arrowstyle='->')
    
    # Warrant-for (purple, dashdot)
    if edge_lists['warrant-for']:
        nx.draw_networkx_edges(G, pos, 
                             edgelist=edge_lists['warrant-for'],
                             edge_color='purple',
                             width=2,
                             alpha=0.7,
                             style=(0, (3, 1, 1, 1)),
                             arrowsize=20,
                             arrowstyle='->')
    
    # Add labels with better formatting
    labels = {}
    for node in G.nodes():
        label = concept_lookup[node]
        # Wrap long labels
        if len(label) > 15:
            words = label.split()
            if len(words) > 2:
                mid = len(words) // 2
                label = ' '.join(words[:mid]) + '\\n' + ' '.join(words[mid:])
            elif len(label) > 20:
                label = label[:17] + '...'
        labels[node] = label
    
    nx.draw_networkx_labels(G, pos, labels, 
                           font_size=9, 
                           font_weight='bold',
                           font_color='black')
    
    # Create legend
    legend_elements = [
        mpatches.Patch(color='green', label='Positive Cause (+)'),
        mpatches.Patch(color='red', label='Negative Cause (-)'),
        mpatches.Patch(color='blue', label='Strategy'),
        mpatches.Patch(color='orange', label='If-Then Conditional'),
        mpatches.Patch(color='purple', label='Warrant-For'),
        mpatches.Patch(color='#FF6B6B', label='Key Concepts'),
        mpatches.Patch(color='#4ECDC4', label='Supporting Concepts')
    ]
    
    plt.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0, 1))
    
    # Add title and metrics
    measures = analysis.get('structural_measures', {})
    size = measures.get('size', 'N/A')
    connectedness = measures.get('connectedness', {}).get('value', 'N/A')
    
    plt.title("Carter's Cognitive Map of US-Soviet Relations\\n" +
              "Young 1996 Cognitive Mapping Analysis",
              fontsize=18, fontweight='bold', pad=20)
    
    plt.figtext(0.5, 0.02, 
                f"Young's Structural Measures: Size = {size} concepts | " +
                f"Connectedness (C_G) = {connectedness} | {len(G.edges())} relationships",
                ha='center', fontsize=12)
    
    # Remove axes
    plt.axis('off')
    
    # Adjust layout
    plt.tight_layout()
    
    return plt

def main():
    """Create NetworkX visualization"""
    print("🎨 CREATING NETWORKX VISUALIZATION")
    print("=" * 50)
    
    # Load analysis
    analysis = load_carter_analysis()
    print("✓ Loaded Carter cognitive map analysis")
    
    # Create graph
    G, concept_lookup = create_networkx_graph(analysis)
    print(f"✓ Created NetworkX graph: {len(G.nodes())} nodes, {len(G.edges())} edges")
    
    # Create visualization
    plt = visualize_network(G, concept_lookup, analysis)
    print("✓ Generated network visualization")
    
    # Save the plot
    output_path = Path('/home/brian/lit_review/carter_cognitive_map_networkx.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    print(f"✓ Saved visualization to: {output_path}")
    
    # Also save as PDF for vector graphics
    pdf_path = Path('/home/brian/lit_review/carter_cognitive_map_networkx.pdf')
    plt.savefig(pdf_path, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    print(f"✓ Saved PDF version to: {pdf_path}")
    
    print()
    print("📊 NETWORK STATISTICS:")
    print(f"   Nodes: {len(G.nodes())}")
    print(f"   Edges: {len(G.edges())}")
    print(f"   Young's Connectedness: {analysis.get('structural_measures', {}).get('connectedness', {}).get('value', 'N/A')}")
    
    # Show relationship breakdown
    rel_types = {}
    for edge in G.edges(data=True):
        rel_type = edge[2]['relationship']
        rel_types[rel_type] = rel_types.get(rel_type, 0) + 1
    
    print(f"   Relationship types:")
    for rel_type, count in sorted(rel_types.items()):
        print(f"     {rel_type}: {count}")

if __name__ == "__main__":
    main()