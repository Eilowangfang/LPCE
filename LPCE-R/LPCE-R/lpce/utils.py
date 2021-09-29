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

    f = open(os.path.join(path, 'child_card.txt'))
    lines = f.readlines()
    for line in lines:
        if line.count("plan") > 0:
            continue
        card = line.split(" ")
        if max_label < int(card[0]):
            max_label = int(card[0])
        if max_label < int(card[1]):
            max_label = int(card[1])
        if min_label > int(card[0]):
            min_label = int(card[0])
        if min_label > int(card[1]):
            min_label = int(card[1])

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

def test():
    return 3.2