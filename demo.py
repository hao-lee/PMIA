'''
物理层链路图
'''
# 节点类
class Pvertex:
	def __init__(self, vertex_id, vertex_capacity):
		self.vertex_id = vertex_id
		self.vertex_capacity = vertex_capacity
		self.listpointer = None
		self.reached = False
		# 以下变量用于 Dijkstra 算法，外部不可访问，仅用于算法计算
		self.__visited = None
		self.__distance = None

# 邻接表节点类
class Padjlist_node:
	def __init__(self, dst_vertex_id, edge_weight, edge_capacity):
		self.dst_vertex_id = dst_vertex_id
		self.edge_weight = edge_weight
		self.edge_capacity = edge_capacity
		self.next = None

# 物理通信图类
class Pgraph:
	def __init__(self):
		self.adjlist = [] # array of pvertex
		# 以下变量用于 Dijkstra 算法，外部不可访问，仅用于算法计算
		self.__unvisited_count = None

	def add_vertex(self, vertex_capacity):
		v = Pvertex(len(self.adjlist), vertex_capacity)
		self.adjlist.append(v)

	def add_edge(self, src_vertex, dst_vertex_id, edge_weight, edge_capacity):
		# 检测节点合法性
		self.__valid_vertex(src_vertex)
		self.__valid_vertex(dst_vertex_id)
		# 从 src 到 dst
		p = self.adjlist[src_vertex].listpointer
		node = Padjlist_node(dst_vertex_id, edge_weight, edge_capacity)
		node.next = p
		self.adjlist[src_vertex].listpointer = node
		# 从 dst 到 src
		p = self.adjlist[dst_vertex_id].listpointer
		node = Padjlist_node(src_vertex, edge_weight, edge_capacity)
		node.next = p
		self.adjlist[dst_vertex_id].listpointer = node

	def dump(self):
		for vertex in self.adjlist:
			print(str(vertex.vertex_id) + " :", end='')
			p = vertex.listpointer
			while p:
				print(" " + str(p.dst_vertex_id), end='')
				p = p.next
			print()

	def __valid_vertex(self, vertex):
		if vertex > len(self.adjlist) or vertex < 0:
			raise Exception("vertex %d doesn't exist" %vertex)

	'''
	下面的两个函数用于计算最短路径
	'''
	# 返回值是 Pvertex 对象引用
	def find_min_distance_vertex(self):
		min_distance = float("inf")
		min_distance_vertex = None
		for v in self.adjlist:
			if v.__visited == False and v.__distance < min_distance:
				min_distance = v.__distance
				min_distance_vertex = v
		return min_distance_vertex

	def shortest_path(self, from_vertex, to_vertex):
		# 初始化所有节点的状态
		for v in self.adjlist:
			v.__visited = False
			v.__distance = float("inf")
		# 设定起点
		# self.adjlist[from_vertex].__visited = true
		self.adjlist[from_vertex].__distance = 0
		# 设定未访问的节点数
		self.__unvisited_count = len(self.adjlist)
		# 算法核心
		prev = dict()
		while self.__unvisited_count != 0:
			min_distance_vertex = self.find_min_distance_vertex()
			# 如果 min_distance_vertex 是 None，则存在孤立节点，当前暂不考虑这种情况
			p = min_distance_vertex.listpointer
			while p:
				p_distance = self.adjlist[p.dst_vertex_id].__distance
				sum_distance = min_distance_vertex.__distance + p.edge_weight
				if sum_distance < p_distance:
					self.adjlist[p.dst_vertex_id].__distance = sum_distance
					prev[p.dst_vertex_id] = min_distance_vertex.vertex_id
				p = p.next
			min_distance_vertex.__visited = True
			self.__unvisited_count -= 1
		path = [to_vertex]
		prev_v = prev[to_vertex]
		while prev_v != from_vertex:
			path.insert(0, prev_v)
			prev_v = prev[prev_v]
		path.insert(0, prev_v)
		return path



'''
社会关系图
'''
# 节点类
class Svertex:
	def __init__(self, vertex_id):
		self.vertex_id = vertex_id
		self.listpointer = None

# 邻接表节点类
class Sadjlist_node:
	def __init__(self, dst_vertex_id, edge_probability):
		self.dst_vertex_id = dst_vertex_id
		self.edge_probability = edge_probability
		self.next = None

