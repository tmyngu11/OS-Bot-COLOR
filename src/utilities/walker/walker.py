import node_settings
import time


def aStarAlgo(start_node, stop_node):
    open_set = set([start_node])
    closed_set = set()
    g = {}  # store distance from starting node
    parents = {}  # parents contains an adjacency map of all nodes

    # distance of starting node from itself is zero
    g[start_node] = 0
    # start_node is root node i.e it has no parent nodes
    # so start_node is set to its own parent node
    parents[start_node] = start_node
    # print(len(open_set))
    while len(open_set) > 0:
        n = None

        # node with lowest f() is found
        for v in open_set:
            try:
                #print(g[v])
                if n == None or g[v] + heuristic(v) < g[n] + heuristic(n):
                    n = v
            except KeyError:
                pass
        #print(v, Graph_nodes[n])
        try:
            if n == stop_node or Graph_nodes[n] == None:
                pass
        except KeyError:
            pass
        else:
            # print('n:', n)
            # m is the available paths, weight is the cost of taking path default=1
            for m in get_neighbors(n):
                # print(get_neighbors(n))
                weight = 1
                # nodes 'm' not in first and last set are added to first
                # n is set its parent
                if m not in open_set and m not in closed_set:
                    open_set.add(m)
                    parents[m] = n
                    g[m] = g[n] + weight
                    # print(open_set)


                # for each node m,compare its distance from start i.e g(m) to the
                # from start through n node
                else:
                    if g[m] > g[n] + weight:
                        # update g(m)
                        g[m] = g[n] + weight
                        # change parent of m to n
                        parents[m] = n

                        # if m in closed set,remove and add to open
                        if m in closed_set:
                            closed_set.remove(m)
                            open_set.add(m)
                            # print(open_set)

        if n == None:
            print('Path does not exist!1')
            return None

        # if the current node is the stop_node
        # then we begin reconstructin the path from it to the start_node
        if n == stop_node:
            path = []

            while parents[n] != n:
                path.append(n)
                n = parents[n]

            path.append(start_node)

            path.reverse()

            print('Path found: {}'.format(path))
            return path

        # remove n from the open_list, and add it to closed_list
        # because all of his neighbors were inspected
        open_set.remove(n)
        closed_set.add(n)

    print('Path does not exist!2')
    return None


# define fuction to return neighbor and its distance
# from the passed node
def get_neighbors(v):
    if v in Graph_nodes:
        return Graph_nodes[v]
    else:
        return None

# for simplicity we ll consider heuristic distances given
# and this function returns heuristic distance for all nodes
def heuristic(n):
    return 1

def convert_array_string(path):
    p = 0
    temp_path = []
    while p < len(path):
        temp_path.append(str(path[p]))
        p += 1
    #print(temp_path)
    return temp_path

def convert_paths_string(df_Paths):
    temp_df_Paths = []
    i = 0
    while i < len(df_Paths):
        path = convert_array_string(df_Paths[i])
        temp_df_Paths.append(path)
        i += 1
    #print(temp_df_Paths)
    return temp_df_Paths



def create_dict(node_main, path_main):
    dict = {}
    node = 0
    while node < len(node_main):
        dict[str(node)] = path_main[node]
        node += 1
    # print(dict)
    return dict

def target_path_to_output(target, node_main):
    xy_path = []
    path = 0
    while path < len(target):
        x = node_main[int(target[path])][0]
        y = node_main[int(target[path])][1]
        xy_path.append([x, y])
        path += 1
    # print(xy_path)
    return xy_path


df_Nodes = node_settings.WorldGraph_Nodes
df_Paths = node_settings.WorldGraph_Paths


df_Paths = convert_paths_string(df_Paths)
Graph_nodes = create_dict(df_Nodes, df_Paths)


def generate_path(p1, p2):
    start_time = time.time()

    start = str(df_Nodes.index(p1))
    end = str(df_Nodes.index(p2))

    # print(df_Paths[df_Nodes.index(p2)])
    print("start:", start, "| end:", end)

    target_path = aStarAlgo(start, end)

    print(target_path)

    test = target_path_to_output(target_path, df_Nodes)

    print(test)
    print("--- %s seconds ---" % (time.time() - start_time))

    return target_path

p1 = node_settings.locArdougneEBank
p2 = node_settings.locBarbarianVillage
generate_path(p1, p2)