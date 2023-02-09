import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

# refined module, we need to consider two cases
#  Case 2
#     (1,2,3,4)
#     /      \
#   (1,2,3)  (4)
#      |
#   connect layer (CNL-B)
#   /    \
#  (2)  (1,3)
#  (2) is executed node from card module,
#  (1,3) are unexecuted node from content module,
#  and (1, 2, 3) (4) are unexecuted node at refine module.
#  the connect layer is CNL-B




class REFINEModuleB(torch.nn.Module):
    def __init__(self, cuda_use, feature_dim, input_dim, mem_dim, hidden_dim):
        super(REFINEModuleB, self).__init__()

        self.use_time = 0.0
        self.cuda_use = cuda_use
        self.feature_dim = feature_dim
        self.input_dim = input_dim
        self.mem_dim = mem_dim
        self.hidden_dim = hidden_dim
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


        self.W_xou = torch.nn.Linear(self.input_dim * 4, 3 * self.mem_dim)
        #output module
        self.out_mlp1 = nn.Linear(self.mem_dim, self.hidden_dim)
        self.out_mlp2 = nn.Linear(self.hidden_dim, 1)

        #connect layer
        self.con_mpl_ab = nn.Linear(self.input_dim * 5, self.mem_dim)
        self.con_mpl_a = nn.Linear(self.input_dim * 5, self.input_dim * 5)
        self.convert_mpl_b = nn.Linear(self.input_dim * 4, self.input_dim * 5)
        self.con_mpl_b = nn.Linear(self.input_dim * 5, self.input_dim * 5)


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
            self.convert_mpl_b.cuda()



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


        # Odd number of child_indexes is left child from card module, done-executed node
        # Even number of child_indexes is right child from content module, unexecuted node
        # 输出c_ab
        # 把c_ab复制到c上
        edge_mask = edge_order == feed
        adjacency_xx = adjacency_list[edge_mask, :]
        parent_indexes = adjacency_xx[:, 0]
        child_indexes = adjacency_xx[:, 1]

        if(child_indexes.dim() != 1):
            print("ERROR: child_indexes dim is unmatched")

        n = child_indexes.numel()
        list_a = []
        list_b = []
        for i in range(n):
            if i % 2 == 0:
                list_a.append(True)
                list_b.append(False)
            else:
                list_a.append(False)
                list_b.append(True)

        mask_l = np.array(list_a)
        mask_l = torch.from_numpy(mask_l)
        mask_l = torch.masked_select(child_indexes, mask_l)
        child_l = c_a[mask_l, :]

        mask_r = np.array(list_b)
        mask_r = torch.from_numpy(mask_r)
        mask_r = torch.masked_select(child_indexes, mask_r)
        child_r = c_b[mask_r, :]


        #connect layer
        weight_a = torch.sigmoid(self.con_mpl_a(child_l))
        child_r = self.convert_mpl_b(child_r)
        weight_b = torch.sigmoid(self.con_mpl_b(child_r))
        c_ab = weight_a * child_l + weight_b * child_r
        c_ab = F.relu(self.con_mpl_ab(c_ab))
        c[mask_l, :] = c_ab


        # init all leaf nodes
        self._run_init(h, c, xx, ff, rr, x, node_order)

        for n in range(feed, node_order.max() + 1):
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