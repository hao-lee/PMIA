import glob
import networkx as nx
import matplotlib
matplotlib.use('WXAgg')
import matplotlib.pyplot as plt
import sys

COLOR_WHITE = 0
COLOR_GREY = 1
COLOR_BLACK = 2

# 节点类
class Vertex:
	def __init__(self, vertex_id, vertex_name):
		self.__vertex_id = vertex_id
		self.__vertex_name = vertex_name
		self.__listpointer = None
		self.__dominance = 0
		self.__color = COLOR_WHITE
		self.__dominated_timeline = None

	def get_name(self):
		return self.__vertex_name

	def get_id(self):
		return self.__vertex_id

	def get_listpointer(self):
		return self.__listpointer

	def insert_adjnode(self, vid, weight):
		v = AdjNode(vid, weight)
		v.set_next(self.__listpointer)
		self.__listpointer = v

	def acc_dominance(self, duration):
		self.__dominance += duration

	def dec_dominance(self, duration):
		self.__dominance -= duration
		if self.__dominance < 0:
			self.__dominance = 0

	def get_dominance(self):
		return self.__dominance

	def reset_dominance(self):
		self.__dominance = 0

	def set_color(self, color):
		self.__color = color

	def get_color(self):
		return self.__color

	def init_timeline(self, lifetime):
		self.__dominated_timeline = [0] * lifetime

	def dominate_timeline(self, start, end):
		for i in range(start, end):
			self.__dominated_timeline[i] = 1

	def timeline_is_dominated(self):
		for i in self.__dominated_timeline:
			if i == 0:
				return False
		return True

# 邻接表节点类
class AdjNode:
	def __init__(self, dst_vertex_id, edge_weight):
		self.__dst_vertex_id = dst_vertex_id
		self.__edge_weight = edge_weight
		self.__next = None

	def get_dst_id(self):
		return self.__dst_vertex_id

	def get_dst_name(self):
		return self.__dst_vertex_name

	def get_edge_weight(self):
		return self.__edge_weight

	def get_next(self):
		return self.__next

	def set_next(self, n):
		self.__next = n

