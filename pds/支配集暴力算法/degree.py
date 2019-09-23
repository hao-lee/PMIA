import networkx as nx
import glob
import matplotlib
matplotlib.use('WXAgg')
import matplotlib.pyplot as plt
import argparse, sys

COLOR_GREY = 0
COLOR_BLACK = 1
COLOR_WHITE = 2

def create_graph(source_file):
	g = nx.Graph()
	with open(source_file, "r") as f:
		next(f)
		for line in f:
			line = line.strip()
			if line == "":
				continue
			g.add_edge(line.split()[0], line.split()[1])
	return g

G = nx.Graph()
gs = []
for source_file in glob.glob("*.txt"):
	g = create_graph(source_file)
	gs.append(g)

white_nr = 0
for g in gs:
	dc=nx.degree_centrality(g)
	for node in g.nodes():
		if G.has_node(node):
			G.nodes[node]["dc"] += dc[node]
		else:
			G.add_node(node, dc=dc[node], color=COLOR_WHITE)
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
		elif G.nodes[node]["dc"] > G.nodes[max_node]["dc"]:
			max_node = node
	return max_node

def color_grey(node, threshold, depth):
	if depth == 0:
		return
	global white_nr
	for adj_node in G.adj[node]:
		if G.edges[node, adj_node]["ref"] < threshold:
			continue
		if G.nodes[adj_node]["color"] != COLOR_WHITE:
			continue
		G.nodes[adj_node]["color"] = COLOR_GREY
		white_nr -= 1
		# recursion
		color_grey(adj_node, threshold, depth-1)

# 从参数获取阈值
parser = argparse.ArgumentParser()
parser.add_argument("-th", help="Threshold", default=3, type=int)
parser.add_argument("-d", help="Recursion Depth", default=1, type=int)
args = parser.parse_args()
threshold = args.th # 边的存在时间小于阈值，不予考虑，值越大，说明对边的要求越高，选择的点越多
depth = args.d
D = []
while white_nr:
	max_node = get_max_node(G)
	D.append(max_node)
	if G.nodes[max_node]["color"] == COLOR_WHITE:
		white_nr -= 1 # 白色计数，只有白色减少才减一，灰黑的涂色对白色技术无影响
	G.nodes[max_node]["color"] = COLOR_BLACK
	color_grey(max_node, threshold, depth)

print(D)
sys.stdout.flush()

# 画图
color_vals = []
for node in G.nodes():
	if G.nodes[node]["color"] == COLOR_BLACK:
		color_vals.append("#000000")
	elif G.nodes[node]["color"] == COLOR_GREY:
		color_vals.append("#7b7b7b")
	else:
		raise Exception("Encounter white node")
plt.title("threshold=%d depth=%d" %(threshold, depth), loc="left")
nx.draw(G, cmap=plt.get_cmap('viridis'), node_color=color_vals, edge_color="#bebebe",
		with_labels=True, font_color='white')
plt.show()
