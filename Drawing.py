import networkx as nx
from votingutils import pairwise_wins
from partitions import get_connected_components

# Returns a NetworkX graph of pairwise comparisons with edges labeled by win strength
def beat_graph(candidates:list, votes:list):
    pairs = pairwise_wins(candidates, votes)
    graph = nx.DiGraph()
    graph.add_weighted_edges_from([(a,b,pairs[(a,b)]) for a,b in pairs.keys()])
    return graph

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