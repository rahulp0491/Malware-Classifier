from mcs import *

# Checks if the edge is in g_subgraph
def notin (edge, g_subgraph_edges, gid):
	for e in g_subgraph_edges:
		if (e[0][gid-1], e[1][gid-1]) == edge:
			return False
	return True

# Returns embedding between a graph and its subgraph
def embedding (subgraph, g, gid):
	g_subgraph_edges = subgraph.edges ()
	g_edges = g.edges ()
	E = []
	for edge in g_edges:
		if notin(edge, g_subgraph_edges, gid):
			E.append (edge)
	return E

# Returns diff of two graphs
def diff (g, g_subgraph, gid):
	g_subgraph_nodes = g_subgraph.nodes ()
	g_nodes = g.nodes ()
	delnodes = []
	for node in g_subgraph_nodes:
		if node[gid-1] in g_nodes:
			for node_adj in g.incidents (node[gid-1]):
				g.del_edge ((node_adj, node[gid-1]))
				if node_adj not in delnodes:
					delnodes.append (node_adj)
			if node[gid-1] not in delnodes:
				delnodes.append (node[gid-1])
	for node in delnodes:
		g.del_node (node)
	return g

# Get a node in second graph, given a node in the first graph, from the subgraph
def getendpoint (node2, subgraph):
	subgraph_nodes = subgraph.nodes ()
	
	for n1, n2 in subgraph_nodes:
		if n2 == node2:
			return n1
	
	return None

# Returns the union of two graphs
def union (g, g_diff, E, subgraph):
	g_diff_nodes = g_diff.nodes ()
	for node in g_diff_nodes:
		g.add_node (node, g_diff.node_attributes (node))
	
	for n1, n2 in E:
		if not (n1 in g_diff and n2 in g_diff):
			if n1 in g_diff:
				node1 = getendpoint (n2, subgraph)
				g.add_edge ((n1, node1))
			elif n2 in g_diff:
				node2 = getendpoint (n1, subgraph)
				g.add_edge ((node2, n2))
	return g

# Sets appropriate weights of edges
def setweight (graph, subgraph):
	subgraph_edges = subgraph.edges ()
	for e1, e2 in subgraph_edges:
		wt = subgraph.edge_weight ((e1[0], e2[0]))
		graph.set_edge_weight ((e1[0], e2[0]), wt + 1)

# Returns isolated nodes in a graph
def getisolatednodes (graph):
	g_nodes = graph.nodes ()
	nodelist = []
	for e1, e2 in graph.edges ():
		if e1 not in nodelist:
			nodelist.append (e1)
		if e2 not in nodelist:
			nodelist.append (e2)
	isolatednodes = []
	for node in g_nodes:
		if node not in nodelist:
			isolatednodes.append (node)
	
	return isolatednodes

# Prunes the graph given a threshold
def prunegraph (graph, theta):
	g_edges = graph.edges ()
	for e1, e2 in g_edges:
		if graph.edge_weight ((e1, e2)) < theta:
			graph.del_edge ((e1, e2))
	
	for node in getisolatednodes (graph):
		graph.del_node (node)
	
	return graph

# Save a graph
def save_graph (g):
	g_nodes = g.nodes ()
	graph = digraph ()
	
	for node in g_nodes:
		graph.add_node (node, g.node_attributes (node))
	g_edges = g.edges ()
	for edge in g_edges:
		graph.add_edge (edge)
	return graph

# Return MinCS of two graphs
def mincs (g1, g2):
	graph = save_graph (g1)
	subgraph = mcsinit (g1, g2)
	E1 = embedding (subgraph, g1, 1)
	E2 = embedding (subgraph, g2, 2)
	U1 = subgraph
	U2 = diff (g1, U1, 1)
	U3 = diff (g2, U1, 2)
	wmincs = union (graph, U3, E2, subgraph)
	return wmincs, subgraph