# 社会关系图类
class Sgraph:
	'''
	注意，对于社会关系图中关系概率为0的边，我们认为此边不存在
	'''
	def __init__(self):
		self.adjlist = [] # array of svertex

	def add_vertex(self):
		v = Svertex(len(self.adjlist))
		self.adjlist.append(v)

	def add_edge(self, src_vertex, dst_vertex_id, edge_probability):
		# 检测节点合法性
		self.__valid_vertex(src_vertex)
		self.__valid_vertex(dst_vertex_id)
		# 从 src 到 dst
		p = self.adjlist[src_vertex].listpointer
		node = Sadjlist_node(dst_vertex_id, edge_probability)
		node.next = p
		self.adjlist[src_vertex].listpointer = node
		# 从 dst 到 src
		p = self.adjlist[dst_vertex_id].listpointer
		node = Sadjlist_node(src_vertex, edge_probability)
		node.next = p
		self.adjlist[dst_vertex_id].listpointer = node

	def get_social_adj_vertex(self, vertex_id):
		adjlist_node = self.adjlist[vertex_id].listpointer
		adj_vertex_list = []
		while adjlist_node:
			adj_vertex_list.append(adjlist_node.dst_vertex_id)
			adjlist_node = adjlist_node.next
		return adj_vertex_list

	def dump(self):
		for vertex in self.adjlist:
			print(str(vertex.vertex_id) + " :", end='')
			p = vertex.listpointer
			while p:
				print(" " + str(p.dst_vertex_id), end='')
				p = p.next
			print()

	def __valid_vertex(self, vertex):
		if vertex > len(self.adjlist) or vertex < 0:
			raise Exception("vertex %d doesn't exist" %vertex)


if __name__ == '__main__':
	vertex_count = 7
	# 创建通信图
	pgraph = Pgraph()
	# 添加通信节点
	for i in range(vertex_count):
		pgraph.add_vertex(0) # 测试阶段，暂时没有用到容量，设为0
	# 添加边和权重；测试阶段，没有用到边容量，故设为0
	pgraph.add_edge(0, 1, 3, 0)
	pgraph.add_edge(1, 2, 7, 0)
	pgraph.add_edge(2, 3, 1, 0)
	pgraph.add_edge(2, 4, 0, 0)
	pgraph.add_edge(3, 6, 11, 0)
	pgraph.add_edge(3, 5, 5, 0)
	pgraph.add_edge(4, 5, 22, 0)
	pgraph.add_edge(5, 6, 2, 0)
	pgraph.add_edge(6, 0, 37, 0)
	# 打印出数据结构看看对不对
	pgraph.dump()
	print()


	# 创建社会关系图
	sgraph = Sgraph()
	# 添加 5 个社会关系节点
	for i in range(vertex_count):
		sgraph.add_vertex()
	# 添加边和边通信概率
	sgraph.add_edge(0, 3, 1)
	sgraph.add_edge(3, 6, 1)
	sgraph.add_edge(3, 4, 1)
	sgraph.add_edge(6, 4, 1)
	sgraph.add_edge(4, 5, 1)
	# 打印数据结构
	sgraph.dump()

	# 假定选择0到3，计算最短路径
	#path = pgraph.shortest_path(0, 3)
	#print(path)

	# 跳数限制，由于图比较小，加了跳数限制的话算法思路不够明显，所以暂时把跳数设为无穷大
	hop_limit = float("inf")
	# 遍历通信图，开始计算种子节点
	max_path_len = 0
	max_path = None
	inf = dict() # start vertex id : number of influenced vertex
	for v in pgraph.adjlist:
		s = v.vertex_id
		p = sgraph.adjlist[s].listpointer
		while p:
			d = p.dst_vertex_id
			path = pgraph.shortest_path(s, d)
			nums = 0 # influence
			for path_vertex_id in path:
				adj_vertex_list = sgraph.get_social_adj_vertex(path_vertex_id)
				nums += len(set(adj_vertex_list))
			inf[s] = nums
			p = p.next

	max_influence = 0
	seed_vertex = None
	for vertex_id, influence in inf.items():
		if influence > max_influence:
			max_influence = influence
			seed_vertex = vertex_id
	print("种子节点：%d，影响力：%d" %(seed_vertex, max_influence))