# 物理通信图类
class Graph:
	def __init__(self):
		self.__adjlist = [] # array of pvertex
		self.__count = 0
		self.__vertex_names = None
		self.__lifetime = 0
		self.__white_count = 0
		self.__dominance_set = set()
		self.__debug = False
		self.__color_process = []

	def enable_debug(self):
		self.__debug = True

	def disable_debug(self):
		self.__debug = False

	def get_vidlist(self):
		return [vid for vid in range(self.__count)]

	def add_vertices(self, vertex_names):
		self.__vertex_names = vertex_names
		for idx, name in enumerate(vertex_names):
			v = Vertex(idx, name)
			self.__adjlist.append(v)

	def add_edge(self, name1, name2, weight):
		vid1 = self.__vertex_names.index(name1)
		vid2 = self.__vertex_names.index(name2)
		# 检测节点合法性
		self.__valid_vertex(vid1)
		self.__valid_vertex(vid2)
		self.__adjlist[vid1].insert_adjnode(vid2, weight)
		self.__adjlist[vid2].insert_adjnode(vid1, weight)

	def dump_graph(self):
		print("Adjacent list of Graph:")
		for vobj in self.__adjlist:
			print("%s:" %vobj.get_name(), end='')
			p = vobj.get_listpointer()
			while p:
				print(" %s" %self.get_name_by_id(p.get_dst_id()), end='')
				p = p.get_next()
			print()
		print()

	def dump_dominance(self):
		print("Dominance of each vertex:")
		for vobj in self.__adjlist:
			print("D(%s)=%d\t" %(vobj.get_name(), vobj.get_dominance()), end="")
			if vobj.get_color() == COLOR_WHITE:
				print("white")
			elif vobj.get_color() == COLOR_BLACK:
				print("black")
			else:
				print("grey")
		print()

	def __valid_vertex(self, vid):
		if vid > len(self.__adjlist) or vid < 0:
			raise Exception("vertex %d doesn't exist" %vid)

	def weight_on_edge(self, src, dst):
		p = self.__adjlist[src].get_listpointer()
		while p:
			if p.get_dst_id() == dst:
				return p.get_edge_weight()
			p = p.get_next()
		return -1

	def get_name_by_id(self, id):
		return self.__adjlist[id].get_name()

	def init_dominance(self):
		for vobj in self.__adjlist:
			p = vobj.get_listpointer()
			while p:
				duration = p.get_edge_weight()[1]
				vobj.acc_dominance(duration)
				p = p.get_next()
		self.__white_count = len(self.__adjlist)

	def update_dominances(self):
		for vobj in self.__adjlist:
			if vobj.get_color() == COLOR_BLACK:
				continue
			self.update_dominance(vobj)

	def update_dominance(self, vobj):
		p = vobj.get_listpointer()
		while p:
			# vobj 邻接了 p 这个黑节点，此边的支配作用消失
			if self.__adjlist[p.get_dst_id()].get_color() == COLOR_BLACK:
				vobj.dec_dominance(p.get_edge_weight()[1])
				p = p.get_next()
				continue
			# 判断 p 这个邻接点是否与黑节点相邻，如果相邻则返回被黑掉的区间
			(vobj_adj_adjoin_black, blacked_weight) = self.is_adj_with_black(p.get_dst_id())
			# p 与黑节点不相邻，vobj <-> p 的边不受影响，继续遍历下一个邻接点
			if not vobj_adj_adjoin_black:
				p = p.get_next()
				continue
			# vobj 不能完全支配其邻接点 p，减去被黑掉的区间长度
			delta = self.intersect(blacked_weight, p.get_edge_weight())
			# 如果交集为空，则 vobj 的支配值不受影响；若非空，则 vobj 的支配值要减掉被黑的部分
			if delta is not None:
				vobj.dec_dominance(delta[1])
			p = p.get_next()

		if self.__debug:
			print("========= Dump dominance for debugging =========")
			self.dump_dominance()

	# 如果 vid 不邻接黑节点，则返回 False，否则算出邻接黑节点的边的并集
	def is_adj_with_black(self, vid):
		p = self.__adjlist[vid].get_listpointer()
		ret = False
		union_weight = None
		while p:
			if self.__adjlist[p.get_dst_id()].get_color() == COLOR_BLACK:
				ret = True
				union_weight = self.union(union_weight, p.get_edge_weight())
			p = p.get_next()
		return (ret, union_weight)

	def union(self, weight1, weight2):
		if weight1 is None:
			return weight2
		if weight2 is None:
			return weight1
		s1 = weight1[0]
		d1 = weight1[1]
		s2 = weight2[0]
		d2 = weight2[1]
		s = s1 if s1 < s2 else s2
		e1 = s1+d1
		e2 = s2+d2
		e = e1 if e1 > e2 else e2
		return (s, e - s)

	def intersect(self, weight1, weight2):
		if weight1 is None or weight2 is None:
			return None
		s1 = weight1[0]
		d1 = weight1[1]
		s2 = weight2[0]
		d2 = weight2[1]
		s = s1 if s1 > s2 else s2
		e1 = s1+d1
		e2 = s2+d2
		e = e1 if e1 < e2 else e2
		if s == e:
			return None
		return (s, e - s)

	def set_lifetime(self, lifetime):
		self.__lifetime = lifetime
		for vobj in self.__adjlist:
			vobj.acc_dominance(lifetime)
			vobj.init_timeline(lifetime)

	def greedy_pds(self):
		while True:
			max_dominance = -1
			max_dominance_vid = -1
			for vobj in self.__adjlist:
				if vobj.get_color() == COLOR_BLACK:
					continue
				if vobj.get_dominance() > max_dominance:
					max_dominance = vobj.get_dominance()
					max_dominance_vid = vobj.get_id()
			# Add Dominance vertex
			self.__dominance_set.add(max_dominance_vid)
			# record process
			self.__color_process.append("[%s]" %self.get_name_by_id(max_dominance_vid))
			# Make sure: white -> black
			if self.__adjlist[max_dominance_vid].get_color() == COLOR_WHITE:
				self.__white_count -= 1
			self.__adjlist[max_dominance_vid].set_color(COLOR_BLACK)
			# set grey vertex
			p = self.__adjlist[max_dominance_vid].get_listpointer()
			while p:
				if self.__adjlist[p.get_dst_id()].get_color() != COLOR_WHITE:
					p = p.get_next()
					continue
				weight = p.get_edge_weight()
				start = weight[0]
				end = weight[0] + weight[1]
				self.__adjlist[p.get_dst_id()].dominate_timeline(start, end)
				if self.__adjlist[p.get_dst_id()].timeline_is_dominated():
					self.__adjlist[p.get_dst_id()].set_color(COLOR_GREY)
					self.__color_process.append(self.get_name_by_id(p.get_dst_id()))
					self.__white_count -= 1
				p = p.get_next()

			if self.__white_count == 0:
				break
			self.update_dominances()

	def get_dominance_set(self):
		names = []
		for vid in self.__dominance_set:
			names.append(self.get_name_by_id(vid))
		return names

	def get_color_process(self):
		return self.__color_process

	def draw(self):
		g = nx.Graph()
		for vobj in self.__adjlist:
			p = vobj.get_listpointer()
			while p:
				g.add_edge(vobj.get_name(), self.get_name_by_id(p.get_dst_id()))
				p = p.get_next()
		color_vals = []
		for node in g.nodes():
			vid = self.__vertex_names.index(node)
			if self.__adjlist[vid].get_color() == COLOR_BLACK:
				color_vals.append("#000000")
			elif self.__adjlist[vid].get_color() == COLOR_GREY:
				color_vals.append("#7b7b7b")
			else:
				raise Exception("Encounter white node")
		nx.draw(g, cmap=plt.get_cmap('viridis'), node_color=color_vals, edge_color="#bebebe",
		with_labels=True, font_color='white')
		plt.show()

