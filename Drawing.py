import networkx as nx
from algorithms.votingutils import pairwise_wins
from algorithms.partitions import get_connected_components

# Returns a NetworkX graph of pairwise comparisons with edges labeled by win strength
def beat_graph(candidates:list, votes:list):
    pairs = pairwise_wins(candidates, votes)
    graph = nx.DiGraph()
    graph.add_weighted_edges_from([(a,b,pairs[(a,b)]) for a,b in pairs.keys()])
    return graph

def draw_beat_graph(candidates:list, votes:list):
    graph = beat_graph(candidates, votes)
    pos = nx.arf_layout(graph)
    color = ['C0','C1','C2','C3','C4','C5','C6','C7','C8','C9']*(len(candidates)//10 + 1)
    nx.draw(graph, pos, arrowsize=50, node_color=color[:len(candidates)], node_size=1000, font_size=20, with_labels=True)
    nx.draw_networkx_edge_labels(graph, pos, font_size=20, edge_labels=nx.get_edge_attributes(graph, 'weight'))

def layered_beat_graph(candidates:list, votes:list):
    wins = pairwise_wins(candidates, votes)
    components = get_connected_components(candidates, wins)
    sorted_keys = sorted(components.keys(), lambda x: sum(wins[(a,b)] for a,b in wins if a == x), reverse=True)
    graph = nx.DiGraph()
    graph.add_weighted_edges_from([(a,b,wins[(a,b)]) for a,b in wins.keys()])
    for i in range(len(sorted_keys)):
        for node in components[sorted_keys[i]]:
            graph.add_node(node, layer=i)
    return graph

def layered_graph(groups:list[set]):
    graph = nx.DiGraph()
    graph.add_weighted_edges_from([(a,b,wins[(a,b)]) for a,b in wins.keys()])
    for i in range(len(sorted_keys)):
        for node in components[sorted_keys[i]]:
            graph.add_node(node, layer=i)
    return graph