import numpy as np
import os, time, argparse
from tqdm import tqdm
import csv
import torch
import torch.nn as nn
import torch.optim as optim
import torch.utils.data as data
import torch.nn.functional as F
from copy import deepcopy


def load_train_data(path, selected_sample, min_label, max_label):
    feature = []
    adjacency_list = []
    node_order = []
    edge_order = []
    label = []


    #load feature vector
    operation_path = os.path.join(path, 'feature.txt')
    with open(operation_path, 'r') as f:
        data_raw = list(list(rec) for rec in csv.reader(f, delimiter=' '))
        query = []

        no = 0
        for i in range(len(data_raw)):
            node = data_raw[i]
            if (node[0].find('plan') == -1):
                query.append(node)
            else:
                if (len(query) > 0):
                    if selected_sample[no] == 1:
                        feature.append(query)
                query = []
                no += 1
            if (i == len (data_raw) - 1):
                feature.append(query)

        for i in range(len(feature)):  # 行数
            for j in range(len(feature[i])):  # 列数
                for k in range(len(feature[i][j])):
                    feature[i][j][k] = float(feature[i][j][k])
                    if k >= len(feature[i][j]) - 2:
                        if feature[i][j][k] < min_label:
                            feature[i][j][k] = min_label
                        norm_feature = (np.log(feature[i][j][k]) - np.log(min_label)) / (
                                np.log(max_label) - np.log(min_label))
                        feature[i][j][k] = norm_feature




    ###
    adjacency_list_path = os.path.join(path, 'adjacency_list.txt')
    with open(adjacency_list_path, 'r') as f:
        data_raw = list(list(rec) for rec in csv.reader(f, delimiter=' '))
        query = []

        no = 0
        for i in range(len(data_raw)):
            node = data_raw[i]
            if (node[0].find('plan') == -1):
                query.append(node)
            else:
                if (len(query) > 0):
                    if selected_sample[no] == 1:
                        adjacency_list.append(query)
                query = []
                no += 1
            if (i == len(data_raw) - 1):
                adjacency_list.append(query)

        for i in range(len(adjacency_list)):  # 行数
            for j in range(len(adjacency_list[i])):  # 列数
                for k in range(len(adjacency_list[i][j])):
                    adjacency_list[i][j][k] = int(adjacency_list[i][j][k])


    node_order_path = os.path.join(path, 'node_order.txt')
    with open(node_order_path, 'r') as f:
        data_raw = list(list(rec) for rec in csv.reader(f, delimiter=' '))
        query = []
        no = 0

        for i in range(len(data_raw)):
            node = data_raw[i]
            if (node[0].find('plan') == -1):
                query.append(node)
            else:
                if (len(query) > 0):
                    if selected_sample[no] == 1:
                        node_order.append(query)
                query = []
                no+=1
            if (i == len(data_raw) - 1):
                node_order.append(query)

        for i in range(len(node_order)):  # 行数
            for j in range(len(node_order[i])):  # 列数
                for k in range(len(node_order[i][j])):
                    node_order[i][j][k] = int(node_order[i][j][k])


    edge_order_path = os.path.join(path, 'edge_order.txt')
    with open(edge_order_path, 'r') as f:
        data_raw = list(list(rec) for rec in csv.reader(f, delimiter=' '))
        query = []

        no = 0
        for i in range(len(data_raw)):
            node = data_raw[i]
            if (node[0].find('plan') == -1):
                query.append(node)
            else:
                if (len(query) > 0):
                    if selected_sample[no] == 1:
                        edge_order.append(query)
                query = []
                no+=1
            if (i == len(data_raw) - 1):
                edge_order.append(query)

        for i in range(len(edge_order)):  # 行数
            for j in range(len(edge_order[i])):  # 列数
                for k in range(len(edge_order[i][j])):
                    edge_order[i][j][k] = int(edge_order[i][j][k])


    label_path = os.path.join(path, 'label.txt')
    with open(label_path, 'r') as f:
        data_raw = list(list(rec) for rec in csv.reader(f, delimiter=' '))
        query = []

        no = 0
        for i in range(len(data_raw)):
            node = data_raw[i]
            if (node[0].find('plan') == -1):
                query.append(node)
            else:
                if (len(query) > 0):
                    if selected_sample[no] == 1:
                        label.append(query)
                query = []
                no+=1
            if (i == len(data_raw) - 1):
                label.append(query)

        for i in range(len(label)):  # 行数
            for j in range(len(label[i])):  # 列数
                for k in range(len(label[i][j])):
                    label[i][j][k] = int(label[i][j][k])
                    if (label[i][j][k] == 0):
                        label[i][j][k] = 1.1

    return feature, adjacency_list, node_order, edge_order, label



def get_sample_size(path, selected_sample):
    count = 0
    operation_path = os.path.join(path, 'feature.txt')
    with open(operation_path, 'r') as f:
        data_raw = list(list(rec) for rec in csv.reader(f, delimiter=' '))

        no = 0
        for i in range(len(data_raw)):
            node = data_raw[i]
            if (node[0].find('plan') != -1):
                if selected_sample[no] == 1:
                    count = count + 1
                no+=1
    return count


class Dataloader(data.Dataset):

    def __init__(self, path, selected_sample, min_label, max_label):
        super(Dataloader, self).__init__()
        tmp_features, tmp_adjacency_list, tmp_node_order, tmp_edge_order, tmp_label = load_train_data(path, selected_sample, min_label, max_label)
        self.feature = []
        self.adjacency_list = []
        self.node_order = []
        self.edge_order = []
        self.label = []
        self.feature = tmp_features
        self.adjacency_list = tmp_adjacency_list
        self.node_order = tmp_node_order
        self.edge_order = tmp_edge_order
        self.label = tmp_label
        self.size = get_sample_size(path, selected_sample)
        self.min_label = min_label
        self.max_label = max_label
        print("Dataset size: ", self.size)


    def __len__(self):
        return self.size

    def __getitem__(self, index):
        feature = deepcopy(self.feature[index])
        adjacency_list = deepcopy(self.adjacency_list[index])
        node_order = deepcopy(self.node_order[index])
        edge_order = deepcopy(self.edge_order[index])
        label = deepcopy(self.label[index])
        return (feature, adjacency_list, node_order, edge_order, label)