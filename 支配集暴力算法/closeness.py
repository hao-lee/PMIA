import networkx as nx
import glob

COLOR_GREY = 0
COLOR_BLACK = 1
COLOR_WHITE = 2

def create_graph(source_file):
	g = nx.Graph()
	with open(source_file, "r") as f:
		next(f)
		for line in f:
			g.add_edge(line.split()[0], line.split()[1])
	return g

G = nx.Graph()
gs = []
for source_file in glob.glob("*.txt"):
	g = create_graph(source_file)
	gs.append(g)

white_nr = 0
for g in gs:
	cc=nx.closeness_centrality(g)
	for node in g.nodes():
		if G.has_node(node):
			G.nodes[node]["cc"] += cc[node]
		else:
			G.add_node(node, cc=cc[node], color=COLOR_WHITE)
			white_nr += 1
	for edge in g.edges():
		if G.has_edge(edge[0], edge[1]):
			G.edges[edge[0], edge[1]]["ref"] += 1
		else:
			G.add_edge(edge[0], edge[1], ref=1)


def get_max_node(G):
	max_node = -1
	for node in G.nodes():
		if G.nodes[node]["color"] == COLOR_BLACK:
			continue
		if max_node == -1:
			max_node = node
		elif G.nodes[node]["cc"] > G.nodes[max_node]["cc"]:
			max_node = node
	return max_node

D = []
threshold = 3 # 边的存在时间小于3，不予考虑
while white_nr:
	max_node = get_max_node(G)
	D.append(max_node)
	if G.nodes[max_node]["color"] == COLOR_WHITE:
		white_nr -= 1 # 白色计数，只有白色减少才减一，灰黑的涂色对白色技术无影响
	G.nodes[max_node]["color"] = COLOR_BLACK

	for adj_node in G.adj[max_node]:
		if G.edges[max_node, adj_node]["ref"] < threshold:
			continue
		if G.nodes[adj_node]["color"] != COLOR_WHITE:
			continue
		G.nodes[adj_node]["color"] = COLOR_GREY
		white_nr -= 1

print(D)
