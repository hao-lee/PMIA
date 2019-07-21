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

	def acc_duration(self, duration):
		self.__dominance += duration

	def dec_duration(self, duration):
		self.__dominance -= duration

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
			print("D(%s)=%d" %(vobj.get_name(), vobj.get_dominance()))
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
				vobj.acc_duration(duration)
				p = p.get_next()
		self.__white_count = len(self.__adjlist)

	def update_dominance(self):
		for vobj in self.__adjlist:
			vobj.reset_dominance()
			p = vobj.get_listpointer()
			while p:
				if self.__adjlist[p.get_dst_id()].get_color() == COLOR_BLACK:
					p = p.get_next()
					continue
				duration = p.get_edge_weight()[1]
				vobj.acc_duration(duration)
				p = p.get_next()

	def set_lifetime(self, lifetime):
		self.__lifetime = lifetime
		for vobj in self.__adjlist:
			vobj.acc_duration(lifetime)
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
					self.__white_count -= 1
				p = p.get_next()

			if self.__white_count == 0:
				break
			self.update_dominance()

	def get_dominance_set(self):
		names = []
		for vid in self.__dominance_set:
			names.append(self.get_name_by_id(vid))
		return names

if __name__ == '__main__':
	graph = Graph()
	vertex_names = ['a', 'b', 'c', 'd', 'e', 'f']

	graph.add_vertices(vertex_names)
	# 添加边和权重
	graph.add_edge('a', 'b', (1, 2))
	graph.add_edge('a', 'f', (3, 2))
	graph.add_edge('a', 'e', (0, 5))
	graph.add_edge('e', 'd', (2, 3))
	graph.add_edge('d', 'f', (1, 4))
	graph.add_edge('d', 'c', (0, 3))
	graph.add_edge('c', 'f', (4, 1))
	graph.add_edge('c', 'b', (3, 2))
	graph.add_edge('f', 'b', (0, 5))

	graph.dump_graph()

	graph.init_dominance()
	graph.set_lifetime(5)
	graph.dump_dominance()
	graph.greedy_pds()
	print("Dominance set:")
	print(graph.get_dominance_set())
