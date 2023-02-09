import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


# refined module, we need to consider two cases
#  Case 1
#   (1,2,3)
#      |
#   connect layer (CNL)
#   /    \
#  (1,3) (2)
# A) (1,3) and (2) are both executed node from card module - (CNL-A)
# This case means to refine nodes at level upper than i,
# The left and right child of level i - 1 are done.


class REFINEModule(torch.nn.Module):
    def __init__(self, cuda_use, feature_dim, input_dim, mem_dim, hidden_dim,
                 operat_dim, table_dim, filter_dim, join_dim):
        super(REFINEModule, self).__init__()

        self.use_time = 0.0
        self.cuda_use = cuda_use
        self.feature_dim = feature_dim
        self.input_dim = input_dim
        self.mem_dim = mem_dim
        self.hidden_dim = hidden_dim
        self.operat_dim = operat_dim
        self.table_dim = table_dim
        self.filter_dim = filter_dim
        self.join_dim = join_dim


        #embeed module embeed input feature
        self.feature_mpl_operation = torch.nn.Linear(self.operat_dim, self.input_dim)
        self.feature_mpl_table = torch.nn.Linear(self.table_dim, self.input_dim)
        self.feature_mpl_filter = torch.nn.Linear(self.filter_dim, self.input_dim)
        self.feature_mpl_join = torch.nn.Linear(self.join_dim , self.input_dim)

        self.feature_mpl_operation_2 = torch.nn.Linear(self.input_dim, self.input_dim)
        self.feature_mpl_table_2 =  torch.nn.Linear(self.input_dim, self.input_dim)
        self.feature_mpl_filter_2  = torch.nn.Linear(self.input_dim, self.input_dim)
        self.feature_mpl_join_2  = torch.nn.Linear(self.input_dim, self.input_dim)


        self.W_xou = torch.nn.Linear(self.input_dim * 4, 3 * self.mem_dim)
        #output module
        self.out_mlp1 = nn.Linear(self.mem_dim, self.hidden_dim)
        self.out_mlp2 = nn.Linear(self.hidden_dim, 1)

        #connect layer
        self.con_mpl_ab = nn.Linear(self.input_dim * 4, self.mem_dim)
        self.convert_a = nn.Linear(self.input_dim * 5, self.input_dim * 4)
        self.con_mpl_a = nn.Linear(self.input_dim * 4, self.input_dim * 4)
        self.con_mpl_b = nn.Linear(self.input_dim * 4, self.input_dim * 4)


        if self.cuda_use:
            self.feature_mpl_operation.cuda()
            self.feature_mpl_table.cuda()
            self.feature_mpl_filter.cuda()
            self.feature_mpl_join.cuda()

            self.feature_mpl_operation_2.cuda()
            self.feature_mpl_table_2.cuda()
            self.feature_mpl_filter_2.cuda()
            self.feature_mpl_join_2.cuda()

            self.W_xou.cuda()
            self.out_mlp1.cuda()
            self.out_mlp2.cuda()

            self.con_mpl_ab.cuda()
            self.con_mpl_a.cuda()
            self.con_mpl_b.cuda()



    def forward(self, oper_feat, tb_feat, filter_feat, join_feat, node_order, adjacency_list, edge_order, c_a, c_b, feed):

        batch_size = node_order.shape[0]
        device = next(self.parameters()).device
        h = torch.zeros(batch_size, self.mem_dim, device=device)
        c = torch.zeros(batch_size, self.mem_dim, device=device)
        #h = torch.zeros(batch_size, self.mem_dim)
        #c = torch.zeros(batch_size, self.mem_dim)

        oper_feat = F.relu(self.feature_mpl_operation(oper_feat))
        oper_feat = F.relu(self.feature_mpl_operation_2(oper_feat))
        tb_feat = F.relu(self.feature_mpl_table(tb_feat))
        tb_feat = F.relu(self.feature_mpl_table_2(tb_feat))
        filter_feat = F.relu(self.feature_mpl_filter(filter_feat))
        filter_feat = F.relu(self.feature_mpl_filter_2(filter_feat))
        join_feat = F.relu(self.feature_mpl_join(join_feat))
        join_feat = F.relu(self.feature_mpl_join_2(join_feat))
        x = torch.cat((oper_feat, tb_feat, filter_feat, join_feat), 1)

        xou = self.W_xou(x)
        xx, ff, rr = torch.split(xou, xou.size(1) // 3, dim=1)
        ff = torch.sigmoid(ff)
        rr = torch.sigmoid(rr)

        #connect layer
        c_a = self.convert_a(c_a)
        weight_a = torch.sigmoid(self.con_mpl_a(c_a))
        weight_b = torch.sigmoid(self.con_mpl_b(c_b))
        c_ab = weight_a * c_a + weight_b * c_b
        c_ab = F.relu(self.con_mpl_ab(c_ab))


        #self._run_init(h, c, xx, ff, rr, x, node_order)
        c_mask = node_order == 0
        c[c_mask, :] = c_b[c_mask, :]
        c_mask = node_order == feed
        c[c_mask, :] = c_ab[c_mask, :]


        for n in range(feed + 1, node_order.max() + 1):
            self._run_SRU(n, h, c, xx, ff, rr, x, node_order, adjacency_list, edge_order)

        hid_output = F.relu(self.out_mlp1(h))
        out = torch.sigmoid(self.out_mlp2(hid_output))
        return out




    def _run_init (self, h, c, xx, ff, rr, features, node_order):
        node_mask = node_order == 0
        c[node_mask, :] = (1 - ff[node_mask, :]) * xx[node_mask, :]
        h[node_mask, :] = rr[node_mask, :] * torch.tanh(c[node_mask, :]) + (1 - rr[node_mask, :]) * features[node_mask, :]




    def _run_SRU(self, iteration, h, c, xx, ff, rr, features, node_order, adjacency_list, edge_order):
        node_mask = node_order == iteration
        edge_mask = edge_order == iteration

        adjacency_list = adjacency_list[edge_mask, :]
        parent_indexes = adjacency_list[:, 0]
        child_indexes = adjacency_list[:, 1]

        child_c = c[child_indexes, :]
        _, child_counts = torch.unique_consecutive(parent_indexes, return_counts=True)
        child_counts = tuple(child_counts)

        parent_children = torch.split(child_c, child_counts)
        parent_list = [item.sum(0) for item in parent_children]
        c_sum = torch.stack(parent_list)

        f = ff[node_mask, :]
        r = rr[node_mask, :]
        c[node_mask, :] = f * c_sum + (1 - f) * xx[node_mask, :]
        h[node_mask, :] = r * torch.tanh(c[node_mask, :]) + (1 - r) * features[node_mask, :]







    def _connctLayer_call_postgre(self, op_feat, tb_feat, ft_feat, join_feat, real_hidden, content_hidden, right_hidden):
        device = next(self.parameters()).device
        op_feat = F.relu(self.feature_mpl_operation(op_feat))
        op_feat = F.relu(self.feature_mpl_operation_2(op_feat))
        tb_feat = F.relu(self.feature_mpl_table(tb_feat))
        tb_feat = F.relu(self.feature_mpl_table_2(tb_feat))
        ft_feat = F.relu(self.feature_mpl_filter(ft_feat))
        ft_feat = F.relu(self.feature_mpl_filter_2(ft_feat))
        join_feat = F.relu(self.feature_mpl_join(join_feat))
        join_feat = F.relu(self.feature_mpl_join_2(join_feat))
        x = torch.cat((op_feat, tb_feat, ft_feat, join_feat), 1)

        xou = self.W_xou(x)
        xx, ff, rr = torch.split(xou, xou.size(1) // 3, dim=1)
        ff = torch.sigmoid(ff)
        rr = torch.sigmoid(rr)

        #connect layer
        c_a = self.convert_a(real_hidden)
        weight_a = torch.sigmoid(self.con_mpl_a(c_a))
        weight_b = torch.sigmoid(self.con_mpl_b(content_hidden))
        c_merge = weight_a * c_a + weight_b * content_hidden
        c_merge = F.relu(self.con_mpl_ab(c_merge))

        c = ff * (c_merge + right_hidden) + (1 - ff) * xx
        h = rr * torch.tanh(c) + (1 - rr) * x

        hid_output = F.relu(self.out_mlp1(h))
        out = torch.sigmoid(self.out_mlp2(hid_output))
        return out, c





    def _internalLayer_call_postgre(self, op_feat, tb_feat, ft_feat, join_feat, refine_hidden, right_hidden):
        device = next(self.parameters()).device
        op_feat = F.relu(self.feature_mpl_operation(op_feat))
        op_feat = F.relu(self.feature_mpl_operation_2(op_feat))
        tb_feat = F.relu(self.feature_mpl_table(tb_feat))
        tb_feat = F.relu(self.feature_mpl_table_2(tb_feat))
        ft_feat = F.relu(self.feature_mpl_filter(ft_feat))
        ft_feat = F.relu(self.feature_mpl_filter_2(ft_feat))
        join_feat = F.relu(self.feature_mpl_join(join_feat))
        join_feat = F.relu(self.feature_mpl_join_2(join_feat))
        x = torch.cat((op_feat, tb_feat, ft_feat, join_feat), 1)

        xou = self.W_xou(x)
        xx, ff, rr = torch.split(xou, xou.size(1) // 3, dim=1)
        ff = torch.sigmoid(ff)
        rr = torch.sigmoid(rr)

        c = ff * (refine_hidden + right_hidden) + (1 - ff) * xx
        h = rr * torch.tanh(c) + (1 - rr) * x

        hid_output = F.relu(self.out_mlp1(h))
        out = torch.sigmoid(self.out_mlp2(hid_output))
        return out, c