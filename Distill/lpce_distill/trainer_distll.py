import numpy as np
import os, time, argparse
from tqdm import tqdm
import csv
import torch
import time
from lpce.utils import *


class DistillTrainer(object):

    def __init__(self, cuda, model_sim, model_com, optimizer, min_label, max_label):
        super(DistillTrainer, self).__init__()
        self.cuda_use = cuda
        self.model_sim = model_sim
        self.model_com = model_com
        self.optimizer = optimizer
        self.min_label = min_label
        self.max_label = max_label
        self.norm_min_label = np.log(min_label)
        self.norm_max_label = np.log(max_label)
        self.epoch = 0


    def train(self, dataset, batch_size):
        self.model_com.eval()
        self.model_sim.train()
        total_loss = 0.0
        indices = torch.randperm(len(dataset)//batch_size)
        self.optimizer.zero_grad()

        # #training one epoch
        for idx in tqdm(range(len(dataset)//batch_size), desc='Training epoch ' + str(self.epoch + 1) + ''):
            batch_dic=()
            for batch_idx in range(0, batch_size):
                feature, adjacency_list, node_order, edge_order, label = dataset[indices[idx]*batch_size + batch_idx]
                feature = np.array(feature)
                operation_feat = feature[:, 0:self.operat_dim]
                table_feat = feature[:, self.operat_dim : self.operat_dim + self.table_dim ]
                filter_feat = feature[:, self.operat_dim + self.table_dim : self.operat_dim + self.table_dim + self.filter_dim]
                join_feat = feature[:, self.operat_dim + self.table_dim + self.filter_dim : self.operat_dim + self.table_dim + self.filter_dim+self.join_dim]

                operation_feat = torch.from_numpy(operation_feat)
                table_feat = torch.from_numpy(table_feat)
                filter_feat = torch.from_numpy(filter_feat)
                join_feat = torch.from_numpy(join_feat)
                adjacency_list = torch.from_numpy(np.array(adjacency_list))
                node_order = torch.from_numpy(np.array(node_order))
                edge_order = torch.from_numpy(np.array(edge_order))
                label = torch.from_numpy(np.array(label))

                #feature = feature.float()
                operation_feat = operation_feat.float()
                table_feat = table_feat.float()
                filter_feat = filter_feat.float()
                join_feat = join_feat.float()
                label = label.float()
                node_order = torch.squeeze(node_order, 0)
                edge_order = torch.squeeze(edge_order, 0)

                data ={'operation_feat': operation_feat,
                       'table_feat': table_feat,
                       'filter_feat': filter_feat,
                       'join_feat': join_feat,
                       'node_order': node_order,
                       'adjacency_list': adjacency_list,
                       'edge_order': edge_order,
                       'labels': label}
                batch_dic = batch_dic + (data,)

            dic = batch_tree_input_comp(batch_dic)


            if self.cuda_use:
                dic['operation_feat'] = dic['operation_feat'].cuda()
                dic['table_feat'] = dic['table_feat'].cuda()
                dic['join_feat'] = dic['join_feat'].cuda()
                dic['filter_feat'] = dic['filter_feat'].cuda()
                dic['node_order'] = dic['node_order'].cuda()
                dic['adjacency_list'] = dic['adjacency_list'].cuda()
                dic['edge_order'] = dic['edge_order'].cuda()
                dic['labels'] = dic['labels'].cuda()


            estimate_output, o_com, x_com, hm_com = self.model_com(
                dic['operation_feat'],
                dic['table_feat'],
                dic['filter_feat'],
                dic['join_feat'],
                dic['node_order'],
                dic['adjacency_list'],
                dic['edge_order']
            )

            estimate_output, o_sim, x_sim, hm_sim = self.model_sim(
                dic['operation_feat'],
                dic['table_feat'],
                dic['filter_feat'],
                dic['join_feat'],
                dic['node_order'],
                dic['adjacency_list'],
                dic['edge_order']
            )

            #hint loss
            loss_x = self.loss_x(x_sim, x_com)
            loss_hm = self.loss_hm(hm_sim, hm_com)
            loss = loss_x + loss_hm
            loss.backward(retain_graph=True)
            self.optimizer.step()
            self.optimizer.zero_grad()


            #prediction loss
            loss_out = self.loss_function(estimate_output, dic['labels'])
            loss_h = self.loss_o(o_sim, o_com)
            loss = 0.5 * loss_out + loss_h * 0.5
            loss.backward()
            self.optimizer.step()
            self.optimizer.zero_grad()
            total_loss += loss

        self.epoch += 1
        epoch_loss = total_loss/(len(dataset)//batch_size)
        print("     Train Epoch {}, loss: {}".format(self.epoch, epoch_loss))
        return epoch_loss


    def loss_function(self, predict, label):
        qerror = []
        predict = self.unnormalize_torch(predict)
        for i in range(len(label)):
            if (predict[i] > label[i]):
                qerror.append(predict[i] / label[i])
            else:
                qerror.append(label[i] / predict[i])
        return torch.mean(torch.cat(qerror))

    def loss_o(self, h_sim, h_com):
        herror = torch.abs(torch.sub(h_sim, h_com))
        return torch.mean(herror)

    def loss_x(self, x_sim, x_com):
        xerror = torch.abs(torch.sub(x_sim, x_com))
        return torch.mean(xerror)

    def loss_hm(self, hm_sim, hm_com):
        hmerror = torch.abs(torch.sub(hm_sim, hm_com))
        return torch.mean(hmerror)

    def unnormalize_torch(self, vals):
        vals = (vals * (self.norm_max_label - self.norm_min_label)) + self.norm_min_label
        return torch.exp(vals)






    def test(self, dataset):
        self.model_sim.eval()
        final_error = 0.0
        use_time = 0.0
        total_final_estimate_output = []
        total_final_label = []

        for idx in range(0, len(dataset)):
            feature, adjacency_list, node_order, edge_order, label = dataset[idx]
            feature = np.array(feature)
            operation_feat = feature[:, 0:self.operat_dim]
            table_feat = feature[:, self.operat_dim : self.operat_dim + self.table_dim ]
            filter_feat = feature[:, self.operat_dim + self.table_dim : self.operat_dim + self.table_dim + self.filter_dim]
            join_feat = feature[:, self.operat_dim + self.table_dim + self.filter_dim : self.operat_dim + self.table_dim + self.filter_dim+self.join_dim]

            operation_feat = torch.from_numpy(operation_feat)
            table_feat = torch.from_numpy(table_feat)
            filter_feat = torch.from_numpy(filter_feat)
            join_feat = torch.from_numpy(join_feat)
            adjacency_list = torch.from_numpy(np.array(adjacency_list))
            node_order = torch.from_numpy(np.array(node_order))
            edge_order = torch.from_numpy(np.array(edge_order))
            label = torch.from_numpy(np.array(label))

            operation_feat = operation_feat.float()
            table_feat = table_feat.float()
            filter_feat = filter_feat.float()
            join_feat = join_feat.float()
            label = label.float()
            node_order = torch.squeeze(node_order, 0)
            edge_order = torch.squeeze(edge_order, 0)

            data ={'operation_feat': operation_feat,
                   'table_feat': table_feat,
                   'filter_feat': filter_feat,
                   'join_feat': join_feat,
                   'node_order': node_order,
                   'adjacency_list': adjacency_list,
                   'edge_order': edge_order,
                   'labels': label}

            if self.cuda_use:
                data['operation_feat'] = data['operation_feat'].cuda()
                data['table_feat'] = data['table_feat'].cuda()
                data['join_feat'] = data['join_feat'].cuda()
                data['filter_feat'] = data['filter_feat'].cuda()
                data['node_order'] = data['node_order'].cuda()
                data['adjacency_list'] = data['adjacency_list'].cuda()
                data['edge_order'] = data['edge_order'].cuda()
                data['labels'] = data['labels'].cuda()

            estimate_output, o, x, hm = self.model_sim(
                data['operation_feat'],
                data['table_feat'],
                data['filter_feat'],
                data['join_feat'],
                data['node_order'],
                data['adjacency_list'],
                data['edge_order']
            )
            final_error += self.final_qerror(estimate_output, data['labels'])

            total_final_estimate_output.append(estimate_output[0])
            total_final_label.append(data['labels'][0])

        test_loss = final_error/(len(dataset))
        print("     Testing q-error for final card: {}".format(test_loss))
        self.print_qerror(total_final_estimate_output, total_final_label)

        return test_loss


    def final_qerror(self, predict, label):
        qerror = []
        predict = self.unnormalize_torch(predict)
        if (predict[0] > label[0]).cpu().data.numpy()[0]:
            qerror.append(predict[0] / label[0])
        else:
            qerror.append(label[0] / predict[0])
        return torch.mean(torch.cat(qerror))


    def print_qerror(self, predict, label):
        qerror = []
        for i in range(len(predict)):
            predict[i] = self.unnormalize_torch(predict[i])
            if predict[i] > float(label[i]):
                qerror.append(float(predict[i]) / float(label[i]))
            else:
                qerror.append(float(label[i]) / float(predict[i]))

        print("     =========Q-error Accuracy=========")
        print("     50th percentile: {}".format(np.percentile(qerror, 50)))
        print("     75th percentile: {}".format(np.percentile(qerror, 75)))
        print("     90th percentile: {}".format(np.percentile(qerror, 90)))
        print("     99th percentile: {}".format(np.percentile(qerror, 99)))
        print("     Max: {}".format(np.max(qerror)))
        print("     Mean: {}".format(np.mean(qerror)))







    def test_batch(self, dataset):
        self.model_sim.eval()
        batch_size = len(dataset)
        use_time = 0.0

        batch_dic=()
        for batch_idx in range(0, batch_size):
            feature, adjacency_list, node_order, edge_order, label = dataset[batch_idx]
            feature = np.array(feature)
            operation_feat = feature[:, 0:self.operat_dim]
            table_feat = feature[:, self.operat_dim : self.operat_dim + self.table_dim ]
            filter_feat = feature[:, self.operat_dim + self.table_dim : self.operat_dim + self.table_dim + self.filter_dim]
            join_feat = feature[:, self.operat_dim + self.table_dim + self.filter_dim : self.operat_dim + self.table_dim + self.filter_dim+self.join_dim]


            operation_feat = torch.from_numpy(operation_feat)
            table_feat = torch.from_numpy(table_feat)
            filter_feat = torch.from_numpy(filter_feat)
            join_feat = torch.from_numpy(join_feat)
            adjacency_list = torch.from_numpy(np.array(adjacency_list))
            node_order = torch.from_numpy(np.array(node_order))
            edge_order = torch.from_numpy(np.array(edge_order))
            label = torch.from_numpy(np.array(label))

            operation_feat = operation_feat.float()
            table_feat = table_feat.float()
            filter_feat = filter_feat.float()
            join_feat = join_feat.float()
            label = label.float()
            node_order = torch.squeeze(node_order, 0)
            edge_order = torch.squeeze(edge_order, 0)

            data ={'operation_feat': operation_feat,
                   'table_feat': table_feat,
                   'filter_feat': filter_feat,
                   'join_feat': join_feat,
                   'node_order': node_order,
                   'adjacency_list': adjacency_list,
                   'edge_order': edge_order,
                   'labels': label}
            batch_dic = batch_dic + (data,)

        dic = batch_tree_input_comp(batch_dic)

        if self.cuda_use:
            dic['operation_feat'] = dic['operation_feat'].cuda()
            dic['table_feat'] = dic['table_feat'].cuda()
            dic['join_feat'] = dic['join_feat'].cuda()
            dic['filter_feat'] = dic['filter_feat'].cuda()
            dic['node_order'] = dic['node_order'].cuda()
            dic['adjacency_list'] = dic['adjacency_list'].cuda()
            dic['edge_order'] = dic['edge_order'].cuda()
            dic['labels'] = dic['labels'].cuda()

        estimate_output, o, x, hm = self.model_sim(
            dic['operation_feat'],
            dic['table_feat'],
            dic['filter_feat'],
            dic['join_feat'],
            dic['node_order'],
            dic['adjacency_list'],
            dic['edge_order']
        )
        final_error = self.final_qerror_inbatch(estimate_output, dic['labels'], dic['tree_sizes'])

        return final_error

    def final_qerror_inbatch(self, predict, label, tree_size):
        qerror = []
        predict = self.unnormalize_torch(predict)
        final_pred = 0

        for idx in range(len(tree_size)):
            if (predict[final_pred] > label[final_pred]).cpu().data.numpy()[0]:
                qerror.append(predict[final_pred] / label[final_pred])
            else:
                qerror.append(label[final_pred] / predict[final_pred])
            final_pred += tree_size[idx]


        qerror = torch.cat(qerror)
        print("     qerror shape: ", qerror.shape)
        qerror = qerror.cpu().detach().numpy()
        print("     =========Q-error Accuracy=========")
        print("     50th percentile: {}".format(np.percentile(qerror, 50)))
        print("     75th percentile: {}".format(np.percentile(qerror, 75)))
        print("     90th percentile: {}".format(np.percentile(qerror, 90)))
        print("     99th percentile: {}".format(np.percentile(qerror, 99)))
        print("     Max: {}".format(np.max(qerror)))
        print("     Mean: {}".format(np.mean(qerror)))

        return np.mean(qerror)





