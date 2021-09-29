#trainer for LPCE-R

from tqdm import tqdm
import csv
import torch
from lpce.utils import *


class HyTrainer(object):

    def __init__(self, cuda, contentModule, cardModule, refineModule, optimizer, min_label, max_label):
        super(HyTrainer, self).__init__()
        self.cuda_use = cuda
        self.modela = contentModule
        self.modelb = cardModule
        self.modelc= refineModule
        self.optimizer = optimizer
        self.min_label = min_label
        self.max_label = max_label
        self.epoch = 0
        self.train_use_time = 0.0
        self.operat_dim = 4
        self.table_dim = 11
        self.filter_dim = 18
        self.join_dim = 37
        self.card_dim = 2


    def train(self, dataset, batch_size):
        self.modela.eval()
        self.modelb.eval()
        self.modelc.train()
        total_loss = 0.0
        self.optimizer.zero_grad()
        indices = torch.randperm(len(dataset)//batch_size)


        #len(dataset)//batch_size
        # #training one epoch
        for idx in tqdm(range(len(dataset)//batch_size), desc='Training epoch ' + str(self.epoch + 1) + ''):


            # hidden state from modela
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

            estimate_output, c_a = self.modela(
                dic['operation_feat'],
                dic['table_feat'],
                dic['filter_feat'],
                dic['join_feat'],
                dic['node_order'],
                dic['adjacency_list'],
                dic['edge_order']
            )



            # hidden state from modelb
            batch_dic=()
            for batch_idx in range(0, batch_size):
                feature, adjacency_list, node_order, edge_order, label = dataset[indices[idx]*batch_size + batch_idx]
                feature = np.array(feature)
                operation_feat = feature[:, 0:self.operat_dim]
                table_feat = feature[:, self.operat_dim : self.operat_dim + self.table_dim ]
                filter_feat = feature[:, self.operat_dim + self.table_dim : self.operat_dim + self.table_dim + self.filter_dim]
                join_feat = feature[:, self.operat_dim + self.table_dim + self.filter_dim : self.operat_dim + self.table_dim + self.filter_dim+self.join_dim]
                card_feat = feature[:, self.operat_dim + self.table_dim + self.filter_dim+self.join_dim:
                                       self.operat_dim + self.table_dim + self.filter_dim+self.join_dim + self.card_dim]


                operation_feat = torch.from_numpy(operation_feat)
                table_feat = torch.from_numpy(table_feat)
                filter_feat = torch.from_numpy(filter_feat)
                join_feat = torch.from_numpy(join_feat)
                card_feat = torch.from_numpy(card_feat)
                adjacency_list = torch.from_numpy(np.array(adjacency_list))
                node_order = torch.from_numpy(np.array(node_order))
                edge_order = torch.from_numpy(np.array(edge_order))
                label = torch.from_numpy(np.array(label))

                #feature = feature.float()
                operation_feat = operation_feat.float()
                table_feat = table_feat.float()
                filter_feat = filter_feat.float()
                join_feat = join_feat.float()
                card_feat = card_feat.float()
                label = label.float()
                node_order = torch.squeeze(node_order, 0)
                edge_order = torch.squeeze(edge_order, 0)

                data ={'operation_feat': operation_feat,
                       'table_feat': table_feat,
                       'filter_feat': filter_feat,
                       'join_feat': join_feat,
                       'card_feat': card_feat,
                       'node_order': node_order,
                       'adjacency_list': adjacency_list,
                       'edge_order': edge_order,
                       'labels': label}
                batch_dic = batch_dic + (data,)

            dic = batch_tree_input_modelB(batch_dic)


            if self.cuda_use:
                dic['operation_feat'] = dic['operation_feat'].cuda()
                dic['table_feat'] = dic['table_feat'].cuda()
                dic['join_feat'] = dic['join_feat'].cuda()
                dic['filter_feat'] = dic['filter_feat'].cuda()
                dic['card_feat'] = dic['card_feat'].cuda()
                dic['node_order'] = dic['node_order'].cuda()
                dic['adjacency_list'] = dic['adjacency_list'].cuda()
                dic['edge_order'] = dic['edge_order'].cuda()
                dic['labels'] = dic['labels'].cuda()

            estimate_output, c_b = self.modelb(
                dic['operation_feat'],
                dic['table_feat'],
                dic['filter_feat'],
                dic['join_feat'],
                dic['card_feat'],
                dic['node_order'],
                dic['adjacency_list'],
                dic['edge_order']
            )



            feed = 2
            estimate_c = self.modelc(dic['operation_feat'],
                                     dic['table_feat'],
                                     dic['filter_feat'],
                                     dic['join_feat'],
                                     dic['node_order'],
                                     dic['adjacency_list'],
                                     dic['edge_order'],
                                     c_a, c_b, feed)
            loss = self.loss_function(estimate_c, dic['labels'], dic['node_order'], feed)
            loss.backward(retain_graph=True)
            self.optimizer.step()
            self.optimizer.zero_grad()

            feed = 4
            estimate_c_3 = self.modelc(dic['operation_feat'],
                                       dic['table_feat'],
                                       dic['filter_feat'],
                                       dic['join_feat'],
                                       dic['node_order'],
                                       dic['adjacency_list'],
                                       dic['edge_order'],
                                       c_a, c_b, feed)
            loss = self.loss_function(estimate_c_3, dic['labels'], dic['node_order'], feed)
            loss.backward(retain_graph=True)
            self.optimizer.step()
            self.optimizer.zero_grad()

            feed = 5
            estimate_c_3 = self.modelc(dic['operation_feat'],
                                       dic['table_feat'],
                                       dic['filter_feat'],
                                       dic['join_feat'],
                                       dic['node_order'],
                                       dic['adjacency_list'],
                                       dic['edge_order'],
                                       c_a, c_b, feed)
            loss = self.loss_function(estimate_c_3, dic['labels'], dic['node_order'], feed)
            loss.backward(retain_graph=True)
            self.optimizer.step()
            self.optimizer.zero_grad()


            feed = 3
            estimate_c_4 = self.modelc(dic['operation_feat'],
                                       dic['table_feat'],
                                       dic['filter_feat'],
                                       dic['join_feat'],
                                       dic['node_order'],
                                       dic['adjacency_list'],
                                       dic['edge_order'],
                                       c_a, c_b, feed)
            loss = self.loss_function(estimate_c_4, dic['labels'], dic['node_order'], feed)
            loss.backward()
            self.optimizer.step()
            self.optimizer.zero_grad()

            total_loss += loss

        self.epoch += 1
        epoch_loss = total_loss/(len(dataset)//batch_size)
        print("     Train Epoch {}, loss: {}".format(self.epoch, epoch_loss))
        return epoch_loss




    def loss_function(self, predict, label, node_order, feed):
            one = torch.ones_like(node_order)
            zero = torch.zeros_like(node_order)
            node_order = torch.where(node_order > feed, one, zero)
            node_mask = node_order == 1
            predict = predict[node_mask, :]
            label = label[node_mask, :]
            qerror = []
            predict = self.unnormalize_torch(predict, np.log(self.min_label), np.log(self.max_label))
            for i in range(len(label)):
                if (predict[i] > label[i]).cpu().data.numpy()[0]:
                    qerror.append(predict[i] / label[i])
                else:
                    qerror.append(label[i] / predict[i])

            return torch.mean(torch.cat(qerror))


    def unnormalize_torch(self, vals, min_val, max_val):
            vals = (vals * (max_val - min_val)) + min_val
            return torch.exp(vals)






















    def test(self, dataset, feed):
        self.modela.eval()
        self.modelb.eval()
        self.modelc.eval()


        total_final_predict = []
        total_final_label = []
        output = []
        #Write output

        for idx in range(0, len(dataset)):

            # hidden state from modela
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

            data = {'operation_feat': operation_feat,
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

            estimate_a, c_a = self.modela(
                data['operation_feat'],
                data['table_feat'],
                data['filter_feat'],
                data['join_feat'],
                data['node_order'],
                data['adjacency_list'],
                data['edge_order']
            )


            # hidden state from modelb
            feature, adjacency_list, node_order, edge_order, label = dataset[idx]
            feature = np.array(feature)
            operation_feat = feature[:, 0:self.operat_dim]
            table_feat = feature[:, self.operat_dim : self.operat_dim + self.table_dim ]
            filter_feat = feature[:, self.operat_dim + self.table_dim : self.operat_dim + self.table_dim + self.filter_dim]
            join_feat = feature[:, self.operat_dim + self.table_dim + self.filter_dim : self.operat_dim + self.table_dim + self.filter_dim+self.join_dim]
            card_feat = feature[:, self.operat_dim + self.table_dim + self.filter_dim+self.join_dim:
                                   self.operat_dim + self.table_dim + self.filter_dim+self.join_dim + self.card_dim]

            operation_feat = torch.from_numpy(operation_feat)
            table_feat = torch.from_numpy(table_feat)
            filter_feat = torch.from_numpy(filter_feat)
            join_feat = torch.from_numpy(join_feat)
            card_feat = torch.from_numpy(card_feat)
            adjacency_list = torch.from_numpy(np.array(adjacency_list))
            node_order = torch.from_numpy(np.array(node_order))
            edge_order = torch.from_numpy(np.array(edge_order))
            label = torch.from_numpy(np.array(label))

            #feature = feature.float()
            operation_feat = operation_feat.float()
            table_feat = table_feat.float()
            filter_feat = filter_feat.float()
            join_feat = join_feat.float()
            card_feat = card_feat.float()
            label = label.float()
            node_order = torch.squeeze(node_order, 0)
            edge_order = torch.squeeze(edge_order, 0)

            datab ={'operation_feat': operation_feat,
                   'table_feat': table_feat,
                   'filter_feat': filter_feat,
                   'join_feat': join_feat,
                   'card_feat': card_feat,
                   'node_order': node_order,
                   'adjacency_list': adjacency_list,
                   'edge_order': edge_order,
                   'labels': label}

            if self.cuda_use:
                datab['operation_feat'] = datab['operation_feat'].cuda()
                datab['table_feat'] = datab['table_feat'].cuda()
                datab['join_feat'] = datab['join_feat'].cuda()
                datab['filter_feat'] = datab['filter_feat'].cuda()
                datab['node_order'] = datab['node_order'].cuda()
                datab['adjacency_list'] = datab['adjacency_list'].cuda()
                datab['edge_order'] = datab['edge_order'].cuda()
                datab['labels'] = datab['labels'].cuda()

            estimate_b, c_b = self.modelb(
                datab['operation_feat'],
                datab['table_feat'],
                datab['filter_feat'],
                datab['join_feat'],
                datab['card_feat'],
                datab['node_order'],
                datab['adjacency_list'],
                datab['edge_order']
            )

            #feed to modelC
            estimate_c = self.modelc(data['operation_feat'],
                                     data['table_feat'],
                                     data['filter_feat'],
                                     data['join_feat'],
                                     data['node_order'],
                                     data['adjacency_list'],
                                     data['edge_order'],
                                     c_a, c_b, feed)
            output = self.node_output(estimate_c, data['labels'], data['node_order'], feed)
            total_final_predict.append(estimate_c[0])
            total_final_label.append(data['labels'][0])


        final_qerror = self.print_qerror(total_final_predict, total_final_label)
        return final_qerror




    def node_output(self, predict, label, node_order, feed):
        output = []
        predict = self.unnormalize_torch(predict, np.log(self.min_label), np.log(self.max_label))
        if(len(node_order) != len(label)):
            print("ERROR: node_order length does not match label length")

        for i in range(len(label)):
            if node_order[i] <= feed:
                output.append(label[i])
            else:
                output.append(predict[i])

        return output


    def print_qerror(self, predict, label):
        qerror = []
        for i in range(len(predict)):
            predict[i] = self.unnormalize_torch(predict[i], np.log(self.min_label), np.log(self.max_label))
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
        return qerror



    def final_qerror(self, predict, label):
        qerror = []
        predict = self.unnormalize_torch(predict, np.log(self.min_label), np.log(self.max_label))
        if (predict[0] > label[0]).cpu().data.numpy()[0]:
            qerror.append(predict[0] / label[0])
        else:
            qerror.append(label[0] / predict[0])
            # print(" qerror, ", predict[0], label[0])
        return torch.mean(torch.cat(qerror))






















    def test_batch(self, dataset):
        self.model.eval()
        batch_size = len(dataset)

        batch_dic=()
        for batch_idx in range(0, batch_size):
            feature, adjacency_list, node_order, edge_order, label = dataset[batch_idx]
            feature = np.array(feature)
            operation_feat = feature[:, 0:3]
            table_feat = feature[:, 0:3]
            filter_feat = feature[:, 3:3+48]
            join_feat = feature[:, 3+48:3+48+23]
            card_feat = feature[:, 3+48+23:3+48+23+2]

            operation_feat = torch.from_numpy(operation_feat)
            table_feat = torch.from_numpy(table_feat)
            filter_feat = torch.from_numpy(filter_feat)
            join_feat = torch.from_numpy(join_feat)
            card_feat = torch.from_numpy(card_feat)
            adjacency_list = torch.from_numpy(np.array(adjacency_list))
            node_order = torch.from_numpy(np.array(node_order))
            edge_order = torch.from_numpy(np.array(edge_order))
            label = torch.from_numpy(np.array(label))

            #feature = feature.float()
            operation_feat = operation_feat.float()
            table_feat = table_feat.float()
            filter_feat = filter_feat.float()
            join_feat = join_feat.float()
            card_feat = card_feat.float()
            label = label.float()
            node_order = torch.squeeze(node_order, 0)
            edge_order = torch.squeeze(edge_order, 0)

            data ={'operation_feat': operation_feat,
                   'table_feat': table_feat,
                   'filter_feat': filter_feat,
                   'join_feat': join_feat,
                   'card_feat': card_feat,
                   'node_order': node_order,
                   'adjacency_list': adjacency_list,
                   'edge_order': edge_order,
                   'labels': label}
            batch_dic = batch_dic + (data,)

        dic = batch_tree_input_modelB(batch_dic)


        if self.cuda_use:
            dic['operation_feat'] = dic['operation_feat'].cuda()
            dic['table_feat'] = dic['table_feat'].cuda()
            dic['join_feat'] = dic['join_feat'].cuda()
            dic['filter_feat'] = dic['filter_feat'].cuda()
            dic['card_feat'] = dic['card_feat'].cuda()
            dic['node_order'] = dic['node_order'].cuda()
            dic['adjacency_list'] = dic['adjacency_list'].cuda()
            dic['edge_order'] = dic['edge_order'].cuda()
            dic['labels'] = dic['labels'].cuda()

        estimate_output = self.model(
            #dic['table_feat'],
            dic['operation_feat'],
            dic['filter_feat'],
            dic['join_feat'],
            dic['card_feat'],
            dic['node_order'],
            dic['adjacency_list'],
            dic['edge_order']
        )
        final_error = self.final_qerror_inbatch(estimate_output, dic['labels'], dic['tree_sizes'])

        return final_error


    def final_qerror_inbatch(self, predict, label, tree_size):
        qerror = []
        predict = self.unnormalize_torch(predict)
        final_pred = 1

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
        print("         50th percentile: {}".format(np.percentile(qerror, 50)))
        print("         90th percentile: {}".format(np.percentile(qerror, 90)))
        print("         95th percentile: {}".format(np.percentile(qerror, 95)))
        print("         99th percentile: {}".format(np.percentile(qerror, 99)))
        print("         Max: {}".format(np.max(qerror)))
        print("         Mean: {}".format(np.mean(qerror)))
        return np.mean(qerror)





