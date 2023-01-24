from collections import deque

import networkx as nx

PRIME = 0
SERIES = 1
PARALLEL = 2
NORMAL = 3
FOREST = -1
LEFT_SPLIT = 1
RIGHT_SPLIT = 2
BOTH_SPLIT = 3
NO_SPLIT = 0
LEFT_OF_SOURCE = -1
RIGHT_OF_SOURCE = 1
SOURCE = 0


class NodeInfo:
    def __init__(self, node_type):
        self.node_type = node_type
        self.node_split = NO_SPLIT
        self.index_in_root = -1
        self.comp_num = -1
        self.is_separated = False

    def set_node_split(self, node_split):
        if self.node_split == NO_SPLIT:
            self.node_split = node_split
        elif ((self.node_split == LEFT_SPLIT and
               node_split == RIGHT_SPLIT) or
              (self.node_split == RIGHT_SPLIT and
               node_split == LEFT_SPLIT)):
            self.node_split = BOTH_SPLIT

    def has_left_split(self):
        return self.node_split == LEFT_SPLIT or self.node_split == BOTH_SPLIT

    def has_right_split(self):
        return self.node_split == RIGHT_SPLIT or self.node_split == BOTH_SPLIT

    def __str__(self):
        if self.node_type == SERIES:
            return "SERIES"
        elif self.node_type == PARALLEL:
            return "PARALLEL"
        elif self.node_type == PRIME:
            return "PRIME"
        elif self.node_type == FOREST:
            return "FOREST"
        else:
            return "NORMAL"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.node_type == other.node_type


def connected_components(graph: nx.Graph):
    visited = {}
    components = []
    for v in graph.nodes:
        if v in visited:
            continue
        cur_nodes = []
        q = [v]
        while len(q) > 0:
            vertex = q[0]
            q = q[1:]
            cur_nodes.append(v)
            visited[v] = True
            for v in graph.neighbors(vertex):
                if v not in visited:
                    visited[v] = True
                    q.append(v)
        components.append(cur_nodes)
    return components


def is_connected(graph: nx.Graph):
    return len(connected_components(graph)) == 1

def complement(graph: nx.Graph) -> nx.Graph:
    gg = graph.copy()
    gg.clear_edges()
    for u in graph:
        for v in graph:
            if u == v:
                continue
            if not graph.has_edge(u, v) and not gg.has_edge(u, v):
                gg.add_edge(u, v)
    return gg

def modular_decomposition(graph: nx.Graph):
    if graph.is_directed():
        raise ValueError("Graph must be undirected")

    if graph.order() == 0:
        return create_prime_node()

    if graph.order() == 1:
        root = create_normal_node(next(graph.nodes.__iter__()))
        return root
    if not is_connected(graph):
        components = connected_components(graph)
        root = create_parallel_node()
        for component in components:
            root[1].append(modular_decomposition(graph.subgraph(component)))
        return root
    elif is_connected(complement(graph)):
        root = create_prime_node()
    else:
        root = create_series_node()

    prev_level_distance = -1
    prev_level_list = []

    vertex_dist = {}

    vertex_status = {}
    vertex_status[next(graph.nodes.__iter__())] = SOURCE

    q = [(next(graph.nodes.__iter__()), 0)]

    while len(q) > 0:
        vertex, distance = q[0]
        q = q[1:]
        vertex_dist[vertex] = distance
        for v in graph.neighbors(vertex):
            if v not in vertex_dist:
                vertex_dist[v] = distance + 1
                q.append((v, distance+1))

        if distance == 1:
            vertex_status[vertex] = LEFT_OF_SOURCE
        elif distance != 0:
            vertex_status[vertex] = RIGHT_OF_SOURCE

        if distance != prev_level_distance:
            if prev_level_list:
                root[1].append(modular_decomposition(
                    graph.subgraph(prev_level_list))
                )
            prev_level_list = []
            prev_level_distance = distance
        prev_level_list.append(vertex)

    root[1].append(modular_decomposition(graph.subgraph(prev_level_list)))

    root[1][0], root[1][1] = root[1][1], root[1][0]

    root[0].node_type = FOREST
    clear_node_split_info(root)
    number_cocomponents(root, vertex_status)
    number_components(root, vertex_status)
    refine(graph, root, vertex_dist, vertex_status)
    promote_left(root)
    promote_right(root)
    promote_child(root)
    assembly(graph, root, vertex_status, vertex_dist)

    if root[0].node_type == FOREST:
        return root[1][0]
    else:
        return root


