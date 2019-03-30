'''
物理层链路图
'''
# 节点类
class Pvertex:
	def __init__(self, vertex_id, vertex_name):
		self.__vertex_id = vertex_id
		self.__vertex_name = vertex_name
		self.__listpointer = None # 出边节点
		self.__incoming_vertex = [] # 入边节点
		# 以下变量用于 Dijkstra 算法
		self.__visited = None
		self.__distance = None

	def get_name(self):
		return self.__vertex_name

	def get_id(self):
		return self.__vertex_id

	def get_visited(self):
		return self.__visited

	def get_distance(self):
		return self.__distance

	def set_visited(self, visited):
		self.__visited = visited

	def set_distance(self, distance):
		self.__distance = distance

	def get_listpointer(self):
		return self.__listpointer

	def set_listpointer(self, adjlist_node):
		self.__listpointer = adjlist_node

	def add_incoming_vertex(self, incoming_vertex): # 记录一下能够直接到达本节点的源点
		self.__incoming_vertex.append(incoming_vertex)

	def get_incoming_vertex(self):
		return self.__incoming_vertex

# 邻接表节点类
class Padjlist_node:
	def __init__(self, dst_vertex_id, edge_weight, dst_vertex_name):
		self.__dst_vertex_id = dst_vertex_id
		self.__dst_vertex_name = dst_vertex_name
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
class Pgraph:
	def __init__(self):
		self.__adjlist = [] # array of pvertex
		# 以下变量用于 Dijkstra 算法，外部不可访问，仅用于算法计算
		self.__unvisited_count = None

	def add_vertex(self, vertex_name):
		v = Pvertex(len(self.__adjlist), vertex_name)
		self.__adjlist.append(v)

	def add_edge(self, src_vertex_id, dst_vertex_id, edge_weight):
		# 检测节点合法性
		self.__valid_vertex(src_vertex_id)
		self.__valid_vertex(dst_vertex_id)
		# 从 src 到 dst
		p = self.__adjlist[src_vertex_id].get_listpointer()
		node = Padjlist_node(dst_vertex_id, edge_weight,
					self.__adjlist[dst_vertex_id].get_name())
		node.set_next(p)
		self.__adjlist[src_vertex_id].set_listpointer(node)
		# 记录下来源，提高反向查找效率
		self.__adjlist[dst_vertex_id].add_incoming_vertex(src_vertex_id)

	def dump(self):
		for vertex in self.__adjlist:
			print("%d(%s):" %(vertex.get_id(), vertex.get_name()), end='')
			p = vertex.get_listpointer()
			while p:
				print(" %d(%s)" %(p.get_dst_id(), p.get_dst_name()), end='')
				p = p.get_next()
			print()

	def __valid_vertex(self, vertex):
		if vertex > len(self.__adjlist) or vertex < 0:
			raise Exception("vertex %d doesn't exist" %vertex)

	'''
	下面的两个函数用于计算最短路径
	'''
	# 返回值是 Pvertex 对象引用
	def find_min_distance_vertex(self):
		min_distance = float("inf")
		min_distance_vertex = None
		for v in self.__adjlist:
			if not v.get_visited() and v.get_distance() < min_distance:
				min_distance = v.get_distance()
				min_distance_vertex = v
		return min_distance_vertex
	# 返回值是个 id list
	def shortest_path(self, from_vertex, to_vertex):
		# 初始化所有节点的状态
		for v in self.__adjlist:
			v.set_visited(False)
			v.set_distance(float("inf"))
		# 设定起点
		# self.__adjlist[from_vertex].__visited = true
		self.__adjlist[from_vertex].set_distance(0)
		# 设定未访问的节点数
		self.__unvisited_count = len(self.__adjlist)
		# 算法核心
		prev = dict()
		while self.__unvisited_count != 0:
			'''
			如果 min_distance_vertex 是 None，则结束路径探测
			1. 对于无向图来讲，剩下的节点都是孤立节点
			2. 对于有向图来讲，剩下的节点可能是孤立节点或者是由于方向原因无法从 from_vertex 访问到
			'''
			min_distance_vertex = self.find_min_distance_vertex()
			if min_distance_vertex is None:
				break

			p = min_distance_vertex.get_listpointer()
			# 如果 min_distance_vertex 的邻接表为空，说明它向后不连接任何点，我们跳过这个点继续找下一个 min_distance_vertex
			if p is None:
				min_distance_vertex.set_visited(True)
				self.__unvisited_count -= 1
				continue

			while p:
				p_distance = self.__adjlist[p.get_dst_id()].get_distance()
				sum_distance = min_distance_vertex.get_distance() + p.get_edge_weight()
				if sum_distance < p_distance:
					self.__adjlist[p.get_dst_id()].set_distance(sum_distance)
					prev[p.get_dst_id()] = min_distance_vertex.get_id()
				p = p.get_next()
			min_distance_vertex.set_visited(True)
			self.__unvisited_count -= 1

		path = [to_vertex]
		# 若 prev 字典里没记录从哪能到 to_vertex，说明到 to_vertex 不可达
		if to_vertex not in prev:
			print("%d->%d no path" %(from_vertex, to_vertex))
			return None
		prev_v = prev[to_vertex]
		while prev_v != from_vertex:
			path.insert(0, prev_v)
			prev_v = prev[prev_v]
		path.insert(0, prev_v)
		return path

	def weight_on_edge(self, src, dst):
		p = self.__adjlist[src].get_listpointer()
		while p:
			if p.get_dst_id() == dst:
				return p.get_edge_weight()
			p = p.get_next()
		return -1

