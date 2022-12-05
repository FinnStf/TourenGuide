#
# convert a python boolean to a javascript boolean
#
def convert_booleans_in_saved_graph(graphs):
    graphs_modified = []

    for graph in graphs:
        if graph["visible"]:
            graph["visible"] = "true"
        else:
            graph["visible"] = "false"
        graphs_modified.append(graph)
    return graphs_modified