def number_components(root, vertex_status):
    comp_num = 0
    flag = False

    if not root:
        return ValueError("Input forest {} is empty".format(root))

    for tree in root[1]:


        if tree[0].node_type == NORMAL and \
                vertex_status[tree[1][0]] == SOURCE:
            flag = True
            continue

        if not flag:
            continue

        comp_num += recursively_number_cocomponents(tree, comp_num, PARALLEL)


def number_cocomponents(root, vertex_status):
    cocomp_num = 0
    for tree in root[1]:

        if tree[0].node_type == NORMAL and \
                vertex_status[tree[1][0]] == SOURCE:
            break
        cocomp_num += recursively_number_cocomponents(tree, cocomp_num,
                                                      SERIES)


def recursively_number_cocomponents(tree, cocomp_num, by_type):


    def number_subtree(tree, number):
        tree[0].comp_num = number
        if tree[0].node_type != NORMAL:
            for subtree in tree[1]:
                number_subtree(subtree, number)

    orig_cocomp_num = cocomp_num

    if tree[0].node_type == by_type:
        tree[0].comp_num = cocomp_num
        for subtree in tree[1]:
            number_subtree(subtree, cocomp_num)
            cocomp_num += 1
    else:

        number_subtree(tree, cocomp_num)
        cocomp_num += 1
    return cocomp_num - orig_cocomp_num


def assembly(graph, root, vertex_status, vertex_dist):

    mu = {}

    source_index = -1

    vertices_in_component = {}

    update_comp_num(root)

    for index, component in enumerate(root[1]):

        if component[0].node_type == NORMAL and \
                vertex_status[component[1][0]] == SOURCE:
            source_index = root[1].index(component)

        vertices_in_component[index] = get_vertices(component)
        component[0].index_in_root = index

    for index, component in enumerate(root[1]):
        if index < source_index:
            mu[index] = compute_mu_for_co_component(graph, index,
                                                    source_index, root,
                                                    vertices_in_component)
        elif index > source_index:
            mu[index] = compute_mu_for_component(graph, index,
                                                 source_index, root,
                                                 vertices_in_component)

    mu[source_index] = root[1][source_index]

    left = root[1][source_index]

    right = root[1][source_index]

    while len(root[1]) != 1:
        result, source_index = check_series(root, left, right,
                                            source_index, mu)
        if result:
            left = root[1][source_index][1][0]
            continue

        result, source_index = check_parallel(graph, root, left, right,
                                              source_index, mu, vertex_dist,
                                              vertices_in_component)
        if result:
            right = root[1][source_index][1][-1]
            continue

        result, source_index = check_prime(graph, root, left, right,
                                           source_index, mu, vertex_dist,
                                           vertices_in_component)
        if result:
            if root[1][source_index][1][0][0].index_in_root != -1:
                left = root[1][source_index][1][0]
            if root[1][source_index][1][-1][0].index_in_root != -1:
                right = root[1][source_index][1][-1]


def update_comp_num(root):
    if root[0].node_type != NORMAL:
        root[0].comp_num = root[1][0][0].comp_num
        for child in root[1]:
            update_comp_num(child)


