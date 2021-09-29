import csv
import sys
import torch
import torch.nn as nn
import numpy as np
import os, time, argparse
from tqdm import tqdm

def print_qerror(preds_unnorm, labels_unnorm, cuda_flag):
    qerror = []
    if cuda_flag:
        preds_unnorm = preds_unnorm.cpu()
        labels_unnorm = labels_unnorm.cpu()
    preds_unnorm = preds_unnorm.detach().numpy()
    labels_unnorm = labels_unnorm.numpy()
    for i in range(len(preds_unnorm)):
        if labels_unnorm[i] == 0:
            labels_unnorm[i] = 1
        if preds_unnorm[i] > float(labels_unnorm[i]):
            qerror.append(preds_unnorm[i] / float(labels_unnorm[i]))
        else:
            qerror.append(float(labels_unnorm[i]) / float(preds_unnorm[i]))

    #print(" Qerror: ", qerror)

    print("     =========Q-error Accuracy=========")
    print("     Median: {}".format(np.median(qerror)))
    print("     90th percentile: {}".format(np.percentile(qerror, 90)))
    print("     95th percentile: {}".format(np.percentile(qerror, 95)))
    print("     99th percentile: {}".format(np.percentile(qerror, 99)))
    print("     Max: {}".format(np.max(qerror)))
    print("     Mean: {}".format(np.mean(qerror)))
    mean = 0.0
    for i in range(len(qerror)):
        mean += qerror[i]/float(len(qerror))
    return mean




def unnormalize_torch(vals, min_val, max_val):
    vals = (vals * (max_val - min_val)) + min_val
    return vals



def unnormalize_torch_log(vals, min_val, max_val):
    min_val_norm = 0.0
    if min_val == 0:
        min_val_norm = 0
    else:
        min_val_norm = np.log(min_val)
    vals = vals * (np.log(max_val) - min_val_norm) + min_val_norm
    return torch.exp(vals)



def get_max_min_label(path):
    label = []
    label_path = os.path.join(path, 'label.txt')
    min_label = 100000000
    max_label = 0
    with open(label_path, 'rU') as f:

        data_raw = list(list(rec) for rec in csv.reader(f, delimiter=' '))
        query = []
        for i in range(len(data_raw)):
            node = data_raw[i]
            if (node[0].find('plan') == -1):
                query.append(node)
            else:
                if (len(query) > 0):
                    label.append(query)
                query = []
            if (i == len(data_raw) - 1):
                label.append(query)

        for i in range(len(label)):  # 行数
            for j in range(len(label[i])):  # 列数
                for k in range(len(label[i][j])):
                    tmp_label = int(label[i][j][k])
                    if tmp_label < min_label:
                         min_label = tmp_label
                    if tmp_label > max_label:
                         max_label = tmp_label
    if min_label == 0:
        min_label = 1.1
    return max_label, min_label


def unnormalize_torch_log_fornode(vals, min_val, max_val):
    node_prediction = []
    if min_val == 0:
        min_val_norm = 0
    else:
        min_val_norm = np.log(min_val)

    for i in range(len(vals)):
        tmp = []
        for j in range(len(vals[i])):
            vals[i][j] = vals[i][j] * (np.log(max_val) - min_val_norm) + min_val_norm
            tmp.append(torch.exp(vals[i][j]))
        node_prediction.append(tmp)

    return node_prediction

def random_split(dataset_size):

    indices = list(range(dataset_size))
    validation_split = .1
    random_seed= 42
    split = int(np.floor(validation_split * dataset_size))
    np.random.seed(random_seed)
    np.random.shuffle(indices)
    train_indices, val_indices = indices[split:], indices[:split]
    train_select = list(range(dataset_size))
    vaild_select = list(range(dataset_size))
    for i in range(dataset_size):
        train_select[i] = 0
        vaild_select[i] = 0
    for i in range(len(train_indices)):
        train_select[train_indices[i]] = 1
    for i in range(len(val_indices)):
        vaild_select[val_indices[i]] = 1

    return  train_select, vaild_select

