import torch

from treelstm import TreeLSTM, calculate_evaluation_orders
from treelstm import batch_tree_input

def _label_node_index(node, n=0):
    node['index'] = n
    for child in node['children']:
        n += 1
        _label_node_index(child, n)


def _gather_node_attributes(node, key):
    features = [node[key]]
    for child in node['children']:
        features.extend(_gather_node_attributes(child, key))
    return features


def _gather_adjacency_list(node):
    adjacency_list = []
    for child in node['children']:
        adjacency_list.append([node['index'], child['index']])
        adjacency_list.extend(_gather_adjacency_list(child))

    return adjacency_list


def convert_tree_to_tensors(tree, device=torch.device('cpu')):
    # Label each node with its walk order to match nodes to feature tensor indexes
    # This modifies the original tree as a side effect
    _label_node_index(tree)

    features = _gather_node_attributes(tree, 'features')
    labels = _gather_node_attributes(tree, 'labels')
    adjacency_list = _gather_adjacency_list(tree)

    node_order, edge_order = calculate_evaluation_orders(adjacency_list, len(features))

    return {
        'features': torch.tensor(features, device=device, dtype=torch.float32),
        'labels': torch.tensor(labels, device=device, dtype=torch.float32),
        'node_order': torch.tensor(node_order, device=device, dtype=torch.int64),
        'adjacency_list': torch.tensor(adjacency_list, device=device, dtype=torch.int64),
        'edge_order': torch.tensor(edge_order, device=device, dtype=torch.int64),
    }


#A tree with N nodes, E edges, F features

#features - N*M tensor containing the features for each nodes

#adjacency_list E*2 containing the node indexes of the parent node and child node for every connect in tree

#node_order - A size N tensor containing the calculation step at which a node can be evaluated
# Note that the order that node data is stored in features and node_order must be identical

#edge_order - A size E tensor containing the calculation step at which each entry in the adjacency_list is needed in order to retrieve the child nodes for a current node.
# Note that the order that parent-child data is stored in adjacency_list and edge_order must be identical.




if __name__ == '__main__':
    # Toy example
    # tree = {
    #     'features': [0, 0], 'labels': [0], 'children': [
    #         {'features': [0, 1], 'labels': [1], 'children': [
    #             {'features': [0, 2], 'labels': [2], 'children': [
    #                 {'features': [0, 4], 'labels': [4], 'children': []},
    #                 {'features': [0, 5], 'labels': [5], 'children': []}
    #             ]},
    #             {'features': [0, 3], 'labels': [3], 'children': []}
    #         ]},
    #     ],
    # }
    tree = {
        'features': [11, 0], 'labels': [1], 'children': [
            {'features': [11, 1], 'labels': [0], 'children': [
                {'features': [11, 2], 'labels': [0], 'children': []},
                {'features': [11, 3], 'labels': [0], 'children': []}
            ]},
            {'features': [11, 4], 'labels': [0], 'children': []},
        ],
    }


    tree2 = {
        'features': [0, 6], 'labels': [0], 'children': [
            {'features': [0, 7], 'labels': [1], 'children': [
                {'features': [0, 8], 'labels': [2], 'children': [
                    {'features': [0, 10], 'labels': [4], 'children': []},
                    {'features': [0, 11], 'labels': [5], 'children': []}
                ]},
                {'features': [0, 9], 'labels': [3], 'children': []}
            ]},
        ],
    }



    data = convert_tree_to_tensors(tree)
    print(" data: ", data)

    data2 = convert_tree_to_tensors(tree2)
    new_batch = data, data2


    #print("data2: ", data)
    #print(" new_batch: ", new_batch)

    dic = batch_tree_input(new_batch)


    model = TreeLSTM(2, 1).train()

    loss_function = torch.nn.BCEWithLogitsLoss()
    optimizer = torch.optim.Adam(model.parameters())

    for n in range(1):
        optimizer.zero_grad()

        h, c = model(
            data['features'],
            data['node_order'],
            data['adjacency_list'],
            data['edge_order']
        )

        labels = data['labels']

        loss = loss_function(h, labels)
        loss.backward()
        optimizer.step()

        print("Iteration {n+1} Loss: {loss}")