def check_prime(graph, root, left, right,
                source_index, mu, vertex_dist,
                vertices_in_component):
    new_right_index = source_index + 1 if source_index + 1 < len(root[1]) \
        else source_index

    new_left_index = source_index - 1 if source_index - 1 >= 0 \
        else source_index

    left_queue = deque()

    right_queue = deque()

    if new_left_index != source_index:
        left_queue.append(new_left_index)
    if new_right_index != source_index:
        right_queue.append(new_right_index)

    while left_queue or right_queue:

        if left_queue:

            left_index = left_queue.popleft()

            while new_right_index < len(root[1]) - 1 and \
                    root[1][new_right_index][0].index_in_root < \
                    mu[left_index][0].index_in_root:
                new_right_index += 1
                right_queue.append(new_right_index)

            while has_left_cocomponent_fragment(root, left_index):
                if left_index >= 1:
                    left_index -= 1
                    if new_left_index > left_index:
                        left_queue.append(left_index)
                    new_left_index = min(left_index, new_left_index)

        if right_queue:

            right_index = right_queue.popleft()

            while new_left_index > 0 and \
                    root[1][new_left_index][0].index_in_root > \
                    mu[right_index][0].index_in_root:
                new_left_index -= 1
                left_queue.append(new_left_index)

            while has_right_component_fragment(root, right_index) or \
                    has_right_layer_neighbor(graph, root,
                                             right_index, vertex_dist,
                                             vertices_in_component):

                if has_right_layer_neighbor(graph, root,
                                            right_index, vertex_dist,
                                            vertices_in_component):
                    new_left_index = 0
                    new_right_index = len(root[1]) - 1
                    break

                if right_index + 1 < len(root[1]):
                    right_index += 1
                    if new_right_index < right_index:
                        right_queue.append(right_index)
                    new_right_index = max(right_index, new_right_index)

    node = create_prime_node()

    for temp in range(new_left_index, new_right_index + 1):
        node[1].append(root[1][temp])

    root[1][new_left_index:new_right_index + 1] = []

    root[1].insert(new_left_index, node)

    return [True, new_left_index]


def check_parallel(graph, root, left, right,
                   source_index, mu, vertex_dist,
                   vertices_in_component):

    new_right_index = source_index

    while new_right_index + 1 < len(root[1]):

        if has_right_component_fragment(root, new_right_index + 1):
            break

        if has_right_layer_neighbor(graph, root, new_right_index + 1,
                                    vertex_dist, vertices_in_component):
            break

        i = root[1][new_right_index + 1][0].index_in_root

        if mu[i][0].index_in_root >= left[0].index_in_root:
            new_right_index += 1
        else:
            break

    if source_index != new_right_index:
        node = create_parallel_node()
        temp = source_index
        for temp in range(source_index, new_right_index + 1):

            if root[1][temp][0].node_type == PARALLEL:
                for tree in root[1][temp][1]:
                    node[1].append(tree)
                    tree[0].index_in_root = root[1][temp][0].index_in_root
            else:
                node[1].append(root[1][temp])

        root[1][source_index:new_right_index + 1] = []

        root[1].insert(source_index, node)

        return [True, source_index]

    return [False, source_index]


def check_series(root, left, right, source_index, mu):
    new_left_index = source_index

    while new_left_index > 0:

        if has_left_cocomponent_fragment(root, new_left_index - 1):
            break

        i = root[1][new_left_index - 1][0].index_in_root

        if mu[i][0].index_in_root <= right[0].index_in_root:
            new_left_index -= 1
        else:
            break

    if source_index != new_left_index:
        node = create_series_node()
        for temp in range(new_left_index, source_index + 1):

            if root[1][temp][0].node_type == SERIES:
                for tree in root[1][temp][1]:
                    tree[0].index_in_root = root[1][temp][0].index_in_root
                    node[1].append(tree)
            else:
                node[1].append(root[1][temp])

        root[1][new_left_index:source_index + 1] = []

        root[1].insert(new_left_index, node)

        return [True, new_left_index]

    return [False, new_left_index]


def has_left_cocomponent_fragment(root, cocomp_index):
    for index in range(cocomp_index):
        if root[1][index][0].comp_num == root[1][cocomp_index][0].comp_num:
            return True
    return False


