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


#normlized label log
def normalize_labels(labels, max_val, min_val):
    labels = np.array([float(l) for l in labels])
    for i in range(len(labels)):
        if labels[i] == min_val:
            labels[i] = labels[i] + 1
        if labels[i] == 1:
            labels[i] = labels[i] + 1.00001

    if min_val == 0:
        min_val_norm = 0.0
    else:
        min_val_norm = np.log(float(min_val))
    max_val_norm = np.log(float(max_val))
    labels_norm = (np.log(labels) - min_val_norm) / (max_val_norm - min_val_norm)

    labels_norm = np.minimum(labels_norm, 1)
    labels_norm = np.maximum(labels_norm, 0)

    return labels_norm

def normalize_card(card, max_val, min_val):
    if card == 0:
        card_norm = 0.0
    else:
        if card == min_val:
            card = card + 1
        if card == 1:
            card = card + 1.00001

        if min_val == 0:
            min_val_norm = 0.0
        else:
            min_val_norm = np.log(float(min_val))
        max_val_norm = np.log(float(max_val))
        card_norm = (np.log(card) - min_val_norm) / (max_val_norm - min_val_norm)

        card_norm = np.minimum(card_norm, 1)
        card_norm = np.maximum(card_norm, 0)

    return card_norm

def load_train_data(path, max_val, min_val):
    operations = []
    tables = []
    predicates = []
    joins = []
    realcard = []
    label_node = []
    tree_depth = []

    operation_path = os.path.join(path, 'operation.txt')
    with open(operation_path, 'rU') as f:
        data_raw = list(list(rec) for rec in csv.reader(f, delimiter=' '))
        query = []

        for i in range(len(data_raw)):
            node = data_raw[i]
            if (node[0].find('plan') == -1):
                query.append(node)
            else:
                if (len(query) > 0):
                    operations.append(query)
                query = []
            if (i == len(data_raw) - 1):
                operations.append(query)

        for i in range(len(operations)):  # 行数
            for j in range(len(operations[i])):  # 列数
                for k in range(len(operations[i][j])):
                    operations[i][j][k] = int(operations[i][j][k])
            # print(operations[i])
            # print("=====")

    table_path = os.path.join(path, 'meta.txt')
    with open(table_path, 'rU') as f:
        data_raw = list(list(rec) for rec in csv.reader(f, delimiter=' '))
        query = []

        for i in range(len(data_raw)):
            node = data_raw[i]
            if node[0].find('plan') == -1:
                query.append(node)
            else:
                if len(query) > 0:
                    tables.append(query)
                query = []
            if i == len(data_raw) - 1:
                tables.append(query)

        for i in range(len(tables)):  # 行数
            for j in range(len(tables[i])):  # 列数
                for k in range(len(tables[i][j])):
                    tables[i][j][k] = int(tables[i][j][k])
            #print(tables[i])
            #print("=====")

    predicate_path = os.path.join(path, 'predicate.txt')
    with open(predicate_path, 'rU') as f:
        data_raw = list(list(rec) for rec in csv.reader(f, delimiter=' '))
        query = []

        for i in range(len(data_raw)):
            node = data_raw[i]
            if node[0].find('plan') == -1:
                query.append(node)
            else:
                if len(query) > 0:
                    predicates.append(query)
                query = []
            if i == len(data_raw) - 1:
                predicates.append(query)

        max_num_predicates = 0
        for i in range(len(predicates)):  # 行数
            for j in range(len(predicates[i])):  # 列数
                temp_max_num_predicates = 0
                for k in range(len(predicates[i][j])):
                    temp_max_num_predicates += 1
                    predicates[i][j][k] = float(predicates[i][j][k])
                if max_num_predicates < temp_max_num_predicates:
                    max_num_predicates = temp_max_num_predicates
            #print(predicates[i])
            #print("=====")
        for i in range(len(predicates)):  # 行数
            for j in range(len(predicates[i])):  # 列数
                temp_num = 0
                for k in range(len(predicates[i][j])):
                    temp_num += 1
                numpad = max_num_predicates - temp_num
                predicates[i][j] = np.pad(predicates[i][j],(0,numpad),'constant', constant_values=(0,0))
        print(" max length of predicates: ", max_num_predicates)


    join_path = os.path.join(path, 'join.txt')
    with open(join_path, 'rU') as f:
        data_raw = list(list(rec) for rec in csv.reader(f, delimiter=' '))
        query = []

        for i in range(len(data_raw)):
            node = data_raw[i]
            if node[0].find('plan') == -1:
                query.append(node)
            else:
                if len(query) > 0:
                    joins.append(query)
                query = []
            if (i == len(data_raw) - 1):
                joins.append(query)

        max_len_joins = 0
        for i in range(len(joins)):
            for j in range(len(joins[i])):
                temp_max_num_joins = 0
                for k in range(len(joins[i][j])):
                    temp_max_num_joins += 1
                    joins[i][j][k] = float(joins[i][j][k])
                if(max_len_joins < temp_max_num_joins):
                    max_len_joins = temp_max_num_joins
        for i in range(len(joins)):
            for j in range(len(joins[i])):
                temp_num = 0
                for k in range(len(joins[i][j])):
                    temp_num += 1
                numpad = max_len_joins - temp_num
                joins[i][j] = np.pad(joins[i][j],(0,numpad),'constant', constant_values=(0,0))
        print(" max length of joins: ", max_len_joins)


    realcard_path = os.path.join(path, 'realcard.txt')
    with open(realcard_path, 'rU') as f:
        data_raw = list(list(rec) for rec in csv.reader(f, delimiter=' '))
        query = []

        for i in range(len(data_raw)):
            node = data_raw[i]
            if node[0].find('plan') == -1:
                query.append(node)
            else:
                if len(query) > 0:
                    realcard.append(query)
                query = []
            if (i == len(data_raw) - 1):
                realcard.append(query)

        max_len_card = 0
        for i in range(len(realcard)):
            for j in range(len(realcard[i])):
                temp_max_num_card = 0
                for k in range(len(realcard[i][j])):
                    temp_max_num_card += 1
                    realcard[i][j][k] = normalize_card(float(realcard[i][j][k]), max_val, min_val)
                if(max_len_card < temp_max_num_card):
                    max_len_card = temp_max_num_card
        for i in range(len(realcard)):
            for j in range(len(realcard[i])):
                temp_num = 0
                for k in range(len(realcard[i][j])):
                    temp_num += 1
                numpad = max_len_card - temp_num
                realcard[i][j] = np.pad(realcard[i][j],(0,numpad),'constant', constant_values=(0,0))
        print(" max length of real card: ", max_len_card)




    parent_path = os.path.join(path, 'parents.txt')
    label_path = os.path.join(path, 'label.txt')
    pfile = open(parent_path, 'r')  # parent node
    lfile = open(label_path, 'r')  # label node
    p = pfile.readlines()
    l = lfile.readlines()


    for i in range(len(p)):
        for m in range(len(l)):
            if m == i:
                tmp_label = []
                p_node = p[i][:-1].split(' ')
                l_node = l[m][:-1].split(' ')
                max = 0
                for j in range(0, len(p_node)):
                    if max < int(p_node[j]):
                        max = int(p_node[j])
                for j in range(0, max+1):
                    cur = max - j
                    for k in range(0, len(p_node)):
                        if cur == int(p_node[k]):
                            tmp_label.append(int(l_node[k]))
                label_node.append(tmp_label)


    for i in range(len(p)):
        max = 0
        p_node = p[i][:-1].split(' ')
        for j in range(len(p_node)):
            if max < int(p_node[j]):
                max = int(p_node[j])
        max = max + 1
        tree_depth.append(max)

    return operations, tables, predicates, joins, realcard, label_node, tree_depth