# 判断两点之间是否连通
	def is_connected(self, start, end):
		if start == end: # 起止点相同，没有物理意义，返回 False
			#print("is_connected: start and end is the same vertex %d" %start)
			return False
		stack = []
		current_id = start
		for each in self.__adjlist:
			each.set_visited(False)
		p = self.__adjlist[start].get_listpointer()
		while p:
			stack.append(p.get_dst_id())
			p = p.get_next()
		while len(stack) != 0:
			current_id = stack.pop()
			if current_id == end:
				break
			current_vertex = self.__adjlist[current_id]
			if current_vertex.get_visited():
				continue
			current_vertex.set_visited(True)
			p = self.__adjlist[current_id].get_listpointer()
			while p:
				stack.append(p.get_dst_id())
				p = p.get_next()
		if current_id == end:
			return True
		else:
			return False

	def get_input_vertex(self, v):
		in_vlist = []
		for each in self.__adjlist:
			if self.is_connected(each.get_id(), v):
				in_vlist.append(each.get_id())
		return in_vlist

	def get_output_vertex(self, v):
		out_vlist = []
		for each in self.__adjlist:
			if self.is_connected(v, each.get_id()):
				out_vlist.append(each.get_id())
		return out_vlist

	def mip(self, u, v):
		pai = 1 # 求积运算
		path = self.shortest_path(u, v) # 计算 u, v 之间的最短路径
		for i in range(len(path)-1): # 对路径上的权重求积
			pai = pai * self.weight_on_edge(path[i], path[i+1])
		return pai

	def miia(self, v, theta):
		union = set()
		for u in self.get_input_vertex(v):
			tmp_mip = self.mip(u, v)
			if tmp_mip < theta:
				continue
			union.add(u)
		return union

	def mioa(self, v, theta):
		union = set()
		for u in self.get_output_vertex(v):
			tmp_mip = self.mip(v, u)
			if tmp_mip < theta:
				continue
			union.add(u)
		return union

	def vertex_id_to_name(self, id):
		return self.__adjlist[id].get_name()

if __name__ == '__main__':
	# 创建通信图
	pgraph = Pgraph()
	# 添加通信节点
	vertex_name = ['L', 'A', 'B', 'C', 'D', 'E']
	vertex_count = 6
	theta = 0.07
	for i in range(vertex_count):
		pgraph.add_vertex(vertex_name[i])
	# 添加边和权重
	pgraph.add_edge(0, 1, 0.1)
	pgraph.add_edge(1, 2, 0.3)
	pgraph.add_edge(1, 3, 0.8)
	pgraph.add_edge(3, 4, 0.6)
	pgraph.add_edge(3, 5, 0.08)
	# 打印出数据结构看看对不对
	print("Graph adjacent list:")
	pgraph.dump()

	# 测试最短路径
	#print(pgraph.shortest_path(0, 4))
	# 测试连通性
	#print(pgraph.is_connected(5, 4))

	# 测试 MIIA 运算
	for vid in range(vertex_count):
		miia_union = pgraph.miia(vid, theta)
		print("MIIA(%s) = " %pgraph.vertex_id_to_name(vid), end='')
		if len(miia_union) == 0:
			print(" Ø".encode('utf-8').decode("gbk"))
			continue
		print("{ ", end='')
		for u in miia_union:
			print(pgraph.vertex_id_to_name(u) + ' ', end='')
		print('}')
	print()
	# 测试 MIOA 运算
	for vid in range(vertex_count):
		mioa_union = pgraph.mioa(vid, theta)
		print("MIOA(%s) = " %pgraph.vertex_id_to_name(vid), end='')
		if len(mioa_union) == 0:
			print(" Ø".encode('utf-8').decode("gbk"))
			continue
		print("{ ", end='')
		for u in mioa_union:
			print(pgraph.vertex_id_to_name(u) + ' ', end='')
		print('}')