def has_right_component_fragment(root, comp_index):
    for index in range(comp_index + 1, len(root[1])):
        if root[1][index][0].comp_num == root[1][comp_index][0].comp_num:
            return True
    return False


def has_right_layer_neighbor(graph, root, comp_index,
                             vertex_dist, vertices_in_component):
    for index in range(comp_index + 1, len(root[1])):

        if ((vertex_dist[get_vertex_in(root[1][index])] >
             vertex_dist[get_vertex_in(root[1][comp_index])]
        ) and
                (is_component_connected(graph, root[1][index][0].index_in_root,
                                        root[1][comp_index][0].index_in_root,
                                        vertices_in_component)
                )):
            return True

    return False


def get_vertex_in(tree):
    while tree[0].node_type != NORMAL:
        tree = tree[1][0]
    return tree[1][0]


def compute_mu_for_co_component(graph, component_index, source_index,
                                root, vertices_in_component):

    for index in range(len(root[1]) - 1, source_index, -1):
        if is_component_connected(graph, component_index,
                                  index, vertices_in_component):
            return root[1][index]

    return root[1][source_index]


def compute_mu_for_component(graph, component_index, source_index,
                             root, vertices_in_component):

    mu_for_component = root[1][0]

    for index in range(0, source_index):
        if mu_for_component == root[1][index] and \
                is_component_connected(graph, component_index,
                                       index, vertices_in_component):
            mu_for_component = root[1][index + 1]

    return mu_for_component


def is_component_connected(graph, index1, index2, vertices_in_component):

    vertices = vertices_in_component[index1]
    index2_vertices_set = set(vertices_in_component[index2])

    for vertex in vertices:
        neighbors = graph.neighbors(vertex)
        if not index2_vertices_set.isdisjoint(neighbors):
            return True
    return False


def get_vertices(component):
    vertices = []

    def recurse_component(root, vertices):
        if root[0].node_type == NORMAL:
            vertices.append(root[1][0])
            return
        for tree in root[1]:
            recurse_component(tree, vertices)

    recurse_component(component, vertices)
    return vertices


def promote_left(root):
    q = deque()

    for tree in root[1]:
        q.append([root, tree])

    while q:
        parent, child = q.popleft()
        if child[0].node_type == NORMAL:
            continue

        to_remove = []

        index = parent[1].index(child)

        for tree in child[1]:
            if tree[0].has_left_split() and child[0].has_left_split():
                parent[1].insert(index, tree)
                index += 1
                to_remove.append(tree)
                q.append([parent, tree])
            else:
                q.append([child, tree])

        for tree in to_remove:
            child[1].remove(tree)


def promote_right(root):
    q = deque()

    for tree in root[1]:
        q.append([root, tree])

    while q:

        parent, child = q.popleft()

        if child[0].node_type == NORMAL:
            continue

        to_remove = []

        index = parent[1].index(child)

        for tree in child[1]:
            if tree[0].has_right_split() and child[0].has_right_split():
                parent[1].insert(index + 1, tree)
                to_remove.append(tree)
                q.append([parent, tree])
            else:
                q.append([child, tree])

        for tree in to_remove:
            child[1].remove(tree)


def promote_child(root):
    q = deque()

    for tree in root[1]:
        q.append([root, tree])

    while q:

        parent, child = q.popleft()

        if child[0].node_type == NORMAL:
            continue

        if len(child[1]) == 1 and (child[0].node_split != NO_SPLIT or
                                   child[0].node_type == FOREST):

            tree = child[1][0]
            index = parent[1].index(child)
            parent[1].insert(index, tree)
            parent[1].remove(child)
            q.append([parent, tree])
        # if child node has no children
        elif ((not child[1]) and child[0].node_split != NO_SPLIT):
            # remove the child node
            parent[1].remove(child)
        else:
            for tree in child[1]:
                q.append([child, tree])


def clear_node_split_info(root):

    root[0].node_split = NO_SPLIT

    if root[0].node_type != NORMAL:
        for subroot in root[1]:
            clear_node_split_info(subroot)