# Dataset class for sql query training dataset
class Dataset(data.Dataset):

    def __init__(self, path, max_val, min_val):
        super(Dataset, self).__init__()
        temp_operations, temp_tables, temp_predicates, temp_joins , temp_realcard, temp_label_node, tmp_tree_depth = load_train_data(path, max_val, min_val)

        parent_path = os.path.join(path, 'parents.txt')
        label_path = os.path.join(path, 'label.txt')
        temp_trees = self.read_trees(parent_path, label_path)

        # travel all trees
        # print('Trees have num ', len(temp_trees))
        # print('Trees have finial label ')
        # for i in range(len(temp_trees)):
        #     print(temp_trees[i].gold_label)

        self.max_val = max_val
        self.min_val = min_val
        self.trees = temp_trees
        self.operations = temp_operations
        self.tables = temp_tables
        self.predicates = temp_predicates
        self.joins = temp_joins
        self.realcard= temp_realcard
        self.label_node = temp_label_node # label for each node of execution plan
        self.tree_depth = tmp_tree_depth

        self.labels = [] # label for final node query output
        for i in range(0, len(self.trees)):
            self.labels.append(self.trees[i].gold_label)
        label_norm = normalize_labels(self.labels, self.max_val, self.min_val)
        self.labels = torch.Tensor(self.labels)  # let labels be tensor
        self.labels_norm = torch.Tensor(label_norm)
        self.size = len(self.trees)




    def read_trees(self, filename_parents, filename_labels):
        pfile = open(filename_parents, 'r')  # parent node
        lfile = open(filename_labels, 'r')  # label node
        p = pfile.readlines()
        l = lfile.readlines()
        pl = zip(p, l)  # (parent, label) tuple
        trees = [self.read_tree(p_line, l_line) for p_line, l_line in tqdm(pl)]

        return trees

    def read_tree(self, line, label_line):
        # FIXED: tree.idx, also tree dict() use base 1 as it was in dataset
        # parents is list base 0, keep idx-1
        # labels is list base 0, keep idx-1
        # parents = map(int,line.split()) # split each number and turn to int
        parents = list(map(int, line.split()))  # split each number and turn to int
        trees = dict()  # this is dict
        root = None
        # labels = map(self.parse_dlabel_token, label_line.split())
        labels = list(map(self.parse_dlabel_token, label_line.split()))
        for i in range(1, len(parents) + 1):
            # for i in range(1,len(list(parents))+1):
            # if not trees[i-1] and parents[i-1]!=-1:
            if i not in trees.keys() and parents[i - 1] != -1:
                idx = i
                prev = None
                while True:
                    parent = parents[idx - 1]
                    if parent == -1:
                        break
                    tree = Tree()
                    if prev is not None:
                        tree.add_child(prev)
                    trees[idx] = tree
                    tree.idx = idx  # -1 remove -1 here to prevent embs[tree.idx -1] = -1 while tree.idx = 0
                    tree.gold_label = labels[idx - 1]  # add node label
                    # if trees[parent-1] is not None:
                    if parent in trees.keys():
                        trees[parent].add_child(tree)
                        break
                    elif parent == 0:
                        root = tree
                        break
                    else:
                        prev = tree
                        idx = parent

        return root

    def parse_dlabel_token(self, x):
        if x == '#':
            return None
        else:
            return int(x)

    def __len__(self):
        return self.size

    def __getitem__(self, index):
        # ltree = deepcopy(self.ltrees[index])
        # rtree = deepcopy(self.rtrees[index])
        # lsent = deepcopy(self.lsentences[index])
        # rsent = deepcopy(self.rsentences[index])
        # label = deepcopy(self.labels[index])
        tree = deepcopy(self.trees[index])
        operation = deepcopy(self.operations[index])
        table = deepcopy(self.tables[index])
        predicate = deepcopy(self.predicates[index])
        join = deepcopy(self.joins[index])
        realcard = deepcopy(self.realcard[index])
        label = deepcopy(self.labels[index])
        tree_depth = deepcopy(self.tree_depth[index])
        return (tree, operation, table, predicate, join, realcard, label, tree_depth)




