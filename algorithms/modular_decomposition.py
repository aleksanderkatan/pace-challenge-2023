from collections import deque

import networkx as nx
from sage.graphs.graph_decompositions.modular_decomposition import *
from sage.graphs.graph import Graph


def dfs(root):
	mods = [root]
	ver = [get_vertices(root)]
	if len(root.children) == 1:
		return mods, ver
	for ch in root.children:
		ch_mods, ch_ver = dfs(ch)
		mods = mods + ch_mods
		ver = ver + ch_ver
	return mods, ver
	

def modular_decomp(graph: nx.Graph):
	graph = Graph(graph)
	md = modular_decomposition(graph)
	# print_md_tree(md)
	mods = [md]
	ver = []
	if len(md.children) == 1:\
		return mods, ver
	for ch in md.children:
		ch_mods, ch_ver = dfs(ch)
		mods = mods + ch_mods
		ver = ver + ch_ver
	return mods, ver
	