def refine(graph: nx.Graph, root, vertex_dist, vertex_status):
    x_used = []

    for v in graph.nodes:
        if v in vertex_status and vertex_status[v] == SOURCE:
            continue

        x = {u for u in graph.neighbors(v)
             if vertex_dist[u] != vertex_dist[v]}

        if x not in x_used:
            x_used.append(x)
            maximal_subtrees_with_leaves_in_x(root, v, x,
                                              vertex_status, False, 0)

    get_child_splits(root)


def get_child_splits(root):
    if root[0].node_type != NORMAL:
        for tree in root[1]:
            get_child_splits(tree)
            root[0].set_node_split(tree[0].node_split)


def maximal_subtrees_with_leaves_in_x(root, v, x, vertex_status,
                                      tree_left_of_source, level):

    def update_node_info(node, node_type, node_split, comp_num, subtree_list):
        node[0].node_type = node_type
        node[0].node_split = node_split
        node[0].comp_num = comp_num
        node[1] = subtree_list

    return_split = NO_SPLIT

    if root[0].node_type == FOREST:

        left_flag = True

        for tree in root[1]:
            if tree[0].node_type == NORMAL and tree[1][0] in vertex_status \
                    and vertex_status[tree[1][0]] == SOURCE:
                left_flag = False
            subtree_result = maximal_subtrees_with_leaves_in_x(tree, v, x,
                                                               vertex_status,
                                                               left_flag,
                                                               level)
            if subtree_result:
                root[0].set_node_split(subtree_result[1])

    elif root[0].node_type != NORMAL:

        flag = True
        split_flag = False
        Ta = []
        Tb = []

        for subtree in root[1]:
            subtree_result = maximal_subtrees_with_leaves_in_x(subtree, v, x,
                                                               vertex_status,
                                                               tree_left_of_source,
                                                               level + 1)
            if subtree_result:
                flag = flag and subtree_result[0]
                root[0].set_node_split(subtree_result[1])
                if subtree_result[0]:
                    Ta.append(subtree)
                    split_flag = True
                else:
                    Tb.append(subtree)

        if root[0].node_type == PRIME:
            for prime_subtree in root[1]:
                prime_subtree[0].set_node_split(root[0].node_split)

        if flag:
            return [True, root[0].node_split]
        elif split_flag:
            split = LEFT_SPLIT
            if vertex_status[v] == RIGHT_OF_SOURCE and not tree_left_of_source:
                split = RIGHT_SPLIT
            root[0].set_node_split(split)

            if root[0].node_type == PRIME:
                for subtree in root[1]:
                    subtree[0].set_node_split(split)
                return [False, split]

            if root[0].is_separated:
                return [flag, root[0].node_split]

            node_type = root[0].node_type
            root[0].is_separated = True

            root[1] = []

            a = create_parallel_node()
            update_node_info(a, node_type, root[0].node_split,
                             Ta[0][0].comp_num, Ta)
            b = create_parallel_node()
            update_node_info(b, node_type, root[0].node_split,
                             Tb[0][0].comp_num, Tb)
            root[1].append(a)
            root[1].append(b)

        return_split = root[0].node_split
        return [flag, return_split]
    elif root[1][0] in x:
        return [True, root[0].node_split]
    else:
        return [False, root[0].node_split]


def create_prime_node():
    return [NodeInfo(PRIME), []]


def create_parallel_node():
    return [NodeInfo(PARALLEL), []]


def create_series_node():
    return [NodeInfo(SERIES), []]


def create_normal_node(vertex):
    return [NodeInfo(NORMAL), [vertex]]


def print_md_tree(root):

    def recursive_print_md_tree(root, level):
        if root[0].node_type != NORMAL:
            print("{}{}".format(level, str(root[0])))
            for tree in root[1]:
                recursive_print_md_tree(tree, level + " ")
        else:
            print("{}{}".format(level, str(root[1][0])))

    recursive_print_md_tree(root, "")

