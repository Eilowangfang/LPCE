import torch
import torch.nn as nn
import torch.nn.functional as F
import time


class SRU_distill(torch.nn.Module):
    def __init__(self, cuda_use, feature_dim, embed_dim, mem_dim, outputdim, embed_dim_teacher):
        super(SRU_distill, self).__init__()

        self.use_time = 0.0
        self.cuda_use = cuda_use
        self.feature_dim = feature_dim
        self.input_dim = embed_dim
        self.mem_dim = mem_dim
        self.outputdim = outputdim
        self.embed_dim_teacher = embed_dim_teacher

        self.operat_dim = 4
        self.table_dim = 11
        self.filter_dim = 18
        self.join_dim = 37

        #embeed module embeed input feature
        self.feature_mpl_operation = torch.nn.Linear(self.operat_dim, self.input_dim)
        self.feature_mpl_table = torch.nn.Linear(self.table_dim, self.input_dim)
        self.feature_mpl_filter = torch.nn.Linear(self.filter_dim, self.input_dim)
        self.feature_mpl_join = torch.nn.Linear(self.join_dim , self.input_dim)

        self.feature_mpl_operation_2 = torch.nn.Linear(self.input_dim, self.input_dim)
        self.feature_mpl_table_2 =  torch.nn.Linear(self.input_dim, self.input_dim)
        self.feature_mpl_filter_2  = torch.nn.Linear(self.input_dim, self.input_dim)
        self.feature_mpl_join_2  = torch.nn.Linear(self.input_dim, self.input_dim)

        self.x_distill =  torch.nn.Linear(self.input_dim * 4, self.embed_dim_teacher * 4)
        self.h_distill =  torch.nn.Linear(self.input_dim * 4, self.embed_dim_teacher * 4)

        self.W_xou = torch.nn.Linear(self.input_dim * 4, 3 * self.mem_dim)
        #output module
        self.out_mlp1 = nn.Linear(self.mem_dim, self.outputdim)
        self.out_mlp2 = nn.Linear(self.outputdim, 1)


        torch.nn.init.xavier_uniform_(self.feature_mpl_operation.weight)
        torch.nn.init.constant_(self.feature_mpl_operation.bias, 0)
        torch.nn.init.xavier_uniform_(self.feature_mpl_filter.weight)
        torch.nn.init.constant_(self.feature_mpl_filter.bias, 0)
        torch.nn.init.xavier_uniform_(self.feature_mpl_join.weight)
        torch.nn.init.constant_(self.feature_mpl_join.bias, 0)
        torch.nn.init.xavier_uniform_(self.feature_mpl_operation_2.weight)
        torch.nn.init.constant_(self.feature_mpl_operation_2.bias, 0)
        torch.nn.init.xavier_uniform_(self.feature_mpl_filter_2.weight)
        torch.nn.init.constant_(self.feature_mpl_filter_2.bias, 0)
        torch.nn.init.xavier_uniform_(self.feature_mpl_join_2.weight)
        torch.nn.init.constant_(self.feature_mpl_join_2.bias, 0)

        torch.nn.init.xavier_uniform_(self.x_distill.weight)
        torch.nn.init.constant_(self.x_distill.bias, 0)
        torch.nn.init.xavier_uniform_(self.h_distill.weight)
        torch.nn.init.constant_(self.h_distill.bias, 0)


        torch.nn.init.xavier_uniform_(self.W_xou.weight)
        torch.nn.init.constant_(self.W_xou.bias, 0)
        torch.nn.init.xavier_uniform_(self.out_mlp1.weight)
        torch.nn.init.constant_(self.out_mlp1.bias, 0)
        torch.nn.init.xavier_uniform_(self.out_mlp2.weight)
        torch.nn.init.constant_(self.out_mlp2.bias, 0)

        if self.cuda_use:
            self.feature_mpl_operation.cuda()
            self.feature_mpl_filter.cuda()
            self.feature_mpl_table.cuda()
            self.feature_mpl_join.cuda()
            self.feature_mpl_operation_2.cuda()
            self.feature_mpl_table_2.cuda()
            self.feature_mpl_filter_2.cuda()
            self.feature_mpl_join_2.cuda()

            self.x_distill.cuda()
            self.h_distill.cuda()
            self.W_xou.cuda()
            self.out_mlp1.cuda()
            self.out_mlp2.cuda()



    def forward(self, op_feat, tb_feat, ft_feat, join_feat, node_order, adjacency_list, edge_order):

        batch_size = node_order.shape[0]
        device = next(self.parameters()).device
        h = torch.zeros(batch_size, self.mem_dim, device=device)
        c = torch.zeros(batch_size, self.mem_dim, device=device)
        #h = torch.zeros(batch_size, self.mem_dim)
        #c = torch.zeros(batch_size, self.mem_dim)

        op_feat = F.relu(self.feature_mpl_operation(op_feat))
        op_feat = F.relu(self.feature_mpl_operation_2(op_feat))
        tb_feat = F.relu(self.feature_mpl_table(tb_feat))
        tb_feat = F.relu(self.feature_mpl_table_2(tb_feat))
        ft_feat = F.relu(self.feature_mpl_filter(ft_feat))
        ft_feat = F.relu(self.feature_mpl_filter_2(ft_feat))
        join_feat = F.relu(self.feature_mpl_join(join_feat))
        join_feat = F.relu(self.feature_mpl_join_2(join_feat))
        x = torch.cat((op_feat, tb_feat, ft_feat, join_feat), 1)
        x_dis = self.x_distill(x)

        xou = self.W_xou(x)
        xx, ff, rr = torch.split(xou, xou.size(1) // 3, dim=1)
        ff = torch.sigmoid(ff)
        rr = torch.sigmoid(rr)

        self._run_init(h, c, xx, ff, rr, x, node_order)
        for n in range(1, node_order.max() + 1):
            self._run_SRU(n, h, c, xx, ff, rr, x, node_order, adjacency_list, edge_order)
        hm_dis = self.h_distill(h)

        hid_output = F.relu(self.out_mlp1(h))
        out = torch.sigmoid(self.out_mlp2(hid_output))
        return out, self.out_mlp2(hid_output), x_dis, hm_dis




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






    def _base_call_postgre(self, op_feat, tb_feat, ft_feat, join_feat):
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

        c = (1 - ff) * xx
        h = rr * torch.tanh(c) + (1 - rr) * x

        hid_output = F.relu(self.out_mlp1(h))
        out = torch.sigmoid(self.out_mlp2(hid_output))
        return out, c






    def _join_call_postgre(self, op_feat, tb_feat, ft_feat, join_feat, left_child, right_child):
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
        c = ff * (left_child + right_child) + (1 - ff) * xx
        h = rr * torch.tanh(c) + (1 - rr) * x

        hid_output = F.relu(self.out_mlp1(h))
        out = torch.sigmoid(self.out_mlp2(hid_output))

        return out, c