if __name__ == '__main__':
	graph = Graph()
	vertex_names = set()
	for source_file in glob.glob("[0-9]*.txt"):
		with open(source_file, "r") as f:
			next(f)
			for line in f:
				line = line.strip()
				if line == "":
					continue
				vertex_names.add(line.split()[0])
				vertex_names.add(line.split()[1])
	# 需要转为list，程序要用到list的特性，使用节点名称反查节点下标，参见add_edge函数
	vertex_names = list(vertex_names)
	# 排个序，当两个节点的支配值相等时，节点在__adjlist中的顺序直接影响谁会被选中，所以如果不排序
	# 则每次运行程序的结果都不一样
	vertex_names = sorted(list(vertex_names))
	graph.add_vertices(vertex_names)

	preprocess = dict()
	time_point = 0
	for source_file in glob.glob("[0-9]*.txt"):
		with open(source_file, "r") as f:
			next(f)
			for line in f:
				line = line.strip()
				if line == "":
					continue
				e = (line.split()[0], line.split()[1])
				# 无向图，("a", "b") 和 ("b", "a") 是一个边
				e = tuple(sorted(e)) # 排个序，这样就不受边端点顺序的影响了
				if e not in preprocess:
					preprocess[e] = (time_point, 1)
				else:
					# 如果时间段不连续，注释掉317 318两行
					if time_point - preprocess[e][0] != preprocess[e][1]:
						raise Exception("%s is not contiguous in timeline" %str(e))
					preprocess[e] = (preprocess[e][0], preprocess[e][1]+1)
		time_point += 1
	#print(preprocess)
	# 添加边和权重
	for e, w in preprocess.items():
		if int(w[0]) + int(w[1]) > time_point:
			raise Exception("%s is invalid, weight=%s. Maybe this is because "
							"there are some duplicate edges in the same file"
							%(str(e), str(w)))
		#print(e[0], e[1], w)
		graph.add_edge(e[0], e[1], w)

	#graph.dump_graph()

	graph.init_dominance()
	graph.set_lifetime(time_point)
	#graph.dump_dominance()
	# 如果需要打印每一次 dominance 更新的过程，可以用下面的语句开启调试
	#graph.enable_debug()
	graph.greedy_pds()
	d = graph.get_dominance_set()
	print("Dominance set: (%d)" %len(d))
	print(d)
	print("Color process")
	print("".join(graph.get_color_process()))
	sys.stdout.flush()
	# 画图
	graph.draw()
