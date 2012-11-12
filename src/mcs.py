import sys, os
import xml.etree.ElementTree as et
from pygraph.classes.digraph import digraph

# Global variables
GTable = []
currentSize = 0
savedmcs = []

# Checks if the pair of nodes are legal/feasible
def isFeasiblePair (g1, g2, state, node1, node2):
	g_unused = state [1]
	if not ((node1, node2) in g_unused):
		return False
	g_used = state [0]
	if (node1, node2) in g_used:
		return False	
	if not (g1.has_node (node1) and g2.has_node (node2)):
		return False
	if g_used == []:
		return True
	length = len (g_used)
	node1_attr = g1.node_attributes (node1)
	node2_attr = g2.node_attributes (node2)
	node1_label = node1_attr [0][1]
	node2_label = node2_attr [0][1]	
	if node1_label != node2_label:
		return False	
	i = 0
	while i < length:
		if (node1, node2) != g_used [i]:
			if (g1.has_edge ((g_used [i][0], node1)) ^ g2.has_edge ((g_used [i][1], node2))) or (g1.has_edge ((node1, g_used [i][0])) ^  g2.has_edge ((node2, g_used [i][1]))):
				return False
		i = i + 1
	return True

# Adds the pair of nodes to the subgraph in the state
def addPair (g1, g2, state, node1, node2):
	g_subGraph = state [2]
	if g_subGraph == None:
		g_subGraph = digraph ()
		g_subGraph.add_node ((node1, node2), g1.node_attributes (node1))
		state [2] = g_subGraph
		state [0].append ((node1, node2))
		return state
	g_subGraph.add_node ((node1, node2), g1.node_attributes (node1))
	g_used = state [0]
	for g1_node, g2_node in g_used:
		if g1.has_edge ((g1_node, node1)) and g2.has_edge ((g2_node, node2)):
			g_subGraph_wt = int(g1.edge_weight ((g1_node, node1))) + int(g2.edge_weight ((g2_node, node2)))
			g_subGraph.add_edge (((g1_node, g2_node), (node1, node2)), g_subGraph_wt)
		elif g1.has_edge ((node1, g1_node)) and g2.has_edge ((node2, g2_node)):
			g_subGraph_wt = int(g1.edge_weight ((node1, g1_node))) + int(g2.edge_weight ((node2, g2_node)))
			g_subGraph.add_edge (((node1, node2), (g1_node, g2_node)), g_subGraph_wt)
	
	state [0].append ((node1, node2))
	return state

# Determines if a state is a leaf
def isLeaf (g1, g2, state):
	g_used = state [0]
	g1_usedlist = [node1 for node1, node2 in g_used]
	g2_usedlist = [node2 for node1, node2 in g_used]
	g1_iter = g1.__iter__ ()
	g2_iter = g2.__iter__ ()
	for g1_node in g1_iter:
		if g1_node not in g1_usedlist:
			return False
	
	for g2_node in g2_iter:
		if g2_node not in g2_usedlist:
			return False
	return True

# Checks if the pruningCondition has arrived
def pruningCondition (g1, g2, state):
	g1_len = len (g1)
	g2_len = len (g2)
	
	global currentSize
	subGraph_len = len (state [2])
	states_left = min (g1_len, g2_len) - len (state [0])
	if currentSize >= subGraph_len + states_left:
		return True

# Initializes GTable in each run
def init_GTable (g1, g2):
	global GTable
	g1_iter = [node for node in g1.__iter__ ()]
	g2_iter = [node for node in g2.__iter__ ()]
	for g1_node in g1_iter:
		for g2_node in g2_iter:
			GTable.append ((g1_node, g2_node))

# Update state information
def update (state):
	if state [1] == None:
		state [1] = GTable [:]
		return	
	g_unused = state [1][:]
	g_used = state [0]
	g1_usedlist = [g1_node for g1_node, g2_node in g_used]
	g2_usedlist = [g2_node for g1_node, g2_node in g_used]

	for g1_node, g2_node in g_unused:
		if g1_node in g1_usedlist or g2_node in g2_usedlist:
			state [1].remove ((g1_node, g2_node))

# Saves a state
def savestate (state):
	copyof_used = state [0][:]
	copyof_unused = state [1][:]
	if state [2] == None:
		return [copyof_used, copyof_unused, None]
	g_subgraph = state [2]
	g_subgraph_nodes = g_subgraph.nodes ()
	g_subgraph_edges = g_subgraph.edges ()
	g_copy = digraph ()
	for node in g_subgraph_nodes:
		g_copy.add_node (node, g_subgraph.node_attributes(node))
	for edge in g_subgraph_edges:
		g_copy.add_edge (edge, g_subgraph.edge_weight (edge))
	
	copy = [copyof_used, copyof_unused, g_copy]
	return copy

# McGregor algorithm to find the maximum common subgraph (mcs) of two graphs
def maxCS (g1, g2, state):
	update (state)
	global currentSize
	global savedmcs
	g_state = state
	for nodePair in g_state [1]:
		g1_node, g2_node = nodePair
		if isFeasiblePair (g1, g2, g_state, g1_node, g2_node):
			g_copy = savestate (g_state)
			new_state = addPair (g1, g2, g_copy, g1_node, g2_node)
			if len (new_state [2]) > currentSize:
				currentSize = len (new_state [2])
				savedmcs.append (new_state [2])
			if not isLeaf (g1, g2, new_state) and not pruningCondition (g1, g2, new_state):
				maxCS (g1, g2, new_state)

# Initializes global variables in each run
def init_globalvar ():
	global savedmcs
	global currentSize
	global GTable
	savedmcs = []
	currentSize = 0
	GTable = []

# Initializes a run of McGregor algo; Returns mcs
def mcsinit (g1, g2):
	init_globalvar ()
	state = [[], None, None]
	init_GTable (g1, g2)
	maxCS (g1, g2, state)
	g_subgraph = savedmcs.pop()
	return g_subgraph