def calculate_evaluation_orders(adjacency_list, tree_size):
    '''Calculates the node_order and edge_order from a tree adjacency_list and the tree_size.

    The TreeLSTM model requires node_order and edge_order to be passed into the model along
    with the node features and adjacency_list.  We pre-calculate these orders as a speed
    optimization.
    '''
    adjacency_list = numpy.array(adjacency_list)

    node_ids = numpy.arange(tree_size, dtype=int)

    node_order = numpy.zeros(tree_size, dtype=int)
    unevaluated_nodes = numpy.ones(tree_size, dtype=bool)

    parent_nodes = adjacency_list[:, 0]
    child_nodes = adjacency_list[:, 1]

    n = 0
    while unevaluated_nodes.any():
        # Find which child nodes have not been evaluated
        unevaluated_mask = unevaluated_nodes[child_nodes]

        # Find the parent nodes of unevaluated children
        unready_parents = parent_nodes[unevaluated_mask]

        # Mark nodes that have not yet been evaluated
        # and which are not in the list of parents with unevaluated child nodes
        nodes_to_evaluate = unevaluated_nodes & ~numpy.isin(node_ids, unready_parents)

        node_order[nodes_to_evaluate] = n
        unevaluated_nodes[nodes_to_evaluate] = False

        n += 1

    edge_order = node_order[parent_nodes]

    return node_order, edge_order


def batch_tree_input(batch):
    '''Combines a batch of tree dictionaries into a single batched dictionary for use by the TreeLSTM model.

    batch - list of dicts with keys ('features', 'node_order', 'edge_order', 'adjacency_list')
    returns a dict with keys ('features', 'node_order', 'edge_order', 'adjacency_list', 'tree_sizes')
    '''
    tree_sizes = [b['features'].shape[0] for b in batch]

    batched_features = torch.cat([b['features'] for b in batch])
    batched_node_order = torch.cat([b['node_order'] for b in batch])
    batched_edge_order = torch.cat([b['edge_order'] for b in batch])
    batched_labels = torch.cat([b['labels'] for b in batch])

    batched_adjacency_list = []
    offset = 0
    for n, b in zip(tree_sizes, batch):
        batched_adjacency_list.append(b['adjacency_list'] + offset)
        offset += n
    batched_adjacency_list = torch.cat(batched_adjacency_list)

    return {
        'features': batched_features,
        'node_order': batched_node_order,
        'edge_order': batched_edge_order,
        'adjacency_list': batched_adjacency_list,
        'tree_sizes': tree_sizes,
        'labels': batched_labels
    }





def batch_tree_input_comp(batch):
    '''Combines a batch of tree dictionaries into a single batched dictionary for use by the TreeLSTM model.

    batch - list of dicts with keys ('features', 'node_order', 'edge_order', 'adjacency_list')
    returns a dict with keys ('features', 'node_order', 'edge_order', 'adjacency_list', 'tree_sizes')
    '''
    tree_sizes = [b['operation_feat'].shape[0] for b in batch]

    batched_operation = torch.cat([b['operation_feat'] for b in batch])
    batched_table = torch.cat([b['table_feat'] for b in batch])
    batched_filter = torch.cat([b['filter_feat'] for b in batch])
    batched_join = torch.cat([b['join_feat'] for b in batch])
    batched_node_order = torch.cat([b['node_order'] for b in batch])
    batched_edge_order = torch.cat([b['edge_order'] for b in batch])
    batched_labels = torch.cat([b['labels'] for b in batch])

    batched_adjacency_list = []
    offset = 0
    for n, b in zip(tree_sizes, batch):
        batched_adjacency_list.append(b['adjacency_list'] + offset)
        offset += n
    batched_adjacency_list = torch.cat(batched_adjacency_list)

    return {
        'operation_feat': batched_operation,
        'table_feat': batched_table,
        'filter_feat': batched_filter,
        'join_feat': batched_join,
        'node_order': batched_node_order,
        'edge_order': batched_edge_order,
        'adjacency_list': batched_adjacency_list,
        'tree_sizes': tree_sizes,
        'labels': batched_labels
    }

def unbatch_tree_tensor(tensor, tree_sizes):
    '''Convenience functo to unbatch a batched tree tensor into individual tensors given an array of tree_sizes.

    sum(tree_sizes) must equal the size of tensor's zeroth dimension.
    '''
    return torch.split(tensor, tree_sizes, dim=0)